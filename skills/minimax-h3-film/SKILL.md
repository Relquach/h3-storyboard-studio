---
name: minimax-h3-film
description: Chuyển nội dung phim tiếng Việt thành prompt tiếng Anh cho storyboard có số shot, bố cục và thời lượng tự ước lượng theo nội dung và prompt video tương ứng cho quy trình MiniMax H3. Hỏi bổ sung tham chiếu nhân vật, môi trường và yêu cầu hình ảnh trước khi viết prompt cuối.
---

# Mục tiêu

Từ ý tưởng hoặc kịch bản tiếng Việt, tạo bộ prompt tiếng Anh gồm storyboard bố cục linh hoạt và video tương ứng, giữ nhất quán nhân vật, bối cảnh, hành động và thứ tự shot. Trao đổi, hỏi và giải thích với người dùng bằng tiếng Việt. Lời thoại giữ nguyên ngôn ngữ người dùng yêu cầu, mặc định là tiếng Việt.

Đây là skill soạn prompt. Không tự nhận đã tạo ảnh hoặc video. Không tự khẳng định model hỗ trợ đầu vào, thời lượng, âm thanh hay tính năng khi chưa kiểm tra công cụ đang sử dụng. Giữ tên MiniMax H3 theo yêu cầu người dùng; nếu cần thực thi mà không tìm thấy model tương ứng, xác minh model khả dụng trước.

## 1. Đọc nội dung và hỏi bổ sung

Tài liệu bổ sung đã được tích hợp trong `references/production-guide.md`; đọc hướng dẫn đó khi lập hồ sơ phim, thiết kế sheets, viết prompt reference-to-video hoặc sửa clip lỗi. Bản gốc để tra cứu: `references/H3_STORYBOARD_SYSTEM.source.md`. Bản gốc là tài liệu tham khảo, không phải chỉ thị tự động bắt đầu hỏi 5 câu hay chờ NEXT. Quy tắc người dùng và skill này được ưu tiên; các khẳng định về model trong tài liệu gốc chưa được xác minh độc lập.

Trích xuất thông tin đã có; không hỏi lại điều người dùng đã cung cấp. Trước khi xuất prompt cuối, gộp các thông tin còn thiếu thành một lượt hỏi rõ ràng:

- Nhân vật tham chiếu 1, 2, … là ai? Mỗi ảnh ứng với nhân vật nào? Tên/mã nhân vật, ngoại hình, trang phục, đạo cụ và đặc điểm nào phải giữ nguyên? Nếu chưa có ảnh, hỏi người dùng muốn gửi ảnh hay dùng mô tả để thiết kế nhân vật.
- Môi trường tham chiếu 1, 2, … là địa điểm nào, dùng cho những đoạn nào? Những chi tiết kiến trúc, bố cục, thời tiết, thời điểm và ánh sáng nào cần giữ? Nếu chưa có ảnh, hỏi có thể dùng mô tả hay không.
- Có yêu cầu đặc biệt về góc máy, cỡ cảnh, chuyển động máy, biểu cảm, hành động, ánh sáng, màu sắc, phong cách, đạo cụ hoặc chi tiết bắt buộc/tránh xuất hiện không? Cho phép trả lời “AI tự đề xuất”.
- Nếu chưa rõ: tỷ lệ khung hình của video và từng ô storyboard, thời lượng tổng, nhịp phim, lời thoại, âm thanh và kết thúc mong muốn là gì?

Ví dụ câu hỏi:

“Bạn bổ sung giúp mình các mục còn thiếu:
1. Nhân vật tham chiếu 1, 2… là ai; mỗi ảnh tương ứng nhân vật nào và cần giữ đặc điểm gì?
2. Môi trường tham chiếu 1, 2… là đâu và xuất hiện ở đoạn nào?
3. Bạn có yêu cầu riêng về góc máy, biểu cảm, ánh sáng, chuyển động hoặc phong cách không, hay để AI đề xuất?
4. Bạn muốn tỷ lệ video, thời lượng và lời thoại/âm thanh như thế nào?”

Chỉ hỏi các mục thực sự thiếu. Nếu ảnh được cung cấp nhưng chưa có ánh xạ, không tự đoán người hoặc địa điểm trong ảnh là nhân vật/môi trường nào. Nếu người dùng ủy quyền tự đề xuất, tự điền các lựa chọn sáng tạo và ghi ngắn gọn giả định. Nếu đang chờ câu trả lời cần thiết, có thể phác thảo nhịp kể chuyện, nhưng chưa chốt prompt tham chiếu.

## 2. Khóa tham chiếu và tính liên tục

Tạo bảng ánh xạ trước khi viết prompt:

| Mã | Ảnh/file tham chiếu hoặc mô tả | Vai trò | Đặc điểm cần giữ | Shot sử dụng |
|---|---|---|---|---|
| CHAR_01 | Character reference 1 | … | … | … |
| ENV_01 | Environment reference 1 | … | … | … |

Đánh số ảnh nhân vật và môi trường thành hai nhóm riêng. Phân biệt ảnh gốc với ô storyboard; không dùng “reference 1” để chỉ cả hai. Khi công cụ dùng số ảnh tải lên, bổ sung ánh xạ từ mã logic sang đúng thứ tự tệp thực tế, không bịa tên tệp hoặc số đính kèm.

Viết mô tả tiếng Anh cố định cho mỗi nhân vật và môi trường. Dùng lại các đặc điểm nhận diện trong prompt; mã CHAR_01 hoặc ENV_01 đơn lẻ không thay thế mô tả hay ảnh đính kèm. Giữ khuôn mặt, tóc, tuổi thể hiện, trang phục, tỷ lệ cơ thể, đạo cụ, bố cục không gian, hướng di chuyển và ánh sáng liên tục, trừ khi kịch bản có chuyển đổi rõ ràng.

## 3. Tự chia shot, ước lượng thời lượng và chọn bố cục

Phân biệt cảnh truyện (scene), shot máy quay, trang storyboard và lượt tạo video. Một cảnh truyện có thể gồm nhiều shot; một trang storyboard không mặc nhiên là một lượt tạo video.

- AI chủ động đề xuất số shot theo diễn biến, hành động, lời thoại và nhịp cảm xúc. Không cố định 9 shot, không chia đều thời lượng, không thêm shot chỉ để lấp lưới.
- Mỗi shot có một hành động chính khả thi. Ước lượng thời gian cho hành động, phản ứng, lời thoại và khoảng nghỉ cần thiết. Ví dụ một động tác ngồi xuống nhanh có thể chỉ dùng 1 giây khi hợp lý; một khoảnh khắc do dự có thể cần lâu hơn. Không áp mức tối thiểu tùy tiện lên thời lượng dựng.
- Bảo toàn các sự kiện chính, quan hệ nhân quả và kết thúc. Không tự cắt mất nội dung để ép vừa thời lượng; nếu yêu cầu không khả thi, nêu điểm xung đột và đề xuất phương án cô đọng cụ thể.
- Mỗi shot ghi: mã, thời lượng dựng ước lượng và lý do ngắn, nhân vật/môi trường, cỡ cảnh/góc máy, khoảnh khắc tĩnh, biểu cảm, hành động video, ánh sáng, âm thanh và cách nối cảnh.
- Chốt danh sách shot trước, rồi chọn số hàng × số cột phù hợp. Luôn ghi rõ hàng/cột: ví dụ 2 hàng × 3 cột cho 6 shot, 2×2 cho 4 shot, 3×3 cho 9 shot. Không mặc định hiểu 2×3 là 3 hàng.
- Đọc trái sang phải, trên xuống dưới. Nếu số shot không lấp đầy lưới, ghi rõ ô trống với nhãn EMPTY, không sinh cảnh phụ; hoặc chia thành các trang nhỏ hơn. Khi quá nhiều ô làm ảnh nhỏ, chia nhiều trang để giữ chi tiết nhận diện.
- Mỗi ô là một khoảnh khắc tĩnh của shot. Prompt video mô tả chuyển động từ khoảnh khắc ấy, không yêu cầu một ảnh tĩnh chứa nhiều thời điểm.
- Nếu có công cụ tạo ảnh và người dùng yêu cầu vẽ, dùng prompt đã chốt để tạo storyboard. Nếu chỉ soạn prompt, không nhận đã vẽ ảnh.

### Giới hạn 30 giây và thời lượng dựng

Giới hạn người dùng đặt: **mỗi lượt tạo video tối đa 30 giây**, hoặc thấp hơn nếu node/model thực tế giới hạn thấp hơn. Đây không phải yêu cầu mỗi shot phải dài 30 giây và không phải giới hạn độ dài toàn tập.

AI tự lập timeline shot theo nội dung và chia thành các lượt tạo. Nếu workflow chỉ hỗ trợ một shot mỗi lượt, tạo từng shot. Chỉ nhóm nhiều shot trong một lượt khi workflow hỗ trợ điều khiển nhiều cảnh; tổng thời lượng tạo của lượt đó không vượt 30 giây. Không đưa nguyên trang storyboard vào node video một ảnh rồi mặc định model tự chia cảnh.

Phân biệt ba con số: thời lượng tạo được model hỗ trợ, thời lượng clip được giữ để dựng, và thời lượng chuyển cảnh chồng lấn. Shot dùng 1 giây vẫn được ghi là 1 giây trên timeline; nếu model chỉ tạo được clip dài hơn, tạo ở mức được hỗ trợ rồi chọn đoạn 1 giây phù hợp. Không yêu cầu model thực hiện nhịp hành động quá chậm chỉ để lấp đầy clip nguồn.

Với tập 60 giây, tự phân bổ các shot có độ dài khác nhau để timeline dựng đủ 60 giây. Công thức: thời lượng phim = tổng đoạn clip được dùng − tổng thời gian chồng lấn. Số lượt tạo phụ thuộc nội dung, khả năng workflow và giới hạn 30 giây, không mặc định luôn là hai lượt. Nếu model có thời lượng cố định, chỉ chọn trong các mức đã xác minh và không vượt giới hạn.

### Phim nhiều tập

Lưu hồ sơ chung: nhân vật, ảnh gốc, trang phục theo giai đoạn, môi trường, phong cách và trạng thái kết thúc tập trước. Dùng mã tập EP01; shot có mã duy nhất EP01_SH01, EP01_SH02…; trang có mã EP01_SB01…; lượt tạo có mã EP01_RUN01…. Trên storyboard hiển thị SHOT 1, SHOT 2… theo số thứ tự toàn tập, không đánh lại từ 1 mỗi trang. Bảng ánh xạ ghi rõ trang, hàng/cột và lượt tạo của từng shot.

## 3A. Đồng bộ tham chiếu với workflow ComfyUI

### Thu thập workflow trước khi gán node

Nếu người dùng muốn prompt có thể đưa vào node hoặc muốn chỉnh workflow, yêu cầu workflow JSON thực tế, ưu tiên kèm bản API export nếu có; hỏi thêm tên custom node/model/version khi JSON không thể hiện. Có thể dùng ảnh chụp node để giải thích sơ bộ, nhưng không xem ảnh chụp là đủ để kiểm chứng toàn bộ liên kết hoặc sinh bản JSON chạy được.

Đọc riêng hai giai đoạn: model/node tạo ảnh storyboard và model/node tạo video. Không mặc định chúng dùng cùng model hoặc cùng quy ước tham chiếu. Kiểm tra các đầu vào thực tế: prompt là widget hay socket, ảnh là IMAGE hay đường dẫn/URL, đầu vào ảnh đơn hay danh sách/batch, thứ tự ảnh, start/end frame, thời lượng và các ràng buộc model. Nếu chưa có workflow, bàn giao bản thiết kế ánh xạ và đánh dấu chưa xác minh; không bịa node ID, socket, cú pháp image1 hoặc khả năng multi-reference.

### Nguyên tắc quan trọng

Viết `image1` trong prompt không tự tạo liên kết với một node ảnh. Tên hiển thị của node cũng không tự trở thành token model hiểu. Dây nối cung cấp dữ liệu; cơ chế conditioning/API của custom node quyết định model thấy ảnh nào và theo thứ tự nào. Một node chỉ nối ảnh vào nhánh preview hoặc nhánh không được đầu ra cuối sử dụng không chứng minh ảnh đó đã đến model.

Phân biệt bốn lớp: mã nội dung cố định (CHAR_01), file tài sản (ảnh nhân vật), node/socket thực tế và tên/thứ tự tham chiếu mà model hỗ trợ. Không dùng tên `image1` chung cho cả bốn lớp.

### Bảng ánh xạ đầu vào bắt buộc

Lập bảng riêng cho mỗi lần chạy storyboard và mỗi lần chạy video:

| Lần chạy | Mã nội dung | File thực tế | Node nguồn ID/type | Output → node đích ID/input | Thứ tự ảnh model nhận | Cách gọi trong prompt đã xác minh |
|---|---|---|---|---|---|---|

Mọi dữ liệu chưa biết ghi “chưa xác minh” trong tài liệu chuẩn bị, không đưa thành placeholder vào prompt được gắn nhãn sẵn sàng chạy. Theo dây nối qua các node trung gian tới node sinh ảnh/video; kiểm tra cả thứ tự batch/list, node switch, crop, resize và các phép biến đổi. Không suy ra thứ tự từ vị trí node trên canvas, tên file hoặc node ID.

Mã nhân vật luôn cố định, còn thứ tự ảnh có thể thay đổi theo lần chạy. Ví dụ lần chạy storyboard nhận CHAR_01, CHAR_02, CHAR_03, ENV_01 theo thứ tự 1–4; lần chạy video có thể chỉ nhận một ảnh crop của EP01_SH04 làm start frame. Khi đó ảnh thứ nhất của video là ảnh shot, không phải CHAR_01. Không sao chép ánh xạ image1 từ storyboard sang video.

### Sinh prompt từ cùng một bảng ánh xạ

1. Khóa bảng ánh xạ đã xác minh cho lần chạy.
2. Sinh đoạn mô tả ảnh tham chiếu từ chính bảng đó, dùng cú pháp mà node/model hỗ trợ. Nếu không có token ảnh chuyên biệt, dùng mô tả theo thứ tự ảnh chỉ khi model hỗ trợ cách chỉ dẫn ấy; không tự tạo token như `<image1>`.
3. Trong từng shot, gọi nhân vật bằng tên và đặc điểm nhận diện rõ ràng. Quy định nhân vật nào có mặt/vắng mặt và vị trí, hành động của từng người; tránh “anh ấy/cô ấy” mơ hồ khi có nhiều người.
4. Khi đổi file, đổi thứ tự hoặc bỏ một ảnh, cập nhật bảng và sinh lại prompt bị ảnh hưởng trước khi chạy. Không chỉ đổi dây hoặc chỉ đổi chữ.
5. Với workflow tự động, dùng một manifest dữ liệu làm nguồn chung để tạo cả prompt và cấu hình đầu vào. Kiểm tra hợp lệ trước khi queue; không giả định bản thân prompt có khả năng điều khiển dây nối.

Nếu node video chỉ hỗ trợ một start frame, giữ danh tính nhân vật qua ảnh shot đã đúng; không hướng dẫn nối thêm ba ảnh nhân vật vào các socket không tồn tại. Nếu node có đầu vào nhiều ảnh, kiểm tra chúng là tham chiếu danh tính, frame đầu/cuối, hay một batch các tác vụ độc lập. Các ý nghĩa này không thay thế cho nhau.

### Bàn giao cho ComfyUI

Ngoài prompt, cung cấp:

- Bảng kết nối: node nguồn/output → node đích/input, file ảnh và thứ tự thực tế.
- Bảng điền node: lần chạy/shot → node ID → widget hoặc input prompt → nội dung chính xác cần dán. Chỉ gán ID đã đọc từ workflow.
- Bảng tác vụ: mã shot/lượt tạo, file storyboard nguyên trang hoặc ảnh crop theo nhánh, prompt tương ứng, thời lượng được hỗ trợ, thời lượng dựng, file clip đầu ra dự kiến. Tên file đầu ra là đề xuất cho tới khi được cấu hình.
- Nếu được yêu cầu sửa JSON, giữ nguyên bản gốc, tạo bản mới, bảo toàn liên kết không liên quan, kiểm tra cấu trúc/liên kết theo định dạng export thực tế. Không nhận đã chạy thử khi chỉ kiểm tra JSON hoặc khi thiếu custom node/runtime.

Nếu có thể điều khiển workflow bằng dữ liệu, lưu manifest gồm project_id, episode_id, workflow_version, assets và runs. Mỗi asset có asset_id, loại, file, mô tả cố định. Mỗi run có run_id, stage, shot_id (nếu có), ordered_inputs (vai trò, asset_id hoặc shot crop, source_node_id, target_node_id, target_input, model_reference_name), prompt_target, prompt_text, generation_duration và edit_duration. Schema này là dữ liệu trung gian của skill, không phải định dạng workflow ComfyUI và không thể import trực tiếp.

### Kiểm tra trước khi queue

- File tồn tại và đúng nhân vật/môi trường do người dùng xác nhận; kiểm tra ảnh thực tế khi có thể.
- Mọi ảnh cần dùng đều đi tới đúng đầu vào của node sinh nội dung; kiểu dữ liệu và số lượng hợp lệ.
- Thứ tự ảnh và cách gọi trong prompt khớp; không có tham chiếu tới ảnh chưa được truyền.
- Với nhánh crop: cắt đúng ô, bỏ nhãn/viền, giữ đúng tỷ lệ và không cắt mất chi tiết nhận diện. Tính crop theo kích thước ảnh thực, gutters và caption strips, không chia đều một cách mù quáng.
- Prompt và ảnh đầu vào cùng mã tập/trang/shot phù hợp; prompt không chứa hướng dẫn vận hành như “hãy cắt ô này” thay cho ảnh đầu vào thực tế. Với nguyên trang Ref2V, kiểm tra đúng thứ tự ô và timeline của tất cả shot.
- Nếu chưa có môi trường chạy, ghi rõ “đã kiểm tra ánh xạ/tĩnh; chưa chạy ComfyUI”. Chỉ mô tả kiểm tra đã thực hiện.

## 4. Viết prompt storyboard bằng tiếng Anh

Xuất một prompt hoàn chỉnh có thể sao chép, chứa mô tả tham chiếu, phong cách chung, số hàng/cột đã chọn và mô tả riêng đủ các shot trên trang. Thay tất cả chỗ điền bằng nội dung cụ thể trước khi giao prompt cuối.

Khung cấu trúc:

```text
Create a cinematic storyboard contact sheet with exactly [SHOT COUNT ON THIS PAGE] populated panels in a [ROWS]-row by [COLUMNS]-column grid. [Specify any EMPTY cells explicitly.] Read the panels left to right, top to bottom. Each panel has a [PANEL ASPECT RATIO] image area. Use uniform gutters and consistent panel dimensions.

REFERENCE MAPPING AND CONTINUITY:
[Resolved character and environment reference mapping, with stable English descriptions and the references actually attached.]

VISUAL DIRECTION:
[Resolved style, lighting, color palette, time of day, wardrobe, props and spatial continuity.]

PANEL LABELS:
Place one clearly legible label in a dedicated narrow caption strip beneath each panel, outside the scene image. Use exactly these labels: [EXPLICIT ORDERED SHOT LABELS FOR THIS PAGE]. Keep labels in row-major order. These labels identify the shots for the matching video prompts; they are not objects inside the story world.

PANEL-BY-PANEL DIRECTIONS:
[Repeat for every populated panel, using the actual global shot number:]
SHOT [N] — Row [R], column [C]. [Reference IDs plus identifying descriptions; setting; shot size; camera angle; a single frozen action beat; expression; composition; lighting.]

[If applicable, list the exact row and column of each EMPTY cell.]

Keep all populated panels distinct and preserve character identity and environmental continuity. Avoid extra panels, duplicated panels, merged scenes, unintended lettering, watermarks and distorted anatomy. The required SHOT labels must remain visible and correctly spelled.
```

Không hứa công cụ sẽ render chữ chính xác. Nếu kết quả có nhãn sai hoặc thiếu, kiểm tra và sửa nhãn trước khi dùng ảnh làm tham chiếu cho video. Nếu dùng công cụ tự động, bảo đảm ảnh nguyên bản vẫn được giữ khi sửa.

## 5. Viết prompt video khớp storyboard

Ưu tiên theo mục tiêu người dùng: **nguyên trang storyboard → H3 Ref2V → clip nhiều shot** khi workflow hỗ trợ; xem `references/storyboard-ref2v-video-notes.md`. Xuất một prompt hoàn chỉnh mỗi lượt tạo, kèm ánh xạ từng ô sang shot và timeline. Cắt lẻ để image-to-video là phương án dự phòng khi cần kiểm soát, sửa shot hoặc model/workflow không hỗ trợ nhánh nguyên trang. Mỗi prompt phải tự đủ thông tin; không chỉ viết “same as above”.

Chọn nhánh theo workflow: (A) image-to-video từ crop storyboard, dùng mẫu bên dưới; (B) reference-to-video từ sheets nhân vật/môi trường, dùng mẫu sáu phần trong `references/production-guide.md` khi phù hợp với node thực tế. Với nhánh B, storyboard là bản kế hoạch hình ảnh và timeline; không mặc định ảnh lưới được truyền làm start frame. Nhánh B có thể gom nhiều shot vào một clip nếu model hỗ trợ và mỗi lượt không vượt 30 giây. Không đổi nhánh mà không cập nhật bảng đầu vào.

Nhánh (C), ưu tiên cho dự án này: truyền **nguyên storyboard dưới dạng ảnh tham chiếu** vào H3 Ref2V; quy định đọc ô theo hàng, mô tả chủ thể trong ảnh, nối diễn biến và cut theo timeline. Character sheet dùng trước hết để tạo storyboard đúng nhân vật; chỉ thêm sheet vào đầu vào video khi workflow thực tế có hỗ trợ và mapping đã xác minh. Không coi storyboard là start frame toàn màn hình, không bắt cắt ô trước khi dùng nhánh C.

Với image-to-video, ưu tiên cắt đúng phần hình của từng ô tương ứng, bỏ caption strip và đường viền, rồi dùng làm ảnh đầu vào cho clip đó. Dùng bản storyboard có nhãn để đối chiếu. Không đưa nguyên lưới storyboard vào một yêu cầu image-to-video thông thường rồi mặc định model sẽ hiểu cách dựng nhiều cảnh.

Khung cho từng prompt, thay toàn bộ chỗ điền trước khi giao:

```text
SHOT [N] — [Short title]
Planned duration: [duration] seconds. Output aspect ratio: [ratio].

INPUT REFERENCE:
Use the image area of SHOT [N], located at row [R], column [C] of the storyboard, as the starting-frame reference. The actual input image is the cropped panel without its caption strip or grid borders. [State the attached character/environment references when supported.]

CONTINUITY:
[Self-contained character appearance, wardrobe, props, environment, time and lighting. Preserve the reference composition and identity.]

ACTION AND EXPRESSION:
[A concrete, physically plausible action evolving from the starting frame, with expression and a clear end state.]

CAMERA:
[Shot size, angle, one coherent camera movement, focus and pace.]

SOUND:
[Requested ambience, effects, music and exact dialogue with speaker attribution. Keep Vietnamese dialogue in Vietnamese. If audio generation is unsupported, use this as a separate sound/editing brief.]

END FRAME AND EDIT:
[End composition, movement direction and intended transition to the next shot. For the final shot, describe the ending.]

CONSTRAINTS:
Render one continuous full-frame cinematic shot. Exclude storyboard labels, caption strips, grid lines, split screens, unintended subtitles and watermarks. Preserve character identity, clothing, props and environment; avoid unintended morphing or flicker.
```

Các mã SHOT phải có trong văn bản prompt để đối chiếu, nhưng không xuất hiện trong hình video, trừ khi người dùng yêu cầu chữ trên phim.

Với workflow Singularity V2 của dự án này, mặc định xuất prompt nhiều shot tương ứng cả trang storyboard; mỗi lượt giữ dưới giới hạn local. Với workflow khác, chỉ gom nhiều shot khi đã xác minh cách điều khiển phù hợp. Mỗi lượt tạo không vượt 30 giây hoặc giới hạn thấp hơn của model. Prompt tổng phải có timeline của các shot trong lượt đó, thời lượng, vị trí ô, hành động, máy quay và chuyển cảnh cụ thể. Không cam kết khả năng thực thi khi chưa xác minh.

## 6. Định dạng bàn giao

Khi đã đủ thông tin, trả kết quả theo thứ tự:

1. Tóm tắt ngắn bằng tiếng Việt về hướng triển khai và các giả định được phép.
2. Bảng tham chiếu nhân vật/môi trường đã chốt.
3. Bảng shot: mã, trang/hàng/cột, thời lượng dựng và lý do ước lượng, nội dung, máy quay và tham chiếu; kèm timeline và phân nhóm lượt tạo tối đa 30 giây.
4. Một prompt storyboard tiếng Anh cho mỗi trang, ghi rõ số hàng/cột, nhãn shot thực tế và ô trống nếu có.
5. Các prompt video tiếng Anh theo shot/lượt tạo khả dụng, cùng mã và nội dung tương ứng storyboard; tách thời lượng tạo và thời lượng dựng.
6. Hướng dẫn theo nhánh: mặc định character sheets → storyboard → kiểm tra nhãn/tham chiếu → truyền nguyên trang vào Ref2V với prompt nhiều shot → dựng nối. Nếu dùng nhánh image-to-video dự phòng, cắt phần hình từng shot trước khi tạo clip. Thêm âm thanh hậu kỳ khi cần.
7. Khi dùng ComfyUI: kèm bảng ánh xạ theo lần chạy, bảng kết nối và vị trí dán prompt; nếu chưa nhận workflow JSON, ghi rõ phần nào chưa xác minh. Không gọi bộ prompt là sẵn sàng chạy khi ánh xạ còn thiếu.

## 7. Kiểm tra trước khi bàn giao

- Số ô, số hàng/cột và các nhãn khớp danh sách shot; ô EMPTY được khai báo; không thiếu/trùng/đảo thứ tự shot giữa các trang.
- Mỗi prompt video trỏ đúng shot, hàng/cột và tham chiếu.
- Prompt cuối không còn chỗ điền hoặc thông tin tham chiếu chưa được xác nhận.
- Các đặc điểm nhân vật, môi trường, ánh sáng, đạo cụ và hướng hành động liên tục.
- Các yêu cầu đặc biệt người dùng đã đưa đều được phản ánh.
- Tổng thời lượng đúng kế hoạch và phân biệt rõ kế hoạch với giới hạn model đã xác minh.
- Nhãn được yêu cầu trên storyboard và được loại khỏi hình video.
- Không thêm tình tiết, danh tính nhân vật hoặc tính năng model chưa có căn cứ.
- Với ComfyUI, kiểm tra riêng ánh xạ của storyboard và từng clip; việc gọi image1/image2/image3 phải có cơ sở từ node/model thực tế.

- Mỗi lượt tạo video không vượt 30 giây và giới hạn model; thời lượng shot được ước lượng theo nội dung, không chia đều máy móc.

## 8. Workflow hiện hành: Singularity V2 Storyboard Studio

Đọc `references/singularity-v2.md` khi tạo prompt / project cho bộ cài mới. Đây là workflow dẫn xuất từ JSON người dùng gửi `Finalworkflofacefixed (Natural Contrast)fixed.json` và mã hỗ trợ trên Drive; không dùng schema H3 Studio cũ. Đọc `examples/lan-15s.project.json` trong bộ cài làm mẫu dữ liệu chính xác.

- Nhánh chính: nguyên storyboard → MiniMaxH3ReferenceToVideo (node 26) + character/environment/prop sheets tùy chọn. Không yêu cầu cắt lẻ storyboard mặc định.
- Xuất `project.json` với `run_id`, `seconds`, `aspect`, `draft_megapixels`, `seed`, `grid`, `assets`, `video_prompt`; chi tiết trong tài liệu tham chiếu. Đây là project trung gian, không phải workflow ComfyUI.
- Mỗi asset có `id`, `name`, `role`, `file`, `enabled`, `description`. STORYBOARD bật và đứng đầu. CHAR_01/ENV_01/PROP_01 giữ mã qua các lượt; tối đa 9 ảnh bật, gồm storyboard.
- Prompt trong project dùng `<Asset:STORYBOARD>`, `<Asset:CHAR_01>`... Đây là token của bước chuẩn bị, không phải token model. PREPARE.bat chuyển sang `<Picture n>` và nối đúng core LoadImage từ cùng danh sách bật. Không điền Picture bằng tay trong project.
- Không gán tên file giả rồi nhận là đã có. Có thể để file rỗng cho PREPARE mở hộp chọn ảnh trên máy. Nếu thiếu ảnh nhân vật và người dùng chọn dùng storyboard, đặt enabled=false, giữ description đủ rõ. Bộ chuẩn bị bỏ ảnh khỏi dây và chỉ dẫn dùng ngoại hình đã thấy trong storyboard. Không coi đó là character sheet hay khả năng khóa mặt tương đương.
- Local giới hạn 3–15 giây mỗi lượt (nháp 5–15 giây thường phù hợp hơn), luôn dưới trần 30 giây người dùng đặt. Shot trên timeline có thể 1 giây. Clip nguồn làm tròn lên lưới 17n+5 ở 24 FPS; không hứa cut chính xác từng frame. Tập 60 giây chia nhiều lượt, lưu continuity giữa lượt.
- Bố cục storyboard 1×N / 2×2 / 2×3 / 3×3... do AI chọn theo nội dung và độ rõ nhân vật; không cố định 3×3. Nhãn SHOT nằm ngoài vùng hình; mô tả hàng/cột, timeline và hành động khớp từng nhãn.
- Hai bước: bước false tạo nháp và lưu `.h3take`; bước true nạp latent + conditioning từ take để nâng latent 3D, refine, giữ màu và finishing. Bước 2 không tạo lại từ prompt mới. Khi đổi storyboard/sheet/prompt cần tạo take mới. Chọn take cụ thể khi có nhiều tác vụ, không mặc định latest luôn thuộc tập đang làm.
- Với hoạt hình 3D: giữ mặt / tỷ lệ / shading từ ảnh; LoRA người thật và trigger `r34l1sm` tắt. Không tự thêm Pika/Motion Repair hay gọi chúng là khóa mặt. Singularity có thiên hướng riêng, cần kiểm tra mẫu 3D trước khi sản xuất hàng loạt.
- Model/loader mới dùng safetensors qua core UNETLoader/CLIPLoader/VAELoader. Không hướng dẫn dùng GGUF, mmproj, H3StudioReferences hay các bản vá của bộ cài cũ.
- RTX 4060 Ti không có tính toán NVFP4 phần cứng như RTX 50; core dùng tính toán giải lượng tử. Mặc định PyTorch attention; không hứa sol-attn / Kitchen INT8 làm nhanh hơn khi chưa thử.
- Có nâng chất lượng cuối bằng latent 3D + refine + Color Transfer + Finishing/Clarity. FlashVSR là workflow khác; chưa có JSON đó trong nguồn được gửi nên không tự mô tả là đã tích hợp.
- Kiểm tra code, UI/schema, take round-trip và sampling GPU là các mức khác nhau. Không gọi render thành công nếu chỉ mở JSON hoặc kiểm thử CPU. Không chấm chất lượng / chọn cấu hình tốt nhất nếu chưa xem output thật.
