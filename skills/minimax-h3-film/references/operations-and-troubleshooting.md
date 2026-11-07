# Vận hành workflow gốc và các lỗi thường gặp

## Hai bước

1. Chọn nhánh reference #62=true. Nạp đúng storyboard / sheets, bypass loader thừa; dán prompt cuối #70; đặt giây #23 và tỷ lệ #25. BƯỚC #105=false → Queue.
2. Xem nháp về đúng người, trang phục, bối cảnh, diễn xuất, thứ tự shot, camera và âm thanh. Chưa đúng thì sửa đầu vào/prompt và tạo take mới, không mặc định upscale sẽ sửa mặt.
3. Khi đã duyệt, ghi tên take #123 đã lưu. Đặt #105=true, chọn đúng take ở #124 → Queue. #120 dùng **latent + conditioning từ take**, không dùng prompt mới #70. Chọn take cụ thể khi nhiều tập/lượt; `latest` có thể là một tác vụ khác.
4. Bản nâng qua ColorTransfer #142 ở bước2, finishing #144 và clarity #147, CreateVideo #139 rồi SaveVideo #43. Đây là latent 3D + diffusion refine + xử lý màu/nét, không phải FlashVSR hoặc công cụ khóa mặt.

Audio-freeze là patch của PlagueKind giúp giữ audio pass1 khi refine untiled; phải kiểm tra bản cài thực sự có patch trước khi khẳng định. Không hứa giữ lip-sync tuyệt đối. Không đổi model/Turbo/attention giữa take và upscale mà không xem tương thích. Thay sheet/prompt/ảnh storyboard cần một take mới nếu muốn các thay đổi đó có hiệu lực.

## Ảnh lỗi setup gần nhất của người dùng

Ảnh báo thiếu **PixaromaMonitor, PixaromaRunTimer**, model **h3-realism-people-t2v-i2v-r2v.safetensors** và **minimax_h3_video_vae_int8_convrot.safetensors**. Đây là trạng thái quan sát ở thời điểm gửi ảnh, không phải chẩn đoán vĩnh viễn cho mọi máy.

| Thiếu | Node gốc | Cách xử lý đúng phạm vi |
|---|---|---|
| PixaromaMonitor / PixaromaRunTimer | #96 / #95 | Pack https://github.com/pixaroma/ComfyUI-Pixaroma. Cài pack vào **đúng ComfyUI hiện dùng** rồi khởi động lại. Đây là monitor/timer, không tạo danh tính hay hình ảnh. Nếu người dùng muốn bỏ node trang trí, chỉ bỏ các node đó trong một bản sao; không tự viết workflow mới |
| Realism People LoRA | #134 | Giữ cấu hình người thật: tải đúng file vào models/loras. Làm3D animation: đề xuất bypass #134, bỏ `r34l1sm` khỏi #70; giữ Turbo #10. Không coi Realism People là LoRA khóa mặt |
| Video VAE INT8 | #3 | Giữ đúng gốc: tải đúng file vào models/vae. Nếu đã có H3 video VAE FP16 hợp lệ, có thể chọn file đó trong #3 như một thay đổi được nêu rõ; không đổi tên FP16 thành INT8 và không dùng audio VAE thay video VAE |

Nguồn model đã có trong tài liệu kèm workflow:

- Realism: https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA/resolve/039cc8579d7aa357a882d7f4111b25da4f72dccc/h3-realism-people-t2v-i2v-r2v.safetensors
- Video VAE INT8: https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/54472221d27c695fca9621b0c3ed52f06c4af707/vae/minimax_h3_video_vae_int8_convrot.safetensors

Sau cài/tải, khởi động lại backend và refresh giao diện; ảnh cảnh báo không xác nhận đang dùng cổng nào. Skill này dùng workflow gốc trong ComfyUI người dùng chọn, không ép chạy runtime cổng8189. Không hướng dẫn cài lại mọi model chỉ vì một file thiếu. Không tự tải/cài nếu nhiệm vụ hiện tại chỉ là sáng tác.

## Sửa lỗi nội dung / chất lượng

| Biểu hiện | Kiểm tra trước / hướng sửa nhỏ nhất |
|---|---|
| Picture2 nhưng chỉ1ảnh | Bảng ảnh hoạt động và node bypass; xóa tham chiếu sheet đã bỏ khỏi prompt, dùng storyboard để chỉ đúng chủ thể nếu đã được chọn; không tự lấy ảnh khác để lấp chỗ |
| Mặt nhầm, trộn người | Ảnh loader có đúng người; slot thừa #93 còn bật không; Picture có bị dồn số sau bypass; Subject có mô tả mâu thuẫn; mặt trong storyboard/sheet đủ lớn không |
| Video thành lưới / nhiều bản sao | #62 có true; storyboard có ở Ref2V thay vì first frame; prompt có nêu sequential full-frame, row-major và exclude grid; không yêu cầu nhiều nhân vật chỉ vì sheet nhiều góc |
| Close-up nền trắng | Sheet có đang bị dùng như first frame; mô tả bối cảnh và vị trí camera ở close-up; nhắc một người duy nhất, bỏ sheet background |
| Biến dạng chuyển động nhanh | Trạng thái bắt đầu/kết thúc rõ, thời gian đủ, một hành động chính, camera không xung đột; tạo nháp shot khó trước; chia beats hoặc sửa riêng shot khi cần |
| Mặt nhòe | Pixel mặt trong ảnh, số ô quá nhiều, ref area #26, mức nháp, nén xuất; thêm sheet/crop mặt chỉ khi mapping được cập nhật; không hứa sharpen hay tăng bước chữa giải phẫu |
| Đổi mặt/miệng sau refine | Denoise/sigmas pass2, đúng take/model, audio-freeze có thật chưa; giảm repaint sau khi so sánh; sửa pass1 nếu mặt vốn sai |
| Sai thứ tự hoặc thiếu shot | Nhãn trên ảnh, panel map và cut timeline; số beats có quá nhiều so với giây; prompt có đủ người/vị trí sau cut; nếu cần tách lượt rồi dựng, không bắt cắt lẻ tất cả mặc định |
| Đổi style thành live-action | Sheet/storyboard/style block; Realism LoRA #134 và trigger; model nền có thiên hướng; không chỉ thêm một câu “3D” vào prompt xung đột |
| Nét quá gắt / flicker | So bản nháp và bản nâng; Finishing #144 / Clarity #147 / ColorTransfer #142; giảm xử lý có đối chiếu, không tự thêm nhiều sharpen hoặc face restoration |
| OOM / backend kernel | Xin đúng log, đối chiếu GPU/PyTorch/CUDA; sau đó đề xuất giảm refs/ref area, kích thước hoặc chia chunk; bypass sparse/backend nếu chính nó không hỗ trợ. Không lấy lời hứa tốc độ RTX5070Ti áp cho4060Ti |

Không biến bảng giả thuyết thành kết luận chắc chắn. Phân biệt thiếu node, thiếu model, ảnh chưa chọn, import lỗi, OOM và sai nội dung; chỉ hỏi log/ảnh hoặc export mới khi nó cần để quyết định bước tiếp theo. Chỉ ghi đã render/benchmark khi có output và số đo thật.
