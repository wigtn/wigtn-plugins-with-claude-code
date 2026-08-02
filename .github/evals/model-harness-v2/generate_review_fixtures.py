#!/usr/bin/env python3
"""Generate one-variable PRD review fixtures from the frozen gold source."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CONTRACTS = ("applicability", "pages", "states", "flow", "acceptance", "delivery")


def strip_markers(text: str) -> str:
    return re.sub(r"^<!-- [a-z]+:(?:start|end) -->\s*\n?", "", text, flags=re.M)


def remove_block(text: str, name: str) -> str:
    return re.sub(
        rf"<!-- {name}:start -->.*?<!-- {name}:end -->\s*",
        "",
        text,
        flags=re.S,
    )


def main(root_arg: str) -> int:
    root = Path(root_arg)
    source = (root / "review-source/leave-approval-gold.md").read_text(encoding="utf-8")
    out = root / "fixtures"
    out.mkdir(parents=True, exist_ok=True)
    instruction = (
        "아래 PRD를 검토해줘. 먼저 프로젝트 산출물 계약의 존재·적용성을 표로 감사하고, "
        "그 다음 실제 누락·모순·검증 불가능성·보안 문제를 findings-first로 영향도·근거·수정 방향과 함께 보고해줘. "
        "원문을 다시 쓰지 말고 파일을 만들거나 저장소를 탐색하지 마.\n\n"
    )
    labels = {}
    clean = strip_markers(source)
    (out / "review-contract-clean.txt").write_text(instruction + clean, encoding="utf-8")
    labels["review-contract-clean"] = {"missing": None}
    for contract in CONTRACTS:
        name = f"review-missing-{contract}"
        variant = strip_markers(remove_block(source, contract))
        (out / f"{name}.txt").write_text(instruction + variant, encoding="utf-8")
        labels[name] = {"missing": contract}
    (out / "review-labels.json").write_text(
        json.dumps(labels, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
