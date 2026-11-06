"""Small reference-order adapter; all diffusion work remains in ComfyUI H3."""
import json
import re


def compose(prompt, roles, count):
    names = json.loads(roles)
    if not isinstance(names, list) or len(names) != count or not all(isinstance(s, str) and s.strip() for s in names):
        raise ValueError('Reference roles must contain one nonempty name per connected image, storyboard first.')
    for n in re.findall(r'<Picture (\d+)>', prompt):
        if not 1 <= int(n) <= count:
            raise ValueError(f'Prompt references missing Picture {n}')
    mapping = '\n'.join(f'<Picture {i+1}>: {name}' for i, name in enumerate(names))
    return ('REFERENCE INPUT ORDER (do not exchange identities):\n' + mapping + '\n\n' + prompt)


class H3StudioReferences:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'clip': ('CLIP',), 'vae': ('VAE',), 'audio_vae': ('VAE',),
            'storyboard': ('IMAGE',),
            'prompt': ('STRING', {'multiline': True}),
            'roles_json': ('STRING', {'default': '["Storyboard: chronological panels"]'}),
            'width': ('INT', {'default': 640, 'min': 32, 'max': 2048, 'step': 32}),
            'height': ('INT', {'default': 384, 'min': 32, 'max': 2048, 'step': 32}),
            'length': ('INT', {'default': 124, 'min': 5, 'max': 362, 'step': 17}),
            'ref_image_size': (['match', 'max'],),
        }, 'optional': {'character_1': ('IMAGE',), 'character_2': ('IMAGE',), 'character_3': ('IMAGE',)}}
    RETURN_TYPES = ('CONDITIONING', 'LATENT', 'STRING')
    RETURN_NAMES = ('positive', 'av_latent', 'resolved_prompt')
    FUNCTION = 'encode'
    CATEGORY = 'H3 Storyboard Studio'

    def encode(self, clip, vae, audio_vae, storyboard, prompt, roles_json, width, height, length,
               ref_image_size='match', character_1=None, character_2=None, character_3=None):
        from comfy_extras.nodes_minimax_h3 import MiniMaxH3ReferenceToVideo
        if length % 17 != 5 or not 5 <= length <= 362:
            raise ValueError('Use H3 frame grid 17n+5, at most 362 frames for this package.')
        chars = [character_1, character_2, character_3]
        connected = [v is not None for v in chars]
        if connected != sorted(connected, reverse=True):
            raise ValueError('Connect characters in order without gaps.')
        images = [storyboard] + [v for v in chars if v is not None]
        resolved = compose(prompt, roles_json, len(images))
        refs = {f'ref_image_{i}': im for i, im in enumerate(images)}
        result = MiniMaxH3ReferenceToVideo.execute(clip=clip, vae=vae, audio_vae=audio_vae,
                    prompt=resolved, width=width, height=height, length=length,
                    ref_image_size=ref_image_size, ref_images=refs)
        return (*result.result, resolved)


class H3StudioUpscale:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'images': ('IMAGE',), 'upscale_model': ('UPSCALE_MODEL',),
                             'batch_size': ('INT', {'default': 1, 'min': 1, 'max': 8})}}
    RETURN_TYPES = ('IMAGE',)
    FUNCTION = 'run'
    CATEGORY = 'H3 Storyboard Studio'

    def run(self, images, upscale_model, batch_size):
        import torch
        from comfy_extras.nodes_upscale_model import ImageUpscaleWithModel
        # CPU accumulation prevents all decoded upscaled frames remaining on GPU.
        out = []
        for start in range(0, images.shape[0], batch_size):
            batch = images[start:start + batch_size]
            out.append(ImageUpscaleWithModel().upscale(upscale_model, batch)[0].cpu())
        return (torch.cat(out, dim=0),)


NODE_CLASS_MAPPINGS = {'H3StudioReferences': H3StudioReferences, 'H3StudioUpscale': H3StudioUpscale}
NODE_DISPLAY_NAME_MAPPINGS = {'H3StudioReferences': 'H3 Studio — Storyboard + Ordered Characters',
                             'H3StudioUpscale': 'H3 Studio — Upscale Frames in Small Batches'}


class H3StudioSaveVideo:
    """Stable legacy UI inputs around the core Video object, no DynamicCombo version coupling."""
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'images': ('IMAGE',), 'audio': ('AUDIO',),
                'filename_prefix': ('STRING', {'default':'h3studio/video'}),
                'fps': ('FLOAT', {'default':24.0,'min':1.0,'max':60.0}),
                'crf': ('INT', {'default':18,'min':0,'max':51})}}
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = 'save'
    CATEGORY = 'H3 Storyboard Studio'

    def save(self, images, audio, filename_prefix, fps, crf):
        import os
        import pathlib
        import folder_paths
        from comfy_extras.nodes_video import CreateVideo
        from comfy_api.latest import Types
        if pathlib.PurePosixPath(filename_prefix.replace('\\','/')).is_absolute() or '..' in filename_prefix.replace('\\','/').split('/') or ':' in filename_prefix:
            raise ValueError('Output prefix must stay within the output directory.')
        video=CreateVideo.execute(images=images,audio=audio,fps=fps).result[0]
        width,height=video.get_dimensions()
        directory,name,counter,subfolder,_=folder_paths.get_save_image_path(filename_prefix,folder_paths.get_output_directory(),width,height)
        file=f'{name}_{counter:05}_.mp4'
        video.save_to(os.path.join(directory,file),format=Types.VideoContainer('mp4'),codec=Types.VideoCodec('h264'),metadata=None,crf=crf)
        return {'ui':{'videos':[{'filename':file,'subfolder':subfolder,'type':'output'}]}}


NODE_CLASS_MAPPINGS['H3StudioSaveVideo']=H3StudioSaveVideo
NODE_DISPLAY_NAME_MAPPINGS['H3StudioSaveVideo']='H3 Studio — Save MP4 + Audio'
