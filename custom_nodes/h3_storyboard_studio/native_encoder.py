"""Native-key sd.cpp H3 GGUF, distinct from llama.cpp text-encoder GGUF.
No on-disk conversion, architecture spoofing or global loader monkeypatch.
"""
import struct


def inspect_native_header(path):
    """Bounded metadata/directory validation without reading tensor payloads."""
    with open(path,'rb') as f:
        def read(n):
            if n<0 or n>1024*1024:raise ValueError('Invalid GGUF header length')
            b=f.read(n)
            if len(b)!=n:raise ValueError('Truncated GGUF header')
            return b
        if read(4)!=b'GGUF':raise ValueError('Not a GGUF file')
        version,count,metadata=struct.unpack('<IQQ',read(20))
        if version!=3 or metadata!=0 or not 500<=count<=2000:
            raise ValueError('This loader accepts only metadata-free native-key H3 encoders. Use a matching llama.cpp loader for other formats.')
        tensors={}
        for _ in range(count):
            size=struct.unpack('<Q',read(8))[0]
            name=read(size).decode('utf-8')
            nd=struct.unpack('<I',read(4))[0]
            if not 1<=nd<=5:raise ValueError('Invalid tensor rank')
            shape=tuple(reversed(struct.unpack('<'+'Q'*nd,read(8*nd))))
            quant,offset=struct.unpack('<IQ',read(12))
            if name in tensors:raise ValueError('Duplicate tensor name')
            tensors[name]=(shape,quant,offset)
        required={'model.embed_tokens.weight':(151936,5120),
                  'model.layers.0.self_attn.q_proj.weight':(8192,5120),
                  'model.layers.49.self_attn.q_proj.weight':(8192,5120)}
        for name,shape in required.items():
            if name not in tensors or tensors[name][0]!=shape:
                raise ValueError('Not the expected native-key H3 Qwen3-VL encoder: '+name)
        for name in ['visual.patch_embed.proj.weight','visual.pos_embed.weight',
                     'visual.blocks.0.attn.qkv.weight','visual.merger.linear_fc1.weight',
                     'visual.deepstack_merger_list.0.linear_fc1.weight']:
            if name not in tensors:raise ValueError('Embedded vision tower missing: '+name)
        return tensors


class H3StudioNativeClipLoader:
    @classmethod
    def INPUT_TYPES(cls):
        import pathlib
        import folder_paths
        files=[]
        for folder in folder_paths.get_folder_paths('text_encoders'):
            root=pathlib.Path(folder)
            if root.exists():files.extend(str(p.relative_to(root)) for p in root.rglob('*.gguf') if 'mmproj' not in p.name.lower())
        return {'required':{'clip_name':(sorted(set(files)),)}}
    RETURN_TYPES=('CLIP',)
    FUNCTION='load'
    CATEGORY='H3 Storyboard Studio'

    def load(self,clip_name):
        import sys,warnings
        import gguf
        import torch
        import folder_paths
        import nodes
        import comfy.sd
        import comfy.model_management
        path=folder_paths.get_full_path('text_encoders',clip_name)
        if path is None:raise ValueError('Encoder file not found: '+clip_name)
        directory=inspect_native_header(path)
        gg_cls=nodes.NODE_CLASS_MAPPINGS.get('CLIPLoaderGGUF')
        if gg_cls is None:raise RuntimeError('ComfyUI-GGUF is required. Restart ComfyUI after installation.')
        gg=sys.modules[gg_cls.__module__]
        loader=sys.modules[gg.gguf_clip_loader.__module__]
        reader=gguf.GGUFReader(path)
        sd={}
        for tensor in reader.tensors:
            name=tensor.name
            shape=torch.Size((1152,3,2,16,16) if name=='visual.patch_embed.proj.weight' else directory[name][0])
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore',message='The given NumPy array is not writable')
                raw=torch.from_numpy(tensor.data)
            if tensor.tensor_type in (gguf.GGMLQuantizationType.F32,gguf.GGMLQuantizationType.F16):raw=raw.reshape(shape)
            wrapped=loader.GGMLTensor(raw,tensor_type=tensor.tensor_type,tensor_shape=shape)
            if tensor.tensor_type==gguf.GGMLQuantizationType.BF16:
                # sd.cpp flattens the vision Conv3D to 4D. Restore the official
                # 5D shape and decode BF16 literals for ordinary conv/position ops.
                wrapped=loader.dequantize_tensor(wrapped,dtype=torch.float32 if len(shape)==1 else torch.float16)
            elif name=='visual.patch_embed.proj.weight':
                wrapped=loader.dequantize_tensor(wrapped,dtype=torch.float16)
            sd[name]=wrapped
        quantized={k:v for k,v in sd.items() if loader.is_quantized(v)}
        if quantized:sd[max(quantized,key=lambda k:quantized[k].numel())].is_largest_weight=True
        print('[H3 Studio] Native H3 encoder: embedded vision loaded; no separate mmproj needed.',flush=True)
        clip=comfy.sd.load_text_encoder_state_dicts(
            clip_type=comfy.sd.CLIPType.MINIMAX,state_dicts=[sd],
            model_options={'custom_operations':gg.GGMLOps,
                           'initial_device':comfy.model_management.text_encoder_offload_device()},
            embedding_directory=folder_paths.get_folder_paths('embeddings'))
        clip.patcher=gg.GGUFModelPatcher.clone(clip.patcher)
        return (clip,)
