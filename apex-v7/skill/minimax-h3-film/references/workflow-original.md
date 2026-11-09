> PHẠM VI: profile `singularity_original_ref2v` trong bản skill v3. Không áp các ID, Picture, Turbo LoRA hoặc quy trình take này cho FastH3 I2V. Đọc SKILL.md và workflow-mode-routing.md trước.

# Workflow gốc: hợp đồng node và dây nối

Nguồn: `Finalworkflofacefixed (Natural Contrast)fixed.json`, lưu nguyên vẹn tại `original-workflow.json`. SHA-256: `983157859d1a043eb7800f0177e6a05234be36a155323a6e3f791c1e1ec6a2ef`. Có 75 node, 99 link; workflow ID `47d01687-55c3-494f-b9b2-7057b4c774a1`. Nếu export mới đổi wiring/ID, đọc lại và lấy bản mới làm nguồn. Không suy ra trạng thái ComfyUI đang mở chỉ từ snapshot này.

## Input ảnh của Ref2V #26

Đây là thứ tự **socket**, không phải số Picture cố định trong mọi cấu hình:

| Slot | Nguồn LoadImage | Đích #26 | Mode lưu trong bản gốc | Nội dung mới đề xuất |
|---|---|---|---|---|
| 0 | #27 | ref_images.ref_image_0 | Bật | Nguyên storyboard |
| 1 | #28 | ref_images.ref_image_1 | Bật | Sheet CHAR_01 nếu dùng |
| 2 | #93 | ref_images.ref_image_2 | **Bật** | Sheet CHAR_02 / set / prop nếu dùng; không dùng thì bypass |
| 3 | #104 | ref_images.ref_image_3 | Bypass | Tài sản tiếp theo nếu cần |
| 4 | #122 | ref_images.ref_image_4 | Bypass | Tài sản tiếp theo nếu cần |
| 5 | #135 | ref_images.ref_image_5 | Bypass | Tài sản tiếp theo nếu cần |

Mode 0=bật, mode 4=bypass. `image` chọn đúng ảnh thật trên máy; tên trong JSON gốc chỉ là ảnh dự án mẫu. Không gán `lo3.png` thành storyboard đã tạo của người dùng. #21 và #22 là ảnh đầu/cuối của MiniMaxH3ImageToVideo #20, mặc định bypass; không dùng chúng cho storyboard nguyên trang.

Core Ref2V bỏ các ảnh None và đưa ảnh hợp lệ vào presentation theo thứ tự còn lại. Với wiring gốc này, sau khi bỏ qua ảnh:

| Các loader thực sự hoạt động | Cách gọi trong prompt |
|---|---|
| #27 | Picture 1 = storyboard; không có Picture 2 |
| #27, #28 | Picture 1 = storyboard; Picture 2 = tài sản ở #28 |
| #27, #93; #28 bypass | Picture 1 = storyboard; Picture 2 = tài sản ở #93 |
| #27, #28, #104; #93 bypass | Picture 1 = storyboard; Picture 2 = #28; Picture 3 = #104 |

Mỗi lần đổi file/slot/bypass, cập nhật bảng **và** sinh lại prompt. Bypass không thể tự sửa chữ trong PrimitiveStringMultiline #70. #27 không được bỏ nếu lượt đó yêu cầu storyboard. Tránh để ảnh thừa active nhưng “không nhắc tới” vì model vẫn nhận nó.

## Widget và đường điều khiển

| Node | Vai trò / giá trị thực trong JSON gốc |
|---|---|
| #70 PrimitiveStringMultiline | Prompt dùng chung → #26 prompt và #20 prompt. Dán nguyên prompt video cuối ở đây; không dán vào widget prompt đang được socket điều khiển ở #26 |
| #62 PrimitiveBoolean | true = nhánh B Ref2V; false = nhánh A text/image/first-last |
| #23 PrimitiveFloat | 15 giây đã lưu; nơi chỉnh thời lượng clip |
| #24 ComfyMathExpression | `max(5, round(a * 24)) + (5 - (max(5, round(a * 24)) % 17)) % 17`; output INT → length #26, #159 và #20 |
| #25 ResolutionSelector | **16:9 (Widescreen), 0.7 MP, multiple 32**; output width/height → EmptyMiniMaxH3LatentAV #159 |
| #26 MiniMaxH3ReferenceToVideo | Vùng tham chiếu riêng **1792×992**, ref_image_size=match; tạo conditioning từ ảnh/chuỗi prompt |
| #159 EmptyMiniMaxH3LatentAV | Latent video lấy kích thước từ #25; qua switch #61 khi Ref2V bật |
| #30 RandomNoise | Seed `503018822422051`, chế độ **randomize**; nếu cần so sánh, đề xuất chuyển fixed và ghi seed dùng, không nói seed đã cố định mặc định |
| #32 BasicScheduler | `simple`, **6 bước**, denoise 1.0; tiêu đề “steps (10)” không phải giá trị thực |
| #31 / #118 KSamplerSelect | `er_sde` cho nháp và refine |
| #145 MiniMaxH3SigmaShift | 6 / 3 |
| #105 PrimitiveBoolean | false = tạo nháp / lưu take; true = nạp take / nâng |
| #123 H3TakeSave | Lưu latent pass 1 và conditioning vào output/h3_takes |
| #124 H3TakeLoad | latest hoặc take cụ thể. Khi nhiều lượt dùng tên cụ thể để tránh nâng nhầm |
| #120 MMH3UltimateUpscale | Latent và conditioning lấy **từ #124**, không lấy prompt mới #70 |
| #107 H3UpscaleSizeLD | Target **2 MP** trong JSON, không phải 0.7 MP của bản cài dẫn xuất |
| #109 PrimitiveBoolean | true = model H3 latent 3D, false = nội suy |
| #113 MMH3TemporalSplitParams | chunk_length **102**, overlap 17, anchor 0.999 |
| #114 PrimitiveBoolean | false = không chia ô không gian; nếu bật để tránh OOM, tác giả yêu cầu sampler refine #118 sang euler |
| #119 ManualSigmas | `0.5500, 0.4200, 0.3158, 0.1579, 0.0000` |
| #142 ColorTransfer | mkl_lab, uniform, strength 1; qua switch #143 chỉ dùng ở bước 2 |
| #144 / #147 VideoFinishDetailTone | Finishing + Clarity sau decode; không phải face replacement hoặc face identity lock |
| #139 / #43 | CreateVideo 24 FPS + audio; SaveVideo MP4/H.264, re-encode, CRF 12 |

**Ghi chú không trùng giá trị thực:** nhiều note viết nháp 0.2 MP/4 bước nhưng file đang lưu 0.7 MP/6 bước. Không nhận đã đặt 0.2/4 chỉ vì note đó. Bản gốc dùng VAE video INT8; README ngoài file từng ghi FP16. Giữ model theo node người dùng dùng, giải thích tùy chọn thay vì tự thay.

Vùng width/height #26 dùng để điều tiết độ chi tiết ảnh reference; kích thước video nháp lấy từ #25/#159. Không bảo người dùng đổi #26 thành 9:16 để đổi tỷ lệ clip. Với video dọc đặt #25 = `9:16 (Portrait Widescreen)`, vẫn multiple 32. Chỉ giảm vùng #26 khi có lý do về token/VRAM, nêu trade-off mặt nhỏ trong sheet.

## Model / LoRA / attention của bản gốc

- #1 UNETLoader: `Minimax-h3_Singularity_ref2va_v2_pruned_int8.safetensors`.
- #2 CLIPLoader: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`, type minimax.
- #3 VAELoader: `minimax_h3_video_vae_int8_convrot.safetensors`.
- #4 VAELoader: `minimax_h3_audio_vae_fp32.safetensors`.
- #10 Turbo: `minimax_h3_ref2v_lightx2v_turbo_4step_v0.1_resized_avg_rank_20_bf16.safetensors`, strength 1, bật. Không đánh đồng tên 4step với việc scheduler hiện đặt 4 bước.
- #134 Realism People, strength 0.75, **bật**. Với 3D animation đề xuất bypass node này và bỏ `r34l1sm` khỏi prompt; không thay nhầm Turbo #10.
- #133 Licon 0.9 / #137 Motion Repair 0.8: bypass. Không tự bật vì tên hứa “motion repair”.
- #11 ModelAttentionBackend: comfy kitchen attention, bật; #12 BlockSparseAttention: sol-attn, tau1.3, start0.2, bật. Tính tương thích phụ thuộc GPU/PyTorch/kernel thực tế. Khi báo lỗi backend mới đối chiếu rồi đề xuất bypass tương ứng, không tự thay toàn bộ stack.

Bộ cài dẫn xuất cũ từng thay đổi các giá trị/nodes trên. Skill hiện tại lấy **bản gốc này**, không lấy các mặc định của bộ cài cũ.
