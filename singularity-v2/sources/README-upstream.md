# MiniMax-H3 Turbo workflow + FlashVSR upscale: what to install

Two workflows:
1. **Finalworkflow_LowRes_detail.json**: makes the video (MiniMax-H3, 2 steps: draft, then upscale).
2. **FlashVSR v1.1 - Upscale H3 Video (natural + skin detail).json**: optional final polish.

Tested on: RTX 5070 Ti 16 GB, 24 GB RAM, **ComfyUI 0.43.1** (ComfyUI Desktop).
Free disk space needed: about **44 GB** for workflow 1, plus about **7 GB** for FlashVSR.

---

## 1. ComfyUI

Use **ComfyUI 0.43.1 or newer**. These nodes are built into ComfyUI, so you don't need
to install anything for them: MiniMax H3 nodes, BlockSparseAttention, ModelAttentionBackend,
Resolution Selector, Switch, Math Expression, Manual Sigmas, Color Transfer, Create/Save Video.
With an older ComfyUI they show up red. **Update ComfyUI first.**

## 2. Custom nodes

### From GitHub (install with ComfyUI Manager or `git clone` into `ComfyUI/custom_nodes`)

| Node pack | Used for | Link |
|---|---|---|
| PlagueKind Nodes | MMH3 Ultimate Upscale, latent upscale params, time chunks, tiles, H3 Upscale Size | https://github.com/PlagueKind/ComfyUI-PlagueKind-Nodes |
| VideoHelperSuite | Load Video (FFmpeg), Video Combine, Batch Manager (FlashVSR workflow) | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite |
| FlashVSR Ultra Fast | FlashVSR v1.1 upscaler (FlashVSR workflow) | https://github.com/lihaoyun6/ComfyUI-FlashVSR_Ultra_Fast |
| Pixaroma | Run timer + monitor (only shows info, not required) | https://github.com/pixaroma/ComfyUI-Pixaroma |

### Included in this folder (you can't download these anywhere else)

`custom_nodes_local.zip` has 3 small node packs. Unzip it into `ComfyUI/custom_nodes` so you get:

```
ComfyUI/custom_nodes/comfyui-h3-take/                      -> SAVE TAKE / LOAD TAKE (step 1 / step 2)
ComfyUI/custom_nodes/comfyui-video-finishing/              -> FINISHING + CLARITY
ComfyUI/custom_nodes/comfyui-temporal-detail-stabilizer/   -> Temporal Detail Stabilizer + Match Tone (FlashVSR)
```

The stabilizer needs OpenCV. If it doesn't load, run this in ComfyUI's Python: `pip install opencv-python`

### Audio-freeze patch (needed for pass 2 lip sync)

After installing PlagueKind Nodes, install Node.js (https://nodejs.org) and run this once:

```
node patch_h3_upscale_audio_freeze.js "<your ComfyUI>\custom_nodes\plaguekind-nodes\ComfyUI-H3-UltimateUpscale-LD\nodes.py"
```

Without it, the upscale pass makes new speech, and the lips move to audio you never hear.
It's safe to run twice. If it prints "Not patching", the node's code has changed since
this was made (tested on PlagueKind 1.5.5). The workflow still runs, only the lip-sync fix is missing.
Run it again after every PlagueKind update.

## 3. Models

Click a link to download the file directly. Put it in the folder shown and **keep the file name exactly as it is**.

### Workflow 1 (required)

| File | Size | Folder | Download |
|---|---|---|---|
| Minimax-h3_Singularity_ref2va_v2_pruned_int8.safetensors | 21.0 GB | `models/diffusion_models` | https://huggingface.co/WarmBloodAban/Minimax-h3_Singularity/resolve/main/Minimax-h3_Singularity_ref2va_v2_pruned_int8.safetensors |
| qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors | 15.7 GB | `models/text_encoders` | https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| minimax_h3_video_vae_fp16.safetensors | 5.2 GB | `models/vae` | https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors |
| minimax_h3_audio_vae_fp32.safetensors | 0.6 GB | `models/vae` | https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors |
| minimax_h3_ref2v_lightx2v_turbo_4step_v0.1_resized_avg_rank_20_bf16.safetensors | 307 MB | `models/loras` | https://huggingface.co/Kijai/MiniMax-H3_comfy/resolve/main/loras/minimax_h3_ref2v_lightx2v_turbo_4step_v0.1_resized_avg_rank_20_bf16.safetensors |
| h3-realism-people-t2v-i2v-r2v.safetensors | 131 MB | `models/loras` | https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA/resolve/main/h3-realism-people-t2v-i2v-r2v.safetensors |
| minimax_h3_latent_upscaler_3d_fp16.safetensors | 691 MB | `models/latent_upscale_models` | https://huggingface.co/PixelAlchemist123/Minimax_h3_latent_Upscaler/resolve/main/minimax_h3_latent_upscaler_3d_fp16.safetensors |

Latent upscaler mirror (same file, original repo, older commit):
https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/resolve/671ecf0f1d0a4dd0855f0cb6664bfb6f65c7e491/minimax_h3_latent_upscaler_3d_fp16.safetensors

### Workflow 1 (optional: these LoRA nodes are bypassed / purple)

| File | Size | Folder | Download |
|---|---|---|---|
| H3-Licon-VBVR-I2V.safetensors | 149 MB | `models/loras` | https://huggingface.co/LiconStudio/Minimax-H3-VBVR/resolve/main/H3-Licon-VBVR-I2V.safetensors |
| Motion_Repair_V2.safetensors | 155 MB | `models/loras` | https://huggingface.co/JOKER141/MiniMax-H3-General-Motion-Continuity-Repair/resolve/main/Motion_Repair_V2.safetensors |

### Workflow 2: FlashVSR v1.1 (about 7 GB)

Nothing to do: the FlashVSR node downloads it on the first run into `models/FlashVSR-v1.1`.
For a manual download, get every file from https://huggingface.co/JunhaoZhuang/FlashVSR-v1.1
and put them in `ComfyUI/models/FlashVSR-v1.1/`.

---

## Model pages (licenses + info)

- MiniMax-H3 (Comfy-Org): https://huggingface.co/Comfy-Org/MiniMax-H3 (MiniMax H3 Community License)
- Singularity V2: https://huggingface.co/WarmBloodAban/Minimax-h3_Singularity
- Turbo LoRA (original by LightX2V): https://huggingface.co/lightx2v/Minimax-h3-Turbo
- Realism People LoRA (fal): https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA
- H3 3D Latent Upscaler: https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler
- FlashVSR: https://huggingface.co/JunhaoZhuang/FlashVSR-v1.1

## How to use

The notes inside the workflow explain each step (STEP 1 = draft, STEP 2 = upscale the take you like).
