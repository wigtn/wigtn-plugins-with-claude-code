# Screen Specifications — internal-doc-sharing (사내 문서 공유 서비스)

> **Generated from**: input-prd.md (§2.3 Roles, §5.4 Pages, §5.4.1 Page State Matrix, §5.5 User Flow)
> **Created**: 2026-07-26
> **Platform**: web (Desktop ≥1024 / Tablet 768~1023 / Mobile <768)
> **Wireframe**: FE 페이지 7개(≥6)이므로 `04-wireframes/<slug>.html` 분할 + `04-WIREFRAME.html` 인덱스

## Convention

각 화면은 7개 슬롯(Meta / States / Components / Microcopy / Responsive / Wireframe Anchor / Open Questions)을 채운다.
States는 PRD §5.4.1에서 체크(✓)된 항목만 명세한다. Audience는 §2.3 Role Key(`guest`/`member`/`admin`)를 그대로 인용한다.

---

## Screen: /login

| 항목 | 값 |
|---|---|
| Audience | guest(미인증 상태의 사내 구성원), member, admin |
| Auth | Optional (Magic Link — 사내 이메일 도메인 화이트리스트, FR-001) |
| Linked FRs | FR-001 |
| Layout | 중앙 정렬 단일 카드 (max-w-sm), 이메일 입력 1필드 + 발송 버튼 |
| Responsive | Desktop / Mobile (동일 카드, 폭만 축소) |

### States

- [x] loading: "로그인 링크 보내기" 클릭 → 버튼 스피너 + 비활성화 (중복 발송 방지)
- [x] error: 400 INVALID_EMAIL → 입력 필드 하단 inline "올바른 이메일 주소를 입력해 주세요." / 429 RATE_LIMITED → 상단 배너 "요청이 너무 많습니다. 5분 후 다시 시도해 주세요."
- [x] success: "메일함을 확인해 주세요. {email}로 로그인 링크를 보냈습니다. 링크는 15분간 유효합니다." 안내 화면으로 전환 (계정 존재 여부와 무관하게 동일 문구 — 계정 열거 방지)
- [x] no-permission: 403 DOMAIN_NOT_ALLOWED → 입력 필드 하단 "사내 이메일 계정으로만 로그인할 수 있습니다. 회사 이메일 주소를 사용해 주세요."

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| email | input[type=email] | Yes | 이메일 형식(RFC 5322 기본) + 공백 트림, 클라이언트 즉시 검증 | "회사 이메일" / placeholder "name@company.com" |
| submit | button | Yes | email 유효 시에만 활성화 | "로그인 링크 보내기" |
| resend | button(text) | No | 발송 성공 화면에서만, 60초 쿨다운 | "메일을 못 받으셨나요? 다시 보내기" |

### Microcopy

- 진입 안내: "사내 문서 공유 서비스입니다. 회사 이메일로 로그인 링크를 받아 시작하세요."
- 에러: "올바른 이메일 주소를 입력해 주세요." / "사내 이메일 계정으로만 로그인할 수 있습니다." (에러 코드 비노출)
- Magic Link 만료(410 TOKEN_EXPIRED, /auth/verify 실패 시 이 화면으로 복귀): "로그인 링크가 만료되었습니다. 다시 요청해 주세요."

### Responsive

- Desktop (≥1024px): 화면 중앙 카드 (max-w-sm)
- Tablet (768~1023): 동일
- Mobile (<768): 카드가 화면 폭에 맞춰 확장, 상하 여백 축소

### Wireframe Anchor

→ `04-wireframes/login.html#screen-login`

### Open Questions

- [ ] 로그인 후 리다이렉트: 항상 `/`인지, 진입 시도했던 보호 라우트(`?next=`)로 복귀인지

---

## Screen: / (문서 목록)

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키, 미인증 시 /login 리다이렉트) |
| Linked FRs | FR-003 (Secondary: FR-009 — 본인 문서의 "관리자에 의해 삭제됨" 배지) |
| Layout | 상단 필터 바(검색·업로더·기간) + 문서 테이블(Desktop)/카드 리스트(Mobile) + "더 보기" 커서 페이지네이션(20건) |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 최초 진입 시 테이블 행 스켈레톤 5개, 필터 변경 시 기존 목록 위 오버레이 스피너
- [x] empty: "아직 업로드된 문서가 없습니다." + CTA "첫 문서 업로드하기" (→ /upload). 필터 결과 0건이면 "조건에 맞는 문서가 없습니다. 필터를 초기화해 보세요." + "필터 초기화" 버튼
- [x] error: 상단 배너 "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요." + "다시 시도" 버튼 (400 INVALID_QUERY는 해당 필터 필드 inline 표시)
- [x] success: 문서 행(제목, 업로더, 크기, 업로드일, 공유 링크 수, 열람 수) + 본인 문서 "나의 문서" 배지, 행 클릭 → /docs/{id}

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| q | input[type=search] | No | ≤100자, 파일명 부분일치 | placeholder "파일명으로 검색" |
| uploaderId | select(combobox) | No | member 목록에서 선택 | "업로더 전체" |
| from / to | date-range picker | No | from ≤ to, ISO date (위반 시 "종료일은 시작일 이후여야 합니다.") | "업로드 기간" |
| upload_btn | button(primary) | Yes | - | "문서 업로드" |
| doc_row | list row(link) | Yes | - | 행 전체 클릭 → 상세 |
| load_more | button | No | nextCursor 존재 시에만 렌더 | "더 보기" |

### Microcopy

- 헤드라인: "문서 목록"
- 진입 안내(서브텍스트): "조직에 업로드된 문서를 검색하고, 링크 하나로 외부에 공유하세요."
- 빈 상태: "아직 업로드된 문서가 없습니다. 첫 문서를 올려 링크로 공유해 보세요."
- 에러: "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."

### Responsive

- Desktop (≥1024px): 6열 테이블(제목/업로더/크기/업로드일/링크 수/열람 수) + 좌측 정렬 필터 바 1행
- Tablet (768~1023): 크기·열람 수 열 숨김, 필터 바 유지
- Mobile (<768): 카드 리스트(제목 + 업로더·날짜 메타 1줄), 필터는 상단 "필터" 버튼 → bottom sheet, 업로드 버튼은 하단 고정(floating)

### Wireframe Anchor

→ `04-wireframes/list.html#screen-list`

### Open Questions

- [ ] "나의 문서" 우선 정렬 vs 전체 최신순 (v1은 전체 최신순으로 명세)

---

## Screen: /upload

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키) |
| Linked FRs | FR-002, FR-013 |
| Layout | 중앙 단일 컬럼 (max-w-lg): 드래그&드롭 존 + 제목 입력 + 업로드 버튼 + 진행률 바 |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 업로드 중 진행률 바(%) + "업로드 중… {n}%" + 취소 버튼. 완료 직후 scanStatus=pending이면 "악성코드 검사 중" 배지와 함께 상세로 이동
- [x] error: 파일 존 하단 inline — 400 INVALID_FILE_TYPE "PDF 또는 DOCX 파일만 업로드할 수 있습니다." / 413 FILE_TOO_LARGE "파일이 50MB를 초과합니다." / 507 QUOTA_EXCEEDED "저장 용량(5GB)을 초과했습니다. 기존 문서를 삭제한 뒤 다시 시도해 주세요." / 네트워크 실패 "업로드에 실패했습니다. 네트워크를 확인하고 다시 시도해 주세요."
- [x] success: "업로드가 완료되었습니다." 토스트 → /docs/{id}로 전환 (Scenario 1)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| file | file dropzone (input[type=file]) | Yes | accept=".pdf,.docx", 1개, ≤50MB — 클라이언트 선검증 + 서버 매직 넘버 재검증 | "파일을 끌어다 놓거나 클릭해서 선택하세요 (PDF·DOCX, 최대 50MB)" |
| title | input[type=text] | No | ≤200자, 미입력 시 파일명 사용 | "문서 제목 (선택 — 비우면 파일명 사용)" |
| submit | button(primary) | Yes | file 선택 전 비활성화 | "업로드" |
| cancel | button | No | 업로드 진행 중에만 | "취소" |
| progress | progressbar | Yes | aria-valuenow 갱신 | "업로드 중… {n}%" |

### Microcopy

- 진입 안내: "PDF 또는 DOCX 문서를 올리세요. 업로드 후 공유 링크를 만들어 외부에 전달할 수 있습니다."
- 스캔 안내: "업로드된 파일은 악성코드 검사를 거칩니다. 검사가 끝나야 공유 링크를 만들 수 있습니다."
- 에러: "PDF 또는 DOCX 파일만 업로드할 수 있습니다." (Scenario 2 — 위장 파일도 동일 문구, 검사 방식 비노출)

### Responsive

- Desktop (≥1024px): 중앙 카드 max-w-lg, 드롭존 높이 240px
- Tablet (768~1023): 동일
- Mobile (<768): 1열, 드롭존은 "파일 선택" 버튼 중심(드래그 힌트 숨김), 업로드 버튼 전체 폭

### Wireframe Anchor

→ `04-wireframes/upload.html#screen-upload`

### Open Questions

- [ ] 업로드 중 페이지 이탈 시 확인 다이얼로그 여부

---

## Screen: /docs/{id} (문서 상세)

| 항목 | 값 |
|---|---|
| Audience | member(타인 문서는 읽기 전용), admin |
| Auth | Required (세션 쿠키. 삭제/공유는 서버 측 소유자 검사 — 클라이언트 role 신뢰 금지) |
| Linked FRs | FR-004, FR-005, FR-008 (Secondary: FR-013 — 스캔 완료 전 공유 차단) |
| Layout | 2컬럼(Desktop): 좌측 문서 메타 + 다운로드, 우측 공유 링크 패널(소유자/admin만). 하단 위험 영역(삭제) |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 메타 영역 스켈레톤(제목·메타 3줄) + 공유 패널 스켈레톤
- [x] error: 404 DOCUMENT_NOT_FOUND → "문서를 찾을 수 없습니다. 삭제되었거나 주소가 잘못되었습니다." + "목록으로" 버튼 / 링크 생성 409 SCAN_IN_PROGRESS → 패널 내 "악성코드 검사 중에는 공유 링크를 만들 수 없습니다." / 423 DOCUMENT_QUARANTINED → 상단 빨간 배너 "보안 검사에서 문제가 발견되어 격리된 문서입니다. 다운로드와 공유가 차단됩니다."
- [x] success: 메타(제목·파일명·크기·업로더·업로드일·열람 수) + 공유 링크 목록(URL 마스킹, 만료일, 열람 수, 폐기 버튼). 링크 생성 성공 시 토큰 원문 1회 노출 모달 "이 링크는 지금만 복사할 수 있습니다." + "복사" 버튼 (Scenario 3)
- [x] no-permission: 타인 문서 → 삭제 버튼·공유 패널 **미노출**(읽기 전용), 안내 캡션 "본인이 업로드한 문서만 공유하거나 삭제할 수 있습니다." API 직접 호출 403은 토스트 "이 문서에 대한 권한이 없습니다."

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| download_btn | button | Yes | scanStatus=clean일 때만 활성 (pending → tooltip "검사 중", infected → 비노출) | "원본 다운로드" |
| share_create_btn | button(primary) | Yes(소유자/admin) | scanStatus=clean일 때만 활성 | "공유 링크 만들기" |
| expiresInDays | select | Yes(모달 내) | 1~90, 기본 7 | "만료 기간 (기본 7일, 최대 90일)" |
| password | input[type=password] | No | 설정 시 ≥8자 — 미달 시 "비밀번호는 8자 이상이어야 합니다." | "열람 비밀번호 (선택)" |
| maxViews | input[type=number] | No | ≥1 정수 — 위반 시 "1 이상의 숫자를 입력해 주세요." | "최대 열람 횟수 (선택 — 비우면 무제한)" |
| link_copy | button | Yes(생성 직후) | - | "링크 복사" |
| link_revoke | button(danger-text) | No | 확인 다이얼로그 "이 링크로는 더 이상 열람할 수 없습니다." | "폐기" |
| delete_btn | button(danger) | Yes(소유자/admin) | 확인 다이얼로그 필수 | "문서 삭제" |

### Microcopy

- 진입 안내: "문서 정보와 공유 링크를 관리합니다. 링크를 폐기하면 이미 전달된 링크도 즉시 열 수 없게 됩니다."
- 삭제 확인: "이 문서를 삭제할까요? 이 문서의 공유 링크 {n}개가 모두 즉시 무효화됩니다."
- 관리자 삭제 문서(FR-009, 업로더 화면): 상단 배너 "관리자에 의해 삭제된 문서입니다."
- 에러: "문서를 찾을 수 없습니다." / "이 문서에 대한 권한이 없습니다." (에러 코드 비노출)

### Responsive

- Desktop (≥1024px): 좌 7 / 우 5 2컬럼, 공유 링크 테이블 형태
- Tablet (768~1023): 2컬럼 유지, 공유 링크는 카드로 전환
- Mobile (<768): 1열 스택(메타 → 다운로드 → 공유 패널 → 위험 영역), 링크 생성은 전체 화면 모달

### Wireframe Anchor

→ `04-wireframes/doc-detail.html#screen-doc-detail`

### Open Questions

- [ ] 공유 링크 URL 마스킹 표기 (생성 이후에는 해시만 있으므로 `…/s/ab12…` 프리픽스 표시 방식)

---

## Screen: /s/{token} (공유 열람)

| 항목 | 값 |
|---|---|
| Audience | guest(유효 토큰 보유자), member, admin |
| Auth | None — 토큰이 유일한 자격 (PRD §5.4 규칙: 검증 실패 시 문서 메타데이터 일절 비노출) |
| Linked FRs | FR-006, FR-007, FR-012, FR-014 |
| Layout | 크롬 최소화: 얇은 상단 바(문서 제목 + 다운로드 버튼) + 전면 문서 뷰어. 사내 네비게이션 미렌더링. `noindex` + `Referrer-Policy: no-referrer` |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 뷰어 영역 스피너 "문서를 불러오는 중…". DOCX 변환 미완료 시 "문서를 변환하고 있습니다. 잠시만 기다려 주세요." (자동 재시도)
- [x] error: 404 LINK_NOT_FOUND → "문서를 찾을 수 없습니다. 링크가 삭제되었거나 주소가 잘못되었습니다." / 410 LINK_EXPIRED → "이 링크는 만료되었습니다. 공유한 담당자에게 문의하세요." (Scenario 5) / 410 VIEW_LIMIT_EXCEEDED → "열람 가능 횟수를 초과한 링크입니다. 공유한 담당자에게 문의하세요." / 423 DOCUMENT_QUARANTINED → "지금은 열람할 수 없는 문서입니다." / 429 RATE_LIMITED → "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요." — **모든 에러 화면에서 제목·파일명·업로더 비노출**
- [x] success: 문서 뷰어 렌더(PDF 인라인 / DOCX는 변환본 PDF), 상단 바에 제목·만료 일시·"다운로드" 버튼. 열람 이벤트는 서버가 감사 로그 기록 (Scenario 4)
- [x] no-permission: 401 PASSWORD_REQUIRED → 중앙 카드 비밀번호 입력 폼 "이 문서는 비밀번호로 보호되어 있습니다." / 403 PASSWORD_INCORRECT → inline "비밀번호가 올바르지 않습니다. 다시 입력해 주세요."

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| viewer | PDF inline viewer(iframe/canvas) | Yes | viewUrl 5분 만료 — 만료 시 자동 재발급 | - |
| password | input[type=password] | 조건부(비밀번호 링크만) | 비어 있으면 제출 불가 | "열람 비밀번호" |
| pw_submit | button(primary) | 조건부 | - | "열람하기" |
| download_btn | button | Yes | downloadUrl 5분 만료 | "다운로드" |
| expiry_caption | text | Yes | - | "이 링크는 {YYYY-MM-DD HH:mm}까지 유효합니다." |

### Microcopy

- 상단 바: "{문서 제목}" + "이 링크는 {만료 일시}까지 유효합니다."
- 비밀번호 폼: "이 문서는 비밀번호로 보호되어 있습니다. 전달받은 비밀번호를 입력하세요."
- 에러: 위 States의 문구를 그대로 사용 — 상태 코드·내부 사유 비노출, 문서 정보 비노출

### Responsive

- Desktop (≥1024px): 뷰어 max-w-4xl 중앙, 상단 바 고정
- Tablet (768~1023): 뷰어 전체 폭
- Mobile (<768): 상단 바 컴팩트(제목 말줄임), 뷰어 전체 화면, 다운로드는 상단 바 아이콘 버튼

### Wireframe Anchor

→ `04-wireframes/share-view.html#screen-share-view`

### Open Questions

- [ ] viewUrl(5분) 만료 시 재발급 UX — 무중단 자동 갱신 vs "다시 불러오기" 버튼

---

## Screen: /admin (전체 문서)

| 항목 | 값 |
|---|---|
| Audience | admin |
| Auth | Required + role=admin (DB role 컬럼 판정 — 파라미터·헤더로 승격 불가) |
| Linked FRs | FR-009, FR-015 |
| Layout | 필터 바(상태·파일명·업로더·기간) + 전체 문서 테이블(status 배지 포함) + 행 액션(삭제/복원). **Desktop only** |
| Responsive | Desktop only (<1024px 접속 시 "PC에서 접속해 주세요" 안내) |

### States

- [x] loading: 테이블 행 스켈레톤 8개
- [x] empty: 필터 결과 0건 → "조건에 맞는 문서가 없습니다. 필터를 초기화해 보세요." + "필터 초기화" 버튼
- [x] error: 상단 배너 "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요." + "다시 시도"
- [x] success: 상태별 배지 — active(회색) / deleted(빨간 텍스트 "삭제됨" + 삭제자·사유 tooltip) / quarantined(노란 배지 "격리됨"). deleted 행에는 30일 이내일 때 "복원" 버튼
- [x] no-permission: member 접속 → "관리자만 접근할 수 있습니다." 안내 후 `/`로 리다이렉트 (토스트 유지)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| status_filter | select | No | active/deleted/quarantined/all (기본 all) | "상태 전체" |
| q / uploaderId / from·to | search + select + date-range | No | 목록 화면과 동일 규칙 | "파일명으로 검색" 외 |
| delete_btn | button(danger, 행 단위) | Yes | 모달에서 reason 필수 | "삭제" |
| reason | textarea(모달 내) | Yes(삭제 시) | 1~500자 — 미입력 시 "삭제 사유를 입력해 주세요." (400 REASON_REQUIRED) | "삭제 사유 (업로더에게 표시되지 않으며 감사 로그에 기록됩니다)" |
| delete_confirm | button(danger) | Yes | reason 유효 시 활성 | "삭제 확인" |
| restore_btn | button(행 단위) | No | deleted + 30일 이내만 노출. 410 RETENTION_EXPIRED → "보존 기간(30일)이 지나 복원할 수 없습니다." | "복원" |
| audit_link | link | Yes | - | "감사 로그 보기" |

### Microcopy

- 헤드라인: "전체 문서 관리"
- 진입 안내: "삭제·격리 문서를 포함한 조직의 모든 문서입니다. 부적절한 문서는 사유와 함께 삭제할 수 있습니다."
- 삭제 확인 모달: "이 문서를 강제 삭제할까요? 공유 링크 {n}개가 즉시 무효화되며, 이 조치는 감사 로그에 기록됩니다." (Scenario 6)
- 복원 안내: "복원해도 기존 공유 링크는 되살아나지 않습니다. 필요 시 업로더가 다시 발급해야 합니다."
- 권한 안내: "관리자만 접근할 수 있습니다."

### Responsive

- Desktop (≥1024px): 8열 테이블 전체 표시
- Mobile/Tablet (<1024px): "관리 화면은 PC에서 접속해 주세요." 안내 (기능 미제공)

### Wireframe Anchor

→ `04-wireframes/admin.html#screen-admin`

### Open Questions

- [ ] 격리(quarantined) 문서에 대한 관리자 액션 범위 — v1은 조회·삭제만인지, 격리 해제가 필요한지

---

## Screen: /admin/audit (감사 로그)

| 항목 | 값 |
|---|---|
| Audience | admin |
| Auth | Required + role=admin |
| Linked FRs | FR-011 (표시 스키마는 FR-010의 로그 항목) |
| Layout | 필터 바(문서·액터·액션·기간) + 로그 테이블(시각 내림차순) + "더 보기" 커서 페이지네이션. **Desktop only** |
| Responsive | Desktop only (<1024px 접속 시 안내) |

### States

- [x] loading: 테이블 행 스켈레톤 10개
- [x] empty: "선택한 기간에 기록된 로그가 없습니다. 기간을 넓혀 보세요."
- [x] error: 상단 배너 "감사 로그를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요." + "다시 시도"
- [x] success: 행 — 시각 / 액션 배지(upload·share_create·share_revoke·view·download·delete·restore·rate_limit_warn) / 액터(user 이메일 또는 "공유 토큰 {id 앞 8자}") / 대상 문서(링크) / IP / User-Agent(말줄임 + tooltip). rate_limit_warn 행은 노란 배경 강조
- [x] no-permission: member 접속 → "관리자만 접근할 수 있습니다." 안내 후 `/` 리다이렉트

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| documentId | combobox | No | 문서 검색 선택 | "문서 전체" |
| actorId | combobox | No | member 목록 | "액터 전체" |
| action | select | No | upload/share_create/share_revoke/view/download/delete (기본 전체) | "액션 전체" |
| from / to | date-range picker | No | from ≤ to | "기간" |
| load_more | button | No | nextCursor 존재 시 | "더 보기" |

### Microcopy

- 헤드라인: "감사 로그"
- 진입 안내: "업로드·공유·열람·삭제 이벤트의 기록입니다. 로그는 수정하거나 삭제할 수 없습니다."
- 빈 상태: "선택한 기간에 기록된 로그가 없습니다. 기간을 넓혀 보세요."

### Responsive

- Desktop (≥1024px): 6열 테이블 전체 표시
- Mobile/Tablet (<1024px): "관리 화면은 PC에서 접속해 주세요." 안내

### Wireframe Anchor

→ `04-wireframes/admin-audit.html#screen-admin-audit`

### Open Questions

- [ ] 로그 CSV 내보내기 필요 여부 (PRD 범위 밖 — v2 후보)

---

## State Coverage Check (PRD §5.4.1 대비)

| Route | loading | empty | error | success | no-permission |
|-------|---------|-------|-------|---------|---------------|
| /login | ✓ 명세 | - | ✓ 명세 | ✓ 명세 | ✓ 명세 |
| / | ✓ 명세 | ✓ 명세 | ✓ 명세 | ✓ 명세 | - |
| /upload | ✓ 명세 | - | ✓ 명세 | ✓ 명세 | - |
| /docs/{id} | ✓ 명세 | - | ✓ 명세 | ✓ 명세 | ✓ 명세 |
| /s/{token} | ✓ 명세 | - | ✓ 명세 | ✓ 명세 | ✓ 명세 |
| /admin | ✓ 명세 | ✓ 명세 | ✓ 명세 | ✓ 명세 | ✓ 명세 |
| /admin/audit | ✓ 명세 | ✓ 명세 | ✓ 명세 | ✓ 명세 | ✓ 명세 |

체크된 상태 전부에 1줄 이상 마이크로카피/UI 처리 명세 완료 ✓
