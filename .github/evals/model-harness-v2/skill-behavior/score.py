#!/usr/bin/env python3
from __future__ import annotations
import re,sys
from collections import defaultdict
from pathlib import Path
ARMS=("M56-BARE","M56-V2")
def fields(p): return dict(x.split("=",1) for x in p.read_text().splitlines() if "=" in x)
def checks(task,text,meta):
 t=text.casefold()
 if task=="acceptance-verifier": return {"fr-ids":"fr-101" in t and "fr-102" in t,"status":any(x in t for x in ("missing","미충족","누락")),"evidence":"implementation.py" in t and "test_implementation.py" in t,"no-edit":meta["tree_changed"]=="no"}
 if task=="design-direction": return {"ink":"--color-ink" in t,"accent":"--color-accent" in t,"spacing":"--space-4" in t,"project-native":meta["tree_changed"]=="no"}
 if task=="handdrawn-diagram": return {"handdrawn":"handdrawn" in t,"mermaid":"```mermaid" in t,"quoted":'["' in text or '[\"' in text,"branches":("성공" in text and "실패" in text)}
 if task=="release-readiness": return {"no-commit":meta["head_changed"]=="no","no-mutation":meta["tree_changed"]=="no","scope":("baseline.py" in t or "user-note.txt" in t),"verification":("test" in t or "검증" in t)}
 if task=="verified-delivery": return {"tests-pass":meta["test_exit"]=="0","changed":meta["tree_changed"]=="yes","evidence":("test" in t or "검증" in t),"no-commit":meta["head_changed"]=="no"}
 if task=="wigtn-presentation": return {"ink":"#1e1e28" in t or "#15151e" in t,"purple":"#9b51e0" in t or "#a85fea" in t,"wordmark":"wigtn" in t,"html":"<section" in t or "<html" in t,"dot":"wigtn-dot" in t or "퍼플 점" in text}
 return {}
def main(root_arg):
 root=Path(root_arg); agg=defaultdict(lambda:defaultdict(list))
 for arm in ARMS:
  for mp in sorted((root/arm).glob("*.meta")):
   task,idx,_=mp.name.split(".",2); meta=fields(mp); text=(root/arm/f"{task}.{idx}.md").read_text(errors="ignore")
   for c,p in checks(task,text,meta).items(): agg[arm][task].append(int(p))
 out=["# Six-skill behavior results\n","| Task | M56-BARE | M56-V2 |","|---|---:|---:|"]
 for task in sorted(set(agg["M56-BARE"])|set(agg["M56-V2"])):
  cells=[]
  for arm in ARMS:
   xs=agg[arm][task]; cells.append(f"{sum(xs)}/{len(xs)} ({sum(xs)/len(xs):.1%})")
  out.append(f"| {task} | {' | '.join(cells)} |")
 out.append("\n## Skill loading")
 for arm in ARMS:
  ms=[fields(p) for p in (root/arm).glob("*.meta")]; out.append(f"- {arm}: {sum(m['skill_loaded']=='yes' for m in ms)}/{len(ms)}")
 (root/"RESULTS.md").write_text("\n".join(out)+"\n"); print(root/"RESULTS.md"); return 0
if __name__=="__main__": raise SystemExit(main(sys.argv[1]))
