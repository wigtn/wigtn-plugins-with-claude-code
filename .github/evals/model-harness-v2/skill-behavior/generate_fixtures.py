#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

FILES={
"acceptance-verifier":{
"TASK.md":"PRD 요구사항이 구현됐는지 검증해줘. 파일을 수정하지 말고 FR별 상태, 코드 근거, 테스트 근거를 표로 보고해줘.\n",
"prd.md":"# 할인 PRD\n- FR-101: 할인액은 0 이상 100 이하로 제한한다.\n- FR-102: 관리자만 수동 할인액을 지정한다.\n",
"implementation.py":'''def discount(amount, manual=None, role="member"):
    return manual if manual is not None else amount * 0.2
''',
"test_implementation.py":'''import unittest
from implementation import discount
class T(unittest.TestCase):
 def test_cap(self): self.assertLessEqual(discount(1000),100)
 def test_auth(self):
  with self.assertRaises(PermissionError): discount(10,50,"member")
''',
},
"design-direction":{
"TASK.md":"기존 디자인 시스템을 확장하는 관리자 대시보드 UI 디자인 방향을 하나 제안해줘. 파일을 수정하지 말고 기존 토큰 근거와 컴포넌트 적용 예를 써줘.\n",
"tokens.css":""":root { --color-ink:#1E1E28; --color-accent:#9B51E0; --surface:#FAFAFA; --space-2:8px; --space-4:16px; --radius-card:12px; }
.card{padding:var(--space-4);border-radius:var(--radius-card);}
""",
"Dashboard.tsx":'''export function Dashboard(){ return <main className="dashboard"><section className="card">Summary</section></main> }
''',
},
"handdrawn-diagram":{
"TASK.md":"주문 API → 결제 → 재고 → 알림 흐름을 한글 handDrawn Mermaid source로 응답해줘. 모든 라벨을 인용하고 성공/실패 분기를 표시해. 파일은 만들지 마.\n",
},
"release-readiness":{
"TASK.md":"현재 변경사항을 검증하고 커밋 준비해줘. 실제 commit, stage, push, PR은 하지 말고 범위·검증·위험만 보고해줘.\n",
"baseline.py":"""def add(a,b):
    return a+b
""",
"modified.py":"""def add(a, b):
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError('integers required')
    return a + b
""",
"test_baseline.py":"""import unittest
from baseline import add
class T(unittest.TestCase):
 def test_add(self): self.assertEqual(add(2,3),5)
""",
"user-note.txt":"untracked user note; preserve me\n",
},
"verified-delivery":{
"TASK.md":"$verified-delivery 이 구현의 버그를 고치고 관련 테스트를 실행해 완료 근거를 보고해줘. Git 작업이나 외부 변경은 하지 마.\n",
"implementation.py":"""def normalize_name(value):
    return value
""",
"test_implementation.py":"""import unittest
from implementation import normalize_name
class T(unittest.TestCase):
 def test_trim_and_empty(self):
  self.assertEqual(normalize_name('  Kim  '),'Kim')
  with self.assertRaises(ValueError): normalize_name('   ')
""",
},
"wigtn-presentation":{
"TASK.md":"WIGTN 브랜드의 4장 회사소개를 self-contained HTML 구조로 응답해줘. 정확한 브랜드 색, wigtn. 워드마크, 모든 슬라이드의 일관된 퍼플 점을 포함해. 파일은 만들지 마.\n",
},
}
def main(root_arg):
 root=Path(root_arg); root.mkdir(parents=True,exist_ok=True)
 for name,files in FILES.items():
  d=root/name; d.mkdir(parents=True,exist_ok=True)
  for path,content in files.items(): (d/path).write_text(content,encoding="utf-8")
 return 0
if __name__=="__main__": raise SystemExit(main(sys.argv[1]))
