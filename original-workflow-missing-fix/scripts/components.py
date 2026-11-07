"""Install the original workflow's non-registry H3 packs, preserving backups."""
import hashlib,json,pathlib,shutil,time,uuid

def freeze_audio(path):
    path=pathlib.Path(path);text=path.read_text(encoding='utf-8')
    if '# h3-audio-freeze patch' in text:return False
    old='                piece = {"samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a))}\n                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)'
    if text.count(old)!=1:raise ValueError('Audio-freeze không khớp mã đã khóa; dừng để tránh patch nhầm.')
    new='''                # h3-audio-freeze patch: preserve original audio during untiled refine
                mv = torch.ones((1, 1, 1, chunk_v.shape[3], chunk_v.shape[4]),
                                device=chunk_v.device, dtype=torch.float32)
                ma = torch.zeros((1, 32, 2, chunk_a.shape[-1]),
                                 device=chunk_a.device, dtype=chunk_a.dtype)
                piece = {"samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a)),
                         "noise_mask": comfy.nested_tensor.NestedTensor((mv, ma))}
                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)'''
    backup=path.with_suffix('.py.before-audio-freeze')
    if not backup.exists():shutil.copy2(path,backup)
    path.write_text(text.replace(old,new),encoding='utf-8');return True


def fingerprint(root):
    root=pathlib.Path(root);h=hashlib.sha256()
    for p in sorted(root.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name.startswith('.h3-'):continue
        h.update(p.relative_to(root).as_posix().encode());h.update(b'\0');h.update(p.read_bytes());h.update(b'\0')
    return h.hexdigest()


def find_target(comfy,name):
    custom=pathlib.Path(comfy)/'custom_nodes';found=[]
    if custom.exists():
        for parent in custom.iterdir():
            if not parent.is_dir():continue
            normalized=parent.name.removesuffix('-main').removesuffix('-master').lower()
            if normalized==name.lower() and (parent/'__init__.py').exists():found.append(parent)
            nested=parent/name
            if (nested/'__init__.py').is_file():found.append(nested)
    found=list(dict.fromkeys(found))
    if len(found)>1:raise ValueError('Có nhiều bản '+name+': '+', '.join(str(p) for p in found))
    return found[0] if found else custom/name


def put_component(comfy,name,source):
    comfy=pathlib.Path(comfy);source=pathlib.Path(source)
    if not (source/'__init__.py').is_file():raise ValueError('Thiếu source component: '+name)
    target=find_target(comfy,name);value=fingerprint(source);marker=target/'.h3-component.json'
    if marker.is_file():
        data=json.loads(marker.read_text(encoding='utf-8'))
        if data.get('fingerprint')==value and fingerprint(target)==value:
            print('Đã có component đúng bản:',target,flush=True);return target
    backup=None;target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        folder=comfy/'user/h3_missing_fix/backups';folder.mkdir(parents=True,exist_ok=True)
        backup=folder/(target.name+'-'+str(time.time_ns()));target.rename(backup)
    try:
        shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__'))
        marker.write_text(json.dumps({'component':name,'fingerprint':value}),encoding='utf-8')
    except Exception:
        if target.exists():shutil.rmtree(target)
        if backup:backup.rename(target)
        raise
    print('Đã bổ sung:',target,flush=True);return target


def install_h3_components(comfy,cache,manifest,root,download,extract_repo):
    comfy=pathlib.Path(comfy);cache=pathlib.Path(cache);root=pathlib.Path(root);installed=[]
    if manifest.get('plague'):
        spec=manifest['plague'];archive=cache/(spec['revision']+'.zip')
        download('https://github.com/'+spec['repo']+'/archive/'+spec['revision']+'.zip',archive,spec['archive_bytes'],spec['archive_sha256'])
        staging=comfy/'user/h3_missing_fix/staging'/uuid.uuid4().hex;staging.mkdir(parents=True,exist_ok=True)
        source=extract_repo(archive,staging,required_files=['__init__.py','ComfyUI-H3-UltimateUpscale-LD/nodes.py','ComfyUI-H3-UpscaleSize/upscale_size.py'])
        freeze_audio(source/'ComfyUI-H3-UltimateUpscale-LD/nodes.py')
        for name in spec['components']:
            part=source/name
            if (source/'LICENSE').exists():shutil.copy2(source/'LICENSE',part/'LICENSE-PlagueKind')
            installed.append(put_component(comfy,name,part))
        shutil.rmtree(staging,ignore_errors=True)
    for name in manifest.get('bundled_nodes',[]):installed.append(put_component(comfy,name,root/'bundled-nodes'/name))
    return installed
