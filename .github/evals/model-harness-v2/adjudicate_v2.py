#!/usr/bin/env python3
"""Post-hoc robustness analysis; never replaces the frozen primary score."""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ARMS = ("M56-BARE", "M56-CURRENT", "M56-V2")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.I | re.M | re.S) is not None


def heading(pattern: str, text: str) -> bool:
    return has(rf"^#{{1,4}}\s+[^\n]*(?:{pattern})", text)


def applicability_body(text: str) -> str:
    match = re.search(
        r"^#{1,4}\s+[^\n]*(?:Applicability|적용성|적용\s*범위)[^\n]*\n"
        r"(?P<body>.*?)(?=^#{1,4}\s+|\Z)",
        text,
        re.I | re.M | re.S,
    )
    return match.group("body") if match else ""


def row(body: str, pattern: str):
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and re.search(pattern, cells[0], re.I):
            status = cells[1].casefold()
            if any(term in status for term in ("required", "필수", "적용")):
                return "required", cells[2]
            if any(term in status for term in ("n/a", "해당 없음", "비해당")):
                return "na", cells[2]
    return None


def relaxed_validator(text: str, require_route_identity: bool) -> tuple[bool, list[str]]:
    failures = []

    def need(code: str, value: bool):
        if not value:
            failures.append(code)

    body = applicability_body(text)
    need("applicability", bool(body))
    need("problem", heading(r"context|problem|배경|문제", text))
    need("goals", heading(r"goals?|목표", text))
    need("non-goals", heading(r"non[- ]?goals?|비목표|제외|범위\s*밖", text))
    need("roles", heading(r"users?|roles?|사용자|역할|권한", text))
    need("fr", len(set(re.findall(r"\bFR-[A-Z0-9-]+\b", text, re.I))) >= 1)
    need("authorization", heading(r"authorization|data boundaries|인가|데이터 경계|권한", text))
    need("acceptance", heading(r"acceptance|수용|인수", text))
    need(
        "acceptance-shape",
        has(r"^\|[^\n]*(?:Given|전제)[^\n]*(?:When|행동)[^\n]*(?:Then|결과)", text),
    )
    need(
        "delivery",
        heading(r"delivery|구현\s*단계|출시\s*단계|전달\s*계획|출시\s*계획|구현\s*계획", text)
        and has(r"(?:Phase|단계|주\s*차).{0,400}\bFR-[A-Z0-9-]+\b", text)
        and has(r"(?:exit|종료|완료|검증|통과)", text),
    )
    conditional = {
        "pages": row(body, r"pages?|routes?|screens?|페이지|화면|경로"),
        "states": row(body, r"state|상태"),
        "flow": row(body, r"flow|흐름"),
    }
    for name, value in conditional.items():
        need(f"{name}-applicability", value is not None)
        if not value:
            continue
        status, evidence = value
        need(f"{name}-evidence", len(evidence.strip()) >= 5)
        if status == "na":
            continue
        if name == "pages":
            need("pages-section", heading(r"pages?|screens?|페이지|화면", text))
            if require_route_identity:
                need(
                    "route-identity",
                    has(
                        r"(?:route|경로|screen\s*id|화면\s*id|deep\s*link|딥링크)"
                        r".{0,160}(?:`?/[A-Za-z0-9:{}/_-]+`?|TBD|미정)|"
                        r"`/[A-Za-z0-9:{}/_-]+`",
                        text,
                    ),
                )
        elif name == "states":
            need("states-section", heading(r"state|상태", text) and has(r"빈\s*상태|empty", text))
        else:
            need("flow-section", has(r"```mermaid\s+(?:flowchart|graph)", text))
    return not failures, failures


def main(study_arg: str) -> int:
    study = Path(study_arg)
    runs = study / "runs-regression"
    v1 = load(study.parent / "model-harness-2026/score_study.py", "v1")
    validator = (
        study
        / "candidate-marketplace/plugins/wigtn-plugins-with-codex/skills/product-spec/scripts/validate-prd.py"
    )
    out = [
        "# Post-hoc robustness adjudication\n",
        "> Frozen primary scores remain authoritative. This file separates lexical scorer/parser misses from behavior misses.",
        "",
        "## Universal defect scorer\n",
        "| Arm | Frozen | Alias-robust |",
        "|---|---:|---:|",
    ]
    for arm in ARMS:
        frozen = []
        robust = []
        for path in sorted((runs / arm).glob("review-universal.*.md")):
            checks = v1.review_checks("review-universal", path.read_text(errors="ignore"))
            frozen.extend(checks.values())
            text = path.read_text(errors="ignore")
            qualitative = checks["qualitative_nfr"] or has(
                r"(?:성능|NFR|충분히\s*빠).{0,180}"
                r"(?:측정\s*불가능|검증\s*불가능|판정.{0,30}(?:없|불가능)|기준.{0,30}없|정성적)",
                text,
            )
            robust.extend(
                qualitative if key == "qualitative_nfr" else value
                for key, value in checks.items()
            )
        out.append(
            f"| {arm} | {sum(frozen)}/{len(frozen)} ({sum(frozen)/len(frozen):.1%}) | "
            f"{sum(robust)}/{len(robust)} ({sum(robust)/len(robust):.1%}) |"
        )

    out += [
        "\n## Create validator robustness\n",
        "| Arm | Frozen validator | Alias-robust structure | Strict route identity |",
        "|---|---:|---:|---:|",
    ]
    failure_counts = {}
    for arm in ARMS:
        paths = sorted((runs / arm).glob("create-*.md"))
        frozen = sum(
            subprocess.run(
                [sys.executable, str(validator), str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
            for path in paths
        )
        alias = 0
        strict = 0
        counts = Counter()
        for path in paths:
            alias_ok, _ = relaxed_validator(path.read_text(errors="ignore"), False)
            strict_ok, failures = relaxed_validator(path.read_text(errors="ignore"), True)
            alias += alias_ok
            strict += strict_ok
            counts.update(failures)
        failure_counts[arm] = counts
        out.append(
            f"| {arm} | {frozen}/{len(paths)} ({frozen/len(paths):.1%}) | "
            f"{alias}/{len(paths)} ({alias/len(paths):.1%}) | "
            f"{strict}/{len(paths)} ({strict/len(paths):.1%}) |"
        )
    out.append("\n### Strict-validator failure codes\n")
    for arm in ARMS:
        summary = ", ".join(f"{key}={value}" for key, value in failure_counts[arm].most_common())
        out.append(f"- {arm}: {summary or 'none'}")
    (runs / "ADJUDICATED.md").write_text("\n".join(out) + "\n")
    print(runs / "ADJUDICATED.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
