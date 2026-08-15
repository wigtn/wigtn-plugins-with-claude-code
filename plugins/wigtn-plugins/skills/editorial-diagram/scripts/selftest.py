#!/usr/bin/env python3
"""check.py 회귀 테스트 — 우회 경로마다 픽스처 1개 + 변이 테스트.

    python3 selftest.py            # 케이스만
    python3 selftest.py --mutate   # 변이 테스트까지 (느림, 각 수정을 되돌려 확인)

**케이스는 판정만이 아니라 어느 rule이 발화했는지까지 단언한다.** 판정만 보면
"기능이 동작함"과 "기능이 완전히 망가짐"이 같은 결과로 보인다 — 실제로 그래서
이전 스위트의 3케이스가 회귀를 못 잡았다.

변이 테스트: 수정 지점을 되돌렸을 때 해당 케이스가 뒤집히지 않으면 그 테스트는
아무것도 보증하지 않는다는 뜻이므로 실패로 처리한다.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
CHECK = HERE / "check.py"

GOOD = ("--paper:#FFFFFF;--paper-2:#F4F2F8;--ink:#1E1E28;--muted:#5A5A6E;"
        "--line:#E6E3EE;--line-strong:#85819B;--accent:#9B51E0;--accent-deep:#6B2EAA;")
LOW_MUTED = GOOD.replace("--muted:#5A5A6E", "--muted:#8F8DA0")   # 2.91:1 — AA 미달

BASE_RULES = (
    ".node-name{font-family:Pretendard;font-size:18px;fill:var(--ink)}"
    ".sublabel{font-family:'JetBrains Mono',monospace;font-size:13px;fill:var(--muted)}"
    ".node{fill:var(--paper-2);stroke:var(--line-strong)}"
    ".dot{fill:var(--accent)}"
)
NODE = ('<rect class="node focal" x="64" y="328" width="352" height="160" rx="8"/>'
        '<circle class="dot" cx="392" cy="352" r="8"/>')
LABEL = '<text class="node-name" x="240" y="402">주문 서비스</text>'
LONG = "가나다라마바사아자차카타파하가나다라마바사아자차카타파하"   # 28자 → 504px


def doc(body, *, tokens=GOOD, root="ed", xmlns=True, theme=None,
        rules=BASE_RULES, extra_css="", root_sel=None):
    ns = ' xmlns="http://www.w3.org/2000/svg"' if xmlns else ""
    th = f' data-theme="{theme}"' if theme else ""
    sel = root_sel or f"svg.{root}"
    css = f"{sel}{{{tokens}}}{rules}{extra_css}" if tokens is not None else rules + extra_css
    return (f'<!doctype html><body><svg class="{root}"{th} viewBox="0 0 1280 720"{ns} '
            'role="img" aria-labelledby="t d">'
            '<title id="t">T</title><desc id="d">D</desc>'
            f"<style>{css}</style>{body}</svg></body>")


# (이름, 기대판정, 기대 FAIL rule(None이면 무관), 문서)
CASES = [
    ("baseline", "PASS", None, doc(NODE + LABEL)),

    ("단위접미사_좌표", "FAIL", "4px-grid",
     doc('<rect class="node" x="65px" y="329px" width="353px" height="161px"/>' + LABEL)),

    ("xmlns없어도_오탐없음", "PASS", None, doc(NODE + LABEL, xmlns=False)),

    ("xmlns없어도_이모지_검출", "FAIL", "anti-pattern",
     doc(NODE + '<text class="node-name" x="240" y="402">DB \U0001F680</text>', xmlns=False)),

    ("tspan_앵커_합성", "FAIL", ("label-overflow", "넘침"),
     doc(NODE + f'<text class="node-name"><tspan x="240" y="402">{LONG}</tspan></text>')),

    ("text_y_tspan_x_분리", "FAIL", ("label-overflow", "넘침"),
     doc(NODE + f'<text class="node-name" y="402"><tspan x="240">{LONG}</tspan></text>')),

    ("마름모_오버플로", "FAIL", "label-overflow",
     doc('<polygon class="node" points="528,328 640,372 528,416 416,372"/>'
         '<circle class="dot" cx="612" cy="344" r="8"/>'
         f'<text class="node-name" x="528" y="376">{LONG}</text>')),

    ("g노드는_계약위반", "FAIL", "contract",
     doc('<g class="node"><rect x="64" y="328" width="352" height="160"/></g>' + LABEL)),

    ("path노드는_계약위반", "FAIL", "contract",
     doc('<path class="node" d="M64 328 H416 V488 H64 Z"/>' + LABEL)),

    ("노드없으면_실패", "FAIL", "density", doc(LABEL)),

    ("points_홀수개", "FAIL", "label-overflow",
     doc('<polygon class="node" points="64,328 416,328 416,488 64"/>' + LABEL)),

    ("media가_라이트토큰_덮기", "FAIL", "contrast",
     doc(NODE + LABEL, tokens=None,
         rules=f"svg.ed{{{LOW_MUTED}}}@media (prefers-color-scheme:dark)"
               f"{{svg.ed{{--muted:#3A3A48}}}}" + BASE_RULES)),

    ("media_문자열속_중괄호", "FAIL", "contrast",
     doc(NODE + LABEL, tokens=None,
         rules=f'svg.ed{{{LOW_MUTED}}}@media screen{{i::after{{content:"}}"}}'
               f"svg.ed{{--muted:#3A3A48}}}}" + BASE_RULES)),

    # 다크 블록은 선언만으로도 검증돼야 한다 (라이트는 정상, 다크만 저대비)
    ("다크팔레트도_검증한다", "FAIL", ("contrast", "[dark]"),
     doc(NODE + LABEL, tokens=None,
         rules=f"svg.ed{{{GOOD}}}svg.ed[data-theme=\"dark\"]{{--muted:#24242E;"
               "--paper-2:#1E1E28;--paper:#15151E;--ink:#F5F4FA;--line-strong:#6E6C84}}"
               + BASE_RULES)),

    ("따옴표없는_data-theme도_인식", "FAIL", ("contrast", "[dark]"),
     doc(NODE + LABEL, tokens=None,
         rules=f"svg.ed{{{GOOD}}}svg.ed[data-theme=dark]{{--muted:#24242E;"
               "--paper-2:#1E1E28;--paper:#15151E;--ink:#F5F4FA;--line-strong:#6E6C84}}"
               + BASE_RULES)),

    ("부분일치_속성셀렉터는_계약위반", "FAIL", "css",
     doc(NODE + LABEL, extra_css='text[data-x^=y]{fill:var(--accent)}')),

    # 중요 규칙을 BASE_RULES보다 앞에 둔다 — 뒤에 두면 문서순서만으로도 이겨서
    # "!important를 실제로 존중하는가"를 구별하지 못한다
    ("important가_특정성을_이긴다", "FAIL", "accent",
     doc(NODE + '<text class="node-name" x="240" y="402">DB</text>',
         rules="text{fill:var(--accent)!important}" + BASE_RULES)),

    ("use는_계약위반", "FAIL", "contract",
     doc('<defs><rect id="tpl" class="node" x="0" y="0" width="8" height="8"/></defs>'
         + NODE + LABEL + '<use href="#tpl" x="64" y="600"/>')),

    ("foreignObject는_계약위반", "FAIL", "contract",
     doc(NODE + LABEL + '<foreignObject x="64" y="600" width="200" height="40"/>')),

    ("g에_class주면_계약위반", "FAIL", "contract",
     doc('<g class="title">' + NODE + LABEL + "</g>")),

    ("자손이_토큰_재정의하면_계약위반", "FAIL", "contract",
     doc(NODE + LABEL, extra_css=".dim{--muted:#8F8DA0}")),

    ("인라인style_fill은_계약위반", "FAIL", "contract",
     doc(NODE + '<text class="node-name" x="240" y="402" '
                'style="fill:var(--accent)">DB</text>')),

    ("tspan_fill속성은_계약위반", "FAIL", "contract",
     doc(NODE + '<text class="node-name" x="240" y="402">'
                '<tspan fill="#9B51E0">DB</tspan></text>')),

    ("tspan_class는_계약위반", "FAIL", "contract",
     doc(NODE + '<text class="node-name" x="240" y="402">'
                '<tspan class="big">가나다</tspan></text>', extra_css=".big{font-size:40px}")),

    ("루트svg에_fill선언은_계약위반", "FAIL", "contract",
     doc(NODE + '<text class="plain" x="240" y="402">DB</text>',
         extra_css="svg{fill:var(--accent)}.plain{font-family:Pretendard;font-size:18px}")),

    ("중첩svg는_계약위반", "FAIL", "contract",
     doc(NODE + LABEL + '<svg x="800" y="600" width="100" height="40">'
                        '<rect x="0" y="0" width="8" height="8"/></svg>')),

    ("앵커기본값은_start", "FAIL", ("label-overflow", "anchor=start"),
     doc('<rect class="node" x="64" y="328" width="352" height="160" rx="8"/>'
         '<circle class="dot" cx="392" cy="352" r="8"/>'
         # .foot에는 text-anchor 선언이 없다 → SVG 기본값 start → 오른쪽으로 이탈
         f'<text class="foot" x="240" y="402">{LONG[:20]}</text>')),

    ("리터럴HEX로_악센트채우기_금지", "FAIL", "contract",
     doc(NODE + LABEL, extra_css=".focal{fill:#9B51E0}")),

    ("리터럴HEX_line테두리_금지", "FAIL", "contract",
     doc(NODE + LABEL, extra_css=".node{stroke:#E6E3EE}")),

    ("결합자셀렉터가_stroke만_선언해도_계약위반", "FAIL", "css",
     doc(NODE + LABEL, extra_css="svg .node{stroke:var(--line)}")),

    ("ry도_4의배수집합만", "FAIL", "contract",
     doc('<rect class="node focal" x="64" y="328" width="352" height="160" rx="8" ry="20"/>'
         '<circle class="dot" cx="392" cy="352" r="8"/>' + LABEL)),

    ("음수폭_노드는_검사불가", "FAIL", "label-overflow",
     doc('<rect class="node" x="416" y="328" width="-352" height="160"/>'
         '<circle class="dot" cx="392" cy="352" r="8"/>' + LABEL)),

    ("패딩보다_좁은노드", "FAIL", ("label-overflow", "좁아"),
     doc('<rect class="node" x="64" y="328" width="32" height="32"/>'
         '<circle class="dot" cx="392" cy="352" r="8"/>'
         '<text class="node-name" x="80" y="344">A</text>')),

    ("콤마셀렉터는_지원한다", "FAIL", "accent",
     doc(NODE + '<text class="node-name hot" x="240" y="402">DB</text>',
         extra_css=".zzz,.hot{fill:var(--accent)}")),

    ("end앵커_왼쪽이탈", "FAIL", ("label-overflow", "anchor=end"),
     doc(NODE + '<text class="node-name end" x="100" y="402">가나다라마바사아자차카타</text>',
         extra_css=".end{text-anchor:end}")),

    ("a11y_role누락", "FAIL", "a11y",
     doc(NODE + LABEL).replace(' role="img"', "", 1)),

    ("a11y_desc비어있음", "FAIL", "a11y",
     doc(NODE + LABEL).replace("<desc id=\"d\">D</desc>", '<desc id="d"></desc>', 1)),

    ("viewBox_누락", "FAIL", "canvas",
     doc(NODE + LABEL).replace(' viewBox="0 0 1280 720"', "", 1)),

    ("노드_10개면_초과", "FAIL", "density",
     doc("".join(f'<rect class="node" x="{64 + i * 4}" y="600" width="8" height="8"/>'
                 for i in range(10)) + NODE + LABEL)),

    # 박스 [64,416], anchor=start, x=240 → 오른쪽 한계는 PAD=20이면 396, PAD=0이면 416.
    # 9자 × 18px = 162px → [240,402]: PAD=20에서만 넘친다. 경계값을 실제로 고정한다.
    ("패딩경계_20px_지킨다", "FAIL", ("label-overflow", "넘침"),
     doc('<rect class="node" x="64" y="328" width="352" height="160"/>'
         '<circle class="dot" cx="392" cy="352" r="8"/>'
         f'<text class="node-name" x="240" y="402">{LONG[:9]}</text>')),

    ("rx는_4의배수집합만", "FAIL", "contract",
     doc('<rect class="node focal" x="64" y="328" width="352" height="160" rx="12"/>'
         '<circle class="dot" cx="392" cy="352" r="8"/>' + LABEL)),

    ("초점을_악센트로_채우면_계약위반", "FAIL", "contract",
     doc(NODE + LABEL, extra_css=".focal{fill:var(--accent)}")),

    ("노드테두리에_line은_계약위반", "FAIL", "contract",
     doc(NODE + LABEL, extra_css=".node{stroke:var(--line)}")),

    ("루트클래스_변경해도_검증", "FAIL", "contrast",
     doc(NODE + LABEL, root="diag", tokens=LOW_MUTED, root_sel="svg.diag")),

    ("rgb_퍼센트는_계약위반", "FAIL", "contract",
     doc(NODE + LABEL, tokens=GOOD.replace("--muted:#5A5A6E", "--muted:rgb(60% 58% 59%)"))),

    ("color_mix는_계약위반", "FAIL", "contract",
     doc(NODE + LABEL,
         tokens=GOOD.replace("--paper-2:#F4F2F8", "--paper-2:color-mix(in srgb,#000 5%,#fff)"))),

    ("토큰없으면_실패", "FAIL", "contrast", doc(NODE + LABEL, tokens=None)),

    ("CSS악센트_텍스트색", "FAIL", "accent",
     doc(NODE + '<text class="node-name hot" x="240" y="402">DB</text>',
         extra_css=".hot{fill:var(--accent)}")),

    # .foot에는 경쟁하는 fill 규칙이 없다 — 그래야 type 셀렉터가 실제로 적용된다
    # (.node-name{fill:var(--ink)}은 특정성 0,1,0으로 text{...} 0,0,1을 이긴다)
    ("type셀렉터_악센트", "FAIL", "accent",
     doc(NODE + LABEL + '<text class="foot" x="240" y="600">src</text>',
         extra_css="text{fill:var(--accent)}")),

    ("id셀렉터_악센트", "FAIL", "accent",
     doc(NODE + '<text class="node-name" id="lbl" x="240" y="402">DB</text>',
         extra_css="#lbl{fill:var(--accent)}")),

    ("특정성_높은쪽이_이긴다", "FAIL", "accent",
     doc(NODE + '<text class="node-name hot" x="240" y="402">DB</text>',
         extra_css=".node-name.hot{fill:var(--accent)}.node-name{fill:var(--ink)}")),

    ("text_fill속성은_계약위반", "FAIL", "contract",
     doc(NODE + '<text class="node-name" x="240" y="402" fill="#1E1E28">DB</text>')),

    ("pt폰트는_계약위반", "FAIL", "contract",
     doc(NODE + f'<text class="node-name" x="240" y="402">{LONG[:15]}</text>',
         extra_css=".node-name{font-size:24pt}")),

    ("인라인style_폰트_반영", "FAIL", "label-overflow",
     doc(NODE + f'<text class="node-name" x="240" y="402" style="font-size:32px">'
                f"{LONG[:15]}</text>")),

    ("결합자셀렉터는_계약위반", "FAIL", "css",
     doc(NODE + LABEL, extra_css="svg .node-name{fill:var(--accent)}")),

    ("defs템플릿은_카운트제외", "PASS", None,
     doc('<defs><rect class="node focal" x="0" y="0" width="8" height="8"/>'
         '<circle class="dot" cx="4" cy="4" r="4"/>'
         '<rect class="node focal" x="0" y="0" width="8" height="8"/>'
         '<circle class="dot" cx="4" cy="4" r="4"/>'
         '<rect class="node" x="0" y="0" width="8" height="8"/></defs>' + NODE + LABEL)),

    ("arc플래그_오탐없음", "PASS", None,
     doc(NODE + LABEL + '<path class="link" d="M416 408 H440 A8 8 0 0 1 448 416 V480"/>')),

    ("체크표시는_이모지_아님", "PASS", None,
     doc(NODE + '<text class="node-name" x="240" y="402">완료 ✓ 실패 ✗</text>')),

    ("자기닫힘_아이콘svg_건너뜀", "PASS", None,
     '<!doctype html><body><svg class="icon" viewBox="0 0 16 16"/>'
     + doc(NODE + LABEL).split("<body>")[1]),
]

# 변이: (설명, check.py 원문, 치환문, 뒤집혀야 하는 케이스 이름들)
MUTATIONS = [
    ("단위접미사 fail-closed 제거", "    except (TypeError, ValueError):\n        return BAD",
     "    except (TypeError, ValueError):\n        return None", ["단위접미사_좌표"]),
    ("defs 제외 제거",
     'NON_RENDERED = ("defs", "marker", "symbol", "pattern", "clipPath", "mask")',
     "NON_RENDERED = ()", ["defs템플릿은_카운트제외"]),
    ("at-rule 제거 무력화", "    out, i, removed = [], 0, 0",
     "    return css, 0\n    out, i, removed = [], 0, 0",
     ["media가_라이트토큰_덮기", "media_문자열속_중괄호"]),
    ("HEX 전용 계약 해제", "    m = HEX_RE.match(str(v).strip())\n    if not m:\n        return None",
     "    m = HEX_RE.match(str(v).strip())\n    if not m:\n        return (0.5, 0.5, 0.5)",
     ["rgb_퍼센트는_계약위반", "color_mix는_계약위반"]),
    ("tspan 앵커 합성 제거",
     "    for sp in el.iter(doc.q(\"tspan\")):\n        if x in (None, BAD):\n"
     "            x = num(sp.get(\"x\"))\n        if y in (None, BAD):\n"
     "            y = num(sp.get(\"y\"))",
     "    pass", ["tspan_앵커_합성", "text_y_tspan_x_분리"]),
    ("arc 플래그 제외 해제", "ARC_COORD_IDX = {5, 6}", "ARC_COORD_IDX = {0,1,2,3,4,5,6}",
     ["arc플래그_오탐없음"]),
    ("특정성 무시(문서순서만)", "        key = (prop in imps, sel.spec, order)",
     "        key = (0, 0, order)", ["특정성_높은쪽이_이긴다", "important가_특정성을_이긴다"]),
    ("a11y 검사 무력화", "def check_a11y(doc, rep):\n    svg = doc.root",
     "def check_a11y(doc, rep):\n    return\n    svg = doc.root",
     ["a11y_role누락", "a11y_desc비어있음"]),
    ("viewBox 검사 무력화",
     "def check_viewbox(doc, rep):\n    vb =", "def check_viewbox(doc, rep):\n    return\n    vb =",
     ["viewBox_누락"]),
    ("밀도 상한 해제", "MAX_NODES = 9", "MAX_NODES = 99999", ["노드_10개면_초과"]),
    ("패딩 예산 제거", "PAD = 20  ", "PAD = 0  ", ["패딩경계_20px_지킨다"]),
    # (구 "다크 테마 발견 무력화" 변이는 제거했다 — declared_themes를 끄면 토큰 재정의
    #  검사가 먼저 contract로 FAIL해서, 대비가 검증된다는 명제를 증명하지 못하고 뒤집힌 것처럼
    #  보였다. 대신 "다크 대비 평가를 라이트로 고정" 변이가 그 명제를 직접 겨냥한다.)
    # (속성 "값" 비교 변이는 넣지 않는다 — 자기일관된 다크 팔레트에서는 값 비교를
    #  무시해도 다크가 전역 적용될 뿐 판정이 바뀌지 않아, 구별 불가능한 변이가 된다.
    #  속성 파싱 자체는 위 두 케이스와 "다크 테마 발견 무력화" 변이가 덮는다.)
    ("요소 화이트리스트 해제", "        if t not in ALLOWED_ELEMENTS:",
     "        if False:", ["use는_계약위반", "foreignObject는_계약위반"]),
    ("tspan/g class 금지 해제", '        if t in ("g", "tspan") and (classes(el) or el.get("style")):',
     "        if False:", ["g에_class주면_계약위반", "tspan_class는_계약위반"]),
    ("루트 상속 속성 금지 해제", "            watched = sorted(k for k in decls if k in INHERITED_PROPS)",
     "            watched = []", ["루트svg에_fill선언은_계약위반"]),
    ("중첩 svg 허용", '        if t == "svg" and el is not doc.root:',
     "        if False:", ["중첩svg는_계약위반"]),
    ("rx/ry 집합 해제", '            for a in ("rx", "ry"):', "            for a in ():",
     ["rx는_4의배수집합만", "ry도_4의배수집합만"]),
    ("리터럴 값 비교 해제", "    rgb = hex_rgb(value)\n    return rgb is not None and rgb in values",
     "    return False", ["리터럴HEX로_악센트채우기_금지", "리터럴HEX_line테두리_금지"]),
    ("stroke 감시 해제",
     'CHECKED_PROPS = ("fill", "stroke", "font-size", "font-family", "text-anchor")',
     'CHECKED_PROPS = ("fill", "font-size", "font-family", "text-anchor")',
     ["결합자셀렉터가_stroke만_선언해도_계약위반"]),
    ("음수 크기 허용", '        if g["width"] <= 0 or g["height"] <= 0:\n            return None',
     "        pass", ["음수폭_노드는_검사불가"]),
    ("좁은 노드 분기 제거", "        if bw < 2 * PAD:", "        if False:", ["패딩보다_좁은노드"]),
    ("콤마 분해 제거", '        for part in raw.split(","):', "        for part in [raw]:",
     ["콤마셀렉터는_지원한다"]),
    ("앵커 기본값 middle로 되돌림", '"text-anchor") or "start")', '"text-anchor") or "middle")',
     ["앵커기본값은_start"]),
    ("다크 대비 평가를 라이트로 고정", "    for th in themes:\n        root.set",
     '    for th in ["light"]:\n        root.set',
     ["다크팔레트도_검증한다", "따옴표없는_data-theme도_인식"]),
    ("text-anchor 해석 무시", '    v = (inline_prop(el, "text-anchor") or declared',
     '    v = ("start" if False else "middle") or (inline_prop(el, "text-anchor") or declared',
     ["end앵커_왼쪽이탈"]),
]


def run(text):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(text)
        path = f.name
    try:
        out = subprocess.run([sys.executable, str(CHECK), path, "--quiet"],
                             capture_output=True, text=True).stdout
        verdict = ("FAIL" if "결과: FAIL" in out else
                   "WARN" if "결과: WARN" in out else
                   "PASS" if "결과: PASS" in out else "?")
        fails = set(re.findall(r"FAIL \[([-\w]+)\]", out))
        return verdict, fails, out
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def run_cases(verbose=True):
    bad = []
    for name, want, rule, text in CASES:
        got, fails, out = run(text)
        ok = (got == want) or (want == "PASS" and got == "WARN")
        if ok and rule:
            want_rule, want_msg = rule if isinstance(rule, tuple) else (rule, None)
            ok = want_rule in fails
            if ok and want_msg:
                ok = any(want_msg in ln for ln in out.splitlines()
                         if f"FAIL [{want_rule}]" in ln)
        if verbose:
            extra = f" rules={sorted(fails)}" if not ok else ""
            label = rule[0] if isinstance(rule, tuple) else rule
            print(f"  {'ok  ' if ok else 'FAIL'}  {name:<30} 기대={want}"
                  f"{'/' + label if label else '':<18} 실제={got}{extra}")
            if not ok:
                for line in out.strip().splitlines()[1:5]:
                    print(f"          {line}")
        if not ok:
            bad.append(name)
    return bad


def run_mutations():
    """수정을 되돌렸을 때 케이스가 뒤집히지 않으면 그 테스트는 무의미하다."""
    src = CHECK.read_text(encoding="utf-8")
    bak = CHECK.with_suffix(".py.bak")
    shutil.copy(CHECK, bak)
    bad = []
    try:
        for desc, old, new, targets in MUTATIONS:
            if old not in src:
                print(f"  FAIL  변이 '{desc}' — 대상 코드를 찾지 못했다(테스트가 낡음)")
                bad.append(desc)
                continue
            CHECK.write_text(src.replace(old, new, 1), encoding="utf-8")
            broke = run_cases(verbose=False)
            missed = [t for t in targets if t not in broke]
            mark = "ok  " if not missed else "FAIL"
            print(f"  {mark}  변이: {desc:<28} 뒤집힘={len(targets) - len(missed)}/{len(targets)}")
            if missed:
                print(f"          뒤집히지 않은 케이스(무의미): {', '.join(missed)}")
                bad.append(desc)
    finally:
        shutil.move(str(bak), str(CHECK))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutate", action="store_true", help="변이 테스트까지 실행")
    a = ap.parse_args()

    print("케이스")
    bad = run_cases()
    print(f"\n  {len(CASES) - len(bad)}/{len(CASES)} 통과")

    mbad = []
    if a.mutate:
        print("\n변이 테스트 (수정을 되돌리면 뒤집혀야 한다)")
        mbad = run_mutations()
        print(f"\n  {len(MUTATIONS) - len(mbad)}/{len(MUTATIONS)} 유효")

    return 1 if bad or mbad else 0


if __name__ == "__main__":
    sys.exit(main())
