# Quy trình mới

1. Gửi nội dung phim, ảnh nhân vật/môi trường và workflow đang dùng cho Codex kèm skill này.
2. Codex đọc workflow, hỏi phần thiếu, lên shot plan và tạo ảnh storyboard. Phong cách mặc định: 3D bán hiện thực Á Đông, pha nét búp bê; số ô và giây từng shot theo nội dung.
3. Bạn xem ảnh, yêu cầu sửa hoặc nói “duyệt bản này”. Có sửa ảnh thì xem lại bản mới.
4. Chỉ sau khi duyệt, Codex dùng chính storyboard đó cùng nội dung/thoại đã chốt để viết prompt video, bảng nạp ảnh và setting.
5. Bạn render nháp trong ComfyUI, xem nội dung/nhân vật trước khi nâng chất lượng.

Nếu workflow là I2V, Codex phải chuẩn bị ảnh shot sạch làm frame đầu; grid chỉ là bản kế hoạch. Nếu muốn đưa nguyên grid và sheet riêng, cần workflow/model Ref2V phù hợp. FastH3 V2 hiện dùng chỉ công bố distillation cho T2AV; đừng coi việc có cổng ảnh là bảo đảm I2V.

Tất cả các ảnh mới/chưa có phải ghi rõ. Bản skill này không tự tạo storyboard hoặc prompt video cho một dự án cụ thể; Codex phải nhận nội dung và tuân thủ bước duyệt.

Bản công khai không gồm JSON, video, frame hoặc thoại riêng. Dùng workflow người dùng cung cấp trong phiên làm việc để đối chiếu.
