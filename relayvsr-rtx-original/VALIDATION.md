# Kiểm tra · RelayVSR + RTX VFX

Ngày: 10/11/2026. Môi trường Linux CPU, Python 3.12, Torch 2.10 CPU. Không có GPU NVIDIA/Windows.

- JSON nguồn và bản sao byte-identical, SHA256 `b7ab1d4a880bbec75c0b99957ee6db2b72636967cbc06ec58da2eef05366fa9e`.
- 18 ca unit kiểm tra installer thành công: checksum, sai model được giữ, copy/backup workflow, model paths/hardlink và tải file cục bộ; thêm giải nén an toàn, node flat ZIP, idempotence, giữ DLSS runtime/config và không tự chấp nhận license.
- Hai lượt chạy subprocess Python -I của installer trên Portable giả lập đều thành công; dùng model rất nhỏ có sẵn và manifest fixture, không dùng model giả để tuyên bố suy luận thành công.
- URL model chính thức trả HTTP206, 16 byte đầu đúng cấu trúc safetensors. Không tải/verify toàn bộ weight nhiều GB tại môi trường này.
- Đã đăng ký 17/19 loại node thật trên core 0.44.0; kiểm schema DLSS/Relay và dây pipeline. Hai node NVIDIA được kiểm trường trong source nhưng không import được SDK vì thiếu CUDA driver (`libcuda.so.1`). Không tạo stub để vượt kiểm tra GPU.
- Chưa validate toàn bộ prompt gốc hoặc chạy DLSS worker Windows. Chế độ `--files-only` chỉ phục vụ kiểm tra file, không có nghĩa bộ cài hoàn chỉnh.
- Guide PDF8 trang, ảnh từ video người dùng đưa và sơ đồ suy từ JSON; đã kiểm tra bố cục và tiếng Việt.

## Những gì chưa được xác nhận

Chưa chạy BAT/PowerShell trên Windows; chưa render GPU, chưa benchmark thời gian/peak RAM/VRAM, chưa so chất lượng nhân vật CGI hoặc phát âm tiếng Việt. Đủ file/schema không bảo đảm chạy vừa RAM32GB/VRAM16GB hoặc không lỗi runtime.

Các kết quả máy đọc được ở reports/. Có thể chạy tests/test_installer.py bằng Python có PyYAML để kiểm lại phần cài, không cần model/GPU. Chạy CAI_DAT/KIEM_TRA trên Portable đích để kiểm môi trường thật.

## Sửa 1.0.1

Đã tái hiện HTTP404 của URL /3.0/; URL chính thức /v3.0/ trả HTTP206 và chữ ký ZIP. Metadata GitHub ghi asset 466.919.995 byte, SHA256 6f0590d81677484f4ecdfaa5c44fc2a0e1a3835d33eefc59d656e6c3bcf35f6a. Đây là hash từ nguồn, chưa tải toàn bộ 467 MB để tính lại. Đã kiểm tra hồi quy lời gọi --url đúng tag và vẫn không truyền --yes; 18 test installer và hai lượt subprocess isolated fixture qua. Chưa chạy DLSS D3D12 worker/GPU trên Windows.
