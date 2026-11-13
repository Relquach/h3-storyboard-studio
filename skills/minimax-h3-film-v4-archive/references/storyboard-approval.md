# Quy trình bắt buộc: storyboard trước, người dùng duyệt, prompt video sau

## Giai đoạn A — thiết kế và duyệt

1. Đọc nội dung, workflow, ảnh nhân vật/môi trường và lựa chọn đã chốt; chỉ hỏi phần thiếu.
2. Tự chọn shot, nhịp, góc máy và lưới hợp lý, giữ đủ nội dung/thoại trong bản kế hoạch.
3. Tạo ảnh storyboard có nhãn SHOT, kiểm tra và gửi để người dùng xem. Nếu I2V cần ảnh đầu sạch, chuẩn bị/giải thích chúng trong bộ ảnh duyệt; không nhét grid vào first_frame.
4. Trả ảnh + tóm tắt diễn biến và thời lượng dự kiến. **Dừng trước prompt video.** Mời người dùng duyệt hoặc ghi phần cần sửa.
5. Nếu có sửa: sửa ảnh, gửi bản mới, chờ duyệt bản mới. Không chỉ sửa lời mô tả trong khi ảnh vẫn cũ.

Có thể viết prompt tạo ảnh storyboard trong giai đoạn A. Không viết/xuất prompt video cuối, không xuất video_prompt.txt, không queue video, không điền prompt “tạm” để lách bước duyệt. Nếu không tạo được ảnh, nói rõ và giao prompt tạo ảnh; chưa coi storyboard đã tồn tại hoặc được duyệt.

## Giai đoạn B — sau khi người dùng duyệt

Lời xác nhận rõ như “duyệt”, “ổn, làm prompt video”, “dùng bản này” trong ngữ cảnh ảnh cụ thể là đủ; không yêu cầu gõ một mã đặc biệt. Không coi im lặng, hết thời gian chờ, tạo ảnh thành công hoặc yêu cầu ban đầu “tạo storyboard + prompt” là duyệt trước.

Codex giữ bản được duyệt và ghi nội bộ revision/ảnh tương ứng cùng câu xác nhận thực; có thể ghi hash khi có file, không bịa hash/message ID. Người dùng không cần quản lý metadata này.

Từ **nội dung phim đã chốt + storyboard đã duyệt + tài sản tham chiếu thực + task/model thực**, tạo prompt video. Storyboard quyết định ngoại hình, bố cục, thứ tự/cỡ cảnh; nội dung quyết định hành động, âm thanh/thoại không nằm trong ảnh. Đối chiếu hai nguồn; nếu mâu thuẫn làm thay đổi hành động quan trọng, giải quyết và duyệt lại ảnh liên quan trước.

Chỉ sau đó bàn giao prompt tự đủ mỗi lượt, bảng ảnh-node/Picture hoặc first/last frame, duration và setting cần áp dụng. Không hỏi duyệt lại chỉ vì đã xong bước kỹ thuật đã được giao.

## Khi bản duyệt thay đổi

Đổi mặt/trang phục/bối cảnh/shot order/diễn biến hoặc tạo lại ảnh làm thay đổi đáng kể → quay lại A cho phần ảnh đổi, vô hiệu prompt cũ. Sửa lỗi chính tả nhãn mà không đổi hình/diễn biến không cần tạo một vòng duyệt mới nếu đã có ủy quyền sửa.

Với I2V, ảnh đầu phải là trạng thái trước hành động. Nếu storyboard được duyệt chỉ có khoảnh khắc kết quả, cần tạo/duyệt thêm ảnh đầu phù hợp; không âm thầm sửa trạng thái rồi gọi đó là bản người dùng đã duyệt.

## Trạng thái nội bộ

`draft` → `awaiting_approval` → `approved` → `video_handoff_ready`.

`changes_requested` hoặc revision đổi sau duyệt → quay lại `awaiting_approval`.

Helper chỉ kiểm tra hồ sơ trạng thái, không thể tự xác minh rằng một con người thật đã duyệt; Codex phải đối chiếu lời người dùng thực tế. Các hồ sơ duyệt trong unit test là dữ liệu giả lập, không phải duyệt dự án thật.
