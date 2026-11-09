# 1.0.0 · 09/11/2026

- Giữ nguyên JSON công khai Apex H3 V7 trong source; SHA256 ghi trong manifest.
- Tạo preset hai chặng H3 và preset ba chặng H3 + LTX2.5, tỷ lệ dọc.
- Bỏ nhánh Qwen8B, switch/concat duration và preview LLM để prompt đã duyệt đi thẳng từ #138 tới #136. Không tải model LLM không được dùng.
- Nối thật ba loader phụ vào ref_image_1/2/3; mặc định bypass. Bảng Picture được tính lại theo ảnh bật thật.
- Bỏ RealismPeople khỏi nhánh refine; LTX positive giữ 3D Á Đông, negative không phủ định cartoon/CGI. Cinematic chỉ là nguồn tham khảo tùy chọn, không tự cài.
- Giữ audio H3 nền ở #7385 và #9259. Không có cam kết sửa phát âm/lip-sync.
- Sửa Upscaler3D theo schema source pinned; dùng model conv_v1 BF16 đã đối chiếu header, không giả có tùy chọn chunk/unload.
- Ghi đúng ManualSigmas bốn mốc là ba khoảng denoise. Giữ Spectrum20 bước lịch; không gọi đó là20 model evaluation đầy đủ.
- Điều chỉnh CreateVideo widget theo core khi sao chép; giữ codec=none cho VIDEO trung gian. MP4 do VHS lưu.
- Việt hóa nhãn chính, chia nhóm theo luồng, tách rõ thời lượng #132 và tỷ lệ #115/#7346/#9411.
- Skill v4 ưu tiên Apex V7, duyệt storyboard trước prompt, giữ profile cũ riêng; helper mới có chặn duyệt và đọc dây Reroute/bypass thật.
