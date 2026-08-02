# Screen Specifications — {feature-name}

> **Generated from**: docs/prd/PRD_{feature-name}.md
> **Created**: {YYYY-MM-DD}

## Convention

각 화면은 다음 7개 슬롯을 모두 채운다:

1. **Meta**: Audience / Auth / Linked FRs / Layout / Responsive
2. **States**: §5.4.1에서 체크된 상태마다 1줄 이상
3. **Components**: 폼 필드/버튼/리스트 등 모든 UI 슬롯
4. **Microcopy**: 진입 안내, 버튼 라벨, 에러 메시지, 빈 상태 메시지
5. **Responsive**: 분기점별 레이아웃 변화
6. **Wireframe Anchor**: 04-WIREFRAME.html의 anchor
7. **Open Questions** (선택): 명세 진입 시 결정되지 않은 항목

> `--interview` 플래그로 수집된 결정사항(네비 패턴 / 밀도 / 에러 톤 / 빈 상태 철학 / 전환 방식 / 모바일 우선순위 / 핵심 후크)이 있다면 각 화면 명세 작성 시 명시적으로 반영한다.

---

## Screen: {route-1}

| 항목 | 값 |
|---|---|
| Audience | {role-1} |
| Auth | {Required 또는 Optional} ({인증 방식}) |
| Linked FRs | {FR-001, FR-002, ...} |
| Layout | {레이아웃 요약, max-width 등} |
| Responsive | {Desktop / Tablet / Mobile 분기} |

### States

PRD §5.4.1에서 체크된 항목만 1줄 이상 명세:
- [x] loading: {구체적 처리 — 스피너/스켈레톤}
- [ ] empty: N/A 또는 {CTA 포함 안내}
- [x] error: {inline 또는 배너, 메시지 톤}
- [x] success: {전환 또는 토스트}
- [ ] no-permission: N/A 또는 {안내 + 리다이렉트}

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| {field-1} | {input/select/textarea/...} | Yes/No | {검증 규칙} | {라벨 또는 placeholder} |
| {field-2} | ... | ... | ... | ... |
| submit | button | Yes | - | "{동사형 라벨}" |

### Microcopy

- 진입 안내: "{1~2줄 안내. 소요 시간/임시저장 가능 여부 등}"
- 에러 메시지: "{사용자 언어로, 코드 노출 금지}"
- 빈 상태: "{다음 행동 유도 + CTA}"

### Responsive

- Desktop (≥1024px): {레이아웃 변화}
- Tablet (768~1023): {접힘/숨김 처리}
- Mobile (<768): {1열 / 모달 / floating button}

### Wireframe Anchor

→ `04-WIREFRAME.html#screen-{slug-1}`

### Open Questions

- [ ] {결정 보류 항목}

---

## Screen: {route-2}

| 항목 | 값 |
|---|---|
| Audience | {role-1} |
| Auth | {Required 또는 Optional} |
| Linked FRs | {FR-003, ...} |
| Layout | {레이아웃 요약} |
| Responsive | {분기} |

### States

- [x] loading: {처리}
- [x] empty: {CTA + 안내}
- [x] error: {처리}
- [x] success: {처리}

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| {필터 또는 액션} | {type} | No | - | "{라벨}" |

### Microcopy

- 헤드라인: "{화면 제목}"
- 빈 상태: "{첫 사용 시 안내 + CTA}"

### Responsive

- Desktop: {표 형식}
- Mobile: {카드 그리드}

### Wireframe Anchor

→ `04-WIREFRAME.html#screen-{slug-2}`

---

## Screen: {route-3} (관리/제한 화면 예시)

| 항목 | 값 |
|---|---|
| Audience | {role-2} |
| Auth | Required + {role 검증} |
| Linked FRs | {FR-...} |
| Layout | {Filter bar + Table + Action bar} |
| Responsive | **Desktop only** 또는 모바일 별도 처리 |

### States

- [x] no-permission: {role 아님 → / 리다이렉트 + 토스트}
- [x] success: {필터/페이지네이션 테이블}

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| filter | multi-select | No | - | "{필터 라벨}" |
| export_btn | button | - | - | "내보내기" |

### Microcopy

- 권한 안내: "{role}만 접근할 수 있습니다. 권한 요청은 {담당자/팀}에게 문의하세요."

### Responsive

- Desktop (≥1280px): 전체 표시
- Mobile (<768): "PC에서 접속하세요" 안내 또는 별도 화면

### Wireframe Anchor

→ `04-WIREFRAME.html#screen-{slug-3}`
