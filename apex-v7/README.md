# Apex H3 V7 Studio · Windows Portable

Nội dung Việt → Codex tạo storyboard → bạn duyệt ảnh → Codex viết prompt Anh và bảng nạp ảnh → ComfyUI tạo video. Style mặc định: **3D bán hiện thực Á Đông, CGI beauty render, pha nét búp bê**, dọc 9:16.

## Chạy lần đầu

1. Giải nén và đóng ComfyUI.
2. **RTX 4060 Ti 16 GB / RAM 32 GB: nên chạy `CAI_DAT_H3_NHE.bat` trước.** Tải tối đa khoảng 53,8 GB nếu chưa có model.
3. Muốn đủ ba chặng H3 + LTX 1080p: chạy `CAI_DAT.bat`, tối đa khoảng 93,7 GB. File đúng SHA256 đã có được dùng lại.
4. Đích mặc định: `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`. Nếu hộp chọn hiện ra, chọn **thư mục chứa `ComfyUI` và `python_embeded`**, không chọn JSON.
5. Mở lại ComfyUI, chạy `KIEM_TRA.bat`; mở `Apex_H3_V7_Studio/01_APEX_V7_3D_H3_2PASS_DOC` trong Workflow Browser, hoặc kéo JSON từ workflows lên canvas.
6. Chọn storyboard thật tại **#7330**, dán prompt đã duyệt tại **#138**, đặt giây tại **#132**. Bắt đầu 5 giây. Ảnh phụ mặc định bypass; chỉ bật sau khi chọn ảnh và đồng bộ số Picture với prompt.

Đọc **[hướng dẫn có ảnh](docs/HUONG_DAN.pdf)** hoặc [HTML](docs/HUONG_DAN.html). Bản DOCX và Markdown cũng có trong docs. Cho Codex đọc [skill v4](skill/minimax-h3-film/SKILL.md) trước khi sáng tác.

## Hai preset

| File | Pipeline | Dùng khi |
|---|---|---|
| 01_APEX_V7_3D_H3_2PASS_DOC.json | H3 nền 0,2 MP → upscale/refine 0,7 MP | Thử nội dung, danh tính, tiếng; nhẹ hơn |
| 02_APEX_V7_3D_LTX_1080_DOC.json | Hai chặng H3 → LTX 2.5 → 1080×1920 | Thử hoàn thiện sau khi H3 ổn |

JSON tác giả giữ nguyên trong `source/`. Preset Studio đã bỏ LLM viết lại prompt, thêm ba đường ảnh phụ có dây thật, chỉnh style 3D, giữ tiếng H3 nền ở file cuối và sửa widget không khớp schema. Xem [thay đổi](CHANGELOG.md).

## Bộ cài làm gì?

Cài bốn pack node từ source có revision/SHA256 cố định; tải model có resume và kiểm tra toàn bộ hash; tìm model cả trong extra_model_paths.yaml; sao lưu node/workflow bị thay thế ra `ComfyUI/user/ApexV7/backups`. Không tự nâng core, Torch, CUDA hay driver. Log trong `logs/`. `CAI_LAI_NODE.bat` chỉ bổ sung/cài lại node. Không cài FlashVSR, Pika, Taomate, Cinematic hoặc TTS vì chúng không nằm trên pipeline Studio này.

## Kiểm thử và giới hạn

Đã qua 28 unit test bộ cài/handoff, 45 test skill, sáu cấu hình UI/API/schema và kiểm tra prefix của 14 URL model. Script bộ cài đã chạy trong Portable giả lập với file test nhỏ; xem [bằng chứng](reports/VALIDATION.md).

**Chưa render GPU, chưa chạy Windows thật hoặc đo tốc độ/chất lượng trên 4060 Ti.** RAM 32 GB có thể thiếu hoặc offload/pagefile rất nhiều với các checkpoint lớn này. Bản hai chặng là điểm bắt đầu; không có bảo đảm một lần bấm là render được trên mọi bản Portable.
