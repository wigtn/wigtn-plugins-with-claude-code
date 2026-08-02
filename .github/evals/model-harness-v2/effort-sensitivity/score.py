#!/usr/bin/env python3
from __future__ import annotations
import csv, importlib.util, json, re, statistics, sys
from collections import defaultdict
from pathlib import Path

def load(path,name):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def tok(path):
 f=re.findall(r"(?:tokens used|total tokens)\s*[:=]?\s*([\d,]+)",path.read_text(errors="ignore"),re.I)
 return int(f[-1].replace(",","")) if f else None
def main(study_arg):
 study=Path(study_arg); reg=load(study/"score_regression.py","reg"); v1=reg.load_v1(study)
 labels=json.loads((study/"fixtures/review-labels.json").read_text())
 rows=[]
 sources={"medium":study/"runs-regression/M56-V2","low":study/"effort-sensitivity/runs-low"}
 for effort,root in sources.items():
  for out in sorted(root.glob("*.md")):
   fixture,rep=out.stem.rsplit(".",1)
   if int(rep)>3: continue
   text=out.read_text(errors="ignore")
   if fixture.startswith("create-"):
    checks=v1.create_checks(fixture,text); family="create"
   elif fixture=="review-universal":
    checks=v1.review_checks("review-universal",text); family="universal"
   else:
    audit=reg.parse_contract_audit(text); missing=labels[fixture]["missing"]
    checks={c:audit.get(c)==("missing" if c==missing else "present") for c in reg.CONTRACTS}
    family="contract-review"
   for c,p in checks.items(): rows.append((effort,family,c,int(p)))
 out=["# GPT-5.6 v2 effort sensitivity\n","| Effort | create | contract review | universal review | tokens median | duration median |","|---|---:|---:|---:|---:|---:|"]
 for effort,root in sources.items():
  cells=[]
  for fam in ("create","contract-review","universal"):
   xs=[r[3] for r in rows if r[0]==effort and r[1]==fam]; cells.append(f"{sum(xs)}/{len(xs)} ({sum(xs)/len(xs):.1%})")
  tv=[tok(p) for p in root.glob("*.log") if tok(p)]
  dv=[]
  for p in root.glob("*.meta"):
   d=dict(x.split("=",1) for x in p.read_text().splitlines() if "=" in x); dv.append(int(d["duration_seconds"]))
  out.append(f"| {effort} | {' | '.join(cells)} | {statistics.median(tv):.0f} | {statistics.median(dv):.0f}s |")
 (study/"effort-sensitivity/RESULTS.md").write_text("\n".join(out)+"\n")
 print(study/"effort-sensitivity/RESULTS.md"); return 0
if __name__=="__main__": raise SystemExit(main(sys.argv[1]))
