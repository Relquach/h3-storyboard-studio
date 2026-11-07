"""Read native-key sd.cpp H3 DiT GGUF without llama.cpp architecture detection."""
import struct


def inspect_native_model_header(path):
    with open(path,'rb') as f:
        def read(n):
            if not 0<=n<=1024*1024:raise ValueError('Invalid tensor directory')
            b=f.read(n)
            if len(b)!=n:raise ValueError('Truncated GGUF directory')
            return b
        if read(4)!=b'GGUF':raise ValueError('Not GGUF')
        version,count,metadata=struct.unpack('<IQQ',read(20))
        if version!=3 or metadata!=0 or not 500<=count<=1000:
            raise ValueError('Expected native-key H3 pruned GGUF without llama.cpp metadata')
        tensors={}
        for _ in range(count):
            name=read(struct.unpack('<Q',read(8))[0]).decode()
            nd=struct.unpack('<I',read(4))[0]
            if not 1<=nd<=5:raise ValueError('Invalid tensor rank')
            shape=tuple(reversed(struct.unpack('<'+'Q'*nd,read(nd*8))))
            quant,offset=struct.unpack('<IQ',read(12))
            if name in tensors:raise ValueError('Duplicate tensor name')
            tensors[name]=(shape,quant,offset)
        expected={'video_patch_proj.weight':(5376,96),'audio_patch_proj.weight':(5376,32),
                  'blocks.0.attn.qkv_proj.weight':(21504,5376),
                  'blocks.49.attn.qkv_proj.weight':(21504,5376),'adaln_t_table':(1025,8)}
        for key,shape in expected.items():
            if key not in tensors or tensors[key][0]!=shape:raise ValueError('Wrong H3 native model layout: '+key)
        return tensors


class H3StudioNativeModelLoader:
    @classmethod
    def INPUT_TYPES(cls):
        import pathlib,folder_paths
        names=[]
        for folder in folder_paths.get_folder_paths('diffusion_models'):
            root=pathlib.Path(folder)
            if root.exists():names += [str(p.relative_to(root)) for p in root.rglob('*.gguf')]
        return {'required':{'model_name':(sorted(set(names)),)}}
    RETURN_TYPES=('MODEL',)
    FUNCTION='load'
    CATEGORY='H3 Storyboard Studio'

    def load(self,model_name):
        import sys,warnings
        import gguf,torch,folder_paths,nodes,comfy.sd
        path=folder_paths.get_full_path('diffusion_models',model_name)
        if not path:raise ValueError('Model file not found: '+model_name)
        shapes=inspect_native_model_header(path)
        cls=nodes.NODE_CLASS_MAPPINGS.get('UnetLoaderGGUF')
        if cls is None:raise RuntimeError('ComfyUI-GGUF not loaded')
        gg=sys.modules[cls.__module__];loader=sys.modules[gg.gguf_sd_loader.__module__]
        reader=gguf.GGUFReader(path);sd={}
        for tensor in reader.tensors:
            shape=torch.Size(shapes[tensor.name][0])
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore',message='The given NumPy array is not writable')
                raw=torch.from_numpy(tensor.data)
            if tensor.tensor_type in (gguf.GGMLQuantizationType.F32,gguf.GGMLQuantizationType.F16):raw=raw.reshape(shape)
            value=loader.GGMLTensor(raw,tensor_type=tensor.tensor_type,tensor_shape=shape)
            if tensor.tensor_type==gguf.GGMLQuantizationType.BF16:
                value=loader.dequantize_tensor(value,dtype=torch.float32 if len(shape)==1 else torch.float16)
            sd[tensor.name]=value
        quantized={k:v for k,v in sd.items() if loader.is_quantized(v)}
        if quantized:sd[max(quantized,key=lambda k:quantized[k].numel())].is_largest_weight=True
        # Native names/shapes match the official pruned BF16 state_dict exactly.
        # Core model detection sees the state_dict, not fake GGUF metadata.
        model=comfy.sd.load_diffusion_model_state_dict(sd,model_options={'custom_operations':gg.GGMLOps()})
        if model is None:raise RuntimeError('ComfyUI core could not detect H3. Check ComfyUI native H3 support/version.')
        model=gg.GGUFModelPatcher.clone(model)
        model.patch_on_device=False
        return (model,)
