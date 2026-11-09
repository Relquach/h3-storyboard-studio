"""Install only the dependencies and byte-identical original OpenH3 workflow."""
import argparse,datetime,hashlib,importlib.metadata,importlib.util,json,os,pathlib,re,shutil,stat,subprocess,sys,tempfile,time,traceback,urllib.request,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_PORTABLE=r'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
spec=importlib.util.spec_from_file_location('openh3_downloads',ROOT/'scripts/downloads.py');dl=importlib.util.module_from_spec(spec);spec.loader.exec_module(dl)
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

def safe_extract(archive,target):
 target=pathlib.Path(target).resolve();target.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(archive) as z:
  for item in z.infolist():
   name=item.filename
   if '\\' in name or ':' in name or pathlib.PurePosixPath(name).is_absolute() or '..' in pathlib.PurePosixPath(name).parts:raise ValueError('Unsafe ZIP path')
   if stat.S_ISLNK(item.external_attr>>16):raise ValueError('Symlinks are not accepted in node archives')
   dest=(target/name).resolve()
   if not dest.is_relative_to(target):raise ValueError('ZIP path escapes staging')
  z.extractall(target)
 roots=[p for p in target.iterdir() if p.is_dir()]
 if len(roots)!=1 or not (roots[0]/'__init__.py').is_file():raise ValueError('Node ZIP must contain one repository root with __init__.py')
 return roots[0]

def fingerprint(root):
 h=hashlib.sha256()
 for f in sorted(root.rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts and '.git' not in f.parts and f.name!='.openh3-installed.json':
   h.update(f.relative_to(root).as_posix().encode());h.update(b'\0');h.update(f.read_bytes());h.update(b'\0')
 return h.hexdigest()

def install_node(comfy,pack):
 archive=ROOT/'vendor'/pack['archive']
 dl.download(pack['url'],archive,pack['bytes'],pack['sha256'])
 custom=comfy/'custom_nodes';custom.mkdir(exist_ok=True)
 candidates=[p for p in custom.iterdir() if p.is_dir() and p.name.removesuffix('-main').removesuffix('-master').casefold()==pack['folder'].casefold()]
 if len(candidates)>1:raise RuntimeError('Có nhiều bản node '+pack['folder']+'. Chuyển bản trùng ra ngoài custom_nodes rồi chạy lại: '+', '.join(str(p) for p in candidates))
 target=candidates[0] if candidates else custom/pack['folder'];backup=None
 with tempfile.TemporaryDirectory(prefix='openh3-node-',dir=str(comfy/'user/OpenH3_Original')) as stage:
  source=safe_extract(archive,pathlib.Path(stage)/'unpack');fp=fingerprint(source)
  if target.exists() and fingerprint(target)==fp:print('Giữ node đúng bản:',target.name);return
  if target.exists():
   backup=comfy/'user/OpenH3_Original/backups'/(target.name+'-'+str(time.time_ns()));backup.parent.mkdir(parents=True,exist_ok=True);target.rename(backup)
  try:
   shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','.git'))
   (target/'.openh3-installed.json').write_text(json.dumps({'revision':pack['revision'],'sha256':pack['sha256']}),encoding='utf-8')
  except Exception:
   if target.exists():shutil.rmtree(target)
   if backup:backup.rename(target)
   raise
  print('Đã cài node:',target.name,'; backup:',backup or 'không cần',flush=True)

class Tee:
 def __init__(self,stream,log):self.stream=stream;self.log=log
 def write(self,text):self.stream.write(text);self.log.write(text);self.log.flush()
 def flush(self):self.stream.flush();self.log.flush()

def original_bytes(manifest):
 data=(ROOT/'workflows'/manifest['workflow']).read_bytes()
 if len(data)!=manifest['workflow_bytes'] or hashlib.sha256(data).hexdigest()!=manifest['workflow_sha256']:
  raise RuntimeError('JSON nguồn không còn đúng bản gốc. Giải nén lại bộ cài; không tự chỉnh file nguồn này.')
 return data

def core_features(comfy,manifest):
 files=[comfy/'nodes.py']+list((comfy/'comfy_extras').glob('nodes_*.py'))
 text='\n'.join(f.read_text(encoding='utf-8') for f in files if f.is_file())
 result={name:name in text for name in manifest['core_required_types']}
 sd=comfy/'comfy/sd.py';vae=comfy/'comfy/ldm/minimax/vae.py';prefetch=comfy/'comfy/model_prefetch.py'
 result['native_vae_output_dtype']=sd.is_file() and 'def vae_output_dtype(' in sd.read_text(encoding='utf-8')
 result['native_h3_chunked_io']=vae.is_file() and 'comfy_has_chunked_io = True' in vae.read_text(encoding='utf-8')
 result['native_model_prefetch_cleanup']=prefetch.is_file() and 'def cleanup_prefetch_queues(' in prefetch.read_text(encoding='utf-8')
 result['python_3_12_or_newer']=sys.version_info>=(3,12)
 return result

def preflight(comfy,manifest):
 original_bytes(manifest);features=core_features(comfy,manifest);missing=[k for k,v in features.items() if not v]
 if missing:raise RuntimeError('ComfyUI/Python hiện tại thiếu: '+', '.join(missing)+'. Dùng updater chính thức update/update_comfyui.bat trong Portable rồi kiểm tra lại. Bộ cài không patch core/Torch hoặc đổi workflow.')
 print('Core/Python có các tính năng native cần dùng; cần mở lại để kiểm tra schema sau cài.',flush=True)

def dependencies(comfy):
 deps=[('PIL','Pillow','10.3.0'),('matplotlib','matplotlib','3.8.0'),('color_matcher','color-matcher','0.6.0'),('mss','mss','9.0.0'),('cv2','opencv-python-headless','4.8.0'),('imageio_ffmpeg','imageio-ffmpeg','0.6.0'),('av','av','17.0.0')]
 requests=[];allow=set()
 def version(value):return tuple(int(x) for x in re.findall(r'\d+',value)[:3])
 def norm(value):return re.sub('[-_.]+','-',value).lower()
 for module,pkg,minimum in deps:
  distribution=pkg
  if pkg=='opencv-python-headless' and any(norm(d.metadata.get('Name',''))=='opencv-python' for d in importlib.metadata.distributions()):distribution='opencv-python'
  need=importlib.util.find_spec(module) is None
  if not need:
   try:need=version(importlib.metadata.version(distribution))<version(minimum)
   except importlib.metadata.PackageNotFoundError:need=True
  if need:requests.append(distribution+'>='+minimum);allow.add(norm(distribution))
 if not requests:return
 constraint=comfy/'user/OpenH3_Original/runtime-constraints.txt'
 constraint.write_text('\n'.join(sorted({d.metadata['Name']+'=='+d.version for d in importlib.metadata.distributions() if d.metadata.get('Name') and norm(d.metadata['Name']) not in allow}))+'\n',encoding='utf-8')
 cmd=[sys.executable,'-I','-m','pip','install','--disable-pip-version-check','--prefer-binary','--upgrade-strategy','only-if-needed','--constraint',str(constraint)]+requests
 print('Bổ sung dependency cần thiết:',', '.join(requests),flush=True)
 with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1) as process:
  for line in process.stdout:print(line,end='',flush=True)
  if process.wait():raise subprocess.CalledProcessError(process.returncode,cmd)

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
 data=original_bytes(manifest);folder=comfy/'user/default/workflows/OpenH3_Original';folder.mkdir(parents=True,exist_ok=True);dest=folder/manifest['workflow']
 if dest.exists() and dest.read_bytes()!=data:
  backup=comfy/'user/OpenH3_Original/backups'/str(time.time_ns());backup.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup/dest.name)
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

def inspect_install(comfy,manifest,port=8188,verify=False):
 result={'workflow_sha256':hashlib.sha256(original_bytes(manifest)).hexdigest(),'workflow_original_unchanged':True,'models':{},'missing_models':[],'core_features':core_features(comfy,manifest),'schema':None,'gpu_render_tested':False,'input_note':'Chọn video thật ở Load Video #1. Tên video demo và preview trong JSON gốc được giữ nguyên; bộ cài không kèm video demo.'}
 installed=comfy/'user/default/workflows/OpenH3_Original'/manifest['workflow']
 result['installed_workflow_sha256']=dl.sha256(installed) if installed.is_file() else None
 result['installed_workflow_original_unchanged']=result['installed_workflow_sha256']==manifest['workflow_sha256']
 for m in manifest['models']:
  f=direct_model(comfy,m,verify)
  if f:result['models'][m['id']]=str(f)
  else:result['missing_models'].append(m['destination'])
 try:
  with urllib.request.urlopen(f'http://127.0.0.1:{port}/object_info',timeout=15) as response:obj=json.load(response)
  result['schema']={name:name in obj for name in manifest['required_types']};result['missing_node_types']=[x for x,v in result['schema'].items() if not v]
  fields=[(4,'VAELoader','vae_name','video_vae'),(7,'VAELoader','vae_name','audio_vae'),(30,'LatentUpscaleModelLoader','model_name','latent_upscale'),(12,'TAOpenH3PromptEncodeRelease','clip_name','encoder'),(13,'TAOpenH3RefineRelease','unet_name','singularity_v2'),(13,'TAOpenH3RefineRelease','main_lora','regenerate_lora'),(13,'TAOpenH3RefineRelease','curve_branches','curve_branches')]
  byid={m['id']:m for m in manifest['models']};result['model_enum']={}
  for nid,typ,name,mid in fields:
   opts=combo_options(obj.get(typ,{}),name);result['model_enum'][str(nid)+':'+name]=opts is not None and byid[mid]['destination'] in opts
 except (OSError,ValueError) as exc:result['runtime_note']='Chưa đọc được schema localhost:'+str(port)+'. Mở lại ComfyUI và chạy KIEM_TRA. '+str(exc)
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['install','nodes','check']);p.add_argument('--portable',default=DEFAULT_PORTABLE);p.add_argument('--port',type=int,default=8188);p.add_argument('--hash',action='store_true',help='Hash lại model khi check (tốn thời gian)');a=p.parse_args()
 portable=portable_path(a.portable);comfy=portable/'ComfyUI';manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'));(comfy/'user/OpenH3_Original').mkdir(parents=True,exist_ok=True)
 print('Portable đích:',portable,flush=True)
 if a.action=='check':
  result=inspect_install(comfy,manifest,a.port,a.hash);report=comfy/'user/OpenH3_Original/local-check.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
  ok=result['installed_workflow_original_unchanged'] and not result['missing_models'] and all(result['core_features'].values()) and result['schema'] is not None and not result.get('missing_node_types') and all(result.get('model_enum',{}).values())
  if not ok:return 2
  print('Model/node/schema đủ; chọn video thật trước khi chạy. Chưa xác minh GPU render.');return 0
 preflight(comfy,manifest);dependencies(comfy)
 for pack in manifest['nodes']:install_node(comfy,pack)
 if a.action=='nodes':print('Đã cài node, mở lại ComfyUI để kiểm tra import.');return 0
 install_models(comfy,manifest);dest=copy_original_workflow(comfy,manifest)
 (ROOT/'local.json').write_text(json.dumps({'portable':str(portable),'workflow':str(dest)},ensure_ascii=False,indent=2),encoding='utf-8')
 print('\nHoàn tất cài file. Mở lại ComfyUI, chạy KIEM_TRA.bat, mở workflow trong OpenH3_Original.',flush=True)
 print('Chọn video tại #1; kích thước đầu ra tại #6. Đọc docs/HUONG_DAN.pdf. JSON gốc và skill được giữ nguyên.',flush=True);return 0
if __name__=='__main__':
 logs=ROOT/'logs';logs.mkdir(exist_ok=True);logpath=logs/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.txt');oldout,olderr=sys.stdout,sys.stderr
 with logpath.open('w',encoding='utf-8') as log:
  sys.stdout=Tee(sys.stdout,log);sys.stderr=Tee(sys.stderr,log)
  try:raise SystemExit(main())
  except Exception as exc:print('LỖI:',exc,file=sys.stderr);traceback.print_exc(file=log);print('Log:',logpath,file=sys.stderr);raise SystemExit(1)
  finally:sys.stdout,sys.stderr=oldout,olderr
