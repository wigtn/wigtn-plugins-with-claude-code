#!/usr/bin/env python3
"""Build deterministic anonymized judge prompts and a private arm map."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ARMS = ("M55-CURRENT", "M56-BARE", "M56-CURRENT", "M56-OPT")
PRIMARY = (
    "create-ui-internal",
    "create-backend-webhook",
    "create-mobile-expense",
    "review-universal",
    "review-convention",
    "review-clean",
    "screen-admin",
)
SUPPLEMENT = ("review-convention-v2", "review-clean-v2")
ALIASES = ("A", "B", "C", "D")

RUBRIC = """당신은 익명화된 네 후보를 비교하는 엄격한 제품·엔지니어링 평가자다.

각 후보를 서로 독립적으로 0~4점으로 채점하라.
- task_fidelity: 요청한 산출물과 범위 준수
- correctness: 논리·보안·상태·요구사항 정확성
- specificity_traceability: 구현·검증 가능한 구체성과 추적성
- restraint: 근거 없는 SLA/아키텍처/범위/finding을 만들지 않는 절제
- usability: 실제 제품·개발팀이 바로 쓸 수 있는 정도

긴 출력, finding 개수, 화려한 형식에는 가점을 주지 마라. 리뷰에서는 실제 근거가 있는 finding만 보상하고, 생성에서는 브리프 밖 사실을 발명하면 감점하라. 동일 점수와 공동 순위를 허용한다. 후보 정체나 모델을 추측하지 마라.

JSON만 반환하라:
{"ranking":[["A"],["B","C"],["D"]],"scores":{"A":{"task_fidelity":0,"correctness":0,"specificity_traceability":0,"restraint":0,"usability":0,"total":0},"B":{},"C":{},"D":{}},"material_errors":{"A":[],"B":[],"C":[],"D":{}},"reason":"100자 이내"}
total은 다섯 점수의 합이어야 한다.
"""


def mapping_for(fixture: str, repeat: int) -> dict[str, str]:
    ranked = sorted(
        ARMS,
        key=lambda arm: hashlib.sha256(f"{fixture}:{repeat}:{arm}".encode()).hexdigest(),
    )
    return dict(zip(ALIASES, ranked))


def main(study_dir_arg: str) -> int:
    study = Path(study_dir_arg)
    prompt_root = study / "judge-prompts"
    prompt_root.mkdir(parents=True, exist_ok=True)
    blind_map = {}

    for fixture in PRIMARY + SUPPLEMENT:
        source_root = study / ("runs-supplement" if fixture in SUPPLEMENT else "runs")
        fixture_text = (study / "fixtures" / f"{fixture}.txt").read_text(encoding="utf-8")
        for repeat in (1, 2):
            key = f"{fixture}.{repeat}"
            mapping = mapping_for(fixture, repeat)
            blind_map[key] = mapping
            chunks = [RUBRIC, "\n## 원 요청\n", fixture_text]
            for alias in ALIASES:
                arm = mapping[alias]
                output = source_root / arm / f"{fixture}.{repeat}.md"
                chunks.extend(
                    [
                        f"\n\n## 후보 {alias}\n\n",
                        output.read_text(encoding="utf-8", errors="ignore"),
                    ]
                )
            (prompt_root / f"{key}.txt").write_text("".join(chunks), encoding="utf-8")

    (prompt_root / "blind-map.json").write_text(
        json.dumps(blind_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
