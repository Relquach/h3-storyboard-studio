# Kiểm thử · 09/11/2026

- JSON đóng gói đúng 36.366 byte/SHA256 gốc; 27 node và 27 link. Sau copy/cài lại và UI test vẫn nguyên byte.
- **23/23 unit test** qua: original copy/hash, pin/archive integrity, path, tên model đúng widget, alias/hardlink/copy, giữ file sai, extra paths, core preflight, ZIP traversal/symlink, backup/rollback/idempotence, resume/hash/HTML.
- **UI:** nạp đúng JSON, không node lạ, xuất 21 API node. Giữ 2560×1440, 2 bước, sampler gốc, nguồn audio/FPS và dây actual_frame_count. Hai SaveLatent muted không được queue.
- **Native validation:** valid=true, node_errors rỗng và output #26 hợp lệ; không queue GPU.
- **CPU media:** nguồn kỹ thuật 1 giây 24 frame → 124 frame xử lý nội bộ, actual 24; audio 32 kHz stereo. source_scale 0.5 giảm kích thước; cap 12 từ chối thay vì cắt. Sigma 2 bước và audio noise mask 0 được kiểm tra thực.
- **7/7 URL model:** HTTP 206, prefix safetensors hợp lệ. Toàn bộ trọng số 54,45 GB không được tải trong môi trường này; khi cài thật phải kiểm tra đủ SHA256.
- **Smoke test:** chạy script thật `nodes`, `install`, cài lại `install`, `check` đều exit 0 trong Portable giả lập, đường dẫn có dấu/khoảng trắng, Python -I, model fixture nhỏ. Đúng một workflow nguyên byte, bốn node pack, alias upscaler hardlink đúng.

Môi trường: Linux CPU, Python 3.12, Torch 2.10 CPU, ComfyUI 0.44.0 commit fca60fe70e5b84c5c6b058263653d15cb3401e44, frontend 1.58.5 và comfy-kitchen 0.2.41. Enum model dùng fixture, không phải trọng số suy luận. KJ cảnh báo thiếu Triton cho PatchTritonVAE không dùng; các node mà workflow cần đã nạp.

**Chưa chạy Windows thật, render H3/vae bằng GPU 4060 Ti, đo peak RAM/VRAM, benchmark tốc độ/chất lượng hoặc xác nhận khóa mặt.** CPU chuẩn bị video và schema không thay cho một lượt render GPU hoàn chỉnh.
