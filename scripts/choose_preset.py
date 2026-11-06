"""Pick fastest acceptable preset only after real renders AND human visual review."""

# Portable bootstrap: pythonXY._pth may omit the script directory.
# Add only this trusted package directory; never change global Python settings.
import sys as _sys
from pathlib import Path as _Path
_script_dir = _Path(__file__).resolve().parent
# Keep stdlib and embedded extension modules ahead of sibling utilities.
_sys.path[:] = [entry for entry in _sys.path if _Path(entry or ".").resolve() != _script_dir]
_sys.path.append(str(_script_dir))
import csv,json,pathlib,sys
from collections import defaultdict

def main():
    import argparse
    parser=argparse.ArgumentParser(description='Choose a preset after real video quality review.')
    parser.add_argument('report')
    parser.add_argument('quality')
    args=parser.parse_args()
    report=pathlib.Path(args.report);quality=pathlib.Path(args.quality);data=json.loads(report.read_text(encoding='utf-8'))
    fields=['identity_1_to_5','motion_anatomy_1_to_5','shot_order_1_to_5','style_3d_1_to_5','flicker_1_to_5']
    scores={}
    for row in csv.DictReader(quality.open(encoding='utf-8-sig')):
        try:values=[float(row[k]) for k in fields]
        except ValueError:raise SystemExit('Quality scores are incomplete. No winner selected.')
        if any(not 1<=x<=5 for x in values):raise SystemExit('Scores must be 1–5; higher is better.')
        key=(row['preset'],int(row['seed']))
        if key in scores:raise SystemExit('Duplicate quality row')
        scores[key]=values
    runs=defaultdict(list);passed=defaultdict(list)
    for result in data['results']:
        key=(result['preset'],result['seed'])
        if result['status']!='success' or key not in scores:raise SystemExit('Missing successful render or quality review.')
        v=scores[key];passed[result['preset']].append(v[0]>=4 and v[1]>=4 and min(v[2:])>=3)
        runs[result['preset']].append(result['wall_seconds'])
    acceptable={p:sum(t)/len(t) for p,t in runs.items() if len(t)>=2 and all(passed[p])}
    if not acceptable:raise SystemExit('No preset passed all reviewed seeds. Fix inputs/settings and rerender.')
    winner=min(acceptable,key=acceptable.get)
    out=report.with_name(report.stem+'-selection.json');out.write_text(json.dumps({'winner':winner,'mean_wall_seconds':acceptable,'basis':'real render wall time + human visual scores, not universal model quality'},indent=2))
    print('Selected for this project:',winner,'Report:',out)

if __name__=='__main__':main()
