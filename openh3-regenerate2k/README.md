# OpenH3 Regenerate2K — bộ nạp workflow gốc

Gói này cài **phụ thuộc + tài liệu hướng dẫn**, dùng đúng file bạn gửi: **OpenH3_Regenerate2K Final.json**. Chỉ có một workflow; JSON giữ nguyên từng byte, không sửa prompt/setting/model/dây nối/bố cục và không cập nhật skill.

## Cài và dùng

1. Giải nén ZIP, đóng ComfyUI/backend rồi nhấp **CAI_DAT.bat**.
2. Nếu hộp chọn hiện ra, chọn **THƯ MỤC chứa `ComfyUI` và `python_embeded`**. Đường dẫn mặc định: `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`.
3. Nếu script báo thiếu native upscale/direct-buffer VAE, dùng updater chính thức `update/update_comfyui.bat` trong Portable, mở kiểm tra rồi cài lại. Bộ nạp không tự đổi core/Torch/driver. Cần Python 3.12+.
4. Sau cài, mở lại ComfyUI, chạy **KIEM_TRA.bat**. Trong Workflow Browser mở **OpenH3_Original / OpenH3_Regenerate2K Final**, hoặc kéo JSON trong `workflows` lên canvas.
5. Chọn **video MP4 thật tại Load Video #1**, đặt **width/height tại Upscale Latent #6**, rồi Run. File gốc lưu 2560×1440; clip dọc cần chọn kích thước dọc phù hợp bằng UI.

[Đọc hướng dẫn tiếng Việt có ảnh](docs/HUONG_DAN.pdf) · [Bản HTML](docs/HUONG_DAN.html) · [Word](docs/HUONG_DAN.docx) · [Markdown](docs/HUONG_DAN.md)

## Đầu vào là video đã render

Workflow này nâng/refine **clip có sẵn**. Trong dự án storyboard, tạo và duyệt clip ở workflow H3 tạo video trước, sau đó đưa MP4 vào đây. Prompt gốc giữ yêu cầu bảo toàn nội dung/style; audio cuối lấy từ nguồn. Không có TTS, node character sheet hoặc bộ sinh video trực tiếp từ storyboard trong graph này.

Thời lượng bám clip nguồn. `max_frames=0` tắt cap; cap dương từ chối clip dài hơn, không cắt đầu clip. Để lấy đoạn, xuất một MP4 riêng trước. Kết quả ở `ComfyUI/output/OpenH3_2K`.

## Model, node và file gốc

Cần **7 model (~54,45 GB nếu chưa có)** và **4 pack node**. Xem `manifest.json` cho size/SHA256/revision. File đúng hash có sẵn được dùng lại, cả qua extra_model_paths.yaml; script tạo alias/hardlink đúng tên gốc khi cần, không đổi JSON. Có resume `.part`. File có sẵn sai hash không bị ghi đè.

- Songssx/ComfyUI-OpenH3-Regenerate2K — commit adf6af3…
- TensorAlchemist/ComfyUI-OpenH3-VideoTools — **v0.1.11**
- kijai/ComfyUI-KJNodes — commit e8e88f7…
- Kosinkadink/ComfyUI-VideoHelperSuite — commit 4d907be…

`CAI_LAI_NODE.bat` chỉ cài/cài lại node. Thư mục node/workflow khác nội dung được backup ra `ComfyUI/user/OpenH3_Original/backups` trước thay thế. Các workflow khác dùng chung pack có thể chịu ảnh hưởng khi thay phiên bản; giữ backup để khôi phục. Log trong `logs/` của bộ nạp. `KIEM_TRA.bat` kiểm tra schema thật ở localhost:8188, model enum và SHA256 bản sao JSON; không queue GPU. Dùng `--port` nếu ComfyUI chạy cổng khác.

SHA256 JSON gốc:
`77801992727a09a22547b44f0b70b985e9472820da2e21941a87cf778d8e5973`

## Kiểm thử

Đã qua 23 unit test, nạp UI không node lạ, native schema validation có output lưu #26, CPU media preparation/audio/padding và smoke test bộ cài trên Portable giả lập. Bảy URL model trả prefix safetensors hợp lệ. [Bằng chứng](reports/VALIDATION.md).

**Chưa kiểm thử Windows thật hoặc render GPU trên RTX 4060 Ti.** Video tác giả dùng RTX 5060 Laptop Blackwell 8 GB, khác kiến trúc máy bạn; không suy ra tốc độ chỉ từ VRAM. Giữ cấu hình gốc theo yêu cầu, thử clip ngắn trước. Mọi giấy phép bên thứ ba giữ theo upstream; xem [nguồn](SOURCES.md).
