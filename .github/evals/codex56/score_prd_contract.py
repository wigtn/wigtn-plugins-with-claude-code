#!/usr/bin/env python3
"""GPT-5.6 PRD 실험의 산출물 계약 채점기.

기존 ../score_prd.py 결과는 원 Opus 실험과의 재현성을 위해 그대로 보존한다.
이 채점기는 기존 정규식이 놓치는 한국어 제목과 실제 표 구조를 보정한다.

주의: 첫 실행 원문을 감사한 뒤 발견한 false negative를 고친 사후 보정 채점기다.
새 기준을 발명하지 않고 arms/a2-contract.patch에 사전 명시된 10개 계약만 검사한다.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Callable


def search(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.I | re.M | re.S) is not None


def roles_table(text: str) -> bool:
    return search(
        r"\|\s*(?:role(?:\s+key)?|역할)\s*\|[^\n]*(?:권한|permission|설명)",
        text,
    ) or (
        search(r"^#{1,4}\s+.*(?:사용자.*(?:역할|권한)|역할|권한 매트릭스)", text)
        and search(r"^\|.+\|$", text)
    )


def pages_table(text: str) -> bool:
    return search(
        r"^\|\s*(?:페이지|화면|경로 예시)\s*\|[^\n]*(?:경로|route|접근)",
        text,
    )


def state_matrix(text: str) -> bool:
    has_heading = search(
        r"^#{1,4}\s+.*(?:state\s*matrix|화면\s*상태\s*매트릭스|상태\s*매트릭스)",
        text,
    )
    has_columns = search(
        r"^\|[^\n]*(?:empty|빈\s*상태)[^\n]*loading[^\n]*(?:error|오류|에러)[^\n]*(?:success|성공)",
        text,
    ) or search(
        r"^\|[^\n]*(?:empty|빈\s*상태)[^\n]*loading[^\n]*(?:success|성공)[^\n]*(?:error|오류|에러)",
        text,
    )
    return has_heading and has_columns


def mermaid_flow(text: str) -> bool:
    return search(r"```mermaid\s+(?:flowchart|graph)\b", text)


def numeric_nfr(text: str) -> bool:
    has_nfr = search(r"^#{1,4}\s+.*(?:비기능|non-functional|\bnfr\b)", text)
    has_measure = search(
        r"(?:p9[059]|9[059]\s*백분위|\d+\s*ms\b|\d+\s*초\s*(?:이내|미만)|"
        r"\d+\s*분\s*(?:이내|미만)|\d+\s*req/s|\d+\s*rps\b|"
        r"\brto\b|\brpo\b|가용성.{0,40}\d+(?:\.\d+)?%)",
        text,
    )
    return has_nfr and has_measure


def given_when_then(text: str) -> bool:
    return search(r"\bgiven\b.{0,500}\bwhen\b.{0,500}\bthen\b", text)


def server_authz(text: str) -> bool:
    return search(r"^#{1,4}\s+.*권한\s*매트릭스", text) or search(
        r"(?:서버|server).{0,120}(?:권한|역할|소유권|인가|authorization).{0,120}"
        r"(?:검증|검사|확인|enforce|check)",
        text,
    )


def fr_table(text: str) -> bool:
    return search(
        r"^\|\s*ID\s*\|[^\n]*(?:요구사항|requirement)[^\n]*\n"
        r"^\|[-:|\s]+\|[^\n]*\n"
        r"(?:^\|[^\n]*\n){0,3}^\|\s*FR-[A-Z0-9-]+",
        text,
    )


def non_goals(text: str) -> bool:
    return search(
        r"^#{1,4}\s+.*(?:non[- ]?goals?|비목표|범위\s*밖|제외\s*범위)",
        text,
    )


def implementation_phases(text: str) -> bool:
    match = re.search(r"^#{1,4}\s+.*구현\s*단계.*$", text, re.I | re.M)
    if not match:
        return False
    section = text[match.start() : match.start() + 2500]
    return search(r"\b(?:FR|NFR)-[A-Z0-9-]+", section)


CHECKS: list[tuple[str, str, Callable[[str], bool]]] = [
    ("roles", "User Roles 권한 표", roles_table),
    ("pages", "Pages/화면-경로 표", pages_table),
    ("state_matrix", "Empty/Loading/Error/Success State Matrix", state_matrix),
    ("user_flow", "Mermaid User Flow", mermaid_flow),
    ("nfr_quant", "정량 NFR", numeric_nfr),
    ("acceptance", "Given/When/Then 수용 기준", given_when_then),
    ("authz", "서버 측 인가 규칙", server_authz),
    ("fr_table", "ID가 붙은 FR 표", fr_table),
    ("nongoals", "Non-Goals/비목표", non_goals),
    ("phases", "요구사항에 매핑된 구현 단계", implementation_phases),
]


def main(dirs: list[str]) -> int:
    arms: dict[str, list[tuple[Path, str]]] = {}
    for directory in dirs:
        root = Path(directory)
        files = sorted(root.glob("prd.*.md"))
        if files:
            arms[root.name] = [
                (path, path.read_text(encoding="utf-8", errors="ignore"))
                for path in files
            ]

    if not arms:
        print("채점할 prd.*.md 파일이 없음", file=sys.stderr)
        return 2

    print("# GPT-5.6 PRD 산출물 계약 채점\n")
    print(
        "> 기존 채점기의 한국어·구조 false negative를 보정한 사후 감사 결과다. "
        "검사 항목은 A2 패치에 사전 명시된 10개 계약과 동일하다.\n"
    )

    header = " | ".join(f"{name} (n={len(runs)})" for name, runs in arms.items())
    print(f"| 계약 | {header} |")
    print("|---" * (len(arms) + 1) + "|")

    totals = {name: 0 for name in arms}
    for _key, description, predicate in CHECKS:
        cells = []
        for name, runs in arms.items():
            hits = sum(predicate(text) for _path, text in runs)
            totals[name] += hits
            marker = "✅" if hits == len(runs) else ("🟡" if hits else "❌")
            cells.append(f"{marker} {hits}/{len(runs)}")
        print(f"| {description} | {' | '.join(cells)} |")

    print()
    for name, runs in arms.items():
        denominator = len(CHECKS) * len(runs)
        average_lines = sum(text.count("\n") + 1 for _path, text in runs) / len(runs)
        print(
            f"- **{name}: {totals[name]}/{denominator} = "
            f"{totals[name] / denominator:.0%}** · 평균 {average_lines:.0f}줄"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
