# v5.1.0 · 14/11/2026

- Chặn prompt lẫn lệnh UI của workflow khác; tách file TXT model và Markdown thao tác.
- Sổ trạng thái hành động, pha start/continue/complete, kết quả giữ qua cut, không replay; trạng thái quan sát từ clip đã duyệt tách khỏi trạng thái mong muốn.
- Lịch thoại theo câu độc lập với cut, ID lượt lời, ngân sách thời gian, cách đọc tên/số, không tự lược hay nói lại.
- Tách duyệt thiết kế giọng với duyệt audio; khai báo phương án native/reference/external và giới hạn điều khiển giọng thực tế.
- Audit đọc được nhãn shot kiểu cũ; thêm kiểm hồi quy cho các lỗi trên.
- Không tạo câu chuyện, storyboard hoặc prompt phim mới; không sửa workflow.

# v5.0.0 · 13/11/2026

- Chuyển từ profile Apex mặc định sang nhận diện workflow thực tế; giữ tài liệu profile cũ như tham khảo có điều kiện.
- Đưa toàn bộ nguyên tắc cần cho AI khác vào một SKILL.md tự đủ.
- Bắt buộc đếm và giữ đủ ô/shot, cỡ cảnh, góc, diễn xuất; giải quyết nhãn thời gian chồng; không pha one-take vào storyboard nhiều cut.
- Hồ sơ giọng theo nhân vật, câu hỏi lần đầu, lưu/chuyển hồ sơ và áp giọng cho lượt thoại đúng người.
- Bổ sung đối chiếu prompt thực tế tại node/metadata render, không chỉ bản người dùng trích.
- Bộ hồ sơ mẫu trống và checker tùy chọn, không yêu cầu người dùng tạo project JSON để có prompt.
- Không sửa workflow, không tạo câu chuyện, storyboard hoặc prompt video mới cho ca riêng của người dùng.
