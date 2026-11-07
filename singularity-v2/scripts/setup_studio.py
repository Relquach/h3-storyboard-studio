"""Isolated Singularity runtime for Windows Portable; no GGUF wrappers."""
import sys,pathlib
HERE=pathlib.Path(__file__).resolve().parent
sys.path[:]=[p for p in sys.path if pathlib.Path(p or '.').resolve()!=HERE];sys.path.append(str(HERE))
import argparse,json,os,shutil,subprocess,urllib.request,zipfile,uuid,hashlib,time
from downloads import download,sha256
ROOT=HERE.parent
MANIFEST=json.loads((ROOT/'manifest.json').read_text())
DEFAULT=pathlib.Path(r'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable')

def safe_extract(archive,target):
    target=pathlib.Path(target).resolve()
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            name=info.filename.replace('\\','/')
            if not (target/name).resolve().is_relative_to(target) or ':' in name:raise ValueError('Unsafe archive path')
            if (info.external_attr>>16)&0o170000==0o120000:raise ValueError('Archive symlink unsupported')
        for info in z.infolist():
            p=target/info.filename.replace('\\','/')
            if info.is_dir():p.mkdir(parents=True,exist_ok=True)
            else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info))

def unpack_repo(cache,spec):
    archive=cache/(spec['revision']+'.zip');download('https://github.com/'+spec['repo']+'/archive/'+spec['revision']+'.zip',archive)
    target=cache/spec['revision']
    if not target.exists():safe_extract(archive,target)
    children=[p for p in target.iterdir() if p.is_dir()]
    if len(children)!=1:raise ValueError('Unexpected repository archive')
    return children[0]

def freeze_audio(path):
    path=pathlib.Path(path);src=path.read_text();mark='# h3-audio-freeze patch'
    if mark in src:return 'already-patched'
    old='                piece = {"samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a))}\n                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)'
    if src.count(old)!=1:raise RuntimeError('Audio-freeze: mã upstream không khớp; dừng để không patch nhầm.')
    new='''                # h3-audio-freeze patch: retain pass-1 audio while refining video
                mv = torch.ones((1, 1, 1, chunk_v.shape[3], chunk_v.shape[4]),
                                device=chunk_v.device, dtype=torch.float32)
                ma = torch.zeros((1, 32, 2, chunk_a.shape[-1]),
                                 device=chunk_a.device, dtype=chunk_a.dtype)
                piece = {"samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a)),
                         "noise_mask": comfy.nested_tensor.NestedTensor((mv, ma))}
                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)'''
    backup=path.with_suffix('.py.before-audio-freeze')
    if not backup.exists():shutil.copy2(path,backup)
    path.write_text(src.replace(old,new),encoding='utf-8');return 'patched'

def check_portable(path):
    p=pathlib.Path(path).resolve()
    if not (p/'python_embeded/python.exe').is_file() or not (p/'ComfyUI/main.py').is_file():raise ValueError('Chọn thư mục chứa python_embeded và ComfyUI: '+str(p))
    return p

def state():
    p=ROOT/'local.json'
    if not p.exists():raise RuntimeError('Chạy INSTALL.bat trước.')
    return json.loads(p.read_text())

def driver_cuda():
    r=subprocess.run(['nvidia-smi','--query-gpu=driver_version','--format=csv,noheader'],capture_output=True,text=True,check=True)
    major=int(r.stdout.strip().splitlines()[0].split('.')[0])
    if major>=581:return 'cu130'
    if major>=572:return 'cu128'
    raise RuntimeError('Cần cập nhật driver NVIDIA lên nhánh 572 hoặc mới hơn trước khi cài runtime CUDA này.')

def install(portable,skip_models=False,full=False):
    portable=check_portable(portable);cuda=driver_cuda();base=portable/'H3-Singularity';comfy=base/'ComfyUI';python=base/'python_embeded/python.exe';shared=portable/'ComfyUI/models'
    selected=[m for m in MANIFEST['models'] if full or m['required']]
    missing=sum(m['bytes'] for m in selected if not (shared/m['destination']).exists())
    # Includes independent Python/core copy and some staging; render/pagefile space is additional.
    required=missing+6*1024**3
    if not skip_models and shutil.disk_usage(portable).free<required:raise RuntimeError(f'Cần ít nhất {required/1e9:.1f} GB trống cho bước cài; chưa gồm file video/pagefile.')
    base.mkdir(exist_ok=True);cache=base/'.cache';cache.mkdir(exist_ok=True)
    source=unpack_repo(cache,MANIFEST['core'])
    marker=comfy/'.singularity-core.json'
    if comfy.exists() and not marker.exists():raise RuntimeError('Thư mục H3-Singularity/ComfyUI đã có nhưng không thuộc bộ cài; dừng để bảo toàn dữ liệu.')
    if marker.exists() and json.loads(marker.read_text())['revision']!=MANIFEST['core']['revision']:raise RuntimeError('Core runtime khác phiên bản. Giữ runtime cũ và đổi tên thư mục H3-Singularity trước khi cài bản mới.')
    if not comfy.exists():
        staging=base/('ComfyUI.install-'+uuid.uuid4().hex[:8]);shutil.copytree(source,staging,ignore=shutil.ignore_patterns('__pycache__','.git'))
        (staging/'.singularity-core.json').write_text(json.dumps(MANIFEST['core']));staging.rename(comfy)
    if not python.exists():
        print('Sao chép Python Portable riêng; không sửa Python/ComfyUI hiện tại.',flush=True)
        staging=base/'python_embeded.installing'
        shutil.copytree(portable/'python_embeded',staging,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','pip-cache'))
        # Embedded Python can contain absolute original site-packages paths. Keep copied stdlib paths,
        # remove absolute injected entries, and enable copied local site-packages explicitly.
        for pth in staging.glob('python*._pth'):
            lines=pth.read_text().splitlines();lines=[l for l in lines if not pathlib.PureWindowsPath(l).is_absolute()]
            if 'import site' not in lines:lines.append('import site')
            pth.write_text('\n'.join(lines)+'\n')
        staging.rename(base/'python_embeded')
    subprocess.run([str(python),'-s','-m','pip','install','--upgrade','torch=='+MANIFEST['torch_version'],'torchvision=='+MANIFEST['torchvision_version'],'torchaudio=='+MANIFEST['torchaudio_version'],'--index-url','https://download.pytorch.org/whl/'+cuda],check=True)
    subprocess.run([str(python),'-s','-m','pip','install','-r',str(comfy/'requirements.txt')],check=True)
    plague=unpack_repo(cache,MANIFEST['plague']);backup=base/'backups';backup.mkdir(exist_ok=True)
    for name in ['ComfyUI-H3-UltimateUpscale-LD','ComfyUI-H3-UpscaleSize']:
        target=comfy/'custom_nodes'/name
        if target.exists():shutil.copytree(target,backup/(name+'-'+str(time.time_ns())),ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(plague/name,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(plague/'LICENSE',target/'LICENSE-PlagueKind')
    freeze_audio(comfy/'custom_nodes/ComfyUI-H3-UltimateUpscale-LD/nodes.py')
    for name in ['comfyui-h3-take','comfyui-video-finishing']:
        shutil.copytree(ROOT/'sources/local-nodes'/name,comfy/'custom_nodes'/name,dirs_exist_ok=True)
    # Dedicated models tree delegates to originals. Original weights are reused, never overwritten.
    comfy.joinpath('extra_model_paths.yaml').write_text('singularity_shared:\n  is_default: true\n  base_path: '+json.dumps(str(shared))+'\n'+''.join('  '+key+': '+key+'\n' for key in ['diffusion_models','text_encoders','vae','loras','latent_upscale_models']),encoding='utf-8')
    workflow_dir=comfy/'user/default/workflows';workflow_dir.mkdir(parents=True,exist_ok=True)
    for name in ['Storyboard-4060Ti-VI.json','KiemTra-5s-VI.json']:
        dest=workflow_dir/name
        if dest.exists():shutil.copy2(dest,backup/(name+'.'+str(time.time_ns())))
        shutil.copy2(ROOT/'workflows'/name,dest)
    conf={'portable':str(portable),'base':str(base),'comfy':str(comfy),'python':str(python),'models':str(shared),'url':'http://127.0.0.1:8189','cuda':cuda}
    (ROOT/'local.json').write_text(json.dumps(conf,indent=2),encoding='utf-8')
    if not skip_models:
        for m in selected:
            url='https://huggingface.co/'+m['repo']+'/resolve/'+m['revision']+'/'+m['file']
            download(url,shared/m['destination'],m['bytes'],m['sha256'])
    print('Cài hoàn tất. Chạy START.bat, rồi PREPARE.bat để chọn storyboard/sheet; CHECK.bat kiểm tra runtime.',flush=True)

def preflight():
    conf=state()
    with urllib.request.urlopen(conf['url']+'/object_info',timeout=30) as r:info=json.load(r)
    w=json.loads((ROOT/'workflows/Storyboard-4060Ti-VI.json').read_text())
    required={n['type'] for n in w['nodes'] if n.get('mode',0)==0 and n['type']!='MarkdownNote'}
    absent=sorted(required-info.keys())
    if absent:raise RuntimeError('Thiếu node runtime: '+', '.join(absent))
    checks={'UNETLoader':('unet_name',MANIFEST['models'][0]['file']), 'CLIPLoader':('clip_name',MANIFEST['models'][1]['file'].split('/')[-1]),'VAELoader':('vae_name','minimax_h3_video_vae_fp16.safetensors'),'LoraLoaderModelOnly':('lora_name','minimax_h3_ref2v_lightx2v_turbo_4step_v0.1_resized_avg_rank_20_bf16.safetensors')}
    for typ,(key,file) in checks.items():
        definition=info[typ]['input']['required'][key]
        options=definition[0] if isinstance(definition[0],list) else definition[1].get('options',[])
        if file not in options:raise RuntimeError('Runtime chưa thấy model: '+file)
    for m in MANIFEST['models']:
        if m['required']:
            p=pathlib.Path(conf['models'])/m['destination']
            if not p.is_file() or p.stat().st_size!=m['bytes']:raise RuntimeError('Model thiếu hoặc sai kích thước: '+str(p))
    nodepath=pathlib.Path(conf['comfy'])/'custom_nodes/ComfyUI-H3-UltimateUpscale-LD/nodes.py'
    if '# h3-audio-freeze patch' not in nodepath.read_text():raise RuntimeError('Thiếu bản vá giữ âm thanh')
    ready=sorted((pathlib.Path(conf['comfy'])/'user/default/workflows').glob('READY-*.json'),key=lambda p:p.stat().st_mtime)
    if not ready:raise RuntimeError('Chạy PREPARE.bat để chọn ảnh và sinh workflow READY trước khi kiểm tra đầu vào.')
    actual=json.loads(ready[-1].read_text());image_nodes=[n for n in actual['nodes'] if n['type']=='LoadImage' and n.get('mode',0)==0]
    for node in image_nodes:
        file=pathlib.Path(conf['comfy'])/'input'/node['widgets_values'][0]
        if not file.is_file():raise RuntimeError('Không thấy ảnh: '+str(file))
        from PIL import Image
        with Image.open(file) as im:im.verify()
    prompt=next(n for n in actual['nodes'] if n['id']==70)['widgets_values'][0]
    import re
    if '<Asset:' in prompt or any(not 1<=int(i)<=len(image_nodes) for i in re.findall(r'<Picture (\d+)>',prompt)):raise RuntimeError('Prompt và ảnh không khớp; chạy PREPARE lại.')
    report={'ready_workflow':str(ready[-1]),'images_checked':len(image_nodes),'checked_node_types':sorted(required),'models_size_checked':True,'audio_freeze':True,'render_tested':False}
    (ROOT/'reports/local-preflight.json').write_text(json.dumps(report,indent=2))
    print('Node, model, ảnh, mapping và audio-freeze: OK. Đây chưa phải render GPU.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['install','preflight','prepare','config']);ap.add_argument('--portable',default=str(DEFAULT));ap.add_argument('--skip-models',action='store_true');ap.add_argument('--full',action='store_true');ap.add_argument('--project');a=ap.parse_args()
    if a.action=='install':install(a.portable,a.skip_models,a.full)
    elif a.action=='preflight':preflight()
    elif a.action=='config':print(json.dumps(state()))
    else:
        from assets import prepare
        conf=state();project=json.loads(pathlib.Path(a.project).read_text(encoding='utf-8-sig'));template=json.loads((ROOT/'workflows/template.json').read_text())
        out=pathlib.Path(conf['comfy'])/'user/default/workflows'/('READY-'+uuid.uuid4().hex[:8]+'.json');print(prepare(template,project,conf['comfy'],out))
if __name__=='__main__':
    try:main()
    except Exception as e:print('\nLỖI:',e,flush=True);raise
