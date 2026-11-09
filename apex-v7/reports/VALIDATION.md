# Kiểm thử · 09/11/2026

- **28/28** unit test bộ cài/handoff: revision/SHA, dây, ảnh ảo, bước duyệt, timing, Portable root, path có model phụ, schema CreateVideo cũ/mới, ZIP traversal/symlink, backup/rollback/idempotence, resume/hash/HTML.
- **45/45** test skill: 34 hồi quy profile cũ và 11 kiểm tra Apex/approval/mapping.
- **6/6** UI/API: hai preset × (chỉ storyboard / đủ bốn ảnh / bỏ sheet ở giữa). Không node lạ; xuất API 44 node H3 hoặc70 node full khi mặc định.
- **6/6** native `execution.validate_prompt`: không node_errors; H3 output #7385 luôn có; preset full có thêm #9259. Không queue.
- **14/14** URL model trả HTTP206 và prefix header safetensors hợp lệ. URL/revision/SHA256 pinned trong manifest. Không tải toàn bộ93,7GB tại đây.
- **322/322** tên/shape tensor model H3 Upscaler3D khớp strict architecture node pinned; dùng header32.552byte và tensor meta, không suy luận.
- Smoke test script thật trong Portable giả lập: `h3`, `install`, chạy lại `install`, `check` đều exit0. Đường dẫn bộ cài có dấu/khoảng trắng; Python `-I`; bốn node pack và hai workflow xuất đúng. File model là fixture nhỏ có checksum riêng, không phải weights.
- JSON tác giả nguyên trạng có SHA256 đúng trong manifest.

Môi trường: Linux CPU, Python3.12, Torch2.10CPU, ComfyUI0.43.1, frontend1.57.4. Core test có enum fixture để validate schema; không có trọng số H3/LTX suy luận. KJ báo thiếu Triton cho PatchTritonVAE không dùng; các node KJ trong graph nạp được.

**Không có kiểm thử Windows thật/GPU4060Ti, benchmark tốc độ, peakRAM/VRAM, so sánh hình ảnh hoặc phát âm Việt.** Các kết quả trên không được hiểu là đã render thành công.
