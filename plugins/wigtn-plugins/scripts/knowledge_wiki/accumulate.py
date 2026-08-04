#!/usr/bin/env python3
"""Knowledge Wiki accumulator — Stop hook 엔트리.

세션 종료 시 contracts/INGEST-POLICY.md §3 의 4단 게이트를 순서대로 통과시킨다.

    G0 테넌트 게이트 (마커)  → G1 결정론 차단 → G2 LLM 컴파일
    → G3 LLM 감사 → G4 결정론 재검사 → per-user/ 커밋+push

**모든 실패 경로는 폐기다.** 위키 항목 하나를 잃는 건 싸고, 유출은 되돌릴 수 없다.
훅이므로 어떤 예외도 세션을 방해하지 않는다 (항상 exit 0).

상태는 위키 repo 의 `.knowledge-wiki.log` 에 남긴다 - 이전 세대 도구가
조용히 죽어서 71일간 아무도 몰랐던 실패를 반복하지 않기 위함이다.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from knowledge_wiki import compile as kw_compile  # noqa: E402
from knowledge_wiki import gates, publish  # noqa: E402

_MAX_TRANSCRIPT_CHARS = 15000
_LOG_NAME = ".knowledge-wiki.log"


def _log(wiki_path: Path | None, message: str) -> None:
    """상태 기록. 실패해도 조용히 넘어간다 (훅은 세션을 막지 않는다)."""
    if wiki_path is None:
        return
    try:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with (wiki_path / _LOG_NAME).open("a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {message}\n")
    except OSError:
        pass


def _read_transcript(path: str, cursor: Path | None) -> str:
    """transcript 의 마지막 구간을 읽는다. 커서가 있으면 델타만."""
    if not path:
        return ""
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""

    start = 0
    if cursor is not None and cursor.exists():
        try:
            start = int(cursor.read_text(encoding="utf-8").strip() or 0)
        except (OSError, ValueError):
            start = 0
    if start > len(lines):
        start = 0

    delta, chunks = lines[start:], []
    for raw in delta:
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role not in ("user", "assistant"):
            continue
        content = message.get("content")
        if isinstance(content, str):
            chunks.append(f"{role}: {content}")
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    chunks.append(f"{role}: {block.get('text', '')}")

    if cursor is not None:
        try:
            cursor.write_text(str(len(lines)), encoding="utf-8")
        except OSError:
            pass

    text = "\n".join(chunks)
    return text[-_MAX_TRANSCRIPT_CHARS:] if len(text) > _MAX_TRANSCRIPT_CHARS else text


def main() -> int:
    try:
        hook_input = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        hook_input = {}

    cwd = hook_input.get("cwd") or ""

    # ── 부트스트랩: 설정이 없으면 만든다 (사용자 파일 작업 0) ──
    # 기본값은 **로컬 축적만** - remote 가 없으면 push 하지 않는다.
    from knowledge_wiki import config as kw_config

    _, _, created = kw_config.bootstrap()
    if created and kw_config.notice_pending():
        # 조용히 시작하지 않는다. 무엇이 어디에 쌓이는지 한 번은 알린다.
        print(
            "[wigtn] 지식 위키를 켰습니다 → "
            f"{kw_config.DEFAULT_WIKI}\n"
            "        세션에서 배운 것이 자동으로 쌓입니다 (로컬 전용, push 없음).\n"
            f"        팀 공유·범위 조정: {kw_config.DEFAULT_HOME / 'knowledge-wiki.yml'}\n"
            "        끄기: 그 파일에 enabled: false",
            file=sys.stderr,
        )
        kw_config.mark_notice_shown()

    # ── G0 스코프 게이트 ──────────────────────────────────────
    tenant, reason = gates.resolve_tenant(cwd)
    if tenant is None:
        # exclude·deny 경로 등. 조용히 종료한다 (로그를 남길 위키를 특정할 수 없고,
        # 무관한 repo 를 오염시키지 않는다).
        return 0

    wiki = tenant.wiki_path

    # ── transcript 확보 ───────────────────────────────────────
    cursor = wiki / tenant.subdir / ".transcript_cursor"
    try:
        cursor.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        cursor = None  # type: ignore[assignment]

    conversation = _read_transcript(hook_input.get("transcript_path") or "", cursor)
    if not conversation.strip():
        return 0

    # ── G1 결정론 차단 (원문) ─────────────────────────────────
    hits = gates.scan(conversation)
    if hits:
        _log(wiki, f"G1 폐기 [{tenant.project}]: {', '.join(hits)}")
        return 0

    no_hooks = wiki / tenant.subdir / ".no-hooks.json"
    if not no_hooks.exists():
        try:
            no_hooks.write_text('{"disableAllHooks": true}\n', encoding="utf-8")
        except OSError:
            no_hooks = None  # type: ignore[assignment]

    # ── G2 LLM 컴파일 ─────────────────────────────────────────
    article, reason = kw_compile.compile_article(conversation, no_hooks)
    if not article:
        if reason != "기록 가치 없음 (SKIP)":
            _log(wiki, f"G2 폐기 [{tenant.project}]: {reason}")
        return 0

    # ── G3 LLM 감사 ───────────────────────────────────────────
    passed, reason = kw_compile.audit_article(article, no_hooks)
    if not passed:
        _log(wiki, f"G3 폐기 [{tenant.project}]: {reason}")
        return 0

    # ── G4 결정론 재검사 (LLM 출력을 신뢰하지 않는다) ─────────
    hits = gates.scan(article)
    if hits:
        _log(wiki, f"G4 폐기 [{tenant.project}]: {', '.join(hits)}")
        return 0

    # ── 게시 ──────────────────────────────────────────────────
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    slug = kw_compile.slugify(article) or "note"
    filename = f"{stamp}-{slug}.md"
    footer = f"\n\n<!-- project: {tenant.project} · generated: {stamp} UTC -->\n"

    ok, detail = publish.write_and_push(wiki, tenant.subdir, filename, article + footer)
    _log(wiki, ("게시" if ok else "게시 실패") + f" [{tenant.project}]: {detail}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001 - 훅은 어떤 경우에도 세션을 막지 않는다
        sys.exit(0)
