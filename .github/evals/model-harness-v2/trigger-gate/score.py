#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
MARKERS={
"product-spec":("# Product Spec","# PRD Create Contract","# PRD Review Contract"),
"screen-spec":("# Screen Spec",),
"acceptance-verifier":("# Acceptance Verifier","# Evidence Matrix"),
"design-direction":("# Design Direction",),
"handdrawn-diagram":("# Handdrawn Diagram",),
"wigtn-presentation":("# WIGTN Presentation",),
"release-readiness":("# Release Readiness","# Git Safety"),
"verified-delivery":("# Verified Delivery",),
}
def main(root_arg):
 root=Path(root_arg); rows=[]; tp=tn=fp=fn=0
 for meta in sorted(root.glob("*.meta"),key=lambda p:int(p.name.split(".",1)[0])):
  idx,expected,_=meta.name.split(".",2)
  log=(root/f"{idx}.{expected}.log").read_text(errors="ignore").casefold()
  loaded=[s for s,marks in MARKERS.items() if any(m.casefold() in log for m in marks)]
  actual=loaded[0] if len(loaded)==1 else ("none" if not loaded else "ambiguous")
  ok=actual==expected
  if expected=="none":
   tn+=ok; fp+=not ok
  else:
   tp+=ok; fn+=not ok
  rows.append((idx,expected,actual,ok))
 out=["# v2 live trigger gate\n","| # | Expected | Actual | Result |","|---:|---|---|---|"]
 out += [f"| {i} | {e} | {a} | {'PASS' if ok else 'FAIL'} |" for i,e,a,ok in rows]
 out += [f"\n- positive recall: {tp}/{tp+fn} ({tp/(tp+fn):.1%})",f"- negative specificity: {tn}/{tn+fp} ({tn/(tn+fp):.1%})"]
 (root/"RESULTS.md").write_text("\n".join(out)+"\n")
 print(root/"RESULTS.md"); return 0
if __name__=="__main__": raise SystemExit(main(sys.argv[1]))
