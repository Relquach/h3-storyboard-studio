"""Read-only check of the supplied H3 workflow and optional MP4 execution metadata.
No server, installations, mutation of workflow files, or GPU rendering.
"""
import argparse, copy, hashlib, json, pathlib, re, subprocess
TASKS={'MiniMaxH3ImageToVideo','MiniMaxH3ReferenceToVideo'}

def frames_for_seconds(seconds):
    n=max(5,round(float(seconds)*24));return n+(5-n%17)%17

def widget_values(node):
    named=node.get('widgets_values_named')
    if named is not None:return dict(named)
    names=[x['name'] for x in node.get('inputs',[]) if x.get('widget')]
    values=node.get('widgets_values') or []
    if len(names)==len(values):return dict(zip(names,values))
    return {}

def top_links(workflow):
    result={}
    for x in workflow.get('links',[]):
        if isinstance(x,list):result[x[0]]={'origin_id':x[1],'origin_slot':x[2],'target_id':x[3],'target_slot':x[4]}
        else:result[x['id']]=x
    return result

def saved_instances(workflow):
    """Read the supplied template's one-level subgraph exposures; don't use inner defaults as overrides."""
    definitions={s['id']:s for s in workflow.get('definitions',{}).get('subgraphs',[])}
    links=top_links(workflow);nodes={n['id']:n for n in workflow.get('nodes',[])}
    instances=[]
    for n in workflow.get('nodes',[]):
        if n.get('mode',0) in (2,4):continue
        if n['type'] in definitions:
            sg=definitions[n['type']];outside=widget_values(n)
            if not outside:raise ValueError('Cannot safely map exposed widget values of group '+str(n['id']))
            src={}
            for inp in n.get('inputs',[]):
                lid=inp.get('link')
                if lid in links:
                    edge=links[lid];origin=nodes[edge['origin_id']]
                    src[inp['name']]={'node':str(origin['id']),'type':origin['type'],'file':(origin.get('widgets_values') or [None])[0]}
            for inner in sg.get('nodes',[]):
                if inner.get('mode',0) in (2,4):continue
                instances.append({'id':str(n['id'])+':'+str(inner['id']),'type':inner['type'],'values':widget_values(inner),'outside':outside,'sources':src,'node':inner})
        else:
            src={}
            for inp in n.get('inputs',[]):
                lid=inp.get('link')
                if lid in links:
                    edge=links[lid];origin=nodes[edge['origin_id']]
                    src[inp['name']]={'node':str(origin['id']),'type':origin['type'],'file':(origin.get('widgets_values') or [None])[0]}
            instances.append({'id':str(n['id']),'type':n['type'],'values':widget_values(n),'outside':{},'sources':src,'node':n})
    return instances

def stamp_end(prompt):
    times=[60*int(m)+float(s) for m,s in re.findall(r'\b(\d{1,2}):(\d{2}(?:\.\d+)?)\b',prompt)]
    return max(times) if times else None

def analyze(workflow,executed=None,image_role=None,media=None):
    inst=saved_instances(workflow)
    report={'schema':1,'read_only':True,'gpu_render_tested':False,'image_role':image_role,'findings':[]}
    def add(level,code,message):report['findings'].append({'level':level,'code':code,'message':message})
    if executed is not None:
        taskrows=[(k,n) for k,n in executed.items() if n.get('class_type') in TASKS]
        modelrows=[n for n in executed.values() if n.get('class_type')=='UNETLoader']
        model=modelrows[0]['inputs'].get('unet_name') if len(modelrows)==1 else None
        report['settings_source']='video_prompt_metadata'
        if len(taskrows)!=1:
            add('error','AMBIGUOUS_TASK','Không tự chọn task khi metadata có nhiều hoặc không có conditioning task.');report['ready']=False;return report
        taskid,n=taskrows[0];typ=n['class_type'];inputs=n['inputs'];prompt=inputs.get('prompt','')
        frames=None;duration=None
        ll=inputs.get('length')
        if isinstance(ll,list):
            mathnode=executed.get(str(ll[0]),{});a=mathnode.get('inputs',{}).get('values.a')
            if isinstance(a,list):duration=executed.get(str(a[0]),{}).get('inputs',{}).get('value')
            if duration is not None:frames=frames_for_seconds(duration)
        elif isinstance(ll,(int,float)):frames=int(ll);duration=frames/24
        first=inputs.get('first_frame');last=inputs.get('last_frame')
        references=[v for k,v in inputs.items() if k.startswith('ref_images.') and v is not None]
        filenames={}
        for field,source in [('first_frame',first),('last_frame',last)]:
            if isinstance(source,list):filenames[field]=executed.get(str(source[0]),{}).get('inputs',{}).get('image')
    else:
        tasks=[x for x in inst if x['type'] in TASKS]
        # Explicitly recognize the known legacy switch, rather than treat both lazy branches as selected.
        byid={n['id']:n for n in workflow.get('nodes',[])}
        if len(tasks)>1 and byid.get(62,{}).get('type')=='PrimitiveBoolean':
            use_ref=(byid[62].get('widgets_values') or [None])[0]
            tasks=[x for x in tasks if x['type']==('MiniMaxH3ReferenceToVideo' if use_ref is True else 'MiniMaxH3ImageToVideo')]
        report['settings_source']='workflow_exposed_widgets_and_links'
        if len(tasks)!=1:
            add('error','AMBIGUOUS_TASK','Không tự chọn task từ các nhánh chưa resolve.');report['ready']=False;return report
        row=tasks[0];taskid=row['id'];typ=row['type'];out=row['outside'];prompt=out.get('prompt',row['values'].get('prompt',''))
        duration=out.get('value_1');frames=frames_for_seconds(duration) if duration is not None else None
        if not out:
            # Known original profile has explicit primitive controls on the top-level canvas.
            if byid.get(70,{}).get('type')=='PrimitiveStringMultiline':prompt=byid[70]['widgets_values'][0]
            if byid.get(23,{}).get('type')=='PrimitiveFloat':duration=byid[23]['widgets_values'][0];frames=frames_for_seconds(duration)
        model=out.get('unet_name')
        if not model:
            models=[x for x in inst if x['type']=='UNETLoader']
            if len(models)==1:model=(models[0]['node'].get('widgets_values') or [None])[0]
        first=row['sources'].get('first_frame');last=row['sources'].get('last_frame')
        references=[]
        for k,v in row['sources'].items():
            if k.startswith('ref_images.'):
                origin=byid.get(int(v['node']),{})
                if origin.get('mode',0) not in (2,4):references.append(v)
        filenames={k:v.get('file') for k,v in row['sources'].items() if k in ('first_frame','last_frame')}
    isfast='fasth3' in str(model).lower()
    isref=typ=='MiniMaxH3ReferenceToVideo'
    profile=('fasth3_ref2v_unsupported' if isref else ('fasth3_i2v_experimental' if first or last else 'fasth3_t2av')) if isfast else ('singularity_original_ref2v' if isref and 'singularity' in str(model).lower() else 'unverified_h3_profile')
    report.update({'profile':profile,'task_node':taskid,'task_type':typ,'checkpoint':model,'requested_seconds':duration,'expected_frames':frames,'source_seconds':frames/24 if frames else None,'prompt_last_timestamp_seconds':stamp_end(prompt),'first_frame_connected':bool(first),'last_frame_connected':bool(last),'reference_image_count':len(references),'input_files':filenames})
    if isfast and (isref or first or last):add('error','CHECKPOINT_TASK_NOT_DISTILLED','FastH3 V2 model card: FL2VA và Ref2VA chưa được distill; input ảnh chạy được không xác minh độ bám ảnh.')
    if not isref and first and image_role in ('storyboard_grid','character_sheet'):add('error','LAYOUT_AS_FIRST_FRAME','Grid/sheet đang là frame mở đầu. Cần ảnh shot sạch hoặc chuyển sang Ref2V đúng model.')
    picture_numbers=[int(x) for x in re.findall(r'<Picture\s+(\d+)>',prompt)]
    image_count=len(references) if isref else int(bool(first))+int(bool(last))
    if any(x<1 or x>image_count for x in picture_numbers):add('error','MISSING_PICTURE_INPUT','Prompt gọi Picture không có ảnh tương ứng trên đường conditioning.')
    if not isref and picture_numbers:add('warning','REF2V_PROMPT_IN_I2V','Không dùng các nhãn Picture như slot sheet Ref2V trong I2V; mô tả opening/ending frame thật.')
    end=report['prompt_last_timestamp_seconds']
    if duration is not None and end is not None and end>float(duration)+0.05:add('error','PROMPT_EXCEEDS_DURATION','Timeline prompt tới %.3fs nhưng duration ngoài group là %.3fs.'%(end,duration))
    if frames and frames>362:add('warning','UNVERIFIED_LONG_RUN','Lượt vượt vùng H3 gốc khoảng 5–15 giây; không chứng nhận task FastH3.')
    if not prompt.strip():add('error','EMPTY_PROMPT','Không đọc được prompt thực; không dùng prompt demo bên trong group thay thế.')
    if media:
        report['media']=media
        if frames and media.get('nb_frames') is not None and int(media['nb_frames'])!=frames:add('warning','METADATA_FRAME_MISMATCH','Số frame file khác số dự kiến từ duration; kiểm tra lịch/phiên workflow.')
    report['ready']=not any(x['level']=='error' for x in report['findings'])
    if report['ready'] and profile=='unverified_h3_profile':report['ready']=False;add('warning','CHECKPOINT_NEEDS_VERIFICATION','Task được đọc nhưng chưa xác minh profile checkpoint.')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workflow',required=True);ap.add_argument('--video');ap.add_argument('--image-role',choices=['storyboard_grid','character_sheet','clean_shot_frame']);ap.add_argument('--out',required=True);args=ap.parse_args()
    path=pathlib.Path(args.workflow);original=path.read_bytes();workflow=json.loads(original.decode('utf-8-sig'));executed=None;media=None
    if args.video:
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',args.video],text=True))
        tags=info.get('format',{}).get('tags',{})
        if tags.get('prompt'):executed=json.loads(tags['prompt'])
        video=next((s for s in info['streams'] if s.get('codec_type')=='video'),{})
        media={k:video.get(k) for k in ['width','height','avg_frame_rate','nb_frames','duration','pix_fmt']}
        media['has_audio']=any(s.get('codec_type')=='audio' for s in info['streams'])
    report=analyze(workflow,executed,image_role=args.image_role,media=media);report['workflow_sha256']=hashlib.sha256(original).hexdigest()
    out=pathlib.Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if path.read_bytes()!=original:raise RuntimeError('Workflow source changed')
    print(json.dumps({'profile':report.get('profile'),'ready':report['ready'],'findings':[x['code'] for x in report['findings']],'report':str(out)},ensure_ascii=False))
    return 0 if report['ready'] else 2
if __name__=='__main__':raise SystemExit(main())
