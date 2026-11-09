"""Read-only authoring helper for Codex: original workflow -> prompt + node table.

It does not edit ComfyUI JSON, install dependencies, connect to a server or render.
The output describes the configuration the user must apply, not observed UI state.
"""
import argparse,csv,hashlib,json,math,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
TOKEN=re.compile(r'\{\{ref:([A-Z][A-Z0-9_]*)\}\}')
PICTURE=re.compile(r'<Picture\s+(\d+)>')


def reference_slots(workflow):
    nodes={n['id']:n for n in workflow['nodes']}
    target=nodes.get(26)
    if not target or target['type']!='MiniMaxH3ReferenceToVideo':
        raise ValueError('Không thấy Ref2V #26 của bản gốc; đọc lại wiring bản mới trước khi gán node.')
    links={l[0]:l for l in workflow['links']};slots=[]
    expected={70:'PrimitiveStringMultiline',62:'PrimitiveBoolean',23:'PrimitiveFloat',25:'ResolutionSelector',105:'PrimitiveBoolean',124:'H3TakeLoad',134:'LoraLoaderModelOnly'}
    if any(nodes.get(i,{}).get('type')!=typ for i,typ in expected.items()):raise ValueError('ID điều khiển khác bản gốc; cần đọc lại bảng node.')
    prompt_input=next((p for p in target.get('inputs',[]) if p['name']=='prompt'),{})
    if prompt_input.get('link') not in links or links[prompt_input['link']][1]!=70:raise ValueError('Prompt #26 không còn lấy từ #70.')
    for p in target.get('inputs',[]):
        match=re.fullmatch(r'ref_images\.ref_image_(\d+)',p['name'])
        if not match or p.get('link') is None:continue
        link=links[p['link']]
        if link[3]!=26:raise ValueError('Link không thuộc node #26')
        src=nodes.get(link[1])
        if not src or src['type']!='LoadImage' or link[2]!=0:
            raise ValueError('Helper chỉ theo dây LoadImage trực tiếp của bản gốc; cần đọc node trung gian.')
        slots.append({'slot':int(match[1]),'node_id':src['id'],'socket':p['name'],'snapshot_mode':src.get('mode',0)})
    slots.sort(key=lambda s:s['slot'])
    if not slots or slots[0]['node_id']!=27:raise ValueError('Slot storyboard gốc không còn là LoadImage #27.')
    if len({s['node_id'] for s in slots})!=len(slots):raise ValueError('Một loader xuất hiện nhiều slot; kiểm tra wiring.')
    return slots


def frames_for_seconds(seconds):
    if isinstance(seconds,bool) or not isinstance(seconds,(int,float)) or not math.isfinite(seconds) or not 0<seconds<=30:
        raise ValueError('Giây phải hữu hạn, >0 và không quá trần30giây của người dùng.')
    n=max(5,round(seconds*24));return n+(5-n%17)%17


def validate_storyboard_approval(plan):
    review=plan.get('storyboard_review',{})
    if review.get('status')!='approved' or review.get('approved_by')!='user':
        raise ValueError('Storyboard chưa được người dùng duyệt; dừng trước bước tạo prompt video.')
    if not str(review.get('evidence','')).strip():
        raise ValueError('Thiếu lời xác nhận duyệt thực của người dùng.')
    if not plan.get('storyboard_revision') or review.get('approved_revision')!=plan['storyboard_revision']:
        raise ValueError('Revision storyboard đã đổi hoặc chưa xác định; cần duyệt đúng bản mới trước prompt video.')


def compile_plan(plan,workflow):
    validate_storyboard_approval(plan)
    slots=reference_slots(workflow);lookup={s['node_id']:s for s in slots}
    seconds=plan['seconds'];frames=frames_for_seconds(seconds)
    if frames>362:raise ValueError('Lượt > vùng profile khoảng15giây chưa kiểm chứng; chia run thay vì tự nâng giới hạn.')
    grid=plan['grid']
    if not isinstance(grid,list) or len(grid)!=2 or not all(type(x) is int and x>0 for x in grid):raise ValueError('grid là [số hàng, số cột] dương.')
    assets=plan['assets'];ids=[a['id'] for a in assets]
    if len(ids)!=len(set(ids)) or not all(re.fullmatch(r'[A-Z][A-Z0-9_]*',x) for x in ids):raise ValueError('Asset ID không hợp lệ hoặc bị trùng.')
    if len({a['node_id'] for a in assets})!=len(assets):raise ValueError('Hai tài sản không được dùng chung một loader trong cùng lượt.')
    by_id={a['id']:a for a in assets};by_node={a['node_id']:a for a in assets}
    for a in assets:
        if a['node_id'] not in lookup:raise ValueError('Asset không nằm trên dây reference gốc: '+str(a['node_id']))
        if not isinstance(a.get('enabled',True),bool):raise ValueError('enabled phải là boolean.')
        if not a.get('description_en','').strip():raise ValueError('Thiếu mô tả nhận diện của '+a['id'])
    sb=by_id.get('STORYBOARD')
    if not sb or sb['node_id']!=27 or not sb.get('enabled',True) or sb.get('role')!='storyboard':raise ValueError('STORYBOARD phải bật ở loader27.')
    active=[by_node[s['node_id']] for s in slots if s['node_id'] in by_node and by_node[s['node_id']].get('enabled',True)]
    if len(active)>9:raise ValueError('Core không nhận quá9ảnh.')
    numbers={a['id']:i+1 for i,a in enumerate(active)}
    shots=plan['shots'];labels=[s['label'] for s in shots];coords=[(s['row'],s['column']) for s in shots]
    if not shots or len(labels)!=len(set(labels)) or len(coords)!=len(set(coords)):raise ValueError('Shot/nhãn/vị trí rỗng hoặc trùng.')
    if not all(re.fullmatch(r'SHOT [1-9]\d*',s) for s in labels):raise ValueError('Nhãn dùng SHOT N.')
    times=[s['seconds'] for s in shots]
    if any(isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t) or t<=0 for t in times):raise ValueError('Thời lượng shot phải dương và hữu hạn.')
    if abs(sum(times)-seconds)>0.001:raise ValueError('Tổng giây shot không khớp giây run.')
    if coords!=sorted(coords) or any(type(r) is not int or type(c) is not int or not 1<=r<=grid[0] or not 1<=c<=grid[1] for r,c in coords):raise ValueError('Shot phải đúng hàng/cột và thứ tự đọc.')
    all_cells={(r,c) for r in range(1,grid[0]+1) for c in range(1,grid[1]+1)}
    empty=plan.get('empty_cells',[])
    if {tuple(x) for x in empty} != all_cells-set(coords):raise ValueError('Khai báo đúng các ô EMPTY khi grid chưa đủ shot.')
    timeline={};cursor=0.0
    for shot in shots:
        timeline[shot['label']]={'start':cursor,'end':cursor+shot['seconds']};cursor+=shot['seconds']
    def stamp(match):
        side,label=match.groups()
        if label not in timeline:raise ValueError('Timestamp gọi shot không có: '+label)
        ms=round(timeline[label][side]*1000)
        return f'{ms//60000:02d}:{ms//1000%60:02d}.{ms%1000:03d}'
    template=re.sub(r'\{\{(start|end):(SHOT [1-9]\d*)\}\}',stamp,plan['video_prompt_template'])
    if PICTURE.search(template):raise ValueError('Plan nội bộ dùng {{ref:ID}}; helper sinh số Picture một lần.')
    fallback=[]
    def resolve(m):
        aid=m[1]
        if aid not in by_id:raise ValueError('Prompt gọi asset chưa khai báo: '+aid)
        if aid in numbers:return f'<Picture {numbers[aid]}>'
        if by_id[aid].get('fallback_from_storyboard') is not True:raise ValueError('Asset tắt chưa cho phép dùng từ storyboard: '+aid)
        fallback.append(aid);return '<Picture 1>'
    prompt=TOKEN.sub(resolve,template)
    if '{{' in prompt or '<Asset:' in prompt:raise ValueError('Prompt còn template token chưa resolve.')
    for label in labels:
        if '['+label+']' not in prompt:raise ValueError('Prompt thiếu nhãn shot '+label)
    if plan.get('style') in {'3d_animation','semi_realistic_3d_east_asian'} and 'r34l1sm' in prompt:raise ValueError('Bỏ trigger Realism khỏi prompt3D.')
    header='REFERENCE INPUT ORDER:\n'+'\n'.join(f'<Picture {numbers[a["id"]]}>: {a["id"]} — {a["description_en"]}' for a in active)
    if fallback:header+='\nNO SEPARATE SHEET: '+', '.join(dict.fromkeys(fallback))+'. Obtain these assets from the storyboard, not an unprovided image.'
    prompt=header+'\n\n'+prompt
    if any(not 1<=int(n)<=len(active) for n in PICTURE.findall(prompt)):raise ValueError('Picture cuối không có ảnh tương ứng.')
    mapping=[];actions=[]
    for s in slots:
        a=by_node.get(s['node_id']);on=a is not None and a.get('enabled',True)
        row={**s,'asset_id':a['id'] if a else '', 'enabled':on,'picture':numbers[a['id']] if on else '', 'file_label':a.get('file_label','Chọn ảnh đúng tài sản') if a else ''}
        mapping.append(row);actions.append({'node_id':s['node_id'],'action':'Nạp '+row['file_label']+'; bật' if on else 'Bypass (Ctrl+B)','picture':row['picture']})
    instructions={'62':'true (nhánh Ref2V)','70':'Dán video_prompt.txt','23':seconds,'25':plan.get('aspect','Giữ tỷ lệ đã chọn; multiple32'),'105':'false tạo nháp; true nâng take','124':'Chọn take đã duyệt; không mặc định latest đúng dự án'}
    if plan.get('style') in {'3d_animation','semi_realistic_3d_east_asian'}:instructions['134']='Bypass Realism People; giữ Turbo #10'
    return {'status':'configuration_to_apply_not_live_runtime_verified','run_id':plan['run_id'],'seconds':seconds,'frames':frames,'source_seconds':frames/24,'grid':grid,'mapping':mapping,'node_actions':actions,'controls':instructions,'prompt':prompt}


def write_handoff(result,out):
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'video_prompt.txt').write_text(result['prompt']+'\n',encoding='utf-8')
    (out/'handoff.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    fields=['asset_id','file_label','node_id','socket','enabled','picture','snapshot_mode']
    with (out/'mapping.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(result['mapping'])
    lines=['# Bàn giao '+result['run_id'],'','Đây là cấu hình cần áp dụng trên workflow gốc, chưa xác minh runtime máy người dùng.','',f'Giây kế hoạch: {result["seconds"]}; nguồn: {result["frames"]} frame / 24 FPS ≈ {result["source_seconds"]:.3f} giây.','','| Node | Thao tác | Picture |','|---|---|---|']
    for row in result['node_actions']:lines.append(f'| #{row["node_id"]} | {row["action"]} | {row["picture"]} |')
    for node,value in result['controls'].items():lines.append(f'| #{node} | {value} | |')
    lines+=['','Bước1: đặt #105=false, Queue, xem nháp; lưu tên take. Bước2: #105=true, #124 chọn take đó, Queue. Đổi ảnh/prompt cần tạo take mới.','', 'Bỏ/đổi ảnh phải sinh lại prompt và bảng Picture. Helper không sửa workflow hoặc cài gì lên máy.']
    (out/'COMFYUI_HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('plan');ap.add_argument('--workflow',default=str(ROOT/'references/original-workflow.json'));ap.add_argument('--out',required=True);args=ap.parse_args()
    p=pathlib.Path(args.workflow);before=hashlib.sha256(p.read_bytes()).hexdigest();workflow=json.loads(p.read_text(encoding='utf-8-sig'));plan=json.loads(pathlib.Path(args.plan).read_text(encoding='utf-8-sig'))
    result=compile_plan(plan,workflow);result['workflow_sha256']=before;write_handoff(result,args.out)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=before:raise RuntimeError('Workflow source changed unexpectedly')
    print('Đã xuất prompt + mapping + bảng node. Không sửa workflow, không render.')
if __name__=='__main__':main()
