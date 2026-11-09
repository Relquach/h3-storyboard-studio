# Nguồn và phiên bản

Đối chiếu ngày 09/11/2026. Gói dùng JSON công khai và metadata model/source; không kèm video nguồn hoặc trọng số model.

- Patreon: https://www.patreon.com/ApexArtist/posts/apex-h3-v7-full-172914052
- JSON đính kèm quan sát được: https://www.patreon.com/file?h=172914052&m=768121915
- Video tham khảo: https://drive.google.com/file/d/1OeIxm6WMkNaCLD8G8TKtWHPWdcWFdrNf/view
- Cinematic (tùy chọn, không bật/cài): https://civitai.com/models/2937713

SHA256 JSON gốc: `c49842b81d979d8f33931aac352a7d5674f275fcf9dd9d907af92ab37db038f1`

## Node source

- https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3/tree/24353c01ce6423a4dba3ddefcc4a53e0541ee875 — ZIP SHA256 `ca68080603c7d817e1539a8c2a91c4cabc2f78c4e396e09884ac110a4439e0a5`
- https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler/tree/64fc9d4c7e2c03e8c61d6886182e3309365a1962 — ZIP SHA256 `a74661aa6c9d85d5fc5b7ca7334d1e76d8c005f1a6fd2bd71559b167894e5ed2`
- https://github.com/kijai/ComfyUI-KJNodes/tree/ab72eda7ffad6280422d71ab7d54d3fb87c0ba18 — ZIP SHA256 `632b3ad45a67caf11e21d2c4c751caafb097d20a72ea2e6383545a628da7b9ef`
- https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite/tree/4d907bee61e92c2e65af3bd6383a4e4d356126d1 — ZIP SHA256 `5114977eefb133c76592a5213c45ad3caa1ad7b1c2e4a77905b5ff0c48ca4363`

Archive trong vendor chứa source/giấy phép của từng nhà phát triển. Preset giữ model và node architecture nguồn; mọi thay đổi Studio ghi trong CHANGELOG.

## Model source

- **h3**: https://huggingface.co/WarmBloodAban/Minimax-h3_Singularity/blob/1259cf16cd0b655ba691a32fb46a409142762972/Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors
  SHA256 `412a7b126595a958964193f3b42513d7cf2df4196ef04223a0f05e3622949cce`; 20967647456 byte.
- **h3_text**: https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors
  SHA256 `bc2ced0fbea64757fa9acddccfc0b3f4819d1dcf1da6c124d690d368be283923`; 27141342152 byte.
- **h3_vae**: https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/vae/minimax_h3_video_vae_int8_convrot.safetensors
  SHA256 `52a2c8c73583c86e4f41cdcce3a6ad0ea562987bc0bf3d60a0cef5f5c8e60c0e`; 2811065184 byte.
- **h3_audio**: https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/vae/minimax_h3_audio_vae_fp32.safetensors
  SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`; 605254808 byte.
- **dmad**: https://huggingface.co/Kijai/MiniMax-H3-experimental/blob/4e6da46acdd9e8cab79b061a0e76663c50f70ddc/loras/minimax_h3_DMAD_4step_full_lora_avg_rank_39_bf16.safetensors
  SHA256 `ddfdd94f4c9a0f32bf3649bb8e98ca20db572e4db6bcd9cca546a5b33ea32d11`; 366647000 byte.
- **lms**: https://huggingface.co/RunningHubAI/rh-minimax-h3-lms-v1.0-r64.safetensors-lora/blob/3bbd0b6cd60b676ac91d3a7b86a143fd0cde776f/minimax_h3_lms_v1.0_r64.safetensors
  SHA256 `16f3195bc6bffa431c0598dc2031e520ba058b4fcbc9f104db9e3fdfdeacf60c`; 1239664536 byte.
- **h3_up**: https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/blob/3f941d5d182014dd5c0a5e16330420ee2d4aa0c6/minimax_h3_latent_upscaler_3d_conv_v1/minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors
  SHA256 `4f57821f5837f32f7142b67d815606dbd7550f194e5c769f7d6c3f83b146a5e6`; 690592992 byte.
- **taeh3**: https://huggingface.co/Kijai/MiniMax-H3-TAE/blob/a213ac8bf2f148b4f32372279a7f207846978900/vae_approx/taeh3.safetensors
  SHA256 `f0f60fa072089997f817402098c2fd90777cb2660dd79cf5df42fc1e3e08e527`; 9791388 byte.
- **ltx**: https://huggingface.co/PulpCut/LTX-2.5-INT8-ConvRot-safetensors/blob/7597fb305b4cab9e7ff2c1d1e9551279c2932f0f/diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors
  SHA256 `b39322c2d03cb85509b148b19f602275a88df8f86be48f28e0c38ba2b25f2dfb`; 21504034388 byte.
- **ltx_vae**: https://huggingface.co/PulpCut/LTX-2.5-INT8-ConvRot-safetensors/blob/7597fb305b4cab9e7ff2c1d1e9551279c2932f0f/vae/ltx-2.5-video-vae-conv-bf16.safetensors
  SHA256 `685b06ee3d9b2039647698fc4ea33175112462fc374e2777312c907897dfce8d`; 1452269922 byte.
- **ltx_audio**: https://huggingface.co/PulpCut/LTX-2.5-INT8-ConvRot-safetensors/blob/7597fb305b4cab9e7ff2c1d1e9551279c2932f0f/vae/ltx-2.5-audio-vae-bf16.safetensors
  SHA256 `c52733d37f6a7fb7949c3dc0fb468c6cb2169e4d836983a73babb9f0d54837a5`; 364866540 byte.
- **gemma**: https://huggingface.co/DreamFast/gemma-3-12b-it-heretic-v2/blob/9cc4aa14f425ab38ddd25344a11c4d8af88ac35f/comfyui/gemma-3-12b-it-heretic-v2_fp8_e4m3fn.safetensors
  SHA256 `3e5f6cfb42cf11be02c606492739d36e6efe1052307e5f4a509a98ba52a67da9`; 13210205768 byte.
- **ltx_proj**: https://huggingface.co/Kijai/LTX2.3_comfy/blob/6d980fde0d330f2fed6ff8dfdfddb06d88a004e5/text_encoders/ltx-2.3_text_projection_bf16.safetensors
  SHA256 `911d59bb4cb7708179c9a0045ea0fe41212ecfb77aed3a02702b7c0a8274911f`; 2312149072 byte.
- **ltx_up**: https://huggingface.co/comfyicu/LTX-2.5/blob/1026e00f808dbd9601911479b22d65b760737dc8/latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors
  SHA256 `eb5a71fe4068ee87ccdb1c3aa635e547ca76bd2d30ae20ae889f2c325c0677e8`; 995778752 byte.

## Cinematic LoRA

Model2937713/version3325658, file3211433. Nguồn khuyên strength0,7 thông thường hoặc0,5 chuyển động nhanh, không dùng trigger DY. Không có trong JSON Apex đã tải và hướng người thật nên không mặc định cho style3D. URL tải đã trảHTML/403 khi thử; nếu cần, tải từ Civitai bằng quyền truy cập hợp lệ và kiểm tra checksum trong manifest. Không có HTML giả weights trong gói.

## Giới hạn kiểm tra

URL probe đọc16byte đầu; model upscale đọc header32552byte và so đủ322tensor bằng Torch/meta. Đây không phải tải toàn bộ trọng số hoặc render. Các nhận xét tốc độ của tác giả chưa được đo lại trên máy người dùng.
