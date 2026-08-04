"""G0 테넌트 게이트 + G1/G4 결정론 redaction.

contracts/INGEST-POLICY.md 의 §3 게이트 중 결정론 부분을 집행한다. LLM 을 쓰지 않으므로
빠르고 재현 가능하며, 최종 통과 판정은 항상 여기(G4)가 내린다.

설계 원칙:
- **폐기 > 마스킹**: 금지 항목이 1건이라도 있으면 세션 전체를 버린다. 부분 정제하면
  "어디까지 지웠나"를 증명할 수 없고, 남은 문맥으로 역추론이 가능하다.
- **fail-closed**: 판정 불가·예외 = 폐기.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from knowledge_wiki import config

MARKER_NAME = ".wigtn-wiki.yml"

# 마커가 있어도 거부하는 경로 조각 (심층 방어).
# 마커 파일이 실수로 커밋된 repo 를 clone 했을 때의 방어선.
_DENY_PATH_PARTS = ("/node_modules/", "/.venv/", "/vendor/", "/site-packages/")


@dataclass(frozen=True)
class Tenant:
    """G0 통과 결과 - 이 repo 의 지식을 어디에 쌓을지."""

    repo_root: Path
    wiki_path: Path       # 위키 repo 로컬 경로
    subdir: str           # per-user/<name> 처럼 auto-push 허용 영역
    project: str          # article 분류용 라벨


# ─────────────────────────────────────────────────────────────
# G1 / G4 — 결정론 deny 패턴 (contracts/INGEST-POLICY.md §2 D1·D2·D4·D6)
# ─────────────────────────────────────────────────────────────
# D3(고객 식별)·D5(코드 원문)·D7(사업 정보)·D8(NDA)은 정규식으로 못 잡는다.
# 그건 G2 의 "일반화 강제" 구조와 G3 의 의미 감사가 담당한다.
DENY_PATTERNS: list[tuple[str, str]] = [
    # D1 — 자격증명
    (r"(?:api[_-]?key|apikey|access[_-]?token|secret[_-]?key)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}", "D1 API 키"),
    (r"AKIA[0-9A-Z]{16}", "D1 AWS 액세스 키"),
    (r"(?:sk|pk)-[A-Za-z0-9]{20,}", "D1 provider 키"),
    (r"gh[pousr]_[A-Za-z0-9]{20,}", "D1 GitHub 토큰"),
    (r"(?:password|passwd|pwd|secret|token)\s*[=:]\s*['\"][^'\"\s]{8,}['\"]", "D1 비밀번호/토큰"),
    (r"Bearer\s+[A-Za-z0-9_\-\.]{20,}", "D1 Bearer 토큰"),
    (r"-----BEGIN\s+[A-Z ]*PRIVATE KEY-----", "D1 개인키"),
    (r"(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s:/@]+:[^\s@]{4,}@", "D1 접속 문자열"),
    # D2 — 개인정보
    (r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", "D2 이메일"),
    (r"\b\d{6}\s*-\s*[1-4]\d{6}\b", "D2 주민등록번호"),
    (r"\b01[016-9]-?\d{3,4}-?\d{4}\b", "D2 휴대전화"),
    (r"\+\d{1,3}[\s\-]\d{2,4}[\s\-]\d{3,4}[\s\-]\d{4}", "D2 국제전화"),
    # D4 — 내부 인프라
    (r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}(?:\.\d{1,3})?\b", "D4 사설 IP"),
    (r"https?://(?:localhost|127\.0\.0\.1|[\w\-]+\.(?:internal|local|corp|intra|lan))\b", "D4 내부 URL"),
    (r"\b[\w\-]+\.(?:internal|local|corp|intra|lan)\b", "D4 내부 호스트명"),
    # D6 — 절대 경로 (사용자명 노출)
    (r"/(?:Users|home)/[A-Za-z0-9._\-]+/", "D6 사용자 홈 절대경로"),
    (r"[A-Z]:\\\\?Users\\\\?[A-Za-z0-9._\-]+", "D6 Windows 사용자 경로"),
]

_COMPILED: list[tuple[re.Pattern[str], str]] = [
    (re.compile(p, re.IGNORECASE), label) for p, label in DENY_PATTERNS
]


def scan(text: str) -> list[str]:
    """금지 패턴 탐지. 위반 라벨 목록을 반환한다 (빈 리스트 = 깨끗).

    G1(원문)과 G4(LLM 산출물) 양쪽에서 같은 함수를 쓴다 - 단일 정본.
    """
    if not text:
        return []
    hits: list[str] = []
    for pattern, label in _COMPILED:
        if pattern.search(text):
            hits.append(label)
    # 중복 라벨 제거 (순서 보존)
    return list(dict.fromkeys(hits))


# ─────────────────────────────────────────────────────────────
# G0 — 테넌트 게이트
# ─────────────────────────────────────────────────────────────
def _parse_marker(path: Path) -> dict[str, Any]:
    """마커 파일 파싱. 전역 설정과 같은 파서를 쓴다 (스키마가 같으므로)."""
    return config.parse_yaml(path.read_text(encoding="utf-8"))


def _locate(start: Path) -> tuple[Path, Path | None]:
    """cwd 에서 위로 올라가며 repo 루트와 마커를 찾는다 (git worktree 안전).

    Returns:
        (repo_root, marker_path | None)
    """
    current = start.resolve()
    marker: Path | None = None
    for candidate in (current, *current.parents):
        if marker is None and (candidate / MARKER_NAME).is_file():
            marker = candidate / MARKER_NAME
        if (candidate / ".git").exists():
            return candidate, marker
        if candidate == candidate.parent:
            break
    return (marker.parent if marker else current), marker


def _wiki_fields(conf: dict[str, Any]) -> tuple[str, str]:
    """설정 dict 에서 (wiki.path, wiki.subdir) 추출. 없으면 빈 문자열."""
    wiki = conf.get("wiki")
    wiki_conf: dict[str, Any] = wiki if isinstance(wiki, dict) else {}
    return (
        str(wiki_conf.get("path") or "").strip(),
        str(wiki_conf.get("subdir") or "").strip(),
    )


def _disabled(conf: dict[str, Any]) -> bool:
    return str(conf.get("enabled", "true")).strip().lower() in ("false", "no", "0", "off")


def resolve_tenant(cwd: str) -> tuple[Tenant | None, str]:
    """G0. 이 세션의 지식을 쌓을 대상을 판정한다.

    판정 순서 — **전역 설정이 정본, 마커는 override**:

    1. deny 경로면 거부 (마커·설정과 무관한 하드 게이트)
    1.5. 전역 ``enabled: false`` 면 거부 (**마커로 우회 불가** — 문서화된 kill-switch)
    2. repo 마커가 있으면 그게 최우선
       - ``enabled: false`` → 거부 (이 repo 만 끄기)
       - 자체 ``wiki:`` 블록이 있으면 그걸 사용 (다른 위키로 보내기)
       - 없으면 전역 위키 설정을 쓰되 **include 검사를 건너뛴다** (명시적 opt-in)
    3. 마커가 없으면 전역 설정의 include/exclude 로 판정

    Returns:
        (Tenant, "") 통과 / (None, 사유) 거부. **거부가 기본값이다.**
    """
    try:
        start = Path(cwd) if cwd else Path.cwd()
        resolved = str(start.resolve())
    except (OSError, ValueError, RuntimeError):
        return None, "cwd 해석 실패"

    for part in _DENY_PATH_PARTS:
        if part in resolved + "/":
            return None, f"deny 경로 ({part.strip('/')})"

    repo_root, marker = _locate(start)
    global_conf, _ = config.load()

    # 전역 kill-switch 는 마커보다 강하다. 마커의 역할은 *범위 opt-in* 이지
    # *kill-switch 해제* 가 아니다 - 사용자가 통째로 끌 수 있어야 기능을 지울 필요가 없다.
    if _disabled(global_conf):
        return None, "전역 설정에서 비활성"

    marker_conf: dict[str, Any] = {}
    if marker is not None:
        try:
            marker_conf = _parse_marker(marker)
        except (OSError, ValueError) as exc:
            return None, f"마커 파싱 실패: {exc}"
        if _disabled(marker_conf):
            return None, "마커에서 비활성"

    raw_path, subdir = _wiki_fields(marker_conf)
    source = "마커"
    if not raw_path or not subdir:
        g_path, g_subdir = _wiki_fields(global_conf)
        raw_path, subdir, source = raw_path or g_path, subdir or g_subdir, "전역 설정"

    if not raw_path or not subdir:
        if not global_conf and marker is None:
            return None, "설정 없음 (전역 설정 파일도 repo 마커도 없음)"
        return None, f"{source}에 wiki.path / wiki.subdir 없음"

    # 마커는 명시적 opt-in 이므로 include 검사를 면제한다.
    # 마커가 없으면 전역 include/exclude 가 유일한 관문이다.
    if marker is None:
        allowed, reason = config.scope_verdict(global_conf, repo_root)
        if not allowed:
            return None, reason
    else:
        for excluded in config._as_paths(global_conf.get("exclude")):
            try:
                rr = repo_root.resolve()
            except (OSError, RuntimeError):
                break
            if rr == excluded or config._is_under(rr, excluded):
                # exclude 는 마커보다 강하다 - 민감 디렉터리를 실수로 열지 못하게.
                return None, f"exclude 매칭 (마커보다 우선): {excluded}"

    # auto-push 는 개인 영역까지만 (contracts/INGEST-POLICY.md §4)
    normalized = subdir.strip("/")
    if normalized.startswith("/") or ".." in Path(normalized).parts:
        return None, f"잘못된 subdir: {subdir}"
    if not normalized.startswith(("per-user/", "ouroboros/")):
        return None, f"subdir 은 per-user/ 또는 ouroboros/ 아래여야 함: {subdir}"

    # 경로가 없고 remote 가 있으면 자동 clone (마커 > 전역 순으로 remote 를 찾는다)
    source_conf = marker_conf if _wiki_fields(marker_conf)[0] else global_conf
    wiki_path, why = config.ensure_wiki(source_conf)
    if wiki_path is None:
        return None, why

    # 자기 오염 방지: 위키가 지금 작업 중인 repo 안이면 거부한다.
    # 이걸 허용하면 "작업 repo 에 지식 디렉터리가 생기는" 옛 세대 안티패턴이 재현된다
    # (세션마다 작업 repo 가 커밋으로 오염되고, 그 커밋이 다음 세션의 입력이 된다).
    try:
        wiki_resolved, root_resolved = wiki_path.resolve(), repo_root.resolve()
    except (OSError, RuntimeError):
        return None, "경로 해석 실패"
    if wiki_resolved == root_resolved or config._is_under(wiki_resolved, root_resolved):
        return None, f"위키가 작업 repo 안에 있음 (자기 오염): {wiki_path}"

    project = str(marker_conf.get("project") or global_conf.get("project") or repo_root.name)
    return Tenant(repo_root=repo_root, wiki_path=wiki_path, subdir=normalized, project=project), ""
