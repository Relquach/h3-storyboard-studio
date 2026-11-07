# Skill MiniMax H3 — dùng workflow gốc

Phiên bản2.0.0. Bám đúng file người dùng gửi ngày08/11/2026: `Finalworkflofacefixed (Natural Contrast)fixed.json` (SHA-256 đã ghi trong references). Đây là **bộ skill**, không phải bộ cài ComfyUI hay workflow đã xây lại.

## Cách dùng với Codex

Đưa cả thư mục `minimax-h3-film` vào nơi Codex của bạn đọc skill, hoặc gửi `SKILL.md` và các file tham chiếu vào cùng dự án. Khi gọi skill, có thể viết:

> Dùng skill minimax-h3-film với workflow gốc. Nội dung15giây: Lan ngồi trên bờ ruộng lúa chín lúc hoàng hôn, nhìn mây bồng bềnh, thấy một đám mây hình trái tim và mỉm cười. Video9:16,3D animation. Dùng sheet Lan đã duyệt; AI tự chọn góc máy và nhịp. Hãy tạo ảnh storyboard và prompt video cuối để dán vào ComfyUI.

Codex sẽ hỏi một lượt những tham chiếu/chi tiết thực sự còn thiếu, tự chia shot/giây/lưới, tạo storyboard nếu có công cụ được cho phép, kiểm tra ảnh, rồi giao prompt tiếng Anh và bảng nạp ảnh/bypass node. Không yêu cầu PREPARE hay bộ cài riêng. Không tự tạo ảnh trong lúc chỉ được yêu cầu sửa skill.

## Phần đã bổ sung

- Sơ đồ gốc: storyboard #27, ảnh phụ #28/#93/#104/#122/#135 → Ref2V#26; prompt#70; giây#23; tỷ lệ video#25.
- Ảnh thừa #93 đang bật trong file gốc phải được xử lý rõ. Bỏ ảnh ở giữa làm dồn Picture; prompt và bảng node phải đổi cùng lúc.
- Lưới linh hoạt, nhãn SHOT/hàng/cột, từng ô đúng tỷ lệ, động tác và trạng thái đầu–cuối, phân bổ giây không chia đều.
- Tạo **ảnh** storyboard bằng công cụ được cho phép, không chỉ trả prompt khi người dùng đã yêu cầu vẽ; không dùng Topview theo lựa chọn đã có.
- Hướng dẫn style3D: đề xuất bypass Realism#134 và bỏ trigger; giữ Turbo#10, không tự bật Licon/MotionRepair.
- Hai bước gốc: nháp/lưu take → duyệt → nạp take/nâng latent/refine/giữ màu/finishing. Đổi prompt mới không tự đổi take cũ.
- Ghi chú setup cho hai node Pixaroma và hai model đang báo thiếu trong ảnh; không biến tác vụ sáng tác thành cài lại hệ thống.
- Helper đọc wiring và sinh prompt/mapping/bảng thao tác từ một plan; **Codex dùng hộ**, người dùng không cần chạy. Helper không sửa JSON, cài dependency hoặc gọi server.

## Ví dụ đi kèm

`examples/lan-storyboard-prompt.txt`: prompt vẽ2×2,4shot.

`examples/lan-15s-handoff/video_prompt.txt`: prompt video cuối, dùng Picture1=storyboard, Picture2=sheetLan; thời gian4+3+5+3giây.

`examples/lan-15s-handoff/COMFYUI_HANDOFF.md`: bảng thao tác trên workflow gốc; bypass #93/#104/#122/#135,3D bypass#134. Tất cả tên ảnh trong ví dụ là tên đề xuất, không phải tuyên bố đã tạo ảnh trong lần sửa skill này. Cần có ảnh thật tương ứng và đặt đúng bảng trước khi chạy.

`examples/lan-15s.plan.json`: dữ liệu nội bộ minh họa cho Codex. Token ref/start/end trong plan được helper chuyển thành bản cuối; **không dán plan hoặc template token vào ComfyUI**.

## Kiểm tra

Đã đối chiếu75node/99link và hash file gốc; có kiểm tra hồi quy cho mapping, bỏ ảnh giữa, storyboard-only, timestamp và bảo toàn JSON. Chạy kiểm tra tác giả bằng `python -m unittest discover -s tests -v`; dùng helper tùy chọn: `python scripts/compile_handoff.py examples/lan-15s.plan.json --out output`.

Bản skill này không có benchmark/renderGPU mới. Kiểm tra prompt/mapping không chứng nhận cài ComfyUI, giữ khuôn mặt hoặc tốc độ trên RTX4060Ti. Công cụ tạo ảnh/video còn tùy phiên Codex đang dùng. Bản JSON gốc được giữ nguyên; ghi chú trong nó là tài liệu tham khảo.
