"""Local-only path helpers. Safe to import without loading networking modules."""
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_PORTABLE = pathlib.Path(r'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable')


def portable_path(value):
    path=pathlib.Path(value).resolve()
    if not (path/'python_embeded/python.exe').is_file() or not (path/'ComfyUI/main.py').is_file():
        raise ValueError('Select the Portable root containing python_embeded and ComfyUI, not the ComfyUI subfolder.')
    return path
