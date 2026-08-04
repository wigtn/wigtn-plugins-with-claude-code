"""전역 설정 로딩 — 사용자는 위키를 한 번만 등록한다.

repo 마다 마커 파일을 두는 건 마찰이 크다. 위키 목적지는 사용자당 보통 하나이므로
**전역 설정이 정본**이고, 마커는 예외 처리용 override 로 남긴다.

탐색 순서 (먼저 찾은 것 사용):
    $WIGTN_WIKI_CONFIG
    $XDG_CONFIG_HOME/wigtn/knowledge-wiki.yml
    ~/.config/wigtn/knowledge-wiki.yml
    ~/.wigtn/knowledge-wiki.yml

안전 속성은 유지한다:
- ``include`` 가 비어 있으면 **아무것도 하지 않는다** (설정 파일이 있어도).
  "설치했으니 다 쌓는다"가 아니라 "쌓을 곳을 지정해야 쌓는다".
- ``exclude`` 가 ``include`` 를 이긴다.
- repo 마커가 있으면 그게 최우선 (다른 위키로 보내거나, 끄거나).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

_FILENAME = "knowledge-wiki.yml"


def config_candidates() -> list[Path]:
    """설정 파일 후보 경로 (탐색 순서)."""
    paths: list[Path] = []
    override = os.environ.get("WIGTN_WIKI_CONFIG")
    if override:
        paths.append(Path(override).expanduser())
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        paths.append(Path(xdg).expanduser() / "wigtn" / _FILENAME)
    home = Path.home()
    paths.append(home / ".config" / "wigtn" / _FILENAME)
    paths.append(home / ".wigtn" / _FILENAME)
    return paths


def parse_yaml(text: str) -> dict[str, Any]:
    """YAML 파싱. PyYAML 이 없어도 동작하도록 최소 파서를 폴백으로 둔다.

    플러그인은 사용자 환경에 의존성을 강요하지 않는다. 지원 형태는
    ``key: value``, 2칸 들여쓴 1단 중첩, ``- item`` 리스트까지 (스키마가 그 이상 필요 없다).
    """
    try:
        import yaml  # type: ignore[import-untyped]

        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except ImportError:
        pass

    result: dict[str, Any] = {}
    section_key: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.strip()

        if stripped.startswith("- "):
            item = stripped[2:].strip().strip("'\"")
            if section_key is None:
                continue
            # 최상위 키는 값 없이 나오면 {} 로 선점된다 (다음 줄이 리스트인지 dict 인지
            # 아직 모르므로). 리스트로 판명되면 여기서 교체한다 - setdefault 로는
            # 선점된 {} 가 그대로 돌아와 항목이 조용히 버려진다.
            bucket = result.get(section_key)
            if not isinstance(bucket, list):
                bucket = []
                result[section_key] = bucket
            bucket.append(item)
            continue

        key, _, val = stripped.partition(":")
        key, val = key.strip(), val.strip().strip("'\"")

        if not line.startswith(" "):
            if val:
                result[key] = val
                section_key = None
            else:
                # 다음 줄이 리스트인지 dict 인지 아직 모른다 - 리스트면 위에서 채워지고,
                # dict 면 아래 분기가 덮어쓴다.
                result[key] = {}
                section_key = key
        elif section_key is not None:
            bucket = result.get(section_key)
            if not isinstance(bucket, dict):
                bucket = {}
                result[section_key] = bucket
            bucket[key] = val
    return result


def load() -> tuple[dict[str, Any], Path | None]:
    """전역 설정을 읽는다. 없으면 ``({}, None)``."""
    for path in config_candidates():
        try:
            if path.is_file():
                return parse_yaml(path.read_text(encoding="utf-8")), path
        except (OSError, ValueError):
            continue
    return {}, None


# ─────────────────────────────────────────────────────────────
# 부트스트랩 — 설정 파일 없이도 바로 동작하게
# ─────────────────────────────────────────────────────────────
DEFAULT_HOME = Path.home() / ".wigtn"
DEFAULT_WIKI = DEFAULT_HOME / "wiki"
_NOTICE_FLAG = DEFAULT_HOME / ".notice-shown"
_STATE_DIR = DEFAULT_HOME / "state"


def state_dir() -> Path | None:
    """머신 로컬 상태 디렉터리. **위키 repo 밖이다.**

    커서와 중첩 호출 차단 설정은 위키 *콘텐츠* 가 아니라 이 기계의 상태다.
    위키 안에 두면 clone 한 팀 repo 워킹카피가 지저분해지고(팀 repo 에 .gitignore 를
    써 넣는 건 요청하지 않은 공유 저장소 변경이다), 커서가 위키 경로에 묶여
    프로젝트끼리 섞인다.

    Returns:
        디렉터리 경로 / 만들 수 없으면 None (호출부가 fail-closed 처리)
    """
    try:
        _STATE_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None
    return _STATE_DIR

_DEFAULT_TEMPLATE = """# wigtn knowledge-wiki — 자동 생성됨
#
# 이 파일은 플러그인이 처음 동작할 때 만들었다. 그대로 둬도 되고 고쳐도 된다.
#
# 기본값 = **로컬 축적만**. remote 가 없으면 push 하지 않는다.
# 팀과 공유하려면 아래 remote 를 채운다 (없는 경로면 자동 clone).

wiki:
  path: {wiki}
  subdir: per-user/{user}
  # remote: git@github.com:myteam/team-wiki.git

# 지식을 쌓을 경로. 기본 = 홈 전체 (로컬 전용이라 허용).
# 범위가 홈/루트 전체인 동안에는 remote 가 있어도 push 하지 않는다 (로컬 축적만).
# 좁히면 그때 push 가 켜진다 - 예: - {home}/Dev
include:
  - {home}

# 제외할 경로. 고객사·NDA repo 는 여기에 넣는다. include 보다 강하다.
exclude:
  - {wiki}
"""


def _sanitize_user(name: str) -> str:
    cleaned = "".join(c for c in name if c.isalnum() or c in "-_")
    return cleaned.lower()[:32] or "me"


def current_user() -> str:
    import getpass

    try:
        return _sanitize_user(getpass.getuser())
    except Exception:  # noqa: BLE001 - 환경에 따라 실패할 수 있다
        return "me"


def bootstrap() -> tuple[dict[str, Any], Path | None, bool]:
    """설정이 없으면 기본 설정 + 로컬 위키를 만든다.

    사용자가 파일을 만들지 않아도 바로 축적이 시작되게 한다. 단 **remote 가 없으므로
    push 하지 않는다** - 기계 밖으로 나가는 건 항상 명시적 설정을 거친다.
    (transcript 는 이미 로컬에 있으므로 로컬 article 은 새 노출이 아니다.)

    Returns:
        (conf, config_path, 새로 만들었는지)
    """
    conf, path = load()
    if conf:
        return conf, path, False

    target = DEFAULT_HOME / _FILENAME
    try:
        DEFAULT_WIKI.mkdir(parents=True, exist_ok=True)
        (DEFAULT_WIKI / f"per-user/{current_user()}").mkdir(parents=True, exist_ok=True)
        target.write_text(
            _DEFAULT_TEMPLATE.format(
                wiki=DEFAULT_WIKI, user=current_user(), home=Path.home()
            ),
            encoding="utf-8",
        )
    except OSError:
        return {}, None, False

    _git_init(DEFAULT_WIKI)
    conf, path = load()
    return conf, path, True


def _git_init(path: Path) -> None:
    """위키 디렉터리를 git repo 로 만든다 (이미 repo 면 no-op)."""
    import subprocess

    try:
        probe = subprocess.run(
            ["git", "rev-parse", "--git-dir"], cwd=str(path),
            capture_output=True, text=True, timeout=15,
        )
        if probe.returncode == 0:
            return
        subprocess.run(["git", "init", "-q"], cwd=str(path),
                       capture_output=True, timeout=15)
        gitignore = path / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(".transcript_cursor\n.no-hooks.json\n", encoding="utf-8")
    except (subprocess.SubprocessError, OSError):
        pass


def notice_pending() -> bool:
    """최초 부트스트랩 안내를 아직 안 보여줬는지."""
    return not _NOTICE_FLAG.exists()


def mark_notice_shown() -> None:
    try:
        _NOTICE_FLAG.parent.mkdir(parents=True, exist_ok=True)
        _NOTICE_FLAG.write_text("1\n", encoding="utf-8")
    except OSError:
        pass


def ensure_wiki(conf: dict[str, Any]) -> tuple[Path | None, str]:
    """위키 경로를 확보한다. 없고 ``remote`` 가 있으면 clone 한다.

    Returns:
        (path, "") 성공 / (None, 사유) 실패
    """
    wiki = conf.get("wiki")
    wiki_conf: dict[str, Any] = wiki if isinstance(wiki, dict) else {}
    raw = str(wiki_conf.get("path") or "").strip()
    if not raw:
        return None, "wiki.path 없음"

    path = Path(raw).expanduser()
    if path.is_dir():
        return path, ""

    remote = str(wiki_conf.get("remote") or "").strip()
    if not remote:
        return None, f"위키 경로 없음: {path}"

    import subprocess

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", "--quiet", remote, str(path)],
            capture_output=True, text=True, timeout=180,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return None, f"clone 실패: {exc}"
    if result.returncode != 0:
        detail = (result.stderr or "").strip().splitlines()
        return None, f"clone 실패: {detail[-1][:80] if detail else '?'}"
    return (path, "") if path.is_dir() else (None, "clone 후에도 경로 없음")


def _as_paths(value: Any) -> list[Path]:
    """문자열 또는 리스트를 확장된 경로 목록으로."""
    if not value:
        return []
    items = value if isinstance(value, list) else [value]
    out: list[Path] = []
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        try:
            out.append(Path(text).expanduser().resolve())
        except (OSError, ValueError, RuntimeError):
            continue
    return out


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def remote_of(conf: dict[str, Any]) -> str:
    """설정에서 ``wiki.remote`` 추출. 없으면 빈 문자열."""
    wiki = conf.get("wiki")
    wiki_conf: dict[str, Any] = wiki if isinstance(wiki, dict) else {}
    return str(wiki_conf.get("remote") or "").strip()


def broad_scope_reason(conf: dict[str, Any]) -> str:
    """``include`` 가 push 를 켜기엔 너무 넓으면 사유를, 아니면 빈 문자열.

    로컬 축적과 팀 공유는 위험도가 다르다. ``remote`` 한 줄을 추가하는 행위의
    사용자 인지는 "팀 공유를 켰다"인데, ``include`` 가 홈 전체면 실제로 일어나는 일은
    "이 기계의 **모든** repo 지식이 원격으로 나가기 시작했다"이다. 한 기계에서 여러
    조직 일을 하면 그게 곧 유출 경로다.

    막는 방식은 **push 보류**지 축적 중단이 아니다. 축적까지 끄면 remote 를 추가한
    사용자가 "아무 일도 안 일어나는" 상태를 만나게 된다 - 이 파이프라인이 피하려는
    실패 모드와 같은 모양이다.
    """
    try:
        home = Path.home().resolve()
    except (OSError, RuntimeError):
        return ""
    for included in _as_paths(conf.get("include")):
        if included == home or included == Path(included.anchor):
            return f"include 범위가 홈/루트 전체 ({included}) - 좁히면 push 가 켜진다"
    return ""


def scope_verdict(conf: dict[str, Any], repo_root: Path) -> tuple[bool, str]:
    """전역 설정의 include/exclude 로 이 repo 가 대상인지 판정한다.

    Returns:
        (True, "") 대상 / (False, 사유) 제외. **제외가 기본값이다.**
    """
    includes = _as_paths(conf.get("include"))
    if not includes:
        return False, "include 미설정 (쌓을 경로를 지정해야 동작한다)"

    try:
        resolved = repo_root.resolve()
    except (OSError, RuntimeError):
        return False, "repo 경로 해석 실패"

    for excluded in _as_paths(conf.get("exclude")):
        if _is_under(resolved, excluded) or resolved == excluded:
            return False, f"exclude 매칭: {excluded}"

    for included in includes:
        if _is_under(resolved, included) or resolved == included:
            return True, ""
    return False, "include 범위 밖"
