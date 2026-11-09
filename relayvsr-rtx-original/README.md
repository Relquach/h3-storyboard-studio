# RelayVSR + RTX VFX · Bộ cài bản gốc

Windows ComfyUI Portable · v1.0.0. Chỉ một workflow: `RealVSR-RTX_VFX - upscale.json`.
**JSON gốc giữ nguyên từng byte. Skill không thay đổi.**

## Cài nhanh

1. Giải nén cả ZIP và đóng ComfyUI/backend.
2. Nhấp đúp **CAI_DAT.bat**. Mặc định dùng `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`.
3. Nếu hỏi đường dẫn, chọn **thư mục chứa ComfyUI và python_embeded**, không chọn JSON.
4. Mở lại ComfyUI, chờ nạp node rồi chạy **KIEM_TRA.bat**.
5. Mở workflow trong `RelayVSR_RTX_Original` ở Workflow Browser.

**Trước khi tải:** NVIDIA VFX Nodes 0.2.1 yêu cầu PyTorch CUDA 13.0+, CUDA hoạt động và Windows x64. Bộ cài không tự nâng Torch/driver. Trình cài DLSS upstream có thông báo giấy phép `Continue? [y/N]`; chỉ nhập y khi bạn đồng ý. Không tự chấp nhận. Nếu chưa cài runtime, dùng CAI_RUNTIME_DLSS.bat sau.

**Đầu vào:** đường dẫn MP4 thật ở #10. Cap gốc 151 frame, không tự chạy hết clip dài. File cuối ở ComfyUI/output/vsr_upscale/; preview #27/#30 không có tiếng. Pipeline gốc bật TrueHDR nhưng exporter H.264/yuv420p chưa cấu hình HDR signaling chuẩn.

## File hướng dẫn

- [PDF có ảnh](docs/HUONG_DAN.pdf)
- [HTML đọc bằng trình duyệt](docs/HUONG_DAN.html)
- [Word](docs/HUONG_DAN.docx)
- [Markdown](docs/HUONG_DAN.md)
- [Nguồn và revision](SOURCES.md)
- [Kết quả và giới hạn kiểm tra](VALIDATION.md)

## Dung lượng và tính toàn vẹn

Hai model tổng 5,29 GB, thêm SDK khoảng 436 MB tải và DLSS runtime khoảng 467 MB ZIP; cần dư chỗ giải nén/output.

Model/node tải theo SHA256 và revision trong manifest; resume `.part`. Không ghi đè model đang có nhưng sai hash. Node cũ được backup ngoài custom_nodes khi cần thay (chỉ Relay). JSON đích khác nguồn được backup trước khi sao chép.

SHA256 workflow: `b7ab1d4a880bbec75c0b99957ee6db2b72636967cbc06ec58da2eef05366fa9e` · 32,359 byte.

**Chưa kiểm thử launcher Windows hoặc render GPU trên RTX 4060 Ti.** Các báo cáo CPU/schema/fixture không phải benchmark chất lượng hay bảo đảm chạy vừa bộ nhớ.
