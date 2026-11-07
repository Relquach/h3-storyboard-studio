# Bổ sung phần còn thiếu — workflow H3 gốc

Bản1.0.0, dành cho **ComfyUI Windows Portable hiện có**, theo ảnh lỗi mới nhất của người dùng.

## Dùng ngay

1. Giải nén ZIP vào thư mục có quyền ghi, ví dụ Downloads.
2. Nhấp **CAI_PHAN_CON_THIEU.bat**. Không chọn workflow JSON.
3. Chờ chương trình báo **HOÀN TẤT**. Đóng backend/cửa sổ CMD ComfyUI rồi mở lại bằng cách bạn vẫn dùng; nhấn **Ctrl+F5** trong trình duyệt.
4. Mở workflow gốc. Có thể chạy **KIEM_TRA.bat** để xác minh file/checksum và xem hai node Pixaroma đã được server nạp chưa.

## Tự cài đúng những mục trong ảnh

| Mục | Đích |
|---|---|
| Pixaroma pack: PixaromaMonitor + PixaromaRunTimer | `ComfyUI/custom_nodes/ComfyUI-Pixaroma` hoặc thư mục Pixaroma hiện có được phát hiện |
| `h3-realism-people-t2v-i2v-r2v.safetensors` | `ComfyUI/models/loras` |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `ComfyUI/models/vae` |
| Dependency thiếu của Pixaroma | `imageio-ffmpeg==0.6.0`, cài vào đúng Python Portable, chỉ khi module chưa có |

Hai model khoảng **2,942 GB**, archive Pixaroma khoảng **11,12 MB**. File cùng tên hợp lệ ở model paths đang cấu hình được kiểm tra SHA-256 và dùng lại. Không tự đổi tên VAE FP16 thành INT8. LoRA Realism vẫn được tải để workflow gốc đầy đủ; khi làm hoạt hình3D bạn có thể bypass node#134 và bỏ trigger như skill hướng dẫn.

## Nhận diện thư mục

Ưu tiên đường dẫn đã lưu bởi bản vá; nếu chưa có thì thử nhận diện một ComfyUI Portable đang chạy. Nếu nhiều phiên đang chạy, yêu cầu chọn đúng thư mục. Khi không có phiên đang chạy, dùng đường dẫn đã biết:

`C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`

Nếu không tìm được, hộp thoại chỉ hỏi **thư mục Portable chứa python_embeded và ComfyUI**, không hỏi chọn file. Đường dẫn đích luôn được in trong cửa sổ. Bản vá dùng Python của Portable đó; không tạo runtime mới, không đổi cổng, không nâng Torch/ComfyUI core, không sửa workflow hoặc sampler.

## Khi tải gián đoạn hoặc gặp lỗi

- Chạy lại cùng file BAT; download `.part` được tiếp tục nếu máy chủ hỗ trợ Range. Checksum sai không được đổi thành model hoàn chỉnh.
- File model cùng tên nhưng sai hash được giữ nguyên và báo đường dẫn; không tự ghi đè model của người dùng.
- Pixaroma cũ được sao lưu vào `ComfyUI/user/h3_missing_fix/backups`, nằm ngoài custom_nodes để tránh đăng ký node trùng. Nếu cài đúng bản vá này rồi thì bỏ qua thay pack.
- Nếu tìm thấy nhiều thư mục Pixaroma, chương trình dừng và liệt kê chúng; tránh tạo thêm một bản gây xung đột route/node.
- Log nằm trong thư mục **logs** của gói này. Các báo cáo cài/kiểm tra được lưu trong **reports**. Gặp lỗi, xem phần cuối log; không cần tải lại cả bộ model H3.
- Sau cài phải khởi động lại **backend**, không chỉ refresh trang web. Nếu server còn thiếu node, KIEM_TRA in riêng trạng thái8188/8189 để tránh nhầm phiên. Cổng khác cần xem trực tiếp log backend; kiểm tra file trên ổ đĩa không đồng nghĩa server đã import thành công.

## Phạm vi kiểm tra

14 kiểm tra CPU đã qua: tìm Portable, ZIP traversal, sao lưu/khôi phục pack, dùng lại model theo hash, đường model dùng chung, pip chỉ cài dependency thiếu, download tiếp tục, checksum hỏng và bảo toàn workflow/core trong lần cài fixture. PowerShell parser thật kiểm tra cú pháp launcher.

Đã tải archive Pixaroma thật, xác minh hash và import cả pack vào ComfyUI0.43.1 trên CPU; cả hai node cần dùng đã đăng ký. URL hai model được kiểm tra bằng range, dung lượng và header safetensors khớp; hash model lấy từ metadata LFS upstream và được kiểm tra đầy đủ khi tải trên máy đích.

Chưa chạy Windows Forms/cài trên Windows thật hoặc renderGPU. Bản vá này xử lý đúng các mục thiếu trong ảnh cuối, không chứng nhận toàn bộ workflow/model H3 đã render thành công.

## Nguồn

Model, pack và archive đều khóa revision/SHA-256 trong `manifest.json`.

- Pixaroma: https://github.com/pixaroma/ComfyUI-Pixaroma
- LoRA: https://huggingface.co/fal/MiniMax-H3-Realism-People-LoRA
- VAE: https://huggingface.co/Comfy-Org/MiniMax-H3

Giữ giấy phép upstream. Gói phát hành không chứa trọng số model hoặc bản ComfyUI/Python khác.
