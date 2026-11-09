# Nguồn và giấy phép

Workflow do người dùng tải lên: `video_fasth3_ominiref_r2v.json`. Giữ nguyên byte, không suy diễn quyền phân phối công khai. Gói được tải lên repository của người dùng theo yêu cầu công khai trên GitHub; giấy phép upstream vẫn áp dụng.

## Model

- https://huggingface.co/FastVideo/FastH3-Omni-Comfy/blob/82eff2a6eee6c962846879f4bab52610a4df24d3/README.md
  File `diffusion_models/fasth3_omniref_8step_pruned_int8_convrot.safetensors` · SHA256 `851b2dc9670ed864b7f1e951ac9da047d83b1c04ded9bfcc1a9e5bba0ee33f80`.
- https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/README.md
  File `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` · SHA256 `35a88d51044231fe332301d7a62aa81e3f2cba62febeb446e2c1e3e0ef76f2c6`.
- https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/README.md
  File `vae/minimax_h3_video_vae_int8_convrot.safetensors` · SHA256 `52a2c8c73583c86e4f41cdcce3a6ad0ea562987bc0bf3d60a0cef5f5c8e60c0e`.
- https://huggingface.co/Comfy-Org/MiniMax-H3/blob/54472221d27c695fca9621b0c3ed52f06c4af707/README.md
  File `vae/minimax_h3_audio_vae_fp32.safetensors` · SHA256 `8e505d95dd1561d47abd43d4238fd40d9bb1ae9e147ed0a4cba778d76ae4db48`.

## Core tham chiếu kiểm tra

- https://github.com/Comfy-Org/ComfyUI/tree/086099f5d8886163ef77dc354f8382cb7431582a (0.43.1)
- https://github.com/Comfy-Org/ComfyUI/tree/fca60fe70e5b84c5c6b058263653d15cb3401e44 (0.44.0)
- Không phân phối hoặc patch core. Không phân phối model weights; tải từ Hugging Face khi cài. Giấy phép model thuộc từng repository upstream.
