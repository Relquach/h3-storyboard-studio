"""Compile prompt references and core LoadImage wires from one asset manifest."""
import copy,json,math,pathlib,re,shutil,uuid
ASSET_TOKEN=re.compile(r'<Asset:([A-Z][A-Z0-9_]*)>')
PICTURE_TOKEN=re.compile(r'<Picture\s+(\d+)>')
REFERENCE_NODE=26
PROMPT_NODE=70

def frame_count(seconds):
    if isinstance(seconds,bool) or not isinstance(seconds,(int,float)) or not math.isfinite(seconds) or not 3<=seconds<=15:
        raise ValueError('Mỗi lượt local dùng 3–15 giây; phim dài hơn chia thành nhiều lượt.')
    return math.ceil((round(seconds*24)-5)/17)*17+5

def compile_assets(project):
    assets=project['assets'];ids=[a['id'] for a in assets]
    frame_count(project['seconds'])
    mp=project.get('draft_megapixels',0.2)
    if isinstance(mp,bool) or not isinstance(mp,(int,float)) or not math.isfinite(mp) or not 0.1<=mp<=16:raise ValueError('draft_megapixels phải trong 0.1–16 theo core.')
    allowed=['1:1 (Square)','2:3 (Portrait Photo)','3:2 (Photo)','3:4 (Portrait Standard)','4:3 (Standard)','9:16 (Portrait Widescreen)','16:9 (Widescreen)','21:9 (Ultrawide)']
    if project.get('aspect','9:16 (Portrait Widescreen)') not in allowed:raise ValueError('Tên tỷ lệ phải đúng enum của ComfyUI; xem ví dụ.')
    if not all(re.fullmatch(r'[A-Z][A-Z0-9_]*',aid) for aid in ids):raise ValueError('Asset ID chỉ gồm chữ hoa, số và dấu gạch dưới.')
    if not all(isinstance(a.get('enabled',True),bool) for a in assets):raise ValueError('enabled phải là true hoặc false.')
    if len(ids)!=len(set(ids)):raise ValueError('Trùng asset ID')
    active=[a for a in assets if a.get('enabled',True)]
    if not active or active[0]['id']!='STORYBOARD' or active[0].get('role')!='storyboard':raise ValueError('STORYBOARD phải là ảnh bật đầu tiên.')
    if not 1<=len(active)<=9:raise ValueError('Tối đa 9 ảnh, gồm storyboard.')
    slots={a['id']:i+1 for i,a in enumerate(active)};by_id={a['id']:a for a in assets}
    prompt=project['video_prompt']
    # Raw ordinal tags cannot establish identity; only semantic IDs do.
    if PICTURE_TOKEN.search(prompt):raise ValueError('project dùng <Asset:ID>; số Picture do bộ chuẩn bị tự sinh.')
    def replace(m):
        aid=m[1]
        if aid not in by_id:raise ValueError('Asset không khai báo: '+aid)
        if aid in slots:return f'<Picture {slots[aid]}>'
        description=by_id[aid].get('description','').strip()
        if not description:raise ValueError('Ảnh bị tắt cần description để dùng storyboard: '+aid)
        return description+' as visible in <Picture 1> (no separate reference supplied)'
    prompt=ASSET_TOKEN.sub(replace,prompt)
    if '<Asset:' in prompt:raise ValueError('Token Asset không hợp lệ hoặc chưa được thay.')
    mapping='\n'.join(f'<Picture {slots[a["id"]]}>: {a["id"]} — {a.get("description",a["role"])}' for a in active)
    return 'REFERENCE INPUT ORDER:\n'+mapping+'\n\n'+prompt,active

def normalize_links(w):
    nodes={n['id']:n for n in w['nodes']}
    for n in nodes.values():
        for p in n.get('inputs',[]):p['link']=None
        for p in n.get('outputs',[]):p['links']=[]
    for lid,src,out,dst,slot,typ in w['links']:
        if src not in nodes or dst not in nodes:raise ValueError('Dangling link '+str(lid))
        inp=nodes[dst]['inputs'][slot];output=nodes[src]['outputs'][out]
        if inp['link'] is not None:raise ValueError('Multiple links on one input')
        inp['link']=lid;output['links'].append(lid)
    w['last_node_id']=max(nodes);w['last_link_id']=max((l[0] for l in w['links']),default=0)

def wire_assets(template,project,paths):
    w=copy.deepcopy(template);prompt,active=compile_assets(project)
    if len(paths)!=len(active):raise ValueError('Asset file count mismatch')
    old={n['id'] for n in w['nodes'] if n['type']=='LoadImage'}
    nodes={n['id']:n for n in w['nodes']};w['links']=[l for l in w['links'] if l[1] not in old and l[3] not in old]
    w['nodes']=[n for n in w['nodes'] if n['id'] not in old]
    ref=nodes[REFERENCE_NODE]
    # Remove old autogrow image sockets; shift surviving input indexes explicitly.
    original=ref['inputs'];keep=[i for i,p in enumerate(original) if not p['name'].startswith('ref_images.')];newidx={old:i for i,old in enumerate(keep)}
    for link in w['links']:
        if link[3]==REFERENCE_NODE:link[4]=newidx[link[4]]
    ref['inputs']=[original[i] for i in keep]
    nid=max(n['id'] for n in w['nodes'])+1;lid=max((l[0] for l in w['links']),default=0)+1
    for i,(a,file) in enumerate(zip(active,paths)):
        node={'id':nid+i,'type':'LoadImage','title':f'ẢNH {i+1} · {a["id"]} · {a.get("name",a["role"])}','pos':[1000+i%2*290,1600+i//2*380],'size':[270,330],'flags':{},'order':len(w['nodes']),'mode':0,'inputs':[],
            'outputs':[{'name':'IMAGE','type':'IMAGE','links':[]},{'name':'MASK','type':'MASK','links':[]}],'properties':{'Node name for S&R':'LoadImage'},'widgets_values':[file,'image']}
        w['nodes'].append(node);slot=len(ref['inputs']);ref['inputs'].append({'name':f'ref_images.ref_image_{i}','type':'IMAGE','link':lid})
        w['links'].append([lid,nid+i,0,REFERENCE_NODE,slot,'IMAGE']);lid+=1
    # Terminal empty socket is frontend autogrow affordance, not a supplied picture.
    ref['inputs'].append({'name':f'ref_images.ref_image_{len(active)}','type':'IMAGE','link':None}) if len(active)<9 else None
    nodes[PROMPT_NODE]['widgets_values']=[prompt];nodes[23]['widgets_values']=[project['seconds']]
    nodes[25]['widgets_values']=[project.get('aspect','9:16 (Portrait Widescreen)'),project.get('draft_megapixels',0.2),32]
    nodes[30]['widgets_values']=[project.get('seed',12004),'fixed']
    nodes[123]['widgets_values']=[project.get('run_id','H3_take')]
    nodes[105]['widgets_values']=[False]
    normalize_links(w);return w,active

def prepare(template,project,comfy,output):
    resolved,active=compile_assets(project);comfy=pathlib.Path(comfy);job=uuid.uuid4().hex[:10];dest=comfy/'input';dest.mkdir(parents=True,exist_ok=True)
    paths=[]
    for a in active:
        src=pathlib.Path(a['file']).expanduser()
        if not src.is_file():raise FileNotFoundError(f'{a["id"]}: không thấy ảnh {src}')
        if src.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('Chỉ dùng PNG/JPG/WEBP: '+str(src))
        from PIL import Image
        with Image.open(src) as im:im.verify()
        name='singularity_'+job+'_'+a['id']+src.suffix.lower();shutil.copy2(src,dest/name);paths.append(name)
    w,active=wire_assets(template,project,paths);output=pathlib.Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(w,ensure_ascii=False,indent=2),encoding='utf-8')
    mapping=[{'asset_id':a['id'],'file':file,'picture':i+1,'target_node_id':26,'target_input':f'ref_images.ref_image_{i}'} for i,(a,file) in enumerate(zip(active,paths))]
    output.with_suffix('.mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
    output.with_suffix('.prompt.txt').write_text(resolved,encoding='utf-8')
    return output
