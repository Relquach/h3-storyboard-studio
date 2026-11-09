# Kiểm tra · FastH3 OmniRef

Ngày: 10/11/2026. Môi trường Linux CPU, Python 3.12, Torch 2.10 CPU. Không có GPU NVIDIA/Windows.

- JSON nguồn và bản sao byte-identical, SHA256 `eb2d92ae93e151d4d86dc697c845e428e2b33ce4e845d1859f28654f4f64d0c7`.
- 11 ca unit kiểm tra installer thành công: checksum, sai model được giữ, copy/backup workflow, model paths/hardlink và tải file cục bộ; thêm cảnh báo schema CreateVideo.
- Hai lượt chạy subprocess Python -I của installer trên Portable giả lập đều thành công; dùng model rất nhỏ có sẵn và manifest fixture, không dùng model giả để tuyên bố suy luận thành công.
- URL model chính thức trả HTTP206, 16 byte đầu đúng cấu trúc safetensors. Không tải/verify toàn bộ weight nhiều GB tại môi trường này.
- Đã mở UI với core0.43.1 và0.44.0/frontend1.58.5; không có unknown node. Schema gốc hợp core0.43.1, không hợp core0.44.0 vì #130 chroma_subsampling=none. Đổi auto trong bộ nhớ UI thì hợp core0.44.0. Không lưu đè nguồn.
- Schema dùng model zero-byte để điền enum và ảnh màu kỹ thuật. Không nạp weight, không render. Chỉ kiểm API/wiring/validation, không đo chất lượng.
- Guide PDF7 trang có screenshot UI thật; đã kiểm tra bố cục và tiếng Việt.

## Những gì chưa được xác nhận

Chưa chạy BAT/PowerShell trên Windows; chưa render GPU, chưa benchmark thời gian/peak RAM/VRAM, chưa so chất lượng nhân vật CGI hoặc phát âm tiếng Việt. Đủ file/schema không bảo đảm chạy vừa RAM32GB/VRAM16GB hoặc không lỗi runtime.

Các kết quả máy đọc được ở reports/. Có thể chạy tests/test_installer.py bằng Python có PyYAML để kiểm lại phần cài, không cần model/GPU. Chạy CAI_DAT/KIEM_TRA trên Portable đích để kiểm môi trường thật.
