# MiniMax H3 Film v4 · Apex V7

Cho Codex đọc `SKILL.md`, gửi nội dung Việt và ảnh nhân vật/môi trường nếu có. Codex tạo storyboard để bạn duyệt, sau đó mới viết prompt video + bảng nạp ảnh/setting theo JSON đang dùng. Không yêu cầu Topview, không tự queue.

Đọc `references/apex-v7.md` cho preset trong gói. Các reference/script v3 giữ để phục vụ workflow cũ, không dùng ID cũ cho Apex. Helper Apex mới: `scripts/apex_handoff.py` (read-only).

Để cài vào Codex local: chép **nguyên thư mục minimax-h3-film** vào thư mục skills của cấu hình Codex bạn dùng (thường `%USERPROFILE%\.codex\skills`), sao lưu bản cũ cùng tên trước. Nếu chỉ dùng trong cuộc trò chuyện, đính kèm SKILL.md + reference Apex + JSON đang chạy. Không phải custom node của ComfyUI.
