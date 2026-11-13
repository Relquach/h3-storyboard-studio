# Kiểm tra MiniMax H3 Film Skill 5.0.0 · 13/11/2026

- 33 kiểm tra logic thành công: bốn ô bị gộp còn hai shot; đủ nhãn nhưng thiếu góc/diễn biến; sai cỡ cảnh; nhãn giờ trùng, giờ nguồn bị đổi, khoảng hở/chồng, thiếu quyết định; Picture không tồn tại; grid vào first_frame; chưa duyệt hoặc đổi revision.
- Kiểm tra giọng pending cho cảnh im lặng/có thoại, thiếu mô tả giọng, thay thoại, người nói chưa biết, hai giọng giống nhau và hai giọng phân biệt.
- Kiểm tra đọc dây prompt, không giả suy output LLM từ input, so prompt mong đợi/metadata, chuẩn hóa newline.
- Đã thử resolve nguồn prompt từ metadata MP4 người dùng cung cấp bằng đọc dữ liệu; không queue/render. Video/ảnh/prompt/tên nhân vật riêng không được đưa vào gói skill.
- Đã đọc lại quy tắc chính trong một SKILL.md; cấu trúc JSON giọng trong file và template hợp lệ. File tham khảo/script chỉ tùy chọn.

Các test kiểm logic dựa trên dữ kiện khai báo, không chứng minh mọi AI tuân thủ, không đọc/đánh giá đúng pixel storyboard, không xác minh lời duyệt thật, không thử speaker lock, không nghe/đo giọng và không render GPU. Chưa thử một dịch vụ AI bên ngoài bằng tài sản của người dùng.

Không tạo câu chuyện, storyboard hoặc prompt video mới cho ca đang trao đổi.
