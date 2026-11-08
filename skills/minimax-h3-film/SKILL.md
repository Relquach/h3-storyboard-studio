---
name: minimax-h3-film
description: Chuyển nội dung phim tiếng Việt thành ảnh storyboard và prompt video tiếng Anh sau khi xác minh đúng task/model H3. Phân biệt Ref2V với I2V/FL2VA và FastH3 thử nghiệm; đọc subgraph, đối chiếu video lỗi, kiểm tra ảnh thật, ánh xạ ảnh và thời lượng. Phong cách dự án là 3D bán hiện thực Á Đông, pha nét búp bê.
---

# MiniMax H3 Film — v3.0.0 · 09/11/2026

Mục tiêu: nội dung Việt → storyboard đã duyệt → ảnh/prompt đúng workflow → duyệt nháp → dựng/nâng chất lượng nếu graph có bước đó. Trao đổi tiếng Việt; prompt tiếng Anh; giữ nguyên thoại đã chốt. Không hứa khóa mặt, cut đúng từng frame hay phát âm đúng tuyệt đối.

## 0. Storyboard trước, người dùng duyệt, prompt video sau

Đọc `references/storyboard-approval.md`. Đây là bước bắt buộc đã được người dùng yêu cầu: **tạo ảnh storyboard → gửi người dùng xem/sửa/duyệt → chỉ sau xác nhận mới dùng storyboard đã duyệt + nội dung phim để tạo prompt video**.

Giai đoạn A chỉ giao ảnh, prompt tạo ảnh nếu hữu ích, và tóm tắt shot/thời lượng. Dừng chờ duyệt; không viết prompt video “tạm”, không xuất video_prompt.txt hoặc queue. “Duyệt”, “ổn, làm tiếp”, “dùng bản này” gắn với ảnh cụ thể là đủ; không coi im lặng hay yêu cầu ban đầu là phê duyệt. Có sửa ảnh thì gửi bản mới để duyệt. Khi công cụ không tạo được ảnh, chưa được gọi storyboard đã duyệt.

Giai đoạn B chỉ bắt đầu sau lời duyệt thực; giữ đúng revision và kết hợp hình ảnh với nội dung/thoại đã chốt. Các bước tạo/bàn giao **prompt video** bên dưới chỉ áp dụng ở giai đoạn B. Nếu ảnh đầu I2V cần thay đổi trạng thái đáng kể so với storyboard, đưa ảnh bổ sung cho người dùng duyệt trước. Không bắt người dùng quản lý mã hay file trạng thái nội bộ.

## 1. Nhận diện task VÀ checkpoint trước khi soạn prompt

Đọc `references/workflow-mode-routing.md`. JSON mới nhất có ưu tiên hơn mẫu cũ. Đọc cả `definitions.subgraphs`, input ngoài group, dây nối và widget tại instance. Giá trị được dây điều khiển thắng widget nội bộ. Không nhầm #105 FastH3 là boolean nháp/nâng của workflow cũ.

Nếu có video lỗi: đọc metadata `workflow`/`prompt` khi khả dụng; xem đầu/giữa/cuối, thời lượng, kích thước thật. Metadata prompt là lượt đã render; JSON rời có thể là phiên sửa sau. Không nhận đã nghe tiếng nếu chỉ xem frame/metadata.

- **`singularity_original_ref2v`**: graph gốc `Finalworkflofacefixed...json`, #62 chọn Ref2V, #26 `MiniMaxH3ReferenceToVideo`, model Singularity Ref2VA. Nguyên storyboard và sheet là reference. Đọc `workflow-original.md`, `prompt-and-handoff.md` trong references; chỉ profile này dùng các ID gốc.
- **`fasth3_i2v_experimental`**: file mới `video_fastvideo_fasth3_i2v.json`, group #105 chứa #104 `MiniMaxH3ImageToVideo`, model FastH3 8-Step V2. Ảnh là first/last frame, không phải reference sheet. Đọc `references/fastvideo-fasth3-i2v.md`.
- **`verified_i2v`**: task I2V/FL2VA và checkpoint có tài liệu hỗ trợ đúng task. Bàn giao ảnh mở đầu sạch cho từng shot; last_frame tùy chọn là kết thúc shot.
- **Không nhận diện được**: vẫn lập truyện/storyboard, nhưng chưa nhận prompt sẵn sàng render; báo đúng phần chưa xác minh.

**Điểm chặn:** model card chính thức FastH3 V2 ghi T2AV; FL2VA và Ref2VA chưa được distill. Note template nói FL2VA mâu thuẫn với nguồn này. Không coi cổng ảnh của node là chứng nhận model hỗ trợ I2V. Không đổi node sang Ref2V rồi giữ FastH3 như một cấu hình sản xuất đã kiểm chứng.

Muốn nguyên storyboard + sheet → ưu tiên đề xuất Ref2V với model hỗ trợ, như graph Singularity cũ trong gói. Muốn giữ FastH3 hiện tại → chỉ đưa phép thử I2V từng ảnh sạch và nêu giới hạn. Không âm thầm đổi workflow/model, cài node hay queue. Chuyển profile không xảy ra chỉ bằng đổi prompt.

## 2. Đọc lựa chọn đã chốt, chỉ hỏi phần thiếu

Không hỏi lại người, áo quần, style, tỷ lệ, ánh sáng đã biết. Hỏi gộp ảnh 1/2/... là ai/môi trường/đạo cụ nào, đặc điểm phải giữ, thoại/thời lượng chưa rõ và phần AI được tự đề xuất. Khi được giao tự chọn, tự quyết và nêu giả định ngắn.

Style dự án: **semi-realistic 3D / CGI beauty render, East Asian character design, subtle doll-like stylization**. Giữ thể tích mặt, vật liệu 3D, da shading mềm có subsurface scattering, mắt biểu cảm, tóc chi tiết và ánh sáng điện ảnh; không tự chuyển thành diễn viên người thật, anime 2D hoặc cartoon phóng đại. Ảnh và prompt phải cùng style.

Theo dõi CHAR_01, ENV_01, PROP_01 cùng mặt/tóc/tuổi thể hiện/thân hình/trang phục, tay cầm đồ, hướng nhìn, trục máy, ánh sáng và trạng thái đầu–cuối. Không gán nhân vật đã có cho vai khác nếu chưa được người dùng xác nhận. Sheet chỉ giữ danh tính ở khâu tạo ảnh shot nếu workflow video không có đường reference sheet riêng; last_frame không phải slot sheet.

## 3. Một shot plan sinh timeline và setting

Đọc `references/storyboard-and-timing.md`, `references/i2v-authoring.md`. Tự chọn shot theo hành động/cảm xúc/thoại; không chia đều giây hay cố định 3×3. Chọn lưới sau shot: 2×2, 2×3… đọc trái→phải, trên→dưới. Không thêm cảnh để lấp ô.

Mỗi shot có ID/nhãn/vị trí ô, thời lượng **dựng** và **render**, trạng thái đầu/hành động/trạng thái cuối, camera, người có mặt, đạo cụ, âm thanh. Prompt tính thời gian từ đầu lượt render tương ứng, không từ timeline tập. Trần người dùng 30 giây/lượt không chứng minh model chạy tốt 30 giây. Vùng 5–15 giây của H3 gốc không tự xác minh FastH3 I2V.

Workflow mới: giây ở #105 `duration`; #105:107 quy đổi 24 FPS → 17n+5. 5 giây→124 frame→5.167 giây; 15 giây→362 frame→15.083 giây. Prompt 15 giây không ghi đè duration=5. Shot dựng 0.9–1 giây có thể lấy từ nguồn dài hơn nhưng phải kiểm tra động tác có nằm trọn đoạn cắt; không tua nhanh tùy tiện để ép đủ nội dung.

Không tự cắt bỏ thoại để vừa thời gian. Đo thời lượng đọc thật khi có âm thanh; không áp từ/giây tiếng Anh cho tiếng Việt. Với thoại/phone narration chính xác xuyên nhiều shot, đề xuất track tiếng riêng để dựng liền mạch; không nhận đã tạo tiếng/lip-sync. Native audio vẫn là một lựa chọn thử nghiệm, không hứa đúng từng chữ/giọng.

## 4. Tạo ảnh đúng vai trò

Khi được yêu cầu vẽ storyboard, tạo ảnh thật bằng công cụ ảnh được phép, gắn sheet đúng và xem lại kết quả; không chỉ giao prompt nếu có công cụ. Không dùng Topview. Không tự vẽ nhân vật điện ảnh bằng Python. Script đọc metadata, lập bảng và kiểm tra frame kỹ thuật được dùng.

- **Storyboard duyệt:** grid có nhãn SHOT ở caption strip riêng, một khoảnh khắc rõ/ô; đúng mặt, trang phục, tay, trạng thái, ánh sáng và đủ nội dung. Tỷ lệ ô không đồng nghĩa tỷ lệ trang.
- **Ref2V:** nguyên trang vào reference đã xác minh; sheet vào slot phụ thật có. Prompt yêu cầu các shot toàn khung hình tuần tự, bỏ lưới/nhãn; vẫn phải xem nháp.
- **I2V:** thêm ảnh `SHOT_XX_START.png` toàn khung hình, không lưới/nhãn/viền/nhiều góc mặt, đúng tỷ lệ video. Ảnh đầu là **trước hành động**: điện thoại còn trên tay trước cú đặt/đập, tay chưa chỉ trước động tác chỉ. Last_frame chỉ nạp nếu có ảnh kết thúc tương thích đã duyệt.
- Có thể lấy ô sạch từ storyboard khi đủ nét và không cắt mất người/đồ; nếu không, tạo lại ảnh shot dùng cùng sheet/bố cục. Không kéo giãn để đổi tỷ lệ hay coi phóng crop là tăng chi tiết. Không nhận frame nén từ video lỗi là ảnh nguồn đã duyệt.

Tên ảnh chưa tạo phải ghi **tên dự kiến — chưa có file**. Thiếu storyboard gốc vẫn cập nhật được skill/plan/prompt, nhưng chưa nhận đã xuất ảnh shot sạch. Không phát sinh lượt tạo ảnh khi yêu cầu hiện tại chỉ là sửa skill.

## 5. Prompt theo task, không có ảnh ảo

**Ref2V:** resolve bảng asset→loader→socket→bật/bypass→Picture theo dây thật; bỏ ảnh giữa thì đánh số lại. Graph Singularity gốc: #27 storyboard, #28/#93/#104/#122/#135 phụ; #93 đang bật phải nhắc bypass khi không dùng. Prompt ở #70. Không áp bảng này cho FastH3.

**I2V:** prompt ở ngoài group #105; ảnh #136 vào first_frame, last_frame đang trống. Không gọi `<Picture 2>` là sheet không được nối. Viết “the adult man in the supplied opening frame” và mô tả nhận diện ngắn. First/last không biến thành reference sheet; sáu tiêu đề của mẫu Ref2V không bắt buộc ở I2V.

Ưu tiên prompt I2V ngắn, tự đủ: style/chủ thể từ frame đầu → hành động → kết thúc → một camera movement → audio/thoại vừa thời gian → vài ràng buộc thiết yếu. Mặc định một lượt một shot liên tục; nhiều cut chỉ là phép thử được nêu rõ. Không dùng lệnh “remove grid” thay ảnh đầu sạch.

Không thêm Turbo LoRA vào FastH3 8 bước vốn đã distill. Các giá trị `res_multistep`, `simple`, 8 bước, shift_video=10/shift_audio=3 là setting đang lưu, không phải chứng nhận I2V. Không sửa sparse ngẫu nhiên để chữa grid/thiếu ảnh. Realism #134 và trigger chỉ được xét khi graph thật sự có node đó.

## 6. Bàn giao và chặn lỗi trước khi nhận sẵn sàng

Giai đoạn A: gửi storyboard và nhịp dự kiến để người dùng duyệt; chưa giao prompt video. Giai đoạn B sau duyệt: trả profile/task/model và giới hạn → ảnh đã duyệt → bảng shot/render/dựng và bảng nạp ảnh → một prompt hoàn chỉnh/lượt → setting/node và trình tự đúng profile → checklist duyệt nháp. Không bắt người dùng chạy PREPARE/helper/cài lại hệ thống.

FastH3 hiện tại: #136 ảnh shot sạch → #142/#141 lấy kích thước → #105 prompt/duration/seed → #92 lưu. #142 chỉ cấp **kích thước**, ảnh gốc #136 vẫn đi thẳng first_frame. Tỷ lệ ảnh đầu quyết định tỷ lệ video; widget width/height cũ không thắng dây. Graph này không có #70, sheet slot, H3TakeLoad, pass 2 hoặc upscale; không hướng dẫn #105=false/true như graph cũ.

Codex có thể dùng `scripts/audit_workflow.py` để đọc JSON + metadata video. Chỉ gán `--image-role storyboard_grid` sau khi đã xem ảnh/video. `scripts/compile_handoff.py` chỉ dành cho profile Singularity gốc. Helper không sửa JSON, cài dependency hoặc queue.

Không nhận bàn giao sẵn sàng nếu: task/model chưa phù hợp mà không nói thử nghiệm; grid/sheet vào first_frame; token ảnh chưa nối; prompt quá thời lượng; ảnh đầu đã hoàn tất hành động; tỷ lệ sai; thoại thiếu thời gian; dùng ID cũ. Gắn trạng thái `needs_clean_frames`/`experimental_checkpoint` hoặc đề xuất Ref2V đúng model.

Nháp sai người/nội dung/đạo cụ thì sửa nguồn và tạo lại trước upscale. Sharpen không chữa cốt truyện. Không nhận đã nghe, render GPU, đo tốc độ, chọn cấu hình tốt nhất hay khóa mặt nếu chưa thực hiện. Giữ nguyên JSON người dùng trừ khi được yêu cầu sửa; không tự đăng JSON, video, ảnh mới lên GitHub.
