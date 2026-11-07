# Sửa phần thiếu của workflow H3 gốc — v1.1.0

Bản vá này bổ sung cả nhóm node đang báo **Pack inconnu** trong ảnh mới: take, latent upscale, tính kích thước và finishing; kèm Pixaroma từ bản1.0.

## Với lỗi 10 node trong ảnh: chạy file này

1. Giải nén ZIP mới vào một thư mục riêng.
2. Chạy **SUA_10_NODE.bat**, chờ **HOÀN TẤT PHẦN NODE**.
3. Đóng hẳn **backend/cửa sổ CMD ComfyUI**, mở lại bằng cách bạn vẫn dùng rồi nhấn **Ctrl+F5** trong trình duyệt.
4. Chạy **KIEM_TRA_NODE.bat** nếu muốn kiểm tra. Nó đối chiếu toàn bộ11 loại custom node cần thiết trong workflow gốc, không chỉ Pixaroma.

**SUA_10_NODE không tải/kiểm tra lại model, không đổi workflow, không nâng Torch hoặc ComfyUI core.** Mã node take/finishing được đóng sẵn từ ZIP Drive. PlagueKind tải khoảng189KB, Pixaroma khoảng11MB nếu chưa có cache đúng hash.

## Các gói được bổ sung

| Nguồn / thư mục | Node trong workflow |
|---|---|
| Drive: `comfyui-h3-take` | H3TakeSave, H3TakeLoad |
| Drive: `comfyui-video-finishing` | VideoFinishDetailTone (2 node trong graph) |
| PlagueKind: `ComfyUI-H3-UltimateUpscale-LD` | MMH3UltimateUpscale, MMH3LatentUpscaleParams, MMH3LatentUpscaleWithModelParams, MMH3SpatialSplitParams, MMH3TemporalSplitParams |
| PlagueKind: `ComfyUI-H3-UpscaleSize` | H3UpscaleSizeLD |
| Pixaroma | PixaromaMonitor, PixaromaRunTimer |

Nhóm báo thiếu10 node có9 loại khác nhau vì VideoFinishDetailTone xuất hiện hai lần. Cộng hai loại Pixaroma là11 loại custom node. Các node take/finishing là pack riêng trong Drive, nên chỉ cài Pixaroma/tra Manager sẽ không bổ sung được chúng.

Audio-freeze được áp dụng có kiểm tra vào mã PlagueKind đúng commit, có backup; không cần Node.js. Temporal Detail Stabilizer/FlashVSR ngoài phạm vi H3 hai bước nên chưa cài.

## Nếu còn thiếu model

**CAI_PHAN_CON_THIEU.bat** cài đủ node như trên và kiểm tra/tải các model **đang bật trong JSON gốc**:

- Singularity Ref2VA V2 pruned INT8.
- Encoder Qwen3-VL32B NVFP4 AWQ.
- Video VAE INT8, audio VAE FP32.
- Turbo Ref2V rank20, Realism People.
- H3 latent upscaler3D FP16.

Chỉ tải file chưa có; file đúng dung lượng/SHA-256 sẽ được dùng lại. Bản1.0 chỉ có hai model trong ảnh cũ; bản1.1 kiểm tra cả model của nhánh upscale để tránh báo thiếu tiếp sau khi node đã nạp. Nếu chưa có bất kỳ model nào thì tổng dung lượng khoảng41.2GB; **để chỉ sửa lỗi node hiện tại, dùng SUA_10_NODE.bat**. Không tải Licon/Motion Repair vốn bypass trong graph gốc.

**KIEM_TRA.bat** kiểm tra file/checksum model và các node. Vì phải đọc trọng số lớn để hash, bước kiểm tra model có thể mất thời gian. Không đổi tên VAE FP16 thành INT8. Muốn giữ model khác đã chủ động chọn trong workflow của bạn, chỉ chạy SUA_10_NODE.

## Chọn đúng ComfyUI

Bản vá dùng Portable đã lưu trong lần chạy cùng gói. Nếu chưa có, thử nhận diện một ComfyUI Portable đang chạy; khi nhiều phiên thì hỏi thư mục đúng. Nếu không có phiên, thử đường dẫn đã biết:

`C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`

Hộp thoại, nếu xuất hiện, hỏi **thư mục Portable chứa python_embeded và ComfyUI**, không hỏi file workflow JSON. Đích cài luôn được in trong console. Không tạo runtime/cổng mới. Bản vá chưa tự nâng core; nguồn workflow dùng ComfyUI0.43.1 hoặc mới hơn.

## Bảo toàn dữ liệu và xử lý lỗi

- Nếu đã có PlagueKind đầy đủ, bản vá tìm các subpack bên trong để cập nhật đúng chỗ thay vì cài thêm một bản trực tiếp gây trùng. Nếu có nhiều bản cùng component, dừng và liệt kê chúng.
- Pack cũ được sao lưu trong `ComfyUI/user/h3_missing_fix/backups`, ngoài custom_nodes. Sao chép thất bại sẽ khôi phục pack cũ. Cài lại cùng nội dung được bỏ qua; dấu vân tay file không tính __pycache__.
- File model cùng tên nhưng sai hash được giữ nguyên và báo đường dẫn, không tự ghi đè. `.part` hỗ trợ tiếp tục tải khi máy chủ cho phép.
- Dependency chỉ cài module còn thiếu; dùng đúng Python Portable và `--no-deps`. Không nâng Torch.
- Log ở **logs**, báo cáo ở **reports** của gói này. Nếu sau restart vẫn thiếu node, xem lỗi import trong CMD hoặc chạy KIEM_TRA_NODE. Không nhận “file đã copy” tương đương “backend đã import”.

## Kiểm tra đã thực hiện

- **21 kiểm tra CPU**: download/hash, model đã có, backup/khôi phục, tìm subpack lồng trong PlagueKind, tránh bản trùng, audio-freeze và bảo toàn workflow/core.
- Chạy luồng SUA_10_NODE thực tế trong Portable giả lập với archive Pixaroma/PlagueKind thật và source Drive thật. Chạy lần hai xác nhận bỏ qua nội dung đã cài. Sau đó ComfyUI0.43.1 thật bằng torch2.10.0+cpu nạp **chính5 thư mục vừa cài**; đủ11 loại node đã đăng ký. Thư mục model không được tạo và core sentinel giữ nguyên. Xem `reports/v11-installed-import.json`.
- Source take/finishing khớp từng byte với custom_nodes_local.zip vừa tải lại từ Drive. SHA ZIP ghi trong `reports/drive-source.json`.
- Parser PowerShell thật kiểm tra launcher. **Chưa chạy trên Windows thật hoặc renderGPU**, chưa chứng nhận tốc độ, VRAM hay chất lượng video. Mã đầy đủ trên ổ đĩa không bảo đảm import trên một core quá cũ hoặc môi trường dependency lỗi.

## Nguồn

- Drive: https://drive.google.com/drive/folders/1-PxsMgTI-RD26KrUbiMnAWkV5-RZvUHS
- PlagueKind: https://github.com/PlagueKind/ComfyUI-PlagueKind-Nodes
- Pixaroma: https://github.com/pixaroma/ComfyUI-Pixaroma
- Model: các repository/commit/hash trong `manifest.json`.

Giữ giấy phép upstream; source hai pack Drive là mã tác giả cung cấp, không tự gán giấy phép khác. Không phân phối trọng số hay ComfyUI/Python trong ZIP.
