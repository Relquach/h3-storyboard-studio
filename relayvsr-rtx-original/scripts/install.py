"""Install dependencies and copy the original RelayVSR/RTX/DLSS graph without modifying it."""
import argparse,datetime,hashlib,importlib.metadata,importlib.util,json,os,pathlib,platform,re,shutil,stat,subprocess,sys,tempfile,time,traceback,urllib.request,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_PORTABLE=r'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
spec=importlib.util.spec_from_file_location('relay_downloads',ROOT/'scripts/downloads.py');dl=importlib.util.module_from_spec(spec);spec.loader.exec_module(dl)
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
 if (target/'__init__.py').is_file():return target
 roots=[p for p in target.iterdir() if p.is_dir()]
 if len(roots)!=1 or not (roots[0]/'__init__.py').is_file():raise ValueError('Node ZIP must contain one repository root with __init__.py')
 return roots[0]

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
 data=original_bytes(manifest);folder=comfy/'user/default/workflows/RelayVSR_RTX_Original';folder.mkdir(parents=True,exist_ok=True);dest=folder/manifest['workflow']
 if dest.exists() and dest.read_bytes()!=data:
  backup=comfy/'user/RelayVSR_RTX_Original/backups'/str(time.time_ns());backup.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup/dest.name)
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
 files=[comfy/'nodes.py']+list((comfy/'comfy_extras').glob('nodes_*.py'));text='\n'.join(f.read_text(encoding='utf-8') for f in files if f.is_file())
 return {name:name in text for name in manifest['core_required_types']}

def preflight(comfy,manifest,files_only=False):
 original_bytes(manifest);missing=[k for k,v in core_features(comfy,manifest).items() if not v]
 if missing:raise RuntimeError('Core thiếu '+', '.join(missing)+'. Cập nhật ComfyUI bằng updater chính thức; bộ cài không thay core/Torch.')
 if files_only:return
 if sys.platform!='win32':raise RuntimeError('Workflow đầy đủ có runtime DLSS5/D3D12 cho Windows. Chỉ --files-only dùng để kiểm tra file ngoài Windows.')
 import torch
 version=torch.version.cuda
 if not torch.cuda.is_available():raise RuntimeError('PyTorch của Portable chưa có CUDA hoạt động. Cần môi trường NVIDIA đang chạy được ComfyUI.')
 if version is None or tuple(map(int,version.split('.')[:2]))<(13,0):raise RuntimeError('Node NVIDIA VFX0.2.1 yêu cầu PyTorch CUDA13.0+. Dùng Portable/CUDA phù hợp; bộ cài không tự nâng Torch.')
 if platform.machine().lower() not in ['amd64','x86_64']:raise RuntimeError('Bộ cài này dành cho Windows x64 trên máy RTX của bạn.')

def run_pip(comfy,requests,allow):
 def norm(n):return re.sub('[-_.]+','-',n).lower()
 constraint=comfy/'user/RelayVSR_RTX_Original/runtime-constraints.txt';constraint.write_text('\n'.join(sorted({d.metadata['Name']+'=='+d.version for d in importlib.metadata.distributions() if d.metadata.get('Name') and norm(d.metadata['Name']) not in allow}))+'\n')
 cmd=[sys.executable,'-I','-m','pip','install','--disable-pip-version-check','--prefer-binary','--upgrade-strategy','only-if-needed','--constraint',str(constraint)]+requests
 with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1) as process:
  for line in process.stdout:print(line,end='',flush=True)
  if process.wait():raise subprocess.CalledProcessError(process.returncode,cmd)

def dependencies(comfy,manifest,files_only=False):
 if files_only:return
 req=[];allow=set()
 for module,pkg in [('cv2','opencv-python-headless'),('imageio_ffmpeg','imageio-ffmpeg'),('av','av')]:
  if importlib.util.find_spec(module) is None:req.append(pkg);allow.add(pkg)
 try:current=importlib.metadata.version('nvidia-vfx')
 except importlib.metadata.PackageNotFoundError:current='0'
 if tuple(int(n) for n in re.findall(r'\d+',current)[:2])<(0,2) or importlib.util.find_spec('nvvfx') is None:
  tag='cp310' if sys.version_info[:2]==(3,10) else 'cp311' if sys.version_info[:2]==(3,11) else 'cp312+'
  req.append(manifest['nvidia_sdk']['windows_wheels'][tag]);allow.add('nvidia-vfx')
 if req:run_pip(comfy,req,allow)

def node_target(comfy,pack):
 root=comfy/'custom_nodes';root.mkdir(exist_ok=True);matches=[p for p in root.iterdir() if p.is_dir() and p.name.removesuffix('-main').removesuffix('-master').casefold()==pack['folder'].casefold()]
 if len(matches)>1:raise RuntimeError('Có nhiều bản node '+pack['folder']+'. Chuyển bản trùng ra ngoài custom_nodes trước.')
 return matches[0] if matches else root/pack['folder']

def install_node(comfy,pack):
 archive=ROOT/'vendor'/pack['archive'];dl.download(pack['url'],archive,pack['bytes'],pack['sha256']);target=node_target(comfy,pack);backup=None
 with tempfile.TemporaryDirectory(prefix='relay-node-',dir=str(comfy/'user/RelayVSR_RTX_Original')) as t:
  source=safe_extract(archive,pathlib.Path(t)/'unpack');files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
  if target.exists() and all((target/p.relative_to(source)).is_file() and (target/p.relative_to(source)).read_bytes()==p.read_bytes() for p in files):print('Giữ node đúng bản và runtime hiện có:',target.name);return target
  if target.exists():
   backup=comfy/'user/RelayVSR_RTX_Original/backups'/(target.name+'-'+str(time.time_ns()));backup.parent.mkdir(parents=True,exist_ok=True);target.rename(backup)
  def link_or_copy(a,b):
   try:os.link(a,b);return b
   except OSError:return shutil.copy2(a,b)
  try:
   shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','.git'))
   if backup:
    for rel in pack.get('preserve_paths',[]):
     old=backup/rel;dest=target/rel
     if old.is_dir() and not dest.exists():shutil.copytree(old,dest,copy_function=link_or_copy)
     elif old.is_file() and not dest.exists():shutil.copy2(old,dest)
  except Exception:
   if target.exists():shutil.rmtree(target)
   if backup:backup.rename(target)
   raise
 print('Đã cài node:',target.name,'; backup:',backup or 'không cần');return target

def dlss_runtime_status(comfy,manifest):
 pack=next(p for p in manifest['nodes'] if p['folder']=='ComfyUI-DLSS5-Enhancer');target=node_target(comfy,pack);candidates=[]
 if os.environ.get('DLSS5_RUNTIME_DIR'):candidates.append(pathlib.Path(os.environ['DLSS5_RUNTIME_DIR']))
 config=target/'config.json'
 if config.is_file():
  data=json.loads(config.read_text(encoding='utf-8'))
  if data.get('runtime_dir'):candidates.append(pathlib.Path(data['runtime_dir']))
 candidates.append(target/'runtime')
 for root in candidates:
  if all((root/name).is_file() and (root/name).stat().st_size>0 for name in manifest['dlss_runtime']['required_files']):return {'files_present':True,'root':str(root),'gpu_worker_tested':False}
 return {'files_present':False,'required_version':'3.0 / worker protocol4','gpu_worker_tested':False}

def install_runtime(comfy,manifest,files_only=False):
 if files_only:print('FILES-ONLY: không cài SDK/runtime GPU; không được xem là render-ready.');return False
 if dlss_runtime_status(comfy,manifest)['files_present']:print('Giữ runtime DLSS5 đang có; không yêu cầu xác nhận tải lại.');return True
 p=next(p for p in manifest['nodes'] if p['folder']=='ComfyUI-DLSS5-Enhancer');script=node_target(comfy,p)/'install_runtime.py'
 print('Trình cài upstream DLSS5 sẽ hiển thị thông báo giấy phép và hỏi Continue? [y/N]. Chỉ nhập y nếu bạn đồng ý. Bộ cài không tự chấp nhận.',flush=True)
 # Inherit the console so the input prompt stays visible; never pass --yes.
 r=subprocess.run([sys.executable,'-I','-X','utf8',str(script)])
 if r.returncode:raise RuntimeError('Runtime DLSS5 chưa được cài (có thể bạn đã từ chối). File model/node vẫn được giữ; chạy CAI_RUNTIME_DLSS.bat khi muốn tiếp tục.')
 if not dlss_runtime_status(comfy,manifest)['files_present']:raise RuntimeError('Script runtime đã chạy nhưng còn thiếu binary. Không báo hoàn tất giả.')
 return True

def inspect_install(comfy,manifest,port=8188,files_only=False):
 r={'workflow_original_unchanged':hashlib.sha256(original_bytes(manifest)).hexdigest()==manifest['workflow_sha256'],'missing_models':[],'core_features':core_features(comfy,manifest),'schema':None,'dlss_runtime':dlss_runtime_status(comfy,manifest),'gpu_render_tested':False,'input_note':'Điền đường dẫn video thật vào #10. Hai preview tạm không phải file cuối #13.','configuration_notes':manifest['known_limitations']}
 installed=comfy/'user/default/workflows/RelayVSR_RTX_Original'/manifest['workflow'];r['installed_workflow_original_unchanged']=installed.is_file() and dl.sha256(installed)==manifest['workflow_sha256']
 for m in manifest['models']:
  if not direct_model(comfy,m):r['missing_models'].append(m['destination'])
 if not files_only:
  process=subprocess.run([sys.executable,'-I','-c','import nvvfx;print(nvvfx.__version__)'],capture_output=True,text=True);r['nvidia_sdk_import']={'success':process.returncode==0,'stdout':process.stdout,'stderr':process.stderr}
  try:
   with urllib.request.urlopen(f'http://127.0.0.1:{port}/object_info',timeout=15) as response:obj=json.load(response)
   r['schema']={name:name in obj for name in manifest['required_types']};r['missing_node_types']=[n for n,v in r['schema'].items() if not v]
  except (OSError,ValueError) as exc:r['runtime_note']='Mở lại ComfyUI rồi KIEM_TRA: '+str(exc)
 r['files_only_complete']=r['installed_workflow_original_unchanged'] and not r['missing_models'] and all(r['core_features'].values());r['dependency_ready']=r['files_only_complete'] and r['dlss_runtime']['files_present'] and r.get('nvidia_sdk_import',{}).get('success',False) and r['schema'] is not None and not r.get('missing_node_types');return r

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['install','runtime','check']);p.add_argument('--portable',default=DEFAULT_PORTABLE);p.add_argument('--port',type=int,default=8188);p.add_argument('--files-only',action='store_true',help='Chỉ file, bỏ qua SDK/GPU/runtime; không phải bản cài hoàn chỉnh');a=p.parse_args();portable=portable_path(a.portable);comfy=portable/'ComfyUI';manifest=json.loads((ROOT/'manifest.json').read_text());(comfy/'user/RelayVSR_RTX_Original').mkdir(parents=True,exist_ok=True);print('Portable đích:',portable,flush=True)
 if a.action=='check':
  r=inspect_install(comfy,manifest,a.port,a.files_only);(comfy/'user/RelayVSR_RTX_Original/local-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if (r['files_only_complete'] if a.files_only else r['dependency_ready']) else 2
 preflight(comfy,manifest,a.files_only)
 if a.action=='runtime':install_runtime(comfy,manifest,a.files_only);return 0
 dependencies(comfy,manifest,a.files_only)
 for pack in manifest['nodes']:install_node(comfy,pack)
 install_models(comfy,manifest);dest=copy_original_workflow(comfy,manifest);(ROOT/'local.json').write_text(json.dumps({'portable':str(portable),'workflow':str(dest)},ensure_ascii=False,indent=2))
 done=install_runtime(comfy,manifest,a.files_only)
 print('Đã cài file và chép workflow nguyên byte.',flush=True)
 if done:print('Mở lại ComfyUI, KIEM_TRA.bat và chọn video nguồn #10. Chưa kiểm thử render GPU trên máy này.')
 else:print('CÒN THIẾU SDK/runtime GPU: files-only không phải cài hoàn chỉnh.')
 return 0
if __name__=='__main__':
 logs=ROOT/'logs';logs.mkdir(exist_ok=True);logpath=logs/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.txt');oldout,olderr=sys.stdout,sys.stderr
 with logpath.open('w',encoding='utf-8') as log:
  sys.stdout=Tee(sys.stdout,log);sys.stderr=Tee(sys.stderr,log)
  try:raise SystemExit(main())
  except Exception as exc:print('LỖI:',exc,file=sys.stderr);traceback.print_exc(file=log);print('Log:',logpath,file=sys.stderr);raise SystemExit(1)
  finally:sys.stdout,sys.stderr=oldout,olderr
