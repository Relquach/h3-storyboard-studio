# FastH3 OmniRef · Bộ cài bản gốc

Windows ComfyUI Portable · v1.0.0. Chỉ một workflow: `video_fasth3_ominiref_r2v.json`.
**JSON gốc giữ nguyên từng byte. Skill không thay đổi.**

## Cài nhanh

1. Giải nén cả ZIP và đóng ComfyUI/backend.
2. Nhấp đúp **CAI_DAT.bat**. Mặc định dùng `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`.
3. Nếu hỏi đường dẫn, chọn **thư mục chứa ComfyUI và python_embeded**, không chọn JSON.
4. Mở lại ComfyUI, chờ nạp node rồi chạy **KIEM_TRA.bat**.
5. Mở workflow trong `FastH3_OmniRef_Original` ở Workflow Browser.

**Trước khi Run:** chọn hai ảnh thật ở #137 (storyboard/Picture 1) và #149 (character sheet/Picture 2), rồi dùng prompt đúng ảnh. Nếu Create Video #130 có chroma_subsampling, chọn auto. File nguồn vẫn giữ nguyên none; đây là khác biệt schema của core mới.

**Thiết lập gốc:** 16:9, 1 MP, khoảng 15 giây, euler/simple 8 bước. Tạo video và âm thanh; không có bước upscale. Không có ảnh nhân vật hay storyboard của bạn trong ZIP.

## File hướng dẫn

- [PDF có ảnh](docs/HUONG_DAN.pdf)
- [HTML đọc bằng trình duyệt](docs/HUONG_DAN.html)
- [Word](docs/HUONG_DAN.docx)
- [Markdown](docs/HUONG_DAN.md)
- [Nguồn và revision](SOURCES.md)
- [Kết quả và giới hạn kiểm tra](VALIDATION.md)

## Dung lượng và tính toàn vẹn

Bốn model tổng 41,32 GB. Dùng lại ba model H3 dùng chung đúng hash có thể chỉ còn tải OmniRef 22,21 GB. RTX 4060 Ti không có FP4 phần cứng Blackwell; chưa benchmark encoder NVFP4 AWQ gốc trên cấu hình của bạn.

Model/node tải theo SHA256 và revision trong manifest; resume `.part`. Không ghi đè model đang có nhưng sai hash. Node cũ được backup ngoài custom_nodes khi cần thay (chỉ Relay). JSON đích khác nguồn được backup trước khi sao chép.

SHA256 workflow: `eb2d92ae93e151d4d86dc697c845e428e2b33ce4e845d1859f28654f4f64d0c7` · 41,549 byte.

**Chưa kiểm thử launcher Windows hoặc render GPU trên RTX 4060 Ti.** Các báo cáo CPU/schema/fixture không phải benchmark chất lượng hay bảo đảm chạy vừa bộ nhớ.
