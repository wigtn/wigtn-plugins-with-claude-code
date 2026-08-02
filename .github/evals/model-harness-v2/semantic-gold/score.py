#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

JUDGES = ("J55", "J56")
ARMS = ("M56-BARE", "M56-CURRENT", "M56-V2")
DIMENSIONS = ("completeness", "correctness", "feasibility", "traceability", "concision")


def parse_json(path: Path) -> dict:
    text = path.read_text(errors="ignore").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def main(root_arg: str) -> int:
    root = Path(root_arg)
    mapping = json.loads((root / "BLIND-MAP.json").read_text())
    records = []
    defect_consensus = defaultdict(lambda: defaultdict(lambda: {"blocker": [], "high": []}))
    for judge in JUDGES:
        for path in sorted((root / "runs" / judge).glob("*.json")):
            data = parse_json(path)
            fixture = data["fixture"]
            reverse = mapping[fixture]["labels"]
            seen = set()
            for candidate in data["candidates"]:
                label = candidate["label"]
                if label in seen or label not in reverse:
                    raise ValueError(f"invalid label {judge}/{fixture}/{label}")
                seen.add(label)
                arm = reverse[label]
                scores = [int(candidate[key]) for key in DIMENSIONS]
                if any(score < 0 or score > 4 for score in scores):
                    raise ValueError(f"invalid score {judge}/{fixture}/{label}")
                records.append(
                    {
                        "judge": judge,
                        "fixture": fixture,
                        "arm": arm,
                        "scores": scores,
                        "blockers": candidate.get("blockers", []),
                        "high": candidate.get("high", []),
                    }
                )
                defect_consensus[fixture][arm]["blocker"].append(len(candidate.get("blockers", [])))
                defect_consensus[fixture][arm]["high"].append(len(candidate.get("high", [])))
            if seen != {"A", "B", "C"}:
                raise ValueError(f"missing labels {judge}/{fixture}")

    out = [
        "# Semantic gold results\n",
        "| Arm | semantic /100 | completeness | correctness | feasibility | traceability | concision | judge blockers | judge high |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        rows = [record for record in records if record["arm"] == arm]
        dimension_means = [
            statistics.mean(record["scores"][index] for record in rows)
            for index in range(len(DIMENSIONS))
        ]
        blockers = sum(len(record["blockers"]) for record in rows)
        high = sum(len(record["high"]) for record in rows)
        total = statistics.mean(sum(record["scores"]) for record in rows) * 5
        out.append(
            f"| {arm} | {total:.1f} | "
            + " | ".join(f"{value:.2f}" for value in dimension_means)
            + f" | {blockers} | {high} |"
        )
    out.append("\n## Dual-judge defect consensus\n")
    for fixture in sorted(defect_consensus):
        for arm in ARMS:
            blockers = defect_consensus[fixture][arm]["blocker"]
            high = defect_consensus[fixture][arm]["high"]
            out.append(
                f"- {fixture} / {arm}: blocker consensus={'yes' if all(value > 0 for value in blockers) else 'no'}; "
                f"high consensus={'yes' if all(value > 0 for value in high) else 'no'}; "
                f"counts={blockers}/{high}"
            )
    (root / "RESULTS.md").write_text("\n".join(out) + "\n")

    packet = [
        "# Human expert review packet\n",
        "모델 judge 합의는 전문가 판정을 대체하지 않는다. 아래 항목을 원문과 함께 확인한다.",
        "",
        "- [ ] brief와 정면 충돌하는 정책 또는 범위가 없는가",
        "- [ ] 권한·테넌트·민감정보·재시도·중복 처리의 치명적 누락이 없는가",
        "- [ ] 모든 주요 요구사항이 관찰 가능한 acceptance criteria로 연결되는가",
        "- [ ] N/A 판정에 실제 brief/repository 근거가 있는가",
        "- [ ] 미결정 사항이 구현을 막는 결정과 나중에 정해도 되는 결정을 구분하는가",
        "- [ ] 단계별 delivery가 요구사항 ID와 연결되는가",
        "- [ ] 불필요한 형식 강제가 의미 품질을 가리지 않는가",
        "",
        "검토자는 각 fixture/arm에 `PASS`, `PASS WITH HIGH`, `FAIL BLOCKER`와 근거를 기록한다.",
        "",
    ]
    for fixture in sorted(mapping):
        packet.append(f"## {fixture}\n")
        for arm, path in mapping[fixture]["paths"].items():
            selection = mapping[fixture]["selection"][arm]
            packet.append(
                f"- [ ] {arm}: `{path}` — deterministic {selection['score']}/{selection['total']}, repeat {selection['repeat']}"
            )
        packet.append("")
    (root / "HUMAN-REVIEW-PACKET.md").write_text("\n".join(packet) + "\n")
    print(root / "RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
