#!/usr/bin/env python3
"""Deterministic smoke test for narrow natural-language trigger contracts."""

from pathlib import Path
import sys


RULES = {
    "product-spec": ("prd", "제품 요구사항", "기획서"),
    "screen-spec": ("화면정의", " ia", "user flow", "wireframe", "와이어프레임", "개발 핸드오프"),
    "acceptance-verifier": ("요구사항을 만족", "요구사항 반영", "acceptance criteria", "fr별"),
    "design-direction": ("ui 디자인 방향", "visual direction"),
    "handdrawn-diagram": ("손그림", "sketch diagram", "handdrawn"),
    "wigtn-presentation": ("wigtn 브랜드", "위그튼"),
    "release-readiness": ("커밋해줘", "푸시해줘", "pr 올려줘", "커밋 준비해줘"),
}


def classify(prompt: str) -> str:
    text = prompt.casefold()
    matches = [name for name, terms in RULES.items() if any(term in text for term in terms)]
    # A source PRD is common input to screen and acceptance work. Prefer the
    # concrete requested artifact or verification over generic PRD matching.
    if "product-spec" in matches and len(matches) > 1:
        matches.remove("product-spec")
    # "sketch diagram" requests an image artifact, not a screen wireframe.
    if "handdrawn-diagram" in matches and "screen-spec" in matches:
        matches.remove("screen-spec")
    return matches[0] if len(matches) == 1 else "none" if not matches else "ambiguous:" + ",".join(matches)


def main() -> int:
    fixture = Path(__file__).resolve().parents[1] / "tests" / "trigger-cases.tsv"
    failures = []
    count = 0
    for number, line in enumerate(fixture.read_text(encoding="utf-8").splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        expected, prompt = line.split("\t", 1)
        actual = classify(prompt)
        count += 1
        if actual != expected:
            failures.append(f"line {number}: expected {expected}, got {actual}: {prompt}")
    if failures:
        print("Trigger contract: FAIL")
        print("\n".join(failures))
        return 1
    print(f"Trigger contract: PASS ({count} cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
