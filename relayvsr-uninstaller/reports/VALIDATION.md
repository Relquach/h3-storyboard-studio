# Kiểm tra bộ gỡ RelayVSR 1.0.0

- 26 unit test thành công trên Linux/Python 3.12. Có xóa file thật trong các Portable tạm: chỉ hai model đúng tên, phần tải dở đúng suffix, node/runtime và backup Relay riêng.
- Kiểm tra giữ model H3, video, VHS, workflow đã sửa, SDK ngoài Portable/được node khác dùng; không theo symlink; không nhận mục xóa tự chèn; không báo hoàn tất khi file bị khóa hoặc SDK lỗi.
- Chạy preview bằng Python -I trong subprocess, file fixture còn nguyên.
- Chạy uninstall bằng Python -I hai lần trong subprocess: model/node fixture bị gỡ, H3/video/VHS còn nguyên, chạy lại không lỗi. SDK metadata được mô phỏng absent bằng executable fixture; không gỡ package thật của môi trường kiểm tra.
- Windows CIM process query và pip uninstall SDK được mô phỏng trong unit test. Chưa chạy BAT/PowerShell hoặc gỡ trên Windows thật; không có quyền truy cập máy người dùng. Không có test GPU vì đây là bộ gỡ file/package.
- Không thay đổi workflow gốc hoặc skill. Không gỡ driver/Torch/CUDA/ComfyUI core.
