"""Runtime preflight and reproducible benchmark. No invented visual quality scores."""

# Portable bootstrap: pythonXY._pth may omit the script directory.
# Add only this trusted package directory; never change global Python settings.
import sys as _sys
from pathlib import Path as _Path
_script_dir = _Path(__file__).resolve().parent
# Keep stdlib and embedded extension modules ahead of sibling utilities.
_sys.path[:] = [entry for entry in _sys.path if _Path(entry or ".").resolve() != _script_dir]
_sys.path.append(str(_script_dir))
import argparse
import copy
import csv
import json
import pathlib
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from studio import ROOT, build, to_ui, validate


def request(base,path,data=None):
    payload=None if data is None else json.dumps(data).encode()
    req=urllib.request.Request(base+path,data=payload,headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
    except urllib.error.HTTPError as e:
        detail=e.read().decode(errors='replace')
        raise RuntimeError(f'ComfyUI HTTP {e.code}: {detail[:3000]}') from e


def preflight(p,info,enhance=False):
    # Validation is against this running ComfyUI, not an assumed release number.
    graphs={}
    for preset in ['baseline','turbo4']:
        g=build(p,preset,enhance)
        ui=to_ui(g,info)
        out=ROOT/'workflows';out.mkdir(exist_ok=True)
        (out/f'{preset}.api.json').write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
        (out/f'{preset}.json').write_text(json.dumps(ui,ensure_ascii=False,indent=2),encoding='utf-8')
        graphs[preset]=g
    return graphs


class GPUMonitor:
    def __init__(self):self.rows=[];self.stop=threading.Event();self.thread=None
    def start(self):
        self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()
    def loop(self):
        while not self.stop.is_set():
            try:
                r=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
                if r.returncode==0:self.rows.append({'time':time.time(),'gpus':r.stdout.strip()})
            except (OSError,subprocess.TimeoutExpired):pass
            self.stop.wait(1)
    def finish(self):
        self.stop.set()
        if self.thread:self.thread.join(timeout=6)


def execute(base,g,label,timeout):
    # Do not mix benchmark results with another user's queued work.
    queue=request(base,'/queue')
    if queue.get('queue_running') or queue.get('queue_pending'):
        raise RuntimeError('Queue is busy. Wait for it to finish before benchmarking.')
    mon=GPUMonitor();mon.start();start=time.perf_counter();result={'label':label,'status':'failed'}
    pid=None
    try:
        accepted=request(base,'/prompt',{'prompt':g,'client_id':str(uuid.uuid4())})
        if accepted.get('node_errors'):raise RuntimeError(json.dumps(accepted['node_errors']))
        pid=accepted['prompt_id'];result['prompt_id']=pid
        while time.perf_counter()-start<timeout:
            hist=request(base,'/history/'+pid).get(pid)
            if hist:
                status=hist.get('status',{})
                result['history']=hist
                if status.get('status_str')=='error':raise RuntimeError(json.dumps(status.get('messages',[])))
                if status.get('completed'):
                    result['status']='success';break
            time.sleep(2)
        else:
            # Do not interrupt unrelated requests. User can cancel their render in ComfyUI.
            result['status']='timeout-still-may-be-running'
    except Exception as e:result['error']=str(e)
    finally:
        result['wall_seconds']=round(time.perf_counter()-start,3);mon.finish();result['gpu_samples']=mon.rows
        values=[]
        for sample in mon.rows:
            for line in sample['gpus'].splitlines():
                try:values.append(float(line.split(',')[1]))
                except (IndexError,ValueError):pass
        result['peak_observed_gpu_memory_mib']=max(values) if values else None
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--base',default='http://127.0.0.1:8188');ap.add_argument('--preflight',action='store_true');ap.add_argument('--benchmark',action='store_true');ap.add_argument('--preset',choices=['baseline','turbo4'],default='baseline');ap.add_argument('--enhance',action='store_true');ap.add_argument('--timeout',type=int,default=21600)
    a=ap.parse_args()
    parsed=urllib.parse.urlsplit(a.base)
    if parsed.hostname not in ['127.0.0.1','localhost','::1']:raise ValueError('This launcher only talks to local ComfyUI.')
    p=json.loads(pathlib.Path(a.project).read_text(encoding='utf-8-sig'));validate(p)
    # Verify image paths without sending them to any external service.
    local=json.loads((ROOT/'local.json').read_text()) if (ROOT/'local.json').exists() else None
    if local:
        inp=pathlib.Path(local['comfy'])/'input'
        for name in [p['storyboard']]+[c['file'] for c in p['characters']]:
            f=(inp/name).resolve()
            if not f.is_relative_to(inp.resolve()) or not f.is_file():raise ValueError('Missing/unsafe input image: '+name)
    info=request(a.base,'/object_info');graphs=preflight(p,info,a.enhance)
    reportdir=ROOT/'reports';reportdir.mkdir(exist_ok=True)
    stamp=str(time.time_ns());(reportdir/f'{stamp}-object-info.json').write_text(json.dumps(info))
    if a.preflight:print('Runtime schema passed. UI workflows created. No render submitted.');return
    # Two equal-seed rounds per preset; model eviction/cache means these are NOT guaranteed warm runs.
    tasks=[(s,r) for r in ['round1','round2'] for s in ['baseline','turbo4']] if a.benchmark else [(a.preset,'render')]
    results=[]
    for preset,run in tasks:
        g=copy.deepcopy(graphs[preset])
        # Unique output prefix prevents cached SaveVideo; identical inference may still be reused.
        # Change noise seed between rounds, equally across presets, to force a fresh sample.
        g['13']['inputs']['noise_seed']=p['seed']+(1 if run=='round2' else 0)
        for n in g.values():
            if n['class_type']=='H3StudioSaveVideo':n['inputs']['filename_prefix']+=f'_{stamp}_{run}'
        result=execute(a.base,g,preset+'-'+run,a.timeout);result['preset']=preset;result['seed']=g['13']['inputs']['noise_seed'];results.append(result)
        (reportdir/f'{stamp}-benchmark.json').write_text(json.dumps({'project':p,'results':results,'quality_winner':None},ensure_ascii=False,indent=2),encoding='utf-8')
        print(result['label'],result['status'],result['wall_seconds'],'seconds',flush=True)
        if result['status']!='success':break
    with open(reportdir/f'{stamp}-quality.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['preset','seed','identity_1_to_5','motion_anatomy_1_to_5','shot_order_1_to_5','style_3d_1_to_5','flicker_1_to_5','notes'])
        for r in results:w.writerow([r['preset'],r['seed'],'','','','','',''])
    print('Review videos side by side and fill the quality CSV. Speed alone never selects a quality winner.')
    if any(r['status']!='success' for r in results):raise SystemExit(1)
if __name__=='__main__':main()
