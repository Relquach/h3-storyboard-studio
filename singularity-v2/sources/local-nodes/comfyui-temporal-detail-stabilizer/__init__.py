"""Temporal Detail Stabilizer: stops upscaler detail (skin, hair, fabric) from changing every frame.

Each frame is split into a base layer (shapes, colour, light) and a fine detail layer.
The neighbouring frames are aligned to it with optical flow, and only the detail layer is
averaged across them. Detail an upscaler invents differently per frame cancels out; real
detail lines up and stays sharp. Where alignment fails (fast motion, blinking, mouth
opening) the neighbour is ignored, so moving parts do not ghost.
"""
import math

import cv2
import numpy as np
import torch
import torch.nn.functional as F

LUMA = (0.2126, 0.7152, 0.0722)  # Rec.709


def _device():
    try:
        import comfy.model_management as mm
        return mm.get_torch_device()
    except Exception:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _gaussian_blur(x, sigma):
    """Separable gaussian blur of a [B,C,H,W] tensor."""
    c, h, w = x.shape[1:]
    radius = max(1, min(int(math.ceil(sigma * 3)), h - 1, w - 1))
    t = torch.arange(-radius, radius + 1, device=x.device, dtype=x.dtype)
    k = torch.exp(-(t * t) / (2 * sigma * sigma))
    k = (k / k.sum()).repeat(c, 1)
    x = F.conv2d(F.pad(x, (radius, radius, 0, 0), mode="reflect"), k.view(c, 1, 1, -1), groups=c)
    return F.conv2d(F.pad(x, (0, 0, radius, radius), mode="reflect"), k.view(c, 1, -1, 1), groups=c)


class _Flow:
    """DIS optical flow on downscaled grey frames, cached per frame pair."""

    def __init__(self, frames, flow_scale):
        self.frames = frames
        self.flow_scale = flow_scale
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        self.grey = {}

    def _grey(self, i):
        if i not in self.grey:
            f = self.frames[i].float().numpy()
            g = f @ np.array(LUMA, dtype=np.float32)
            h, w = g.shape
            g = cv2.resize(g, (round(w * self.flow_scale), round(h * self.flow_scale)), interpolation=cv2.INTER_AREA)
            self.grey[i] = np.clip(g * 255, 0, 255).astype(np.uint8)
            self.grey.pop(i - 8, None)
        return self.grey[i]

    def __call__(self, t, k):
        """Flow from frame t to frame k, in pixels of the full-size frame, [H,W,2]."""
        flow = self.dis.calc(self._grey(t), self._grey(k), None)
        return torch.from_numpy(flow) / self.flow_scale


def _warp(img, flow, base_grid):
    """Sample img [1,C,H,W] at x + flow so it lines up with the target frame."""
    h, w = img.shape[-2:]
    flow = F.interpolate(flow.permute(2, 0, 1)[None], size=(h, w), mode="bilinear", align_corners=False)
    grid = base_grid + torch.stack((flow[:, 0] * 2 / (w - 1), flow[:, 1] * 2 / (h - 1)), dim=-1)
    return F.grid_sample(img, grid, mode="bilinear", padding_mode="border", align_corners=True)


def stabilize(images, radius=2, detail_sigma=2.0, strength=1.0, motion_tolerance=0.03, flow_scale=0.5, progress=None):
    n, h, w, _ = images.shape
    dev = _device()
    out = torch.empty_like(images)
    flow = _Flow(images, flow_scale)
    ys, xs = torch.meshgrid(torch.linspace(-1, 1, h, device=dev), torch.linspace(-1, 1, w, device=dev), indexing="ij")
    base_grid = torch.stack((xs, ys), dim=-1)[None]
    luma = torch.tensor(LUMA, device=dev).view(1, 3, 1, 1)

    def split(i):
        x = images[i:i + 1].to(dev, torch.float32).permute(0, 3, 1, 2)
        base = _gaussian_blur(x, detail_sigma)
        return base, x - base

    for t in range(n):
        base_t, detail_t = split(t)
        acc, wsum = detail_t.clone(), torch.ones_like(base_t[:, :1])
        for k in range(max(0, t - radius), min(n, t + radius + 1)):
            if k == t:
                continue
            f = flow(t, k).to(dev)
            base_k, detail_k = split(k)
            warped = _warp(torch.cat((base_k, detail_k), dim=1), f, base_grid)
            # Trust a neighbour only where its base layer lines up with this frame's.
            diff = ((warped[:, :3] - base_t) * luma).sum(1, keepdim=True).abs()
            wk = torch.exp(-(diff / motion_tolerance) ** 2) * math.exp(-0.5 * ((k - t) / max(radius, 1)) ** 2)
            acc += warped[:, 3:] * wk
            wsum += wk
        detail = detail_t + strength * (acc / wsum - detail_t)
        out[t] = (base_t + detail).clamp(0, 1).permute(0, 2, 3, 1)[0].to(out.dtype).cpu()
        if progress is not None:
            progress.update(1)
    return out


class TemporalDetailStabilizer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "radius": ("INT", {"default": 2, "min": 1, "max": 4,
                    "tooltip": "Frames on each side to average with. 2 = 5 frames. Higher = calmer but slower."}),
                "detail_sigma": ("FLOAT", {"default": 2.0, "min": 0.5, "max": 8.0, "step": 0.1,
                    "tooltip": "Size of the detail that gets stabilized, in pixels. 2 = skin/hair texture. Higher also calms bigger shapes."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "1 = full stabilizing, 0 = off."}),
                "motion_tolerance": ("FLOAT", {"default": 0.03, "min": 0.005, "max": 0.2, "step": 0.005,
                    "tooltip": "How different a neighbour may look before it is ignored. Lower = safer on fast motion (no ghosting), higher = calmer."}),
                "flow_scale": ("FLOAT", {"default": 0.5, "min": 0.25, "max": 1.0, "step": 0.25,
                    "tooltip": "Resolution of the motion tracking. 0.5 is accurate and fast."}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "main"
    CATEGORY = "video"
    DESCRIPTION = "Stops fine detail (skin, hair, fabric) from changing every frame after an AI upscaler."

    def main(self, images, radius, detail_sigma, strength, motion_tolerance, flow_scale):
        import comfy.utils
        if images.shape[0] < 2 or strength == 0:
            return (images,)
        pbar = comfy.utils.ProgressBar(images.shape[0])
        with torch.no_grad():
            return (stabilize(images, radius, detail_sigma, strength, motion_tolerance, flow_scale, pbar),)


def _restore_texture(x, o, amount, sigma=1.0):
    """Add the original's fine luma grain back where the upscaler smoothed it away (waxy skin).

    Compares the fine-detail energy of both around each pixel: where the upscaled frame
    already has as much as the original (edges, hair, eyes) nothing is added.
    """
    luma = torch.tensor(LUMA, device=x.device).view(1, 3, 1, 1)
    hp_x = ((x - _gaussian_blur(x, sigma)) * luma).sum(1, keepdim=True)
    hp_o = ((o - _gaussian_blur(o, sigma)) * luma).sum(1, keepdim=True)
    e_x = _gaussian_blur(hp_x * hp_x, 3.0)
    e_o = _gaussian_blur(hp_o * hp_o, 3.0)
    lost = (1 - torch.sqrt(e_x / (e_o + 1e-8))).clamp(0, 1)
    return x + amount * lost * hp_o


def _skin_grain(x, amount, seed):
    """Fine luma grain (pore-sized) on smooth areas only, so waxy skin gets some texture back.

    Busy areas (hair, edges, fabric) get none; shadows and highlights get less, like real film grain.
    """
    luma = torch.tensor(LUMA, device=x.device).view(1, 3, 1, 1)
    l = (x * luma).sum(1, keepdim=True)
    hp = l - _gaussian_blur(l, 1.0)
    smooth = torch.exp(-_gaussian_blur(hp * hp, 3.0) / 4e-5)
    mid = (4 * l * (1 - l)).clamp(0, 1)
    g = torch.Generator(device="cpu").manual_seed(seed)
    noise = _gaussian_blur(torch.randn(l.shape, generator=g).to(x.device), 0.7)
    noise = noise / noise.std()
    return x + amount * 0.02 * smooth * mid * noise


def match_tone(images, original, radius=4.0, strength=1.0, contrast_limit=0.015, limit_window=5,
               skin_texture=0.0, skin_grain=0.0, progress=None):
    """Keep the fine detail of images, take everything coarser (brightness, contrast, colour) from original.

    contrast_limit: no pixel may get darker/brighter than the original's darkest/brightest
    within limit_window pixels, plus this margin. Stops the upscaler inking in darker brows,
    lids and hair strands, while edges stay sharp. 1.0 = off.
    skin_texture: brings back the original's own fine grain where the upscaler made skin waxy.
    """
    n, h, w, _ = images.shape
    dev = _device()
    out = torch.empty_like(images)
    pad = limit_window // 2
    for t in range(n):
        x = images[t:t + 1].to(dev, torch.float32).permute(0, 3, 1, 2)
        o = original[min(t, original.shape[0] - 1)][None].to(dev, torch.float32).permute(0, 3, 1, 2)
        if o.shape[-2:] != (h, w):
            o = F.interpolate(o, size=(h, w), mode="bicubic", align_corners=False, antialias=o.shape[-1] > w)
        y = x + strength * (_gaussian_blur(o, radius) - _gaussian_blur(x, radius))
        if skin_texture > 0:
            y = _restore_texture(y, o, skin_texture)
        if contrast_limit < 1:
            hi = F.max_pool2d(F.pad(o, (pad,) * 4, mode="replicate"), limit_window, stride=1)
            lo = -F.max_pool2d(F.pad(-o, (pad,) * 4, mode="replicate"), limit_window, stride=1)
            y = torch.minimum(torch.maximum(y, lo - contrast_limit), hi + contrast_limit)
        if skin_grain > 0:
            y = _skin_grain(y, skin_grain, t)
        out[t] = y.clamp(0, 1).permute(0, 2, 3, 1)[0].to(out.dtype).cpu()
        if progress is not None:
            progress.update(1)
    return out


class MatchToneToOriginal:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Upscaled frames."}),
                "original": ("IMAGE", {"tooltip": "The same frames before upscaling (any size), e.g. the Load Video output."}),
                "radius": ("FLOAT", {"default": 4.0, "min": 1.0, "max": 20.0, "step": 0.5,
                    "tooltip": "Detail finer than this (pixels) is kept from the upscaler, everything coarser comes from the original. Lower = closer to the original look, higher = more upscaler punch."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "1 = tone exactly like the original, 0 = off."}),
                "contrast_limit": ("FLOAT", {"default": 0.015, "min": 0.0, "max": 1.0, "step": 0.005,
                    "tooltip": "How much darker/brighter than the original any spot may get. Stops darker brows, lids and hair lines. 0 = never beyond the original, 0.03 = a bit more punch, 1 = off."}),
                "limit_window": ("INT", {"default": 5, "min": 3, "max": 15, "step": 2,
                    "tooltip": "Size of the 'same spot' in pixels for contrast_limit. Bigger = looser."}),
            },
            "optional": {
                "skin_texture": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 2.0, "step": 0.05,
                    "tooltip": "Brings back the original's fine skin grain where the upscaler made it waxy. 0 = off, 0.6 = natural, 1 = full original grain. Edges are not touched."}),
                "skin_grain": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3.0, "step": 0.05,
                    "tooltip": "Adds fine pore-sized grain on smooth areas (skin) only, against the plastic look. 0 = off, 0.5 = subtle, 1 = visible."}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "main"
    CATEGORY = "video"
    DESCRIPTION = "Gives upscaled video the brightness, contrast and colour of the original, keeping the upscaler's sharp detail."

    def main(self, images, original, radius, strength, contrast_limit=0.015, limit_window=5,
             skin_texture=0.0, skin_grain=0.0):
        import comfy.utils
        if strength == 0 and contrast_limit >= 1 and skin_texture == 0 and skin_grain == 0:
            return (images,)
        pbar = comfy.utils.ProgressBar(images.shape[0])
        with torch.no_grad():
            return (match_tone(images, original, radius, strength, contrast_limit, limit_window,
                               skin_texture, skin_grain, pbar),)


NODE_CLASS_MAPPINGS = {"TemporalDetailStabilizer": TemporalDetailStabilizer, "MatchToneToOriginal": MatchToneToOriginal}
NODE_DISPLAY_NAME_MAPPINGS = {"TemporalDetailStabilizer": "Temporal Detail Stabilizer (anti-flicker)",
                              "MatchToneToOriginal": "Match Tone to Original (no extra contrast)"}
