# Phân shot, storyboard và thời gian

## Thiết kế trang

Nhãn trên ảnh là SHOT 1, SHOT 2...; nhãn nằm trong caption strip ngoài vùng hình. Prompt video gắn mỗi nhãn với hàng/cột chính xác, ví dụ SHOT 3 = hàng2 cột1 của lưới2×2. Với tập dài giữ số shot toàn tập; timestamp của mỗi run bắt đầu lại 00:00. Có thể dùng bảng `global_shot_id / label / page / row / col / run / local_start / local_end`.

Tỷ lệ video là tỷ lệ **vùng hình từng ô**, không mặc định là tỷ lệ toàn contact sheet. Tổng trang phụ thuộc số hàng/cột, gutters, strip nhãn và lề. Lưới 2 hàng×3 cột chứa ô dọc9:16 không thể đồng thời ép toàn trang9:16 mà không đổi ô hoặc padding. Nêu rõ tỷ lệ từng ô và bố cục trang; khi công cụ chỉ có vài kích thước, ưu tiên ô không méo và lề hợp lý. Không kéo giãn nhân vật để ép grid.

Không biến một hành động nhiều giai đoạn thành collage trong một ô. Chọn khoảnh khắc bắt đầu rõ; video làm phần chuyển động. Nếu cần động tác ngồi xuống1giây, ô nên cho biết đang bắt đầu hạ người; không vẽ người đã ngồi xong rồi yêu cầu bước kế tiếp là ngồi xuống lần nữa. Với đoạn Lan **đã ngồi**, không tự thêm động tác đứng/ngồi.

Ưu tiên nhịp có ý nghĩa: thiết lập → hướng chú ý → điều được nhìn thấy → phản ứng/kết thúc. Không áp công thức này cho truyện không cần nó. Cảnh nhanh dễ biến dạng: chia thành beats rõ, camera nhỏ/ổn định, mặt đủ lớn và tránh tay che mặt nếu không bắt buộc. Không cấm hành động người dùng muốn; nói rõ phương án kiểm soát.

## Công thức thời gian gốc

Đọc #24 thay vì lấy số length124 còn lưu ở widget đã bị link điều khiển:

`n=max(5, round(seconds*24)); frames=n + (5 - n%17)%17`.

| Giây nhập #23 | Frame | Nguồn ở24FPS |
|---:|---:|---:|
| 3 | 73 | 3.042s |
| 4 | 107 | 4.458s |
| 5 | 124 | 5.167s |
| 8 | 192 | 8.000s |
| 10 | 243 | 10.125s |
| 15 | 362 | 15.083s |

Đây là làm tròn frame, không chứng nhận 3s hoặc30s cho chất lượng ổn. Profile được ghi vùng huấn luyện ~124–362frame; mặc định chọn5–15s/run và không vượt trần30s của người dùng. Giữ shot1s trên timeline nếu nội dung cần; không buộc mọi shot dài5s. Lượt nhiều shot có thể4+3+5+3=15s. Nếu run dài hơn15s chưa được kiểm chứng, chia theo beat/nối cảnh thay vì tự tăng widget.

Thời lượng tập = tổng đoạn được giữ − tổng overlap. Không làm chậm động tác để lấp clip nguồn. Tập60s có thể nhiều run ngắn tùy truyện; không mặc định luôn4clip15s hoặc2clip30s. Khi chia run, ghi trạng thái cuối/đầu, hướng di chuyển, ánh sáng, đạo cụ và sound bridge. Dựng/cắt nguồn về thời lượng đích sau khi xem thực tế.

## Prompt storyboard mẫu cấu trúc

Viết thành một prompt đã điền đủ trước khi giao, không để token khung:

- Exactly N populated panels; rows×columns; row-major order; explicit EMPTY coordinates nếu có.
- Attached reference identities, outfits and setting; style và lighting thống nhất.
- Mỗi panel: nhãn, hàng/cột, chủ thể, framing/angle, một khoảnh khắc tĩnh, biểu cảm, vị trí và ánh sáng.
- Separate caption strips below panels; exact ordered labels; no writing inside scene, no extra panels or unintended duplicates.

Mỗi lần tạo ảnh, xem và ghi kết quả QA: nhãnđúng, ôđúng, nhânvậtđúng, wardrobeđúng, trạngtháiđúng. Nếu chưa xem được, ghi chưa kiểm tra. Không bảo đảm chữ render đúng chỉ bằng prompt. Nếu sửa ảnh, dùng công cụ ảnh được cho phép; giữ ảnh gốc và phiên bản đã sửa.
