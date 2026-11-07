"""Install only the missing parts reported for the user's original H3 workflow."""
import sys,pathlib
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:]=[p for p in sys.path if pathlib.Path(p or '.').resolve()!=HERE];sys.path.append(str(HERE))
import argparse,datetime,importlib.util,json,os,shutil,subprocess,time,traceback,urllib.request,uuid,zipfile
from downloads import download,sha256
ROOT=HERE.parent
MANIFEST=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))


def portable_root(value):
    p=pathlib.Path(value).expanduser().resolve()
    for candidate in [p,p/'ComfyUI_windows_portable',p.parent]:
        if (candidate/'python_embeded/python.exe').is_file() and (candidate/'ComfyUI/main.py').is_file():return candidate
    raise ValueError('Chọn thư mục Portable chứa python_embeded và ComfyUI: '+str(p))


def extract_repo(archive,destination):
    destination=pathlib.Path(destination).resolve()
    with zipfile.ZipFile(archive) as z:
        names=[]
        for entry in z.infolist():
            name=entry.filename.replace('\\','/')
            if ':' in name or not (destination/name).resolve().is_relative_to(destination):raise ValueError('Đường dẫn ZIP không hợp lệ.')
            if (entry.external_attr>>16)&0o170000==0o120000:raise ValueError('ZIP có symlink không được hỗ trợ.')
            names.append((entry,name))
        for entry,name in names:
            path=destination/name
            if entry.is_dir():path.mkdir(parents=True,exist_ok=True)
            else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(z.read(entry))
    children=[p for p in destination.iterdir() if p.is_dir()]
    if len(children)!=1:raise ValueError('Cấu trúc archive repository không đúng.')
    src=children[0]
    for relative in ['__init__.py','nodes/node_monitor.py','nodes/node_run_timer.py']:
        if not (src/relative).is_file():raise ValueError('Thiếu file trong Pixaroma: '+relative)
    return src


def model_folders(comfy,category):
    comfy=pathlib.Path(comfy);paths=[comfy/'models'/category]
    config=comfy/'extra_model_paths.yaml'
    if config.exists():
        try:import yaml
        except ImportError:
            print('Chưa có PyYAML để đọc extra_model_paths; dùng thư mục model mặc định.',flush=True)
            return paths
        data=yaml.safe_load(config.read_text(encoding='utf-8')) or {}
        for group in data.values():
            if not isinstance(group,dict) or not isinstance(group.get(category),str):continue
            base=group.get('base_path')
            if base:
                base=pathlib.Path(os.path.expandvars(os.path.expanduser(base)))
                if not base.is_absolute():base=config.parent/base
            else:base=config.parent
            for line in group[category].splitlines():
                if not line.strip():continue
                q=pathlib.Path(os.path.expandvars(os.path.expanduser(line.strip())))
                paths.append(q if q.is_absolute() else base/q)
    return list(dict.fromkeys(p.resolve() for p in paths))


def resolve_model(comfy,model):
    category,name=model['destination'].split('/',1)
    candidates=[p/name for p in model_folders(comfy,category)]
    for p in candidates:
        if p.is_file() and p.stat().st_size==model['bytes']:
            print('Kiểm tra SHA-256:',p,flush=True)
            if sha256(p)==model['sha256']:return p,True
    target=candidates[0]
    if target.exists():raise RuntimeError('File cùng tên khác manifest; giữ nguyên để bảo toàn dữ liệu: '+str(target))
    return target,False


def pack_target(comfy):
    folder=pathlib.Path(comfy)/'custom_nodes';candidates=[]
    if folder.exists():
        for p in folder.iterdir():
            if p.is_dir() and 'pixaroma' in p.name.lower() and (p/'__init__.py').is_file():candidates.append(p)
    if len(candidates)>1:raise RuntimeError('Có nhiều bản Pixaroma. Giữ lại đúng một bản trước khi chạy: '+', '.join(str(p) for p in candidates))
    return candidates[0] if candidates else folder/MANIFEST['node_pack']['folder']


def install_pack(comfy,archive):
    comfy=pathlib.Path(comfy);target=pack_target(comfy);spec=MANIFEST['node_pack'];marker=target/'.h3-missing-fix.json'
    if marker.is_file() and json.loads(marker.read_text())['revision']==spec['revision'] and (target/'nodes/node_monitor.py').is_file() and (target/'nodes/node_run_timer.py').is_file():
        print('Pixaroma đã ở đúng bản đã kiểm tra:',target,flush=True);return target
    scratch=comfy/'user/h3_missing_fix/staging'/uuid.uuid4().hex;scratch.mkdir(parents=True,exist_ok=True)
    src=extract_repo(archive,scratch);(src/'.h3-missing-fix.json').write_text(json.dumps({'revision':spec['revision'],'archive_sha256':spec['archive_sha256']}),encoding='utf-8')
    target.parent.mkdir(parents=True,exist_ok=True);backup=None
    if target.exists():
        backups=comfy/'user/h3_missing_fix/backups';backups.mkdir(parents=True,exist_ok=True);backup=backups/(target.name+'-'+str(time.time_ns()));target.rename(backup)
    try:shutil.move(str(src),str(target))
    except Exception:
        if backup is not None and not target.exists():backup.rename(target)
        raise
    shutil.rmtree(scratch,ignore_errors=True)
    print('Đã cài Pixaroma:',target,flush=True)
    if backup:print('Bản cũ đã sao lưu ngoài custom_nodes:',backup,flush=True)
    return target


def install_dependencies():
    for dep in MANIFEST['node_pack']['dependencies']:
        if importlib.util.find_spec(dep['module']) is not None:
            print('Đã có dependency:',dep['module'],flush=True);continue
        command=[sys.executable,'-X','utf8','-s','-m','pip','install','--no-deps','--no-cache-dir',dep['package']]
        print('Cài dependency thiếu:',dep['package'],flush=True)
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
        print(result.stdout,flush=True)
        if result.returncode:raise RuntimeError('Cài dependency thất bại; xem log bên trên.')


def run_install(portable):
    portable=portable_root(portable);comfy=portable/'ComfyUI';cache=comfy/'user/h3_missing_fix/cache';cache.mkdir(parents=True,exist_ok=True)
    print('COMFYUI ĐƯỢC BỔ SUNG:',comfy,flush=True)
    print('PYTHON ĐANG DÙNG:',sys.executable,flush=True)
    targets=[(m,*resolve_model(comfy,m)) for m in MANIFEST['models']]
    missing=sum(max(0,m['bytes']-min(m['bytes'],p.with_name(p.name+'.part').stat().st_size if p.with_name(p.name+'.part').exists() else 0)) for m,p,found in targets if not found)
    if shutil.disk_usage(comfy).free<missing+400*1024**2:raise RuntimeError(f'Cần khoảng {(missing+400*1024**2)/1e9:.2f} GB trống ở ổ cài ComfyUI.')
    spec=MANIFEST['node_pack'];archive=cache/(spec['revision']+'.zip')
    download('https://github.com/'+spec['repo']+'/archive/'+spec['revision']+'.zip',archive,spec['archive_bytes'],spec['archive_sha256'])
    install_dependencies();installed=install_pack(comfy,archive)
    for model,path,found in targets:
        if found:print('Đã có file đúng checksum; bỏ qua tải:',path,flush=True);continue
        url='https://huggingface.co/'+model['repo']+'/resolve/'+model['revision']+'/'+model['file']
        print('Tải model:',path.name,flush=True);download(url,path,model['bytes'],model['sha256'])
    report={'portable':str(portable),'comfy':str(comfy),'python':str(sys.executable),'pack':str(installed),'models':[{'path':str(p),'sha256':m['sha256'],'reused':found} for m,p,found in targets],'restart_required':True,'gpu_render_tested':False}
    (ROOT/'local.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'reports/installed.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\nHOÀN TẤT. Đóng backend ComfyUI và mở lại bằng cách bạn vẫn dùng; Ctrl+F5 trang web.',flush=True)
    print('Workflow gốc và các model khác được giữ nguyên. Không cần chuyển sang một runtime/cổng khác.',flush=True)


def check_install(portable):
    portable=portable_root(portable);comfy=portable/'ComfyUI';target=pack_target(comfy)
    for rel in ['__init__.py','nodes/node_monitor.py','nodes/node_run_timer.py']:
        if not (target/rel).is_file():raise RuntimeError('Chưa thấy Pixaroma: '+str(target/rel))
    print('Pixaroma trên ổ đĩa:',target,flush=True)
    for model in MANIFEST['models']:
        p,found=resolve_model(comfy,model)
        if not found:raise RuntimeError('Chưa có model đúng checksum: '+str(p))
        print('Model OK:',p,flush=True)
    observations=[]
    for port in [8188,8189]:
        url=f'http://127.0.0.1:{port}'
        try:
            with urllib.request.urlopen(url+'/object_info',timeout=3) as r:info=json.load(r)
            missing=[name for name in MANIFEST['node_pack']['nodes'] if name not in info]
            observations.append({'url':url,'missing_nodes':missing})
            print(url,': '+('đã nạp cả hai node Pixaroma' if not missing else 'chưa nạp '+', '.join(missing)),flush=True)
        except (OSError,ValueError) as exc:
            print(url,': chưa đọc được server ('+str(exc)+')',flush=True)
    (ROOT/'reports/check.json').write_text(json.dumps({'files_checked':True,'runtime_observations':observations,'render_tested':False},indent=2),encoding='utf-8')
    if not observations:print('Các file đã đủ. Mở lại đúng ComfyUI đã cài để nạp node.',flush=True)
    elif all(o['missing_nodes'] for o in observations):raise RuntimeError('Server chưa nạp Pixaroma: cần restart đúng backend; xem log import nếu còn lỗi.')


class Tee:
    def __init__(self,*streams):self.streams=streams
    def write(self,value):
        for stream in self.streams:stream.write(value);stream.flush()
        return len(value)
    def flush(self):
        for stream in self.streams:stream.flush()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['install','check']);ap.add_argument('--portable',required=True);a=ap.parse_args()
    logs=ROOT/'logs';logs.mkdir(exist_ok=True);(ROOT/'reports').mkdir(exist_ok=True)
    log=logs/(a.action+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.txt')
    original_out,original_err=sys.stdout,sys.stderr
    if hasattr(original_out,'reconfigure'):original_out.reconfigure(encoding='utf-8',errors='replace')
    with log.open('w',encoding='utf-8') as f:
        sys.stdout=Tee(original_out,f);sys.stderr=Tee(original_err,f)
        try:
            print('Log:',log,flush=True)
            (run_install if a.action=='install' else check_install)(a.portable)
        except Exception:
            traceback.print_exc();print('\nChưa hoàn tất. Giữ log và chạy lại sau khi xử lý lỗi ghi bên trên.',flush=True);raise SystemExit(1)
        finally:sys.stdout,sys.stderr=original_out,original_err
if __name__=='__main__':main()
