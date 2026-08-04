#!/usr/bin/env python3
"""knowledge-wiki 회귀 테스트 — 결정론만, 모델 호출 없음.

여기서 지키는 것은 **경계**다. G2/G3 의 LLM 품질은 검증하지 않는다.
경계가 무너지는 두 가지 방식만 막는다:

    1. 조용히 아무것도 안 함  (설정을 못 읽어 모든 세션이 거부됨)
    2. 조용히 너무 많이 함    (꺼 뒀는데 켜져 있음 / 금지 영역에 씀)

CI 에서 `python3 .github/scripts/test_knowledge_wiki.py` 로 실행한다.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "wigtn-plugins" / "scripts"))

FAILURES: list[str] = []
CHECKS = 0


def check(name: str, actual: object, expected: object) -> None:
    global CHECKS
    CHECKS += 1
    if actual != expected:
        FAILURES.append(f"{name}\n    기대: {expected!r}\n    실제: {actual!r}")


def section(title: str) -> None:
    print(f"\n── {title}")


# ═════════════════════════════════════════════════════════════
# 1. YAML 폴백 파서 — PyYAML 없는 환경에서도 리스트를 읽어야 한다
#
# 회귀 이력: 최상위 키가 {} 로 선점된 뒤 setdefault 가 그 {} 를 돌려줘
# 리스트 항목이 전부 버려졌다 → include 가 항상 비어 G0 가 모든 세션을 거부.
# 로그도 안 남아서 무증상이었다.
# ═════════════════════════════════════════════════════════════
def test_fallback_parser() -> None:
    section("YAML 폴백 파서 (PyYAML 부재 가정)")

    # sys.modules 에 None 을 박으면 `import yaml` 이 ImportError 를 낸다 (CPython 규약).
    # meta_path finder 로 막는 방법은 3.12 에서 find_module 이 제거돼 조용히 무력화된다 -
    # 그러면 PyYAML 이 설치된 러너에서 테스트가 폴백을 전혀 타지 않고도 통과한다.
    had_yaml = "yaml" in sys.modules
    saved = sys.modules.get("yaml")
    sys.modules["yaml"] = None  # type: ignore[assignment]
    try:
        from knowledge_wiki import config

        parsed = config.parse_yaml(
            "wiki:\n"
            "  path: /tmp/w\n"
            "  subdir: per-user/me\n"
            "include:\n"
            "  - /tmp/a\n"
            "  - '/tmp/b'\n"
            "exclude:\n"
            "  - /tmp/a/secret\n"
        )
        check("include 를 리스트로 읽는다", parsed.get("include"), ["/tmp/a", "/tmp/b"])
        check("exclude 를 리스트로 읽는다", parsed.get("exclude"), ["/tmp/a/secret"])
        check("중첩 dict 를 읽는다", parsed.get("wiki", {}).get("subdir"), "per-user/me")

        # 부트스트랩 템플릿 그대로도 통과해야 한다 (기본 설치 경로)
        tpl = config._DEFAULT_TEMPLATE.format(wiki="/tmp/w", user="me", home="/tmp/home")
        boot = config.parse_yaml(tpl)
        check("부트스트랩 템플릿의 include 가 비지 않는다", boot.get("include"), ["/tmp/home"])
        check(
            "부트스트랩 설정이 include 범위를 통과시킨다",
            config.scope_verdict(boot, Path("/tmp/home/proj"))[0],
            True,
        )
    finally:
        if had_yaml:
            sys.modules["yaml"] = saved
        else:
            sys.modules.pop("yaml", None)


# ═════════════════════════════════════════════════════════════
# 2. G0 스코프 게이트 — 거부가 기본값
# ═════════════════════════════════════════════════════════════
def test_scope_gate() -> None:
    section("G0 스코프 게이트")
    from knowledge_wiki import gates

    tmp = Path(tempfile.mkdtemp())
    wiki = tmp / "wiki"
    (wiki / "per-user/me").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=wiki, capture_output=True)
    work = tmp / "work"
    (work / ".git").mkdir(parents=True)
    cfg = tmp / "knowledge-wiki.yml"
    os.environ["WIGTN_WIKI_CONFIG"] = str(cfg)

    def write_config(*, enabled: str = "true", subdir: str = "per-user/me",
                     exclude: str = "", wiki_path: Path = wiki) -> None:
        text = (
            f"enabled: {enabled}\n"
            "wiki:\n"
            f"  path: {wiki_path}\n"
            f"  subdir: {subdir}\n"
            "include:\n"
            f"  - {tmp}\n"
        )
        if exclude:
            text += f"exclude:\n  - {exclude}\n"
        cfg.write_text(text, encoding="utf-8")

    def marker(content: str | None) -> None:
        path = work / gates.MARKER_NAME
        if content is None:
            path.unlink(missing_ok=True)
        else:
            path.write_text(content, encoding="utf-8")

    def verdict() -> bool:
        return gates.resolve_tenant(str(work))[0] is not None

    # 기본 통과 (이후 케이스가 "거부됐다"를 의미있게 만들기 위한 대조군)
    write_config()
    marker(None)
    check("include 안 + 활성 → 통과", verdict(), True)

    # 회귀: 전역 kill-switch 를 마커가 우회했다
    write_config(enabled="false")
    check("전역 enabled:false → 거부", verdict(), False)
    marker("enabled: true\n")
    check("전역 enabled:false 는 마커로 우회 불가", verdict(), False)

    # exclude 는 마커보다 강하다 (기존 계약 — 깨지지 않게 고정)
    write_config(exclude=str(work))
    check("전역 exclude 는 마커보다 강하다", verdict(), False)

    # 마커 자체의 off 스위치
    write_config()
    marker("enabled: false\n")
    check("마커 enabled:false → 거부", verdict(), False)
    marker(None)

    # include 범위 밖
    outside = Path(tempfile.mkdtemp()) / "elsewhere"
    (outside / ".git").mkdir(parents=True)
    write_config()
    check("include 범위 밖 → 거부", gates.resolve_tenant(str(outside))[0] is None, True)

    # auto-push 허용 영역 밖
    for bad in ("shared/team", "../escape", "/absolute"):
        write_config(subdir=bad)
        check(f"subdir={bad!r} → 거부", verdict(), False)
    write_config(subdir="ouroboros/self")
    check("subdir=ouroboros/ → 통과", verdict(), True)

    # 자기 오염 — 위키가 작업 repo 안
    inner = work / "wiki"
    (inner / "per-user/me").mkdir(parents=True)
    write_config(wiki_path=inner)
    check("위키가 작업 repo 안 → 거부", verdict(), False)

    # deny 경로
    write_config()
    nested = work / "node_modules" / "pkg"
    nested.mkdir(parents=True)
    check("node_modules 하위 → 거부", gates.resolve_tenant(str(nested))[0] is None, True)

    os.environ.pop("WIGTN_WIKI_CONFIG", None)


# ═════════════════════════════════════════════════════════════
# 3. G1/G4 결정론 패턴 — 놓치면 안 되는 것만
# ═════════════════════════════════════════════════════════════
def test_deny_patterns() -> None:
    section("G1/G4 결정론 패턴")
    from knowledge_wiki import gates

    must_catch = [
        ("AWS 키", "AKIAIOSFODNN7EXAMPLE 를 썼다"),
        ("provider 키", "sk-abcdefghijklmnopqrstuvwxyz012345"),
        ("GitHub 토큰", "ghp_abcdefghijklmnopqrstuvwxyz0123456789"),
        ("개인키", "-----BEGIN RSA PRIVATE KEY-----"),
        ("접속 문자열", "postgres://admin:hunter2pass@db/app"),
        ("주민번호", "901231-1234567"),
        ("Bearer", "Authorization: Bearer abcdefghijklmnopqrstuvwxyz"),
    ]
    for name, text in must_catch:
        check(f"탐지: {name}", bool(gates.scan(text)), True)

    must_pass = [
        ("일반 기술 서술", "이 라이브러리는 재시도 시 지수 백오프를 쓴다."),
        ("의사코드", "if retries > 3: raise TimeoutError"),
    ]
    for name, text in must_pass:
        check(f"통과: {name}", gates.scan(text), [])


# ═════════════════════════════════════════════════════════════
# 4. 게시 경계 — shared/ 는 코드가 막는다
# ═════════════════════════════════════════════════════════════
def test_publish_boundary() -> None:
    section("게시 경계")
    from knowledge_wiki import publish

    tmp = Path(tempfile.mkdtemp())
    for bad in ("shared", "shared/decisions", "docs"):
        ok, why = publish.write_and_push(tmp, bad, "a.md", "x", push=False)
        check(f"auto-push 금지: {bad!r}", ok, False)
        check(f"  사유가 금지 영역인가: {bad!r}", "금지 영역" in why, True)
    check(
        "per-user/ 는 허용",
        publish.write_and_push(tmp, "per-user/me", "a.md", "x", push=False)[0],
        True,
    )


def main() -> int:
    test_fallback_parser()
    test_scope_gate()
    test_deny_patterns()
    test_publish_boundary()

    print()
    if FAILURES:
        print(f"knowledge-wiki 회귀 테스트 실패 — {len(FAILURES)}/{CHECKS}건\n")
        for f in FAILURES:
            print(f"  ✗ {f}")
        return 1
    print(f"knowledge-wiki 회귀 테스트 통과 — 검사 {CHECKS}건, 실패 0건.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
