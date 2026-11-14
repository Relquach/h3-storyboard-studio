"""Declared action-state/audio checks; no model execution, pixel evaluation or speaker verification."""
import math,re,unicodedata

def normalize(s):
 return ''.join(c for c in unicodedata.normalize('NFD',str(s).casefold().replace('đ','d')) if unicodedata.category(c)!='Mn')

def prompt_hygiene(text):
 errors=[];clean=normalize(text)
 if re.search(r'(?m)^\s*```',text):errors.append({'code':'prompt_code_fence','message':'Ô prompt có code fence; chỉ nạp nội dung TXT sạch.'})
 if re.search(r'(?im)\b(?:bat|bypass|enable|disable)\s+loaders?\s*[:=\[]',clean) or re.search(r'chi\s+sao\s+chep|tao\s+take\s+moi|(?:paste|copy)\s+(?:only\s+)?(?:the\s+)?(?:content|text|block)\s+(?:below|into)',clean):errors.append({'code':'prompt_ui_instructions','message':'Hướng dẫn UI/take/sao chép bị trộn vào prompt model.'})
 if re.search(r'#\d+\s*(?:=|→|->)',text):errors.append({'code':'prompt_node_assignments','message':'Lệnh #node=value nằm trong prompt model thay vì file bàn giao.'})
 return errors

def number(x):return type(x) in (float,int) and math.isfinite(x)
def consent(obj):return isinstance(obj,dict) and obj.get('approved_by')=='user' and bool(obj.get('evidence'))

def validate_production(p):
 errors=prompt_hygiene(p.get('video_prompt_en',''));warnings=[]
 def fail(code,message):errors.append({'code':code,'message':message})
 initial=p.get('initial_states',{})
 if not isinstance(initial,dict):fail('invalid_initial_states','initial_states phải là bảng object_id → thuộc tính.');initial={}
 state={k:dict(v) for k,v in initial.items() if isinstance(v,dict)};events={};finished=set()
 def check(snapshot,where):
  if not isinstance(snapshot,dict):fail('invalid_state',where+' phải là bảng trạng thái.');return
  for obj,attrs in snapshot.items():
   if obj not in state:fail('unknown_state_object','Thiếu trạng thái đầu của '+str(obj));continue
   if not isinstance(attrs,dict):fail('invalid_state',str(obj)+' thiếu bảng thuộc tính.');continue
   for key,value in attrs.items():
    if state[obj].get(key,object())!=value:fail('state_reset',where+': '+str(obj)+'.'+str(key)+' không khớp kết quả trước đó.')
 for shot in p.get('shots',[]):
  actions=shot.get('actions')
  if not isinstance(actions,list):fail('missing_action_plan','Shot cần actions; shot tĩnh khai báo [] và hold_states/camera_only.');continue
  if not actions and not shot.get('camera_only') and not shot.get('hold_states'):fail('missing_hold_state','Shot không thao tác cần nêu trạng thái đang giữ, không tạo động tác lấp giờ.')
  for action in actions:
   eid=action.get('event_id');phase=action.get('phase','complete');count=action.get('occurrences',1)
   if not isinstance(eid,str) or not eid.strip():fail('missing_event_id','Hành động cần event_id ổn định.');continue
   if phase not in {'start','continue','complete'}:fail('invalid_event_phase','Pha dùng start/continue/complete.');continue
   if eid in finished:fail('completed_event_replayed','Sự kiện đã hoàn tất bị thực hiện lại: '+eid)
   if phase=='start' and eid in events:fail('action_restarted','Sự kiện đang chạy lại bị start từ đầu: '+eid)
   if phase=='continue' and eid not in events:fail('action_continue_without_start','Pha continue chưa có start: '+eid)
   if type(count) is not int or count<1:fail('invalid_action_count','Số lần hành động phải dương.')
   elif count>1 and not consent(action.get('repeat_approval')):fail('unapproved_action_repeat','Hành động lặp nhiều lần cần ý định người dùng/kịch bản làm căn cứ.')
   before,after=action.get('state_before'),action.get('state_after')
   if not before or not after:fail('missing_action_states','Hành động cần trạng thái vào/ra, không chỉ chữ once.')
   check(before or {},'Shot '+str(shot.get('id'))+' trước '+eid)
   if not isinstance(after,dict):after={}
   for obj,attrs in after.items():
    if obj not in state:fail('unknown_state_object','Thiếu trạng thái đầu của '+str(obj));continue
    if not isinstance(attrs,dict):fail('invalid_state','Trạng thái ra phải là bảng thuộc tính.');continue
    state[obj].update(attrs)
   if phase=='complete':
    finished.add(eid)
    for field in ['completion_en','hold_en']:
     if not str(action.get(field,'')).strip():fail('missing_completion_or_hold','Hành động hoàn tất cần '+field)
   events[eid]=phase
  if shot.get('hold_states'):check(shot['hold_states'],'Trạng thái giữ sau shot '+str(shot.get('id')))
 unfinished=set(events)-finished-set(p.get('carry_actions_to_next_clip',[]))
 if unfinished:fail('unfinished_events','Hành động chưa hoàn tất và chưa khai báo chuyển tiếp: '+', '.join(sorted(unfinished)))
 if p.get('expected_final_states'):check(p['expected_final_states'],'Trạng thái kết thúc clip')
 audio=p.get('audio',{});dialogue=audio.get('dialogue',[]);chars={c.get('character_id'):c for c in p.get('characters',[])};seen_ids=set();seen_lines={};last_end=-1;spoken=set()
 for d in dialogue:
  uid=d.get('utterance_id')
  if not uid or uid in seen_ids:fail('duplicate_utterance_id','Mỗi lượt lời cần ID duy nhất, không copy lại cho mỗi cut.')
  seen_ids.add(uid);text=d.get('spoken_text',d.get('text',''))
  if d.get('spoken_text') and d['spoken_text']!=d.get('text') and not consent(d.get('pronunciation_approval')):fail('unapproved_spoken_text','Bản để đọc khác câu gốc cần cách đọc đã chốt.')
  key=(d.get('character_id'),normalize(text).strip())
  if key in seen_lines and not consent(d.get('repeat_approval')):fail('repeated_dialogue','Câu thoại bị lặp ở nhiều lượt mà chưa có ý định rõ.')
  seen_lines[key]=uid
  a,b=d.get('start_s'),d.get('end_s')
  if number(a) and number(b):
   if a<last_end-.001 and not consent(audio.get('overlap_approval')):fail('overlapping_dialogue','Các lượt lời chồng nhau khi chưa chủ ý hội thoại đồng thời.')
   last_end=max(last_end,b)
   timing=d.get('timing_check',{});duration=timing.get('duration_s')
   if timing.get('method') not in {'measured_audio','estimate'} or not number(duration) or duration<=0 or not timing.get('basis'):fail('missing_speech_budget','Cần thời lượng lời đã đo hoặc ước lượng có căn cứ.')
   elif duration>b-a+.001:fail('speech_over_budget','Lời nói cần nhiều thời gian hơn slot; không tự ép tốc độ hoặc cắt chữ.')
   elif timing.get('method')=='estimate':warnings.append('Ngân sách lời nói '+str(uid)+' chỉ là ước lượng, cần nghe thử.')
  char=chars.get(d.get('character_id'))
  if not char:continue
  cid=char.get('character_id');spoken.add(cid);voice=char.get('voice',{});mode=voice.get('generation_mode')
  if mode not in {'native_exploratory','audio_reference','external_voiceover'} or not voice.get('delivery_choice_evidence'):fail('missing_voice_delivery_choice','Chưa chốt cách thực hiện giọng ngoài mô tả chữ.')
  if mode=='native_exploratory':
   warnings.append('Native audio của '+str(cid)+' là thử; mô tả được duyệt không chứng minh giọng đã đúng.')
   if voice.get('strict_identity_required'):fail('native_cannot_verify_identity_lock','Native prompt-only không đáp ứng cam kết khóa giọng xuyên clip.')
  if mode=='audio_reference':
   ref=voice.get('reference_audio') or {}
   if not ref.get('asset') or ref.get('connected') is not True or not ref.get('socket'):fail('unconnected_voice_reference','Mẫu giọng chưa có tài sản/cổng nối thật.')
  if mode=='external_voiceover' and not voice.get('delivery_plan'):fail('missing_external_audio_plan','Chưa có cách thu/TTS và nạp/dựng tiếng vào clip.')
  verification=voice.get('verification') or {}
  if verification.get('status')=='accepted' and (not verification.get('audio_asset') or not verification.get('evidence')):fail('false_voice_verification','Giọng được ghi đã nghe duyệt nhưng không có audio/bằng chứng.')
 return {'errors':errors,'warnings':warnings,'completed_events':sorted(finished),'final_declared_states':state,'spoken_characters':sorted(spoken),'media_semantics_verified':False}
