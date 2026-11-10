# Gỡ RelayVSR + RTX VFX khỏi ComfyUI Portable

Phiên bản 1.0.0 · 10/11/2026. Dành cho bộ RelayVSR-RTX-VFX-Original 1.0.0/1.0.1 đã cài vào Portable của bạn. Không tải model, không cần Git.

## Chạy bộ gỡ

1. **Đóng ComfyUI/backend và cửa sổ render DLSS** đang chạy.
2. Giải nén ZIP bộ gỡ vào một thư mục bình thường.
3. Nhấp đúp **GO_RELAYVSR.bat**. Mặc định dùng:

   ```text
   C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable
   ```

4. Nếu được hỏi, chọn **thư mục chứa `ComfyUI` và `python_embeded`**, không chọn JSON hoặc thư mục model.
5. Đợi thông báo hoàn tất. Báo cáo chi tiết nằm trong `reports/uninstall-*.json`, log nằm trong `logs/`. Sau đó có thể mở lại ComfyUI.

**GO_RELAYVSR.bat xóa trực tiếp các thành phần Relay riêng, không tạo bản sao model để giữ dung lượng.** Bạn đã yêu cầu gỡ; script không hỏi xác nhận thêm. Nếu muốn xem danh sách trước, dùng **XEM_TRUOC.bat**, thao tác này không xóa file.

## Phần được gỡ tự động

| Thành phần | Xử lý |
| --- | --- |
| `relayvsr_x2_lightx2v_int8_convrot.safetensors` | Xóa trong diffusion_models/unet và thư mục con thuộc các model path được cấu hình |
| `relayvsr_flash_vae_x2_fp32.safetensors` | Xóa trong vae và thư mục con thuộc các model path được cấu hình |
| File `.part`, `.part.corrupt-<số>`, `.alias-<số>` của đúng hai model | Xóa phần tải dở/hỏng hoặc bản sao dang dở |
| `ComfyUI-DLSS5-Enhancer` | Gỡ node, runtime DLSS, FFmpeg nằm trong node và config của node |
| `ComfyUI_Nvidia_VFX_Nodes` / tên RTX Nodes cũ | Gỡ pack node, gồm bản `-main`, `-master`, `.disabled` nếu có |
| Backup DLSS/NVIDIA do bộ Relay tạo | Gỡ trong `ComfyUI/user/RelayVSR_RTX_Original/backups` |
| Python distribution `nvidia-vfx` | Gỡ bằng pip của Portable nếu nằm trong Portable và không có node khác dùng SDK |
| Workflow gốc do bộ Relay chép | Chỉ gỡ bản đúng SHA256 trong `user/default/workflows/RelayVSR_RTX_Original`; giữ file bạn đã sửa |
| Metadata kiểm tra của bộ Relay | Gỡ `local-check.json`, `runtime-constraints.txt`; dọn thư mục quản lý trống |

Tổng hai file model chuẩn khoảng **5,29 GB**, chưa tính SDK/runtime. Dung lượng ổ đĩa thu hồi thực tế phụ thuộc hardlink, số bản sao và các file đã tải thành công.

`extra_model_paths.yaml` được đọc để tìm đúng hai tên model trên. Không quét toàn ổ đĩa hoặc xóa tất cả file có chữ “relay”. Liên kết thư mục bên trong cây được bỏ qua; nếu chính node là symlink/junction thì chỉ gỡ liên kết, giữ ứng dụng đích.

## Phần được giữ

- **VideoHelperSuite và backup của nó**: pack dùng chung cho các workflow video khác. Gỡ nó có thể làm hỏng workflow H3 của bạn.
- Model H3/OmniRef, encoder Qwen, VAE H3, LoRA và model upscale khác.
- ComfyUI core, các native node `RelayVSRConditioning`/`VSRDecode`, Torch, CUDA và driver. Các native node là một phần của core, không phải pack riêng để xóa.
- NumPy, OpenCV, PyAV, imageio-ffmpeg và dependency Python dùng chung.
- Video input/output, phim đã render và workflow đã chỉnh sửa.
- SDK nằm ngoài Portable hoặc SDK vẫn được node khác dùng; lý do được ghi trong báo cáo.
- DLSS runtime nằm ngoài pack và được đăng ký từ một ứng dụng khác; không xóa ứng dụng đó.
- Thư mục ZIP/bộ cài đã tải trong Downloads/C:\Ai, pip cache chung và dữ liệu NVIDIA dùng chung ngoài Portable. Bộ gỡ không tự suy đoán các thư mục cá nhân đó.

## Nếu chưa gỡ hết

Script từ chối chạy khi phát hiện ComfyUI/backend hoặc worker `nvngx.dll` đang dùng Portable này. Nó không tự tắt tiến trình. Đóng ứng dụng rồi chạy lại.

Nếu một file bị khóa/không có quyền, script tiếp tục các mục khác và ghi `failed`/`remaining_targets`. Thông báo **CHUA GO HET** sẽ xuất hiện thay vì báo hoàn tất. Không cần tải lại hoặc cài lại Relay để thử gỡ tiếp.

Nếu YAML lỗi hoặc không kiểm tra được SDK, báo cáo ghi rõ mục chưa xác minh. Script không xóa trực tiếp toàn bộ site-packages hoặc dependency liên quan bằng cách đoán tên.

## Kiểm tra đã thực hiện

Đã thử xóa file thật trong các Portable **giả lập**, kiểm tra model H3/video còn nguyên, exact filenames, model path ngoài, symlink, backup, khóa tiến trình, file đổi sau khi quét, file bị khóa, SDK dùng chung và chạy gỡ hai lần. SDK/pip và tiến trình Windows được giả lập trong test; **chưa chạy BAT/PowerShell hoặc gỡ trên máy Windows của bạn**. Xem `reports/VALIDATION.md`.

Khi dùng CLI, chạy bằng Python nhúng: `python.exe -I -X utf8 scripts/uninstall.py inspect --portable "đường_dẫn_Portable"`; thay `inspect` bằng `uninstall` để gỡ thực sự.
