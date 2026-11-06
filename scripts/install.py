"""Idempotent installer for an existing Windows ComfyUI Portable; stdlib downloads."""

# Portable bootstrap: pythonXY._pth may omit the script directory.
# Add only this trusted package directory; never change global Python settings.
import sys as _sys
from pathlib import Path as _Path
_script_dir = _Path(__file__).resolve().parent
# Keep stdlib and embedded extension modules ahead of sibling utilities.
_sys.path[:] = [entry for entry in _sys.path if _Path(entry or ".").resolve() != _script_dir]
_sys.path.append(str(_script_dir))
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile

from portable_paths import ROOT, DEFAULT_PORTABLE, portable_path


def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def download(url, dest, expected_size=None, expected_hash=None, attempts=4):
    dest=pathlib.Path(dest); dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        if (expected_size is None or dest.stat().st_size==expected_size) and (not expected_hash or sha256(dest)==expected_hash):
            print('Verified existing:',dest.name,flush=True);return
        # Do not delete or replace an existing user's model on a mismatch.
        raise RuntimeError(f'Existing file differs from manifest: {dest}. Rename it manually before retrying.')
    part=dest.with_name(dest.name+'.part')
    for attempt in range(attempts):
        start=part.stat().st_size if part.exists() else 0
        if expected_size and start==expected_size:break
        try:
            req=urllib.request.Request(url,headers={'Range':f'bytes={start}-'} if start else {})
            with urllib.request.urlopen(req,timeout=90) as response:
                resumed=start>0 and response.status==206
                if resumed and not response.headers.get('Content-Range','').startswith(f'bytes {start}-'):
                    raise RuntimeError('Server returned a mismatched download range')
                mode='ab' if resumed else 'wb'
                with open(part,mode) as out:
                    copied=start if resumed else 0;last=time.monotonic()
                    while True:
                        data=response.read(4*1024*1024)
                        if not data:break
                        out.write(data);copied+=len(data)
                        if time.monotonic()-last>10:
                            print(f'{dest.name}: {copied/1e9:.2f} GB',flush=True);last=time.monotonic()
            break
        except Exception:
            if attempt+1==attempts:raise
            time.sleep(min(2**attempt,8))
    if expected_size is not None and part.stat().st_size!=expected_size:raise RuntimeError('Incomplete download: '+dest.name)
    if expected_hash and sha256(part)!=expected_hash:
        # Keep it for diagnosis, but do not repeatedly resume a corrupt full file.
        part.rename(part.with_name(part.name+'.corrupt-'+str(time.time_ns())))
        raise RuntimeError('SHA256 mismatch: '+dest.name)
    part.replace(dest)


def safe_extract(archive,target):
    target=pathlib.Path(target).resolve()
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            resolved=(target/info.filename).resolve()
            if not resolved.is_relative_to(target) or '\\' in info.filename:raise RuntimeError('Unsafe archive path')
        z.extractall(target)



def install(portable, skip_models=False, dry_run=False):
    portable=portable_path(portable);comfy=portable/'ComfyUI';py=portable/'python_embeded/python.exe'
    manifest=json.loads((ROOT/'manifest.json').read_text())
    missing=sum(m['bytes'] for m in manifest['models'] if not (comfy/m['destination']).exists())
    print(f'Target: {comfy}\nModel downloads still needed: {missing/1e9:.2f} GB')
    print('No ComfyUI core update, no launch-flag changes to existing BATs, no existing model overwrite.')
    if dry_run:return
    if shutil.disk_usage(comfy).free < missing + 8*1024**3:
        raise RuntimeError('Not enough free disk space: model downloads + 8 GiB reserve required.')
    # Verify the installed core has the H3 implementation before installing addons.
    core=comfy/'comfy_extras/nodes_minimax_h3.py'
    if not core.exists() or 'class MiniMaxH3ReferenceToVideo' not in core.read_text(encoding='utf-8'):
        raise RuntimeError('ComfyUI is too old. Back up and update it with its official updater, then rerun INSTALL.bat.')
    cache=ROOT/'.cache';cache.mkdir(exist_ok=True)
    for item in manifest['custom_nodes']:
        target=comfy/'custom_nodes'/item['folder'];marker=target/'.h3studio-revision'
        if target.exists():
            if not marker.exists() or marker.read_text().strip()!=item['revision']:
                raise RuntimeError(f'Addon already exists at {target}; not overwriting it. Back it up/move it, or use a separate Portable installation.')
        else:
            archive=cache/(item['folder']+'-'+item['revision']+'.zip')
            download(f'https://github.com/{item["repo"]}/archive/{item["revision"]}.zip',archive)
            unpack=cache/('unpack-'+item['folder']);unpack.mkdir(exist_ok=True);safe_extract(archive,unpack)
            children=[p for p in unpack.iterdir() if p.is_dir()]
            if len(children)!=1:raise RuntimeError('Unexpected node archive layout')
            shutil.copytree(children[0],target)
            marker.write_text(item['revision'])
        requirements=target/'requirements.txt'
        if requirements.exists():subprocess.run([str(py),'-s','-m','pip','install','-r',str(requirements)],check=True)
    subprocess.run([str(py),'-s','-m','pip','install','gguf'],check=True)
    custom=comfy/'custom_nodes/h3_storyboard_studio'
    shutil.copytree(ROOT/'custom_nodes/h3_storyboard_studio',custom,dirs_exist_ok=True)
    if not skip_models:
        for m in manifest['models']:
            url=m.get('url') or f'https://huggingface.co/{m["repo"]}/resolve/{m["revision"]}/{urllib.parse.quote(m["file"],safe="/")}'
            download(url,comfy/m['destination'],m['bytes'],m['sha256'])
    # Catch the previous wrong llama.cpp-loader choice before queueing a GPU task.
    encoder=comfy/'models/text_encoders/qwen3vl_32b_minimax_h3-Q2_K_M.gguf'
    if encoder.exists():
        import importlib.util
        spec=importlib.util.spec_from_file_location('native_header',ROOT/'custom_nodes/h3_storyboard_studio/native_encoder.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.inspect_native_header(encoder)
    (ROOT/'local.json').write_text(json.dumps({'portable':str(portable),'comfy':str(comfy)},indent=2))
    inputs=comfy/'input/h3studio';inputs.mkdir(parents=True,exist_ok=True)
    print('Installed. Run START-STUDIO.bat. GPU inference is not yet validated; inspect reports after the first render.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--portable',default=str(DEFAULT_PORTABLE));p.add_argument('--skip-models',action='store_true');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    install(a.portable,a.skip_models,a.dry_run)
