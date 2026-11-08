# MiniMax H3 Film Skill v3.0.0

Bản công khai của skill v3, có kiểm tra task/model và bước duyệt storyboard bắt buộc. Không phân phối JSON riêng, video, frame, thoại hoặc báo cáo dự án của người dùng. Gói skill, không phải bộ cài hoặc workflow mới.

**Điểm quan trọng:** graph mới là I2V, nguyên storyboard đang làm first_frame; prompt gọi Picture2 chưa nối; duration thực 5 giây nhưng prompt dài 15 giây. Ngoài ra model card FastH3 V2 chỉ công bố T2AV, FL2VA/Ref2VA chưa distill. Skill v3 chặn các lỗi này trước khi nhận prompt sẵn sàng.

## Quy trình sáng tác bắt buộc

**Tạo storyboard → người dùng duyệt → từ bản đã duyệt và nội dung phim mới tạo prompt video.** Có sửa ảnh thì gửi bản mới để duyệt; chưa được duyệt thì không xuất prompt video. Skill giữ trạng thái nội bộ, người dùng chỉ cần xem ảnh và phản hồi. Đọc `references/storyboard-approval.md`.

## Sử dụng

Đưa cả thư mục `minimax-h3-film` vào nơi Codex đọc skill hoặc gửi cả gói vào dự án. Đừng chỉ chép SKILL.md mà bỏ các reference. Có thể yêu cầu:

> Dùng skill minimax-h3-film v3. Đọc workflow tôi gửi trước, xác nhận task và checkpoint. Dùng style 3D bán hiện thực Á Đông, pha nét búp bê. Tạo storyboard theo nội dung, tự chọn số ô và nhịp; gửi tôi duyệt trước. Sau khi tôi duyệt mới tạo prompt video từ bản đó và nội dung phim. Nếu workflow nhận first_frame, chuẩn bị ảnh shot sạch, báo rõ model có hỗ trợ I2V không. Nếu tôi yêu cầu nguyên grid + sheet, chỉ dùng profile Ref2V đã xác minh. Không gọi ảnh chưa nối hoặc để timeline vượt duration.

- `SKILL.md`: quy tắc chính, nhận diện task/model trước nội dung.
- `references/fastvideo-fasth3-i2v.md`: bảng node và setting thật của JSON mới.
- `references/workflow-mode-routing.md`: chọn Ref2V/I2V, giới hạn FastH3.
- `references/i2v-authoring.md`: ảnh đầu/trạng thái/cuối, prompt và dựng.
- `references/original-workflow.json` và ví dụ Lan cũ: giữ cho profile Singularity Ref2V, không áp node đó vào FastH3.

## Hai đường phù hợp

**Muốn nguyên storyboard + sheet → video:** dùng workflow Ref2V có model hỗ trợ, như Singularity cũ. Không sửa prompt để giả FastH3 là Ref2V. Cần xem nháp để kiểm tra mức bám shot.

**Giữ nguyên FastH3 đang dùng:** thử ảnh sạch từng shot và prompt đúng thời lượng. Chỉ là I2V ngoài phạm vi distillation công bố; chưa thể gọi pipeline sản xuất đã kiểm chứng. Nếu cần I2V ổn định, phải chọn model có hỗ trợ I2V cùng lịch phù hợp trước.

Skill không tự sửa JSON, đổi model, cài node, render hoặc đăng tài sản lên mạng. Không có benchmark RTX 4060 Ti hoặc cam kết giữ mặt tuyệt đối.

## Công cụ của Codex, không bắt người dùng chạy

`python scripts/audit_workflow.py --workflow /duong/dan/workflow-cua-ban.json --image-role storyboard_grid --out report.json`

Với video thực thêm `--video VIDEO.mp4`; cần ffprobe. Exit 2 nghĩa báo cáo tìm thấy vấn đề/chưa sẵn sàng, không phải tool bị hỏng. Exit 0 chỉ là kiểm tra tĩnh vượt qua; không chứng nhận ảnh/video đẹp.

Helper `compile_handoff.py` chỉ dùng với workflow Singularity gốc và chặn xuất prompt khi hồ sơ storyboard chưa có duyệt đúng revision. Ví dụ Lan trong gói cố ý ở trạng thái chờ duyệt, không có ảnh kèm theo. Kiểm tra tác giả: `python -m unittest discover -s tests -v`.
