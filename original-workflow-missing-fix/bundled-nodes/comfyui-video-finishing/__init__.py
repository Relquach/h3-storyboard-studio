"""Video Finishing: detail contrast + tone roll-off for decoded video frames.

Both steps run in one node so the video is copied in system RAM only once.
Frames are processed on the GPU a few at a time, so VRAM use stays small.
"""
import math

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
    """Separable gaussian blur of a [B,1,H,W] tensor."""
    h, w = x.shape[-2:]
    radius = max(1, min(int(math.ceil(sigma * 3)), h - 1, w - 1))
    t = torch.arange(-radius, radius + 1, device=x.device, dtype=x.dtype)
    k = torch.exp(-(t * t) / (2 * sigma * sigma))
    k = k / k.sum()
    x = F.conv2d(F.pad(x, (radius, radius, 0, 0), mode="reflect"), k.view(1, 1, 1, -1))
    return F.conv2d(F.pad(x, (0, 0, radius, radius), mode="reflect"), k.view(1, 1, -1, 1))


def _tone(lum, knee, white, lift):
    # Shadow lift: f(0) = lift, f(1) = 1, stays monotonic for lift < 0.5.
    if lift > 0:
        lum = lum + lift * (1 - lum) ** 2
    # Highlight roll-off: cubic Hermite shoulder from (knee, slope 1) to (1, white, slope 0.25).
    if knee < 1:
        d = 1 - knee
        t = ((lum - knee) / d).clamp(0, 1)
        t2, t3 = t * t, t * t * t
        shoulder = ((2 * t3 - 3 * t2 + 1) * knee + (t3 - 2 * t2 + t) * d
                    + (-2 * t3 + 3 * t2) * white + (t3 - t2) * d * 0.25)
        lum = torch.where(lum > knee, shoulder, lum)
    return lum


class VideoFinishDetailTone:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "detail_contrast": ("FLOAT", {"default": -0.20, "min": -1.0, "max": 1.0, "step": 0.01,
                    "tooltip": "Local contrast (clarity). Negative = softer, less crunchy texture. 0 = off."}),
                "detail_radius": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1,
                    "tooltip": "Size of the 'detail' in % of frame height. 1.0 = texture/skin, 3+ = bigger shapes."}),
                "highlight_knee": ("FLOAT", {"default": 0.70, "min": 0.30, "max": 1.0, "step": 0.01,
                    "tooltip": "Brightness where the roll-off starts. Lower = softer highlights. 1.0 = off."}),
                "white_level": ("FLOAT", {"default": 0.97, "min": 0.50, "max": 1.0, "step": 0.005,
                    "tooltip": "Where pure white ends up. 1.0 keeps full white, 0.95 is a gentle film roll-off."}),
                "shadow_lift": ("FLOAT", {"default": 0.02, "min": 0.0, "max": 0.20, "step": 0.005,
                    "tooltip": "Raises the blacks a little. 0 = off."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01,
                    "tooltip": "Mix with the original. 0 = no change."}),
                "frames_per_chunk": ("INT", {"default": 8, "min": 1, "max": 64,
                    "tooltip": "Frames sent to the GPU at once. Lower if VRAM is tight."}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "finish"
    CATEGORY = "image/postprocessing"
    DESCRIPTION = "Detail contrast + highlight roll-off for video frames, in one pass (one RAM copy)."

    def finish(self, images, detail_contrast, detail_radius, highlight_knee, white_level,
               shadow_lift, strength, frames_per_chunk):
        if strength == 0 or (detail_contrast == 0 and highlight_knee >= 1 and shadow_lift == 0):
            return (images,)

        device = _device()
        n, h = images.shape[0], images.shape[1]
        sigma = max(0.5, detail_radius / 100.0 * h)
        knee = min(highlight_knee, 1.0)
        # Keep the shoulder monotonic: white must stay well above the knee.
        white = max(white_level, knee + 0.4 * (1 - knee))
        luma = torch.tensor(LUMA, device=device, dtype=torch.float32)
        out = torch.empty_like(images)

        for i in range(0, n, frames_per_chunk):
            x = images[i:i + frames_per_chunk].to(device, dtype=torch.float32)
            lum = (x * luma).sum(-1)
            new = lum
            if detail_contrast != 0:
                blur = _gaussian_blur(lum.unsqueeze(1), sigma).squeeze(1)
                new = lum + detail_contrast * (lum - blur)
            new = _tone(new.clamp(0, 1), knee, white, shadow_lift)
            # Same brightness change on R, G and B keeps the hue.
            x = (x + strength * (new - lum).unsqueeze(-1)).clamp_(0, 1)
            out[i:i + frames_per_chunk] = x.to(out.device, dtype=out.dtype)

        return (out,)


NODE_CLASS_MAPPINGS = {"VideoFinishDetailTone": VideoFinishDetailTone}
NODE_DISPLAY_NAME_MAPPINGS = {"VideoFinishDetailTone": "Video Finishing (detail contrast + tone roll-off)"}
