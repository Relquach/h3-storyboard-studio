"""Install only model dependencies and copy the original OmniRef JSON byte-for-byte."""
import argparse,ast,datetime,hashlib,importlib.util,json,os,pathlib,shutil,subprocess,sys,time,traceback,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_PORTABLE=r'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
spec=importlib.util.spec_from_file_location('omniref_downloads',ROOT/'scripts/downloads.py');dl=importlib.util.module_from_spec(spec);spec.loader.exec_module(dl)
def portable_path(value):
 p=pathlib.Path(value).expanduser()
 for q in dict.fromkeys([p,p/'ComfyUI_windows_portable',p.parent if p.name.lower()=='comfyui' else p]):
  if (q/'python_embeded/python.exe').is_file() and (q/'ComfyUI/main.py').is_file():return q.resolve()
 raise ValueError('Chọn THƯ MỤC chứa python_embeded và ComfyUI. Không chọn JSON.')

def model_roots(comfy,category):
 roots=[comfy/'models'/category];cfg=comfy/'extra_model_paths.yaml'
 if cfg.exists():
  import yaml
  for entry in (yaml.safe_load(cfg.read_text(encoding='utf-8-sig')) or {}).values():
   if not isinstance(entry,dict):continue
   base=pathlib.Path(os.path.expandvars(os.path.expanduser(str(entry.get('base_path',comfy)))))
   if not base.is_absolute():base=comfy/base
   for key in ([category,'unet'] if category=='diffusion_models' else [category]):
    for line in str(entry.get(key,'')).splitlines():
     if line.strip():
      q=pathlib.Path(os.path.expandvars(os.path.expanduser(line.strip())));roots.append(q if q.is_absolute() else base/q)
 return list(dict.fromkeys(roots))

class Tee:
 def __init__(self,stream,log):self.stream=stream;self.log=log
 def write(self,text):self.stream.write(text);self.log.write(text);self.log.flush()
 def flush(self):self.stream.flush();self.log.flush()

def original_bytes(manifest):
 data=(ROOT/'workflows'/manifest['workflow']).read_bytes()
 if len(data)!=manifest['workflow_bytes'] or hashlib.sha256(data).hexdigest()!=manifest['workflow_sha256']:
  raise RuntimeError('JSON nguồn không còn đúng bản gốc. Giải nén lại bộ cài; không tự chỉnh file nguồn này.')
 return data

def file_matches(file,model,verify):
 if not file.is_file() or file.stat().st_size!=model['bytes']:return False
 if verify:
  print('Kiểm tra SHA256:',file,flush=True)
  return dl.sha256(file)==model['sha256']
 return True

def direct_model(comfy,model,verify=False):
 for base in model_roots(comfy,model['category']):
  f=base/model['destination']
  if f.exists():
   if not file_matches(f,model,verify):raise RuntimeError('Model đúng tên nhưng sai dung lượng/SHA256: '+str(f)+'. Giữ nguyên file này; chuyển nó ra ngoài hoặc đổi tên rồi chạy lại.')
   return f
 return None

def reusable_model(comfy,model):
 accepted={model['destination'].casefold()}|{x.casefold() for x in model.get('aliases',[])}
 for base in model_roots(comfy,model['category']):
  if not base.exists():continue
  for f in base.rglob('*.safetensors'):
   if f.name.casefold() in accepted and file_matches(f,model,True):return f
 return None

def make_model_alias(source,dest,model):
 source=pathlib.Path(source);dest=pathlib.Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():
  if not file_matches(dest,model,True):raise RuntimeError('Đích alias đã tồn tại và khác model: '+str(dest))
  return 'existing'
 if not file_matches(source,model,True):raise RuntimeError('Nguồn alias không đúng SHA256: '+str(source))
 try:os.link(source,dest);method='hardlink'
 except OSError:
  if shutil.disk_usage(dest.parent).free<model['bytes']+64*1024**2:raise RuntimeError('Alias khác ổ cần sao chép nhưng không đủ dung lượng: '+str(dest))
  part=dest.with_name(dest.name+'.alias-'+str(time.time_ns()))
  try:
   shutil.copy2(source,part)
   if not file_matches(part,model,True):raise RuntimeError('Alias copy checksum mismatch')
   if dest.exists():raise RuntimeError('Đích alias xuất hiện trong lúc sao chép; không ghi đè.')
   # link creates the destination exclusively on the same filesystem as staging.
   os.link(part,dest)
  finally:part.unlink(missing_ok=True)
  method='copy'
 print('Dùng lại model bằng '+method+': '+str(dest),flush=True);return method

def install_models(comfy,manifest):
 missing=[];reuse=[]
 for m in manifest['models']:
  direct=direct_model(comfy,m,True)
  if direct:print('Có model dùng trực tiếp:',direct,flush=True);continue
  source=reusable_model(comfy,m)
  if source:reuse.append((m,source))
  else:missing.append(m)
 needed=sum(max(0,m['bytes']-((comfy/'models'/m['category']/(m['destination']+'.part')).stat().st_size if (comfy/'models'/m['category']/(m['destination']+'.part')).exists() else 0)) for m in missing)
 print('Cần tải khoảng %.2f GB; SSD trống %.2f GB.'%(needed/1e9,shutil.disk_usage(comfy).free/1e9),flush=True)
 if needed>0 and shutil.disk_usage(comfy).free<needed+512*1024**2:raise RuntimeError('Không đủ dung lượng cho model còn thiếu; cần thêm chỗ cho output/pagefile.')
 for m,source in reuse:make_model_alias(source,comfy/'models'/m['category']/m['destination'],m)
 for m in missing:
  url='https://huggingface.co/'+m['repo']+'/resolve/'+m['revision']+'/'+m['file'];dl.download(url,comfy/'models'/m['category']/m['destination'],m['bytes'],m['sha256'])

def copy_original_workflow(comfy,manifest):
 data=original_bytes(manifest);folder=comfy/'user/default/workflows/FastH3_OmniRef_Original';folder.mkdir(parents=True,exist_ok=True);dest=folder/manifest['workflow']
 if dest.exists() and dest.read_bytes()!=data:
  backup=comfy/'user/FastH3_OmniRef_Original/backups'/str(time.time_ns());backup.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup/dest.name)
 if not dest.exists() or dest.read_bytes()!=data:
  staging=dest.with_name(dest.name+'.new-'+str(time.time_ns()))
  try:staging.write_bytes(data);staging.replace(dest)
  finally:staging.unlink(missing_ok=True)
 if dest.read_bytes()!=data:raise RuntimeError('Workflow copy không còn giống nguồn.')
 print('Đã chép workflow gốc, đúng từng byte:',dest,flush=True);return dest

def combo_options(definition,name):
 for section in ['required','optional']:
  field=definition.get('input',{}).get(section,{}).get(name)
  if not field:continue
  if isinstance(field[0],list):return field[0]
  if len(field)>1 and isinstance(field[1],dict):return field[1].get('options')
 return None

def core_features(comfy,manifest):
 files=[comfy/'nodes.py']+list((comfy/'comfy_extras').glob('nodes_*.py'));text='\n'.join(p.read_text(encoding='utf-8') for p in files if p.is_file())
 return {name:name in text for name in manifest['core_required_types']}

def file_compatibility_warnings(comfy,manifest):
 file=comfy/'comfy_extras/nodes_video.py'
 if not file.exists():return []
 tree=ast.parse(file.read_text(encoding='utf-8'));cls=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CreateVideo'),None)
 if cls and any(isinstance(n,ast.Call) and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='chroma_subsampling' for n in ast.walk(cls)):
  return [{'node':130,'field':'chroma_subsampling','saved_value':'none','required_ui_action':'Chọn auto tại Create Video #130 trước khi Run. JSON nguồn giữ nguyên.','note':'Core mới có schema chroma_subsampling khác bản workflow đang lưu.'}]
 return []

def preflight(comfy,manifest):
 original_bytes(manifest);missing=[k for k,v in core_features(comfy,manifest).items() if not v]
 if missing:raise RuntimeError('Core thiếu: '+', '.join(missing)+'. Dùng updater chính thức của Portable rồi thử lại. Bộ cài không thay core/Torch hoặc sửa workflow.')
 for warning in file_compatibility_warnings(comfy,manifest):print('LƯU Ý TƯƠNG THÍCH:',warning['required_ui_action'],flush=True)

def runtime_compatibility_warnings(obj):
 choices=combo_options(obj.get('CreateVideo',{}),'chroma_subsampling')
 if choices is not None and 'none' not in choices:return [{'node':130,'field':'chroma_subsampling','original':'none','allowed_values':choices,'ui_action':'Chọn auto trên giao diện Create Video #130; không cần sửa file JSON nguồn.'}]
 return []

def inspect_install(comfy,manifest,port=8188,verify=False):
 result={'workflow_original_unchanged':True,'workflow_sha256':hashlib.sha256(original_bytes(manifest)).hexdigest(),'core_features':core_features(comfy,manifest),'models':{},'missing_models':[],'schema':None,'compatibility_warnings':file_compatibility_warnings(comfy,manifest),'gpu_render_tested':False,'input_note':'Chọn ảnh storyboard #137 và sheet nhân vật #149 khớp prompt. Ảnh riêng không có trong bộ cài.'}
 installed=comfy/'user/default/workflows/FastH3_OmniRef_Original'/manifest['workflow'];result['installed_workflow_original_unchanged']=installed.is_file() and dl.sha256(installed)==manifest['workflow_sha256']
 for m in manifest['models']:
  f=direct_model(comfy,m,verify)
  if f:result['models'][m['id']]=str(f)
  else:result['missing_models'].append(m['destination'])
 try:
  with urllib.request.urlopen(f'http://127.0.0.1:{port}/object_info',timeout=15) as r:obj=json.load(r)
  result['schema']={name:name in obj for name in manifest['required_types']};result['missing_node_types']=[x for x,v in result['schema'].items() if not v];result['compatibility_warnings']=runtime_compatibility_warnings(obj)
  byid={m['id']:m for m in manifest['models']};fields=[('UNETLoader','unet_name','omniref'),('CLIPLoader','clip_name','encoder'),('VAELoader','vae_name','video_vae'),('VAELoader','vae_name','audio_vae')];result['model_enum']={}
  for typ,field,mid in fields:
   opts=combo_options(obj.get(typ,{}),field);result['model_enum'][mid]=opts is not None and byid[mid]['destination'] in opts
 except (OSError,ValueError) as exc:result['runtime_note']='Mở ComfyUI ở cổng '+str(port)+' rồi chạy lại KIEM_TRA. '+str(exc)
 result['installation_ready']=result['installed_workflow_original_unchanged'] and not result['missing_models'] and all(result['core_features'].values()) and result['schema'] is not None and not result.get('missing_node_types') and all(result.get('model_enum',{}).values())
 result['original_runtime_compatibility']='requires_ui_change' if result['compatibility_warnings'] else 'no_known_schema_issue_detected';return result

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['install','check']);p.add_argument('--portable',default=DEFAULT_PORTABLE);p.add_argument('--port',type=int,default=8188);p.add_argument('--hash',action='store_true');a=p.parse_args();portable=portable_path(a.portable);comfy=portable/'ComfyUI';manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'));(comfy/'user/FastH3_OmniRef_Original').mkdir(parents=True,exist_ok=True);print('Portable đích:',portable,flush=True)
 if a.action=='check':
  r=inspect_install(comfy,manifest,a.port,a.hash);(comfy/'user/FastH3_OmniRef_Original/local-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False,indent=2))
  if not r['installation_ready']:return 2
  print('Phụ thuộc đã đủ. Chọn hai ảnh thật; xem các lưu ý tương thích trước khi Run. Không phải xác nhận render GPU.');return 0
 preflight(comfy,manifest);install_models(comfy,manifest);dest=copy_original_workflow(comfy,manifest);(ROOT/'local.json').write_text(json.dumps({'portable':str(portable),'workflow':str(dest)},ensure_ascii=False,indent=2),encoding='utf-8')
 print('Đã cài model và chép workflow đúng từng byte. Không có custom node hoặc LoRA cần cài.',flush=True)
 for warning in file_compatibility_warnings(comfy,manifest):print('LƯU Ý TƯƠNG THÍCH:',warning['required_ui_action'],flush=True)
 print('Mở lại ComfyUI, chạy KIEM_TRA.bat, mở FastH3_OmniRef_Original và chọn ảnh #137/#149. Đọc docs/HUONG_DAN.pdf.',flush=True);return 0
if __name__=='__main__':
 logs=ROOT/'logs';logs.mkdir(exist_ok=True);logpath=logs/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.txt');oldout,olderr=sys.stdout,sys.stderr
 with logpath.open('w',encoding='utf-8') as log:
  sys.stdout=Tee(sys.stdout,log);sys.stderr=Tee(sys.stderr,log)
  try:raise SystemExit(main())
  except Exception as exc:print('LỖI:',exc,file=sys.stderr);traceback.print_exc(file=log);print('Log:',logpath,file=sys.stderr);raise SystemExit(1)
  finally:sys.stdout,sys.stderr=oldout,olderr
