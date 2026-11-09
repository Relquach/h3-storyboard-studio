# 1.0.1 — sửa tải runtime DLSS

- Đổi URL runtime từ tag không tồn tại `3.0` sang tag chính thức `v3.0` bằng tùy chọn `--url` của script upstream. Không đổi source node/DLL hoặc JSON workflow.
- Đã kiểm tra link cũ HTTP404, link mới HTTP206 và chữ ký ZIP. Giữ lời nhắc xác nhận giấy phép, không dùng `--yes`.
- Người đã có model/node chỉ chạy CAI_RUNTIME_DLSS.bat từ gói mới; không tải lại model.
