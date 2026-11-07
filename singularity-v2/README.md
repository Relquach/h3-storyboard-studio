# Singularity V2 — Storyboard Studio cho Windows Portable

Bộ cài dựa trên **workflow JSON bạn cung cấp**, video hướng dẫn dài 9:50 và share_package trên Drive. Mục tiêu: **nguyên storyboard + sheet tùy chọn → video nhiều shot → lưu take → nâng latent 3D và refine take đã chọn**. Không dùng lại loader GGUF hay H3StudioReferences của bộ cài cũ.

## Cài và dùng

1. Giải nén bộ cài. Chạy **INSTALL.bat**. Bộ cài nhận đường dẫn `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`; nếu khác mới hỏi chọn thư mục chứa `python_embeded` và `ComfyUI`.
2. Chạy **START.bat**, giữ cửa sổ đang chạy. Studio riêng tại **http://127.0.0.1:8189**.
3. Chạy **PREPARE.bat**. Chọn dùng ví dụ Lan 15 giây hoặc project JSON do skill xuất. Chọn ảnh storyboard rồi sheet Lan khi được hỏi. Không cần tìm workflow JSON cũ hoặc cắt lẻ storyboard.
4. Trong ComfyUI, mở workflow **READY-... mới nhất** trong danh sách workflow; nếu chưa hiện, làm mới danh sách hoặc kéo file READY từ `H3-Singularity/ComfyUI/user/default/workflows` vào cửa sổ. Chạy **CHECK.bat** để kiểm tra node/model/ảnh/ánh xạ trước khi Queue.
5. **BƯỚC = false:** tạo nháp, xem video. Mỗi lần lưu một `.h3take` trong `output/h3_takes`. Nếu chưa đúng mặt, hành động, thứ tự shot thì sửa và tạo nháp lại.
6. **BƯỚC = true:** chọn take cụ thể hoặc `latest`, rồi Queue. Chỉ nâng take đã lưu; latent và conditioning lấy từ take, không encode lại từ prompt hiện tại. Video tại `H3-Singularity/ComfyUI/output/video`.

Ảnh của bạn không nằm trong bộ cài: PREPARE phải chọn ảnh trên máy. Hai file `Storyboard-4060Ti-VI.json` và `KiemTra-5s-VI.json` là mẫu để tham khảo/chọn ảnh thủ công; **READY** mới là bản đã tự đồng bộ prompt và dây ảnh. Để thử rẻ hơn, chạy **PREPARE-5S.bat** để tạo bản kiểm tra 5 giây/1 shot trước; không chỉ giảm giây mà giữ nguyên timeline 15 giây.

## Bộ cài thay đổi gì trên máy

- Tạo runtime riêng trong `ComfyUI_windows_portable/H3-Singularity`, gồm bản sao Python Portable và ComfyUI **0.43.1** đã khóa commit. Dependency chỉ cài vào bản sao Python này. Không cập nhật/ghi đè ComfyUI và Python hiện tại.
- Dùng lại thư mục model hiện tại qua `extra_model_paths.yaml`. File cùng tên được kiểm tra dung lượng và SHA-256; sai thì dừng, không tự xóa hoặc ghi đè. Các VAE đúng file đã tải từ bộ cài trước sẽ được dùng lại.
- Tải được tiếp tục sau gián đoạn. Cần khoảng **43.47 GB model** nếu chưa có gì, cộng dung lượng bản sao Python/core, cache và chỗ render/pagefile. RAM 32 GB không đồng nghĩa mọi cấu hình chắc chắn vừa bộ nhớ.
- Không cần Git hoặc Node.js. Audio-freeze được áp dụng bằng Python vào đúng phiên bản PlagueKind, có bản sao lưu và kiểm tra mẫu mã. Patch không khớp thì dừng.
- Giữ bản JSON gốc trong `sources/original-workflow.json`. Các ảnh, video hướng dẫn và trọng số không được đóng vào gói phát hành.
- Không tự đổi pagefile hoặc driver. Nếu driver NVIDIA quá cũ, bộ cài báo rõ. Nhánh driver 581+ dùng torch CUDA 13.0; nhánh 572–580 dùng CUDA 12.8 và các phép tính dự phòng của core. RTX 4060 Ti không có tăng tốc FP4 phần cứng.

## Model sử dụng

URL, commit, số byte và SHA-256 chính xác: `manifest.json`.

| Model | Dung lượng | Vai trò |
|---|---:|---|
| Singularity Ref2VA V2 pruned INT8 | 20.97 GB | Model video gốc trong JSON |
| Qwen3-VL 32B H3 NVFP4 AWQ | 15.69 GB | Encoder văn bản + ảnh; core giải lượng tử khi tính trên RTX 40 |
| H3 video VAE FP16 | 5.21 GB | VAE theo README tác giả; dùng decode tiled |
| H3 audio VAE FP32 | 0.61 GB | Audio của clip |
| LightX2V Ref2V Turbo resized rank 20 | 0.31 GB | Nháp 4 bước |
| H3 latent upscaler 3D FP16 | 0.69 GB | Bước nâng latent trước refine |

File gốc dùng VAE INT8; README tác giả ghi FP16. Bản cho bạn chọn **FP16** theo README và bật giải mã tiled, không đổi âm thầm model video Singularity sang model khác.

LoRA Realism People / Licon / Motion Repair vẫn được ghi nguồn trong manifest nhưng **không tải và không bật mặc định**. Realism People và trigger `r34l1sm` được bỏ khỏi prompt hoạt hình 3D. Không gọi các LoRA đó là khóa khuôn mặt.

## Custom node và core

- **ComfyUI core 0.43.1**: Ref2V/I2V, switch lazy, math, resolution selector, manual sigmas, sigma shift, attention backend, color transfer, video create/save, loader safetensors và các sampler.
- **PlagueKind**, commit `d58d006a4ea32c25c06499f2ff104f0852a045a6`: chỉ cài hai subpack cần dùng, `ComfyUI-H3-UltimateUpscale-LD` và `ComfyUI-H3-UpscaleSize`; có audio-freeze.
- **comfyui-h3-take** và **comfyui-video-finishing**: dùng đúng mã trong ZIP người dùng gửi. Take là safetensors + cấu trúc JSON, không dùng pickle.
- Không cần Pixaroma vì timer/monitor đã bỏ khỏi bản vận hành; không cần VideoHelperSuite/FlashVSR cho H3 hai bước. Mã temporal-detail-stabilizer được giữ trong nguồn để đối chiếu, chưa cài vào runtime này.

## Các điều chỉnh cho RTX 4060 Ti / hoạt hình 3D

Giữ cấu trúc hai pass; attention dùng PyTorch, hai node Sparse/Kitchen attention ở trạng thái bypass. Nháp 0.2 MP, bội 32; bản nâng mặc định 0.7 MP, chia thời gian 68 frame / overlap 17; latent upscaler 3D + refine với sigmas `0.55,0.42,0.3158,0.1579,0`. Vùng tham chiếu node 26 là 992×1792, độc lập kích thước latent nháp. Finishing/Clarity nhẹ hơn bản người thật; CRF 12, 24 FPS.

Các thông số này là **điểm bắt đầu để thử tương thích**, chưa phải cấu hình đã đo nhanh/đẹp nhất trên RTX 4060 Ti. Nâng latent/refine có thể đổi mặt/miệng hoặc gây flicker; audio-freeze giữ audio gốc, không bảo đảm lip-sync tuyệt đối. Singularity cũng có thiên hướng phong cách riêng nên cần duyệt mẫu 3D.

Nếu OOM: giảm target upscale, giảm số reference hoặc vùng tham chiếu hợp lý; giảm chunk 68 khi upstream cho phép; nếu bật chia ô refine, đổi sampler refine sang **euler** như hướng dẫn tác giả. Không tự bật sol-attn/Triton cho cấu hình Windows này trước khi kiểm tra tương thích.

## Storyboard, nhân vật và skill

`skills/minimax-h3-film/SKILL.md` đã cập nhật cho workflow mới. AI hỏi các thông tin còn thiếu; tự chia shot, ước lượng giây, chọn lưới linh hoạt 2×2/2×3/3×3...; viết prompt storyboard tiếng Anh với nhãn SHOT và prompt video khớp timeline. Local dùng 3–15 giây/lượt, dưới trần 30 giây ban đầu; shot dựng có thể 1 giây.

`project.json` dùng ID ổn định `STORYBOARD`, `CHAR_01`, `ENV_01`, `PROP_01`; prompt dùng `<Asset:ID>`. PREPARE đổi token sang `<Picture n>` và tạo core LoadImage tương ứng từ **cùng danh sách ảnh bật**. Ví dụ bỏ sheet Lan thì không còn Picture 2 trỏ tới Lan: prompt chỉ dẫn ngoại hình từ storyboard. Tắt sheet làm giảm thông tin nhận diện, không tương đương dùng sheet.

Thêm/bỏ tham chiếu bằng `assets[].enabled` trong project rồi chạy PREPARE lại. Không bypass ảnh trực tiếp trong UI mà giữ prompt cũ. Storyboard phải bật đầu tiên; tổng tối đa 9 ảnh bật. Không dán token Asset chưa resolve vào H3. Xem ví dụ `examples/lan-15s.project.json`.

## Kiểm tra và phạm vi đã xác minh

Đọc `reports/VALIDATION.md`. Đã chạy ComfyUI core thật trên CPU, mở JSON bằng Chromium, lấy API prompt từ frontend và kiểm tra schema cả hai pass. Đã thử lưu–nạp take với tensor thật và finishing CPU. Model trong lần thử schema là file tên giả lập, **không có trọng số thật được load/render**.

Chưa có GPU NVIDIA ở đây; chưa thực thi cài Windows Portable trên máy thật, chưa benchmark RTX 4060 Ti, chưa xác minh khuôn mặt/phong cách 3D qua video sinh. Thời gian hiển thị trong video hướng dẫn không được dùng làm số đo của máy bạn. FlashVSR hoãn theo lựa chọn người dùng; bản này hoàn thiện H3 hai bước trước.

## Nguồn và quyền sử dụng

Workflow / README / ba pack nhỏ / patch JS: tài liệu người dùng cung cấp. Giữ nguồn gốc, không tự gán giấy phép MIT cho mã tác giả. ComfyUI, PlagueKind và model giữ giấy phép upstream. `sources/PROVENANCE.md` ghi URL và hash của các file đầu vào. Bộ cài không phân phối lại model hay ảnh/video riêng.
