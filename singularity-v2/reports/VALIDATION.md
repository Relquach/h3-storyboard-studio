# Trạng thái kiểm tra

Bản 1.0.0 là bộ cài thử nghiệm dẫn xuất từ workflow được cung cấp. Không gọi đây là một bản đã render/benchmark GPU thành công.

Đã thực hiện:

- 21 kiểm tra logic: sinh chung prompt và dây từ asset IDs, chỉ storyboard không để sót Picture 2, bỏ asset ở giữa không đảo danh tính, giới hạn ảnh, enum/aspect và frame alignment, file-copy không chạm bản gốc, lưu/nạp take theo dây gốc, download tiếp tục và SHA-256, bảo toàn file model khác hash, chống archive traversal và patch audio có điều kiện.
- Khởi động ComfyUI **0.43.1** thật bằng torch **2.10.0+cpu** trong môi trường thử riêng; nạp hai subpack PlagueKind và hai pack local. Ghi nhận 1.036 node trong object_info; không lấy số node làm bằng chứng render.
- Chromium mở frontend **1.57.4**, nạp workflow từ PREPARE, chuyển sang API prompt bằng graphToPrompt thật. Kiểm tra hai ảnh (storyboard + sheet) và một ảnh (storyboard-only): không còn setup issues, đúng số dây ảnh, không có Picture 2 khi chỉ một ảnh. Media dùng ảnh trắng nhỏ làm fixture, không phải ảnh Lan hay chứng nhận chất lượng 3D.
- API prompt từ frontend qua execution.validate_prompt của core thật, kiểm tra cả hai giá trị bước false/true và trường hợp một/hai ảnh. Xem live-schema-validation.json. Dùng các file rỗng mang đúng tên model để kiểm tra enum/schema; **không đọc trọng số từ các file này**. Đây là kiểm tra hợp lệ prompt, không phải sampling.
- Lưu và đọc `.h3take` bằng đúng node local, tensor CPU thật: video, audio, embedding, reference latent và tuple metadata khôi phục chính xác. File take dùng safetensors + JSON; không thử GPU hoặc take lớn.
- Finishing CPU: đúng shape, giá trị hữu hạn trong [0,1], strength=0 trả nguyên ảnh. Không đo chất lượng cảm nhận hay temporal flicker trên clip thật.
- Audio-freeze khớp đúng block untiled của commit PlagueKind đã khóa; áp dụng trên mã thật, có backup, chạy lần hai không patch trùng; mã đã patch compile được. Giữ đường dẫn model shared làm is_default vì upscaler tìm ở thư mục đầu tiên.
- Sáu URL model đã khóa revision được truy cập bằng range 8 byte; dung lượng Content-Range khớp manifest và kích thước header safetensors hợp lệ. SHA-256 lấy từ metadata LFS upstream và được installer kiểm tra khi tải/reuse; chưa tải và hash đầy đủ 43.47 GB model ở đây.
- Python compile và parser PowerShell thật kiểm tra launch.ps1. Không tương đương chạy cửa sổ Windows Forms hoặc cài Windows thật.

Chưa thực hiện:

- Không có NVIDIA GPU trong môi trường này. Chưa load/forward encoder, DiT, VAE hoặc latent upscaler bằng trọng số thật.
- Chưa chạy cả bộ cài trên Windows Portable thật, chưa render trên RTX 4060 Ti 16 GB / RAM 32 GB, chưa đo thời gian/VRAM/pagefile hoặc chọn preset tốt nhất.
- Chưa xem output 3D của Lan từ Singularity V2; chưa xác nhận mức giữ mặt, môi trường, thứ tự shot, chuyển động nhanh hoặc lip-sync.
- Không tích hợp FlashVSR theo lựa chọn hiện tại của người dùng. Không cài các pack/VAE/LoRA tùy chọn vào cấu hình mặc định.

Báo cáo số liệu hiện có chỉ nói về kiểm tra CPU/schema; không dùng thời gian trên video tác giả làm số đo của máy người dùng. CHECK.bat trên máy đích kiểm tra runtime, model size, ảnh và mapping trước khi Queue; installer kiểm tra checksum tải. Một lần render thử thật vẫn cần để xác nhận toàn bộ đường chạy GPU.
