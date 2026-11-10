"""Remove only known RelayVSR installer components from a selected ComfyUI Portable."""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,pathlib,re,shutil,subprocess,sys,traceback

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_PORTABLE=r'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
MODELS={
 'diffusion_models':('relayvsr_x2_lightx2v_int8_convrot.safetensors',),
 'vae':('relayvsr_flash_vae_x2_fp32.safetensors',),
}
EXCLUSIVE_NODES={'comfyuidlss5enhancer','comfyuinvidiavfxnodes','comfyuinvidiartxnodes'}
VHS='comfyuivideohelpersuite'
WORKFLOW='RealVSR-RTX_VFX - upscale.json'
WORKFLOW_HASH='b7ab1d4a880bbec75c0b99957ee6db2b72636967cbc06ec58da2eef05366fa9e'
METADATA={'local-check.json','runtime-constraints.txt'}

def node_key(name):
 name=re.sub(r'(?i)(?:\.disabled|-main|-master)+$','',name)
 return re.sub(r'[-_.]','',name).casefold()

def linked(p):
 return p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction())

def exists(p):return p.exists() or p.is_symlink()

def portable_path(value):
 p=pathlib.Path(value).expanduser()
 for q in dict.fromkeys([p,p/'ComfyUI_windows_portable',p.parent if p.name.casefold()=='comfyui' else p]):
  if (q/'python_embeded/python.exe').is_file() and (q/'ComfyUI/main.py').is_file():return q.resolve()
 raise ValueError('Chon THU MUC Portable chua python_embeded va ComfyUI; khong chon JSON.')

def walk_files(root,errors):
 """Do not descend directory symlinks/junctions. Model roots themselves may be configured links."""
 if not root.is_dir():return
 def fail(exc):errors.append('Khong doc duoc '+str(exc.filename)+': '+str(exc))
 for base,dirs,files in os.walk(root,followlinks=False,onerror=fail):
  base=pathlib.Path(base);dirs[:]=[n for n in dirs if n not in {'.git','__pycache__'} and not linked(base/n)]
  for name in files:yield base/name

def model_roots(comfy,category,errors):
 roots=[comfy/'models'/category]
 if category=='diffusion_models':roots.append(comfy/'models/unet')
 cfg=comfy/'extra_model_paths.yaml'
 if cfg.is_file():
  try:
   import yaml
   data=yaml.safe_load(cfg.read_text(encoding='utf-8-sig')) or {}
   if not isinstance(data,dict):raise ValueError('YAML root must be a mapping')
   for entry in data.values():
    if not isinstance(entry,dict):continue
    base=pathlib.Path(os.path.expandvars(os.path.expanduser(str(entry.get('base_path',comfy)))))
    if not base.is_absolute():base=comfy/base
    for key in ([category,'unet'] if category=='diffusion_models' else [category]):
     for line in str(entry.get(key,'')).splitlines():
      if line.strip():
       q=pathlib.Path(os.path.expandvars(os.path.expanduser(line.strip())));roots.append(q if q.is_absolute() else base/q)
  except (ImportError,OSError,ValueError) as exc:errors.append('Chua quet duoc extra_model_paths.yaml: '+str(exc))
  except Exception as exc:errors.append('YAML khong hop le: '+str(exc))
 return list(dict.fromkeys(roots))

def model_name_matches(name,expected):
 return any(re.fullmatch(re.escape(n)+r'(?:\.part(?:\.corrupt-\d+)?|\.alias-\d+)?',name) for n in expected)

def tree_size(p):
 if linked(p):return 0
 if p.is_file():return p.stat().st_size
 errors=[];total=0
 for f in walk_files(p,errors):
  if not linked(f):
   try:total+=f.stat().st_size
   except OSError:pass
 return total

def stat_stamp(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_mtime_ns,s.st_size,s.st_mode]

def sdk_info(portable):
 code="""import importlib.metadata as m,json
try:
 d=m.distribution('nvidia-vfx');print(json.dumps({'installed':True,'version':d.version,'location':str(d.locate_file(''))}))
except m.PackageNotFoundError:print(json.dumps({'installed':False}))
"""
 try:
  p=subprocess.run([str(portable/'python_embeded/python.exe'),'-I','-X','utf8','-c',code],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
  if p.returncode:raise RuntimeError(p.stderr.strip())
  return json.loads(p.stdout)
 except (OSError,ValueError,subprocess.SubprocessError,RuntimeError) as exc:return {'installed':None,'error':str(exc)}

def sdk_dependents(comfy,errors):
 found=[];root=comfy/'custom_nodes'
 if not root.is_dir():return found
 for pack in root.iterdir():
  if node_key(pack.name) in EXCLUSIVE_NODES or pack.name=='__pycache__':continue
  if linked(pack):errors.append('Khong theo lien ket node dung chung khi kiem SDK: '+str(pack));continue
  files=walk_files(pack,errors) if pack.is_dir() else [pack]
  for file in files:
   if file.suffix.casefold() not in {'.py','.txt','.toml','.json','.yaml','.yml'}:continue
   try:
    if file.stat().st_size>2*1024**2:continue
    text=file.read_text(encoding='utf-8',errors='replace')
   except OSError as exc:errors.append('Khong kiem duoc dependency '+str(file)+': '+str(exc));continue
   if re.search(r'\b(?:nvvfx|nvidia[-_]vfx)\b',text,re.I):found.append(str(file));break
 return found

def active_processes(portable):
 if sys.platform!='win32':return []
 ps=r"""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=New-Object System.Text.UTF8Encoding($false); @(Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne [int]$env:RELAY_REMOVE_PID -and ($_.ExecutablePath -and $_.ExecutablePath.StartsWith($env:RELAY_REMOVE_ROOT,[System.StringComparison]::OrdinalIgnoreCase) -or $_.CommandLine -and $_.CommandLine.IndexOf($env:RELAY_REMOVE_ROOT,[System.StringComparison]::OrdinalIgnoreCase) -ge 0) } | Select-Object ProcessId,Name,CommandLine) | ConvertTo-Json -Compress"""
 env=dict(os.environ,RELAY_REMOVE_ROOT=str(portable),RELAY_REMOVE_PID=str(os.getpid()))
 p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',ps],env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
 if p.returncode:raise RuntimeError('Khong kiem tra duoc tien trinh ComfyUI: '+p.stderr.strip())
 rows=json.loads(p.stdout.strip() or '[]');rows=rows if isinstance(rows,list) else [rows];found=[]
 for row in rows:
  if (row.get('Name') or '').casefold()=='nvngx.dll' or re.search(r'(?i)(?:\bmain\.py\b|\bnvngx\.dll\b)',row.get('CommandLine') or ''):found.append({'pid':row['ProcessId'],'name':row.get('Name')})
 return found

def build_plan(portable,info=None):
 comfy=portable/'ComfyUI';errors=[];items=[];kept=[];seen=set()
 def add(path,kind):
  if not exists(path):return
  key=os.path.normcase(os.path.abspath(path))
  if key in seen:return
  # Do not schedule a path already covered by an owned directory.
  if any(path.is_relative_to(pathlib.Path(x['path'])) for x in items if x['kind'] in {'node','backup_node'}):return
  seen.add(key);items.append({'path':str(path),'kind':kind,'bytes':tree_size(path),'stamp':stat_stamp(path)})
 for category,names in MODELS.items():
  for root in model_roots(comfy,category,errors):
   for file in walk_files(root,errors):
    if model_name_matches(file.name,names):add(file,'model')
 nodes=comfy/'custom_nodes'
 if nodes.is_dir():
  for pack in nodes.iterdir():
   key=node_key(pack.name)
   if key in EXCLUSIVE_NODES:add(pack,'node')
   elif key==VHS:kept.append({'path':str(pack),'reason':'VideoHelperSuite dung chung voi workflow video khac.'})
 workdir=comfy/'user/default/workflows/RelayVSR_RTX_Original'
 # Only remove original, byte-matching workflow files; retain user edits.
 if workdir.is_dir() and not linked(workdir):
  for file in walk_files(workdir,errors):
   if file.name==WORKFLOW and not linked(file) and hashlib.sha256(file.read_bytes()).hexdigest()==WORKFLOW_HASH:add(file,'workflow')
   else:kept.append({'path':str(file),'reason':'File da sua/khac workflow goc; giu du lieu nguoi dung.'})
 state=comfy/'user/RelayVSR_RTX_Original';backup=state/'backups'
 if backup.is_dir() and not linked(backup):
  for item in backup.iterdir():
   if item.is_dir():
    base=re.sub(r'-\d+$','',item.name)
    if node_key(base) in EXCLUSIVE_NODES:add(item,'backup_node')
    elif node_key(base)==VHS:kept.append({'path':str(item),'reason':'Ban sao luu VideoHelperSuite truoc khi cai Relay; giu de phuc hoi neu can.'})
   elif item.is_file() and item.name not in {'.DS_Store'}:kept.append({'path':str(item),'reason':'Backup khong nam trong danh sach Relay rieng.'})
  for file in walk_files(backup,errors):
   if file.name==WORKFLOW and not linked(file) and hashlib.sha256(file.read_bytes()).hexdigest()==WORKFLOW_HASH:add(file,'workflow_backup')
 if state.is_dir() and not linked(state):
  for filename in METADATA:add(state/filename,'installer_metadata')
 info=sdk_info(portable) if info is None else info;sdk=dict(info);sdk_errors=[]
 dependents=sdk_dependents(comfy,sdk_errors) if info.get('installed') else [];errors.extend(sdk_errors)
 if info.get('installed'):
  location=pathlib.Path(info.get('location','')).resolve()
  if not location.is_relative_to(portable.resolve()):sdk.update(action='keep',reason='SDK nam ngoai Portable; khong go Python/ung dung dung chung.')
  elif dependents or sdk_errors:sdk.update(action='keep',reason='Con node khac su dung SDK, hoac chua kiem tra duoc het.',dependents=dependents)
  else:sdk.update(action='uninstall',reason='Chi go distribution nvidia-vfx; giu Torch/CUDA va dependency dung chung.')
 elif info.get('installed') is False:sdk['action']='absent'
 else:sdk.update(action='unknown',reason='Chua doc duoc metadata SDK; khong tu xoa site-packages.')
 return {'portable':str(portable),'files':items,'sdk':sdk,'kept':kept,'scan_errors':errors,'file_bytes_selected':sum(x['bytes'] for x in items),'preserved':['H3/OmniRef models','ComfyUI core va native RelayVSR nodes','Torch, CUDA, driver','VideoHelperSuite','NumPy, OpenCV, PyAV, imageio-ffmpeg','Video input/output va project da sua','Runtime DLSS ngoai thu muc node (neu duoc dang ky tu ung dung khac)']}

def remove_path(path):
 if path.is_symlink():path.unlink()
 elif hasattr(path,'is_junction') and path.is_junction():path.rmdir()
 elif path.is_dir():
  def onerror(func,name,exc):
   if isinstance(exc[1],PermissionError):os.chmod(name,0o700);func(name)
   else:raise exc[1]
  shutil.rmtree(path,onerror=onerror)
 else:path.unlink()

def apply_plan(plan):
 portable=pathlib.Path(plan['portable']);comfy=portable/'ComfyUI';report={'removed':[],'failed':[],'kept':plan['kept'],'scan_errors':plan['scan_errors'],'sdk':dict(plan['sdk']),'estimated_file_bytes_removed':0}
 busy=active_processes(portable)
 if busy:raise RuntimeError('Dong ComfyUI/backend va DLSS worker truoc khi go. Tien trinh con mo: '+json.dumps(busy))
 # Re-build paths from constants; never execute an arbitrary saved plan.
 fresh=build_plan(portable,info=plan['sdk']);allowed={x['path']:x for x in fresh['files']}
 for item in plan['files']:
  path=pathlib.Path(item['path'])
  try:
   if not exists(path):continue
   if item['path'] not in allowed or stat_stamp(path)!=item['stamp']:raise RuntimeError('File/thu muc da doi sau khi quet; khong xoa.')
   remove_path(path);report['removed'].append({'path':str(path),'kind':item['kind'],'bytes':item['bytes']});report['estimated_file_bytes_removed']+=item['bytes'];print('DA GO:',path,flush=True)
  except (OSError,RuntimeError) as exc:report['failed'].append({'path':str(path),'error':str(exc)});print('CHUA GO:',path,str(exc),flush=True)
 # Check dependent nodes again before using pip; do not infer cleanup from file deletion.
 sdk=plan['sdk']
 if sdk['action']=='uninstall':
  errors=[];deps=sdk_dependents(comfy,errors);current=sdk_info(portable)
  if current.get('installed') is False:report['sdk'].update(action='absent',after=current)
  elif current.get('installed') is not True:report['sdk'].update(action='unknown',reason='Chua kiem tra lai duoc SDK.');report['scan_errors'].append('Khong xac minh duoc SDK truoc pip uninstall.')
  elif not pathlib.Path(current.get('location','')).resolve().is_relative_to(portable.resolve()):report['sdk'].update(action='keep',reason='Vi tri SDK da doi ra ngoai Portable; giu SDK.')
  elif deps or errors:report['sdk'].update(action='keep',reason='Dependency da thay doi; giu SDK.',dependents=deps);report['scan_errors'].extend(errors)
  elif any(x['kind']=='node' and exists(pathlib.Path(x['path'])) for x in plan['files']):report['sdk'].update(action='keep',reason='Chua go xong node RTX/DLSS; giu SDK de thu lai.')
  else:
   cmd=[str(portable/'python_embeded/python.exe'),'-I','-X','utf8','-m','pip','uninstall','-y','nvidia-vfx']
   print('GO SDK nvidia-vfx bang Python Portable...',flush=True)
   r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace');print(r.stdout,flush=True)
   after=sdk_info(portable);report['sdk'].update(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,after=after)
   if r.returncode or after.get('installed') is not False:report['failed'].append({'path':'pip:nvidia-vfx','error':r.stderr or 'SDK van con/chua kiem tra duoc.'})
   else:report['sdk']['action']='uninstalled'
 # Only remove empty installer-owned directories, never an entire user/output tree.
 owned=[comfy/'user/default/workflows/RelayVSR_RTX_Original',comfy/'user/RelayVSR_RTX_Original']
 for folder in owned:
  if folder.is_dir() and not linked(folder):
   for base,dirs,_ in os.walk(folder,topdown=False,followlinks=False):
    p=pathlib.Path(base)
    if linked(p):continue
    try:p.rmdir()
    except OSError:pass
 remaining=build_plan(portable,info=report['sdk'].get('after') or sdk_info(portable));report['remaining_targets']=[x['path'] for x in remaining['files']];report['remaining_sdk']=remaining['sdk'];report['scan_errors']=list(dict.fromkeys(report['scan_errors']+remaining['scan_errors']))
 report['success']=not report['failed'] and not report['remaining_targets'] and not report['scan_errors'] and remaining['sdk']['action'] not in {'uninstall','unknown'}
 return report

class Tee:
 def __init__(self,stream,log):self.stream=stream;self.log=log
 def write(self,s):self.stream.write(s);self.log.write(s);self.log.flush()
 def flush(self):self.stream.flush();self.log.flush()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['inspect','uninstall']);p.add_argument('--portable',default=DEFAULT_PORTABLE);a=p.parse_args();portable=portable_path(a.portable);print('PORTABLE:',portable,flush=True)
 busy=active_processes(portable)
 if a.action=='uninstall' and busy:raise RuntimeError('Dong ComfyUI/backend va DLSS worker truoc khi go: '+json.dumps(busy))
 plan=build_plan(portable);reports=ROOT/'reports';reports.mkdir(exist_ok=True);tag=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');(reports/('plan-'+tag+'.json')).write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Tim thay',len(plan['files']),'muc; dung luong file khoang %.2f GB (chua tinh SDK).'%(plan['file_bytes_selected']/1e9),flush=True)
 for item in plan['files']:print('GO:',item['kind'],item['path'],flush=True)
 print('SDK:',json.dumps(plan['sdk'],ensure_ascii=False),flush=True)
 for item in plan['kept']:print('GIU:',item['path'],'-',item['reason'],flush=True)
 for err in plan['scan_errors']:print('LUU Y:',err,flush=True)
 if a.action=='inspect':print('CHI XEM; chua xoa file nao.');return 0
 report=apply_plan(plan);out=reports/('uninstall-'+tag+'.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('BAO CAO:',out,flush=True)
 if report['success']:print('DA GO CAC THANH PHAN RELAYVSR RIENG. Giu node/dependency dung chung va video cua ban.');return 0
 print('CHUA GO HET: xem failed / remaining_targets / scan_errors trong bao cao. Dong ComfyUI roi chay lai neu file dang bi khoa.');return 2

if __name__=='__main__':
 logs=ROOT/'logs';logs.mkdir(exist_ok=True);path=logs/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.txt');oldout,olderr=sys.stdout,sys.stderr
 with path.open('w',encoding='utf-8') as log:
  sys.stdout=Tee(oldout,log);sys.stderr=Tee(olderr,log)
  try:raise SystemExit(main())
  except Exception as exc:print('LOI:',exc,file=sys.stderr);traceback.print_exc(file=log);print('LOG:',path,file=sys.stderr);raise SystemExit(1)
  finally:sys.stdout,sys.stderr=oldout,olderr
