#!/usr/bin/env python3
from __future__ import annotations
import re, statistics, sys
from pathlib import Path

ARMS=("M56-BARE","M56-CURRENT","M56-V2")
def fields(path):
    return dict(line.split("=",1) for line in path.read_text().splitlines() if "=" in line)
def main(root_arg):
    root=Path(root_arg)
    out=["# Real implementation benchmark\n","| Arm | valid test passes | model exits | test tampering | skill misloads | duration median | tokens median |","|---|---:|---:|---:|---:|---:|---:|"]
    for arm in ARMS:
        metas=[fields(p) for p in sorted((root/arm).glob("*.meta"))]
        token_values=[]
        for log in sorted((root/arm).glob("*.log")):
            if log.name.endswith(".test.log"): continue
            found=re.findall(r"(?:tokens used|total tokens)\s*[:=]?\s*([\d,]+)",log.read_text(errors="ignore"),re.I)
            if found: token_values.append(int(found[-1].replace(",","")))
        out.append(
            f"| {arm} | {sum(m['test_exit']=='0' and m['test_integrity']=='intact' for m in metas)}/{len(metas)} | "
            f"{sum(m['model_exit']=='0' for m in metas)}/{len(metas)} | "
            f"{sum(m['test_integrity']!='intact' for m in metas)}/{len(metas)} | "
            f"{sum(m['wigtn_skill_loaded']=='yes' for m in metas)}/{len(metas)} | "
            f"{statistics.median(int(m['duration_seconds']) for m in metas):.0f}s | "
            f"{statistics.median(token_values):.0f} |"
        )
    (root/"RESULTS.md").write_text("\n".join(out)+"\n")
    print(root/"RESULTS.md")
    return 0
if __name__=="__main__": raise SystemExit(main(sys.argv[1]))
