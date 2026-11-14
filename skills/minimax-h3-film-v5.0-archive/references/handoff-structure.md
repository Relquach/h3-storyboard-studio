# Hồ sơ tùy chọn cho kiểm cơ học

AI có thể gọi `python scripts/validate_handoff.py handoff.json` trước khi bàn giao. Không bắt người dùng tự điền/chạy để được nhận prompt. Không cần JSON nếu AI chỉ có khả năng đọc SKILL.md; vẫn phải tự kiểm đầy đủ.

Cấu trúc khai báo:

- `storyboard_revision`; `storyboard_review` gồm `status`, `approved_by`, `approved_revision`, `evidence` lấy từ lời người dùng thực.
- `seconds`, `workflow_mode` (`ref2v` hoặc `i2v`), `editing_mode` (`cuts` cho nhiều shot có cut).
- `panels`: mỗi ô có `id`, `row`, `column`, `empty`; `source_interval: [start,end]` nếu caption ảnh có giờ, không sửa/che giờ gốc để lách kiểm tra.
- `shots`: mỗi shot có `id`, `panel_id`, `start_s`, `end_s`, `panel_anchor_en`, `camera_size_en`, `camera_angle_en`, `start_state_en`, `action_en`, `end_state_en`, `transition_en` (từ shot thứ hai).
- `timing_resolution`: khi caption gốc chồng/trùng, `authority` là `explicit_user_approval` hoặc `user_delegated_timing`, kèm `evidence` có thật. Không dùng dữ liệu mẫu làm lời duyệt.
- `assets`: mỗi ảnh có `picture`, `role`, `active`, `connected`, file/URI thật; I2V thêm `socket` để tránh grid/sheet vào first_frame.
- `characters`: mỗi nhân vật có `character_id`, `name`, `voice` theo hồ sơ trong SKILL.md. Hồ sơ trong CHARACTERS.json có thể được ghép vào đây để kiểm, không tạo hai bản giọng mâu thuẫn.
- `audio.dialogue`: mỗi lượt có `character_id`, `text`, `start_s`, `end_s`, loại nói trong cảnh/voice-over.
- `video_prompt_en`: một prompt cuối duy nhất. Mỗi block theo cú pháp `[Shot N] [START-ENDs]`, mô tả đầy đủ ở bên dưới.

Checker không mở ảnh, không nghe tiếng, không kiểm nhân vật được mô tả đúng hay bằng chứng duyệt có thật. Nó đối chiếu các khai báo để chặn lỗi cơ học (mất shot, bỏ dữ kiện, lệch thời gian, giọng chưa chốt, Picture ảo). Một chuỗi từ khóa hợp checker chưa chứng minh prompt tốt hoặc model sẽ làm đúng.

Nếu gộp/tách shot do người dùng chốt, lưu `shot_alteration_review.approved_by="user"` và `evidence`; hồ sơ vẫn phải tham chiếu các panel có thật. Các sửa này không được tự suy ra từ chữ “tối ưu”.
