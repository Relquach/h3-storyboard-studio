"""Optional mechanical checks for a declared storyboard handoff. Does not inspect pixels/audio."""
import argparse,json,math,pathlib,re,sys,importlib.util
_spec=importlib.util.spec_from_file_location('_h3_production_checks',pathlib.Path(__file__).with_name('production_checks.py'));production=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(production)
BLOCK=re.compile(r'\[shot\s+(\d+)\]\s*\[\s*([\d.]+)\s*-\s*([\d.]+)\s*s\s*\]',re.I)
TAGS=re.compile(r'\[shot\s+(\d+)\]',re.I)
def norm(s):return re.sub(r'[^\w]+',' ',str(s).casefold()).strip()
def numeric(x):return type(x) in (int,float) and math.isfinite(x)
def one_take_conflict(text):
 for m in re.finditer(r'\b(one continuous shot|single unbroken take|no cuts|static steady close-up throughout|continuous close-up sequence)\b',text,re.I):
  prefix=text[max(0,m.start()-45):m.start()]
  prefix=re.split(r'[.!?\n]',prefix)[-1]
  if not re.search(r'\b(?:not|never|avoid)\b',prefix,re.I):return True
 return False

def validate(p):
 errors=[];warnings=[]
 def fail(code,message):errors.append({'code':code,'message':message})
 review=p.get('storyboard_review',{})
 if review.get('status')!='approved' or review.get('approved_by')!='user' or not str(review.get('evidence','')).strip():fail('storyboard_not_approved','Cần lời duyệt storyboard thực; checker không chứng thực con người đã duyệt.')
 revision=p.get('storyboard_revision')
 if not revision or review.get('approved_revision')!=revision:fail('revision_mismatch','Bản storyboard đang dùng khác/thiếu revision đã duyệt.')
 panels=p.get('panels',[]);shots=p.get('shots',[]);film=[x for x in panels if not x.get('empty',False)]
 if not film:fail('no_panels','Chưa kiểm kê các ô có hình.')
 ids=[x.get('id') for x in film]
 if any(type(x) is not int or x<1 for x in ids) or len(set(ids))!=len(ids):fail('panel_ids','Panel ID phải dương và không trùng.')
 coords=[(x.get('row'),x.get('column')) for x in film]
 if any(type(r) is not int or type(c) is not int or r<1 or c<1 for r,c in coords) or len(set(coords))!=len(coords):fail('panel_coordinates','Hàng/cột dương và duy nhất cho các ô phim.')
 order=[x.get('id') for x in sorted(film,key=lambda x:(str(x.get('row','')),str(x.get('column',''))))] if any(type(r) is not int or type(c) is not int for r,c in coords) else [x['id'] for x in sorted(film,key=lambda x:(x['row'],x['column']))]
 alteration=p.get('shot_alteration_review',{})
 authorized=alteration.get('approved_by')=='user' and bool(alteration.get('evidence'))
 if len(shots)!=len(film) and not authorized:fail('shot_count','Số block shot phải bằng số ô phim; gộp/tách cần lời chốt của người dùng.')
 assigned=[x.get('panel_id') for x in shots]
 if assigned!=order and not authorized:fail('panel_order','Bỏ/trùng/đổi thứ tự ô so với thứ tự đọc, chưa được chốt.')
 if any(x not in ids for x in assigned):fail('unknown_panel','Shot gọi ô không có trên board.')
 labels=[x.get('id') for x in shots]
 if labels!=list(range(1,len(shots)+1)):fail('shot_ids','Shot ID phải liên tục từ 1, không bỏ/trùng.')
 duration=p.get('seconds');cursor=0;times_ok=True
 if not numeric(duration) or not 0<duration<=30:fail('duration','Thời lượng phải hữu hạn, >0 và ≤30 giây.');times_ok=False
 for s in shots:
  a,b=s.get('start_s'),s.get('end_s')
  if not numeric(a) or not numeric(b) or b<=a:fail('bad_interval','Shot có thời gian không hợp lệ.');times_ok=False;continue
  if abs(a-cursor)>.001:fail('timeline_overlap_or_gap','Timeline phải nối tiếp từ 0; không chồng hoặc có khoảng hở.');times_ok=False
  cursor=b
 if times_ok and abs(cursor-duration)>.001:fail('timeline_total','Thời điểm kết thúc không khớp tổng giây.')
 original_intervals=[x.get('source_interval') for x in film];conflict=False;last_end=0
 for iv in original_intervals:
  if iv is None:continue
  if not isinstance(iv,list) or len(iv)!=2 or not all(numeric(v) for v in iv) or iv[1]<=iv[0]:conflict=True;continue
  if abs(iv[0]-last_end)>.001:conflict=True
  last_end=iv[1]
 for panel in film:
  iv=panel.get('source_interval');shot=next((s for s in shots if s.get('panel_id')==panel.get('id')),None)
  if isinstance(iv,list) and len(iv)==2 and shot and iv!=[shot.get('start_s'),shot.get('end_s')]:conflict=True
 if conflict:
  r=p.get('timing_resolution',{})
  if r.get('authority') not in {'explicit_user_approval','user_delegated_timing'} or not str(r.get('evidence','')).strip():fail('source_timing_conflict','Nhãn board bị chồng/trùng; cần quyết định có căn cứ, không tự coi đã duyệt.')
 prompt=p.get('video_prompt_en','');tag_ids=[int(x) for x in TAGS.findall(prompt)];blocks=list(BLOCK.finditer(prompt))
 if tag_ids!=labels:fail('prompt_shot_coverage','Prompt thiếu/trùng/sai thứ tự block Shot so với bảng.')
 if len(blocks)!=len(shots):fail('prompt_timestamp_blocks','Mỗi [Shot N] phải có [START-ENDs] riêng.')
 for i,match in enumerate(blocks):
  if i>=len(shots):break
  s=shots[i];end=blocks[i+1].start() if i+1<len(blocks) else len(prompt);text=prompt[match.start():end]
  if numeric(s.get('start_s')) and numeric(s.get('end_s')) and (abs(float(match[2])-s['start_s'])>.001 or abs(float(match[3])-s['end_s'])>.001):fail('prompt_time_mismatch','Timestamp trong prompt khác bảng shot.')
  for field in ['panel_anchor_en','camera_size_en','camera_angle_en','start_state_en','action_en','end_state_en']:
   if not str(s.get(field,'')).strip():fail('incomplete_shot',f'Shot {s.get("id")} thiếu {field}.')
   elif norm(s[field]) not in norm(text):fail('shot_detail_omitted',f'Shot {s.get("id")} thiếu dữ kiện đã khai báo: {field}.')
  if i and not s.get('transition_en'):fail('missing_transition','Shot sau cần nêu chuyển cảnh.')
  if s.get('transition_en') and norm(s['transition_en']) not in norm(text):fail('transition_omitted','Chuyển cảnh chưa có trong block prompt.')
  for action in s.get('actions',[]) if isinstance(s.get('actions'),list) else []:
   if action.get('phase','complete')=='complete':
    for field in ['completion_en','hold_en']:
     if action.get(field) and norm(action[field]) not in norm(text):fail('action_endpoint_omitted','Điểm hoàn tất/giữ trạng thái của hành động chưa có trong block prompt.')
 if len(shots)>1 and p.get('editing_mode','cuts')=='cuts':
  if one_take_conflict(prompt):fail('contradictory_one_take','Lệnh one-take/không cut mâu thuẫn storyboard nhiều shot.')
 assets=[a for a in p.get('assets',[]) if a.get('active') and a.get('connected')]
 numbers=[a.get('picture') for a in assets]
 if numbers!=list(range(1,len(numbers)+1)):fail('picture_numbering','Picture cần liên tục theo ảnh nối thật đang bật.')
 refs={int(n) for n in re.findall(r'\bPicture\s+(\d+)\b',prompt,re.I)}
 if any(n not in numbers for n in refs):fail('phantom_picture','Prompt gọi Picture chưa nạp/nối.')
 if p.get('workflow_mode')=='ref2v' and (not any(a.get('role')=='storyboard' for a in assets) or not refs):fail('missing_reference_roles','Ref2V cần storyboard đang nối và vai trò Picture trong prompt.')
 if p.get('workflow_mode')=='i2v' and any(a.get('role') in {'storyboard_grid','character_sheet'} and a.get('socket') in {'first_frame','last_frame'} for a in assets):fail('grid_to_frame','Grid/sheet không phải frame phim đầu/cuối cho I2V.')
 voices=p.get('characters',[]);byid={c.get('character_id'):c for c in voices};speech=p.get('audio',{}).get('dialogue',[])
 if len(byid)!=len(voices):fail('character_ids','Mã nhân vật bị trùng.')
 signatures={};speaking=set();same_review=p.get('shared_voice_approval',{});allow_same=isinstance(same_review,dict) and same_review.get('approved_by')=='user' and bool(same_review.get('evidence'))
 for d in speech:
  c=byid.get(d.get('character_id'))
  if not c:fail('unknown_speaker','Thoại chưa có nhân vật/hồ sơ giọng.');continue
  v=c.get('voice',{})
  speaking.add(d['character_id'])
  if v.get('status')!='approved' or not str(v.get('approval_evidence','')).strip():fail('voice_not_approved','Người nói chưa có giọng đã chốt.')
  anchor=v.get('voice_anchor_en','')
  if not str(anchor).strip() or norm(anchor) not in norm(prompt):fail('voice_anchor_missing','Prompt chưa lặp mô tả giọng của người nói.')
  spoken=d.get('spoken_text') or d.get('text','')
  if not isinstance(spoken,str) or not spoken.strip() or spoken not in prompt:fail('dialogue_modified','Thiếu/thay câu thoại/cách đọc đã khai báo trong prompt.')
  a,b=d.get('start_s'),d.get('end_s')
  if not numeric(a) or not numeric(b) or a<0 or b<=a or not numeric(duration) or b>duration+.001:fail('dialogue_timing','Thoại thiếu khoảng thời gian hợp lệ.')
  signature=norm(anchor)
  previous=signatures.get(signature)
  if previous and previous!=d['character_id'] and not allow_same:fail('identical_character_voices','Hai người dùng cùng mô tả giọng; cần phân biệt hoặc ngoại lệ được chốt.')
  signatures[signature]=d['character_id']
 speakers=sorted(speaking)
 for i,a in enumerate(speakers):
  for b in speakers[i+1:]:
   va,vb=byid[a].get('voice',{}),byid[b].get('voice',{})
   differing=sum(bool(va.get(k)) and bool(vb.get(k)) and norm(va[k])!=norm(vb[k]) for k in ['accent','pitch','timbre','pace','vocal_age','distinctive_traits'])
   if differing<2 and not allow_same:fail('voices_not_distinct','Chưa khai báo ít nhất hai đặc điểm phân biệt giọng của hai người nói.')
 for c in voices:
  v=c.get('voice',{})
  if v.get('status')=='approved' and not v.get('voice_anchor_en'):fail('missing_saved_voice','Giọng đã chốt cần câu mô tả cố định để chuyển AI.')
 if not speech:warnings.append('Không thoại: giọng pending không chặn cảnh im lặng; checker không tự thêm lời nói.')
 extra=production.validate_production(p);errors.extend(extra['errors']);warnings.extend(extra['warnings'])
 warnings.append('Chỉ kiểm cấu trúc và dữ kiện đã khai báo. Không đọc pixel, nghe giọng, xác minh lời duyệt thật hoặc bảo đảm model tuân thủ.')
 return {'valid':not errors,'errors':errors,'warnings':warnings,'declared_panels':len(film),'declared_shots':len(shots),'prompt_shot_blocks':len(blocks),'production':{k:v for k,v in extra.items() if k not in {'errors','warnings'}},'gpu_render_tested':False}

def main():
 a=argparse.ArgumentParser();a.add_argument('handoff');a=a.parse_args();p=json.loads(pathlib.Path(a.handoff).read_text(encoding='utf-8-sig'));result=validate(p);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['valid'] else 2
if __name__=='__main__':raise SystemExit(main())
