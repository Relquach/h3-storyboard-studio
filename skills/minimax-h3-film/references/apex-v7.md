> Tham khảo profile cụ thể từ gói trước. Chỉ áp dụng khi workflow/task/checkpoint thực tế khớp. Các quy tắc duyệt, 1 ô–1 shot, giọng và kiểm prompt của SKILL.md v5 luôn áp dụng; không suy ra đây là profile mặc định.

# Apex H3 V7 — hồ sơ workflow

Nguồn tác giả: https://www.patreon.com/ApexArtist/posts/apex-h3-v7-full-172914052

Bản nguyên gốc SHA256 `c49842b81d979d8f33931aac352a7d5674f275fcf9dd9d907af92ab37db038f1`: 53 node root, 71 dây, 3 subgraph. Có Qwen8B viết lại prompt, nhưng chỉ ảnh đầu nối vào H3 Ref2V. Bản Studio giữ file gốc trong source, không thay thế file riêng của người dùng.

## Những khác biệt có chủ đích

| Phần | Nguyên gốc | Studio 3D |
|---|---|---|
| Prompt | #138 → ghép thời lượng → Qwen/switch | #138 → #136 trực tiếp; bỏ group LLM và preview có thể buộc LLM chạy |
| Ảnh | 1 ảnh thực nối Ref2V | 4 socket nối thật; 3 ảnh phụ mặc định bypass |
| Phong cách | có RealismPeople; LTX phủ định cartoon | bỏ RealismPeople; LTX bảo toàn 3D Á Đông, không ép người thật |
| Tỷ lệ | 16:9 / 1920×1080 | 9:16 ở cả hai selector / 1080×1920 |
| Lượt đầu | 10 giây | 5 giây để thử; người dùng đổi #132 |
| Tiếng cuối | LTX tạo lại | H3 nền giữ tới #9259 |
| Upscaler3D | widget chunk/unload không khớp mã pinned | model conv_v1 BF16 có header 3D24 kênh; keep_proportion/device/precision khớp schema |
| CreateVideo | thiếu chroma_subsampling | giá trị auto rõ ràng, codec none hợp lệ cho VIDEO trung gian |
| WAS Number to String | cần để ghép duration | bỏ nhánh vì Codex đã đồng bộ duration, không cần WAS |

## Chặng 1 — nền nội dung và âm thanh

#127 Singularity Ref2VA v1.3 INT8 → attention #7344 → Spectrum #7134 → switch #141(false) → preview #7139 → sampler #125. Scheduler #124 simple, steps từ switch #142(false) lấy #14320. #123 res_multistep. Positive #136, seed #129, giây #132 qua #131. #122/#121 decode. #7347 chỉ preview.

Turbo nền không phải công tắc “nâng chất lượng”; bật #146 đồng thời đổi nhánh model và steps. Không bật cho preset đã đề xuất trước khi thử riêng.

Spectrum audio_blend=0, offline_smoothing_replay=true theo nguồn. Đây là thiết lập của thuật toán, không chứng nhận tiếng Việt. Khi thử Spectrum off, giữ seed/ảnh/steps để so sánh thực trên cùng máy.

## Chặng 2 — upscale latent H3 + refine

#145 DMAD0.8 → #9370 LMS0.5 → model input #7129. Refine không đi qua Spectrum của nền. Trong nhóm: #6924 upscale latent3D đến #7346 (.7MP, multiple32), #6921 ghép audio latent, #7033 guider, #9483 sigma `[.8,.6,.35,0]`, #7230 euler_ancestral, #6920 sampler, #6918 decode. Có thể repaint mặt/chi tiết và thay khẩu hình. #7385 lấy IMAGE output2 và First Pass Audio output4. Chưa chứng minh khóa danh tính.

Node pinned LBH-123-AI commit64fc9d... không có enable_temporal_chunking/force_unload; không hướng dẫn chỉnh các mục này như thể có sẵn. keep_proportion=false cho phép selector quyết định hai chiều như nguồn; ratio selector cùng 9:16, sai số do bội32 có thể gây crop nhẹ.

## Chặng 3 — LTX2.5 tùy chọn

#9258 dùng LTX2.5 distilled INT8, Gemma3 FP8 + text projection LTX2.3, VAE video/audio LTX2.5, spatial latent upscaler2×. beta2 bước, denoise0.2, euler, CFG1/1. Decode tiled512 overlap64, temporal64 overlap16; resize #9411 về1080×1920. Đầu ra1080p là kích thước file sau xử lý, không phải H3 sinh gốc1080p.

#9259 giữ audio H3 nền; VIDEO output trong nhóm là phụ, không phải file lưu chính. H3 frame17n+5 và LTX frame8n+1 khác nhau; đọc framecount MP4 thật khi ghép audio. Nếu cần giảm tải, dùng file 01 H3-only, không bypass ngẫu nhiên group rồi mất nối IMAGE/AUDIO.

## Kiểm tra bằng helper

`python scripts/apex_handoff.py workflow.json` chỉ đọc snapshot wiring, không bảo đảm API/node import/GPU. Có `--plan plan.json --output handoff.json` chỉ khi storyboard đã được user duyệt; không ghi đè file output có sẵn. Mẫu plan trong examples là pending, helper phải từ chối biên dịch.
