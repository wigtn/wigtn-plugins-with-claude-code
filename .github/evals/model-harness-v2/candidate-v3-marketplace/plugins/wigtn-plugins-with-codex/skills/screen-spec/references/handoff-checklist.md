# Handoff Checklist

`/screen-spec` 산출물이 `/implement`로 넘어가기 전 frontend-developer 에이전트가 자동 검증하는 항목.

## 1. Accessibility (a11y)

| 항목 | 통과 기준 |
|------|----------|
| Landmark | `<header>`, `<nav>`, `<main>`, `<footer>` 사용 |
| 폼 label | 모든 input에 `<label for>` 또는 `aria-label` |
| 버튼 라벨 | 아이콘만 있는 버튼은 `aria-label` 필수 |
| 색 대비 | WCAG AA 기준 (텍스트 4.5:1, 큰 텍스트 3:1) |
| 키보드 네비 | 모든 인터랙티브 요소가 Tab으로 접근 가능 |
| 포커스 표시 | `:focus-visible` 스타일 명시 |
| ARIA 상태 | loading/error 상태에 `aria-busy`, `aria-invalid` |

**FAIL 기준**: 폼 필드에 label 없음, 아이콘 버튼에 aria-label 없음.

## 2. Responsive

| 항목 | 통과 기준 |
|------|----------|
| Breakpoint 명시 | 모든 페이지에 ≥2 breakpoint 정의 (Desktop ≥1024 / Mobile <768) |
| 모바일 UX | 터치 타깃 ≥44×44px |
| 가로 스크롤 | Mobile에서 가로 스크롤 발생 X |
| 폰트 크기 | Mobile 본문 ≥14px |
| 이미지 반응형 | `max-width: 100%` 또는 srcset |

**FAIL 기준**: Mobile 분기점이 정의되지 않은 페이지 존재.
**WARN**: Desktop-only 페이지의 안내 화면 누락.

## 3. AI 냄새 / Design Smell

| 안티 | 처리 |
|------|------|
| 보랏빛 그라데이션 남발 | WARN |
| "쉽고 빠르게" 같은 클리셰 | WARN |
| 모든 버튼이 동일 색 (primary 남용) | WARN |
| 그림자 5겹 이상 | WARN |
| 이모지로 정보 전달 (텍스트 X) | FAIL |

**참고**: `plugins/wigtn-plugins/skills/design-system-reference/`의 공통 안티패턴 가이드 참조.

## 4. Microcopy Coverage

| 항목 | 통과 기준 |
|------|----------|
| 빈 상태 메시지 | §5.4.1에서 `empty: ✓`인 모든 화면에 카피 존재 |
| 에러 메시지 | §5.4.1에서 `error: ✓`인 모든 화면에 카피 존재 |
| 권한 안내 | `no-permission: ✓`인 화면에 안내 카피 + CTA |
| placeholder | 모든 input에 예시 또는 형식 안내 |
| 버튼 라벨 | 명사가 아닌 동사 ("저장하기") |

**FAIL 기준**: 체크된 상태인데 카피 없음.

## 5. Component Specification

| 항목 | 통과 기준 |
|------|----------|
| validation | 모든 required 폼 필드에 validation rule |
| 타입 명시 | input type, select options, button intent |
| 의존성 | 페이지가 사용하는 reusable component 목록 |
| 상태 전이 | 폼 status, modal open/close 등 명시 |

**FAIL 기준**: required 필드에 validation 누락.

## 6. Coverage Cross-Check

| 항목 | 통과 기준 |
|------|----------|
| FR ↔ Screen | 모든 FR이 1+ 화면에 매핑 |
| Screen ↔ FR | 모든 화면이 1+ FR과 연결 |
| Scenario ↔ Flow | 모든 Acceptance Criteria 시나리오가 1+ Flow에 매핑 |
| Page ↔ State | 모든 페이지에 1+ state 체크 |

**FAIL 기준**: 매핑되지 않은 FR/화면/시나리오가 1+ 존재.

## 7. Document Hygiene

| 항목 | 통과 기준 |
|------|----------|
| Open Questions | 화면당 ≤3개 (그 이상이면 명세가 모호) |
| TODO 마커 | `TBD`, `???`가 5개 이상이면 WARN |
| Wireframe 링크 | 모든 화면 명세에 wireframe anchor |
| Style 일관성 | 선택된 design-discovery 스타일과 일치 |

## Output Format

frontend-developer 에이전트 응답:

```yaml
result: PASS | WARN | FAIL
warn_count: 0
fail_items:
  - section: 3.4 Components
    screen: /admin
    issue: filter_dept에 validation 누락
    suggestion: "min 1 select 추가"
  - section: 5.4 Microcopy
    screen: /my
    issue: empty 상태 카피 누락
    suggestion: "'첫 {항목}을 만들어보세요' 형식의 안내 추가"
fix_strategy: regenerate_section  # 전체 재생성 vs 부분 패치
```

## 통과 기준 요약

- **PASS**: FAIL 0건 + WARN ≤3
- **WARN**: FAIL 0건 + WARN 4~7
- **FAIL**: FAIL ≥1 또는 WARN ≥8

PASS면 `/implement`로 진행. FAIL이면 해당 섹션 재생성.
