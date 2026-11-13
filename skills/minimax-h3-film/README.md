# MiniMax H3 Film Skill v5.0.0

**Để đưa cho AI khác dùng: gửi `SKILL.md` cùng yêu cầu của bạn.** Quy tắc bắt buộc nằm trọn trong file đó; không cần AI có cùng lịch sử chat hoặc chạy Python.

Nếu tiếp tục phim đã có, gửi thêm ảnh storyboard cuối, ảnh tham chiếu, workflow đúng bản đang dùng, `CHARACTERS.json` và `PROJECT_STATE.md` đã điền. Không gửi mẫu trống như hồ sơ đã duyệt. AI sẽ hỏi phần còn thiếu thay vì tự đặt lại giọng hoặc đoán dữ liệu từ tên file.

## Đã sửa

- Board N ô SHOT riêng → đúng N block shot, có vị trí ô và mô tả riêng; cấm tự tóm bốn shot thành hai.
- Giữ cỡ cảnh/góc/tư thế/biểu cảm từng ô; không chỉ có đủ nhãn Shot.
- Phát hiện timestamp trùng/chồng; cần quyết định rõ trước khi chốt video prompt.
- Cấm yêu cầu one-take/static toàn clip khi storyboard có nhiều cut khác góc.
- Hỏi giọng lần đầu theo từng nhân vật, lưu câu mô tả giọng cố định; lặp đúng cho người có lượt nói và chuyển hồ sơ sang AI khác.
- Chỉ có một prompt cuối; kiểm giá trị tại node hoặc metadata video để phát hiện bản đã bị rút gọn/thay trước render.
- Giữ quy trình storyboard trước → người dùng duyệt → prompt sau; không tự sáng tác khi chỉ được yêu cầu sửa skill.

## Trong ZIP

- `SKILL.md`: bản dùng riêng, đầy đủ quy tắc chính.
- `templates/`: hồ sơ nhân vật/giọng và trạng thái dự án trống.
- `references/`: cấu trúc bàn giao và một số chi tiết workflow có điều kiện.
- `scripts/validate_handoff.py`: kiểm cơ học một bản handoff đã khai báo, tùy chọn.
- `scripts/audit_render_prompt.py`: đối chiếu file prompt với metadata ComfyUI trong video; cần ffprobe, không render và không nghe âm thanh.
- `tests/` và `reports/`: kiểm logic; không phải thử khả năng tuân thủ của mọi AI hay chất lượng render GPU.

Script chỉ hỗ trợ Codex/AI có công cụ. Người dùng vẫn có thể dùng riêng SKILL.md. Không có storyboard, prompt sáng tác mới, giọng mẫu, video hay tài sản riêng của bạn trong ZIP này.
