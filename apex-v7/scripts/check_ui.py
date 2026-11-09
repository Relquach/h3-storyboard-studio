"""Developer-only CPU frontend check. Never queues rendering."""
import json,pathlib,sys,importlib.util
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
core=pathlib.Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('apex_install',ROOT/'scripts/install.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1700,'height':1100},device_scale_factor=1.3)
 page.goto('http://127.0.0.1:8201',wait_until='networkidle',timeout=60000);page.evaluate("async()=>{const{app}=await import('/scripts/app.js');window.apexApp=app;}")
 rows=[]
 for profile in json.loads((ROOT/'profiles.json').read_text()):
  w=installer.adapt_video_schema(json.loads((ROOT/'workflows'/profile['file']).read_text()),core)
  result=page.evaluate('''async w=>{const a=window.apexApp;await a.loadGraphData(w);const g=await a.graphToPrompt();return{unknown:a.graph._nodes.filter(n=>n.has_errors||n.type==='Unknown').map(n=>n.type),output:g.output,graph:a.graph.serialize()}}''',w)
  api=result.pop('output');serialized=result.pop('graph');print(profile['id'],'unknown',result['unknown'],'api_nodes',len(api),flush=True)
  (ROOT/'reports'/('api-'+profile['id']+'.json')).write_text(json.dumps(api,ensure_ascii=False,indent=2));(ROOT/'reports'/('ui-serialized-'+profile['id']+'.json')).write_text(json.dumps(serialized,ensure_ascii=False,indent=2))
  result.update(profile=profile['id'],api_nodes=len(api));rows.append(result)
  if result['unknown']:continue
  assert api['136']['inputs']['prompt']==['138',0]
  assert len([k for k in api['136']['inputs'] if k.startswith('ref_images.')])==1
  assert not any(n['class_type']=='TextGenerate' for n in api.values())
  assert not any(n['class_type']=='LoraLoaderModelOnly' and 'realism' in n['inputs']['lora_name'] for n in api.values())
  if profile['id']=='full':assert api['9259']['inputs']['audio']==['121',0]
  # All four references enabled, then an interior slot removed. Test actual API compaction, not label assumptions.
  for variant in ['all-refs','gap-ref']:
   ww=json.loads(json.dumps(w))
   for n in ww['nodes']:
    if n['id'] in [9408,9409,9413]:n['mode']=0 if variant=='all-refs' or n['id']!=9408 else 4
   out=page.evaluate('''async w=>{await window.apexApp.loadGraphData(w);return(await window.apexApp.graphToPrompt()).output}''',ww)
   refs={k:v for k,v in out['136']['inputs'].items() if k.startswith('ref_images.')}
   expected=4 if variant=='all-refs' else 3;assert len(refs)==expected,(variant,refs)
   (ROOT/'reports'/('api-'+profile['id']+'-'+variant+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2));rows.append({'profile':profile['id']+'-'+variant,'unknown':[],'api_nodes':len(out),'reference_count':len(refs)})
  # Restore default and screenshot actual ComfyUI controls.
  page.evaluate('async w=>{await window.apexApp.loadGraphData(w)}',w);page.keyboard.press('Escape')
  for label,bounds in [('inputs',[-20,0,1140,1630]),('controls',[440,0,700,650]),('references',[-20,0,450,1580]),('processing',[1120,0,4050,1720])]:
   clip=page.evaluate('''b=>{const a=window.apexApp,r=a.canvas.canvas.getBoundingClientRect();const[x,y,w,h]=b,s=Math.min((r.width-30)/w,(r.height-30)/h,1.5);a.canvas.ds.scale=s;a.canvas.ds.offset=[(r.width/s-w)/2-x,(r.height/s-h)/2-y];a.canvas.setDirty(true,true);a.canvas.draw(true,true);return{x:r.x+(x+a.canvas.ds.offset[0])*s,y:r.y+(y+a.canvas.ds.offset[1])*s,width:w*s,height:h*s}}''',bounds)
   page.wait_for_timeout(300);page.screenshot(path=str(ROOT/'docs/assets'/('ui-'+profile['id']+'-'+label+'.png')),clip=clip)
 (ROOT/'reports/ui-checks.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));b.close()
 if any(x['unknown'] for x in rows):raise RuntimeError('Unknown nodes in workflow import')
