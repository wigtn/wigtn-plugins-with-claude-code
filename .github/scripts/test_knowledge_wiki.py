#!/usr/bin/env python3
"""knowledge-wiki 회귀 테스트 — 결정론만, 모델 호출 없음.

여기서 지키는 것은 **경계**다. G2/G3 의 LLM 품질은 검증하지 않는다.
경계가 무너지는 두 가지 방식만 막는다:

    1. 조용히 아무것도 안 함  (설정을 못 읽어 모든 세션이 거부됨)
    2. 조용히 너무 많이 함    (꺼 뒀는데 켜져 있음 / 금지 영역에 씀)

CI 에서 `python3 .github/scripts/test_knowledge_wiki.py` 로 실행한다.
"""

from __future__ import annotations

import json
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
                     exclude: str = "", wiki_path: Path = wiki,
                     include: Path | None = None, remote: str = "") -> None:
        text = f"enabled: {enabled}\nwiki:\n  path: {wiki_path}\n  subdir: {subdir}\n"
        if remote:
            text += f"  remote: {remote}\n"
        text += f"include:\n  - {include or tmp}\n"
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

    # ── push 경계 (#40) — 범위가 넓으면 축적은 하되 push 는 보류 ──
    def tenant() -> object:
        return gates.resolve_tenant(str(work))[0]

    write_config(remote="git@example.com:team/wiki.git")
    t = tenant()
    check("remote + 좁은 include → push 허용", getattr(t, "push", None), True)

    # 픽스처가 홈 밖(임시 디렉터리)이므로 루트를 넓은 범위의 대표로 쓴다.
    # 홈 자체에 대한 판정은 아래 broad_scope_reason 단위 검사에서 본다.
    write_config(remote="git@example.com:team/wiki.git", include=Path("/"))
    t = tenant()
    check("remote + 루트 전체 include → push 보류", getattr(t, "push", None), False)
    check("  보류 사유가 기록된다", bool(getattr(t, "push_hold", "")), True)
    check("  축적 자체는 계속된다", t is not None, True)

    write_config(include=Path("/"))
    check("remote 없으면 범위가 넓어도 보류 아님", getattr(tenant(), "push", None), True)

    write_config(remote="git@example.com:team/wiki.git", include=Path("/"))
    marker("enabled: true\n")
    check("마커로 명시 opt-in 한 repo 는 보류 대상 아님", getattr(tenant(), "push", None), True)
    marker(None)

    from knowledge_wiki import config as kw_config

    check(
        "broad_scope_reason: 홈 전체는 넓다",
        bool(kw_config.broad_scope_reason({"include": [str(Path.home())]})),
        True,
    )
    check(
        "broad_scope_reason: 홈 하위는 넓지 않다",
        kw_config.broad_scope_reason({"include": [str(Path.home() / "Dev")]}),
        "",
    )

    os.environ.pop("WIGTN_WIKI_CONFIG", None)


# ═════════════════════════════════════════════════════════════
# 3. G1/G4 결정론 패턴 — 놓치면 안 되는 것만
# ═════════════════════════════════════════════════════════════
def test_deny_patterns() -> None:
    section("G1/G4 결정론 패턴")
    from knowledge_wiki import gates

    # 입력·출력 양쪽에서 반드시 잡아야 하는 것 (모델에 넣는 것 자체가 위험)
    hard = [
        ("AWS 키", "AKIAIOSFODNN7EXAMPLE 를 썼다"),
        ("provider 키", "sk-abcdefghijklmnopqrstuvwxyz012345"),
        ("GitHub 토큰", "ghp_abcdefghijklmnopqrstuvwxyz0123456789"),
        ("개인키", "-----BEGIN RSA PRIVATE KEY-----"),
        ("접속 문자열", "postgres://admin:hunter2pass@db/app"),
        ("주민번호", "901231-1234567"),
        ("Bearer", "Authorization: Bearer abcdefghijklmnopqrstuvwxyz"),
    ]
    for name, text in hard:
        check(f"G1 탐지: {name}", bool(gates.scan_input(text)), True)
        check(f"G4 탐지: {name}", bool(gates.scan(text)), True)

    # 반출물에서만 막는다. 원문에 있다고 세션을 버리지 않는다 (#35).
    output_only = [
        ("홈 절대경로", "프로젝트 파일 /Users/someone/proj/a.ts 를 수정"),
        ("개인 이메일", "문의는 person.name@example.com 으로"),
        ("사설 IP", "게이트웨이는 192.168.0.1 이다"),
        ("내부 호스트", "build.internal 에서 받는다"),
    ]
    for name, text in output_only:
        check(f"G1 통과(원문 허용): {name}", gates.scan_input(text), [])
        check(f"G4 탐지(반출 차단): {name}", bool(gates.scan(text)), True)

    # 오탐 — 어느 계층에서도 잡히면 안 된다
    clean = [
        ("일반 기술 서술", "이 라이브러리는 재시도 시 지수 백오프를 쓴다."),
        ("의사코드", "if retries > 3: raise TimeoutError"),
        ("SSH remote", "remote 는 git@github.com:team/wiki.git 이다"),
        ("noreply 주소", "커밋 트레일러의 noreply@users.example.com"),
        ("macOS 버전", "macOS 10.15.7 에서 재현됨"),
        ("Kafka 버전", "Kafka 10.2.1 클러스터에서 측정"),
        ("의존성 버전", "라이브러리 172.20.1 릴리스 노트"),
    ]
    for name, text in clean:
        check(f"오탐 없음: {name}", gates.scan(text), [])


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

    # 덮어쓰기 금지 (#39) — 같은 이름이 또 오면 접미사를 붙인다
    publish.write_and_push(tmp, "per-user/me", "dup.md", "first", push=False)
    ok, rel = publish.write_and_push(tmp, "per-user/me", "dup.md", "second", push=False)
    check("같은 파일명 재게시 성공", ok, True)
    check("  덮어쓰지 않고 새 이름을 쓴다", "dup-2.md" in rel, True)
    check(
        "  먼저 쓴 내용이 남아 있다",
        (tmp / "per-user/me/dup.md").read_text(encoding="utf-8"),
        "first",
    )


def test_slug() -> None:
    """#39 — 파일명 slug 는 절대 비지 않는다."""
    section("파일명 slug")
    from knowledge_wiki.compile import slugify

    check("ASCII 제목", slugify("# Debouncing async writes"), "debouncing-async-writes")
    check(
        "혼합 제목은 ASCII 부분을 남긴다",
        slugify("# LangGraph interrupt 패턴의 재개 조건"),
        "langgraph-interrupt",
    )
    korean = slugify("# 캐시 무효화 타이밍 문제")
    check("한글 전용 제목도 빈 값이 아니다", bool(korean), True)
    check("  note 로 수렴하지 않는다", korean != "note", True)
    check(
        "  결정론 — 같은 제목이면 같은 slug",
        slugify("# 캐시 무효화 타이밍 문제"),
        korean,
    )
    check(
        "  다른 제목이면 다른 slug",
        slugify("# 재시도 백오프 설계") != korean,
        True,
    )


_STATE_PROBE = r"""
import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from knowledge_wiki import accumulate, config

cursor = accumulate._cursor_for("/somewhere/session-abc.jsonl")
other = accumulate._cursor_for("/somewhere/session-xyz.jsonl")
print(json.dumps({
    "cursor": str(cursor) if cursor else "",
    "distinct": bool(cursor and other and cursor != other),
    "stable": str(accumulate._cursor_for("/somewhere/session-abc.jsonl")) == str(cursor),
    "no_hooks": str(accumulate._no_hooks_settings() or ""),
    "state": str(config.state_dir() or ""),
}))
"""


def test_state_isolation() -> None:
    """#36 — 커서·중첩 설정은 위키 repo 밖(머신 로컬 상태)에 있어야 한다."""
    section("상태 격리 (위키 repo 오염 방지)")

    home = Path(tempfile.mkdtemp())
    env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home)}
    env.pop("WIGTN_WIKI_CONFIG", None)
    scripts = str(REPO_ROOT / "plugins" / "wigtn-plugins" / "scripts")

    result = subprocess.run(
        [sys.executable, "-c", _STATE_PROBE, scripts],
        capture_output=True, text=True, env=env, timeout=60,
    )
    if result.returncode != 0:
        FAILURES.append(f"상태 격리 프로브 실행 실패\n    {result.stderr.strip()[:300]}")
        return

    data = json.loads(result.stdout.strip().splitlines()[-1])
    state = home / ".wigtn" / "state"
    check("state_dir 이 홈 아래 .wigtn/state", data["state"], str(state))
    check("커서가 state 아래", data["cursor"].startswith(str(state / "cursors")), True)
    check("transcript 마다 커서가 다르다", data["distinct"], True)
    check("같은 transcript 는 같은 커서", data["stable"], True)
    check("no-hooks 설정도 state 아래", data["no_hooks"], str(state / "no-hooks.json"))

    # 위키 repo 에는 article 말고 아무것도 생기지 않는다
    wiki = home / ".wigtn" / "wiki"
    strays = (
        sorted(p.name for p in wiki.rglob(".transcript_cursor")) if wiki.exists() else []
    ) + (sorted(p.name for p in wiki.rglob(".no-hooks.json")) if wiki.exists() else [])
    check("위키 repo 에 상태 파일이 생기지 않는다", strays, [])


def main() -> int:
    test_fallback_parser()
    test_scope_gate()
    test_deny_patterns()
    test_publish_boundary()
    test_slug()
    test_state_isolation()

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
