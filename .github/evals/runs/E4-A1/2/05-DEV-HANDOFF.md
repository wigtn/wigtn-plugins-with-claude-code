# Dev Handoff — internal-doc-sharing (사내 문서 공유)

> **Generated from**: 01-IA.md + 02-USER-FLOW.md + 03-SCREEN-SPEC.md + 04-WIREFRAME.html
> **Target**: `/implement internal-doc-sharing`
> **Created**: 2026-07-26

## 1. FR ↔ Screen ↔ Component Mapping

화면 목록: `/login`, `/` (문서 목록), `/upload`, `/docs/{id}`, `/s/{token}`, `/admin`, `/admin/audit`

| FR | Description | Screens | Components | Estimated Tasks |
|----|------------|---------|-----------|----------------|
| FR-001 | 사내 이메일 도메인 화이트리스트 + Magic Link 로그인/로그아웃 | `/login` | EmailLoginForm, MagicLinkSentPanel, ResendButton, ErrorBanner(403 DOMAIN_NOT_ALLOWED) | `POST /api/v1/auth/login`·`/auth/verify` 구현, 도메인 화이트리스트 검증, 세션 쿠키(HttpOnly+Secure+SameSite=Lax) 발급, 발송 레이트 리밋(5분 3회), 로그아웃, 발송 완료/재발송 UI |
| FR-002 | PDF/DOCX 업로드 (≤50MB, 확장자+매직 넘버 이중 검증, 5GB 쿼터) | `/upload` | UploadDropzone, TitleInput, UploadProgressBar, ScanStatusBadge, ErrorInline(400/413/507) | `POST /api/v1/documents` multipart 처리, 클라 확장자·크기 검증, 서버 매직 넘버 검증, 파일명 정규화, 쿼터 검사, 진행률 표시, 성공 시 `/docs/{id}` 이동 |
| FR-003 | 조직 문서 목록 조회 + 파일명/업로더/기간 필터 + 20건 페이지네이션 | `/` (문서 목록) | DocFilterBar(SearchInput, UploaderSelect, DateRangePicker), DocTable, MyDocBadge, EmptyState, ErrorBanner, LoadMoreButton(CursorPagination) | `GET /api/v1/documents` 쿼리(q/uploaderId/from/to/cursor/limit), 커서 페이지네이션 훅, 필터 상태 URL 동기화, "나의 문서" 배지, 스켈레톤/empty/error 상태 |
| FR-004 | 문서 상세 조회 + 원본 다운로드 | `/docs/{id}` | DocMetaCard, DownloadButton, ShareLinkList, ErrorFullPage(404) | `GET /api/v1/documents/{id}`, `GET /api/v1/documents/{id}/download`(presigned 5분), scanStatus에 따른 다운로드 버튼 활성 제어(409/423 처리) |
| FR-005 | 공유 링크 생성 (CSPRNG 128bit 토큰, 해시 저장, 만료 기본 7·최대 90일) | `/docs/{id}` | ShareLinkModal(ExpirySelect, PasswordInput, MaxViewsInput), TokenRevealPanel, CopyButton, ShareLinkList | `POST /api/v1/documents/{id}/share-links`, CSPRNG 토큰 생성 + SHA-256 해시 저장, 토큰 원문 1회 노출 UI + 클립보드 복사, 만료일 검증(400 INVALID_EXPIRY) |
| FR-006 | guest가 링크로 로그인 없이 열람 (PDF 인라인 / DOCX 변환본 렌더, 다운로드) | `/s/{token}` | ShareViewer(PDF iframe/embed + CSP), ShareTitleBar, DownloadButton, ConvertingIndicator | `GET /api/v1/share/{token}`, viewUrl/downloadUrl(5분 presigned) 렌더, DOCX 변환 중 폴링 UI, 최소 크롬(네비 미노출) 레이아웃 |
| FR-007 | 링크 무효화 3경로 (만료·폐기·문서 삭제) + 무효 시 메타데이터 미노출 | `/s/{token}`, `/docs/{id}` | ErrorFullPage(404/410 — 메타데이터 미노출), RevokeButton + ConfirmDialog | 토큰 검증 함수(해시 일치+미폐기+미만료+열람 수), `DELETE /api/v1/share-links/{linkId}`, 문서 삭제 시 링크 일괄 무효화, 무효 응답 본문에서 파일명·업로더 제거, 통합 테스트(3경로) |
| FR-008 | 본인 문서 soft delete + 링크 동시 무효화 | `/docs/{id}` | DeleteButton(danger), ConfirmDialog, Toast | `DELETE /api/v1/documents/{id}` 서버 측 소유자 검사(403), soft delete + 링크 일괄 revoke 트랜잭션, 타인 문서 버튼 미노출(no-permission), 삭제 후 `/` 이동 |
| FR-009 | admin 전체 문서 조회 + 사유 필수 강제 삭제, 업로더 화면에 "관리자에 의해 삭제됨" 표시 | `/admin`, `/` (배지 표시) | AdminDocFilterBar(StatusSelect 포함), AdminDocTable, DeleteReasonModal, DeletedBadge, Toast | `GET /api/v1/admin/documents`(status 필터), `DELETE` + reason 필수(400 REASON_REQUIRED), admin role 가드(DB role 컬럼), `/` 목록에 삭제 배지·행 비활성, 삭제 토스트("링크 {n}건 무효화") |
| FR-010 | 업로드/링크 생성·폐기/열람/다운로드/삭제 감사 로그 기록 | **Backend (API/worker)** — 조회 UI는 `/admin/audit`(FR-011) | (FE 컴포넌트 없음 — 서버 사이드 기록) | audit_logs append-only 기록 함수(액터·액션·문서·IP·UA), 각 API 핸들러에 로깅 삽입, 열람 시 view_count 증가, UPDATE/DELETE 경로 미제공 검증 |
| FR-011 | admin 감사 로그 문서별·기간별 조회 | `/admin/audit` | AuditFilterBar(DocumentSelect, ActorSelect, ActionSelect, DateRangePicker), AuditLogTable, EmptyState, LoadMoreButton | `GET /api/v1/admin/audit-logs` 쿼리·커서 페이지네이션, 액션 한글 라벨 매핑, User-Agent 말줄임+툴팁, Desktop only 가드 |
| FR-012 | 링크 접근 제한 옵션 — 열람 비밀번호 / 최대 열람 횟수 | `/docs/{id}` (설정), `/s/{token}` (검증) | ShareLinkModal(PasswordInput ≥8자, MaxViewsInput ≥1), PasswordGate, ErrorInline(403 PASSWORD_INCORRECT), ErrorFullPage(410 VIEW_LIMIT_EXCEEDED) | password bcrypt/argon2 해시 저장, `X-Share-Password` 헤더 검증(401/403), max_views 카운트 검증(410), PasswordGate 폼 UI |
| FR-013 | 백그라운드 악성코드 스캔 + 격리 + 알림, 스캔 전 공유 차단 | `/upload`, `/docs/{id}` (+ **Backend worker**) | ScanStatusBadge("검사 중"), ShareCreateButton 비활성(409 게이트), QuarantineNotice(423) | 스캔 워커 + scan_status 갱신, 공유 생성·다운로드 409 SCAN_IN_PROGRESS 게이트, infected 시 quarantined 전환 + 업로더·관리자 알림, scanStatus 폴링 |
| FR-014 | 공유 엔드포인트 IP 레이트 리밋 (분당 30회) + 초과 경고 로깅 | **Backend (미들웨어)** — FE 접점: `/s/{token}` 429 에러 상태 | ErrorFullPage(429 "요청이 많습니다. 잠시 후 다시 시도해주세요.") | `/api/v1/share/*` IP 레이트 리밋 미들웨어, 429 응답, 임계 초과 시 audit_logs `rate_limit_warn` 기록, 429 에러 화면 |
| FR-015 | admin 삭제 문서 30일 내 복원 (링크는 무효 유지) | `/admin` | RestoreButton(deleted + 30일 내 행만), Toast, ErrorBanner(410 RETENTION_EXPIRED) | `POST /api/v1/admin/documents/{id}/restore`, 보존 기간 서버 검증, 복원 토스트("링크는 다시 발급해야 합니다"), 410 처리 |
| FR-016 | 보존 정책 (기본 1년) + 만료 문서 배치 자동 정리 | **Backend (worker/배치)** — v1 FE 노출 없음 (업로드 시 만료 정책 입력은 P2) | (FE 컴포넌트 없음) | documents.expires_at 기본값 세팅, 만료 도래 문서 정리 배치(cron), soft delete 30일 경과 물리 삭제 배치 |

### Coverage Check

- 모든 FR 매핑 여부: **✓** (FR-001~FR-016, 16/16 — 누락 없음)
  - Backend 전용 3건은 FE 접점을 명시: FR-010(기록 자체는 서버, 조회 UI는 `/admin/audit`), FR-014(미들웨어, FE는 `/s/{token}` 429 상태만), FR-016(배치, v1 FE 노출 없음)
- 모든 화면이 1+ FR 연결 여부: **✓** — 고아 페이지 없음
  - `/login`(FR-001) / `/`(FR-003, FR-009) / `/upload`(FR-002, FR-013) / `/docs/{id}`(FR-004·005·007·008·012·013) / `/s/{token}`(FR-006·007·012·014) / `/admin`(FR-009, FR-015) / `/admin/audit`(FR-010, FR-011)
- 매핑 누락 FR: **없음**

## 2. Component Inventory

### Reusable (다른 기능에서도 재사용 가능)

- `EmptyState` — 결과 0건 안내 + CTA 슬롯 (`/`, `/admin`, `/admin/audit`)
- `ErrorBanner` — 상단 에러 배너 + [다시 시도] (목록/관리 화면 공통)
- `Toast` — 성공/실패 알림 (업로드 완료, 삭제, 복원, 권한 리다이렉트)
- `ConfirmDialog` — 파괴적 액션 확인 (문서 삭제, 링크 폐기)
- `StatusBadge` — 상태 배지 variant: 나의 문서 / 관리자에 의해 삭제됨 / 검사 중 / 활성·삭제됨·격리됨
- `LoadMoreButton` + `useCursorPagination` — nextCursor 기반 20건 페이지네이션 훅
- `DateRangePicker` — from ≤ to 검증 포함 (`/`, `/admin`, `/admin/audit`)
- `SearchSelect` — 업로더/문서/액터 검색 셀렉트
- `CopyButton` — Clipboard API + "복사됨" 피드백
- `Skeleton` — 테이블 행/카드 스켈레톤
- `useBreakpoint` — Desktop ≥1024 / Tablet 768~1023 / Mobile <768 분기
- `DesktopOnlyGuard` — `/admin*` 모바일 접속 시 "관리 기능은 PC에서 이용해주세요." 안내
- `GlobalNav` — 로그인 후 top 네비 (관리 메뉴는 admin role만 렌더)

### Feature-specific

- `EmailLoginForm` / `MagicLinkSentPanel` — `/login` 이메일 입력·발송 완료·재발송
- `UploadDropzone` / `UploadProgressBar` — `/upload` 드롭존(모바일은 파일 선택 버튼) + 진행률
- `DocFilterBar` / `DocTable` — `/` 필터 바 + 문서 테이블(모바일 카드 전환)
- `DocMetaCard` — `/docs/{id}` 문서 메타 (제목·업로더·크기·업로드일·열람 수·scanStatus)
- `ShareLinkModal` — 만료일(7/30/60/90)·비밀번호·최대 열람 횟수 입력 (모바일 전체 화면 시트)
- `TokenRevealPanel` — 토큰 원문 1회 노출 + "지금만 복사할 수 있습니다" 경고
- `ShareLinkList` — 링크 목록(마스킹·만료·열람·상태) + 행별 RevokeButton
- `ShareViewer` / `ShareTitleBar` — `/s/{token}` PDF 인라인 뷰어(CSP) + 최소 크롬 상단 바
- `PasswordGate` — 보호 링크 비밀번호 입력 폼 (`X-Share-Password`)
- `ConvertingIndicator` — DOCX "변환 중" 폴링 표시
- `ErrorFullPage` — `/s/{token}`·`/docs/{id}` 전체 화면 에러 (메타데이터 미노출 원칙)
- `AdminDocTable` / `AdminDocFilterBar` — `/admin` 상태 포함 전체 문서 테이블
- `DeleteReasonModal` — 삭제 사유(필수, ≤500자) 입력 모달
- `RestoreButton` — deleted + 30일 내 행 전용 복원 버튼
- `AuditLogTable` / `AuditFilterBar` — `/admin/audit` append-only 로그 테이블 + 필터

## 3. State Management

> 그린필드 Next.js 앱(PRD §5.3: Next.js SSR + API Routes, PostgreSQL, object storage, worker). 아래는 **제안 기본값**이며 확정은 Open Questions(§7) 참조.

| Scope | Library (제안) | Note |
|-------|---------|------|
| Auth | 자체 세션 (Magic Link + HttpOnly/Secure/SameSite=Lax 쿠키) — Auth.js(Email Provider) 채택 여부는 결정 필요 | session·user(role 포함)는 서버에서 조회, 클라이언트에는 최소 정보만. admin 판정은 항상 DB role 컬럼 기준 |
| Form | react-hook-form + zod (제안) | `/login`(이메일), `/upload`(제목), ShareLinkModal(만료·비밀번호·maxViews), DeleteReasonModal(사유), PasswordGate |
| Server data | TanStack Query (제안) | 목록 커서 페이지네이션(`useInfiniteQuery`), 문서 상세, scanStatus·DOCX 변환 폴링(`refetchInterval`), 뮤테이션 후 invalidate |
| UI state | React Context/useState 로컬 우선, 필요 시 zustand (제안) | modal 개폐, toast 큐, 모바일 필터 바텀 시트 — 전역 스토어 최소화 |

## 4. Data Fetching Patterns

| Screen | API | Strategy |
|--------|-----|----------|
| `/login` | `POST /api/v1/auth/login`, `POST /api/v1/auth/verify` | mutation. 발송 성공 시 로컬 상태로 완료 화면 전환(계정 열거 방지 — 응답 동일). verify는 Magic Link 랜딩 시 1회 mutation 후 `/` 리다이렉트 |
| `/` (문서 목록) | `GET /api/v1/documents?q&uploaderId&from&to&cursor&limit=20` | query + filter + cursor pagination (`useInfiniteQuery`, nextCursor). 필터 변경 시 쿼리 키 갱신, URL 검색 파라미터 동기화 |
| `/upload` | `POST /api/v1/documents` (multipart) | mutation + 업로드 진행률(onUploadProgress). 성공(201) 시 문서 목록 캐시 invalidate 후 `/docs/{id}` 이동 |
| `/docs/{id}` | `GET /api/v1/documents/{id}` / `GET .../download` / `POST .../share-links` / `DELETE /api/v1/share-links/{linkId}` / `DELETE /api/v1/documents/{id}` | 상세 query — `scanStatus=pending`이면 polling(제안 3~5s, 완료 시 중단). 다운로드·링크 생성·폐기·삭제는 mutation 후 상세 invalidate. 토큰 원문은 캐시에 저장하지 않고 모달 로컬 상태로만 유지 |
| `/s/{token}` | `GET /api/v1/share/{token}` (+ `X-Share-Password` 헤더) | query (세션 불필요). DOCX 변환 중이면 polling(≤20s 예상, 제안 2~3s), viewUrl/downloadUrl 5분 만료 — 만료 시 재요청으로 재발급. 401 PASSWORD_REQUIRED → PasswordGate 후 재시도. 에러 응답은 메타데이터 미포함 전제로 렌더 |
| `/admin` | `GET /api/v1/admin/documents?status&q&uploaderId&from&to&cursor` / `DELETE /api/v1/documents/{id}` (reason 필수) / `POST /api/v1/admin/documents/{id}/restore` | query + filter + cursor pagination. 삭제·복원 mutation 후 목록 invalidate + Toast |
| `/admin/audit` | `GET /api/v1/admin/audit-logs?documentId&actorId&action&from&to&cursor` | query + filter + cursor pagination (조회 전용 — 뮤테이션 없음) |

## 5. Routing

```
app/
├── page.tsx                      # / (문서 목록) — member, admin
├── login/page.tsx                # /login — Magic Link 요청·발송 완료 (verify 처리 포함 여부는 §7)
├── upload/page.tsx               # /upload — member, admin
├── docs/[id]/page.tsx            # /docs/{id} 문서 상세 — member, admin
├── s/[token]/page.tsx            # /s/{token} 공유 열람 — 무인증(토큰), 최소 크롬 전용 레이아웃
├── admin/
│   ├── page.tsx                  # /admin 전체 문서 — admin only, Desktop only
│   └── audit/page.tsx            # /admin/audit 감사 로그 — admin only, Desktop only
└── api/                          # /api/v1/* API Routes (auth, documents, share-links, share, admin)
```

Auth middleware: `middleware.ts` — **`/login`과 `/s/*`(및 `/api/v1/auth/*`, `/api/v1/share/*`)를 제외한 전체 라우트**에서 세션 쿠키 검증. 미인증 → `/login` 리다이렉트. `/admin*`은 추가로 DB role 검증(admin 아니면 `/` 리다이렉트 + 토스트 "관리자만 접근할 수 있습니다"). 클라이언트 role 값은 신뢰하지 않는다.

`/s/[token]` 보안 헤더 (필수):
- `<meta name="robots" content="noindex, nofollow">` + `X-Robots-Tag: noindex` — 검색엔진 색인 차단
- `Referrer-Policy: no-referrer` — 토큰의 Referer 유출 방지
- 뷰어 렌더링 CSP 적용, 전역 네비·breadcrumb·footer 미노출(별도 layout)

## 6. Suggested Implementation Order

Task Plan(`docs/todo_plan/PLAN_internal-doc-sharing.md`)에 반영할 순서 — PRD §6 Phase 1~3 정렬:

1. **Phase 1: MVP (PRD Phase 1)**
   - 프로젝트 부트스트랩 (Next.js + 스타일 + 공통 컴포넌트 셸)
   - 인증: 도메인 화이트리스트 + Magic Link + 세션 쿠키 + `middleware.ts` (FR-001, `/login`)
   - DB 스키마·마이그레이션 + RLS 정책 (users / documents / share_links / audit_logs)
   - 업로드: 이중 검증 + 쿼터 + 진행률 (FR-002, `/upload`)
   - 문서 목록/상세/다운로드 (FR-003, FR-004, `/` + `/docs/{id}`)
   - 공유 링크 생성: CSPRNG 토큰 + 해시 저장 + 1회 노출 모달 (FR-005)
   - 공유 열람 `/s/{token}` + noindex/no-referrer 헤더 + 최소 크롬 (FR-006)
   - 링크 무효화 3경로 (만료·폐기·문서 삭제) + 통합 테스트 (FR-007)
   - 본인 문서 삭제 (FR-008)
   - 관리자 전체 문서 조회 + 사유 필수 강제 삭제 + `/` 삭제 배지 (FR-009, `/admin`)
   - 감사 로그 기록 (FR-010, 전 API 핸들러)

2. **Phase 2: Enhancement (PRD Phase 2)**
   - 감사 로그 조회 UI (FR-011, `/admin/audit`)
   - 공유 링크 비밀번호 / 최대 열람 횟수 + PasswordGate (FR-012)
   - 백그라운드 악성코드 스캔 + 격리 + 409 공유 게이트 + scanStatus 폴링 (FR-013)
   - 공유 엔드포인트 IP 레이트 리밋 + `rate_limit_warn` 로깅 + 429 화면 (FR-014)
   - DOCX → PDF 변환 워커 + "변환 중" 폴링 UI

3. **Phase 3: Operations (PRD Phase 3)**
   - 관리자 문서 복원 (30일 보존) (FR-015)
   - 보존 정책 + 만료 자동 정리 배치 + 물리 삭제 배치 (FR-016)
   - 모니터링·백업 자동화, 부하 테스트(50 RPS)·p95 SLA 검증

4. **Phase 4: Polish**
   - 반응형 마무리 (모바일 카드 목록·바텀 시트 필터·전체 화면 시트 모달, `/admin*` DesktopOnlyGuard)
   - 에러/빈 상태 마이크로카피 전수 반영 (03-SCREEN-SPEC States 기준)
   - 권한 로직 단위 테스트 커버리지 90% (소유자 검사·토큰 유효성·admin 판정)

## 7. Open Questions Carried Over

01-IA / 02-USER-FLOW / 03-SCREEN-SPEC에서 결정되지 않은 항목 통합(중복 제거):

- [ ] `/` "나의 문서" 구분 방식 — 탭 분리 vs 목록 내 배지 (현 명세는 배지 방식 가정) (01-IA, 03-SCREEN-SPEC)
- [ ] `/admin`·`/admin/audit` 모바일 접속 처리 — 안내 화면 vs 강제 리다이렉트 (현 명세는 안내 화면 가정) (01-IA)
- [ ] 공유 링크 생성 UI — `/docs/{id}` 내 모달 vs 인라인 패널 (현 명세는 모달 가정) (01-IA)
- [ ] 세션 만료(401) 공통 처리 — 전 화면 `/login` 리다이렉트 + "다시 로그인해주세요" 토스트로 통일 여부 (02-USER-FLOW)
- [ ] DOCX "변환 중" 처리 — 폴링(주기 포함) vs 수동 새로고침 안내 (02-USER-FLOW; §4는 폴링 2~3s 제안)
- [ ] 격리(quarantined) 문서의 업로더 알림 채널 — 이메일 vs 화면 내 배너 (02-USER-FLOW)
- [ ] Magic Link 검증 페이지 — `/auth/verify` 별도 화면 vs `/login` 내 상태 처리 (03-SCREEN-SPEC)
- [ ] 링크 목록 URL 표시 — 원문 재조회 불가(해시 저장)이므로 URL 열 마스킹 + "복사 시점에만 노출" 확정 (03-SCREEN-SPEC)
- [ ] 감사 로그 CSV 내보내기 — v1 범위 밖(BI 통계 제외)으로 확정 여부 (03-SCREEN-SPEC)
- [ ] 라이브러리 확정 — Auth(자체 세션 vs Auth.js Email Provider), Server data(TanStack Query vs SWR), Form(react-hook-form + zod), UI state(zustand 필요 여부), 레이트 리밋 스토어(메모리 vs Redis), 악성코드 스캔 엔진(ClamAV 등), DOCX→PDF 변환기(LibreOffice headless 등) (§3·§4 제안 기반)

**규칙**: 이 질문들은 `/implement` 진행 중 즉시 결정하거나, 결정 보류 시 코드 주석으로 TODO 표시.

## 8. Acceptance Mapping for /implement

`/implement`가 PRD Acceptance Criteria(§2.2)를 task로 분해할 때 참조:

| Scenario | Implementation Tasks |
|----------|---------------------|
| Scenario 1 — 사내 팀원 문서 업로드 성공 (25MB PDF → `/docs/{id}` 이동, `/`에 "나의 문서" 표시) | FR-001(세션), FR-002(업로드+검증), FR-003(목록+MyDocBadge), FR-004(상세) tasks |
| Scenario 2 — 위장 실행 파일 거부 (400 INVALID_FILE_TYPE + 안내 문구) | FR-002(서버 매직 넘버 검증 + ErrorInline "PDF 또는 DOCX 파일만 업로드할 수 있습니다") tasks |
| Scenario 3 — 공유 링크 생성 (7일 만료, `/s/{token}` URL + 복사 버튼 + 만료 일시) | FR-005(CSPRNG 토큰·해시 저장·ShareLinkModal·TokenRevealPanel·CopyButton) tasks |
| Scenario 4 — 외부인 링크 열람 (무로그인 뷰어 렌더 + 열람 감사 로그) | FR-006(ShareViewer), FR-010(view 이벤트: 토큰·시각·IP·UA) tasks |
| Scenario 5 — 만료 링크 차단 (410 LINK_EXPIRED, 메타데이터 미노출) | FR-007(만료 검증 + ErrorFullPage — 파일명·내용 미노출) tasks |
| Scenario 6 — 관리자 강제 삭제 (사유 입력 → soft delete + 링크 즉시 무효화 → 404 + 감사 로그) | FR-009(DeleteReasonModal + 강제 삭제), FR-007(링크 일괄 무효화), FR-010(delete 로그: 관리자 ID·사유·시각) tasks |
| Scenario 7 — 타인 문서 삭제 403 (DELETE 직접 호출 차단) | FR-008(서버 측 소유자 검사 403 FORBIDDEN — 클라이언트 값 불신뢰) tasks |

## 9. Interview Decisions (선택, `--interview` 플래그 사용 시)

N/A — `--interview` 플래그 미사용. 추론 모드(inference mode)로 생성되어 UI 의사결정(네비게이션 top 패턴, 삭제 사유 모달, 배지 방식 등)은 01-IA/03-SCREEN-SPEC의 가정을 따르며, 보류 항목은 §7 Open Questions에 기록했다.
