# Screen Specifications — internal-document-sharing (사내 문서 공유 서비스)

> **Generated from**: input-prd.md (§2.3 Roles, §5.4 Pages, §5.4.1 Page State Matrix, §5.5 User Flow)
> **Created**: 2026-07-26
> **Mode**: 추론 모드 (`--interview` 미사용) — 네비게이션 top, 밀도 compact(문서 목록/관리 테이블), 에러 톤 공식적, 전환 방식 page(공유 링크 생성만 modal)

## Convention

각 화면은 다음 7개 슬롯을 모두 채운다:

1. **Meta**: Audience / Auth / Linked FRs / Layout / Responsive
2. **States**: §5.4.1에서 체크된 상태마다 1줄 이상
3. **Components**: 폼 필드/버튼/리스트 등 모든 UI 슬롯
4. **Microcopy**: 진입 안내, 버튼 라벨, 에러 메시지, 빈 상태 메시지
5. **Responsive**: 분기점별 레이아웃 변화
6. **Wireframe Anchor**: 04-WIREFRAME.html(인덱스) → 04-wireframes/ 분할 파일의 anchor
7. **Open Questions** (선택)

> 페이지 7개(≥6)로 와이어프레임은 `04-wireframes/<slug>.html` 분할, `04-WIREFRAME.html`은 인덱스.

---

## Screen: /login

| 항목 | 값 |
|---|---|
| Audience | guest |
| Auth | Optional (사내 이메일 도메인 화이트리스트 + Magic Link) |
| Linked FRs | FR-001 |
| Layout | 중앙 정렬 단일 카드 (max-w-md), 로고 + 이메일 폼 |
| Responsive | Desktop / Mobile (동일 카드, 폭만 축소) |

### States

- [x] loading: "로그인 링크 보내기" 클릭 시 버튼 스피너 + 비활성화 (중복 발송 방지)
- [ ] empty: N/A
- [x] error: 이메일 형식 오류(400 INVALID_EMAIL)는 필드 하단 inline, 429(5분 3회 초과)는 상단 배너 "요청이 너무 잦습니다. 5분 후 다시 시도하세요."
- [x] success: "로그인 링크를 이메일로 보냈습니다. 받은 편지함을 확인하세요." 확인 화면으로 전환 (계정 존재 여부와 무관하게 동일 문구 — 계정 열거 방지)
- [x] no-permission: 허용 도메인 외 이메일(403 DOMAIN_NOT_ALLOWED) → "사내 이메일 계정으로만 로그인할 수 있습니다." amber 안내 배너
- (부가) Magic Link 검증 실패: 400 INVALID_TOKEN / 410 TOKEN_EXPIRED(15분 초과) → "링크가 만료되었습니다. 다시 요청해 주세요." + 재요청 버튼

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| email | input[type=email] | Yes | 이메일 형식(RFC 5322 수준), 공백 trim | "회사 이메일" / placeholder "name@company.com" |
| submit | button | Yes | - | "로그인 링크 보내기" |
| resend | button (성공 화면) | No | 429 정책(5분 3회) 준수 | "다시 보내기" |

### Microcopy

- 진입 안내: "사내 이메일로 로그인 링크를 보내드립니다. 비밀번호는 필요 없습니다."
- 에러 메시지: "이메일 형식을 확인해 주세요." (코드·스택 노출 금지)
- no-permission: "사내 이메일 계정으로만 로그인할 수 있습니다."

### Responsive

- Desktop (≥1024px): 중앙 카드 max-w-md, 상하 여백 충분
- Tablet (768~1023): 동일 카드 유지
- Mobile (<768): 카드 폭 100% (좌우 16px 패딩), 1열

### Wireframe Anchor

→ `04-wireframes/login.html#screen-login`

---

## Screen: / (문서 목록)

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키 — 미인증 시 /login 리다이렉트) |
| Linked FRs | FR-003 |
| Layout | Top nav + 필터 바(검색·업로더·기간) + 문서 테이블 + "더 보기"(커서 페이지네이션 20건) |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 초기 진입 시 테이블 스켈레톤 5행, 추가 로드 시 하단 스피너
- [x] empty: "아직 업로드된 문서가 없습니다." + [문서 업로드] CTA. 필터 결과 0건은 "조건에 맞는 문서가 없습니다." + [필터 초기화]
- [x] error: 목록 조회 실패 시 상단 배너 "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요." + [다시 시도]. 400 INVALID_QUERY는 해당 필터 inline 안내
- [x] success: 문서 테이블 렌더 (파일명·업로더·크기·업로드일·공유 링크 수·열람 수), 본인 문서에 "나의 문서" 배지
- [ ] no-permission: N/A (미인증은 /login 리다이렉트로 처리)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| q | input[type=search] | No | 파일명 부분일치, 최대 100자 | placeholder "파일명 검색" |
| uploaderId | select (member 목록) | No | - | "업로더 전체" |
| from / to | date range picker | No | ISO date, from ≤ to | "업로드 기간" |
| doc_row | table row / card | - | - | 클릭 → `/docs/{id}` 이동 |
| upload_btn | button (primary) | Yes | - | "문서 업로드" |
| load_more | button | No | nextCursor 존재 시만 노출 | "더 보기" |

### Microcopy

- 헤드라인: "문서 목록"
- 빈 상태: "아직 업로드된 문서가 없습니다. 첫 문서를 업로드해 보세요."
- 에러: "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."

### Responsive

- Desktop (≥1024px): 6열 테이블 (파일명 / 업로더 / 크기 / 업로드일 / 링크 수 / 열람 수)
- Tablet (768~1023): 링크 수·열람 수 열 접힘 (행 확장으로 확인)
- Mobile (<768): 카드 리스트 1열 (파일명 + 업로더·날짜 메타), 필터는 상단 접이식 패널

### Wireframe Anchor

→ `04-wireframes/home.html#screen-home`

---

## Screen: /upload

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키) |
| Linked FRs | FR-002, FR-013 |
| Layout | 중앙 카드 (max-w-lg): 드래그&드롭 존 + 제목 입력 + 업로드 버튼 + 진행률 바 |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 업로드 중 진행률 바(%) + "업로드 중…" — 완료 전 버튼 비활성. 업로드 완료 후 스캔 대기 시 "검사 중" 배지 (FR-013: 스캔 완료 전 공유 링크 생성 차단 안내)
- [ ] empty: N/A
- [x] error: 400 INVALID_FILE_TYPE → "PDF 또는 DOCX 파일만 업로드할 수 있습니다." / 413 FILE_TOO_LARGE → "파일이 50MB를 초과합니다." / 507 QUOTA_EXCEEDED → "저장 용량(5GB)을 초과했습니다. 기존 문서를 정리해 주세요." — 모두 드롭존 하단 inline (red)
- [x] success: 201 응답 → `/docs/{id}` 상세로 즉시 이동 + "문서가 업로드되었습니다" 토스트
- [ ] no-permission: N/A (미인증은 /login 리다이렉트)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| file | file dropzone (input[type=file]) | Yes | 확장자 .pdf/.docx + 클라이언트 MIME 사전 검사(최종 판정은 서버 매직 넘버), ≤50MB | "PDF 또는 DOCX 파일을 끌어다 놓거나 클릭해 선택하세요 (최대 50MB)" |
| title | input[type=text] | No | ≤200자, 미입력 시 파일명 사용 | "문서 제목 (선택 — 비우면 파일명 사용)" |
| submit | button (primary) | Yes | 파일 선택 전 비활성 | "업로드" |
| cancel | button | No | 업로드 중에만 노출 | "취소" |

### Microcopy

- 진입 안내: "PDF 또는 DOCX 문서를 업로드하세요. 업로드 후 공유 링크를 만들 수 있습니다."
- 에러 메시지: "PDF 또는 DOCX 파일만 업로드할 수 있습니다." (서버 코드 미노출)
- 스캔 안내: "보안 검사 중입니다. 검사가 끝나면 공유 링크를 만들 수 있습니다."

### Responsive

- Desktop (≥1024px): 중앙 카드 max-w-lg, 드롭존 높이 240px
- Tablet (768~1023): 동일
- Mobile (<768): 드롭존 대신 파일 선택 버튼 중심 UI (터치), 1열

### Wireframe Anchor

→ `04-wireframes/upload.html#screen-upload`

---

## Screen: /docs/{id} (문서 상세)

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키 + 서버 측 소유자 검사) |
| Linked FRs | FR-004, FR-005, FR-008 (+ FR-007 링크 폐기, FR-012 공유 옵션) |
| Layout | 2열 — 좌: 문서 메타(제목·파일명·크기·업로더·업로드일·열람 수·scanStatus) + 다운로드, 우: 공유 링크 목록 패널(소유자/admin만) |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 메타 영역 스켈레톤 + 공유 링크 패널 스켈레톤
- [ ] empty: N/A (공유 링크 0건은 패널 내 안내 "아직 공유 링크가 없습니다." + [공유 링크 만들기])
- [x] error: 404 DOCUMENT_NOT_FOUND → "문서를 찾을 수 없습니다. 삭제되었거나 주소가 잘못되었습니다." 전체 화면 안내. 관리자 강제 삭제 문서는 업로더에게 "관리자에 의해 삭제됨" 상태 표시(FR-009). 409 SCAN_IN_PROGRESS(다운로드/공유 시) → "보안 검사 중입니다." / 423 DOCUMENT_QUARANTINED → "보안 문제로 격리된 문서입니다."
- [x] success: 메타 + 공유 링크 목록 렌더. 링크 생성 성공 시 URL 1회 노출 모달 + "복사되었습니다" 토스트. 링크 폐기 성공 시 "공유 링크가 폐기되었습니다" 토스트. 문서 삭제 성공 시 `/` 이동 + "문서가 삭제되고 링크 N개가 무효화되었습니다" 토스트
- [x] no-permission: 타인 문서에서는 삭제·공유 버튼 미노출(§5.4.1). API 직접 호출 403 FORBIDDEN 시 "본인이 업로드한 문서만 관리할 수 있습니다." amber 배너

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| download_btn | button | Yes | scanStatus=clean일 때만 활성 | "원본 다운로드" |
| share_create_btn | button (primary, 소유자/admin만) | No | scanStatus=clean일 때만 활성 | "공유 링크 만들기" |
| expiresInDays | select (모달 내) | Yes | 1~90, 기본 7 | "만료 기간 (기본 7일, 최대 90일)" |
| password | input[type=password] (모달 내) | No | 설정 시 8자 이상 | "열람 비밀번호 (선택, 8자 이상)" |
| maxViews | input[type=number] (모달 내) | No | ≥1 정수 | "최대 열람 횟수 (선택, 비우면 무제한)" |
| copy_url_btn | button (생성 결과) | Yes | - | "링크 복사" |
| share_link_row | list row (URL 마스킹·만료일·열람 수·비밀번호 여부) | - | - | 폐기 버튼 "폐기" + 확인 다이얼로그 |
| delete_btn | button (danger, 소유자/admin만) | No | 확인 다이얼로그 필수 | "문서 삭제" |

### Microcopy

- 진입 안내: (헤더) 문서 제목 + "업로드한 문서의 정보를 확인하고 외부 공유 링크를 관리합니다."
- 링크 생성 결과: "이 링크는 지금 한 번만 표시됩니다. 복사해 두세요."
- 삭제 확인: "이 문서를 삭제하면 발급된 공유 링크 N개가 모두 즉시 무효화됩니다. 삭제하시겠습니까?"
- 에러: "문서를 찾을 수 없습니다. 삭제되었거나 주소가 잘못되었습니다."

### Responsive

- Desktop (≥1024px): 2열 (좌 메타 2/3 + 우 공유 링크 패널 1/3)
- Tablet (768~1023): 2열 유지, 패널 폭 축소
- Mobile (<768): 1열 — 메타 → 액션 버튼 → 공유 링크 목록 순 세로 배치

### Wireframe Anchor

→ `04-wireframes/docs-id.html#screen-docs-id`

---

## Screen: /s/{token} (공유 열람)

| 항목 | 값 |
|---|---|
| Audience | guest, member, admin |
| Auth | None — 토큰이 유일한 자격 (PRD §4.5: noindex, no-referrer, IP 레이트 리밋) |
| Linked FRs | FR-006, FR-007, FR-012, FR-014 |
| Layout | 네비게이션 없는 단독 뷰어 — 상단 얇은 바(문서 제목·다운로드 버튼) + 전체 화면 문서 뷰어 |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 뷰어 로드 중 중앙 스피너 + "문서를 불러오는 중…". DOCX 변환 미완료 시 "변환 중입니다. 잠시 후 새로고침해 주세요."
- [ ] empty: N/A
- [x] error: 404 LINK_NOT_FOUND → "존재하지 않는 링크입니다." / 410 LINK_EXPIRED → "이 링크는 만료되었습니다. 공유한 담당자에게 문의하세요." / 410 VIEW_LIMIT_EXCEEDED → "열람 가능 횟수를 초과했습니다." / 423 DOCUMENT_QUARANTINED → "보안상의 이유로 열람할 수 없는 문서입니다." / 429 RATE_LIMITED → "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요." — **모든 오류 화면에서 문서 제목·파일명·업로더 미노출** (PRD §4.5)
- [x] success: 문서 뷰어 렌더 (PDF 인라인 / DOCX는 변환된 PDF) + 다운로드 버튼. 열람 이벤트는 서버가 감사 로그 기록
- [x] no-permission: 401 PASSWORD_REQUIRED → 비밀번호 입력 폼 (문서 정보 미노출). 403 PASSWORD_INCORRECT → "비밀번호가 올바르지 않습니다." inline (red)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| password | input[type=password] | 비밀번호 링크만 | 1자 이상 입력 시 제출 가능 | "열람 비밀번호를 입력하세요" |
| password_submit | button | 비밀번호 링크만 | - | "확인" |
| viewer | PDF viewer (iframe/canvas) | Yes | viewUrl 5분 만료 — 만료 시 재발급 요청 | - |
| download_btn | button | Yes | downloadUrl 5분 만료 | "다운로드" |
| expiry_note | text | No | - | "이 링크는 {만료일시}까지 열람할 수 있습니다." |

### Microcopy

- 진입 안내(비밀번호 화면): "이 문서는 비밀번호로 보호되어 있습니다."
- 에러 메시지: "이 링크는 만료되었습니다. 공유한 담당자에게 문의하세요." (내부 코드·문서 정보 미노출)
- 만료 안내: "이 링크는 {만료일시}까지 열람할 수 있습니다."

### Responsive

- Desktop (≥1024px): 뷰어 max-w-4xl 중앙, 상단 바 고정
- Tablet (768~1023): 뷰어 좌우 여백 축소
- Mobile (<768): 뷰어 전체 폭, 다운로드 버튼은 하단 고정 바

### Wireframe Anchor

→ `04-wireframes/s-token.html#screen-s-token`

---

## Screen: /admin (전체 문서)

| 항목 | 값 |
|---|---|
| Audience | admin |
| Auth | Required + role=admin 검증 (DB role 컬럼 — 파라미터 승격 불가) |
| Linked FRs | FR-009, FR-015 |
| Layout | Filter bar(상태·검색·업로더·기간) + 전체 문서 테이블(상태 배지 포함) + 행 액션(삭제/복원) |
| Responsive | **Desktop only** (PRD §5.4) |

### States

- [x] loading: 테이블 스켈레톤 5행
- [x] empty: 필터 결과 0건 → "조건에 맞는 문서가 없습니다." + [필터 초기화]
- [x] error: 조회 실패 → 상단 배너 "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요." + [다시 시도]. 복원 시 410 RETENTION_EXPIRED → "보존 기간(30일)이 지나 복원할 수 없습니다."
- [x] success: 전체 문서 테이블 (상태 배지: active=중립 / deleted=red / quarantined=amber, 삭제 사유·삭제자 표시). 강제 삭제 성공 → "문서가 삭제되고 공유 링크가 모두 무효화되었습니다" 토스트. 복원 성공 → "문서가 복원되었습니다. 공유 링크는 다시 발급해야 합니다" 토스트
- [x] no-permission: admin 아님 → `/` 리다이렉트 + "관리자만 접근할 수 있습니다" 토스트

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| status | select (all/active/deleted/quarantined) | No | enum, 기본 all | "상태 전체" |
| q | input[type=search] | No | 최대 100자 | placeholder "파일명 검색" |
| uploaderId | select | No | - | "업로더 전체" |
| from / to | date range picker | No | from ≤ to | "업로드 기간" |
| delete_btn | button (danger, 행 액션) | No | 삭제 모달 열기 | "삭제" |
| delete_reason | textarea (모달 내) | Yes (타인 문서) | 필수, ≤500자 | "삭제 사유를 입력하세요 (업로더에게 전달됩니다)" |
| delete_confirm | button (danger, 모달) | Yes | 사유 입력 전 비활성 | "삭제 확정" |
| restore_btn | button (deleted 행만) | No | 30일 이내만 활성 | "복원" |
| load_more | button | No | nextCursor 존재 시 | "더 보기" |

### Microcopy

- 헤드라인: "전체 문서 관리"
- 삭제 확인: "이 문서를 삭제하면 모든 공유 링크가 즉시 무효화되며, 업로더에게 삭제 사유가 안내됩니다."
- 권한 안내: "관리자만 접근할 수 있습니다. 권한이 필요하면 시스템 관리자에게 문의하세요."

### Responsive

- Desktop (≥1024px): 전체 테이블 표시 (상태 / 파일명 / 업로더 / 업로드일 / 삭제 정보 / 링크 수 / 열람 수 / 액션)
- Mobile (<768): "관리 기능은 PC 환경에서 이용해 주세요." 안내만 표시

### Wireframe Anchor

→ `04-wireframes/admin.html#screen-admin`

### Open Questions

- [ ] 격리(quarantined) 문서의 관리자 원본 확인 경로 제공 여부 (v1은 미제공 가정)

---

## Screen: /admin/audit (감사 로그)

| 항목 | 값 |
|---|---|
| Audience | admin |
| Auth | Required + role=admin 검증 |
| Linked FRs | FR-010, FR-011 |
| Layout | Filter bar(문서·액터·액션·기간) + 로그 테이블 (읽기 전용, append-only 데이터) |
| Responsive | **Desktop only** (PRD §5.4) |

### States

- [x] loading: 테이블 스켈레톤 8행
- [x] empty: 기간 필터 결과 0건 → "해당 기간의 로그가 없습니다." + [기간 초기화]
- [x] error: 조회 실패 → 상단 배너 "감사 로그를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요." + [다시 시도]
- [x] success: 로그 테이블 (시각 / 액션 / 액터 유형·ID / 대상 문서 / IP / User-Agent), rate_limit_warn 행은 amber 강조
- [x] no-permission: admin 아님 → `/` 리다이렉트 + "관리자만 접근할 수 있습니다" 토스트

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| documentId | search select (문서) | No | - | "문서 전체" |
| actorId | search select (member/토큰) | No | - | "액터 전체" |
| action | select (upload/share_create/share_revoke/view/download/delete) | No | enum | "액션 전체" |
| from / to | date range picker | No | from ≤ to | "기간" |
| log_row | table row (읽기 전용) | - | - | - |
| load_more | button | No | nextCursor 존재 시 | "더 보기" |

### Microcopy

- 헤드라인: "감사 로그"
- 진입 안내: "업로드·공유·열람·삭제 이벤트가 기록됩니다. 로그는 수정·삭제할 수 없습니다."
- 빈 상태: "해당 기간의 로그가 없습니다."

### Responsive

- Desktop (≥1024px): 6열 테이블 전체 표시
- Mobile (<768): "관리 기능은 PC 환경에서 이용해 주세요." 안내만 표시

### Wireframe Anchor

→ `04-wireframes/admin-audit.html#screen-admin-audit`
