#!/usr/bin/env python3
"""프롬프트 계약 검증 — 문서가 주장하는 것이 실재하는지 CI가 확인한다.

이 저장소의 반복된 실패는 "같은 사실이 여러 곳에 재진술되어 드리프트"와
"실행되지 않는 것을 공개 문서가 광고"였다. 두 가지 모두 사람이 못 지키므로
기계가 지킨다. 검사 항목:

  1. 참조 경로 실재      — ${CLAUDE_PLUGIN_ROOT}/... 로 가리킨 파일이 있는가
  2. 에이전트명 실재     — subagent_type / agent: 로 지명한 에이전트가 있는가
  3. 플래그 정의         — 본문이 쓰는 --flag 가 그 커맨드 Parameters에 있는가
  4. hooks.json 무결성   — 이벤트명·구조·참조 스크립트 실재 (과거 4회 파손)
  5. README 에이전트명   — 공개 문서가 나열한 에이전트가 실재하는가

일부러 넣지 않은 것: 임계값 리터럴 grep. 판정 경계 숫자는 코드(롤업)와
문서 양쪽에 필연적으로 존재하므로, "1곳에만 있어야 한다"는 검사는 구현
직후부터 red가 된다. (v1.4가 FR-130으로 겪은 실패)

로컬 실행: python3 .github/scripts/check_contracts.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "wigtn-plugins"

errors: List[str] = []
checked = 0

# Claude Code가 인식하는 hook 이벤트. 오타는 조용히 무시되므로 기계가 잡아야 한다.
KNOWN_HOOK_EVENTS: Set[str] = {
    "SessionStart", "SessionEnd", "Setup",
    "UserPromptSubmit", "UserPromptExpansion",
    "PreToolUse", "PostToolUse", "PostToolUseFailure", "PostToolBatch",
    "PermissionRequest", "PermissionDenied",
    "Notification", "MessageDisplay", "Stop", "StopFailure",
    "SubagentStart", "SubagentStop", "TeammateIdle",
    "TaskCreated", "TaskCompleted", "InstructionsLoaded",
    "ConfigChange", "CwdChanged", "FileChanged",
    "WorktreeCreate", "WorktreeRemove", "PreCompact", "PostCompact",
    "Elicitation", "ElicitationResult",
}

# 예시·플레이스홀더라 실재를 요구하지 않는 토큰
PLACEHOLDER = re.compile(r"\{[^}]*\}|\*|<[^>]*>|\$\{?[A-Z_]+\}?|\.\.\.")


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def md_files() -> List[Path]:
    return sorted(PLUGIN.rglob("*.md"))


def agent_names() -> Dict[str, Path]:
    """agents/*.md 의 frontmatter name → 파일."""
    out: Dict[str, Path] = {}
    for f in sorted((PLUGIN / "agents").glob("*.md")):
        m = re.search(r"^name:\s*(\S+)\s*$", f.read_text(encoding="utf-8"), re.M)
        if m:
            out[m.group(1)] = f
    return out


# ── 1. 참조 경로 실재 ────────────────────────────────────────────────────
def check_referenced_paths() -> None:
    global checked
    pat = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_\-./]+)")
    for f in md_files() + [PLUGIN / "hooks" / "hooks.json"]:
        if not f.exists():
            continue
        for m in pat.finditer(f.read_text(encoding="utf-8")):
            target = m.group(1)
            if PLACEHOLDER.search(target):
                continue
            checked += 1
            if not (PLUGIN / target).exists():
                errors.append(
                    f"{rel(f)}: ${{CLAUDE_PLUGIN_ROOT}}/{target} 가 실재하지 않음"
                )


# ── 2. 에이전트명 실재 ───────────────────────────────────────────────────
def check_agent_references() -> None:
    global checked
    names = agent_names()
    # subagent_type: "..." / agent: ... (줄 첫머리 frontmatter 필드) 만 본다.
    # 산문 속의 "agent" 는 보지 않는다 — 그러면 "agent (conditional" 같은 게 걸린다.
    pat = re.compile(
        r"(?:\bsubagent_type\s*[:=]|^\s*agent\s*:)\s*[\"']?"
        r"([a-z0-9][a-z0-9\-]*(?::[a-z0-9][a-z0-9\-]*)?)",
        re.M,
    )
    for f in md_files():
        text = f.read_text(encoding="utf-8")
        for m in pat.finditer(text):
            ref = m.group(1)
            # "wigtn-plugins:backend-architect" 처럼 플러그인 접두사가 붙는다
            if ":" in ref:
                ref = ref.split(":", 1)[1]
            # 빌트인 에이전트 타입은 이 플러그인 소유가 아니다
            if ref in {"general-purpose", "explore", "plan", "claude"}:
                continue
            checked += 1
            if ref not in names:
                errors.append(
                    f"{rel(f)}: 존재하지 않는 에이전트 '{ref}' 를 지명함 "
                    f"(agents/ 에 있는 것: {', '.join(sorted(names)[:4])}…)"
                )


# ── 3. 플래그 정의 ───────────────────────────────────────────────────────
def check_flag_definitions() -> None:
    global checked
    flag_pat = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]{1,30})")
    fence = re.compile(r"^```.*?^```", re.M | re.S)
    # 셸 바이너리가 들어 있는 인라인 코드 스팬 — 그 안의 플래그는 그 바이너리 것이다.
    # (`--resume` 처럼 플래그만 든 스팬은 우리 커맨드 파라미터이므로 남긴다)
    shell_span = re.compile(
        r"`[^`]*\b(?:git|gh|npm|npx|pnpm|yarn|bash|sh|make|python3?|pip|go|cargo"
        r"|ruff|mypy|tsc|jq|ls|cd|find|grep|sed|awk|printf|echo|touch|mkdir)\b[^`]*`"
    )
    for f in sorted((PLUGIN / "commands").glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        # 셸 예시 안의 플래그는 이 커맨드의 파라미터가 아니라 git/gh/npx 의 것이다.
        text = shell_span.sub("", fence.sub("", raw))
        # Parameters 섹션 추출 (없으면 검사 스킵 — 플래그를 안 쓰는 커맨드일 수 있다)
        sec = re.search(r"^##\s+Parameters\s*$(.*?)(?=^##\s|\Z)", raw, re.M | re.S)
        if not sec:
            continue
        defined = set(flag_pat.findall(sec.group(1)))
        # 이 저장소 관례상 커맨드 파라미터는 항상 인라인 코드로 쓴다(`--flag`).
        # 맨 산문에 섞인 "pull --rebase 제안" 같은 언급은 우리 파라미터가 아니다.
        used: Set[str] = set()
        for span in re.findall(r"`([^`]+)`", text):
            used.update(flag_pat.findall(span))
        for flag in sorted(used - defined):
            checked += 1
            errors.append(
                f"{rel(f)}: 본문이 '{flag}' 를 쓰는데 ## Parameters 에 정의가 없음"
            )


# ── 4. hooks.json 무결성 ─────────────────────────────────────────────────
def check_hooks_json() -> None:
    global checked
    path = PLUGIN / "hooks" / "hooks.json"
    if not path.exists():
        errors.append("hooks/hooks.json 이 없음")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"hooks/hooks.json: JSON 파싱 실패 — {exc}")
        return

    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        errors.append("hooks/hooks.json: 최상위 'hooks' 객체가 없음")
        return

    for event, entries in hooks.items():
        checked += 1
        if event not in KNOWN_HOOK_EVENTS:
            errors.append(
                f"hooks/hooks.json: 알 수 없는 이벤트 '{event}' "
                f"(오타는 조용히 무시되어 hook이 영영 안 돈다)"
            )
        if not isinstance(entries, list):
            errors.append(f"hooks/hooks.json: '{event}' 값이 배열이 아님")
            continue
        for i, entry in enumerate(entries):
            loc = f"hooks/hooks.json {event}[{i}]"
            if "hooks" not in entry or not isinstance(entry["hooks"], list):
                errors.append(f"{loc}: 'hooks' 배열이 없음")
                continue
            for j, h in enumerate(entry["hooks"]):
                if h.get("type") != "command":
                    errors.append(f"{loc}.hooks[{j}]: type 이 'command' 가 아님")
                if not (h.get("command") or "").strip():
                    errors.append(f"{loc}.hooks[{j}]: command 가 비어 있음")


# ── 5. README가 나열한 에이전트 실재 ─────────────────────────────────────
def check_readme_agents() -> None:
    global checked
    names = agent_names()
    known = set(names)
    # 실제 에이전트명처럼 생긴 토큰만 본다 (하이픈 2개 이상 = 이 저장소 명명 규칙)
    pat = re.compile(r"`([a-z]+(?:-[a-z]+){1,3})`")
    for readme in sorted(ROOT.glob("README*.md")):
        text = readme.read_text(encoding="utf-8")
        for m in pat.finditer(text):
            tok = m.group(1)
            # 에이전트 이름 공간에 속한 것만 검사 (접미사 규칙)
            if not tok.endswith(("-coordinator", "-reviewer", "-developer",
                                 "-architect", "-formatter", "-discovery",
                                 "-decision", "-agent")):
                continue
            checked += 1
            if tok not in known:
                errors.append(
                    f"{rel(readme)}: 공개 문서가 '{tok}' 를 나열하는데 실재하지 않음"
                )


def main() -> int:
    for fn in (
        check_referenced_paths,
        check_agent_references,
        check_flag_definitions,
        check_hooks_json,
        check_readme_agents,
    ):
        fn()

    if errors:
        print("계약 검증 실패:\n")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n{len(errors)}건. 검사 {checked}개 수행.")
        return 1
    print(f"계약 검증 통과 — 검사 {checked}개, 위반 0건.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
