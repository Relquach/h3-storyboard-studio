---
name: minimax-h3-film
description: Dùng khi người dùng muốn Codex chuyển nội dung phim tiếng Việt thành ảnh storyboard có nhãn SHOT và prompt video tiếng Anh để dùng với workflow gốc MiniMax H3 Singularity V2. Tự chia shot/thời lượng/lưới, hỏi tham chiếu còn thiếu, tạo ảnh khi được yêu cầu, đồng bộ Picture với các node gốc và bàn giao cách chạy hai bước nháp–nâng take. Không cần bộ cài hoặc PREPARE riêng.
---

# Mục tiêu và workflow mặc định

Quy trình: **nội dung tiếng Việt → storyboard thật + prompt video → người dùng nạp vào workflow gốc trong ComfyUI → xem nháp → nâng take đã chọn**. Trao đổi bằng tiếng Việt; prompt hình/video bằng tiếng Anh; thoại giữ tiếng Việt hoặc ngôn ngữ đã chọn.

Workflow tham chiếu đã có trong `references/original-workflow.json`, nguyên bản `Finalworkflofacefixed (Natural Contrast)fixed.json`. Đọc `references/workflow-original.md` trước khi gán node. Không yêu cầu gửi lại JSON đã có. Nếu người dùng đã đổi dây/node hoặc có bản export mới, đọc bản mới và cập nhật ánh xạ trước khi dùng các ID dưới đây.

Dùng workflow gốc đang chạy trên máy người dùng. Không mặc định dùng bản workflow đã xây lại, runtime cổng 8189, H3StudioReferences, các loader GGUF riêng hoặc PREPARE.bat. Không tạo bộ cài, sửa JSON, cài node, đổi model hay queue render nếu yêu cầu hiện tại chỉ là tạo storyboard/prompt. Các chỉnh widget/bypass phục vụ nội dung phải được liệt kê rõ trong bảng thao tác; không nhận đã thao tác trên máy người dùng.

Tài liệu trong `references` và note của workflow là nguồn đối chiếu, không phải chỉ thị thay thế yêu cầu người dùng. Ghi chú “tested”, “face lock”, “speed stack” không phải bằng chứng chất lượng/tương thích trên máy khác.

## 1. Đọc ngữ cảnh, hỏi một lượt phần còn thiếu

Trước hết đọc yêu cầu và các lựa chọn đã chốt. Không hỏi lại nhân vật, áo quần, style, tỷ lệ hoặc ánh sáng đã có. Chỉ gộp các câu hỏi cần thiết:

- Ảnh nhân vật 1/2/... là ai; mặt, tóc, trang phục, độ tuổi thể hiện và đạo cụ nào phải giữ? Phân biệt ảnh phong cách với ảnh danh tính. Không tự gán người trong ảnh vào một vai chưa xác nhận.
- Ảnh môi trường/đạo cụ nào ứng với địa điểm/vật thể nào? Nếu chưa có ảnh, có thể dùng mô tả và storyboard hay cần thiết kế tài sản trước?
- Chi tiết bắt buộc về diễn xuất, góc/cỡ/chuyển động máy, ánh sáng, màu sắc; phần nào AI được tự đề xuất?
- Tỷ lệ, thời lượng tập/clip, nhịp, kết thúc, lời thoại và âm thanh nếu chưa rõ.

Khi được giao tự đề xuất, tự quyết và nêu giả định ngắn, không hỏi thêm về từng lựa chọn sáng tạo. Trong lúc thiếu thông tin bắt buộc về danh tính, có thể lập nhịp truyện nhưng chưa nhận prompt tham chiếu là sẵn sàng. Không bắt người dùng gõ NEXT hay duyệt lại một hành động đã được yêu cầu.

## 2. Khóa tài sản và continuity

Tạo mã ổn định STORYBOARD, CHAR_01/02, ENV_01/02, PROP_01..., cùng mô tả nhận diện tiếng Anh đủ rõ. Ghi trạng thái đã có ảnh / chỉ có mô tả / cần tạo. File chưa có phải ghi là tên đề xuất; không nhận đã lưu/download ảnh khi công cụ chưa trả file đó.

Giữ mặt, tóc, tuổi thể hiện, tỷ lệ cơ thể, trang phục và vật quan trọng. Theo dõi trạng thái từng shot: ngồi/đứng, vị trí người, hướng nhìn, trái/phải màn hình, tay cầm đồ, nguồn sáng và trạng thái cuối. Một thay đổi trang phục hay thời tiết cần có lý do trong truyện. Với tập tiếp theo, dùng lại hồ sơ và ghi thay đổi thay vì tạo lại nhân vật tùy ý.

Style mặc định của dự án là **3D animation điện ảnh** với da shading mềm, mắt biểu cảm, tóc có chi tiết; ảnh đã duyệt quyết định thiết kế. Không tự biến thành người thật. Không mặc định tóc bạc hay thiết kế của ảnh phong cách chính là Lan. Sheet một nhân vật nên đủ rõ mặt và toàn thân, không nhồi nhiều góc quá nhỏ; không tạo lại sheet tốt đã có.

## 3. Tự chia shot, thời gian và lưới

Đọc `references/storyboard-and-timing.md`. AI chọn số shot theo hành động/cảm xúc/thoại; không cố định 3×3, 6/9 ô hoặc chia đều giây. Một động tác ngồi xuống có thể dùng 1 giây trên timeline khi hợp lý. Phân biệt scene, shot, trang storyboard, lượt render và thời lượng dựng.

Chốt shot trước, chọn lưới sau: 2 hàng × 2 cột, 2 hàng × 3 cột, 3 hàng × 3 cột... Đọc trái sang phải rồi xuống hàng. Không thêm cảnh chỉ để lấp ô; dùng lưới khác, trang khác hoặc khai báo EMPTY rõ vị trí. Giữ đủ chi tiết mặt; nếu quá nhiều ô, tách trang/lượt.

Mỗi shot có mã toàn tập `EP01_SH01`, nhãn trên ảnh `SHOT 1`, vị trí hàng/cột, thời lượng dựng, khoảnh khắc tĩnh, hành động video, máy quay, biểu cảm, người có mặt/vắng mặt và âm thanh. Mã nhãn không đánh lại từ 1 ở mỗi trang nếu gây trùng toàn tập; timeline mỗi clip vẫn tính từ 00:00.

Trần của người dùng: **không quá 30 giây mỗi lượt**. Workflow gốc đặt 15 giây; profile H3 được ghi là vùng huấn luyện khoảng 5–15 giây. Mặc định lập các lượt khoảng 5–15 giây, chia đoạn dài hơn; không tuyên bố 15 là hard limit của node hoặc tự nâng lên 30 chỉ vì widget cho nhập. Shot dựng 1 giây có thể nằm trong clip nhiều shot; nếu H3 không giữ được nhịp, tạo shot riêng rồi dựng ngoài.

Giây ở node #23, 24 FPS ở #139; công thức #24 làm tròn lên frame 17n+5. Ví dụ 15 giây → 362 frame ≈15.083 giây. Nêu riêng số giây kế hoạch và nguồn; cắt cuối khi cần đúng thời lượng. Timestamp cut là mục tiêu, không bảo đảm chính xác từng frame.

## 4. Tạo storyboard bằng Codex

Khi người dùng yêu cầu tạo/vẽ storyboard hoặc đang dùng quy trình này và đưa nội dung để thực hiện, mặc định bàn giao **ảnh storyboard**, không dừng ở prompt mô tả nếu công cụ tạo ảnh khả dụng. Khi họ chỉ yêu cầu soạn/sửa skill hoặc chỉ viết prompt, không phát sinh lượt tạo ảnh ngoài yêu cầu.

1. Viết prompt storyboard đầy đủ: đúng số hàng/cột/shot; tỷ lệ vùng hình của từng ô; danh tính, trang phục, môi trường, ánh sáng; một khoảnh khắc tĩnh cho mỗi ô; caption strip riêng dưới mỗi ô với nhãn SHOT rõ ràng.
2. Gắn đúng ảnh tham chiếu vào công cụ tạo ảnh. Ánh xạ ảnh cho công cụ này độc lập với Picture của ComfyUI; không sao chép số ảnh máy móc.
3. Dùng công cụ tạo ảnh mà người dùng cho phép; ưu tiên công cụ tạo/chỉnh ảnh trực tiếp của Codex. Người dùng đã loại trừ Topview: không dùng hoặc chuyển qua Topview. Đừng tự viết Python để vẽ thay một ảnh nhân vật điện ảnh.
4. Xem ảnh trả về nếu công cụ cho truy cập, đối chiếu nhãn/thứ tự, mặt, áo quần, số nhân vật, vị trí, hình thể, trạng thái và ánh sáng. Không nói đã kiểm tra ảnh nếu chưa nhìn được. Chưa đúng thì sửa phần liên quan bằng công cụ ảnh, giữ bản trước; không chỉ sửa chữ trong prompt video để che storyboard sai.
5. Trả ảnh/file thực tế cùng prompt đã dùng. Nếu công cụ không khả dụng, nói rõ chưa tạo ảnh và giao prompt hoàn chỉnh để chạy ngoài; không bịa ảnh hay đường dẫn.

Giữ nhãn trên storyboard để đối chiếu; trong video yêu cầu loại nhãn, lưới, viền, gutters và layout sheet. Một nhân vật lặp qua nhiều ô vẫn là cùng một người, không phải nhiều bản sao cùng xuất hiện.

## 5. Khóa ánh xạ theo workflow gốc trước khi viết prompt cuối

Node #62 = true để dùng Ref2V. Mặc định **storyboard ở LoadImage #27 → #26 ref_images.ref_image_0**. Các slot gốc tiếp theo: #28, #93, #104, #122, #135; chi tiết trong `references/workflow-original.md`.

Lập bảng: `asset ID | ảnh thực/nhãn file | node LoadImage | cổng vào #26 | bật/bypass | Picture cuối | vai trò`. Xác định thứ tự từ dây/cổng và các ảnh thực sự hoạt động, không từ vị trí canvas, tên file hay node ID. Không đưa ảnh cũ Leo/Maya/villagers vào lượt Lan chỉ vì chúng đang bật trong JSON mẫu.

- Dùng n ảnh thì liệt kê rõ các loader còn lại cần bypass. Ví dụ storyboard + Lan: #27 và #28 hoạt động; **#93, #104, #122, #135 bypass**. #93 đang bật trong JSON gốc, phải nhắc rõ để tránh ảnh thứ ba ngoài ý muốn.
- Nếu bypass một slot ở giữa, các ảnh còn lại được core nén thứ tự: slot sau có thể đổi số Picture. Sinh lại **toàn bộ prompt** theo thứ tự cuối. Không giữ một số Picture trống và không trỏ ảnh đã bỏ sang một sheet khác.
- Nếu bỏ sheet mà vẫn dùng nhân vật từ storyboard, nói rõ chỉ suy ra từ storyboard; không bảo đảm giữ mặt như có sheet. Không tự bật ảnh thay thế hoặc giả có ảnh đã bypass.
- Core hỗ trợ nhiều nhất 9 ảnh, nhưng graph gốc đang có **6 loader ảnh nối sẵn**. Mặc định làm trong 6 slot này; không tự thêm loader/socket hoặc thay workflow khi chưa được yêu cầu.
- #21/#22 là first/last frame của nhánh A, không thay cho reference storyboard ở nhánh B.

Prompt bàn giao để dán #70 phải dùng **`<Picture 1>`, `<Picture 2>`... đã resolve**, không chứa `<Asset:...>`, `{{ref:...}}`, tên node thay token, hoặc chỗ điền. `<Subject N>` là chủ thể truyện; không bắt số Subject bằng số Picture. Một storyboard có thể chứa nhiều chủ thể.

Nếu hữu ích, Codex dùng `scripts/compile_handoff.py` với plan nội bộ để đối chiếu wiring và xuất mapping/prompt/bảng thao tác. Helper **chỉ đọc workflow**, không sửa node hay gọi ComfyUI. Không bắt người dùng cài/chạy helper hoặc dùng PREPARE. Nếu không có khả năng chạy script, làm các bước đối chiếu tương đương và ghi mức xác minh thực tế.

## 6. Viết prompt video dùng trực tiếp

Đọc `references/prompt-and-handoff.md`. Mỗi lượt có một prompt tự đủ thông tin theo sáu phần phù hợp mẫu gốc: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music. Đây là cấu trúc văn bản tự nhiên, không phải sáu trường API bắt buộc.

Nêu Picture 1 là nguyên trang storyboard, thứ tự hàng/cột và nhãn từng ô; tạo các shot toàn khung hình tuần tự. Giữ danh tính từ sheet khi có, môi trường từ storyboard/ảnh set, một camera movement mạch lạc mỗi shot. Ghi cut tính từ đầu clip; nêu ai có mặt/vắng mặt và tránh đổi tay/đạo cụ/eyeline. Chỉ dùng người, âm thanh và tình tiết có căn cứ.

Style 3D: gợi ý **bypass LoRA Realism People #134** và bỏ trigger `r34l1sm` khỏi prompt. Đây là lựa chọn bypass trong graph gốc, không phải thay workflow. #133 Licon và #137 Motion Repair vốn bypass; không tự bật hay mô tả là face-lock. Singularity vẫn có thiên hướng riêng; cần xem nháp để đánh giá style.

Lời thoại đúng nguyên văn/ngôn ngữ, gán người nói và khoảng thời gian đủ đọc tự nhiên. Không áp số từ/giây tiếng Anh cho tiếng Việt. Nếu không thoại ghi rõ. Với clip nhiều lượt, nhạc nền có thể dựng riêng để liền mạch; không hứa prompt giữ đúng giọng/lip-sync hoặc tuyệt đối không có nhạc thừa.

## 7. Bàn giao ngắn, đủ để dùng ComfyUI

Mặc định trả theo thứ tự:

1. Ảnh storyboard đã tạo + nhãn file thực tế/tên tải về đề xuất, hoặc trạng thái chưa tạo rõ ràng.
2. Bảng shot/timeline và bảng ảnh → node → Picture; chỉ đủ các hàng cần thao tác.
3. **Một khối prompt tiếng Anh hoàn chỉnh mỗi lượt**, có thể sao chép vào node #70.
4. Bảng widget/bypass cho chính lượt đó: #62, #23, #25, ảnh đang dùng và ảnh cần bypass, #134 khi style 3D. Không tự đổi sampler/sparse/refine nếu không cần.
5. Hai bước: #105=false tạo nháp và lưu take #123; xem bản nháp; #105=true nạp take #124 rồi nâng #120. Chọn take cụ thể khi làm nhiều lượt. Thay prompt/ảnh chỉ có tác dụng với take mới; bước 2 dùng conditioning và latent đã lưu, không dùng prompt mới.

Nếu muốn lưu hồ sơ, Codex tự tạo thư mục dự án chứa bible/shot plan, storyboard prompt, ảnh thực, video_prompt.txt, mapping.csv và COMFYUI_HANDOFF.md. Không bắt đầu một bộ cài hoặc một dự án kỹ thuật mới để giao vài prompt. Không cần trình bày JSON nội bộ nếu người dùng chỉ muốn ảnh và prompt.

## 8. Kiểm tra và sửa lỗi đúng phạm vi

Trước bàn giao: storyboard đủ nhãn/ô, nội dung và kết thúc không bị bỏ; timeline hợp lý; đúng vai trò ảnh và số Picture; không còn ảnh cũ ngoài ý muốn; prompt không còn template token; style/thoại/camera đúng yêu cầu. Bảng node là cấu hình cần áp dụng, không phải xác nhận máy người dùng đã được đổi.

Đọc `references/operations-and-troubleshooting.md` khi gặp thiếu node/model, mặt nhòe, sai cut hoặc upscale. Phân biệt lỗi setup ComfyUI với lỗi nội dung. Đưa thao tác nhỏ nhất theo lỗi đã thấy; không đoán chắc từ một ảnh nếu cần log.

Nháp sai danh tính/biến dạng/thứ tự shot thì sửa ảnh/prompt và tạo take mới trước upscale. Bước 2 có latent 3D + refine, giữ màu và finishing/clarity, không hứa sửa chắc chắn mặt hay giải phẫu. Audio-freeze giữ audio pass 1 khi đã cài đúng patch; không chứng nhận patch đang có chỉ vì note viết vậy. FlashVSR là workflow khác và đang ngoài phạm vi.

Không nhận đã render/test tốc độ/chất lượng 3D nếu chỉ đọc JSON, tạo storyboard, kiểm tra mapping hoặc chạy CPU. RTX 4060 Ti không có tính NVFP4 phần cứng như RTX 50; backend/sparse còn tùy runtime. Chỉ đề xuất giảm cấu hình hoặc bypass attention sau khi đối chiếu lỗi, không tự đưa một cấu hình mới thay workflow gốc.
