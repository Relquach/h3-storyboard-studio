"""H3 Take: keep a MiniMax-H3 pass 1 on disk and upscale it later.

Save H3 Take sits between the pass 1 sampler and the decoder. It writes the
finished AV latent, plus the conditioning that made it (text embeddings,
reference and keyframe latents), to output/h3_takes as one .h3take file and
passes the latent straight through. Load H3 Take reads a take back, so the
upscale pass can run on it without re-running pass 1 or the text encoder.

A .h3take file is a safetensors file. The tensors are stored as tensors, and
the structure around them (dicts, lists, NestedTensor, plain values) is JSON
in the header, so loading a take never unpickles anything.
"""

import json
import math
import numbers
import os
import time

import safetensors.torch
import torch

import comfy.model_management
import comfy.nested_tensor
import folder_paths
from comfy.cli_args import args
from comfy.ldm.minimax.model import FRAME_PER_TOKEN

TAKES_SUBFOLDER = "h3_takes"
EXTENSION = ".h3take"
LATEST = "latest"
FORMAT_VERSION = "1"
FPS = 24


def takes_dir():
    return os.path.join(folder_paths.get_output_directory(), TAKES_SUBFOLDER)


def list_takes():
    """Take names (file name without the extension), newest first."""
    try:
        entries = [e for e in os.scandir(takes_dir()) if e.is_file() and e.name.endswith(EXTENSION)]
    except FileNotFoundError:
        return []
    entries.sort(key=lambda e: e.stat().st_mtime, reverse=True)
    return [e.name[:-len(EXTENSION)] for e in entries]


def resolve_take(take):
    """Path of the take file for a combo value, or None if there is no such take."""
    if take == LATEST:
        takes = list_takes()
        if not takes:
            return None
        take = takes[0]
    if not take or os.path.basename(take) != take:
        return None
    path = os.path.join(takes_dir(), take + EXTENSION)
    return path if os.path.isfile(path) else None


def h3_video_latent(latent):
    samples = latent.get("samples") if isinstance(latent, dict) else None
    if not isinstance(samples, comfy.nested_tensor.NestedTensor) or len(samples.tensors) != 2:
        raise ValueError("H3 Take expects a MiniMax H3 AV latent (video + audio)")
    video = samples.tensors[0]
    if video.ndim != 5 or video.shape[1] != 24:
        raise ValueError("H3 Take expects a MiniMax H3 AV latent, got a video latent of shape {}".format(tuple(video.shape)))
    return video


class TakePacker:
    """Turns a latent/conditioning tree into JSON plus a flat dict of tensors."""

    def __init__(self):
        self.tensors = {}
        self.keys_by_id = {}

    def tensor(self, t):
        key = self.keys_by_id.get(id(t))
        if key is None:
            key = "t{}".format(len(self.tensors))
            self.keys_by_id[id(t)] = key
            # clone: safetensors refuses tensors that share storage (views of one buffer)
            self.tensors[key] = t.detach().to("cpu").clone().contiguous()
        return {"__tensor__": key}

    def pack(self, value, path):
        if isinstance(value, torch.Tensor):
            return self.tensor(value)
        if isinstance(value, comfy.nested_tensor.NestedTensor):
            return {"__nested__": [self.pack(t, "{}[{}]".format(path, i)) for i, t in enumerate(value.tensors)]}
        if value is None or isinstance(value, (bool, str)):
            return value
        if isinstance(value, numbers.Integral):
            return int(value)
        if isinstance(value, numbers.Real):
            value = float(value)
            return value if math.isfinite(value) else {"__float__": repr(value)}
        if isinstance(value, dict):
            bad = [k for k in value if not isinstance(k, str)]
            if bad:
                raise TypeError("H3 Take can't save {}: non-text key {!r}".format(path, bad[0]))
            return {"__dict__": {k: self.pack(v, "{}.{}".format(path, k)) for k, v in value.items()}}
        if isinstance(value, list):
            return [self.pack(v, "{}[{}]".format(path, i)) for i, v in enumerate(value)]
        if isinstance(value, tuple):
            return {"__tuple__": [self.pack(v, "{}[{}]".format(path, i)) for i, v in enumerate(value)]}
        if isinstance(value, torch.dtype):
            return {"__dtype__": str(value).removeprefix("torch.")}
        if isinstance(value, torch.device):
            return {"__device__": str(value)}
        raise TypeError("H3 Take can't save {} ({}.{})".format(path, type(value).__module__, type(value).__name__))


def unpack(value, tensors):
    if isinstance(value, list):
        return [unpack(v, tensors) for v in value]
    if not isinstance(value, dict):
        return value
    if "__tensor__" in value:
        return tensors[value["__tensor__"]]
    if "__nested__" in value:
        return comfy.nested_tensor.NestedTensor([unpack(v, tensors) for v in value["__nested__"]])
    if "__dict__" in value:
        return {k: unpack(v, tensors) for k, v in value["__dict__"].items()}
    if "__tuple__" in value:
        return tuple(unpack(v, tensors) for v in value["__tuple__"])
    if "__float__" in value:
        return float(value["__float__"])
    if "__dtype__" in value:
        dtype = getattr(torch, value["__dtype__"], None)
        if not isinstance(dtype, torch.dtype):
            raise ValueError("unknown dtype in H3 take: {}".format(value["__dtype__"]))
        return dtype
    if "__device__" in value:
        return torch.device(value["__device__"])
    raise ValueError("unknown entry in H3 take: {}".format(sorted(value)))


class H3TakeSave:
    DESCRIPTION = (
        "Saves the finished pass 1 of a MiniMax H3 video to output/h3_takes as a .h3take file: "
        "the video+audio latent and the conditioning that made it. The latent passes straight "
        "through, so the preview decodes exactly as before. Load H3 Take reads it back for the "
        "upscale pass, without re-running pass 1 or the text encoder."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT", {"tooltip": "The finished pass 1 latent (sampler output)."}),
                "conditioning": ("CONDITIONING", {"tooltip": "The positive conditioning pass 1 was sampled with."}),
                "take_prefix": ("STRING", {"default": "MiniMaxH3_take", "tooltip": "Takes are named <prefix>_00001_, <prefix>_00002_, ..."}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("LATENT", "STRING", "STRING")
    RETURN_NAMES = ("latent", "take_name", "video_prefix")
    OUTPUT_TOOLTIPS = (
        "The same latent, unchanged.",
        "Name of the saved take, e.g. MiniMaxH3_take_00007_",
        "video/<take name>preview - use it as the Save Video filename_prefix so the preview matches its take.",
    )
    FUNCTION = "save"
    CATEGORY = "model/latent/minimax"

    def save(self, latent, conditioning, take_prefix, prompt=None, extra_pnginfo=None):
        video = h3_video_latent(latent)
        prefix = take_prefix.strip().replace("\\", "_").replace("/", "_") or "MiniMaxH3_take"
        full_folder, filename, counter, _, _ = folder_paths.get_save_image_path(
            "{}/{}".format(TAKES_SUBFOLDER, prefix), folder_paths.get_output_directory())
        take_name = "{}_{:05}_".format(filename, counter)

        packer = TakePacker()
        tree = {"latent": packer.pack(latent, "latent"), "conditioning": packer.pack(conditioning, "conditioning")}
        frames = sum(FRAME_PER_TOKEN[k % 5] for k in range(video.shape[2]))
        info = {
            "take": take_name,
            "width": video.shape[4] * 16,
            "height": video.shape[3] * 16,
            "frames": frames,
            "seconds": round(frames / FPS, 2),
            "saved": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        metadata = {
            "h3take_format": FORMAT_VERSION,
            "h3take_tree": json.dumps(tree),
            "h3take_info": json.dumps(info),
        }
        if not args.disable_metadata:
            if prompt is not None:
                metadata["prompt"] = json.dumps(prompt)
            if extra_pnginfo is not None:
                for k in extra_pnginfo:
                    metadata[k] = json.dumps(extra_pnginfo[k])

        path = os.path.join(full_folder, take_name + EXTENSION)
        part = path + ".part"
        try:
            safetensors.torch.save_file(packer.tensors, part, metadata=metadata)
            # rename last, so "latest" never picks up a half-written take
            os.replace(part, path)
        finally:
            if os.path.exists(part):
                os.remove(part)
        print("[H3 Take] saved {} ({}x{}, {} frames)".format(path, info["width"], info["height"], frames))
        return (latent, take_name, "video/{}preview".format(take_name))


class H3TakeLoad:
    DESCRIPTION = (
        "Loads a take saved by Save H3 Take: the pass 1 video+audio latent and its conditioning, "
        "plus the take's pixel size. 'latest' is the newest take on disk. Press R in ComfyUI "
        "to refresh the list after new takes are saved."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "take": ([LATEST] + list_takes(), {"tooltip": "latest = the newest take in output/h3_takes. Press R to refresh this list."}),
            },
        }

    RETURN_TYPES = ("LATENT", "CONDITIONING", "INT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("latent", "conditioning", "width", "height", "take_name", "video_prefix")
    OUTPUT_TOOLTIPS = (
        "The pass 1 video+audio latent.",
        "The conditioning pass 1 was sampled with.",
        "Pass 1 width in pixels.",
        "Pass 1 height in pixels.",
        "Name of the loaded take.",
        "video/<take name>UPSCALED - use it as the Save Video filename_prefix.",
    )
    FUNCTION = "load"
    CATEGORY = "model/latent/minimax"

    @classmethod
    def VALIDATE_INPUTS(cls, take):
        # Accept any name here and check it in load() instead. ComfyUI validates this node even
        # when a switch leaves it unused (step 1), and the combo list goes stale as takes are
        # saved, so a strict check would block runs that never read a take.
        return True

    @classmethod
    def IS_CHANGED(cls, take):
        path = resolve_take(take)
        if path is None:
            return ""
        st = os.stat(path)
        return "{}|{}|{}".format(path, st.st_mtime_ns, st.st_size)

    def load(self, take):
        path = resolve_take(take)
        if path is None:
            if take == LATEST:
                raise RuntimeError("No H3 takes saved yet. Run the workflow once in step 1 (make video) first.")
            raise RuntimeError("H3 take not found in output/{}: {}".format(TAKES_SUBFOLDER, take))

        # read the whole file instead of memory-mapping it, so Windows doesn't keep
        # the take locked (undeletable) while ComfyUI caches the loaded tensors
        with open(path, "rb") as f:
            data = f.read()
        header_size = int.from_bytes(data[:8], "little")
        metadata = json.loads(data[8:8 + header_size]).get("__metadata__") or {}
        if metadata.get("h3take_format") != FORMAT_VERSION:
            raise RuntimeError("{} is not an H3 take this node can read".format(path))
        device = comfy.model_management.intermediate_device()
        tensors = {k: t.to(device) for k, t in safetensors.torch.load(data).items()}
        del data
        tree = json.loads(metadata["h3take_tree"])
        latent = unpack(tree["latent"], tensors)
        conditioning = unpack(tree["conditioning"], tensors)

        video = h3_video_latent(latent)
        name = os.path.basename(path)[:-len(EXTENSION)]
        print("[H3 Take] loaded {}".format(path))
        return (latent, conditioning, video.shape[4] * 16, video.shape[3] * 16, name, "video/{}UPSCALED".format(name))


NODE_CLASS_MAPPINGS = {
    "H3TakeSave": H3TakeSave,
    "H3TakeLoad": H3TakeLoad,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "H3TakeSave": "Save H3 Take (pass 1 to disk)",
    "H3TakeLoad": "Load H3 Take (for upscale)",
}
