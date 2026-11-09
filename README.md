# Bộ cài workflow gốc — OmniRef tạo video và RelayVSR upscale

Hai bộ riêng cho **ComfyUI Windows Portable**, giữ nguyên từng byte JSON bạn gửi. **Skill hiện tại không thay đổi.**

| Bộ | Tải ZIP cài tự động | Hướng dẫn có ảnh |
| --- | --- | --- |
| **FastH3 OmniRef** — tạo video từ storyboard + character sheet + prompt | [TẢI BỘ CÀI OMNIREF](https://github.com/Relquach/h3-storyboard-studio/raw/refs/heads/main/dist/FastH3-OmniRef-Original-v1.0.0.zip) | [PDF 7 trang](fasth3-omniref-original/docs/HUONG_DAN.pdf) · [Word](fasth3-omniref-original/docs/HUONG_DAN.docx) · [Markdown](fasth3-omniref-original/docs/HUONG_DAN.md) |
| **RelayVSR + RTX VFX** — hậu kỳ video đã có: tăng FPS → DLSS5 → upscale 2× → TrueHDR | [TẢI BỘ CÀI RELAYVSR](https://github.com/Relquach/h3-storyboard-studio/raw/refs/heads/main/dist/RelayVSR-RTX-VFX-Original-v1.0.0.zip) | [PDF 8 trang](relayvsr-rtx-original/docs/HUONG_DAN.pdf) · [Word](relayvsr-rtx-original/docs/HUONG_DAN.docx) · [Markdown](relayvsr-rtx-original/docs/HUONG_DAN.md) |

**Cài:** tải đúng ZIP riêng ở bảng → giải nén → đóng ComfyUI → chạy **CAI_DAT.bat**. Mặc định dùng `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`. Nếu hỏi đường dẫn, chọn **thư mục chứa ComfyUI và python_embeded**, không chọn JSON. Mở lại ComfyUI rồi chạy **KIEM_TRA.bat**.

- **OmniRef:** bốn model tổng khoảng **41,32 GB**; ba model H3 dùng chung đúng hash được dùng lại, có thể chỉ còn tải OmniRef **22,21 GB**. Không có custom node hoặc LoRA cần thêm. Chọn storyboard ở **#137 / Picture 1**, character sheet ở **#149 / Picture 2**. Ảnh riêng không nằm trong gói. Core mới có `chroma_subsampling` thì chọn **auto ở Create Video #130**; JSON nguồn giữ nguyên. [Cách dùng và setting](fasth3-omniref-original/README.md) · [Manifest](fasth3-omniref-original/manifest.json).
- **RelayVSR:** hai model tổng khoảng **5,29 GB**, thêm NVIDIA SDK và DLSS runtime. NVIDIA VFX Nodes 0.2.1 yêu cầu **PyTorch CUDA 13.0+**, Windows/NVIDIA CUDA hoạt động; bộ cài không tự thay Torch/driver. Trình cài DLSS upstream hỏi giấy phép **Continue? [y/N]**, không tự chấp nhận. Nhập MP4 thật ở **#10**; cap gốc **151 frame**. File cuối ở `ComfyUI/output/vsr_upscale/`; preview #27/#30 không có tiếng. **Nhánh TrueHDR đang bật nhưng H.264/yuv420p gốc chưa cấu hình HDR signaling chuẩn**; xem hướng dẫn trước khi đánh giá màu. [Cách dùng và setting](relayvsr-rtx-original/README.md) · [Manifest](relayvsr-rtx-original/manifest.json).

Quy trình: tạo storyboard → **người dùng duyệt** → prompt đúng storyboard/ảnh tham chiếu → OmniRef render → duyệt MP4 → RelayVSR hậu kỳ. Không đưa ảnh storyboard vào ô video nguồn của RelayVSR.

Đã qua **29 ca kiểm tra installer**, chạy cài hai lần bằng Python isolated mode trên Portable giả lập; OmniRef kiểm UI/schema trên hai core, Relay kiểm các thành phần khả dụng trên CPU. **Chưa kiểm thử launcher Windows, render GPU hoặc benchmark RTX 4060 Ti 16 GB / RAM 32 GB.** Đủ dependency không bảo đảm mọi cấu hình chạy vừa bộ nhớ. [Chi tiết OmniRef](fasth3-omniref-original/VALIDATION.md) · [Chi tiết RelayVSR](relayvsr-rtx-original/VALIDATION.md).

[Checksum hai ZIP](dist/Original-OmniRef-RelayVSR-v1.0.0.sha256)

---

# OpenH3 Regenerate2K — bộ nạp workflow gốc

**[TẢI BỘ CÀI OPENH3 REGENERATE2K](dist/OpenH3-Regenerate2K-Original-v1.0.0.zip)** · [Hướng dẫn PDF 15 trang có ảnh](openh3-regenerate2k/docs/HUONG_DAN.pdf) · [Word](openh3-regenerate2k/docs/HUONG_DAN.docx) · [HTML](openh3-regenerate2k/docs/HUONG_DAN.html)

Bộ này dùng cho **video đã render**: MP4 nguồn → latent upscale → OpenH3 refine → decode → lưu MP4 với tiếng nguồn. Trong chuỗi phim: Codex/storyboard → workflow tạo video như Apex → duyệt clip → OpenH3 Regenerate2K để hậu kỳ.

**Chỉ một workflow gốc `OpenH3_Regenerate2K Final.json`, giữ nguyên từng byte; không sửa skill, prompt, setting hoặc dây nối.** [Xem JSON gốc](openh3-regenerate2k/workflows/OpenH3_Regenerate2K%20Final.json).

1. Tải **ZIP OpenH3 riêng ở trên**, giải nén và đóng ComfyUI.
2. Chạy **CAI_DAT.bat**. Chọn thư mục Portable chứa **ComfyUI và python_embeded** nếu được hỏi. Mặc định `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`.
3. Bộ nạp kiểm tra core/Python trước khi tải. Nếu thiếu native H3 upscale hoặc direct-buffer VAE, dùng updater chính thức `update/update_comfyui.bat` của Portable rồi thử lại.
4. Mở lại ComfyUI → chạy **KIEM_TRA.bat** → mở **OpenH3_Original / OpenH3_Regenerate2K Final**.
5. Chọn **MP4 thật ở Load Video #1**, đặt **width/height ở Upscale Latent #6**, rồi Run. File gốc lưu 2560×1440; clip dọc cần chọn kích thước dọc bằng UI. Kết quả ở `ComfyUI/output/OpenH3_2K`.

Cài **4 pack node + 7 model (~54,45 GB nếu chưa có)**; dùng lại file đúng SHA256, có resume và alias/hardlink để giữ tên model trong JSON gốc. Backup node/workflow ở `ComfyUI/user/OpenH3_Original/backups`. `CAI_LAI_NODE.bat` chỉ cài node. Thời lượng bám video nguồn; `max_frames` là cap từ chối, không phải công cụ cắt clip.

[Hướng dẫn nhanh](openh3-regenerate2k/README.md) · [Model/node và SHA256](openh3-regenerate2k/manifest.json) · [Bằng chứng kiểm thử](openh3-regenerate2k/reports/VALIDATION.md) · [Checksum ZIP](dist/OpenH3-Regenerate2K-Original-v1.0.0.sha256)

Đã qua 23 unit test, nạp UI/schema và chuẩn bị video/audio trên CPU; script cài đã chạy trong Portable giả lập. **Chưa render GPU trên RTX 4060 Ti hoặc kiểm thử Windows thật.** JSON gốc SHA256 `77801992727a09a22547b44f0b70b985e9472820da2e21941a87cf778d8e5973`.

---

# Apex H3 V7 — tạo video từ storyboard

**[TẢI BỘ CÀI APEX V7](dist/Apex-H3-V7-Studio-v1.0.0.zip)** · [Skill H3 v4 riêng](dist/MiniMax-H3-Film-Skill-v4-Apex-V7.zip) · [Hướng dẫn PDF 19 trang có ảnh](apex-v7/docs/HUONG_DAN.pdf) · [Word](apex-v7/docs/HUONG_DAN.docx) · [HTML](apex-v7/docs/HUONG_DAN.html)

Nội dung Việt → Codex tạo storyboard → **bạn duyệt ảnh** → prompt video tiếng Anh và bảng ảnh/Picture → ComfyUI. Preset dành cho **3D bán hiện thực Á Đông / CGI beauty render, pha nét búp bê**, dọc 9:16.

1. Tải **ZIP Apex riêng ở trên**, giải nén và đóng ComfyUI.
2. Máy **RTX 4060 Ti 16 GB / RAM 32 GB**: nên chạy **CAI_DAT_H3_NHE.bat** trước, tối đa khoảng **53,8 GB** model nếu chưa có file.
3. Muốn đủ H3 + LTX 2.5 hoàn thiện 1080×1920: chạy **CAI_DAT.bat**, tối đa khoảng **93,7 GB**. File có sẵn đúng SHA256 được dùng lại.
4. Chọn thư mục Portable chứa **ComfyUI và python_embeded** nếu bộ cài hỏi. Mặc định `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`.
5. Mở lại ComfyUI, chạy **KIEM_TRA.bat**, mở workflow **01_APEX_V7_3D_H3_2PASS_DOC**. Nạp storyboard **#7330**, dán prompt đã duyệt **#138**, đặt giây **#132**. Bắt đầu 5 giây.

Có hai preset: **H3 hai chặng** và **H3 + LTX 1080p**. Ảnh phụ có dây thật và mặc định bypass; phải đồng bộ số Picture theo ảnh đang bật. Prompt Codex nối trực tiếp, giữ tiếng H3 nền ở đầu ra cuối. JSON tác giả được giữ trong source của gói; các điều chỉnh Studio ghi trong [CHANGELOG](apex-v7/CHANGELOG.md).

[Đọc hướng dẫn nhanh](apex-v7/README.md) · [Đọc skill v4](skills/minimax-h3-film/SKILL.md) · [Model/node, revision và SHA256](apex-v7/manifest.json) · [Kiểm thử](apex-v7/reports/VALIDATION.md) · [Checksum tệp tải](dist/Apex-H3-V7-downloads.sha256)

Đã kiểm tra **28 test bộ cài/handoff, 45 test skill, 6 cấu hình UI/API/schema, 14 URL model** và script cài trên Portable giả lập. **Chưa render GPU, chạy Windows thật hoặc benchmark tốc độ/chất lượng trên 4060 Ti.** RAM 32 GB có thể cần offload/pagefile nhiều.

---

## Các bản trước

> **Skill v3 lưu trữ — đã có v4 ở trên:** [Tải ZIP đầy đủ](dist/MiniMax-H3-Storyboard-Skill-v3.0.0.zip) · [Đọc SKILL.md](skills/minimax-h3-film/SKILL.md) · [Quy trình mới](skills/minimax-h3-film/QUY_TRINH_MOI.md) · [Cách nhận diện workflow](skills/minimax-h3-film/references/workflow-mode-routing.md). Phân biệt FastH3 I2V với Singularity Ref2V, kiểm tra ảnh/Picture và duration, giữ style 3D bán hiện thực Á Đông. Bản công khai không kèm JSON/video/frame/thoại riêng của người dùng. Đã qua 34 kiểm tra CPU; chưa render GPU mới.

> **Hướng dẫn workflow gốc — 36 trang có ảnh:** [Đọc/tải PDF](docs/workflow-guide/Huong-dan-workflow-goc-MiniMax-H3.pdf) · [Word có thể chỉnh sửa](docs/workflow-guide/Huong-dan-workflow-goc-MiniMax-H3.docx) · [Tải gói đầy đủ](docs/workflow-guide/Huong-dan-MiniMax-H3-tron-bo.zip) · [Cách đọc tài liệu](docs/workflow-guide/README.md). Giải thích setting, ảnh-node-Picture, quy trình tạo nháp → chọn take → upscale và ví dụ Lan 15 giây. Gói đầy đủ có thêm HTML ngoại tuyến tìm kiếm được và prompt mẫu.

> **Sửa lỗi 10 node thiếu — bản1.1:** [Tải ZIP mới](dist/H3-Original-Missing-Parts-v1.1.0.zip). Giải nén và chạy **SUA_10_NODE.bat** để cài take/finishing từ Drive, PlagueKind upscale/size và Pixaroma vào đúng ComfyUI đang dùng. Chế độ này không tải model. [Hướng dẫn](original-workflow-missing-fix/README.md). Đã thử luồng cài node và import đủ11 loại bằng ComfyUI thật trên CPU; chưa chạy Windows/GPU.

> **Bản vá các phần thiếu trong workflow gốc:** [Tải ZIP](dist/H3-Original-Missing-Parts-v1.0.0.zip) · [Hướng dẫn](original-workflow-missing-fix/README.md). Chạy CAI_PHAN_CON_THIEU.bat để thêm Pixaroma, Realism People LoRA và video VAE INT8 vào đúng Portable hiện có (~2.94 GB model). Giữ nguyên workflow, Torch và ComfyUI core.

> **Skill v2 lưu trữ cho workflow Singularity gốc (đã được thay bằng v3 ở trên):** [Tải ZIP skill](dist/MiniMax-H3-Original-Workflow-Skill-v2.0.0.zip) · [Đọc SKILL.md](skills/minimax-h3-film/SKILL.md) · [Bảng node gốc](skills/minimax-h3-film/references/workflow-original.md). Codex tạo storyboard và prompt để nạp trực tiếp vào workflow gốc; không cần bộ cài hay PREPARE riêng. File workflow gốc được giữ nguyên trong gói skill.

> **Bộ cài mới theo workflow/video Singularity V2:** [Tải ZIP riêng](dist/Singularity-Storyboard-Studio-v1.0.0.zip) · [Hướng dẫn](singularity-v2/README.md) · [Skill đã cập nhật](singularity-v2/skills/minimax-h3-film/SKILL.md). Giải nén ZIP riêng rồi chạy INSTALL.bat bên trong; không dùng bộ cài GGUF cũ ở phần dưới. Đã kiểm tra UI/schema/take trên CPU, chưa render GPU/Windows.

# H3 Storyboard Studio — Windows Portable

**Experimental release. Installer and graph logic tested on CPU; no GPU render or Windows execution has been completed by the author of this package. No preset is yet a measured quality/speed winner.**

Dành cho RTX 4060 Ti 16 GB, RAM 32 GB, ComfyUI Windows Portable. Nguyên storyboard + tối đa 8 ảnh tham chiếu tùy chọn → H3 Ref2V → video/audio → tùy chọn upscale 2×. Phong cách thử: 3D animation, mắt biểu cảm, tóc nhiều chi tiết, ánh sáng mềm.

## Cập nhật v0.3.0 — dành cho máy đã cài model

1. [Tải source ZIP mới](https://github.com/Relquach/h3-storyboard-studio/archive/refs/heads/main.zip), giải nén. Đóng hẳn cửa sổ ComfyUI/backend đang chạy.
2. Chạy **UPGRADE.bat trong thư mục vừa giải nén**. Nó dùng đường dẫn Portable đã biết, cập nhật node và tự chép workflow vào `ComfyUI/user/default/workflows/H3_Storyboard_VI_v0.3.json`. Không hỏi chọn workflow JSON, không tải lại model. Node cũ được sao lưu ngoài custom_nodes; workflow cũ được giữ lại.
3. Mở lại ComfyUI, nhấn **Ctrl+F5**, mở **H3_Storyboard_VI_v0.3** trong danh sách workflow. Nếu chưa hiện, kéo file `workflows/lan-15s-vi.json` từ bộ cài vào ComfyUI.
4. Chọn ảnh storyboard và ảnh Lan trong **Tham chiếu 1**. Prompt Lan 15 giây đã điền sẵn; ảnh riêng không nằm trong ZIP nên phải chọn ảnh trên máy.

**Lỗi model:** DiT Q3 có 532 tensor native và không có metadata `general.architecture`; loader GGUF thông thường không nhận diện được. Loader mới đọc tên/shape native rồi chuyển cho bộ nhận diện model của ComfyUI core. Đã đối chiếu đủ 532 tên và shape với bản BF16 chính thức; chưa xác minh một lần render GPU hoàn chỉnh.

**Ảnh tham chiếu tùy chọn:** mỗi node có Bật tham chiếu, Tên tài sản, Loại tham chiếu và Chọn ảnh. Môi trường/đạo cụ mặc định tắt; ảnh Lan mặc định bật. Tắt node bằng công tắc này sẽ không đọc ảnh của node. Có thể nhân đôi node để thêm nhân vật/môi trường/vũ khí/phong cách rồi nối `Danh sách tham chiếu` → `Tham chiếu trước`, node cuối → `Ảnh tham chiếu bổ sung`. Tối đa 8 ô cộng storyboard. Khi tắt một ô ở giữa, hệ thống tự đánh lại Picture cho ảnh đang dùng và cập nhật tag trong prompt, giữ thứ tự ban đầu. Tag của ảnh đã tắt chuyển về storyboard và có ghi chú rõ ràng. Không cần nhập danh sách roles_json thủ công. Dùng công tắc để bỏ qua; chế độ Bypass chung của ComfyUI không thay thế công tắc này.

## Cài và dùng

1. GitHub → **Code → Download ZIP**, giải nén vào một thư mục cố định. Đóng ComfyUI trước khi cài.
2. Nhấp **INSTALL.bat**. Bộ cài thử đường dẫn `C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable`; nếu không có, chọn thư mục chứa `python_embeded` và `ComfyUI`. Tự cài hai bộ custom node đã khóa commit, node của dự án và tải 6 file model (~29,65 GB), xác minh SHA-256. Cần thêm dung lượng dự phòng. Không cần Git cho bước cài.
3. Nhấp **START-STUDIO.bat**, chờ ComfyUI sẵn sàng. Nếu ComfyUI đã chạy, dùng phiên đang chạy, không mở thêm server.
4. Nhấp **PREPARE-INPUTS.bat**, chọn project JSON do skill xuất (hoặc `examples/project.json`), nguyên ảnh storyboard rồi đúng sheet từng nhân vật. Ảnh được sao chép vào thư mục input bằng tên duy nhất; ảnh gốc không bị sửa.
5. Nhấp **PREFLIGHT.bat**. Kiểm tra node, model enum, liên kết và ảnh trên runtime thật; sinh `workflows/baseline.json` và `turbo4.json` để kéo vào ComfyUI. Đừng import `*.api.json` như workflow giao diện.
6. **RENDER.bat** tạo baseline và bản upscale. Video ở `ComfyUI/output/h3studio`. **BENCHMARK.bat** so sánh baseline 20 bước với Turbo 4 bước qua hai seed, ghi báo cáo vào `reports/`.

Bộ cài chưa tự cập nhật ComfyUI core hoặc đè node cũ. Nếu core thiếu H3, hãy sao lưu và dùng updater chính thức của Portable rồi cài lại. Nếu đã có bộ node cùng tên nhưng khác commit, installer dừng để bảo vệ cấu hình của bạn. Các dependency pip sẽ được cài vào Python Portable đã chọn; đây không phải môi trường Python tách biệt. Bộ cài cần Internet; sau khi đủ model và dependency, render dùng local.

## Model và node

`manifest.json` là nguồn chính: URL/repository, commit, dung lượng, SHA-256. Chọn H3 Ref2VA pruned Q3 và encoder native Q2 có sẵn vision. Dùng hai loader riêng H3StudioNativeModelLoader và H3StudioNativeClipLoader; vẫn cần lần encode/render đầu xác minh thực thi và chất lượng. Không gọi nó là một bộ đã benchmark.

- `unsloth/MiniMax-H3-GGUF`: Ref2VA pruned Q3, H3 Qwen3-VL Q2 encoder, video VAE FP16, audio VAE FP32.
- Không tải thêm mmproj trong v0.2: encoder Q2 đã tích hợp vision; giữ lại file mmproj cũ trên máy nếu đã tải, workflow mới không dùng nó.
- `Comfy-Org/MiniMax-H3`: LightX2V Ref2V Turbo 4-step (nhánh so sánh, chưa xác minh kết quả trên GGUF này).
- `xinntao/Real-ESRGAN`: x2plus cho upscale cuối theo từng batch nhỏ.
- `city96/ComfyUI-GGUF` + `jlucasmcrell/ComfyUI-H3-Multishot`: nạp GGUF và encoder/vision H3. **Không dùng sampler seamless-chain của pack**: clip có cut theo storyboard, không biến mọi cảnh thành một take.
- Node của dự án `H3StudioReferences`: truyền nguyên grid + sheet theo thứ tự và sinh phần ánh xạ prompt; `H3StudioUpscale`: giải phóng GPU theo từng batch upscale.

Tham khảo: [ComfyUI H3](https://github.com/Comfy-Org/docs/blob/main/tutorials/video/minimax/minimax-h3.mdx), [H3 core](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py), [GGUF](https://huggingface.co/unsloth/MiniMax-H3-GGUF), [loader H3](https://github.com/jlucasmcrell/ComfyUI-H3-Multishot), [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN).

## Giữ nhân vật và phong cách

Picture 1 luôn là nguyên storyboard. Trong chuỗi tham chiếu mới, Picture 2 trở đi theo thứ tự các ô đang bật; mỗi ô giữ tên và loại tài sản riêng. `project.json` ghi ID, tên, file và mô tả từng người; code sinh prompt và dây nối từ cùng dữ liệu, không đánh số riêng bằng tay. Sheet nên có khuôn mặt rõ và trang phục giống các ô storyboard. Lặp lại người trong các ô là cùng một nhân vật; prompt loại lưới, nhãn và nền sheet khỏi video.

Các bộ cài không kèm ảnh riêng làm đầu vào render. Tài liệu hướng dẫn mới có ảnh Lan và storyboard minh họa đã được người dùng cho phép công khai; để chạy workflow, chọn storyboard và character sheet của bạn trên máy. Bộ cài không tự có ảnh riêng trong cuộc trò chuyện và không tự huấn luyện LoRA nhân vật.

`grid` là [số hàng, số cột], không cố định 6/9 ô. Thời lượng từng shot tùy hành động, có thể 1 giây; project mỗi lượt 4–15 giây, số frame bám lưới 17n+5, nên thời lượng clip nguồn có thể dài hơn timeline dự kiến. Dựng/cắt cuối để đạt thời lượng tập. Cut trong prompt là mục tiêu, không bảo đảm đúng từng frame.

## Chất lượng cuối và giới hạn

Đã có **nhánh upscale 2× theo frame** và giữ lại bản gốc để so sánh. Đây không phải latent refine; có thể làm lộ flicker và không chữa được sai hình thể. Không bật thêm FaceRefine, LMS, Pika hoặc nhiều Turbo đồng thời khi chưa kiểm chứng, đặc biệt mặt 3D. Latent upscale/refine và FaceRefine là hạng mục nâng cấp sau thử GPU, chưa có trong phiên bản này.

640×384, 124 frame (~5,17 giây) là thử chức năng, không phải tiêu chuẩn mặt đẹp. Sau khi chạy ổn, thử tăng độ phân giải với cùng input. 16 GB VRAM/32 GB RAM không được bảo đảm đủ cho mọi số nhân vật/độ phân giải; offload có thể chậm. Không có số phút render hứa trước.

## Đo và chọn cấu hình

Benchmark giữ cùng storyboard, sheets, kích thước, thời lượng, seed theo từng vòng. Baseline và Turbo dùng lịch sampling riêng theo mục đích nên đây là so sánh **hai cấu hình hoàn chỉnh**, không phải ablation chỉ một LoRA. Hai vòng dùng hai seed; cache/offload không bảo đảm cold/warm giống nhau. Báo cáo có wall time, history, mẫu VRAM quan sát từ nvidia-smi (không phải đỉnh CUDA tuyệt đối). Không dùng upscale khi benchmark generation mặc định.

Mở video side-by-side và điền CSV theo thang 1–5, cao hơn là tốt hơn: nhận diện mặt, giải phẫu/chuyển động, thứ tự shot, phong cách 3D, ổn định giữa frame. Chỉ khi mọi seed đạt nhận diện/chuyển động ≥4, tiêu chí khác ≥3, `scripts/choose_preset.py REPORT.json QUALITY.csv` mới chọn preset nhanh nhất chấp nhận được. Không có điểm chất lượng tự bịa hoặc lựa chọn tốt nhất toàn cục. Với kết quả rỗng hoặc thất bại, chưa chọn được preset.

Nếu clip sai động tác/méo mặt, tạo lại trước upscale. Không cố cứu hình thể sai bằng sharpen. Để sửa một shot khó có thể tách lượt tạo, nhưng nhánh chính vẫn dùng nguyên storyboard.

## Kiểm thử và hỗ trợ

`python -m unittest discover -s tests -v` kiểm tra logic tải/kiểm tra checksum, ánh xạ ảnh, duration, reference wrapper và graph. `reports/VALIDATION.md` tách rõ điều đã kiểm tra với việc chưa chạy GPU/Windows. `PREFLIGHT.bat` cần ComfyUI thật; runtime không tương thích sẽ dừng thay vì giả vờ thành công. Nếu encoder báo shape mismatch/vision, giữ log và không render batch lớn.

## Phạm vi và giấy phép

Code do dự án viết: MIT (`LICENSE`). Các model/node bên thứ ba giữ giấy phép riêng của chúng; tải từ upstream, không phân phối lại trọng số trong repo. Repo không gồm ComfyUI Portable/NVIDIA driver/FFmpeg binary hay model sinh storyboard. Skill đã được hoàn thiện để xuất prompt storyboard/video và project JSON cho bộ cài này.

## Bản sửa v0.2.0: encoder, giao diện tiếng Việt và thời lượng

Nếu bạn gặp `This gguf file is incompatible with llama.cpp` tại H3 CLIP Loader với encoder Q2 của bộ cài, **không tải lại model**. File đó là native-key GGUF của H3, không phải llama.cpp GGUF. Nó chứa cả encoder văn bản và 351 tensor thị giác; không cần mmproj riêng. Loader mới `H3StudioNativeClipLoader` đọc trực tiếp định dạng này. Có một tensor Conv3D thị giác được sd.cpp dàn thành 4 chiều; loader khôi phục đúng shape 5 chiều của encoder chính thức. Không sửa metadata, không đổi tên file để giả định dạng, không patch global loader.

**Người đã cài:** xem hướng dẫn v0.3.0 ở đầu tài liệu; UPGRADE.bat tự cài workflow mới, không hiện hộp chọn JSON.

**Thời lượng:** ô `THỜI LƯỢNG CLIP (GIÂY)` nằm ngay trên prompt. Nhập 4–15 giây; đầu ra tự nối tới `length`. Ví dụ 15 giây → 362 frame (~15,08 giây); 5 giây → 124 frame (~5,17 giây). Đây là thời lượng clip nguồn, tách biệt nhịp từng shot trong prompt.

**Giao diện:** nhóm ảnh màu xanh lá; prompt/tham chiếu màu xanh lam; seed và sampling màu xanh ngọc; kết quả màu vàng; model nâng cao thu gọn phía dưới. Tiêu đề, nhãn cổng, nhãn widget và hướng dẫn tiếng Việt. Mã node/socket/tag Picture và prompt tiếng Anh giữ nguyên. Extension không đổi ngôn ngữ menu ComfyUI toàn hệ thống.

Kiểm tra hồi quy mới có bảo toàn ảnh/prompt/liên kết khi migrate, chống nhân đôi ô thời lượng, phát hiện thiếu vision và phát hiện nhầm GGUF llama.cpp. Header thật của encoder đã đối chiếu đủ 902 tên tensor với safetensors H3 chính thức; chưa có lần encode/render GPU sau bản sửa này.


## Bản vá v0.2.1: Python nhúng không tìm thấy install.py

Lỗi `ModuleNotFoundError: No module named install` đã được tái hiện với Python isolated mode. Sáu entry script hiện tự thêm đúng thư mục scripts của bộ cài vào sys.path trước khi import nội bộ. Không sửa pythonXY._pth, không cài module tên install qua pip. Tải lại source ZIP mới và chạy UPGRADE.bat trong thư mục vừa giải nén; không tải lại model.

31 bài kiểm tra CPU qua, gồm chạy repair thực tế trong Portable giả lập bằng `python -I`, sao lưu node và bảo toàn model. Đây vẫn chưa phải thử render GPU hoặc chạy trên Windows thật.


## Bản vá v0.2.2: tránh trùng module select của Python

Tiện ích chấm/chọn cấu hình đã đổi tên từ scripts/select.py sang scripts/choose_preset.py. Bootstrap hiện đặt thư mục scripts sau thư viện chuẩn và các module nhúng. repair.py cũng dùng portable_paths.py nhẹ, không import installer hoặc urllib để cập nhật node. Bản mới vẫn chạy được nếu bạn giải nén đè và còn file select.py cũ. Không cần tải lại model.

Cách sửa nhanh bản cũ: đổi tên scripts/select.py thành scripts/choose_preset.py rồi chạy lại UPGRADE.bat. Khi dùng CLI chọn cấu hình sau benchmark, dùng tên choose_preset.py.


