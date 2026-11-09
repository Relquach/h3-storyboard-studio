"""Read-only Apex V7 mapping and approved-storyboard prompt compiler for Codex."""
import argparse,copy,hashlib,json,math,pathlib,re
TOKEN=re.compile(r'\{\{ref:([A-Z][A-Z0-9_]*)\}\}')
def frames(seconds):
 if type(seconds) not in (float,int) or not math.isfinite(seconds) or not 0<seconds<=30:raise ValueError('Giây phải hữu hạn, >0 và ≤30.')
 n=max(5,round(seconds*24));return n+(5-n%17)%17

def slots(workflow):
 nodes={n['id']:n for n in workflow['nodes']};links={l[0]:l for l in workflow['links']};target=nodes.get(136)
 if not target or target['type']!='MiniMaxH3ReferenceToVideo':raise ValueError('Không phải profile Apex V7 Ref2V #136.')
 result=[]
 for inp in target.get('inputs',[]):
  m=re.fullmatch(r'ref_images\.ref_image_(\d+)',inp['name'])
  if not m or inp.get('link') is None:continue
  edge=links[inp['link']];src=nodes[edge[1]];seen=set()
  while src['type']=='Reroute':
   if src['id'] in seen:raise ValueError('Vòng lặp Reroute.')
   seen.add(src['id']);edge=links[src['inputs'][0]['link']];src=nodes[edge[1]]
  if src['type']!='LoadImage' or edge[2]!=0:raise ValueError('Cần kiểm tra node trung gian ở reference '+inp['name'])
  result.append({'slot':int(m[1]),'socket':inp['name'],'loader':src['id'],'enabled':src.get('mode',0)==0,'file':src['widgets_values'][0]})
 result.sort(key=lambda x:x['slot'])
 if not result or result[0]['loader']!=7330:raise ValueError('Storyboard không còn ở loader #7330. Đọc lại workflow.')
 return result

def compile_plan(plan,workflow):
 review=plan.get('storyboard_review',{})
 if review.get('status')!='approved' or review.get('approved_by')!='user' or not str(review.get('evidence','')).strip():raise ValueError('Storyboard chưa được người dùng duyệt thực; chưa tạo prompt video.')
 if not plan.get('storyboard_revision') or review.get('approved_revision')!=plan['storyboard_revision']:raise ValueError('Storyboard đã đổi revision; cần duyệt lại.')
 s=slots(workflow);byloader={x['loader']:x for x in s};nodes={n['id']:n for n in workflow['nodes']}
 pi=next(x for x in nodes[136]['inputs'] if x['name']=='prompt');link=next(l for l in workflow['links'] if l[0]==pi['link'])
 if link[1]!=138:raise ValueError('Prompt còn qua LLM/switch. Dùng preset Codex trực tiếp hoặc xác minh chuỗi trước khi bàn giao.')
 sec=plan['seconds'];count=frames(sec)
 if count>362:raise ValueError('Profile mặc định không vượt vùng 15 giây; chia lượt và duyệt storyboard từng lượt.')
 assets=plan['assets'];ids=[a['id'] for a in assets];loaders=[a['loader'] for a in assets]
 if len(set(ids))!=len(ids) or len(set(loaders))!=len(loaders):raise ValueError('Trùng asset ID hoặc loader.')
 for a in assets:
  if a['loader'] not in byloader:raise ValueError('Asset không được nối thật: '+str(a['loader']))
  if type(a.get('enabled',True)) is not bool:raise ValueError('enabled phải là boolean.')
  if not re.fullmatch(r'[A-Z][A-Z0-9_]*',a['id']):raise ValueError('Asset ID không hợp lệ.')
  if a.get('enabled',True) and (not a.get('file') or not a.get('description_en','').strip()):raise ValueError('Thiếu file/mô tả ảnh đang bật.')
 byasset={a['id']:a for a in assets};byid={a['loader']:a for a in assets};sb=byasset.get('STORYBOARD')
 if not sb or sb['loader']!=7330 or not sb.get('enabled',True):raise ValueError('STORYBOARD phải bật tại #7330.')
 active=[byid[x['loader']] for x in s if x['loader'] in byid and byid[x['loader']].get('enabled',True)]
 numbers={a['id']:i+1 for i,a in enumerate(active)};grid=plan['grid'];shots=plan['shots']
 if not isinstance(grid,list) or len(grid)!=2 or any(type(x) is not int or x<1 for x in grid):raise ValueError('Grid dùng [hàng,cột] dương.')
 if not shots:raise ValueError('Thiếu shot.')
 coords=[(x['row'],x['column']) for x in shots];labels=[x['label'] for x in shots]
 if len(set(coords))!=len(coords) or len(set(labels))!=len(labels) or coords!=sorted(coords):raise ValueError('Shot bị trùng hoặc sai thứ tự đọc.')
 if any(type(r) is not int or type(c) is not int or not 1<=r<=grid[0] or not 1<=c<=grid[1] for r,c in coords):raise ValueError('Shot ngoài grid.')
 if any(not re.fullmatch(r'SHOT [1-9]\d*',x) for x in labels):raise ValueError('Nhãn dùng SHOT N.')
 times=[x['seconds'] for x in shots]
 if any(type(t) not in (int,float) or not math.isfinite(t) or t<=0 for t in times) or abs(sum(times)-sec)>.001:raise ValueError('Tổng thời lượng shot không khớp.')
 cells={(r,c) for r in range(1,grid[0]+1) for c in range(1,grid[1]+1)}
 if {tuple(x) for x in plan.get('empty_cells',[])}!=cells-set(coords):raise ValueError('Khai báo ô EMPTY chính xác.')
 template=plan['video_prompt_template']
 if re.search(r'<Picture\s+\d+>',template):raise ValueError('Dùng {{ref:ID}}, không hardcode số Picture.')
 def ref(m):
  if m[1] not in numbers:raise ValueError('Prompt gọi ảnh không được bật/nối: '+m[1])
  return '<Picture '+str(numbers[m[1]])+'>'
 prompt=TOKEN.sub(ref,template);timeline={};cursor=0
 for shot in shots:timeline[shot['label']]={'start':cursor,'end':cursor+shot['seconds']};cursor+=shot['seconds']
 def stamp(m):
  t=round(timeline[m[2]][m[1]]*1000);return f'{t//60000:02d}:{t//1000%60:02d}.{t%1000:03d}'
 prompt=re.sub(r'\{\{(start|end):(SHOT [1-9]\d*)\}\}',stamp,prompt)
 if '{{' in prompt or any('['+label+']' not in prompt for label in labels):raise ValueError('Thiếu shot hoặc còn token chưa resolve.')
 header='REFERENCE INPUT ORDER:\n'+'\n'.join(f'<Picture {numbers[a["id"]]}>: {a["id"]} — {a["description_en"]}' for a in active)
 mapping=[dict(x,asset=byid.get(x['loader'],{}).get('id'),desired_enabled=byid.get(x['loader'],{}).get('enabled',True) if x['loader'] in byid else False,picture=numbers.get(byid.get(x['loader'],{}).get('id')),desired_file=byid.get(x['loader'],{}).get('file')) for x in s]
 return {'profile':'apex_v7_ref2v_3d','prompt':header+'\n\n'+prompt,'mapping':mapping,'seconds_setting_node_132':sec,'h3_frames':count,'h3_duration':count/24,'storyboard_revision':plan['storyboard_revision'],'storyboard_sha256':plan.get('storyboard_sha256'),'ui_actions_required':['Set enabled state and image filenames exactly as mapping','Paste prompt into #138','Set #132 seconds and both aspect selectors; LTX output dimensions must match'],'gpu_render_tested':False}

def audit(workflow):
 ns={n['id']:n for n in workflow['nodes']};defs={d['id']:d for d in workflow.get('definitions',{}).get('subgraphs',[])}
 model=ns.get(127,{}).get('widgets_values',[''])[0]
 return {'profile':'apex_v7_ref2v','references':slots(workflow),'model':model,'duration_control':ns.get(132,{}).get('widgets_values'),'h3_frames':frames(ns[132]['widgets_values'][0]),'llm_present':9482 in ns,'stages':2+int(9258 in ns),'subgraphs':{str(n['id']):defs[n['type']]['name'] for n in ns.values() if n['type'] in defs},'gpu_render_tested':False,'note':'Snapshot only. Final mapping must use exported graph with current bypass states; this is not a GPU test.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('workflow');p.add_argument('--plan');p.add_argument('--output');a=p.parse_args();w=json.loads(pathlib.Path(a.workflow).read_text(encoding='utf-8-sig'))
 result=compile_plan(json.loads(pathlib.Path(a.plan).read_text(encoding='utf-8-sig')),w) if a.plan else audit(w)
 txt=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if a.output:
  with open(a.output,'x',encoding='utf-8') as f:f.write(txt)
 else:print(txt)
if __name__=='__main__':main()
