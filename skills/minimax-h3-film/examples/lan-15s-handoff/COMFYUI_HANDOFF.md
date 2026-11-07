# Bàn giao EP01_RUN01_LAN

Đây là cấu hình cần áp dụng trên workflow gốc, chưa xác minh runtime máy người dùng.

Giây kế hoạch: 15; nguồn: 362 frame / 24 FPS ≈ 15.083 giây.

| Node | Thao tác | Picture |
|---|---|---|
| #27 | Nạp Ảnh storyboard Lan 2×2 đã tạo (tên đề xuất: lan-storyboard.png); bật | 1 |
| #28 | Nạp Sheet Lan áo dài trắng đã duyệt (tên đề xuất: lan-sheet.png); bật | 2 |
| #93 | Bypass (Ctrl+B) |  |
| #104 | Bypass (Ctrl+B) |  |
| #122 | Bypass (Ctrl+B) |  |
| #135 | Bypass (Ctrl+B) |  |
| #62 | true (nhánh Ref2V) | |
| #70 | Dán video_prompt.txt | |
| #23 | 15 | |
| #25 | 9:16 (Portrait Widescreen); multiple32; megapixels theo cấu hình hiện dùng | |
| #105 | false tạo nháp; true nâng take | |
| #124 | Chọn take đã duyệt; không mặc định latest đúng dự án | |
| #134 | Bypass Realism People; giữ Turbo #10 | |

Bước1: đặt #105=false, Queue, xem nháp; lưu tên take. Bước2: #105=true, #124 chọn take đó, Queue. Đổi ảnh/prompt cần tạo take mới.

Bỏ/đổi ảnh phải sinh lại prompt và bảng Picture. Helper không sửa workflow hoặc cài gì lên máy.
