> Tham khảo profile cụ thể từ gói trước. Chỉ áp dụng khi workflow/task/checkpoint thực tế khớp. Các quy tắc duyệt, 1 ô–1 shot, giọng và kiểm prompt của SKILL.md v5 luôn áp dụng; không suy ra đây là profile mặc định.

# Storyboard là bản kế hoạch; ảnh I2V là trạng thái đầu

## Chuẩn bị tài sản

Tạo master storyboard có SHOT labels để duyệt. Với I2V, xuất thêm từng ảnh mở đầu sạch từ cùng sheet và thiết kế đã duyệt. Việc này giữ storyboard làm nguồn nội dung; không bỏ các shot vì khó tạo. Đây là cách thích nghi task I2V, không phải yêu cầu mọi workflow H3 đều phải tách ô.

Chỉ crop khi ô có đủ nét và đúng khung; nếu cần đổi từ khung ngang sang 9:16, tạo lại/reframe có tham chiếu và duyệt lại, không kéo giãn người. Không đưa nhiều góc mặt trong một character sheet làm frame đầu. Khi tạo ảnh mới, sheet dùng ở công cụ tạo ảnh; I2V video nhận kết quả đã ghép nhân vật vào cảnh.

## Trạng thái quan trọng

| Shot ví dụ | Frame đầu đúng | Frame đầu dễ gây lỗi |
|---|---|---|
| Ngồi xem điện thoại | Người đã ngồi, điện thoại một tay đúng phía | Sheet nhiều tư thế/người đứng |
| Nhận ra chuyện vô lý | Điện thoại vẫn trên tay, mức giận phù hợp giai đoạn | Chỉ tay vào điện thoại đang nằm trên ghế |
| Đập/đặt mạnh điện thoại xuống đệm | Điện thoại còn trong bàn tay, trước va chạm | Ảnh sau va chạm, tay trống và điện thoại đã nằm xuống |
| Chỉ tay và mắng | Điện thoại nằm đúng chỗ, tay trống trước khi đưa ngón trỏ | Điện thoại quay lại bàn tay |

Last_frame cần cùng trục/cỡ máy tương thích và là kết quả diễn biến; không là sheet nhận diện. Cắt đổi góc thường nên là lượt/shot khác để dựng cut thật thay vì ép nội suy giữa hai góc mâu thuẫn.

## Prompt I2V

Viết ngắn, ưu tiên diễn biến quan sát được: nhân vật trong ảnh đầu, state changes, camera, sound. Hạn chế diễn giải lưới/shot-index hoặc checklist phủ định dài. Không dùng Picture2 chưa nối. Một câu style ngắn phải khớp ảnh: `Semi-realistic East Asian 3D CGI, subtle doll-like facial stylization, soft cinematic lighting, consistent facial proportions and materials.`

SFX/thoại nằm trong thời lượng render thật. Phone narrator là người ngoài hình; không làm nhân vật lip-sync lời narrator. Với thoại chính xác xuyên nhiều clip, track tiếng riêng giúp dựng liền mạch hơn native audio ngẫu nhiên, nhưng lip-sync vẫn cần được xử lý/duyệt riêng.

## Thời gian dựng và nguồn

Một shot dựng 0.9 giây không có nghĩa model phải render 0.9 giây. Có thể dùng nguồn dài hơn và chọn đoạn, nhưng nếu động tác không đủ trong đoạn cắt thì điều chỉnh diễn xuất/timeline, không tự tuyên bố đã đạt. Tất cả clip dùng mốc 00:00 riêng; không đưa prompt mốc 08.7–15 vào nguồn 5 giây.

Mỗi thay đổi checkpoint đòi hỏi lịch sampling/attention theo chính checkpoint đó; ảnh sạch không giải quyết giới hạn distillation của FastH3.
