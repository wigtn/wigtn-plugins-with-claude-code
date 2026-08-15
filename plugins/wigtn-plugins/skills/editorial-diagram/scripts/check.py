#!/usr/bin/env python3
"""editorial-diagram 출력 검증기.

    python3 check.py out.html [--theme light|dark] [--quiet]

exit 0 = PASS/WARN, exit 1 = FAIL.

## 이 도구의 계약 (중요)

이건 **임의 SVG 검증기가 아니다.** `assets/template.html`이 만드는 *정규 형태*만
검증한다. 브라우저를 다시 구현하지 않기 때문에, 지원 범위 밖 구문은 조용히
통과시키지 않고 **"미지원 구문 → FAIL"**로 끊는다. 검증할 수 없는 것을 통과시키면
게이트가 꺼진 줄도 모르게 꺼진다.

정규 형태:

- 색은 **3/6자리 HEX만**. `rgb()`·`color-mix()`·색이름·8자리 HEX는 FAIL.
- 노드는 `rect`/`polygon`/`circle`/`ellipse`에 `class="node"`. `g`·`path` 노드는 FAIL.
- 폰트 크기는 `px`/`rem`/`em`만.
- 색·폰트·정렬은 **클래스 규칙으로**. `text`/`tspan`/`g`의 표현 속성·인라인 style은 FAIL.
- `--토큰`은 **루트 한 곳에서만** 선언한다. 자손에서 재정의하면 FAIL.
- 셀렉터는 `type`/`.class`/`#id`/`[attr]`/`[attr=v]` 조합만. 결합자·부분일치는 FAIL.
- 렌더 요소는 화이트리스트만. `use`/`foreignObject`/`image`/중첩 `svg`는 FAIL.
- 캔버스는 `viewBox`로 지정한다.

**다크 블록을 선언하면 다크 팔레트도 검증한다** — 두 테마 모두 대비를 통과해야 한다.
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET

GRID = 4
MAX_NODES = 9
IDEAL_NODES = 5
MAX_FOCAL = 2
PAD = 20                      # 노드 좌우 안쪽 여백
NODE_PADDING = PAD * 2

GEOM_ATTRS = {
    "rect": ("x", "y", "width", "height", "rx", "ry"),
    "circle": ("cx", "cy", "r"),
    "ellipse": ("cx", "cy", "rx", "ry"),
    "line": ("x1", "y1", "x2", "y2"),
    "image": ("x", "y", "width", "height"),
    "use": ("x", "y"),
}
POINT_SHAPES = ("polygon", "polyline")
NODE_SHAPES = ("rect", "polygon", "circle", "ellipse")
NON_RENDERED = ("defs", "marker", "symbol", "pattern", "clipPath", "mask")
CHECKED_PROPS = ("fill", "stroke", "font-size", "font-family", "text-anchor")
INHERITED_PROPS = ("fill", "font-size", "font-family", "text-anchor")

# 정규 형태에서 나올 수 있는 요소는 이게 전부. use/foreignObject/image/중첩 svg는
# 참조나 좌표계 때문에 정적으로 잴 수 없다 → 무시하지 않고 계약 위반으로 끊는다.
ALLOWED_ELEMENTS = {"svg", "g", "defs", "style", "title", "desc", "marker",
                    "rect", "circle", "ellipse", "line", "polygon", "polyline",
                    "path", "text", "tspan"}
ALLOWED_RX = (0, 4, 8)

FONT_SIZE_FALLBACK = {
    "title": 28.0, "subtitle": 15.0, "node-name": 18.0, "sublabel": 13.0, "foot": 12.0,
}
KNOWN_CANVASES = {(1280, 720), (1024, 768), (1200, 630)}

# 이모지 표현형만. ✓ ✗ ★ ⚠ 같은 기호는 정상 타이포라 제외한다.
EMOJI = re.compile("[\U0001F000-\U0001FAFF⬀-⯿"
                   "✅❌❎❓-❕❗➕-➗➰➿]|️")
NUM_RE = r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"
HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\Z")

BAD = object()


# ---------------------------------------------------------------- 값 파싱
def num(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return BAD


def length_px(v):
    if v is None:
        return None
    m = re.fullmatch(rf"({NUM_RE})\s*(px|rem|em)?", str(v).strip())
    if not m:
        return BAD
    return float(m.group(1)) * (16.0 if m.group(2) in ("rem", "em") else 1.0)


def hex_rgb(v):
    if not v:
        return None
    m = HEX_RE.match(str(v).strip())
    if not m:
        return None
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def srgb_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(v):
    rgb = hex_rgb(v)
    if rgb is None:
        return None
    r, g, b = (srgb_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    lf, lb = luminance(fg), luminance(bg)
    if lf is None or lb is None:
        return None
    hi, lo = max(lf, lb), min(lf, lb)
    return (hi + 0.05) / (lo + 0.05)


def is_wide(ch):
    o = ord(ch)
    return (0x1100 <= o <= 0x11FF or 0x3040 <= o <= 0x30FF or 0x3130 <= o <= 0x318F
            or 0x3400 <= o <= 0x9FFF or 0xAC00 <= o <= 0xD7A3 or 0xFF00 <= o <= 0xFF60)


def text_width(s, font_size, mono=False):
    latin = 0.6 if mono else 0.55
    return sum(font_size * (1.0 if is_wide(c) else latin) for c in s)


# ---------------------------------------------------------------- 리포트
class Report:
    def __init__(self):
        self.items = []

    def add(self, lv, rule, msg):
        self.items.append((lv, rule, msg))

    def fail(self, r, m):
        self.add("FAIL", r, m)

    def warn(self, r, m):
        self.add("WARN", r, m)

    def info(self, r, m):
        self.add("INFO", r, m)

    @property
    def verdict(self):
        lv = {x for x, _, _ in self.items}
        return "FAIL" if "FAIL" in lv else ("WARN" if "WARN" in lv else "PASS")


# ---------------------------------------------------------------- 문서
class Doc:
    def __init__(self, root):
        self.root = root
        self.ns = root.tag.split("}")[0] + "}" if "}" in root.tag else ""
        self.parent = {id(root): None}
        for p in root.iter():
            for c in p:
                self.parent[id(c)] = p
        self.hidden = set()
        for name in NON_RENDERED:
            for c in root.iter(self.q(name)):
                self.hidden.update(id(d) for d in c.iter())

    def q(self, n):
        return f"{self.ns}{n}"

    def tag(self, el):
        return el.tag.replace(self.ns, "") if self.ns else el.tag

    def rendered(self, el):
        return id(el) not in self.hidden

    def iter_rendered(self, name=None):
        it = self.root.iter(self.q(name)) if name else self.root.iter()
        return (el for el in it if self.rendered(el))


def classes(el):
    return set((el.get("class") or "").split())


def describe(doc, el):
    keys = ("class", "id", "x", "y", "cx", "cy", "x1", "y1")
    bits = [f'{k}="{el.get(k)}"' for k in keys if el.get(k) is not None]
    return f"<{doc.tag(el)} {' '.join(bits)}>" if bits else f"<{doc.tag(el)}>"


# ---------------------------------------------------------------- CSS
SEL_TOKEN = re.compile(r"\A(?P<type>[-\w]+)?(?P<rest>(?:\#[-\w]+|\.[-\w]+)*)\Z")
# [attr] / [attr=v] / [attr="v"] / [attr='v'] 만. ^= *= $= |= ~= 는 해석하지 않는다.
ATTR_RE = re.compile(r"""\[\s*([-\w]+)\s*(?:=\s*(?:"([^"]*)"|'([^']*)'|([-\w]+))\s*)?\]""")


class Sel:
    def __init__(self, type_, id_, cls, attrs):
        self.type, self.id, self.cls, self.attrs = type_, id_, cls, attrs
        self.spec = (1 if id_ else 0, len(cls) + len(attrs), 1 if type_ else 0)

    def matches(self, doc, el):
        if self.type and self.type not in (doc.tag(el), "*"):
            return False
        if self.id and el.get("id") != self.id:
            return False
        if not self.cls <= classes(el):
            return False
        for k, v in self.attrs:
            if v is None:
                if el.get(k) is None:
                    return False
            elif (el.get(k) or "") != v:
                return False
        return True


def sel_text(sel):
    """진단 메시지용 — 속성까지 보여야 어느 규칙인지 식별된다."""
    parts = [sel.type or ""]
    if sel.id:
        parts.append(f"#{sel.id}")
    parts += [f".{c}" for c in sorted(sel.cls)]
    parts += [f"[{k}={v!r}]" if v is not None else f"[{k}]" for k, v in sel.attrs]
    return "".join(parts) or "*"


def parse_selector(sel):
    """해석 못 하면 None — 호출부가 FAIL로 끊는다 (잘못 해석해서 통과시키지 않는다)."""
    s = re.sub(r"\s+", " ", sel).strip()
    if not s or any(c in s for c in " >+~,:"):
        return None
    attrs = [(m.group(1), next((g for g in m.groups()[1:] if g is not None), None))
             for m in ATTR_RE.finditer(s)]
    rest = ATTR_RE.sub("", s)
    if "[" in rest or "]" in rest:
        return None
    m = SEL_TOKEN.match(rest)
    if not m:
        return None
    ids = re.findall(r"#([-\w]+)", m.group("rest") or "")
    if len(ids) > 1:
        return None
    cls = set(re.findall(r"\.([-\w]+)", m.group("rest") or ""))
    return Sel(m.group("type"), ids[0] if ids else None, cls, attrs)


def strip_at_rule_blocks(css):
    out, i, removed = [], 0, 0
    while True:
        m = re.search(r"@[-\w]+[^;{]*\{", css[i:])
        if not m:
            out.append(css[i:])
            break
        start = i + m.start()
        out.append(css[i:start])
        depth, j, q = 0, i + m.end() - 1, None
        while j < len(css):
            c = css[j]
            if q:
                if c == q:
                    q = None
            elif c in "\"'":
                q = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        removed += 1
        i = j + 1
    return "".join(out), removed


def parse_style(doc, rep):
    css = "\n".join("".join(s.itertext()) for s in doc.root.iter(doc.q("style")))
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css, n_at = strip_at_rule_blocks(css)
    if n_at:
        rep.warn("css", f"at-rule 블록 {n_at}개는 검증 대상이 아니다 — "
                        "테마는 data-theme 속성으로 분기한다(tokens.md §2)")
    rules = []
    for order, (raw, body) in enumerate(re.findall(r"([^{}]+)\{([^{}]*)\}", css)):
        raw = raw.split(";")[-1]
        decls, imps = {}, set()
        for k, v in re.findall(r"([-\w]+)\s*:\s*([^;]+?)\s*(?:;|$)", body):
            v2 = re.sub(r"\s*!\s*important\s*$", "", v)
            if v2 != v:
                imps.add(k)
            decls[k] = v2.strip()
        if not decls:
            continue
        watched = [k for k in decls if k.startswith("--") or k in CHECKED_PROPS]
        for part in raw.split(","):          # `.a, .b { … }` 는 흔한 관용구라 지원한다
            if not part.strip():
                continue
            sel = parse_selector(part)
            if sel is None:
                if watched:
                    rep.fail("css", f"해석할 수 없는 셀렉터 '{part.strip()}'가 "
                                    f"{', '.join(sorted(watched))}를 선언한다 — "
                                    "type/.class/#id/[attr=v] 조합만 지원한다")
                continue
            rules.append((sel, decls, imps, order))
    return rules


def declared(doc, rules, el, prop):
    """CSS 캐스케이드: (!important, 특정성, 문서순서) 최대."""
    best, best_key = None, None
    for sel, decls, imps, order in rules:
        if prop not in decls or not sel.matches(doc, el):
            continue
        key = (prop in imps, sel.spec, order)
        if best_key is None or key > best_key:
            best, best_key = decls[prop], key
    return best


def inline_prop(el, prop):
    m = re.search(rf"(?<![-\w]){prop}\s*:\s*([^;]+)", el.get("style") or "")
    return m.group(1).strip() if m else None


def tokens_for(doc, rules):
    """루트에 적용되는 --토큰. 테마는 doc.root의 data-theme 속성이 결정한다."""
    toks, keys = {}, {}
    for sel, decls, imps, order in rules:
        t = {k: v for k, v in decls.items() if k.startswith("--")}
        if not t or not sel.matches(doc, doc.root):
            continue
        for k, v in t.items():
            key = (k in imps, sel.spec, order)
            if k not in keys or key > keys[k]:
                toks[k], keys[k] = v, key
    return toks


def declared_themes(rules):
    """스타일시트가 선언한 테마. 다크 블록이 있으면 다크도 검증해야 한다."""
    themes = {"light"}
    for sel, _, _, _ in rules:
        for k, v in sel.attrs:
            if k == "data-theme" and v:
                themes.add(v)
    return themes


def resolve_font(doc, rules, el):
    raw = inline_prop(el, "font-size") or declared(doc, rules, el, "font-size")
    size = length_px(raw) if raw is not None else None
    if size is None:
        size = next((FONT_SIZE_FALLBACK[c] for c in sorted(classes(el))
                     if c in FONT_SIZE_FALLBACK), 16.0)
    fam = (inline_prop(el, "font-family") or declared(doc, rules, el, "font-family") or "")
    return size, "mono" in fam.lower()


def resolve_anchor(doc, rules, el):
    # SVG 기본값은 start다. middle로 가정하면 좌측 배치 라벨에 없는 오버플로를 만들고,
    # 중앙 배치 라벨의 실제 이탈을 놓친다.
    v = (inline_prop(el, "text-anchor") or declared(doc, rules, el, "text-anchor") or "start")
    v = v.strip()
    return v if v in ("start", "middle", "end") else None


# ---------------------------------------------------------------- 계약
def token_values(doc, rules, name):
    """선언된 모든 테마에서의 토큰 값 집합 (정규화된 RGB). 리터럴 우회 탐지용."""
    out, original = set(), doc.root.get("data-theme")
    for th in sorted(declared_themes(rules)):
        doc.root.set("data-theme", th)
        v = tokens_for(doc, rules).get(f"--{name}")   # 토큰 키는 `--name` 형태다
        rgb = hex_rgb(v) if v else None
        if rgb:
            out.add(rgb)
    if original is None:
        doc.root.attrib.pop("data-theme", None)
    else:
        doc.root.set("data-theme", original)
    return out


def uses(value, names, values):
    """`var(--name)` 이거나, 토큰과 같은 색을 손으로 적었거나.

    이름은 **경계까지** 맞춘다 — 접두사로 비교하면 `var(--line-strong)`이
    `--line` 규칙에 걸린다(정상 사용을 차단하는 오탐).
    """
    v = value or ""
    for nm in names:
        if re.search(rf"var\(\s*--{re.escape(nm)}\s*[,)]", v):
            return True
    rgb = hex_rgb(value)
    return rgb is not None and rgb in values


def check_contract(doc, rules, rep):
    accents = token_values(doc, rules, "accent")
    lines = token_values(doc, rules, "line")
    for el in doc.root.iter():
        t = doc.tag(el)
        if t == "svg" and el is not doc.root:
            rep.fail("contract", "중첩 <svg> — 새 뷰포트를 만들어 내용을 자르거나 스케일한다. "
                                 "정적으로 측정할 수 없다")
            continue
        if t not in ALLOWED_ELEMENTS:
            rep.fail("contract", f"<{t}> — 정규 형태에 없는 요소다. use/foreignObject/image/"
                                 "중첩 svg는 정적으로 측정할 수 없어 검사를 무력화한다")
    for el in doc.iter_rendered():
        t = doc.tag(el)
        if "node" in classes(el) and t not in NODE_SHAPES:
            rep.fail("contract", f'{describe(doc, el)} — class="node"는 '
                                 f"{'/'.join(NODE_SHAPES)}에만 붙인다(받은 것: {t})")
        if t in ("text", "tspan", "g"):
            for prop in INHERITED_PROPS:
                if el.get(prop) is not None:
                    rep.fail("contract", f'{describe(doc, el)} {prop}="{el.get(prop)}" — '
                                         f"{t}의 {prop}은 표현 속성이 아니라 클래스 규칙으로 준다")
                if prop != "font-size" and inline_prop(el, prop):
                    rep.fail("contract", f"{describe(doc, el)} style에 {prop} — "
                                         "클래스 규칙으로 준다")
        if t in ("g", "tspan") and (classes(el) or el.get("style")):
            what = "<g>는 묶기 전용" if t == "g" else "<tspan>은 줄바꿈 전용"
            rep.fail("contract", f"{describe(doc, el)} — {what}이다. class·style을 주면 "
                                 "상속으로 색·폰트가 바뀌는데 그걸 계산하지 않는다"
                                 "(스타일은 부모 <text>에 준다)")
        if t == "rect":
            for a in ("rx", "ry"):
                v = num(el.get(a))
                if v not in (None, BAD) and int(v) not in ALLOWED_RX:
                    rep.fail("contract", f'{describe(doc, el)} {a}="{v:g}" — '
                                         f"{ALLOWED_RX} 중 하나여야 한다")
        if "focal" in classes(el) and doc.tag(el) != "circle":
            fill = el.get("fill") or declared(doc, rules, el, "fill") or ""
            if uses(fill, ("accent", "accent-deep"), accents):
                rep.fail("contract", f"{describe(doc, el)} — 초점은 악센트로 **채우지** 않는다. "
                                     "2px 테두리 + 시그니처 점으로 표시한다(SKILL.md 하드 규칙 3)")
        if "node" in classes(el):
            stroke = el.get("stroke") or declared(doc, rules, el, "stroke") or ""
            if uses(stroke, ("line",), lines):
                rep.fail("contract", f"{describe(doc, el)} — 노드 테두리에 --line은 대비 1.3:1이라 "
                                     "쓸 수 없다. --line-strong을 쓴다(tokens.md §1)")
    for el in doc.iter_rendered("text"):
        if resolve_font(doc, rules, el)[0] is BAD:
            rep.fail("contract", f"{describe(doc, el)} font-size를 px/rem/em으로 읽을 수 없다")
        if resolve_anchor(doc, rules, el) is None:
            rep.fail("contract", f"{describe(doc, el)} text-anchor를 해석할 수 없다 "
                                 "(start/middle/end만 지원)")
    # 루트를 겨냥한 규칙이 상속 속성을 선언하면 <g>와 같은 문제가 생긴다
    original_r = doc.root.get("data-theme")
    for th in sorted(declared_themes(rules)):
        doc.root.set("data-theme", th)
        for sel, decls, _, _ in rules:
            watched = sorted(k for k in decls if k in INHERITED_PROPS)
            if watched and sel.matches(doc, doc.root):
                rep.fail("contract", f"셀렉터 '{sel_text(sel)}'가 루트에 "
                                     f"{', '.join(watched)}를 선언한다 — 상속으로 모든 자손의 "
                                     "색·폰트가 바뀌는데 그걸 계산하지 않는다. 클래스에 준다")
    if original_r is None:
        doc.root.attrib.pop("data-theme", None)
    else:
        doc.root.set("data-theme", original_r)

    # --토큰은 루트에서만. 단 테마 변형(`[data-theme=…]`)은 정규 형태이므로,
    # 선언된 테마 중 하나로라도 루트에 걸리면 합법이다.
    original = doc.root.get("data-theme")
    themes = sorted(declared_themes(rules))
    for sel, decls, _, _ in rules:
        if not any(k.startswith("--") for k in decls):
            continue
        ok = False
        for th in themes:
            doc.root.set("data-theme", th)
            if sel.matches(doc, doc.root):
                ok = True
                break
        if not ok:
            rep.fail("contract", f"셀렉터 '{sel_text(sel)}'가 --토큰을 재정의한다 — "
                                 "토큰은 루트에서만 선언한다"
                                 "(CSS 변수는 상속되어 대비 검증을 우회한다)")
    if original is None:
        doc.root.attrib.pop("data-theme", None)
    else:
        doc.root.set("data-theme", original)


def check_tokens_are_hex(tokens, theme, rep):
    for k, v in sorted(tokens.items()):
        if hex_rgb(v) is None:
            rep.fail("contract", f"[{theme}] 토큰 {k}={v.strip()!r} — 3/6자리 HEX만 지원한다")


# ---------------------------------------------------------------- 기하
PATH_PARAMS = {"m": 2, "l": 2, "t": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "a": 7, "z": 0}
ARC_COORD_IDX = {5, 6}


def path_numbers(d):
    toks = re.findall(rf"[A-Za-z]|{NUM_RE}", d or "")
    coords, cmd, idx = [], None, 0
    for t in toks:
        if t.isalpha():
            cmd, idx = t.lower(), 0
            continue
        if cmd is None:
            continue
        n = PATH_PARAMS.get(cmd, 0)
        if n == 0:
            continue
        if cmd != "a" or (idx % n) in ARC_COORD_IDX:
            coords.append((float(t), t))
        idx += 1
    return coords


def points_of(el):
    """polygon/polyline 좌표. 숫자가 아닌 토큰이 섞이면 BAD."""
    raw = (el.get("points") or "").strip()
    if not raw:
        return None
    toks = [t for t in re.split(r"[\s,]+", raw) if t]
    vals = []
    for t in toks:
        v = num(t)
        if v is BAD or v is None:
            return BAD
        vals.append(v)
    if len(vals) < 4 or len(vals) % 2:
        return BAD
    return vals


def bbox(doc, el):
    t = doc.tag(el)
    g = {k: num(el.get(k)) for k in ("x", "y", "width", "height", "cx", "cy", "r", "rx", "ry")}
    if any(v is BAD for v in g.values()):
        return None
    if t == "rect" and None not in (g["x"], g["y"], g["width"], g["height"]):
        if g["width"] <= 0 or g["height"] <= 0:
            return None
        return (g["x"], g["y"], g["width"], g["height"])
    if t == "circle" and None not in (g["cx"], g["cy"], g["r"]):
        return (g["cx"] - g["r"], g["cy"] - g["r"], 2 * g["r"], 2 * g["r"])
    if t == "ellipse" and None not in (g["cx"], g["cy"], g["rx"], g["ry"]):
        return (g["cx"] - g["rx"], g["cy"] - g["ry"], 2 * g["rx"], 2 * g["ry"])
    if t in POINT_SHAPES:
        vals = points_of(el)
        if vals not in (None, BAD):
            xs, ys = vals[0::2], vals[1::2]
            return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    return None


# ---------------------------------------------------------------- 검사
def check_grid(doc, rep):
    bad = 0
    for el in doc.iter_rendered():
        t = doc.tag(el)
        for attr in GEOM_ATTRS.get(t, ()):
            v = num(el.get(attr))
            if v is BAD:
                bad += 1
                rep.fail("4px-grid", f'{describe(doc, el)} {attr}="{el.get(attr)}" — 숫자가 아니다')
            elif v is not None and v % GRID != 0:
                bad += 1
                rep.fail("4px-grid", f'{describe(doc, el)} {attr}="{v:g}" — 4의 배수 아님')
        if t in POINT_SHAPES:
            vals = points_of(el)
            if vals is BAD:
                bad += 1
                rep.fail("4px-grid", f"{describe(doc, el)} points를 좌표쌍으로 읽을 수 없다 "
                                     "(숫자가 아니거나 개수가 홀수)")
            elif vals:
                for v in vals:
                    if v % GRID != 0:
                        bad += 1
                        rep.fail("4px-grid", f"{describe(doc, el)} points {v:g} — 4의 배수 아님")
        elif t == "path":
            for v, raw in path_numbers(el.get("d")):
                if v % GRID != 0:
                    bad += 1
                    rep.fail("4px-grid", f"{describe(doc, el)} d 좌표 {raw} — 4의 배수 아님")
    if not bad:
        rep.info("4px-grid", "모든 도형 좌표가 4의 배수")


def check_transform(doc, rep):
    hit = [el for el in doc.iter_rendered() if el.get("transform")]
    if hit:
        rep.warn("transform", f"transform이 {len(hit)}곳 — 검사는 변환 전 좌표만 본다 "
                              f"({describe(doc, hit[0])})")


def check_density(doc, rep):
    nodes = [el for el in doc.iter_rendered()
             if doc.tag(el) in NODE_SHAPES and "node" in classes(el)]
    n = len(nodes)
    if n == 0:
        rep.fail("density", 'class="node"인 노드가 없다 — 밀도·오버플로 검사가 통째로 꺼진다')
    elif n > MAX_NODES:
        rep.fail("density", f"노드 {n}개 — 최대 {MAX_NODES}. 묶거나 빼거나 쪼갠다")
    elif n > IDEAL_NODES:
        rep.warn("density", f"노드 {n}개 — 이상적 범위는 4~{IDEAL_NODES}")
    else:
        rep.info("density", f"노드 {n}개")
    return nodes


def check_focus_count(doc, rep):
    """개수는 테마와 무관하다 — 테마 루프 안에서 세면 findings가 테마 수만큼 중복된다."""
    focal = [el for el in doc.iter_rendered() if "focal" in classes(el)]
    dots = [el for el in doc.iter_rendered() if "dot" in classes(el)]
    if len(focal) > MAX_FOCAL:
        rep.fail("accent", f"focal {len(focal)}개 — 최대 {MAX_FOCAL}")
    if len(dots) > MAX_FOCAL:
        rep.fail("accent", f"시그니처 점 {len(dots)}개 — 최대 {MAX_FOCAL}")
    if not focal and not dots:
        rep.warn("accent", "초점 표시가 없다 — 강조점이 정말 없는 다이어그램인지 확인")


def check_accent(doc, rules, theme, accents, rep):
    for el in doc.iter_rendered("text"):
        fill = declared(doc, rules, el, "fill") or ""
        if uses(fill, ("accent", "accent-deep"), accents):
            rep.fail("accent", f"[{theme}] {describe(doc, el)} — 악센트를 텍스트 색으로 사용"
                               "(대비 미달). 테두리·점에만 쓴다")


def check_a11y(doc, rep):
    svg = doc.root
    if svg.get("role") != "img":
        rep.fail("a11y", '<svg>에 role="img"가 없다')
    labelled = (svg.get("aria-labelledby") or "").split()
    kids = list(svg)
    titles = [e for e in kids if doc.tag(e) == "title"]
    descs = [e for e in kids if doc.tag(e) == "desc"]
    if not titles:
        rep.fail("a11y", "<title>이 <svg>의 직계 자식으로 없다")
    elif not (titles[0].text or "").strip():
        rep.fail("a11y", "<title>이 비어 있다")
    if not descs:
        rep.fail("a11y", "<desc>가 <svg>의 직계 자식으로 없다")
    elif not ("".join(descs[0].itertext())).strip():
        rep.fail("a11y", "<desc>가 비어 있다 — 그림을 못 보는 사람에게 내용을 전달할 수단")
    ids = {e.get("id") for e in titles + descs if e.get("id")}
    if not labelled:
        rep.fail("a11y", "aria-labelledby가 없다")
    else:
        missing = [i for i in labelled if i not in ids]
        if missing:
            rep.fail("a11y", f"aria-labelledby가 존재하지 않는 id를 가리킨다: {', '.join(missing)}")


def anchor_of(doc, el):
    x, y = num(el.get("x")), num(el.get("y"))
    for sp in el.iter(doc.q("tspan")):
        if x in (None, BAD):
            x = num(sp.get("x"))
        if y in (None, BAD):
            y = num(sp.get("y"))
    if x in (None, BAD) or y in (None, BAD):
        return None
    return x, y


def text_lines(doc, el):
    spans = [s for s in el.iter(doc.q("tspan"))]
    if spans:
        return [t for t in ("".join(s.itertext()).strip() for s in spans) if t]
    s = "".join(el.itertext()).strip()
    return [s] if s else []


def span_of(anchor, x, w):
    if anchor == "start":
        return x, x + w
    if anchor == "end":
        return x - w, x
    return x - w / 2, x + w / 2


def check_overflow(doc, rules, nodes, rep):
    boxes = []
    for nd in nodes:
        bb = bbox(doc, nd)
        if bb is None:
            rep.fail("label-overflow", f"{describe(doc, nd)} — 노드 크기를 계산할 수 없다. "
                                       "오버플로 검사 불가")
        else:
            boxes.append((nd, bb))
    hit = 0
    for t in doc.iter_rendered("text"):
        if not text_lines(doc, t):
            continue
        pt = anchor_of(doc, t)
        if pt is None:
            rep.fail("label-overflow", f"{describe(doc, t)} — 기준점(x·y)을 찾을 수 없다")
            continue
        tx, ty = pt
        cands = [(bw * bh, nd, (bx, by, bw, bh)) for nd, (bx, by, bw, bh) in boxes
                 if bx <= tx <= bx + bw and by <= ty <= by + bh]
        if not cands:
            continue
        _, nd, (bx, _, bw, _) = min(cands, key=lambda c: c[0])
        size, mono = resolve_font(doc, rules, t)
        anchor = resolve_anchor(doc, rules, t)
        if size is BAD or anchor is None:
            continue
        if bw < 2 * PAD:
            rep.fail("label-overflow", f"{describe(doc, nd)} 폭 {int(bw)} — 좌우 패딩 "
                                       f"{2 * PAD}보다 좁아 라벨이 들어갈 수 없다")
            continue
        left_lim, right_lim = bx + PAD, bx + bw - PAD
        for line in text_lines(doc, t):
            w = text_width(line, size, mono)
            lo, hi = span_of(anchor, tx, w)
            over = max(left_lim - lo, hi - right_lim)
            if over > 0:
                hit += 1
                rep.fail("label-overflow",
                         f'"{line}" ({size:g}px{", mono" if mono else ""}, anchor={anchor}) '
                         f"→ [{lo:.0f}, {hi:.0f}] 이 박스 안쪽 [{left_lim:.0f}, {right_lim:.0f}]를 "
                         f"{int(over)}px 넘침. 줄이거나 2줄로")
    if not hit:
        rep.info("label-overflow", "측정된 모든 라벨이 박스 안쪽 예산 안")


CONTRAST_PAIRS = [
    ("--ink", "--paper-2", 4.5, "본문 텍스트"),
    ("--muted", "--paper-2", 4.5, "보조 텍스트"),
    ("--ink", "--paper", 4.5, "제목 텍스트"),
    ("--line-strong", "--paper", 3.0, "노드 테두리·커넥터"),
]
REQUIRED_TOKENS = sorted({t for a, b, _, _ in CONTRAST_PAIRS for t in (a, b)})


def check_contrast(tokens, theme, rep):
    if not tokens:
        rep.fail("contrast", f"[{theme}] 시맨틱 토큰을 찾지 못했다 — 토큰은 루트를 겨냥한 "
                             "셀렉터로 정의해야 검증된다(tokens.md §1)")
        return
    for fg, bg, need, label in CONTRAST_PAIRS:
        if fg not in tokens or bg not in tokens:
            rep.fail("contrast", f"[{theme}] 토큰 {fg} 또는 {bg}가 없다 — 필요: "
                                 f"{', '.join(REQUIRED_TOKENS)}")
            continue
        r = contrast(tokens[fg], tokens[bg])
        if r is None:
            continue
        if r < need:
            rep.fail("contrast", f"[{theme}] {label}: {fg} on {bg} = {r:.2f}:1 < {need}:1")
        else:
            rep.info("contrast", f"[{theme}] {label}: {r:.2f}:1 ≥ {need}:1")


def check_antipatterns(doc, rep):
    raw = ET.tostring(doc.root, encoding="unicode")
    if "linearGradient" in raw or "radialGradient" in raw:
        rep.warn("anti-pattern", "그라데이션 사용 — 배경 그라데이션 금지")
    if "drop-shadow" in raw or "feDropShadow" in raw or "feGaussianBlur" in raw:
        rep.fail("anti-pattern", "그림자/블러 사용 — 1px 헤어라인만 쓴다")
    for t in doc.iter_rendered("text"):
        s = "".join(t.itertext())
        if EMOJI.search(s):
            rep.fail("anti-pattern", f'이모지 라벨 "{s.strip()}" — PNG 렌더 시 tofu 위험')
        if not classes(t):
            rep.warn("font-role", f"{describe(doc, t)} class 없음")


def check_viewbox(doc, rep):
    vb = [p for p in re.split(r"[\s,]+", (doc.root.get("viewBox") or "").strip()) if p]
    if len(vb) != 4:
        rep.fail("canvas", "viewBox가 없거나 값이 4개가 아니다")
        return
    try:
        w, h = float(vb[2]), float(vb[3])
    except ValueError:
        rep.fail("canvas", f"viewBox 값이 숫자가 아니다: {' '.join(vb)}")
        return
    if (w, h) not in KNOWN_CANVASES:
        rep.warn("canvas", f"비표준 캔버스 {w:g}×{h:g} — geometry.md 좌표표가 맞지 않을 수 있다")


# ---------------------------------------------------------------- 추출
def _tag_end(s, start):
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


def extract_svgs(src):
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    out, i = [], 0
    open_re = re.compile(r"<svg(?=[\s>/])")
    any_re = re.compile(r"<svg(?=[\s>/])|</svg\s*>")
    while True:
        m = open_re.search(src, i)
        if not m:
            return out
        j = _tag_end(src, m.start())
        if j is None:
            return out
        if src[m.start():j + 1].rstrip().endswith("/>"):
            i = j + 1
            continue
        depth, k = 1, j + 1
        while depth > 0:
            m2 = any_re.search(src, k)
            if not m2:
                return out
            if m2.group(0).startswith("</"):
                depth -= 1
                k = m2.end()
            else:
                jj = _tag_end(src, m2.start())
                if jj is None:
                    return out
                if not src[m2.start():jj + 1].rstrip().endswith("/>"):
                    depth += 1
                k = jj + 1
        out.append(src[m.start():k])
        i = k


def check_svg(svg_text, theme_override, rep):
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as e:
        rep.fail("parse", f"SVG를 XML로 파싱할 수 없다: {e}")
        return
    doc = Doc(root)
    rules = parse_style(doc, rep)

    themes = sorted({theme_override} if theme_override else declared_themes(rules))
    rep.info("theme", f"검증할 테마: {', '.join(themes)}"
                      + ("" if doc.ns else " (xmlns 없는 인라인 SVG)"))

    check_contract(doc, rules, rep)
    check_viewbox(doc, rep)
    check_grid(doc, rep)
    check_transform(doc, rep)
    nodes = check_density(doc, rep)
    check_focus_count(doc, rep)
    check_a11y(doc, rep)
    check_overflow(doc, rules, nodes, rep)
    check_antipatterns(doc, rep)

    # 테마별 검증 — 루트 속성을 실제로 바꿔 캐스케이드가 다크 규칙을 켜게 한다.
    original = root.get("data-theme")
    for th in themes:
        root.set("data-theme", th)
        tokens = tokens_for(doc, rules)
        check_tokens_are_hex(tokens, th, rep)
        check_contrast(tokens, th, rep)
        check_accent(doc, rules, th, token_values(doc, rules, "accent"), rep)
    if original is None:
        root.attrib.pop("data-theme", None)
    else:
        root.set("data-theme", original)


def main():
    ap = argparse.ArgumentParser(description="editorial-diagram 출력 검증")
    ap.add_argument("path")
    ap.add_argument("--theme", choices=("light", "dark"))
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    try:
        src = open(a.path, encoding="utf-8").read()
    except OSError as e:
        print(f"FAIL  파일을 읽을 수 없다: {e}")
        return 1
    svgs = extract_svgs(src)
    if not svgs:
        print("FAIL  <svg> 요소를 찾지 못했다")
        return 1
    worst = "PASS"
    for i, s in enumerate(svgs, 1):
        rep = Report()
        check_svg(s, a.theme, rep)
        print(f"\n── SVG #{i} ── {rep.verdict}")
        for lv, rule, msg in rep.items:
            if a.quiet and lv == "INFO":
                continue
            print(f"  {lv:<4} [{rule}] {msg}")
        if rep.verdict == "FAIL" or (rep.verdict == "WARN" and worst == "PASS"):
            worst = rep.verdict
    print(f"\n결과: {worst}  ({len(svgs)}개 SVG)")
    return 1 if worst == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
