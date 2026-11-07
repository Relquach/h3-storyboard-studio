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

Ảnh bạn cung cấp trong chat **không được đăng lên repo**. Ví dụ chỉ mô tả phong cách bằng chữ; để thử đúng, bạn cần chọn storyboard và character sheet do bạn tạo/duyệt từ ảnh đó. Bộ cài không tự có ảnh riêng trong cuộc trò chuyện và không tự huấn luyện LoRA nhân vật.

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
