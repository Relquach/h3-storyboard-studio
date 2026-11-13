> Tham khảo profile cụ thể từ gói trước. Chỉ áp dụng khi workflow/task/checkpoint thực tế khớp. Các quy tắc duyệt, 1 ô–1 shot, giọng và kiểm prompt của SKILL.md v5 luôn áp dụng; không suy ra đây là profile mặc định.

# FastH3 và I2V: kiểm tra trước khi viết prompt

Bản công khai không kèm JSON, video hoặc frame của người dùng. Đọc workflow trong chính cuộc trò chuyện để lấy node ID và setting; không giả định hai graph dùng cùng ID.

## Khả năng checkpoint

Đối chiếu ngày 09/11/2026:

- https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2
- https://huggingface.co/FastVideo/FastVideo-FastH3-Comfy

Model card chính thức ghi: “This checkpoint supports text-to-audio-video generation. FL2VA and Ref2VA were not distilled.” Cổng ảnh trong node không chứng minh checkpoint đã được distill cho I2V. Nếu note template nói có FL2VA, nêu mâu thuẫn và ưu tiên phạm vi công bố của checkpoint. Model card ghi video shift=10 và VSA-H3; không lấy benchmark nhiều GPU của tác giả làm số đo cho RTX 4060 Ti.

## Đọc đường ảnh

`MiniMaxH3ImageToVideo` nhận `first_frame`/`last_frame`. Core dùng chúng làm keyframe đầu/cuối. Grid làm first_frame có thể giữ lưới trong video. Last_frame là kết thúc, không phải character sheet. Nhãn Picture trong chữ không tự tạo input ảnh.

`MiniMaxH3ReferenceToVideo` nhận reference images; chỉ profile này dùng nguyên storyboard + sheet như các reference đúng socket, cùng checkpoint hỗ trợ Ref2VA. Không đổi node sang Ref2V rồi giữ FastH3 như một cấu hình được bảo đảm.

## Đọc setting

Đọc widget ngoài group và các dây width/height; đừng dùng mặc định nội bộ hoặc số cũ hiển thị ở input được nối. Kiểm tra timeline prompt không vượt duration thật. Nếu công thức là 17n+5 tại 24 FPS: 5 giây → 124 frame ≈5.167 giây; 15 giây → 362 frame ≈15.083 giây.

Lịch 8 bước của checkpoint distill không cần thêm một Turbo LoRA khác. Sampling/attention phải theo tài liệu của chính model; không chỉnh ngẫu nhiên để chữa grid hoặc input ảnh chưa nối. Chỉ dùng hướng dẫn take/upscale khi graph thật sự có các node đó.

Nếu giữ I2V: chuẩn bị ảnh shot sạch, đúng trạng thái trước hành động, rồi đưa vào quy trình duyệt. Nếu giữ FastH3 V2: đánh dấu I2V là thử nghiệm ngoài phạm vi distillation. Muốn nguyên grid + sheet: đề xuất Ref2V với model có hỗ trợ.
