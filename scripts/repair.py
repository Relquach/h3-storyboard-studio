"""Repair only this package's custom node; never download/delete/modify model weights."""

# Portable bootstrap: pythonXY._pth may omit the script directory.
# Add only this trusted package directory; never change global Python settings.
import sys as _sys
from pathlib import Path as _Path
_script_dir = _Path(__file__).resolve().parent
# Keep stdlib and embedded extension modules ahead of sibling utilities.
_sys.path[:] = [entry for entry in _sys.path if _Path(entry or ".").resolve() != _script_dir]
_sys.path.append(str(_script_dir))
import argparse,json,pathlib,shutil
from portable_paths import ROOT,DEFAULT_PORTABLE,portable_path

def repair(portable):
    portable=portable_path(portable);comfy=portable/'ComfyUI'
    source=ROOT/'custom_nodes/h3_storyboard_studio';target=comfy/'custom_nodes/h3_storyboard_studio'
    backup=comfy/'user/h3studio_backups'
    if target.exists():
        import time
        backup.mkdir(parents=True,exist_ok=True)
        # Store backup OUTSIDE custom_nodes so ComfyUI cannot register old node classes twice.
        shutil.copytree(target,backup/('h3_storyboard_studio-'+str(time.time_ns())),ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(source,target,dirs_exist_ok=True)
    (ROOT/'local.json').write_text(json.dumps({'portable':str(portable),'comfy':str(comfy)},indent=2))
    encoder=comfy/'models/text_encoders/qwen3vl_32b_minimax_h3-Q2_K_M.gguf'
    if encoder.exists():
        import importlib.util
        spec=importlib.util.spec_from_file_location('native_header',source/'native_encoder.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        tensors=mod.inspect_native_header(encoder)
        print('Encoder native hợp lệ:',len(tensors),'tensor; giữ nguyên file đã tải.')
    else:print('Chưa tìm thấy encoder Q2; cần cài model trước khi render.')
    print('Đã cập nhật node. Đóng hẳn rồi mở lại ComfyUI để nạp loader mới.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--portable',default=str(DEFAULT_PORTABLE));a=p.parse_args();repair(a.portable)
