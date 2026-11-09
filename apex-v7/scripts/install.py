"""Install pinned Apex V7 dependencies and verified model files into an existing Portable."""
import argparse,ast,datetime,traceback,hashlib,importlib.metadata,importlib.util,json,os,pathlib,shutil,stat,subprocess,sys,tempfile,time,urllib.request,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('apex_downloads',ROOT/'scripts/downloads.py');dl=importlib.util.module_from_spec(spec);spec.loader.exec_module(dl)
DEFAULT_PORTABLE=r'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'

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

def locate(comfy,m,verify=False):
 for base in model_roots(comfy,m['category']):
  if not base.exists():continue
  for f in base.rglob('*.safetensors'):
   if f.name.casefold()!=m['destination'].casefold():continue
   if f.stat().st_size!=m['bytes']:raise RuntimeError('Model cùng tên nhưng sai dung lượng: '+str(f)+'. Bộ cài giữ nguyên file này; đổi tên hoặc chuyển ra ngoài trước khi chạy lại.')
   if verify and dl.sha256(f)!=m['sha256']:raise RuntimeError('Model có sẵn sai SHA256: '+str(f)+'. Không ghi đè. Đổi tên hoặc chuyển file này ra ngoài rồi chạy lại.')
   return f,f.relative_to(base).as_posix()
 return None,None

def core_check(comfy,full=True):
 files=[comfy/'nodes.py']+list((comfy/'comfy_extras').glob('nodes_*.py'))
 text='\n'.join(f.read_text(encoding='utf-8') for f in files if f.is_file())
 required=['MiniMaxH3ReferenceToVideo','ResolutionSelector','ComfySwitchNode','ModelAttentionBackend','MiniMaxH3SigmaShift']
 if full:required+=['LTXVLatentUpsampler','ResizeImageMaskNode']
 missing=[name for name in required if name not in text]
 if missing:
  raise RuntimeError('Core chưa có '+', '.join(missing)+'. Chạy update/update_comfyui.bat của Portable, mở ComfyUI kiểm tra rồi cài lại. Bộ cài không tự đổi core/Torch.')
 print('Core có các loại node native cần dùng. Chạy KIEM_TRA.bat sau khi mở lại để kiểm tra import thật.',flush=True)


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
  if f.is_file() and '__pycache__' not in f.parts and '.git' not in f.parts and f.name!='.apex-installed.json':
   h.update(f.relative_to(root).as_posix().encode());h.update(b'\0');h.update(f.read_bytes());h.update(b'\0')
 return h.hexdigest()

def install_node(comfy,pack):
 archive=ROOT/'vendor'/pack['archive']
 dl.download(pack['url'],archive,pack['bytes'],pack['sha256'])
 custom=comfy/'custom_nodes';custom.mkdir(exist_ok=True)
 candidates=[p for p in custom.iterdir() if p.is_dir() and p.name.removesuffix('-main').removesuffix('-master').casefold()==pack['folder'].casefold()]
 if len(candidates)>1:raise RuntimeError('Có nhiều bản node '+pack['folder']+'. Chuyển bản trùng ra ngoài custom_nodes rồi chạy lại: '+', '.join(str(p) for p in candidates))
 target=candidates[0] if candidates else custom/pack['folder'];backup=None
 with tempfile.TemporaryDirectory(prefix='apex-node-',dir=str(comfy/'user/ApexV7')) as stage:
  source=safe_extract(archive,pathlib.Path(stage)/'unpack');fp=fingerprint(source)
  if target.exists() and fingerprint(target)==fp:print('Giữ node đúng bản:',target.name);return
  if target.exists():
   backup=comfy/'user/ApexV7/backups'/(target.name+'-'+str(time.time_ns()));backup.parent.mkdir(parents=True,exist_ok=True);target.rename(backup)
  try:
   shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','.git'))
   (target/'.apex-installed.json').write_text(json.dumps({'revision':pack['revision'],'sha256':pack['sha256']}),encoding='utf-8')
  except Exception:
   if target.exists():shutil.rmtree(target)
   if backup:backup.rename(target)
   raise
  print('Đã cài node:',target.name,'; backup:',backup or 'không cần',flush=True)

def dependencies(comfy):
 # Lock every installed distribution while resolving only genuinely missing dependencies.
 deps=[('PIL','Pillow>=10.3.0'),('matplotlib','matplotlib==3.10.3'),('color_matcher','color-matcher==0.6.0'),('mss','mss==10.1.0'),('cv2','opencv-python==4.11.0.86'),('imageio_ffmpeg','imageio-ffmpeg==0.6.0')]
 absent=[pkg for module,pkg in deps if importlib.util.find_spec(module) is None]
 if not absent:return
 constraint=comfy/'user/ApexV7/runtime-constraints.txt'
 constraint.write_text('\n'.join(sorted({d.metadata['Name']+'=='+d.version for d in importlib.metadata.distributions() if d.metadata.get('Name')}))+'\n',encoding='utf-8')
 cmd=[sys.executable,'-I','-m','pip','install','--disable-pip-version-check','--upgrade-strategy','only-if-needed','--constraint',str(constraint)]+absent
 print('Chỉ bổ sung Python dependency còn thiếu:',', '.join(absent),flush=True)
 with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1) as process:
  for line in process.stdout:print(line,end='',flush=True)
  if process.wait():raise subprocess.CalledProcessError(process.returncode,cmd)

def rewrite_names(w,found,manifest):
 names={m['destination']:found[m['id']] for m in manifest['models'] if m['id'] in found}
 def walk(v):
  if isinstance(v,dict):return {k:walk(x) for k,x in v.items()}
  if isinstance(v,list):return [walk(x) for x in v]
  return names.get(v,v) if isinstance(v,str) else v
 return walk(w)

def adapt_video_schema(w,comfy):
 # Read widget order and optional chroma choices from the installed CreateVideo class.
 source=comfy/'comfy_extras/nodes_video.py';text=source.read_text(encoding='utf-8') if source.is_file() else ''
 values={'fps':24,'bit_depth':8,'color_space':'sRGB','codec':'none'};order=[];chroma_default='auto'
 tree=ast.parse(text)
 cls=next((n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CreateVideo'),None)
 if cls:
  calls=sorted((n for n in ast.walk(cls) if isinstance(n,ast.Call)),key=lambda n:(n.lineno,n.col_offset))
  for call in calls:
   if not isinstance(call.func,ast.Attribute) or call.func.attr!='Input' or not call.args or not isinstance(call.args[0],ast.Constant):continue
   name=call.args[0].value
   if name in values or name=='chroma_subsampling':order.append(name)
   if name=='chroma_subsampling':
    opts=None;default=None
    for kw in call.keywords:
     if kw.arg not in ('default','options'):continue
     try:literal=ast.literal_eval(kw.value)
     except (ValueError,TypeError):continue
     if kw.arg=='options':opts=literal
     else:default=literal
    if opts:chroma_default='auto' if 'auto' in opts else default if default in opts else opts[0]
    elif default is not None:chroma_default=default
 if not order:order=['fps','bit_depth','color_space']+(['chroma_subsampling'] if 'chroma_subsampling' in text else [])+['codec']
 if 'chroma_subsampling' in order:values['chroma_subsampling']=chroma_default
 for graph in [w]+w.get('definitions',{}).get('subgraphs',[]):
  for n in graph['nodes']:
   if n['type']=='CreateVideo':n['widgets_values']=[values[k] for k in order];n['widgets_values_named']={k:values[k] for k in order}
 return w


def install_workflows(comfy,found,manifest,full):
 target=comfy/'user/default/workflows/Apex_H3_V7_Studio';target.mkdir(parents=True,exist_ok=True);files=[]
 for p in json.loads((ROOT/'profiles.json').read_text(encoding='utf-8')):
  if p['id']=='full' and not full:continue
  w=adapt_video_schema(rewrite_names(json.loads((ROOT/'workflows'/p['file']).read_text(encoding='utf-8')),found,manifest),comfy)
  dest=target/p['file'];data=(json.dumps(w,ensure_ascii=False,indent=2)+'\n').encode()
  if dest.exists() and dest.read_bytes()!=data:
   backup=comfy/'user/ApexV7/backups'/str(time.time_ns());backup.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup/dest.name)
  dest.write_bytes(data);files.append(str(dest))
 return files

def inspect_install(comfy,manifest,full,port=8188):
 models=[m for m in manifest['models'] if full or m['profile']=='h3'];found={};missing=[]
 for m in models:
  f,n=locate(comfy,m)
  if f:found[m['id']]=str(f)
  else:missing.append(m['destination'])
 result={'comfy':str(comfy),'missing_models':missing,'found_models':found,'file_hashes_verified':False,'gpu_render_tested':False,'schema':None}
 try:
  with urllib.request.urlopen(f'http://127.0.0.1:{port}/object_info',timeout=10) as r:obj=json.load(r)
  required=manifest['required_types_by_profile']['full' if full else 'h3']
  result['schema']={name:name in obj for name in required};result['missing_node_types']=[x for x,v in result['schema'].items() if not v]
 except (OSError,ValueError) as exc:result['runtime_note']='Chưa đọc được ComfyUI localhost:'+str(port)+'. Mở lại ComfyUI rồi chạy KIEM_TRA; chưa thể xác nhận node đã nạp. '+str(exc)
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['install','h3','check','nodes']);p.add_argument('--portable',default=DEFAULT_PORTABLE);p.add_argument('--port',type=int,default=8188);a=p.parse_args()
 portable=portable_path(a.portable);comfy=portable/'ComfyUI';manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'));state=ROOT/'local.json';full=a.action=='install'
 if state.exists() and a.action=='check':full=json.loads(state.read_text(encoding='utf-8')).get('full',False)
 (comfy/'user/ApexV7').mkdir(parents=True,exist_ok=True)
 print('ComfyUI đích:',comfy,flush=True)
 if a.action=='check':
  result=inspect_install(comfy,manifest,full,a.port);report=comfy/'user/ApexV7/local-check.json';report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
  if result['missing_models'] or result.get('missing_node_types') or result['schema'] is None:return 2
  print('File đủ dung lượng; schema có đủ node. Chưa xác nhận GPU render hoặc SHA256 bằng lượt kiểm tra nhanh.');return 0
 core_check(comfy,full=full)
 if a.action!='nodes':
  selected=[m for m in manifest['models'] if full or m['profile']=='h3'];found={};missing=[]
  for m in selected:
   f,n=locate(comfy,m,verify=True)
   if f:found[m['id']]=n;print('Đúng SHA256, dùng lại:',n,flush=True)
   else:missing.append(m)
  needed=sum(max(0,m['bytes']-((comfy/'models'/m['category']/(m['destination']+'.part')).stat().st_size if (comfy/'models'/m['category']/(m['destination']+'.part')).exists() else 0)) for m in missing)
  print('Còn tải %.2f GB; SSD trống %.2f GB.'%(needed/1e9,shutil.disk_usage(comfy).free/1e9),flush=True)
  if needed>0 and shutil.disk_usage(comfy).free<needed+2*1024**3:raise RuntimeError('Không đủ chỗ trống. Cần số GB còn tải và ít nhất 2 GiB dự phòng, chưa tính output/pagefile.')
 dependencies(comfy)
 for pack in manifest['nodes']:install_node(comfy,pack)
 if a.action=='nodes':print('Đã cài node. Mở lại ComfyUI để kiểm tra import.');return 0
 for m in missing:
  dest=comfy/'models'/m['category']/m['destination'];url='https://huggingface.co/'+m['repo']+'/resolve/'+m['revision']+'/'+m['file']
  dl.download(url,dest,m['bytes'],m['sha256']);found[m['id']]=m['destination']
 files=install_workflows(comfy,found,manifest,full)
 state.write_text(json.dumps({'portable':str(portable),'full':full,'workflows':files},ensure_ascii=False,indent=2),encoding='utf-8')
 print('\nĐã cài file và sao chép workflow. Mở lại ComfyUI; chạy KIEM_TRA.bat.',flush=True)
 print('Mở Apex_H3_V7_Studio / 01_APEX... để thử 5 giây trước. Chọn storyboard thật và dán prompt đã được duyệt.',flush=True)
 print('Skill: đọc skill/minimax-h3-film/SKILL.md bằng Codex. Hướng dẫn: docs/HUONG_DAN.pdf.',flush=True)
 return 0
class Tee:
 def __init__(self,stream,log):self.stream=stream;self.log=log
 def write(self,text):self.stream.write(text);self.log.write(text);self.log.flush()
 def flush(self):self.stream.flush();self.log.flush()

if __name__=='__main__':
 logs=ROOT/'logs';logs.mkdir(exist_ok=True);logpath=logs/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.txt')
 original_stdout,original_stderr=sys.stdout,sys.stderr
 with logpath.open('w',encoding='utf-8') as logfile:
  sys.stdout=Tee(sys.stdout,logfile);sys.stderr=Tee(sys.stderr,logfile)
  try:raise SystemExit(main())
  except Exception as exc:
   print('LỖI:',exc,file=sys.stderr);traceback.print_exc(file=logfile);print('Log:',logpath,file=sys.stderr);raise SystemExit(1)
  finally:sys.stdout,sys.stderr=original_stdout,original_stderr

