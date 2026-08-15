#!/usr/bin/env bash
# editorial-diagram export — HTML 안의 인라인 SVG를 독립 .svg / .png 로 뽑는다.
#
#   ./export.sh diagram.html                 # .svg + .png(@2x)
#   ./export.sh diagram.html --scale 3       # PNG 3배
#   ./export.sh diagram.html --svg-only
#   ./export.sh diagram.html --png-only
#
# PNG는 시스템 Chrome/Edge headless를 쓴다(설치 불필요). 없으면 SVG만 나오고 안내한다.
# 실패는 조용히 넘어가지 않는다 — 크기를 못 구하거나 PNG가 잘리면 non-zero로 끝난다.
set -euo pipefail

SRC=""; SCALE=2; DO_SVG=1; DO_PNG=1
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    --scale)
      [ $# -ge 2 ] || { echo "--scale 에 값이 없다" >&2; exit 1; }
      SCALE="$2"; shift 2 ;;
    --svg-only) DO_PNG=0; shift ;;
    --png-only) DO_SVG=0; shift ;;
    -*) echo "알 수 없는 옵션: $1" >&2; exit 1 ;;
    *) SRC="$1"; shift ;;
  esac
done
[ -n "$SRC" ] || { echo "사용법: export.sh <diagram.html> [--scale N] [--svg-only|--png-only]" >&2; exit 1; }
[ -f "$SRC" ] || { echo "파일 없음: $SRC" >&2; exit 1; }
case "$SCALE" in
  ''|*[!0-9]*) echo "--scale 은 양의 정수여야 한다 (받은 값: '$SCALE')" >&2; exit 1 ;;
  0) echo "--scale 은 1 이상이어야 한다" >&2; exit 1 ;;
esac

# .svg를 입력으로 받으면 출력이 원본을 덮어쓴다 — 접미사를 붙여 막는다.
BASE="${SRC%.*}"
case "$SRC" in *.svg) BASE="${BASE}-export" ;; esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- SVG 추출 + 크기 결정 -----------------------------------------------------
# 크기는 **루트 <svg> 태그 안에서만** 읽는다. 문서 전체에서 첫 viewBox를 찾으면
# <marker viewBox="0 0 8 8">를 집어 8×8 PNG를 만들고도 성공으로 보고한다.
python3 - "$SRC" "$TMP" <<'PY'
import re, sys, pathlib

NUM = r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"
src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
out = pathlib.Path(sys.argv[2])
src = re.sub(r"<!--.*?-->", "", src, flags=re.S)


def tag_end(s, start):
    q = None
    for i in range(start, len(s)):
        c = s[i]
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == ">":
            return i
    return None


def extract(s):
    out, i = [], 0
    open_re = re.compile(r"<svg(?=[\s>/])")
    any_re = re.compile(r"<svg(?=[\s>/])|</svg\s*>")
    while True:
        m = open_re.search(s, i)
        if not m:
            return out
        j = tag_end(s, m.start())
        if j is None:
            return out
        if s[m.start():j + 1].rstrip().endswith("/>"):
            i = j + 1
            continue
        depth, k = 1, j + 1
        while depth > 0:
            m2 = any_re.search(s, k)
            if not m2:
                return out
            if m2.group(0).startswith("</"):
                depth -= 1
                k = m2.end()
            else:
                jj = tag_end(s, m2.start())
                if jj is None:
                    return out
                if not s[m2.start():jj + 1].rstrip().endswith("/>"):
                    depth += 1
                k = jj + 1
        out.append(s[m.start():k])
        i = k


def attr(open_tag, name):
    # \b는 stroke-width의 width에도 걸린다 → 하이픈 앞 경계를 명시한다
    m = re.search(rf'(?<![-\w]){name}\s*=\s*"([^"]*)"', open_tag) or \
        re.search(rf"(?<![-\w]){name}\s*=\s*'([^']*)'", open_tag)
    return m.group(1) if m else None


def size_of(open_tag, idx):
    vb = attr(open_tag, "viewBox")
    if vb:
        parts = [p for p in re.split(r"[\s,]+", vb.strip()) if p]
        if len(parts) != 4:
            sys.exit(f"SVG #{idx}: viewBox 값이 4개가 아니다 ({vb!r}) — 크기를 정할 수 없다")
        try:
            w, h = float(parts[2]), float(parts[3])
        except ValueError:
            sys.exit(f"SVG #{idx}: viewBox 값이 숫자가 아니다 ({vb!r})")
    else:
        w = attr(open_tag, "width")
        h = attr(open_tag, "height")
        if not w or not h:
            sys.exit(f"SVG #{idx}: viewBox도 width/height도 없다 — 크기를 정할 수 없다")
        def px(v, which):
            m = re.fullmatch(rf"({NUM})\s*(px)?", v.strip())
            if not m:
                sys.exit(f"SVG #{idx}: {which}={v.strip()!r} — 상대 단위(%, em, vw…)로는 "
                         "출력 크기를 정할 수 없다. viewBox를 주거나 px로 고정한다")
            return float(m.group(1))
        w, h = px(w, "width"), px(h, "height")
    if w <= 0 or h <= 0:
        sys.exit(f"SVG #{idx}: 크기가 0 이하다 ({w}×{h})")
    return int(round(w)), int(round(h))


svgs = extract(src)
if not svgs:
    sys.exit("<svg>를 찾지 못했다")

for i, s in enumerate(svgs, 1):
    j = tag_end(s, 0)
    open_tag = s[:j + 1]
    w, h = size_of(open_tag, i)
    if "xmlns=" not in open_tag:
        s = s.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        open_tag = s[:tag_end(s, 0) + 1]
    standalone = s if attr(open_tag, "width") else \
        s.replace("<svg", f'<svg width="{w}" height="{h}"', 1)
    (out / f"{i}.svg").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' + standalone, encoding="utf-8")
    (out / f"{i}.html").write_text(
        '<!doctype html><meta charset="utf-8">'
        '<style>html,body{margin:0;padding:0}svg{display:block}</style>' + standalone,
        encoding="utf-8")
    (out / f"{i}.size").write_text(f"{w} {h}\n", encoding="utf-8")
(out / "count").write_text(str(len(svgs)), encoding="utf-8")
PY

COUNT="$(cat "$TMP/count")"

find_chrome() {
  for c in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
    "$(command -v google-chrome || true)" \
    "$(command -v chromium || true)" \
    "$(command -v chromium-browser || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && { echo "$c"; return 0; }
  done
  return 1
}

# PNG가 끝까지 쓰였는지 — IEND 청크로 확인한다. 파일 크기가 잠깐 멈춘 것만으로는
# "다 썼다"를 알 수 없어서, 잘린 PNG를 성공으로 보고하는 일이 생긴다.
png_complete() {
  python3 - "$1" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
try:
    d = p.read_bytes()
except OSError:
    sys.exit(1)
# IEND 청크는 길이(4) + "IEND" + CRC(4) = 12바이트다. 8바이트만 보면 절대 일치하지 않는다.
sys.exit(0 if d[:8] == b"\x89PNG\r\n\x1a\n" and d[-12:] == b"\x00\x00\x00\x00IEND\xaeB`\x82" else 1)
PY
}

# Chrome headless는 원격 폰트(@import)를 기다리느라 스크린샷을 쓰고도 종료하지 않는
# 경우가 있다(오프라인·사내망). 완성된 PNG가 보이면 바로 끊는다. macOS엔 timeout(1)이 없다.
shoot() {
  local chrome="$1" src="$2" out="$3" w="$4" h="$5"
  rm -f "$out"
  "$chrome" --headless=new --disable-gpu --no-sandbox --no-first-run \
    --disable-extensions --hide-scrollbars --virtual-time-budget=3000 \
    --run-all-compositor-stages-before-draw \
    --force-device-scale-factor="$SCALE" --window-size="$w,$h" \
    --user-data-dir="$TMP/chrome" --screenshot="$out" "file://$src" \
    >/dev/null 2>&1 &
  local pid=$! n=0 done=1 prev=-1 cur=0
  while [ "$n" -lt 100 ]; do          # 상한 ~30초
    sleep 0.3; n=$((n + 1))
    if [ -f "$out" ]; then
      cur=$(wc -c < "$out" | tr -d " ")
      # 크기가 멈춘 뒤에만 IEND를 확인한다 (매 폴링마다 python3를 띄우면 상한이 늘어난다)
      if [ "$cur" -gt 0 ] && [ "$cur" = "$prev" ] && png_complete "$out"; then
        done=0; kill "$pid" 2>/dev/null || true; break
      fi
      prev="$cur"
    fi
    kill -0 "$pid" 2>/dev/null || { done=0; break; }   # 스스로 종료함
  done
  if [ "$n" -ge 100 ]; then
    kill "$pid" 2>/dev/null || true                   # 상한 도달 → 반드시 끊는다
  fi
  { wait "$pid"; } >/dev/null 2>&1 || true
  return "$done"
}

rc=0
for i in $(seq 1 "$COUNT"); do
  suffix=""
  if [ "$COUNT" -gt 1 ]; then suffix="-$i"; fi

  if [ "$DO_SVG" -eq 1 ]; then
    cp "$TMP/$i.svg" "${BASE}${suffix}.svg"
    echo "SVG  ${BASE}${suffix}.svg"
  fi

  if [ "$DO_PNG" -eq 1 ]; then
    if CHROME="$(find_chrome)"; then
      read -r W H < "$TMP/$i.size" || true
      shoot "$CHROME" "$TMP/$i.html" "${BASE}${suffix}.png" "$W" "$H" || true
      if [ -f "${BASE}${suffix}.png" ] && png_complete "${BASE}${suffix}.png"; then
        echo "PNG  ${BASE}${suffix}.png  (@${SCALE}x = $((W * SCALE))×$((H * SCALE)))"
      else
        if [ "$DO_SVG" -eq 1 ]; then
          echo "PNG  실패 — 완결된 PNG가 만들어지지 않았다 (SVG #$i). SVG는 정상 생성됨." >&2
        else
          echo "PNG  실패 — 완결된 PNG가 만들어지지 않았다 (SVG #$i)." >&2
        fi
        rm -f "${BASE}${suffix}.png"
        rc=1
      fi
    else
      echo "PNG  건너뜀 — Chrome/Chromium/Edge를 찾지 못했다. SVG를 브라우저에서 열어 저장하거나 Chrome을 설치한다." >&2
      rc=1
    fi
  fi
done

cat <<'NOTE'

주의
- 독립 SVG는 폰트를 @import로 불러온다 → 브라우저에선 정상, Illustrator/Figma에선
  폰트가 없으면 폴백된다. 벡터 편집이 목적이면 대상 머신에 Pretendard /
  Space Grotesk / JetBrains Mono를 설치한다.
- PNG를 슬라이드에 넣을 땐 @2x 이상. 인쇄물은 @3x.
NOTE

exit "$rc"
