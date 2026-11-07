import { app } from "/scripts/app.js";
const labels = {
    enabled:"Bật tham chiếu (tắt = bỏ qua)", name:"Tên tài sản", role:"Loại tham chiếu", seconds:"Thời lượng clip (giây)", clip_name:"Tệp encoder", model_name:"Tệp model", image:"Chọn ảnh", upload:"Tải ảnh lên",
    prompt:"Prompt tiếng Anh", roles_json:"Ánh xạ ảnh (JSON)", width:"Chiều rộng", height:"Chiều cao",
    length:"Số khung hình", ref_image_size:"Chi tiết ảnh: match / max", noise_seed:"Seed so sánh",
    control_after_generate:"Seed sau mỗi lượt", steps:"Số bước", scheduler:"Lịch lấy mẫu", denoise:"Mức khử nhiễu",
    sampler_name:"Thuật toán lấy mẫu", vae_name:"Tệp VAE", filename_prefix:"Thư mục / tên video",
    fps:"FPS", crf:"Mức nén CRF", batch_size:"Số frame mỗi lượt", strength_model:"Cường độ LoRA",
    lora_name:"Tệp LoRA", activation_reserve_gb:"VRAM dự phòng (0 = tự động)"
};
const allowed = new Set(["H3StudioExtraReference","H3StudioNativeModelLoader","H3StudioDuration","H3StudioNativeClipLoader","H3StudioReferences","H3StudioUpscale","H3StudioSaveVideo",
    "H3ModelLoaderAny","LoadImage","RandomNoise","BasicScheduler","KSamplerSelect","VAELoader","LoraLoaderModelOnly"]);
app.registerExtension({
    name:"H3StoryboardStudio.Vietnamese",
    async beforeRegisterNodeDef(nodeType,nodeData) {
        if (!allowed.has(nodeData.name)) return;
        const original=nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated=function(...args) {
            const result=original?.apply(this,args);
            for (const widget of this.widgets ?? []) {
                if (labels[widget.name]) widget.label=labels[widget.name];
                if (nodeData.name === "H3StudioReferences" && widget.name === "roles_json") {
                    widget.computeSize=()=>[0,0];
                    widget.hidden=true;
                }
            }
            return result;
        };
    }
});
