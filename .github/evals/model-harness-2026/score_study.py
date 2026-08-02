#!/usr/bin/env python3
"""Pre-registered deterministic scorer for the GPT-5.5/5.6 harness study."""

from __future__ import annotations

import csv
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path


ARMS = ("M55-CURRENT", "M56-BARE", "M56-CURRENT", "M56-OPT")
FIXTURES = (
    "create-ui-internal",
    "create-backend-webhook",
    "create-mobile-expense",
    "review-universal",
    "review-convention",
    "review-clean",
    "screen-admin",
)


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.I | re.M | re.S) is not None


def heading(term: str, text: str) -> bool:
    return has(rf"^#{{1,4}}\s+[^\n]*(?:{term})", text)


def issue(term: str, text: str) -> bool:
    problem = r"(?:누락|없(?:음|다)|미정의|불명확|모순|충돌|검증\s*불가|구체적이지|필요|부족|위험|문제)"
    return has(rf"(?:{term}).{{0,180}}{problem}|{problem}.{{0,180}}(?:{term})", text)


def create_checks(fixture: str, text: str) -> dict[str, bool]:
    checks = {
        "problem": heading(r"context|문제|배경", text),
        "goals": heading(r"goals?|목표", text),
        "non_goals": heading(r"non[- ]?goals?|비목표|제외|범위\s*밖", text),
        "roles": heading(r"users?|roles?|사용자|역할|권한", text)
        and has(r"^\|[^\n]*(?:role|역할|사용자)[^\n]*\|", text),
        "fr_ids": len(set(re.findall(r"\bFR-[A-Z0-9-]+\b", text, re.I))) >= 3,
        "server_authz": has(
            r"(?:서버|server).{0,160}(?:권한|인가|authorization|소유권|tenan|조직|프로젝트).{0,160}(?:검사|검증|강제|enforce|확인)",
            text,
        ),
        "nfr": heading(r"non-functional|비기능|\bnfr\b", text),
        "acceptance_gwt": heading(r"acceptance|수용", text)
        and (
            has(r"\bgiven\b.{0,300}\bwhen\b.{0,300}\bthen\b", text)
            or has(r"^\|[^\n]*(?:Given|전제)[^\n]*(?:When|행동)[^\n]*(?:Then|결과)", text)
        ),
        "risks_open": heading(r"risk|위험", text)
        and heading(r"assumption|open|가정|열린|미결정", text),
        "mapped_phases": heading(r"delivery|구현\s*단계|출시\s*단계|phase", text)
        and has(r"(?:Phase|단계).{0,300}\bFR-[A-Z0-9-]+\b", text),
    }
    if fixture == "create-backend-webhook":
        ui_na = has(
            r"(?:UI|화면|Pages?|State\s*Matrix|페이지).{0,100}(?:해당\s*없음|N/?A|범위\s*아님|없다)",
            text,
        )
        ui_sections = heading(r"pages?|화면|state\s*matrix|상태\s*매트릭스", text)
        fabricated_sla = has(
            r"(?:SLA|지연|latency|처리량|throughput).{0,100}(?:p9[059]|\d+\s*(?:ms|초|rps|req/s))",
            text,
        )
        checks.update(
            {
                "ui_applicability": ui_na and not (ui_sections and not ui_na),
                "delivery_semantics": has(
                    r"(?:최소\s*1회|at[- ]least[- ]once).{0,240}(?:중복|idempot|event\s*id)|"
                    r"(?:중복|idempot|event\s*id).{0,240}(?:최소\s*1회|at[- ]least[- ]once)",
                    text,
                ),
                "security_open_no_fake_sla": issue(
                    r"서명|signature|secret|rotation", text
                )
                and not fabricated_sla,
            }
        )
    else:
        checks.update(
            {
                "pages_routes": has(
                    r"^\|[^\n]*(?:Page|페이지|화면)[^\n]*(?:Route|경로)[^\n]*(?:Role|역할|접근)",
                    text,
                ),
                "state_matrix": heading(r"state\s*matrix|상태\s*매트릭스", text)
                and has(
                    r"^\|[^\n]*(?:Empty|빈\s*상태)[^\n]*(?:Loading|로딩)[^\n]*(?:Error|오류|에러)[^\n]*(?:Success|성공)",
                    text,
                ),
                "mermaid_flow": has(r"```mermaid\s+(?:flowchart|graph)\b", text),
            }
        )
    return checks


def review_checks(fixture: str, text: str) -> dict[str, bool]:
    if fixture == "review-universal":
        return {
            "fr_contradiction": issue(r"FR-101|FR-102|모든\s*로그인|관리자만", text),
            "authorization": issue(r"권한|인가|authorization", text),
            "qualitative_nfr": issue(r"충분히\s*빠|성능|NFR", text),
            "unverifiable_acceptance": issue(r"AC-101|AC-102|정상적으로|적절히|수용", text),
            "ownerless_expiry": issue(r"만료|expiry|열린\s*결정|owner|소유자", text),
        }
    if fixture == "review-convention":
        return {
            "applicability": issue(r"applicability|적용성|필수.*해당\s*없음", text),
            "pages_routes": issue(r"pages?|페이지|화면.*경로|routes?", text),
            "state_matrix": issue(r"state\s*matrix|상태\s*매트릭스|empty.*loading.*error.*success", text),
            "mermaid_flow": issue(r"mermaid|user\s*flow|사용자\s*흐름", text),
            "gwt": issue(r"given.?when.?then|전제.*행동.*결과", text),
            "mapped_phases": issue(r"delivery|구현\s*단계|phase|단계.*FR", text),
        }
    severe_finding = has(
        r"^\s*(?:[-*]|\|)\s*(?:blocker|high|치명|중대|높음)\b"
        r"[^\n]*(?:누락|모순|취약|위험|문제)",
        text,
    )
    explicit_clean = has(
        r"(?:blocker|high|중대|중요).{0,80}(?:없음|없다|발견되지|해당\s*없음)|"
        r"(?:중대한|중요한).{0,80}(?:문제|결함).{0,40}(?:없음|없다|발견되지)",
        text,
    )
    return {"clean_no_severe_false_positive": explicit_clean and not severe_finding}


def screen_checks(text: str) -> dict[str, bool]:
    return {
        "artifact_ia": heading(r"(?:^|01[- .])?IA\b|정보\s*구조", text),
        "artifact_flow": heading(r"user\s*flow|사용자\s*흐름", text),
        "artifact_screen_spec": heading(r"screen\s*spec|화면\s*명세|화면\s*정의", text),
        "artifact_html": heading(r"(?:lo-?fi\s*)?(?:html\s*)?wireframe|와이어프레임", text)
        and has(r"<(?:!doctype|html|main|section|form)\b", text),
        "artifact_handoff": heading(r"dev(?:eloper)?\s*handoff|개발\s*핸드오프", text),
        "mermaid": has(r"```mermaid\s+(?:flowchart|graph)\b", text),
        "roles_routes": has(r"(?:요청자|승인자|감사자).{0,500}(?:route|경로)", text),
        "states": all(
            has(term, text)
            for term in (r"empty|빈\s*상태", r"loading|로딩", r"error|오류|에러", r"success|성공")
        ),
        "recovery": has(r"재시도|입력\s*보존|사유\s*보존|recovery|retry", text),
        "microcopy": has(r"마이크로카피|microcopy|오류\s*문구|버튼\s*(?:문구|레이블)", text),
        "components": has(r"컴포넌트|components?", text),
        "responsive": has(r"모바일|반응형|single[- ]column|단일\s*열", text),
        "traceability": has(r"\bFR-10[1-5]\b", text)
        and has(r"(?:handoff|핸드오프).{0,1800}\bFR-10[1-5]\b", text),
    }


def read_meta(path: Path) -> dict[str, str]:
    result = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                result[key] = value
    return result


def extract_tokens(log: str) -> int | None:
    matches = re.findall(r"(?:total tokens|tokens used)\s*[:=]?\s*([\d,]+)", log, re.I)
    return int(matches[-1].replace(",", "")) if matches else None


def wilson(hits: int, total: int) -> tuple[float, float]:
    if not total:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = hits / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return center - radius, center + radius


def median_iqr(values: list[int]) -> str:
    if not values:
        return "N/A"
    values = sorted(values)
    if len(values) == 1:
        return str(values[0])
    qs = statistics.quantiles(values, n=4, method="inclusive")
    return f"{statistics.median(values):.0f} [{qs[0]:.0f}–{qs[2]:.0f}]"


def main(root_arg: str) -> int:
    root = Path(root_arg)
    rows = []
    for arm in ARMS:
        for fixture in FIXTURES:
            for output in sorted((root / arm).glob(f"{fixture}.*.md")):
                text = output.read_text(encoding="utf-8", errors="ignore")
                stem = output.name.removesuffix(".md")
                index = stem.rsplit(".", 1)[-1]
                meta = read_meta(root / arm / f"{fixture}.{index}.meta")
                log_path = root / arm / f"{fixture}.{index}.log"
                log = log_path.read_text(encoding="utf-8", errors="ignore") if log_path.exists() else ""
                if fixture.startswith("create-"):
                    checks = create_checks(fixture, text)
                    family = "create"
                elif fixture.startswith("review-"):
                    checks = review_checks(fixture, text)
                    family = "review"
                else:
                    checks = screen_checks(text)
                    family = "screen"
                for criterion, passed in checks.items():
                    rows.append(
                        {
                            "arm": arm,
                            "fixture": fixture,
                            "repeat": index,
                            "family": family,
                            "criterion": criterion,
                            "passed": int(passed),
                            "duration_seconds": int(meta.get("duration_seconds", "0")),
                            "exit_code": int(meta.get("exit_code", "99")),
                            "lines": text.count("\n") + 1,
                            "tokens": extract_tokens(log) or "",
                            "output": str(output),
                        }
                    )

    if not rows:
        print("No study outputs found", file=sys.stderr)
        return 2

    csv_path = root / "SCORES.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    by_arm_family: dict[tuple[str, str], list[int]] = defaultdict(list)
    run_metrics: dict[str, dict[tuple[str, str], int]] = defaultdict(dict)
    for row in rows:
        by_arm_family[(row["arm"], row["family"])].append(row["passed"])
        key = (row["fixture"], row["repeat"])
        run_metrics[row["arm"]][key] = row["duration_seconds"]

    lines_by_arm: dict[str, dict[tuple[str, str], int]] = defaultdict(dict)
    tokens_by_arm: dict[str, dict[tuple[str, str], int]] = defaultdict(dict)
    exits_by_arm: dict[str, dict[tuple[str, str], int]] = defaultdict(dict)
    for row in rows:
        key = (row["fixture"], row["repeat"])
        lines_by_arm[row["arm"]][key] = row["lines"]
        exits_by_arm[row["arm"]][key] = row["exit_code"]
        if row["tokens"] != "":
            tokens_by_arm[row["arm"]][key] = int(row["tokens"])

    out = []
    out.append("# GPT‑5.5/5.6 × WIGTN 플러그인 — 자동 채점 결과\n")
    out.append("> 사전등록된 구조·결함 기준의 1차 점수. 의미 품질 pairwise 판정 전 결과다.\n")
    out.append("## 계약 및 결함 점수\n")
    out.append("| Arm | PRD 생성 | PRD 리뷰 | 화면정의 | 전체 |")
    out.append("|---|---:|---:|---:|---:|")
    summary = {}
    for arm in ARMS:
        cells = []
        all_values = []
        for family in ("create", "review", "screen"):
            values = by_arm_family[(arm, family)]
            all_values.extend(values)
            cells.append(f"{sum(values)}/{len(values)} ({sum(values)/len(values):.1%})")
        lo, hi = wilson(sum(all_values), len(all_values))
        total_cell = (
            f"{sum(all_values)}/{len(all_values)} ({sum(all_values)/len(all_values):.1%}; "
            f"95% CI {lo:.1%}–{hi:.1%})"
        )
        summary[arm] = {"hits": sum(all_values), "total": len(all_values)}
        out.append(f"| {arm} | {' | '.join(cells)} | {total_cell} |")

    out.append("\n## 효율 및 실행 안정성\n")
    out.append("| Arm | 시간 초 median [IQR] | 출력 줄 median [IQR] | 토큰 median [IQR] | 성공 실행 |")
    out.append("|---|---:|---:|---:|---:|")
    for arm in ARMS:
        durations = list(run_metrics[arm].values())
        lines = list(lines_by_arm[arm].values())
        tokens = list(tokens_by_arm[arm].values())
        exits = list(exits_by_arm[arm].values())
        out.append(
            f"| {arm} | {median_iqr(durations)} | {median_iqr(lines)} | "
            f"{median_iqr(tokens)} | {sum(code == 0 for code in exits)}/{len(exits)} |"
        )

    out.append("\n## 픽스처별 점수\n")
    out.append("| Fixture | " + " | ".join(ARMS) + " |")
    out.append("|---|" + "---:|" * len(ARMS))
    for fixture in FIXTURES:
        cells = []
        for arm in ARMS:
            vals = [r["passed"] for r in rows if r["arm"] == arm and r["fixture"] == fixture]
            cells.append(f"{sum(vals)}/{len(vals)} ({sum(vals)/len(vals):.0%})")
        out.append(f"| {fixture} | " + " | ".join(cells) + " |")

    results_path = root / "RESULTS.md"
    results_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    (root / "SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(results_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
