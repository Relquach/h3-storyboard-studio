# Kiểm tra skill v5.1.0 · 14/11/2026

57 kiểm tra logic thành công (33 quy tắc v5 và 24 kiểm tra mới):

- Dán nhầm hướng dẫn node/bật-bypass/code fence vào prompt; nhận diện nhãn shot cũ mà không đếm lặp header.
- Hành động đã hoàn tất bị replay, reset trạng thái qua cut, start lại sự kiện đang chạy, thiếu trạng thái vào/ra, thiếu điều kiện hoàn tất/giữ trong prompt; pha kéo dài qua shot, hold và chuyển tiếp clip có chủ ý.
- Câu bị lặp/ID trùng theo shot, thoại vượt ngân sách, cách đọc bị đổi chưa chốt; mô tả giọng được duyệt bị nhầm thành khóa giọng, audio reference chưa nối, external audio chưa có kế hoạch, khai báo đã nghe duyệt thiếu bằng chứng.
- Giữ các kiểm tra số ô/shot, thứ tự/camera/timeline, duyệt/revision, Picture thật, giọng từng người và prompt metadata từ v5.

Đã kiểm riêng clip người dùng gửi: đọc metadata, xem frame mẫu và chạy ASR multilingual small trên CPU trong môi trường phân tích riêng. ASR chỉ gợi ý nội dung/thời gian lời, không chứng thực chữ chính xác, vùng giọng hoặc speaker identity. Không nghe/duyệt bằng người, không có storyboard ảnh gốc của clip để đối chiếu đầy đủ. Video, âm thanh, frame, metadata/prompt và nội dung thoại riêng không đưa vào gói skill.

Đã giải nén ZIP mới, kiểm checksum và chạy lại các test bằng Python isolated mode. Chưa chạy dịch vụ AI khác, không tạo clip/storyboard/prompt phim mới, không render GPU, không đo hiệu quả giảm lặp hoặc giữ giọng trên một lần render mới. Các test kiểm khai báo dữ liệu, không chứng minh mọi AI/model sẽ làm đúng.
