# Nguồn, revision và giấy phép

Ngày đối chiếu: 09/11/2026. File workflow do người dùng cung cấp, được giữ nguyên. Video chỉ dùng tham khảo, không kèm trong gói.

- Video hướng dẫn: https://drive.google.com/file/d/1PRqGB9z5rjtHzSpAMiKHhPNhwtd8wdjm/view
- VideoTools release v0.1.11: https://github.com/TensorAlchemist/ComfyUI-OpenH3-VideoTools/releases/tag/v0.1.11
- OpenH3 project: https://nvlabs.github.io/Sana/Open-H3-Regenerate-2K/
- ComfyUI dùng kiểm tra: https://github.com/Comfy-Org/ComfyUI/tree/fca60fe70e5b84c5c6b058263653d15cb3401e44

## Source node

- https://github.com/Songssx/ComfyUI-OpenH3-Regenerate2K/tree/adf6af360d8f3cfaa473ef2ed254d7a787bfb169
  ZIP SHA256 `bb6977b2b1f676934cba515b5c3b5104b94fd201ad514f9680d278d58e124801`.
- https://github.com/kijai/ComfyUI-KJNodes/tree/e8e88f7c88e3f6205b122f5de87e69a09fbce5ac
  ZIP SHA256 `a07ee4454557012f4640fdf0c0c96ead1b960d2a07d02f10037f63b7e2a0339e`.
- https://github.com/TensorAlchemist/ComfyUI-OpenH3-VideoTools/tree/f737f50205fceb474742654ac05c6f3fb1c0fd52
  ZIP SHA256 `3f0cb6b6f7960a378a635521c0c5173f2c437f0067e73cf11633790072542d87`.
- https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/tree/4d907bee61e92c2e65af3bd6383a4e4d356126d1
  ZIP SHA256 `5114977eefb133c76592a5213c45ad3caa1ad7b1c2e4a77905b5ff0c48ca4363`.

Các ZIP trong vendor là source gốc, bao gồm LICENSE/notice đi kèm. VideoTools là GPL-3.0-only, giữ nguyên TensorAlchemist copyright và MIT upstream notice. Node/model khác giữ giấy phép riêng; bộ nạp không phân phối trọng số.

## Model

- **Minimax-h3_Singularity_ref2va_v2_pruned_int8.safetensors**: https://huggingface.co/WarmBloodAban/Minimax-h3_Singularity/blob/1259cf16cd0b655ba691a32fb46a409142762972/Minimax-h3_Singularity_ref2va_v2_pruned_int8.safetensors
  20967647456byte; SHA256 `d7637c2c35cd30facd9e93778c491f6d82f91c4a441aecbdb4c384a62a5f3d9f`.
- **qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors**: https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
  15687142551byte; SHA256 `35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6`.
- **minimax_h3_video_vae_int8_convrot.safetensors**: https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/vae/minimax_h3_video_vae_int8_convrot.safetensors
  2811065184byte; SHA256 `52a2c8c73583c86e4f41cdcce3a6ad0ea562987bc0bf3d60a0cef5f5c8e60c0e`.
- **minimax_h3_audio_vae_fp32.safetensors**: https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/vae/minimax_h3_audio_vae_fp32.safetensors
  605254808byte; SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`.
- **minimax_h3_latent_upscaler_3d_bf16.safetensors**: https://huggingface.co/Efficient-Large-Model/Open-H3-Regenerate-2K/blob/5809c33730c18b6b1c827b40974855a4288641b3/latent_upsampler/minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors
  690592992byte; SHA256 `4f57821f5837f32f7142b67d815606dbd7550f194e5c769f7d6c3f83b146a5e6`.
- **open_h3_regenerate_2k_lora.safetensors**: https://huggingface.co/Efficient-Large-Model/Open-H3-Regenerate-2K/blob/5809c33730c18b6b1c827b40974855a4288641b3/lora/open_h3_regenerate_2k_lora.safetensors
  12452449080byte; SHA256 `8e36a0912ab72f7f3b00f41e3c7c97c7dfdec21e66c88ab22f08b9b0c681bb04`.
- **sharp_curve_branches.safetensors**: https://huggingface.co/Efficient-Large-Model/Open-H3-Regenerate-2K/blob/5809c33730c18b6b1c827b40974855a4288641b3/lora/sharp_curve_branches.safetensors
  1238746768byte; SHA256 `26ff1c4ea50fc5b0cea252912b67ec308a65d534cef026ef56f415ae92102e4e`.

## Nhận xét phần cứng có nguồn

Trong video khoảng07:12–07:35, tác giả hiển thị RTX 5060 Laptop Blackwell 8 GB, RAM 32 GB và môi trường Python 3.12/CUDA 13.2/PyTorch 2.14.dev. Đây là máy của tác giả, không phải kết quả của chúng tôi trên 4060 Ti.

Core kiểm tra chọn native/emulated quant formats theo khả năng thiết bị: comfy/ops.py, get_disabled_quant_formats và pick_operations. NVFP4 hardware matmul cần Blackwell; fallback/emulated có thể thay chi phí tính toán/bộ nhớ. Không tự thay encoder gốc hoặc cài Torch dev theo video.

Nguồn video được đối chiếu bằng frame và ASR tham khảo, không coi ASR là bản chép hoàn hảo. Setting/schema và JSON thực có ưu tiên khi khác lời trình bày.
