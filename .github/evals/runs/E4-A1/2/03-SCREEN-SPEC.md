# Screen Specifications — internal-doc-sharing (사내 문서 공유)

> **Generated from**: input-prd.md
> **Created**: 2026-07-26
> **Platform**: web (Desktop ≥1024 / Tablet 768~1023 / Mobile <768)

## Convention

각 화면은 다음 7개 슬롯을 모두 채운다:

1. **Meta**: Audience / Auth / Linked FRs / Layout / Responsive
2. **States**: §5.4.1에서 체크된 상태마다 1줄 이상
3. **Components**: 폼 필드/버튼/리스트 등 모든 UI 슬롯
4. **Microcopy**: 진입 안내, 버튼 라벨, 에러 메시지, 빈 상태 메시지
5. **Responsive**: 분기점별 레이아웃 변화
6. **Wireframe Anchor**: 04-WIREFRAME.html(인덱스) → 04-wireframes/{slug}.html의 anchor
7. **Open Questions** (선택)

> 페이지 7개 ≥ 6이므로 SKILL 규칙에 따라 와이어프레임은 `04-wireframes/<slug>.html`로 분할하고 `04-WIREFRAME.html`은 인덱스로 사용한다.
> 에러 메시지는 PRD §5.1의 `error.message` 사용자 노출 문구를 그대로 인용하며 내부 코드는 노출하지 않는다.

---

## Screen: /login

| 항목 | 값 |
|---|---|
| Audience | guest (미인증), member, admin |
| Auth | Optional (사내 이메일 도메인 화이트리스트 + Magic Link — FR-001) |
| Linked FRs | FR-001 |
| Layout | 중앙 정렬 단일 카드 (max-w-md), 이메일 입력 1필드 |
| Responsive | Desktop / Mobile — 동일 단일 카드, 폭만 축소 |

### States

- [x] loading: "로그인 링크 보내기" 클릭 후 버튼 스피너 + 비활성화 (중복 발송 방지)
- [ ] empty: N/A
- [x] error: 입력 필드 하단 inline — 형식 오류("이메일 주소 형식을 확인해주세요"), 발송 한도 초과 429("잠시 후 다시 시도해주세요. 같은 이메일로는 5분에 3회까지 요청할 수 있습니다")
- [x] success: 발송 완료 화면 전환 — "로그인 링크를 보냈습니다. 메일함을 확인해주세요. 링크는 15분간 유효합니다." (계정 존재 여부와 무관하게 동일 화면 — 계정 열거 방지)
- [x] no-permission: 허용 도메인 외 이메일 403 — 상단 warning 배너 "사내 이메일 계정으로만 로그인할 수 있습니다."

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| email | input[type=email] | Yes | 이메일 형식 (RFC 5322 기본 패턴), 서버 측 도메인 화이트리스트 재검증 | "회사 이메일 주소" / placeholder "name@company.com" |
| submit | button | Yes | 이메일 형식 통과 전 비활성 | "로그인 링크 보내기" |
| resend | button (발송 완료 화면) | No | 5분 3회 레이트 리밋 안내 | "링크 다시 보내기" |
| expired_notice | banner (Magic Link 만료 시) | No | - | "로그인 링크가 만료되었습니다. 다시 요청해주세요." |

### Microcopy

- 진입 안내: "사내 문서 공유. 회사 이메일로 로그인 링크를 받아 시작하세요."
- 에러: "이메일 주소 형식을 확인해주세요." / "사내 이메일 계정으로만 로그인할 수 있습니다."
- 성공: "로그인 링크를 보냈습니다. 메일함을 확인해주세요."

### Responsive

- Desktop (≥1024px): 중앙 카드 max-w-md, 상하 여백 충분
- Tablet (768~1023): 동일 카드 유지
- Mobile (<768): 카드 전폭(패딩 16px), 입력·버튼 세로 스택

### Wireframe Anchor

→ `04-wireframes/login.html#screen-login` (인덱스: `04-WIREFRAME.html`)

### Open Questions

- [ ] Magic Link 클릭 후 검증 중간 페이지(/auth/verify)를 별도 화면으로 둘지, /login 내 상태로 처리할지

---

## Screen: / (문서 목록)

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키 — 미인증 시 /login 리다이렉트) |
| Linked FRs | FR-003 (+ FR-009: 관리자 삭제 문서 표시) |
| Layout | 상단 필터 바 + 문서 테이블(Desktop) / 카드 리스트(Mobile), 20건 커서 페이지네이션 |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 테이블 행 스켈레톤 5줄 (필터 바는 즉시 렌더)
- [x] empty: 문서 0건 — "아직 업로드된 문서가 없습니다." + [문서 업로드] CTA. 필터 결과 0건 — "조건에 맞는 문서가 없습니다. 필터를 조정해보세요." + [필터 초기화]
- [x] error: 상단 배너 "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요." + [다시 시도]. 필터 형식 오류(400 INVALID_QUERY)는 해당 필터 inline
- [x] success: 문서 목록 렌더. 본인 문서에 "나의 문서" 배지, 관리자 삭제 문서는 "관리자에 의해 삭제됨" 상태로 표시(행 비활성)
- [ ] no-permission: N/A (인증 게이트에서 처리)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| search_q | input[type=search] | No | 파일명 부분일치, trim, 최대 200자 | placeholder "파일명 검색" |
| uploader_filter | select (member 목록) | No | - | "업로더 전체" |
| date_range | date range picker | No | from ≤ to, ISO date | "업로드 기간" |
| upload_btn | button (primary) | Yes | - | "문서 업로드" |
| doc_table | table/list (제목·업로더·크기·업로드일·링크 수·열람 수) | Yes | - | 열 헤더: "제목 / 업로더 / 크기 / 업로드일 / 공유 링크 / 열람" |
| my_badge | badge | No | `uploader_id = me` | "나의 문서" |
| deleted_badge | badge (neutral) | No | `status = deleted` | "관리자에 의해 삭제됨" |
| load_more | button (cursor pagination) | No | nextCursor 존재 시만 | "더 보기" |

### Microcopy

- 헤드라인: "문서 목록"
- 진입 안내: "조직에 공유된 문서를 확인하고, 링크 하나로 외부에 전달하세요."
- 빈 상태: "아직 업로드된 문서가 없습니다. 첫 문서를 업로드해보세요."
- 에러: "문서 목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요."

### Responsive

- Desktop (≥1024px): 필터 바 1열 가로 배치 + 6열 테이블
- Tablet (768~1023): 링크 수·열람 수 열 접힘 (4열)
- Mobile (<768): 필터는 [필터] 버튼 → 바텀 시트, 목록은 1열 카드(제목·업로더·날짜)

### Wireframe Anchor

→ `04-wireframes/home.html#screen-home` (인덱스: `04-WIREFRAME.html`)

### Open Questions

- [ ] "나의 문서" 탭 분리 여부 (현 명세는 배지 방식 — 01-IA Open Question 승계)

---

## Screen: /upload

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키) |
| Linked FRs | FR-002, FR-013 |
| Layout | 중앙 카드 (max-w-lg): 파일 드롭존 + 제목 입력 + 진행률 |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 업로드 중 진행률 바(%) + "업로드 중… 창을 닫지 마세요." 업로드 완료 후 스캔 대기 시 "검사 중" 배지 노출
- [ ] empty: N/A
- [x] error: 드롭존 하단 inline — 형식(400 INVALID_FILE_TYPE) "PDF 또는 DOCX 파일만 업로드할 수 있습니다." / 크기(413) "파일이 50MB를 초과합니다." / 쿼터(507) "저장 공간(5GB)이 가득 찼습니다. 문서를 정리한 뒤 다시 시도해주세요."
- [x] success: "업로드가 완료되었습니다" 토스트 → `/docs/{id}` 상세로 자동 이동
- [ ] no-permission: N/A (인증 게이트에서 처리)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| file | file dropzone (click + drag&drop) | Yes | 확장자 ∈ {.pdf, .docx}, 크기 ≤ 50MB (클라) + 매직 넘버·쿼터 (서버) | "파일을 끌어다 놓거나 클릭해서 선택하세요 (PDF/DOCX, 최대 50MB)" |
| title | input[type=text] | No | 최대 200자, 미입력 시 파일명 사용 | "문서 제목 (선택 — 비우면 파일명을 사용합니다)" |
| progress | progress bar | Yes (업로드 중) | 0–100% | "{percent}% 업로드 중" |
| scan_badge | badge (neutral) | No | scanStatus = pending | "검사 중 — 완료 후 공유 링크를 만들 수 있습니다" |
| submit | button (primary) | Yes | 파일 선택 전 비활성 | "업로드" |
| cancel | button (secondary) | No | - | "취소" |

### Microcopy

- 진입 안내: "PDF 또는 DOCX 문서를 올려 링크로 공유하세요. 파일당 최대 50MB."
- 에러: "PDF 또는 DOCX 파일만 업로드할 수 있습니다." (내부 코드 미노출)
- 성공: "업로드가 완료되었습니다."

### Responsive

- Desktop (≥1024px): 중앙 카드 max-w-lg, 드롭존 높이 240px
- Tablet (768~1023): 동일
- Mobile (<768): 드롭존 대신 [파일 선택] 버튼 중심 (드래그 불가 환경), 전폭 카드

### Wireframe Anchor

→ `04-wireframes/upload.html#screen-upload` (인덱스: `04-WIREFRAME.html`)

---

## Screen: /docs/{id} (문서 상세)

| 항목 | 값 |
|---|---|
| Audience | member, admin |
| Auth | Required (세션 쿠키) — 삭제/공유 액션은 소유자 또는 admin만 (서버 측 소유자 검사) |
| Linked FRs | FR-004, FR-005, FR-008 (+ FR-012 링크 옵션, FR-013 스캔 게이트) |
| Layout | 좌: 문서 메타 카드(제목·업로더·크기·업로드일·열람 수) + 우: 공유 링크 목록 패널. 공유 링크 생성은 모달 |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 메타 카드·링크 패널 스켈레톤
- [ ] empty: N/A (문서 단건 화면 — 링크 0건은 패널 내 안내 "아직 공유 링크가 없습니다.")
- [x] error: 404 시 전체 화면 "문서를 찾을 수 없습니다. 삭제되었거나 주소가 잘못되었습니다." + [목록으로]. 다운로드 409 SCAN_IN_PROGRESS "악성코드 검사가 끝나면 받을 수 있습니다." / 423 "이 문서는 보안상 격리되어 열 수 없습니다."
- [x] success: 메타 + 링크 목록 렌더. 링크 생성 성공 시 모달에 URL 1회 노출 + "링크는 지금만 복사할 수 있습니다" 경고 + [복사] 버튼 + 만료 일시
- [x] no-permission: 타인 문서 — 삭제·공유 버튼 미노출, 안내 캡션 "내가 올린 문서만 공유하거나 삭제할 수 있습니다." (열람·다운로드는 허용)

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| meta_card | card (제목·파일명·업로더·크기·업로드일·열람 수·scanStatus) | Yes | - | 라벨: "업로더 / 크기 / 업로드일 / 열람 수" |
| download_btn | button | Yes | scanStatus = clean일 때만 활성 | "원본 다운로드" |
| share_create_btn | button (primary, 소유자·admin만) | No | scanStatus = clean일 때만 활성 (409 게이트) | "공유 링크 만들기" |
| share_modal.expiresInDays | select (7/30/60/90) | Yes | 1 ≤ 일수 ≤ 90, 기본 7 | "만료 기간 (기본 7일, 최대 90일)" |
| share_modal.password | input[type=password] | No | 설정 시 8자 이상 | "열람 비밀번호 (선택, 8자 이상)" |
| share_modal.maxViews | input[type=number] | No | ≥1 정수 | "최대 열람 횟수 (선택, 비우면 무제한)" |
| share_modal.submit | button | Yes | - | "링크 생성" |
| copy_btn | button (생성 결과) | Yes | Clipboard API | "링크 복사" / 복사 후 "복사됨" |
| link_list | table (URL 마스킹·만료일·열람 수·상태) | Yes | 소유자·admin에게만 표시 | 열: "링크 / 만료 / 열람 / 상태" |
| revoke_btn | button (행별, danger) | No | 확인 다이얼로그 | "폐기" / 확인 "이 링크를 폐기하면 즉시 열 수 없게 됩니다." |
| delete_btn | button (danger, 소유자·admin만) | No | 확인 다이얼로그 필수 | "문서 삭제" / 확인 "삭제하면 이 문서의 모든 공유 링크가 즉시 무효화됩니다." |

### Microcopy

- 진입 안내: (breadcrumb) "홈 > 문서 상세"
- 에러: "문서를 찾을 수 없습니다. 삭제되었거나 주소가 잘못되었습니다."
- 토큰 1회 노출 경고: "보안을 위해 이 링크는 지금만 확인할 수 있습니다. 복사해두세요."
- 삭제 확인: "삭제하면 이 문서의 모든 공유 링크가 즉시 무효화됩니다. 계속할까요?"

### Responsive

- Desktop (≥1024px): 2열 (메타 7 : 링크 5)
- Tablet (768~1023): 1열 세로 스택 (메타 → 링크)
- Mobile (<768): 1열, 공유 링크 생성 모달은 전체 화면 시트로 전환

### Wireframe Anchor

→ `04-wireframes/doc-detail.html#screen-doc-detail` (인덱스: `04-WIREFRAME.html`)

### Open Questions

- [ ] 링크 목록의 URL 표시 방식 — 원문은 재조회 불가(해시 저장)이므로 목록에는 생성일·만료일만 표시하고 URL 열은 마스킹("복사 시점에만 노출") 확정 필요

---

## Screen: /s/{token} (공유 열람)

| 항목 | 값 |
|---|---|
| Audience | guest, member, admin |
| Auth | None — 공유 토큰이 유일한 자격 (PRD §5.4 유일한 무인증 페이지). `noindex` 메타 + `Referrer-Policy: no-referrer` |
| Linked FRs | FR-006, FR-007, FR-012, FR-014 |
| Layout | 최소 크롬: 상단 바(문서 제목 + 다운로드 버튼) + 전면 문서 뷰어. 사내 네비·링크 일절 미노출 |
| Responsive | Desktop / Mobile |

### States

- [x] loading: 뷰어 영역 스피너 + "문서를 불러오는 중…". DOCX 변환 미완료 시 "문서를 변환하고 있습니다. 잠시만 기다려주세요." (폴링)
- [ ] empty: N/A
- [x] error: 전체 화면 안내 — 404 "문서를 찾을 수 없습니다." / 410 LINK_EXPIRED "이 링크는 만료되었습니다. 공유한 담당자에게 문의하세요." / 410 VIEW_LIMIT_EXCEEDED "열람 가능 횟수를 초과했습니다. 공유한 담당자에게 문의하세요." / 423 "이 문서는 열람이 제한되었습니다." / 429 "요청이 많습니다. 잠시 후 다시 시도해주세요." — 모든 에러 화면에서 파일명·업로더 등 메타데이터 미노출
- [x] success: 문서 뷰어 렌더 (PDF 인라인 / DOCX는 변환된 PDF), 상단에 제목·만료 일시·다운로드 버튼. 열람 이벤트는 서버가 감사 로그 기록
- [x] no-permission: 비밀번호 설정 링크(401 PASSWORD_REQUIRED) — 중앙 비밀번호 입력 폼 "이 문서는 비밀번호로 보호되어 있습니다." 오답 403 시 inline "비밀번호가 올바르지 않습니다."

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| title_bar | header (제목 + 만료 일시) | Yes | - | "{문서 제목}" / "만료: {YYYY-MM-DD HH:mm}" |
| viewer | PDF inline viewer (iframe/embed, CSP 적용) | Yes | viewUrl 5분 만료 — 만료 시 재발급 요청 | - |
| password | input[type=password] | 조건부 (보호 링크만) | 입력 필수, `X-Share-Password` 헤더 전달 | "비밀번호를 입력하세요" |
| password_submit | button | 조건부 | - | "열람하기" |
| download_btn | button | Yes | 5분 presigned URL 발급, 만료 시 재클릭 재발급 | "다운로드" |
| error_panel | full-screen notice | 조건부 | 메타데이터 미노출 | 상태별 문구 (States 참조) |

### Microcopy

- 진입 안내: 없음 (외부인 대상 — 뷰어 즉시 표시가 원칙)
- 비밀번호 안내: "이 문서는 비밀번호로 보호되어 있습니다. 전달받은 비밀번호를 입력하세요."
- 에러: "이 링크는 만료되었습니다. 공유한 담당자에게 문의하세요." (코드·내부 정보 미노출)

### Responsive

- Desktop (≥1024px): 뷰어 max-w-4xl 중앙, 상단 고정 바
- Tablet (768~1023): 뷰어 전폭
- Mobile (<768): 뷰어 전폭·핀치 줌 허용, 다운로드 버튼은 하단 고정 바

### Wireframe Anchor

→ `04-wireframes/share-view.html#screen-share-view` (인덱스: `04-WIREFRAME.html`)

---

## Screen: /admin (전체 문서)

| 항목 | 값 |
|---|---|
| Audience | admin |
| Auth | Required + role 검증 (DB role 컬럼 기준 — 파라미터 승격 불가). member 접근 시 no-permission |
| Linked FRs | FR-009, FR-015 |
| Layout | Filter bar + 상태 포함 전체 문서 테이블 + 행 액션(삭제/복원). 삭제는 사유 입력 모달 |
| Responsive | **Desktop only** (PRD §5.4) — 모바일 접속 시 안내 |

### States

- [x] loading: 테이블 스켈레톤
- [x] empty: 필터 결과 0건 — "조건에 맞는 문서가 없습니다." + [필터 초기화]
- [x] error: 상단 배너 "목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요." + [다시 시도]. 복원 410 RETENTION_EXPIRED "보존 기간(30일)이 지나 복원할 수 없습니다."
- [x] success: 전체 문서(active/deleted/quarantined) 테이블. 삭제 완료 토스트 "문서를 삭제했습니다. 공유 링크 {n}건이 무효화되었습니다." 복원 완료 토스트 "문서를 복원했습니다. 공유 링크는 다시 발급해야 합니다."
- [x] no-permission: admin 아님 → `/` 리다이렉트 + 토스트 "관리자만 접근할 수 있습니다."

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| status_filter | select (all/active/deleted/quarantined) | No | 기본 all | "상태 전체" |
| search_q | input[type=search] | No | 최대 200자 | placeholder "파일명 검색" |
| uploader_filter | select | No | - | "업로더 전체" |
| date_range | date range picker | No | from ≤ to | "업로드 기간" |
| doc_table | table (제목·업로더·상태·업로드일·삭제 정보·링크·열람) | Yes | 20건 커서 페이지네이션 | 상태 배지: "활성 / 삭제됨 / 격리됨" |
| delete_btn | button (행별, danger) | No | 사유 모달 필수 | "삭제" |
| delete_modal.reason | textarea | Yes | 필수, ≤500자 — 미입력 시 "삭제 사유를 입력해주세요." | "삭제 사유 (필수, 500자 이내)" |
| delete_modal.confirm | button (danger) | Yes | reason 입력 전 비활성 | "삭제 확인" |
| restore_btn | button (행별, deleted + 30일 내만) | No | 보존 기간 검증 (서버) | "복원" |
| audit_link | link | Yes | - | "감사 로그 보기" |
| load_more | button | No | nextCursor 존재 시 | "더 보기" |

### Microcopy

- 헤드라인: "전체 문서 관리"
- 진입 안내: "조직의 모든 문서를 조회하고 부적절한 문서를 삭제할 수 있습니다. 삭제 즉시 모든 공유 링크가 무효화됩니다."
- 권한 안내: "관리자만 접근할 수 있습니다."
- 삭제 확인: "이 문서를 삭제하면 배포된 모든 공유 링크가 즉시 열리지 않게 됩니다. 사유는 감사 로그에 기록됩니다."

### Responsive

- Desktop (≥1024px): 전체 테이블 표시
- Mobile/Tablet (<1024): "관리 기능은 PC에서 이용해주세요." 안내 화면 (기능 미제공)

### Wireframe Anchor

→ `04-wireframes/admin.html#screen-admin` (인덱스: `04-WIREFRAME.html`)

---

## Screen: /admin/audit (감사 로그)

| 항목 | 값 |
|---|---|
| Audience | admin |
| Auth | Required + role 검증 (member 접근 시 no-permission) |
| Linked FRs | FR-010, FR-011 |
| Layout | Filter bar + append-only 로그 테이블 (조회 전용 — 수정/삭제 액션 없음) |
| Responsive | **Desktop only** (PRD §5.4) — 모바일 접속 시 안내 |

### States

- [x] loading: 테이블 스켈레톤
- [x] empty: 기간 필터 결과 0건 — "선택한 조건의 로그가 없습니다. 기간을 넓혀보세요."
- [x] error: 상단 배너 "감사 로그를 불러오지 못했습니다. 잠시 후 다시 시도해주세요." + [다시 시도]
- [x] success: 로그 테이블 (액션·액터·대상 문서·IP·User-Agent·시각), 20건 커서 페이지네이션
- [x] no-permission: admin 아님 → `/` 리다이렉트 + 토스트 "관리자만 접근할 수 있습니다."

### Components

| Slot | Type | Required | Validation | Microcopy |
|---|---|---|---|---|
| document_filter | search select (문서) | No | documentId | "문서 전체" |
| actor_filter | search select (액터) | No | actorId | "액터 전체" |
| action_filter | select (upload/share_create/share_revoke/view/download/delete) | No | enum 값만 | "액션 전체" |
| date_range | date range picker | No | from ≤ to | "기간" |
| log_table | table (시각·액션·액터(유형)·대상 문서·IP·User-Agent) | Yes | 조회 전용 | 액션 라벨: "업로드 / 링크 생성 / 링크 폐기 / 열람 / 다운로드 / 삭제" |
| load_more | button | No | nextCursor 존재 시 | "더 보기" |

### Microcopy

- 헤드라인: "감사 로그"
- 진입 안내: "업로드·공유·열람·삭제 이력을 조회합니다. 로그는 수정하거나 삭제할 수 없습니다."
- 권한 안내: "관리자만 접근할 수 있습니다."

### Responsive

- Desktop (≥1024px): 6열 테이블 전체 표시 (User-Agent는 말줄임 + 툴팁)
- Mobile/Tablet (<1024): "관리 기능은 PC에서 이용해주세요." 안내 화면

### Wireframe Anchor

→ `04-wireframes/admin-audit.html#screen-admin-audit` (인덱스: `04-WIREFRAME.html`)

### Open Questions

- [ ] 로그 내보내기(CSV)는 v1 범위 밖(BI 통계 제외)으로 두는지 확정
