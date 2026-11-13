# Hợp đồng prompt sau duyệt — Apex Ref2V

Đây là khung chỉ dẫn, không phải prompt video cho một storyboard chưa duyệt.

1. **REFERENCE INPUT ORDER**: `<Picture n>` đi kèm vai trò và mô tả nhận diện. Tạo bảng từ dây + bypass thực; trong plan dùng `{{ref:STORYBOARD}}`, `{{ref:CHAR_01}}` để helper resolve số một lần. Một sheet nhiều góc = một nhân vật; nhân vật cùng ảnh có mô tả phân biệt rõ.
2. **OUTPUT / STORYBOARD INTERPRETATION**: nêu tỷ lệ, giây tổng, style; grid là thứ tự shot, không phải bố cục video. Mỗi cảnh chiếm toàn khung hình; đọc hàng trước cột; không render nhãn, viền hoặc ô EMPTY. Không morph sheet thành người trong cảnh.
3. **CONTINUITY**: ngoại hình/áo/đạo cụ/ánh sáng/trục đã chốt; chỉ dùng asset hiện có. Vai trò shot của storyboard ưu tiên; sheet chỉ nhận diện, môi trường chỉ bối cảnh. Không yêu cầu khóa tuyệt đối.
4. **SHOT TIMELINE**: `[SHOT N] start–end`, vị trí hàng/cột, mở đầu → động tác → trạng thái cuối, cỡ cảnh/góc/một hướng máy. Chủ thể rõ tên/mô tả thay đại từ mơ hồ. Chuyển cut/dissolve khi có lý do; không thêm montage không có trong board.
5. **AUDIO**: ambience, nhạc nếu người dùng yêu cầu; thoại nguyên văn Việt có dấu trong dấu ngoặc kép, ai nói, nói trong cảnh hay voice-over, thời gian. Không thêm hội thoại tự phát. Native audio là thử, không chứng nhận TTS tiếng Việt.
6. **ESSENTIAL CONSTRAINTS**: chỉ vài điều thật cần: một người mỗi sheet, đúng tay/đồ, không bản sao, không text/grid. Không nhồi hàng trăm phủ định. Dài hơn không bảo đảm bám storyboard tốt hơn.

Timing là chỉ dẫn cho model, không phải EDL. Một clip nhiều cut có thể trộn cảnh/mất mặt; thử lượt ngắn ít shot, nếu vẫn sai đề xuất người dùng duyệt phương án từng shot từ frame sạch. Không tự thay cả grid Ref2V bằng ảnh I2V mà không nói rõ thay workflow/task.

Đối với ảnh tham chiếu từ người dùng: xem ảnh thật. Filename “Lan” không đủ chứng minh đúng nhân vật. Không gọi danh tính từ sheet nếu sheet chưa được nối/đang bypass. Thiếu sheet thì chỉ hướng dẫn dùng nhân vật có trên storyboard và nói rõ giới hạn.

## Trường LTX riêng trong preset full

Sau duyệt, có thể bổ sung một đoạn LTX positive ngắn ở #9258 `text`: bảo toàn style 3D, nhân vật/trang phục và bối cảnh đã duyệt, chuyển động/khối mặt hiện có. LTX nhận video pixel, không nhận các Picture reference của H3; không sao chép token Picture, lệnh grid hoặc timeline cut vào trường này. Negative giữ vài lỗi hình học/temporal cần tránh và không phủ định CGI/cartoon.
