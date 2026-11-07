# Prompt và bàn giao trực tiếp cho workflow gốc

Một lượt render có một prompt đầy đủ để dán vào #70. Không yêu cầu người dùng chạy code để biến đổi token. `<Picture N>` trỏ đúng ảnh đang truyền qua Ref2V; `<Subject N>` là chủ thể do văn bản định nghĩa. Ví dụ Picture1=storyboard nhiều ô, Picture2=sheetLan, Subject1=Lan, Subject2=đồnglúa: số Subject2 không có nghĩa là Picture2.

## Khung sáu phần

```text
subject_definitions:
<Picture 1> is the entire storyboard contact sheet: [resolved grid, exact panel labels and row-major positions]. It is a sequential shot plan, not a first-frame split screen.
<Subject 1> is [name and stable identity], matched to [the correct active Picture or the character depicted in Picture 1]. [Exact outfit and props.]
[Other subjects and active reference roles.]

summary:
[reference generation] [Complete concrete action and emotional arc over this run.] Animate the labeled panels as chronological full-frame shots.

retention_analysis:
[For each subject: where it appears, what remains constant and what changes.] Repeated appearances across storyboard panels show the same individual; multi-view sheets do not create extra people. Use the actual setting in close-ups, not sheet backgrounds.

detailed_description:
[Resolved visual style, lighting, palette and setting.]
[SHOT N] 00:00.000 to [first end], [row/column]. [Framing and angle; people present/absent, positions, gaze, action, expression, one camera move and end state.]
[SHOT N+1] At [cut time], cut to [row/column and fully described next shot]. [Action and end state.]
[Every remaining populated panel exactly once.]
Render each shot as one full-frame cinematic image. Exclude contact-sheet layout, borders, gutters, SHOT captions, split screens, character-sheet backgrounds, unintended subtitles and watermarks.

overall_soundscape:
[Concrete ambience and SFX. Exact dialogue, speaker and timing if requested. Otherwise no dialogue/narration.]

non_diegetic_music:
[Requested music or N/A.]
```

Đây là khung cho tác giả skill; bản bàn giao cuối phải thay mọi chỗ điền. Không khẳng định `[reference generation]` hay sáu header là API/parser chính thức; chúng là cách tổ chức văn bản theo prompt gốc. Picture là cú pháp tham chiếu có trong core.

Giữ prompt có liên hệ với từng panel thật. Nếu ảnh tạo ra khác kế hoạch, sửa storyboard trước hoặc cập nhật kế hoạch có giải thích, không mô tả vật thể không xuất hiện rồi nói đã kiểm tra. Không yêu cầu đồ vật đứng yên ở ô A nhưng bay ở video nếu không có dụng ý.

## Bảng thao tác cho người dùng

Sau prompt, chỉ cần một bảng vừa đủ:

| Node gốc | Điền / thao tác |
|---|---|
| #27 LoadImage | Chọn storyboard vừa tạo, nguyên trang |
| #28 LoadImage | Chọn sheet đúng CHAR_01 nếu dùng |
| #93/#104/#122/#135 | Nạp tài sản thực sự cần hoặc bypass đúng danh sách của lượt |
| #70 PROMPT | Dán nguyên khối prompt video tiếng Anh đã resolve |
| #62 USE REFERENCE IMAGES | true |
| #23 duration | Số giây kế hoạch của lượt, không phải số shot |
| #25 aspect_ratio | Đúng tỷ lệ video; multiple32; megapixels theo lựa chọn thực tế |
| #134 Realism People | Bypass nếu làm3D animation; bỏ trigger r34l1sm khỏi prompt |
| #105 STEP | false để tạo nháp; true để nâng take đã duyệt |
| #124 which take | Tên take đúng; latest chỉ khi biết chắc take mới nhất là lượt cần |

Không cần đưa toàn bộ node model/sampler vào bảng mỗi lần nếu không thay. Bảng là yêu cầu cấu hình cần áp dụng, không chứng nhận trạng thái máy từ xa. Sau khi người dùng bypass/đổi ảnh, Codex phải sinh lại prompt và bảng số Picture, không chỉ đổi vài số bằng tìm-thay tuần tự gây dây chuyền.

## Lưu hồ sơ tùy chọn

Nếu người dùng muốn dự án nhiều tập, Codex có thể tự lưu:

- `project_bible.md`: identities / outfits / set map / tone / voice.
- `shot_plan.json` hoặc `.md`: panel labels, rows/cols, seconds and per-run continuity.
- `storyboard_prompt.txt`, ảnh storyboard thực tế và bản sửa nếu có.
- `video_prompt.txt`: bản cuối dán được, chỉ dùng Picture đã resolve.
- `mapping.csv`, `COMFYUI_HANDOFF.md`: node/source/socket/reference number và các thao tác.
- `take_log.csv`: run, prompt version, storyboard version, active assets, seed, source seconds, take name and review status. Chỉ ghi tên take đã quan sát, không tự bịa take00007.

Helper `scripts/compile_handoff.py` nhận một plan nội bộ và chỉ xuất prompt/mapping/table; người dùng không cần chạy nó. Không nhận helper đã sửa file workflow hoặc đảm bảo pixel identity. Dữ liệu nội bộ chưa resolve không phải thứ cần dán vào ComfyUI.
