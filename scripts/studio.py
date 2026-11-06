"""Build API and importable UI workflows from one project; no ComfyUI imports required."""

# Portable bootstrap: pythonXY._pth may omit the script directory.
# Add only this trusted package directory; never change global Python settings.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
import argparse
import copy
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODELS = {
 'dit': 'minimax_h3_ref2va_pruned-Q3_K.gguf',
 'clip': 'qwen3vl_32b_minimax_h3-Q2_K_M.gguf',
 'vae': 'minimax_h3_video_vae_fp16.safetensors',
 'audio': 'minimax_h3_audio_vae_fp32.safetensors',
 'turbo': 'minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors',
 'upscale': 'RealESRGAN_x2plus.pth',
}
STYLE = ('Stylized 3D animated film, large expressive eyes, softly shaded skin, finely detailed hair, '
         'delicate jewelry, soft cinematic lighting. Preserve the reference character design and facial proportions; '
         'do not turn characters into live-action humans.')


def validate(project):
    for key in ['episode_id', 'storyboard', 'characters', 'shots', 'width', 'height', 'seed']:
        if key not in project: raise ValueError('Missing project key: ' + key)
    if not re.fullmatch(r'[A-Za-z0-9_-]+', project['episode_id']): raise ValueError('Unsafe episode ID')
    if not isinstance(project['seed'], int) or not 0 <= project['seed'] < 2**64: raise ValueError('Invalid seed')
    if not isinstance(project['characters'], list) or len(project['characters']) > 3:
        raise ValueError('This package supports up to three character sheets per run.')
    names = [c['id'] for c in project['characters']]
    if len(names) != len(set(names)): raise ValueError('Duplicate character IDs')
    for dim in ['width', 'height']:
        if not isinstance(project[dim], int) or project[dim] % 32 or not 32 <= project[dim] <= 2048:
            raise ValueError('Dimensions must be multiples of 32, between 32 and 2048')
    rows, cols = project.get('grid', [2, 3])
    if not isinstance(rows, int) or not isinstance(cols, int) or min(rows, cols) < 1: raise ValueError('Invalid grid')
    ids, total = set(), 0.0
    if not project['shots'] or len(project['shots']) > rows * cols: raise ValueError('Shot count exceeds grid')
    for s in project['shots']:
        if s['id'] in ids: raise ValueError('Duplicate shot IDs')
        ids.add(s['id'])
        if not isinstance(s['seconds'], (int, float)) or not math.isfinite(s['seconds']) or s['seconds'] <= 0:
            raise ValueError('Shot duration must be finite and positive')
        if not s['description'].strip(): raise ValueError('Empty shot description')
        total += s['seconds']
    # Stay in the documented local range, not the user's upper ceiling of 30s.
    if not 4 <= total <= 15: raise ValueError('Each local run must total 4–15 seconds; split longer episodes.')
    return rows, cols, total


def make_prompt(p):
    rows, cols, total = validate(p)
    roles = [f'Storyboard, {rows} rows by {cols} columns: chronological shot order, staging, actions and setting.']
    roles += [f'{c["id"]}, {c["name"]}: {c["description"]}. Identity reference only; not another story panel.' for c in p['characters']]
    subjects = [f'<Subject {i+1}> is {c["name"]} ({c["id"]}), matching <Picture {i+2}>: {c["description"]}.' for i,c in enumerate(p['characters'])]
    subjects += [f'<Picture 1> is the complete {rows} by {cols} storyboard, not a start-frame collage. '
                 'Read left to right, then row by row. Repeated appearances across panels are the same characters, not extra people.']
    detailed = [p.get('style', STYLE)]
    t = 0.0
    for i,s in enumerate(p['shots']):
        r,c = divmod(i,cols)
        cut = '' if i == 0 else f'At 00:{t:06.3f}, cut to '
        detailed.append(f'[Shot {i+1}] {cut}storyboard panel row {r+1}, column {c+1}, labeled {s["id"]}. '
                        f'{s["description"]} Planned duration {s["seconds"]} seconds.')
        t += s['seconds']
    detailed.append('Render sequential full-screen shots, never a grid or split-screen. Do not reproduce panel labels, '
                    'borders, sheet layouts or white studio backgrounds. Preserve character count, facial identity, '
                    'clothes and props. Clear natural-speed action; no unintended slow motion. No subtitles or watermarks.')
    text = ('subject_definitions:\n' + '\n'.join(subjects) + '\n\nsummary:\n[reference generation] ' + p.get('summary','Follow the chronological storyboard.') +
            '\n\nretention_analysis:\nPreserve each character identity and design from its assigned sheet. '
            'Use storyboard panels for composition and action order, not a multi-panel output.\n\ndetailed_description:\n' + '\n'.join(detailed) +
            '\n\noverall_soundscape:\n' + p.get('sound','Only scene ambience and physical action sounds. No speech.') +
            '\n\nnon_diegetic_music:\nN/A')
    return text, roles


def build(p, preset='baseline', enhance=False):
    _,_,seconds = validate(p)
    text, roles = make_prompt(p)
    frames = math.ceil((round(seconds*24)-5)/17)*17+5
    frames = min(362,max(107,frames))
    g={}
    def add(i,typ,**inputs): g[str(i)]={'class_type':typ,'inputs':inputs}
    def link(i,o=0): return [str(i),o]
    add(1,'H3ModelLoaderAny',model_name=MODELS['dit'],activation_reserve_gb=0.0)
    add(2,'H3StudioNativeClipLoader',clip_name=MODELS['clip'])
    add(3,'VAELoader',vae_name=MODELS['vae']); add(4,'VAELoader',vae_name=MODELS['audio'])
    add(5,'LoadImage',image=p['storyboard'])
    add(9,'H3StudioDuration',seconds=float(seconds))
    ref={'clip':link(2),'vae':link(3),'audio_vae':link(4),'storyboard':link(5),
         'prompt':text,'roles_json':json.dumps(roles,ensure_ascii=False),'width':p['width'],'height':p['height'],
         'length':link(9),'ref_image_size':p.get('reference_size','match')}
    for i,c in enumerate(p['characters']):
        add(6+i,'LoadImage',image=c['file']);ref[f'character_{i+1}']=link(6+i)
    add(10,'H3StudioReferences',**ref)
    model=link(1)
    if preset=='turbo4':
        add(11,'LoraLoaderModelOnly',model=model,lora_name=MODELS['turbo'],strength_model=1.0);model=link(11)
    elif preset!='baseline':raise ValueError('Unknown preset')
    add(12,'BasicGuider',model=model,conditioning=link(10))
    add(13,'RandomNoise',noise_seed=p['seed'])
    add(14,'KSamplerSelect',sampler_name='euler' if preset=='turbo4' else 'res_multistep')
    add(15,'BasicScheduler',model=model,scheduler='simple' if preset=='turbo4' else 'beta',steps=4 if preset=='turbo4' else 20,denoise=1.0)
    add(16,'SamplerCustomAdvanced',noise=link(13),guider=link(12),sampler=link(14),sigmas=link(15),latent_image=link(10,1))
    add(17,'VAEDecode',samples=link(16),vae=link(3)); add(18,'VAEDecodeAudio',samples=link(16),vae=link(4))
    prefix=f'h3studio/{p["episode_id"]}_{preset}_{p["seed"]}'
    add(20,'H3StudioSaveVideo',images=link(17),audio=link(18),fps=24.0,filename_prefix=prefix,crf=18)
    if enhance:
        add(21,'UpscaleModelLoader',model_name=MODELS['upscale'])
        add(22,'H3StudioUpscale',images=link(17),upscale_model=link(21),batch_size=1)
        add(24,'H3StudioSaveVideo',images=link(22),audio=link(18),fps=24.0,filename_prefix=prefix+'_upscaled',crf=18)
    return g


# UI conversion is grounded in real object_info from the user's running ComfyUI.
# This also rejects missing nodes / invalid enum values before queueing anything.
def check_schema(g, info):
    for nid,n in g.items():
        if n['class_type'] not in info:raise ValueError('Missing node: '+n['class_type'])
        schema=info[n['class_type']]['input']
        definitions={**schema.get('required',{}),**schema.get('optional',{})}
        for key in schema.get('required',{}):
            if key not in n['inputs']:raise ValueError(f'{nid}: missing {key}')
        for k,v in n['inputs'].items():
            if k not in definitions:raise ValueError(f'{nid}: unknown input {k}')
            if isinstance(v,list) and len(v)==2 and isinstance(v[0],str) and isinstance(v[1],int):
                if v[0] not in g:raise ValueError('Dangling link')
                outs=info[g[v[0]]['class_type']]['output']
                if not 0<=v[1]<len(outs):raise ValueError('Output index out of bounds')
                expected=definitions[k][0]
                if isinstance(expected,str) and expected!='*' and outs[v[1]]!=expected:
                    raise ValueError(f'{nid}.{k}: expected {expected}, got {outs[v[1]]}')
            elif isinstance(definitions[k][0],list) and v not in definitions[k][0]:
                raise ValueError(f'{nid}.{k}: unsupported value {v}')


def to_ui(g,info):
    check_schema(g,info)
    nodes=[];links=[];by_id={}
    for index,(nid,n) in enumerate(g.items()):
        typ=n['class_type']; meta=info[typ];schema=meta['input']
        node={'id':int(nid),'type':typ,'pos':[index%4*420,index//4*350],'size':[370,290],
              'flags':{},'order':index,'mode':0,'inputs':[],'outputs':[],
              'properties':{'Node name for S&R':typ},'widgets_values':[]}
        for k,d in {**schema.get('required',{}),**schema.get('optional',{})}.items():
            v=n['inputs'].get(k);t=d[0];opts=d[1] if len(d)>1 else {}
            linked=isinstance(v,list) and len(v)==2 and isinstance(v[0],str) and isinstance(v[1],int)
            primitive=isinstance(t,list) or t in ['INT','FLOAT','BOOLEAN','STRING','COMBO']
            if not primitive or linked:
                entry={'name':k,'type':t if isinstance(t,str) else 'COMBO','link':None}
                if primitive:entry['widget']={'name':k}
                node['inputs'].append(entry)
            if primitive:
                default=(t[0] if isinstance(t,list) and t else opts.get('default',''))
                node['widgets_values'].append(v if v is not None and not linked else default)
                if opts.get('control_after_generate'):node['widgets_values'].append('fixed')
        for j,t in enumerate(meta['output']):
            name=meta.get('output_name',meta['output'])[j]
            node['outputs'].append({'name':name,'type':t,'links':[]})
        if typ=='LoadImage':node['widgets_values'].append('image')
        nodes.append(node);by_id[nid]=node
    for nid,n in g.items():
        for k,v in n['inputs'].items():
            if isinstance(v,list) and len(v)==2 and isinstance(v[0],str) and isinstance(v[1],int):
                dest=by_id[nid];src=by_id[v[0]]
                slot=next(i for i,x in enumerate(dest['inputs']) if x['name']==k)
                num=len(links)+1;typ=src['outputs'][v[1]]['type']
                links.append([num,int(v[0]),v[1],int(nid),slot,typ])
                src['outputs'][v[1]]['links'].append(num);dest['inputs'][slot]['link']=num
    result = {'last_node_id':max(map(int,g)),'last_link_id':len(links),'nodes':nodes,'links':links,
            'groups':[],'config':{},'extra':{},'version':0.4}
    from workflow_ui import beautify
    return beautify(result)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--preset',choices=['baseline','turbo4'],default='baseline');ap.add_argument('--enhance',action='store_true');ap.add_argument('--output',default=str(ROOT/'workflows'))
    a=ap.parse_args();p=json.loads(pathlib.Path(a.project).read_text(encoding='utf-8-sig'));g=build(p,a.preset,a.enhance)
    out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True)
    (out/f'{a.preset}.api.json').write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
    print('API draft written. Use run.py preflight to validate against the installed runtime and create UI JSON.')
if __name__=='__main__':main()
