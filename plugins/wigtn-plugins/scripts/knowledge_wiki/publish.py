"""위키 repo 에 커밋 + push.

contracts/INGEST-POLICY.md §4: auto-push 는 개인 영역(`per-user/`, `ouroboros/`)까지다.
`shared/` 로의 승격은 사람이 PR 로 한다 - 이 모듈은 거기에 쓰지 않는다
(경로 검증은 gates.resolve_tenant 가 이미 했고, 여기서 한 번 더 확인한다).
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

_TIMEOUT = 60
_ALLOWED_ROOTS = ("per-user/", "ouroboros/")


def _git(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return 1, str(exc)
    return result.returncode, (result.stdout + result.stderr).strip()


def _free_path(target: Path) -> Path | None:
    """이미 있으면 접미사를 붙여 비어 있는 경로를 찾는다.

    덮어쓰기는 하지 않는다 - 잃어버린 쪽은 로그에도 "게시 성공"으로 남아서
    사라진 걸 알 방법이 없다.
    """
    if not target.exists():
        return target
    for n in range(2, 100):
        candidate = target.with_name(f"{target.stem}-{n}{target.suffix}")
        if not candidate.exists():
            return candidate
    return None


def write_and_push(
    wiki_path: Path,
    subdir: str,
    filename: str,
    content: str,
    *,
    push: bool = True,
) -> tuple[bool, str]:
    """article 을 위키 repo 에 쓰고 커밋·push 한다.

    Returns:
        (True, 상대경로) 성공 / (False, 사유) 실패
    """
    normalized = subdir.strip("/")
    if not normalized.startswith(_ALLOWED_ROOTS):
        # 방어선 2 - resolve_tenant 를 우회한 호출이 있어도 shared/ 는 막는다
        return False, f"auto-push 금지 영역: {subdir}"

    target_dir = wiki_path / normalized
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        target = _free_path(target_dir / filename)
        if target is None:
            return False, f"파일명 충돌 회피 실패: {filename}"
        target.write_text(content, encoding="utf-8")
    except OSError as exc:
        return False, f"파일 쓰기 실패: {exc}"

    rel = f"{normalized}/{target.name}"

    code, out = _git(["rev-parse", "--git-dir"], wiki_path)
    if code != 0:
        return True, f"{rel} (git repo 아님 - 파일만 저장)"

    code, out = _git(["add", "--", rel], wiki_path)
    if code != 0:
        return False, f"git add 실패: {out}"

    # 변경이 없으면 커밋하지 않는다 (빈 커밋 방지)
    code, _ = _git(["diff", "--cached", "--quiet"], wiki_path)
    if code == 0:
        return True, f"{rel} (변경 없음)"

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    code, out = _git(
        ["commit", "-m", f"docs(wiki): {target.stem} ({stamp})", "--", rel],
        wiki_path,
    )
    if code != 0:
        return False, f"git commit 실패: {out}"

    if not push:
        return True, f"{rel} (커밋만)"

    # remote 가 없으면 로컬 축적만 한다 (부트스트랩 기본값). 실패가 아니라 정상 경로다.
    code, remotes = _git(["remote"], wiki_path)
    if code != 0 or not remotes.strip():
        return True, f"{rel} (로컬 축적 - remote 미설정)"

    code, out = _git(["push"], wiki_path)
    if code != 0:
        # 커밋은 남았으므로 다음 실행이나 수동 push 로 복구 가능
        return True, f"{rel} (커밋됨, push 실패: {out.splitlines()[-1][:80] if out else '?'})"
    return True, rel
