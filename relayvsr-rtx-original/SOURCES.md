# Nguồn và giấy phép

Workflow do người dùng tải lên: `RealVSR-RTX_VFX - upscale.json`. Giữ nguyên byte, không suy diễn quyền phân phối công khai. Gói được tải lên repository của người dùng theo yêu cầu công khai trên GitHub; giấy phép upstream vẫn áp dụng.

## Model

- https://huggingface.co/Comfy-Org/RelayVSR/blob/ba556c9fab83606eb82285b7eb3a9375232744b6/README.md
  File `diffusion_models/relayvsr_x2_lightx2v_int8_convrot.safetensors` · SHA256 `240e75e0c17cf2845d559b25254a230ff7458f81449d7a8c5e7e3fb8275c7b3c`.
- https://huggingface.co/Comfy-Org/RelayVSR/blob/ba556c9fab83606eb82285b7eb3a9375232744b6/README.md
  File `vae/relayvsr_flash_vae_x2_fp32.safetensors` · SHA256 `b5bb0339acb5b52545911ea29a51b4c5b805776a779222b5a14591571f42e21c`.

## Video và bài giới thiệu

- Video Drive được người dùng cung cấp: https://drive.google.com/file/d/1sb5rn5ViSAXh3Pirh4e1XXtOejxpn5Fu/view
- Khung minh họa trích video ở 04:10, 05:45 và 06:20. Không đóng gói lại video đầy đủ.
- Patreon: https://www.patreon.com/aifuturetech/posts/relayvsr-video-174673261 — nội dung đầy đủ yêu cầu quyền; không truy cập/bỏ qua giới hạn trả phí. Phân tích dựa JSON được gửi, video Drive được cấp và source công khai.

## Custom node cố định

- https://github.com/Blueforcer/ComfyUI-DLSS5-Enhancer · revision `9ca896aa6f85ecfedd0456da00ca165bd0c39cd0`
  Nguồn archive: https://codeload.github.com/Blueforcer/ComfyUI-DLSS5-Enhancer/zip/9ca896aa6f85ecfedd0456da00ca165bd0c39cd0
  SHA256 `0bd7c818951005667919f0a418909b791ab4af781cff6123ae4ddcda37eec339`. Source và LICENSE nếu upstream có được giữ trong `vendor/dlss.zip`.
- https://github.com/Comfy-Org/ComfyUI_Nvidia_VFX_Nodes · revision `0.2.1`
  Nguồn archive: https://cdn.comfy.org/comfyui/comfyui_nvidia_rtx_nodes/0.2.1/node.zip
  SHA256 `7bf843330b82086a1a64b01332a51897f0ddf1c14f7a6e4debcd5b6140a4c440`. Source và LICENSE nếu upstream có được giữ trong `vendor/nvidia.zip`.
- https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite · revision `449839959f0153fb8a57211a9364c55163935ca9`
  Nguồn archive: https://codeload.github.com/Kosinkadink/ComfyUI-VideoHelperSuite/zip/449839959f0153fb8a57211a9364c55163935ca9
  SHA256 `ba810634da69ed09491781ebf607e12f8d450a355936ecf2e69dcf285c9440a6`. Source và LICENSE nếu upstream có được giữ trong `vendor/vhs.zip`.

## Runtime không phân phối lại

- NVIDIA VFX SDK0.2.0.0: https://pypi.nvidia.com/nvidia-vfx/ — wheel Windows có URL/hash trong manifest; không dùng wheel-stub PyPI làm binary.
- DLSS5 upstream: https://github.com/Blueforcer/ComfyUI-DLSS5-Enhancer/blob/9ca896aa6f85ecfedd0456da00ca165bd0c39cd0/install_runtime.py
- Runtime nguồn: https://github.com/Merserk/dlss5-visual-enhancer/releases/tag/3.0
- Runtime gồm các thành phần có điều khoản NVIDIA/ReShade/RenoDX riêng. Script upstream tự hiển thị NOTICE và xin xác nhận; không truyền --yes. Không có binary SDK/DLSS trong gói này.
- README upstream NVIDIA VFX yêu cầu cu130+ và RTX40+ cho frame generation. DLSS5 worker trong tích hợp cộng đồng cần Windows/D3D12; khả năng chạy trên máy đích chưa được kiểm chứng.
