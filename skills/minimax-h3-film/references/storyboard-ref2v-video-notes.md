# Bổ sung từ video hướng dẫn 6-grid của người dùng

Nguồn: video MP4 trên Drive, file ID `1AyybNb_dYVN1zdHLsrlH-uoElcTLPmZw`, tên “Master Storyboard-to-Video in MiniMax H3_ 6-Grid Reference Guide - (1080p).mp4”, thời lượng khoảng 11 phút 45 giây. Ghi nhận qua các khung hình được trích, chưa phiên âm lời nói, chưa lấy workflow JSON và chưa chạy thử. Không coi preview trong video là chứng minh chính xác mọi tham số hoặc chất lượng giữ danh tính.

## Các quan sát có thể đối chiếu

- Khoảng 04:30: node hiển thị tên `MiniMax H3 Reference to Video`, ID #11 trong ví dụ; có các socket `ref_images.ref_image_0`, `ref_images.ref_image_1`, prompt và các loại reference video/audio. Dòng model thấy `10Eros_Max_h3_TURBO_ref2va_beta2.safetensors`. ID, tên file và socket ở đây là ghi chép ví dụ, chưa phải cấu hình workflow của người dùng.
- Khoảng 05:00–05:10: `Load Image` #9 chứa nguyên storyboard 2 hàng × 3 cột, có số 1–6. Prompt bắt đầu bằng `subject_definitions`, định nghĩa chủ thể riêng và `<Picture 1>` là toàn bộ storyboard sáu ô. Duration hiển thị 10.0. Các dây đi ra ngoài vùng quay không đủ để tái dựng đầy đủ liên kết.
- Khoảng 05:30: có chuỗi sampling, `Separate AV Latent`, node latent upscale, `Concat AV Latent` và sampling tiếp theo. Upscale là bước chất lượng, không phải cơ chế ánh xạ nhân vật hoặc đọc thứ tự ô.
- Khoảng 06:30: màn hình chat có ảnh sheet nhiều góc của hai nhân vật và yêu cầu tạo storyboard. Đây là bằng chứng dùng sheets ở bước tạo storyboard, chưa chứng minh chúng được truyền riêng vào node video.
- Khoảng 08:15: nguyên storyboard pha trà vẫn nằm trong Load Image, prompt bên cạnh có `[Shot 5] At 00:07.600` và `[Shot 6] At 00:09.600`, kèm chỉ dẫn giữ nhận diện, đồ vật và loại bỏ chữ thừa.
- Các đoạn preview cho thấy hình toàn màn hình thay vì giữ lưới. Video trình diễn cả ảnh storyboard màu và dạng phác họa; không suy ra mọi storyboard/model đều hoạt động như nhau.

## Quy trình ưu tiên đã điều chỉnh

1. Khóa character sheet, look, môi trường và ánh xạ tài sản.
2. Tạo storyboard có nhận diện đúng ngay từ đầu. Chọn số ô theo nội dung; không bắt 6 ô vì video dùng 6.
3. Chia storyboard và kế hoạch thành các lượt tạo không vượt 30 giây hoặc giới hạn model thấp hơn. Một trang không mặc nhiên phải chứa cả tập.
4. Nạp nguyên trang vào **reference image** của nhánh Ref2V đã kiểm tra. Giữ nhãn trong ảnh để đối chiếu nhưng yêu cầu không tái hiện nhãn, đường viền hay lưới trong phim.
5. Viết prompt một lượt nhiều shot: mô tả vai trò toàn ảnh, thứ tự đọc, số hàng/cột, từng ô và thời lượng, chủ thể nào có mặt, động tác nối tiếp và phong cách đích.
6. Chỉ thêm ảnh character sheet vào đầu vào reference khác khi đã xác minh cách node sắp thứ tự ảnh và cách prompt chỉ đúng nhân vật. Đừng khẳng định video nguồn đã chứng minh nhánh kết hợp này.
7. Kiểm tra kết quả; nếu sai cut/nhận diện hoặc shot quá ngắn khó điều khiển, giảm số shot mỗi lượt, sửa ảnh storyboard hoặc tạo riêng shot cần sửa để dựng nối.

## Đoạn chỉ dẫn gợi ý cho prompt

Đây là mẫu tự soạn theo quan sát, không phải bản chép nguyên prompt của tác giả. Điền đầy đủ và điều chỉnh cách gọi ảnh theo workflow thực tế:

```text
The reference image is a storyboard containing [ROWS] rows and [COLUMNS] columns, with [N] populated panels. Read it left to right across the top row, then continue row by row downward. Each labeled panel represents one chronological shot, not a simultaneous split-screen composition. Use it to guide shot order, character identity, staging, action progression and camera framing.

Generate a full-screen cinematic sequence. Do not reproduce the storyboard grid, gutters, borders, panel numbers or SHOT labels. Preserve the intended characters without creating extra copies from their repeated appearances across the panels.

[List every actual panel-to-shot mapping, subject identity, action, camera direction and planned local cut time. State explicitly whether the storyboard's visual style is preserved or intentionally transformed.]
```

Nếu dùng template sáu phần, đưa vai trò storyboard vào `subject_definitions`, diễn biến vào `summary`, yếu tố cần giữ/đổi vào `retention_analysis`, timeline vào `detailed_description`. Nêu rõ một ảnh storyboard có thể chứa nhiều chủ thể; không mặc định Picture N và Subject N có cùng số.

Các mốc cut là mục tiêu điều khiển, không bảo đảm chính xác từng frame. Ví dụ trong video có cut 9,6 giây khi duration hiển thị 10 giây; không lấy đó làm mẫu bắt buộc hoặc xác nhận clip thực tế dài đúng 10 giây. Khi có JSON, kiểm tra thêm công thức quy đổi thời lượng sang số frame, FPS và giới hạn node.
