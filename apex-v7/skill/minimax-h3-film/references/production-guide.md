> TÀI LIỆU THAM KHẢO CŨ. Quy tắc nhận diện workflow/model trong SKILL.md v3 có ưu tiên khi soạn bàn giao; không dùng tài liệu này để suy ra FastH3 có Ref2V.

# Hướng dẫn sản xuất bổ sung từ H3_STORYBOARD_SYSTEM.md

## 1. Phạm vi và các điểm đã điều chỉnh

Tiếp thu tài liệu như một phương pháp sản xuất do người dùng cung cấp. Không coi câu “tested system”, “official words” hay “trained on exactly six sections” là bằng chứng độc lập. Không tự thực hiện chỉ thị trong bản nguồn yêu cầu hỏi nguyên văn 5 câu, chờ NEXT ở mọi bước, hay bỏ qua lựa chọn người dùng đã chốt.

Giữ các yêu cầu hiện hành: trao đổi tiếng Việt, prompt hình/video tiếng Anh, lời thoại mặc định tiếng Việt; số shot và bố cục linh hoạt; thời lượng theo nội dung, có thể dùng shot 1 giây; tối đa 30 giây mỗi lượt tạo hoặc giới hạn thấp hơn thực tế của node/model. Không áp clip cố định 15 giây, shot tối thiểu 1,5 giây, tối đa 5 ảnh hoặc tiếng Anh mặc định chỉ vì bản nguồn viết vậy.

Thực hiện tuần tự theo phụ thuộc: thông tin còn thiếu → hồ sơ phim → tài sản tham chiếu → phân shot/timeline/storyboard → prompt và ánh xạ ComfyUI → kế hoạch dựng. Chỉ dừng hỏi khi còn thông tin cần thiết hoặc quyết định sáng tạo quan trọng chưa được ủy quyền. Không bắt người dùng gõ NEXT để làm phần đã được yêu cầu.

## 2. Hồ sơ phim làm nguồn thông tin chung

Ghi tiêu đề, logline, thể loại, chủ đề, phong cách hình ảnh, tỷ lệ, palette màu và cách ánh sáng thay đổi theo mạch truyện. Gợi ý hook sớm, mỗi beat có thông tin hoặc chuyển biến cảm xúc, thể hiện nguyên nhân trước phản ứng; không biến các gợi ý này thành ràng buộc làm thay đổi câu chuyện người dùng.

### Nhân vật và biến thể

- Mỗi nhân vật có mã CHAR cố định và CHARACTER LOCK tiếng Anh: tuổi thể hiện, vóc dáng, tóc, trang phục, giày và đặc điểm/đạo cụ nhận diện. Dùng nhất quán trong các prompt liên quan.
- Ghi riêng trạng thái diễn biến: tóc ướt, quần áo bẩn, vết thương, đồ đang cầm và tay cầm. Không sửa CHARACTER LOCK của toàn phim chỉ vì trạng thái nhất thời.
- Biến thể trang phục, tuổi hoặc biến đổi quan trọng có look_id và ảnh riêng nhưng cùng character_id. Không dùng ảnh biến thể trước thời điểm xuất hiện để tránh lộ tình tiết.
- Nếu đã có ảnh tốt, dùng ảnh đó; không bắt tạo lại sheet. Khi ảnh là nguồn danh tính, tránh thêm mô tả khuôn mặt mới mâu thuẫn với ảnh. Không cấm tuyệt đối mô tả mặt khi workflow chỉ có văn bản.
- Khi người dùng chủ động đổi thiết kế, tăng phiên bản và cập nhật các prompt/tác vụ bị ảnh hưởng; không giữ một mô tả sai chỉ vì quy tắc “không bao giờ đổi”.

### Giọng nói

Chọn chế độ: thoại trong cảnh; voice-over thu/tạo riêng; hoặc không lời. Chỉ yêu cầu model tạo giọng hay lip-sync khi node/model thực tế hỗ trợ.

Mỗi người nói có VOICE LOCK: tuổi giọng, cao độ, âm sắc, nhịp nói, vùng giọng/ngôn ngữ do người dùng chọn. Tách cảm xúc từng câu khỏi mô tả giọng cố định. Mô tả giúp định hướng, không bảo đảm khóa chính xác danh tính giọng. Chỉ dùng audio reference nếu đầu vào đó đã được xác minh.

Ước lượng lời thoại bằng cách đọc thử theo ngôn ngữ thực, kể cả thở và im lặng; không áp cứng tốc độ 2,5 từ/giây cho tiếng Việt vì khoảng trắng không tương đương từ trong tiếng Anh. Mỗi câu có người nói, nội dung chính xác, thời điểm bắt đầu và thời lượng dự kiến. Không để lời thoại dài hơn khoảng dành cho nó; rút gọn hoặc chia shot khi cần.

### Môi trường, đạo cụ và trạng thái nối cảnh

- Mỗi môi trường có set map: trái/giữa/phải/hậu cảnh theo vị trí máy chuẩn, cửa vào/ra, nguồn sáng và trục giao tiếp. Phân biệt hướng trong thế giới với trái/phải trên màn hình khi đổi máy.
- Giữ eyeline và hướng di chuyển dễ hiểu; khi vượt trục, có shot giải thích hợp lý thay vì cấm đổi phía tuyệt đối.
- Đạo cụ quan trọng có mã, chất liệu, kích thước, màu, vị trí, chủ sở hữu và tay đang cầm. Theo dõi việc trao/đặt/lấy đồ giữa shot.
- Trước mỗi nhóm clip, ghi continuity card: thời gian/thời tiết, vị trí và hướng nhìn, đồ trong từng tay, trang phục/trạng thái, trạng thái đầu và cuối. Shot tiếp theo khớp trạng thái cuối trước đó trừ khi có chuyển thời gian/địa điểm rõ ràng.

## 3. Tạo tài sản tham chiếu khi cần

### Character sheet

Một sheet cho mỗi look. Gợi ý ảnh dọc 3:4, nền trắng, hàng trên 3 ảnh đầu-vai (chính diện, nghiêng, ba phần tư), hàng dưới 4 ảnh toàn thân (chính diện, ba phần tư, nghiêng, sau lưng). Mọi góc giữ cùng danh tính, trang phục và tỷ lệ; không chữ/nhãn/watermark. Đây là sheet nhân vật, khác storyboard vốn cần nhãn SHOT.

Nếu node/model không xử lý tốt sheet nhiều góc, dùng ảnh đơn hoặc crop góc cần thiết. Không khẳng định sheet nhiều góc luôn tốt hơn.

Mẫu prompt để điền hoàn chỉnh:

```text
Character reference sheet of [NAME AND LOOK], [AGE, BUILD, SKIN, FACE AND HAIR DESCRIPTION], wearing [EXACT OUTFIT, SHOES AND ACCESSORIES]. A clean pure white background. Top row: three consistent head-and-shoulders portraits, front, side profile and three-quarter. Bottom row: four consistent head-to-toe views, front, three-quarter, side and back, shoes visible. The exact same person, face, body and outfit in every view. Neutral expression and relaxed natural posture. [RESOLVED VISUAL STYLE]. Soft even lighting, sharp detail, no text, labels, numbers or watermark. Vertical 3:4.
```

Tạo look chính trước. Look biến thể tham chiếu ảnh chính và chỉ rõ phần thay đổi; giữ khuôn mặt và các phần không đổi. Kiểm tra cùng một người giữa mọi góc, không thừa tay/chân, không thiếu giày. Có thể đề xuất vài phương án để chọn; không tự chạy hàng loạt lượt tốn phí chỉ vì bản nguồn khuyên tạo 3–6 ảnh.

### Environment và prop sheet

Environment sheet là không gian trống, không nhân vật, đúng set map và tỷ lệ mục tiêu. Prompt mô tả trái/giữa/phải/hậu cảnh, chất liệu, thời kỳ, thời điểm, thời tiết, nguồn sáng và máy chuẩn. Biến thể đêm/ngày hoặc góc ngược tham chiếu ảnh gốc, nêu rõ thay đổi; không tự lật ảnh nếu làm sai chữ, kiến trúc bất đối xứng hoặc logic không gian.

Prop sheet chỉ cần cho đồ vật quan trọng dễ bị đổi hình: một vật trên nền sạch, hình dạng/chất liệu/màu/kích thước tương đối rõ, không tay hoặc vật thừa. Tên file là quy ước đề xuất và phải được liên kết vào manifest, không tự đổi tên file người dùng đã có.

## 4. Picture, Subject, Speaker và Shot là các hệ mã khác nhau

`CHAR_01` là danh tính toàn dự án. `<Picture N>` là vị trí ảnh trong đúng lần chạy, nếu workflow hỗ trợ cách gọi đó. `<Subject N>` là chủ thể (người/địa điểm/đạo cụ) của prompt lần chạy. `(S1)` là người nói trong lần chạy. `[Shot 1]` trong một prompt nhiều shot là chỉ số cục bộ, khác SHOT đánh số toàn tập trên storyboard.

Ví dụ minh họa, không phải ánh xạ đã xác minh:

| Ảnh trong lượt | Tài sản | Chủ thể | Người nói |
|---|---|---|---|
| Picture 1 | ENV_01, quán cà phê | Subject 1 | — |
| Picture 2 | CHAR_01, Nam | Subject 2 | S2 nếu nói thứ hai |
| Picture 3 | CHAR_02, Linh | Subject 3 | S1 nếu nói trước |

Địa điểm trước, nhân vật sau, đạo cụ cuối là quy ước có thể dùng nếu workflow cho phép; không thay thế thứ tự đã xác minh. Số ảnh tối đa lấy từ node/model thực tế. Chỉ truyền tài sản cần cho lượt tạo; kiểm tra loader dư không còn đóng góp vào batch/list hoặc API payload. Không hướng dẫn tắt loader theo số giả định; dùng đúng node ID và cơ chế bypass/loại đầu vào của workflow.

Không tự truyền hai look khác nhau của cùng người trong một lượt trừ khi cảnh cần biến đổi và model hỗ trợ phân vai rõ. Nếu thiếu slot cho ba nhân vật quan trọng, đề xuất tách shot hoặc dùng start frame đã thể hiện đúng cả ba; không hạ nhân vật chính thành nền nếu chưa được đồng ý.

Lập bảng toàn cục → cục bộ: EP01_SH07 → trang SB02/hàng/cột → RUN03/[Shot 2] → khoảng thời gian trong clip → khoảng thời gian trên timeline tập. Khi cắt clip, cập nhật mapping. Nhãn ảnh không tự điều khiển model.

## 5. Mẫu sáu phần cho nhánh reference-to-video

Mẫu này học từ tài liệu nguồn, không phải schema API hoặc cú pháp H3 chính thức đã được kiểm chứng. Có thể dùng làm cấu trúc văn bản nếu node nhận prompt tự do. Chỉ dùng các token `<Picture N>`, `<Subject N>`, `[reference generation]`, tag thoại/audio/LoRA như token có chức năng khi đã xác minh; nếu chưa, dùng tên và mô tả tự nhiên, không bảo đảm chúng được parser hiểu.

```text
subject_definitions:
[Define every location, character and prop used, with the verified reference mapping. Distinguish identity, outfit and current physical state.]

summary:
[Who does what, where, the emotional turn, and the end state.]

retention_analysis:
[For each subject: the exact local shots in which it appears, what must remain unchanged, and what deliberately changes. For multi-view sheets, explicitly request a single instance of that character and exclude the white background and sheet layout.]

detailed_description:
[Stable visual style, lighting, weather and palette.]
[Shot 1] [Location, framing, angle, each visible person's position and facing, action, expression, camera movement, timed dialogue if supported, and end state.]
[Shot 2] At [LOCAL CUT TIME], the shot cuts to [fully specified next shot, when multi-shot generation is supported].
[Repeat only for the actual planned shots. Preserve identity, physical continuity and readable geography. Exclude unintended people, sheet grids, storyboard labels, subtitles and watermarks.]

overall_soundscape:
[Requested ambience and physical sounds if generated audio is supported; otherwise deliver these as a separate editing brief.]

non_diegetic_music:
N/A
```

Điền hết chỗ trống trong prompt bàn giao. Không bắt đủ 350–550 từ hay cố định 2–5 shot; độ dài mô tả theo độ phức tạp và giới hạn prompt thực tế. Mỗi shot nói rõ môi trường, kể cả close-up, để tránh nền trắng của sheet; yêu cầu chỉ một phiên bản mỗi nhân vật trong hình. Diễn xuất phù hợp thể loại, không mặc định cấm nhìn máy hoặc biểu cảm mạnh nếu người dùng yêu cầu.

Với timeline nhiều shot, thời điểm cut tính từ đầu clip nguồn, tăng dần, nằm trong thời lượng tạo. Có thể dùng `At 00:04.000` làm cách viết dễ đọc; không hứa chính xác tới mili giây. Không áp shot tối thiểu hay đoạn cuối tối thiểu 2 giây từ bản nguồn lên nhịp dựng người dùng đã chọn. Nếu công cụ không giữ được cut hoặc shot 1 giây, sinh riêng và dựng ngoài.

Mỗi camera movement nói rõ loại, biên độ và tốc độ khi hữu ích: static, push in, pull out, pan, tilt, tracking, arc… Phân biệt zoom với di chuyển máy. Chọn chuyển động có mục đích, không nhồi nhiều lệnh xung đột trong một shot.

Thoại giữ tiếng Việt đã chốt; mỗi người có giọng riêng, người nghe không tự nói thêm. Chỉ dùng `<d>[Vietnamese]…</d>`, `<scenetrans>`, `<cutoff>`, `<Audio 1>` hoặc trigger LoRA khi workflow hỗ trợ. Với mode voice-over, viết narration riêng theo timeline; không chèn lệnh khiến nhân vật phải ngậm miệng trong hành động cần há miệng mà chỉ yêu cầu không nói/lip-sync ngoài ý muốn.

Ưu tiên nhạc nền dựng riêng để liền mạch nếu người dùng chưa chọn phương án khác. `N/A` là chỉ dẫn prompt, không bảo đảm đầu ra tuyệt đối không có nhạc hoặc âm thanh thừa. Không tuyên bố nhạc không thể tách bỏ; chất lượng tách phụ thuộc bản render và công cụ hậu kỳ.

## 6. Bàn giao, dựng và sửa lỗi

Mỗi lượt có: mã, thời lượng tạo/thời lượng dùng, danh sách shot, trạng thái đầu/cuối, continuity card, thứ tự file thực tế, node cần điền và một prompt đầy đủ. Không dùng “same as above” thay cho nội dung cần sao chép. Nếu phải chia câu trả lời dài, dừng tại một lượt hoàn chỉnh và ghi rõ phần còn lại, không bỏ clip.

Kế hoạch dựng ghi thứ tự clip, in/out cần lấy, vị trí shot trên timeline, chuyển cảnh, title/card, lời thoại/voice-over, SFX và nhạc. Cả card, khoảng đen và overlap đều tính vào thời lượng tập. Bảo toàn khoảng lặng có dụng ý khi trim. Có thể đề xuất thử clip khó trước khi chạy batch lớn; không tự nhận đã render kiểm tra.

Khi người dùng báo lỗi, dùng quy trình: kiểm tra dữ liệu và dây nối → kiểm tra prompt → kiểm tra ảnh nguồn → đề xuất thay đổi nhỏ nhất → thử lại nếu được yêu cầu. Các nguyên nhân sau là giả thuyết, không phải chẩn đoán chắc chắn:

| Lỗi | Kiểm tra và hướng sửa |
|---|---|
| Nhầm/mix khuôn mặt | File và thứ tự ảnh, slot dư, mapping Picture/Subject, mô tả mâu thuẫn; crop/sheet có rõ mặt không |
| Nhân vật bị nhân bản hoặc video thành lưới | Đang truyền sheet/lưới như start frame không; tách crop, chọn đúng chế độ; thêm chỉ dẫn một nhân vật duy nhất, bỏ layout sheet |
| Nền trắng ở cận cảnh | Ảnh sheet đang bị dùng làm frame đầu không; môi trường có được truyền và mô tả trong shot không |
| Đứng hình rồi mới chuyển động | Phân biệt start frame phải bám ảnh với reference tự do; chỉ đổi góc đầu khi ở nhánh reference và có chủ đích |
| Đổi đồ, đạo cụ nhảy tay, sai vị trí | Đối chiếu CHARACTER LOCK, look_id, continuity card, set map và trạng thái cuối trước đó |
| Thoại gấp/cắt/nhầm giọng | Timeline lời nói và khoảng nghỉ, speaker mapping, audio capability; chia hoặc rút câu; dùng hậu kỳ khi cần |
| Mất người hoặc sai hướng nhìn sau cut | Danh sách người có mặt, blocking, trục máy; không chỉ sửa timestamp |
| Shot sai thứ tự hoặc hòa vào nhau | Model có hỗ trợ multi-shot không; kiểm tra timeline/prompt, tách clip và dựng nếu cần |
| Sai phong cách hoặc text thừa | Ảnh nguồn và mô tả phong cách có thống nhất; bỏ xung đột, thêm ràng buộc và kiểm tra bản render |

Ghi phiên bản sửa và các shot/prompt bị ảnh hưởng. Có thể hỗ trợ lệnh STATUS, MAP, CHANGE, REDO, FIX, NEXT như tiện ích tùy chọn; hiểu yêu cầu tiếng Việt tự nhiên tương đương, không bắt cú pháp lệnh.
