# MiniMax H3 Film Skill v5.1.0

**Để đưa cho AI khác dùng: gửi `SKILL.md` cùng yêu cầu của bạn.** Quy tắc bắt buộc nằm trọn trong file đó; không cần AI có cùng lịch sử chat hoặc chạy Python.

Nếu tiếp tục phim đã có, gửi thêm ảnh storyboard cuối, ảnh tham chiếu, workflow đúng bản đang dùng, `CHARACTERS.json` và `PROJECT_STATE.md` đã điền. Không gửi mẫu trống như hồ sơ đã duyệt. AI sẽ hỏi phần còn thiếu thay vì tự đặt lại giọng hoặc đoán dữ liệu từ tên file.

## Bổ sung v5.1

- Theo dõi trạng thái đạo cụ/tay và sự kiện hoàn tất qua cut; cấm reset/replay ngoài kịch bản, ghi điểm kết thúc và cách giữ sau hoàn tất.
- Lịch câu thoại độc lập với lịch shot, mỗi lượt lời chỉ có một bản; kiểm cách đọc tên/số và thời gian bằng audio hoặc ước lượng có căn cứ.
- Phân biệt mô tả giọng đã chốt với waveform đã nghe duyệt; chọn native thử/reference/TTS theo workflow thật, không hứa khóa giọng bằng chữ.
- Xuất video_prompt.txt sạch tách khỏi COMFYUI_HANDOFF.md, chặn lệnh node/bật-bypass/code fence bị dán nhầm vào model.

## Các quy tắc từ v5 được giữ

- Board N ô SHOT riêng → đúng N block shot, có vị trí ô và mô tả riêng; cấm tự tóm bốn shot thành hai.
- Giữ cỡ cảnh/góc/tư thế/biểu cảm từng ô; không chỉ có đủ nhãn Shot.
- Phát hiện timestamp trùng/chồng; cần quyết định rõ trước khi chốt video prompt.
- Cấm yêu cầu one-take/static toàn clip khi storyboard có nhiều cut khác góc.
- Hỏi giọng lần đầu theo từng nhân vật, lưu câu mô tả giọng cố định; lặp đúng cho người có lượt nói và chuyển hồ sơ sang AI khác.
- Chỉ có một prompt cuối; kiểm giá trị tại node hoặc metadata video để phát hiện bản đã bị rút gọn/thay trước render.
- Giữ quy trình storyboard trước → người dùng duyệt → prompt sau; không tự sáng tác khi chỉ được yêu cầu sửa skill.

## Trong ZIP

- `SKILL.md`: bản dùng riêng, đầy đủ quy tắc chính.
- `templates/`: hồ sơ nhân vật/giọng, trạng thái dự án, sổ thao tác và kế hoạch audio trống.
- `references/`: cấu trúc bàn giao và một số chi tiết workflow có điều kiện.
- `scripts/validate_handoff.py` + `production_checks.py`: kiểm cơ học shot, trạng thái, lời nói và prompt sạch, tùy chọn.
- `scripts/audit_render_prompt.py`: đối chiếu file prompt với metadata ComfyUI trong video; cần ffprobe, không render và không nghe âm thanh.
- `tests/` và `reports/`: kiểm logic; không phải thử khả năng tuân thủ của mọi AI hay chất lượng render GPU.

Script chỉ hỗ trợ Codex/AI có công cụ. Người dùng vẫn có thể dùng riêng SKILL.md. Không có storyboard, prompt sáng tác mới, giọng mẫu, video hay tài sản riêng của bạn trong ZIP này.
