# Hợp đồng trạng thái và audio v5.1

Đây là cấu trúc dữ liệu tùy chọn cho AI có công cụ kiểm. Người dùng không phải tự điền JSON hoặc chạy checker để được dùng skill. Quy tắc viết bằng lời vẫn nằm đầy đủ trong SKILL.md.

## Trạng thái hành động

- `initial_states`: bảng mã vật/nhân vật → thuộc tính ban đầu, lấy từ nội dung/ảnh được chốt.
- Trong từng `shots[]`, `actions` là danh sách sự kiện. Mỗi sự kiện có `event_id`, `phase` (`start`, `continue`, `complete`), `occurrences` (mặc định 1), `state_before`, `state_after`.
- `state_before/state_after`: bảng object_id → thuộc tính, chỉ rõ phần liên quan. Kết quả trước được giữ qua cut; trước hành động kế phải khớp trạng thái hiện có.
- Pha `complete` cần `completion_en` và `hold_en`; cả hai phải xuất hiện bằng câu tự nhiên trong block tương ứng của prompt. ID event chỉ phục vụ hồ sơ, không làm model tự hiểu thao tác.
- Sự kiện đã complete không được start/complete lại. Khi kịch bản chủ ý một sự kiện lặp nhiều lần, `occurrences>1` cần `repeat_approval` gồm `approved_by:"user"` và `evidence` từ yêu cầu thật. Không dùng dữ liệu test làm lời duyệt.
- Shot không có thao tác: `actions:[]` và `hold_states`; hoặc `camera_only:true` khi thực sự chỉ quan sát/camera. Không bịa một hành động để điền trường.
- Hành động cố ý còn tiếp ở clip sau: khai báo `carry_actions_to_next_clip`. `expected_final_states` là mục tiêu, chưa phải kết quả đã xem.
- Checker chỉ so khai báo; không chứng minh nét vẽ trong video đã xong, tay đã thả đồ hoặc chuyển động không bị lặp.

## Audio và giọng

- `audio.dialogue[]`: `utterance_id` duy nhất, `character_id`, `text` gốc, `start_s`, `end_s`, loại offscreen/in_scene. Một lượt có thể chạy qua nhiều cut; không nhân bản nó theo số shot.
- Nếu `spoken_text` khác `text`, cần `pronunciation_approval` ghi cách đọc đã chốt. Lặp câu có chủ ý cần `repeat_approval`. Nói đồng thời có chủ ý cần `audio.overlap_approval`.
- `timing_check`: `method` là `measured_audio` hoặc `estimate`, có `duration_s` và `basis`. Audio đo thật đáng tin hơn ước lượng. Đếm khoảng trắng tiếng Việt không phải đo phát âm; không tự cắt/tua tiếng nếu vượt slot.
- `characters[].voice.generation_mode`: `native_exploratory`, `audio_reference`, hoặc `external_voiceover`; kèm `delivery_choice_evidence` thực.
- `native_exploratory`: có thể thử khi chấp nhận biến thiên; không đánh dấu strict identity lock. Profile được người dùng duyệt không phải waveform được nghe duyệt.
- `audio_reference`: `reference_audio` cần `asset`, `connected:true`, `socket` thật. Chỉ có VAE decode không đáp ứng điều kiện này.
- `external_voiceover`: cần `delivery_plan` mô tả cách dùng cùng giọng/TTS/thu và ghép tiếng; không giả nhận workflow đã có node.
- `verification.status=accepted` cần audio thật và bằng chứng đánh giá. Checker không nghe tiếng, kiểm vùng giọng hoặc chứng thực người dùng đã duyệt.

## Prompt sạch

`video_prompt_en`/TXT không chứa code fence dòng đầu/cuối, lệnh bật-bypass, #node=value, lưu take hoặc câu “chỉ sao chép khối dưới”. Hướng dẫn đó thuộc COMFYUI_HANDOFF.md. Checker có chặn các mẫu UI phổ biến nhưng không phải bộ hiểu mọi cách diễn đạt tự nhiên.

Audit metadata chấp nhận nhận diện nhãn `[Shot N]` hoặc dòng cũ `00.0–01.5s | SHOT 001:` để đếm đúng ca render cũ. Handoff mới vẫn dùng cú pháp thống nhất trong SKILL.md để dễ kiểm; audit không được diễn giải “không nhận regex” thành “video không có shot”.
