"""Read-only comparison of an expected prompt with a ComfyUI prompt embedded in video metadata."""
import argparse,hashlib,json,pathlib,re,subprocess

def shot_labels(text):
 bracket=re.findall(r'(?im)^\s*\[shot\s+(\d+)\]',text)
 if bracket:return [str(int(x)) for x in bracket]
 legacy=re.findall(r'(?im)^\s*\d[\d:.]*\s*[–-]\s*\d[\d:.]*s?\s*\|\s*SHOT\s*0*(\d+)\s*:',text)
 if legacy:return [str(int(x)) for x in legacy]
 return [str(int(x)) for x in re.findall(r'\[shot\s+(\d+)\]',text,re.I)]

def get_prompt(api,node_id=None):
 if node_id is None:
  targets=[k for k,n in api.items() if n.get('class_type') in {'MiniMaxH3ReferenceToVideo','MiniMaxH3ImageToVideo'}]
  if len(targets)!=1:raise ValueError('Không xác định duy nhất node H3; dùng --node-id để chọn ô prompt.')
  node_id=targets[0]
 seen=set()
 while True:
  if node_id in seen:raise ValueError('Vòng lặp trong dây prompt.')
  seen.add(node_id);node=api.get(str(node_id))
  if not node:raise ValueError('Không thấy node '+str(node_id))
  if node.get('class_type') not in {'MiniMaxH3ReferenceToVideo','MiniMaxH3ImageToVideo','PrimitiveStringMultiline','PrimitiveString','StringConstant'}:raise ValueError('Có node biến đổi/LLM trong dây prompt; metadata input không chứng minh output được sinh. Cần kiểm đầu ra thật.')
  data=node.get('inputs',{})
  values=[data[k] for k in ['prompt','value','text','string'] if k in data]
  if len(values)!=1:raise ValueError('Node có phép biến đổi/phối hợp hoặc không có một ô prompt duy nhất; cần kiểm đầu ra thật.')
  value=values[0]
  if isinstance(value,str):return value,str(node_id)
  if isinstance(value,list) and len(value)==2 and str(value[0]) in api:node_id=str(value[0]);continue
  raise ValueError('Không resolve được prompt bằng đọc dữ liệu; không chạy node để đoán.')

def compare(expected,actual):
 normalize=lambda s:s.replace('\r\n','\n').strip()
 a,b=normalize(expected),normalize(actual)
 return {'prompt_matches':a==b,'expected_sha256':hashlib.sha256(a.encode()).hexdigest(),'rendered_sha256':hashlib.sha256(b.encode()).hexdigest(),'expected_shot_labels':shot_labels(a),'rendered_shot_labels':shot_labels(b),'comparison':'UTF-8 text with CRLF normalized and outside whitespace trimmed','gpu_render_tested':False,'audio_listened':False}

def main():
 p=argparse.ArgumentParser();p.add_argument('--video',required=True);p.add_argument('--expected-prompt',required=True);p.add_argument('--node-id');p.add_argument('--output');a=p.parse_args()
 r=subprocess.run(['ffprobe','-v','error','-show_entries','format_tags=prompt','-of','json',a.video],capture_output=True,text=True,encoding='utf-8',check=True)
 tags=json.loads(r.stdout).get('format',{}).get('tags',{});raw=tags.get('prompt')
 if not raw:raise ValueError('Video không kèm metadata prompt; không thể suy ra prompt từ hình ảnh.')
 actual,node=get_prompt(json.loads(raw),a.node_id);expected=pathlib.Path(a.expected_prompt).read_text(encoding='utf-8-sig');report=compare(expected,actual);report['resolved_prompt_source_node']=node
 text=json.dumps(report,ensure_ascii=False,indent=2)
 if a.output:pathlib.Path(a.output).write_text(text+'\n',encoding='utf-8')
 print(text);return 0 if report['prompt_matches'] else 2
if __name__=='__main__':raise SystemExit(main())
