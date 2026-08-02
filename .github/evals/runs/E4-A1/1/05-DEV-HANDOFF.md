# Dev Handoff — internal-doc-sharing (사내 문서 공유 서비스)

> **Generated from**: 01-IA.md + 02-USER-FLOW.md + 03-SCREEN-SPEC.md + 04-WIREFRAME.html
> **Target**: `/implement internal-doc-sharing`
> **Created**: 2026-07-26
> **Platform**: web (Next.js SSR + API Routes — PRD §5.3)

## 1. FR ↔ Screen ↔ Component Mapping

우선순위는 PRD §3의 P0(Must) / P1(Should) / P2(Could)를 그대로 인용한다.
백엔드 전용 FR(FR-010, FR-014, FR-016)은 Screens를 `- (backend)`로 표기하되 backend task를 함께 명시하고, FE 표면이 있는 경우 비고로 연결한다.

| FR | Priority | Description | Screens | Components | Estimated Tasks |
|----|----------|------------|---------|-----------|----------------|
| FR-001 | P0 | 사내 이메일 도메인 화이트리스트 Magic Link 로그인/로그아웃 | `/login` | LoginCard, MagicLinkSentCard, ResendButton | BE: `POST /auth/login`(도메인 화이트리스트 + 계정 열거 방지 동일 응답), `POST /auth/verify`(15분 토큰 → 세션 쿠키 HttpOnly+Secure+SameSite=Lax), 로그아웃 / FE: 이메일 폼 + 발송 완료 화면 + 410 TOKEN_EXPIRED 복귀 처리 |
| FR-002 | P0 | PDF/DOCX 업로드 (≤50MB, 확장자+매직 넘버 이중 검증, 5GB 쿼터) | `/upload` | UploadDropzone, UploadProgress, TitleInput | BE: `POST /documents`(multipart, 매직 넘버 검증, 쿼터 검사, 파일명 정규화, 비공개 버킷 저장) / FE: 드롭존 클라이언트 선검증 + 진행률 바 + 400/413/507 inline 에러 |
| FR-003 | P0 | 문서 목록 조회 + 파일명/업로더/기간 필터 + 20건 커서 페이지네이션 | `/` | FilterBar, DocumentTable(카드 전환), LoadMoreButton, EmptyState | BE: `GET /documents`(q/uploaderId/from·to/cursor) / FE: 필터 바 + 테이블/카드 반응형 + "더 보기" + empty 2종(0건/필터 0건) |
| FR-004 | P0 | 문서 상세 조회 + 원본 다운로드 (presigned URL 5분) | `/docs/{id}` | DocumentMetaPanel, DownloadButton, ScanStatusBadge | BE: `GET /documents/{id}`(공유 링크 목록은 소유자/admin만), `GET /documents/{id}/download`(presigned 5분, 409/423 분기) / FE: 메타 표시 + 다운로드 버튼 활성 조건(scanStatus=clean) |
| FR-005 | P0 | 공유 링크 생성 (CSPRNG 128bit+, 해시 저장, 기본 7일·최대 90일) | `/docs/{id}` | ShareLinkPanel, ShareLinkCreateModal, ShareLinkCopyOnceModal | BE: `POST /documents/{id}/share-links`(CSPRNG 토큰 생성, SHA-256 해시만 저장, 원문 1회 응답) / FE: 만료일 select(1~90) + 생성 직후 1회 노출 모달 + 클립보드 복사 |
| FR-006 | P0 | 로그인 없는 공유 열람 (PDF 인라인, DOCX→PDF 변환 렌더) + 다운로드 | `/s/{token}` | ShareViewerBar, PdfViewer, ConvertingNotice, DownloadButton | BE: `GET /share/{token}`(단일 문서만, viewUrl/downloadUrl 5분) + DOCX→PDF 변환 워커 / FE: 최소 크롬 뷰어 + "변환 중" loading + 만료 일시 캡션 |
| FR-007 | P0 | 링크 무효화 3경로(만료·폐기·문서 삭제) + 무효 시 메타데이터 비노출 | `/s/{token}`, `/docs/{id}` | ShareErrorScreen(404/410 공용), LinkRevokeButton | BE: 토큰 검증 함수(해시 일치+미폐기+미만료+열람 횟수), `DELETE /share-links/{linkId}`, 문서 삭제 시 연쇄 무효화 / FE: 404/410 에러 화면(제목·파일명·업로더 비노출) + 폐기 확인 다이얼로그. 통합 테스트 필수(PRD §4.6) |
| FR-008 | P0 | 본인 문서 soft delete + 링크 연쇄 무효화 | `/docs/{id}` | DeleteButton(danger), ConfirmDialog | BE: `DELETE /documents/{id}` 서버 측 소유자 검사(403 FORBIDDEN — Scenario 7) / FE: 타인 문서 버튼 미노출 + 삭제 확인("링크 {n}개 즉시 무효화") + 완료 후 `/` 이동 |
| FR-009 | P0 | admin 전체 문서 조회 + 사유 필수 강제 삭제 + 업로더 화면 "관리자에 의해 삭제됨" 표시 | `/admin` (표시: `/`, `/docs/{id}`) | AdminDocumentTable, StatusBadge, AdminDeleteReasonModal | BE: `GET /admin/documents`(status 필터), `DELETE /documents/{id}` reason 필수(400 REASON_REQUIRED) / FE: 상태 배지(active/deleted/quarantined) + 사유 모달(1~500자) + 업로더 화면 삭제 배너/배지 |
| FR-010 | P0 | 감사 로그 기록 (업로드/링크 생성·폐기/열람/다운로드/삭제 — 액터·액션·문서·시각·IP·UA) | - (backend) | (FE 표면: `/admin/audit`의 AuditLogTable이 표시 스키마 사용) | BE: append-only `audit_logs` 기록 미들웨어/헬퍼(actor_type user·share_token·system), 각 이벤트 지점 삽입, 수정·삭제 API 미제공(PRD §4.5). 표시는 FR-011에서 커버 |
| FR-011 | P1 | admin 감사 로그 문서별·기간별 조회 | `/admin/audit` | AuditFilterBar, AuditLogTable, LoadMoreButton | BE: `GET /admin/audit-logs`(documentId/actorId/action/from·to/cursor) / FE: 액션 배지 8종 + rate_limit_warn 행 강조 + UA 말줄임 tooltip |
| FR-012 | P1 | 공유 링크 접근 제한 옵션 — 열람 비밀번호(≥8자) / 최대 열람 횟수 | `/docs/{id}`, `/s/{token}` | PasswordInput·MaxViewsInput(생성 모달 내), SharePasswordForm | BE: password_hash(bcrypt/argon2) 저장, `X-Share-Password` 검증(401/403), max_views 초과 시 410 VIEW_LIMIT_EXCEEDED / FE: 생성 모달 옵션 필드 + 열람 측 비밀번호 폼(no-permission 상태) |
| FR-013 | P1 | 백그라운드 악성코드 스캔 + 격리 + 스캔 완료 전 공유 차단 | `/upload`, `/docs/{id}` | ScanStatusBadge, QuarantineBanner | BE: 스캔 워커(pending→clean/infected), 감염 시 status=quarantined + 업로더·관리자 알림, 공유 생성 409 SCAN_IN_PROGRESS / FE: "검사 중" 배지 + 공유 버튼 비활성 + 423 격리 배너 |
| FR-014 | P1 | 공유 엔드포인트 IP 레이트 리밋(분당 30회) + 초과 시 감사 로그 경고 | - (backend) | (FE 표면: `/s/{token}`의 429 error 상태 — ShareErrorScreen) | BE: `/api/v1/share/{token}` IP 기준 분당 30회 리밋, 초과 시 429 RATE_LIMITED + `rate_limit_warn` 감사 로그 / FE: 429 안내 화면("잠시 후 다시 시도") |
| FR-015 | P2 | admin 삭제 문서 30일 내 복원 (링크는 무효 유지) | `/admin` | RestoreButton, ConfirmDialog | BE: `POST /admin/documents/{id}/restore`(30일 초과 시 410 RETENTION_EXPIRED) / FE: deleted 행 조건부 "복원" 버튼 + "링크는 되살아나지 않습니다" 안내 |
| FR-016 | P2 | 문서 보존 정책(기본 1년) + 만료 문서 배치 자동 정리 | - (backend) | (v1 FE 표면 없음 — 01-IA.md §2 확인) | BE: `documents.expires_at` 지정 로직 + 만료 도래 문서 정리 배치(soft delete 30일 후 물리 삭제 포함), 배치 실행 감사 로그(actor_type=system) |

### Coverage Check

- 모든 FR 매핑 여부: ✓ (FR-001~FR-016, 16/16 — P0 10건, P1 4건, P2 2건)
- 모든 화면이 1+ FR 연결 여부: ✓ (`/login`=FR-001, `/`=FR-003·009, `/upload`=FR-002·013, `/docs/{id}`=FR-004·005·008·012·013, `/s/{token}`=FR-006·007·012·014, `/admin`=FR-009·015, `/admin/audit`=FR-010·011 — 고아 페이지 없음)
- 매핑 누락 FR: 없음 (FR-010·014·016은 backend-only로 명시 매핑, FE 표면은 각각 `/admin/audit` 표시 / `/s/{token}` 429 상태 / 없음)

## 2. Component Inventory

### Reusable (다른 기능에서도 재사용 가능)

- `AppTopBar` — 로그인 후 Primary Navigation (Logo / 문서 목록 / 업로드 / 관리(admin만) / 사용자·로그아웃). `/s/{token}`에서는 미렌더링
- `FilterBar` — 검색 input + 업로더 combobox + 기간 date-range 조합 (`/`, `/admin`, `/admin/audit` 공용)
- `DateRangePicker` — from ≤ to 검증 포함
- `DataTable` / `CardList` — Desktop 테이블 ↔ Mobile 카드 전환 목록 프리미티브
- `LoadMoreButton` — nextCursor 존재 시에만 렌더되는 커서 페이지네이션 버튼
- `EmptyState` — 아이콘 + 문구 + CTA 슬롯
- `ErrorBanner` — 상단 배너 + "다시 시도" 버튼
- `ConfirmDialog` — 삭제/폐기 등 파괴적 액션 확인
- `Toast` — 성공/에러 알림
- `StatusBadge` — active/deleted/quarantined, scanStatus, 액션 배지 등 variant 기반
- `SkeletonRows` — 테이블/메타 스켈레톤
- `CopyButton` — 클립보드 복사 + 복사됨 피드백
- `ProgressBar` — aria-valuenow 갱신 업로드 진행률
- `DesktopOnlyGuard` — <1024px에서 "관리 화면은 PC에서 접속해 주세요." 안내 (`/admin`, `/admin/audit`)
- `useBreakpoint` — Desktop ≥1024 / Tablet 768~1023 / Mobile <768 분기 hook
- `useSession` — 세션 사용자·role 조회 hook (서버 판정 값만 신뢰)

### Feature-specific

- `LoginCard` / `MagicLinkSentCard` — 이메일 입력 카드 / 발송 완료 안내(60초 쿨다운 재발송)
- `UploadDropzone` — accept=".pdf,.docx" + ≤50MB 클라이언트 선검증 드래그&드롭 존
- `DocumentMetaPanel` — 제목·파일명·크기·업로더·업로드일·열람 수
- `ShareLinkPanel` — 공유 링크 목록(마스킹 URL, 만료일, 열람 수, 폐기) — 소유자/admin만 렌더
- `ShareLinkCreateModal` — expiresInDays(1~90) + password(≥8자) + maxViews(≥1) 폼
- `ShareLinkCopyOnceModal` — 토큰 원문 1회 노출 + "이 링크는 지금만 복사할 수 있습니다."
- `PdfViewer` — PDF 인라인 렌더(iframe/canvas), viewUrl 5분 만료 대응
- `ConvertingNotice` — DOCX 변환 중 loading + 완료 후 자동 렌더
- `SharePasswordForm` — 공유 열람 비밀번호 입력 카드 (401/403 처리)
- `ShareErrorScreen` — 404/410/423/429 공용 에러 화면 (문서 메타데이터 일절 비노출)
- `AdminDocumentTable` — 상태 배지 + 행 액션(삭제/복원) 테이블
- `AdminDeleteReasonModal` — 삭제 사유 textarea(1~500자) 필수 검증
- `AuditLogTable` — 시각/액션 배지/액터/문서 링크/IP/UA 6열

## 3. State Management

> 아래 라이브러리는 **제안 기본값**이다. 프로젝트에 기존 표준이 있으면 그것을 따른다(오버라이드 가능).

| Scope | Library (제안) | Note |
|-------|---------------|------|
| Auth | 자체 Magic Link + 세션 쿠키 (HttpOnly + Secure + SameSite=Lax) — PRD §4.5 | 클라이언트는 `GET /me`류 세션 조회로 user·role 파생. role 판정은 항상 서버(DB role 컬럼) |
| Form | react-hook-form + zod | `/login`(email), `/upload`(file·title), 공유 링크 생성 모달(expiresInDays·password·maxViews), 삭제 사유 모달(reason 1~500자) |
| Server data | TanStack Query | `/`·`/admin`·`/admin/audit` 커서 기반 `useInfiniteQuery`, `/docs/{id}` 상세 query + 삭제/공유 mutation 후 invalidate, `/s/{token}` 변환 중 폴링(refetchInterval) |
| UI state | zustand 또는 React Context (경량이므로 Context로 충분) | 모달 open/close, 토스트 큐, 업로드 진행률, 모바일 필터 bottom sheet |

## 4. Data Fetching Patterns

| Screen | API | Strategy |
|--------|-----|----------|
| `/login` | `POST /api/v1/auth/login`, `POST /api/v1/auth/verify` | mutation (발송 → 성공 화면 전환), verify는 메일 링크 콜백에서 mutation → 세션 쿠키 수신 후 `/` 이동 |
| `/` | `GET /api/v1/documents` | query + filter(q/uploaderId/from·to) + cursor pagination (20건, "더 보기") |
| `/upload` | `POST /api/v1/documents` | upload with progress (multipart/form-data, 진행률 이벤트 + 취소) → 성공 시 `/docs/{id}` 이동 |
| `/docs/{id}` | `GET /api/v1/documents/{id}` / `GET .../download` / `POST .../share-links` / `DELETE /api/v1/share-links/{linkId}` / `DELETE /api/v1/documents/{id}` | query (scanStatus=pending이면 폴링) / on-demand mutation(presigned URL 수신 즉시 사용) / mutation → 상세 invalidate / mutation / mutation → `/` 이동 |
| `/s/{token}` | `GET /api/v1/share/{token}` (`X-Share-Password` 헤더) | query (변환 중이면 재시도 폴링, viewUrl 5분 만료 시 재발급) — 401/403은 비밀번호 폼 상태로 분기 |
| `/admin` | `GET /api/v1/admin/documents` / `DELETE /api/v1/documents/{id}` (reason) / `POST /api/v1/admin/documents/{id}/restore` | query + filter(status 포함) + cursor pagination / mutation → 목록 invalidate / mutation → 목록 invalidate |
| `/admin/audit` | `GET /api/v1/admin/audit-logs` | query + filter(documentId/actorId/action/from·to) + cursor pagination |

## 5. Routing

Next.js App Router 기준(PRD §5.3: Next.js SSR + API Routes):

```
app/
├── layout.tsx                      # 루트 레이아웃 (AppTopBar는 인증 그룹에서만)
├── page.tsx                        # /            문서 목록 (member, admin)
├── login/page.tsx                  # /login       Magic Link 로그인
├── auth/verify/page.tsx            # Magic Link 콜백 → POST /auth/verify → 세션 발급
├── upload/page.tsx                 # /upload      업로드
├── docs/[id]/page.tsx              # /docs/{id}   문서 상세
├── s/[token]/page.tsx              # /s/{token}   공유 열람 — 사내 네비게이션 미렌더링
├── admin/
│   ├── page.tsx                    # /admin       전체 문서 (Desktop only)
│   └── audit/page.tsx              # /admin/audit 감사 로그 (Desktop only)
└── api/v1/                         # API Routes (auth, documents, share-links, share, admin)
middleware.ts
```

Auth middleware: `middleware.ts` — `/login`과 `/s/[token]`(및 `/auth/verify`, `/api/v1/auth/*`, `/api/v1/share/*`)을 제외한 **모든 라우트**를 세션 쿠키로 보호. 미인증 시 `/login` 리다이렉트. `/admin/*`는 추가로 DB role=admin 판정(파라미터·헤더 승격 불가), member 접근 시 no-permission 안내 후 `/` 리다이렉트.

`/s/[token]` 응답 헤더(PRD §4.5 필수):
- `<meta name="robots" content="noindex, nofollow">` + `X-Robots-Tag: noindex` — 검색엔진 색인 차단
- `Referrer-Policy: no-referrer` — 외부 링크 클릭 시 토큰 Referer 유출 방지

## 6. Suggested Implementation Order

Task Plan(`docs/todo_plan/PLAN_internal-doc-sharing.md`)에 반영할 순서 — PRD §6 Phase(MVP FR-001~010 → P1 → P2)를 따른다:

1. **Phase 1: Foundation (PRD §6 Phase 1 전반부)**
   - 프로젝트 부트스트랩 (Next.js + 스타일 시스템)
   - PostgreSQL 스키마 마이그레이션 + RLS 정책 (users / documents / share_links / audit_logs — PRD §5.2)
   - 오브젝트 스토리지 비공개 버킷 + presigned URL 유틸
   - Magic Link 인증 + 도메인 화이트리스트 + 세션 쿠키 + `middleware.ts` (FR-001)
   - 감사 로그 기록 헬퍼 — append-only (FR-010, 이후 모든 이벤트 지점에서 사용)

2. **Phase 2: member Path (PRD §6 Phase 1 — MVP 핵심)**
   - `/upload` 업로드 + 이중 검증 + 쿼터 (FR-002)
   - `/` 문서 목록 + 필터 + 커서 페이지네이션 (FR-003)
   - `/docs/{id}` 상세 + 다운로드 (FR-004)
   - 공유 링크 생성 — CSPRNG 토큰 + 해시 저장 + 1회 노출 모달 (FR-005)
   - `/s/{token}` 공유 열람 + noindex/no-referrer 헤더 (FR-006)
   - 링크 무효화 3경로 + 본인 문서 삭제 (FR-007, FR-008) — 통합 테스트 포함

3. **Phase 3: admin Path (PRD §6 Phase 1 마무리)**
   - `/admin` 전체 문서 조회 + 사유 필수 강제 삭제 + 업로더 화면 삭제 표시 (FR-009)
   - `/admin/audit` 감사 로그 조회 UI (FR-011 — P1이지만 FR-010 검증 수단으로 조기 착수 권장)

4. **Phase 4: Polish + P1/P2 (PRD §6 Phase 2·3)**
   - 공유 링크 비밀번호 / 최대 열람 횟수 (FR-012)
   - 악성코드 스캔 워커 + 격리 + 공유 차단, DOCX→PDF 변환 파이프라인 + "변환 중" UI (FR-013)
   - 공유 엔드포인트 IP 레이트 리밋 + 429 화면 + 경고 로깅 (FR-014)
   - 관리자 문서 복원 30일 (FR-015), 보존 정책 + 만료 정리 배치 (FR-016)
   - 반응형 마무리(모바일 카드/bottom sheet/Desktop only 가드), 에러/빈 상태 마이크로카피 정합, 권한 로직 단위 테스트 90%+ (PRD §4.6)

## 7. Open Questions Carried Over

01-IA / 02-USER-FLOW / 03-SCREEN-SPEC에서 결정되지 않은 항목 통합(중복 제거):

**01-IA.md**
- [ ] 업로드 진입점 — `/upload` 별도 페이지 유지 vs `/` 상단 모달 (v1은 PRD §5.4대로 별도 페이지로 명세)
- [ ] `/admin`·`/admin/audit`는 Desktop only (PRD §5.4) — 모바일 접속 시 "PC에서 접속하세요" 안내로 처리할지 확정
- [ ] `/docs/{id}`에서 본인 문서의 "관리자에 의해 삭제됨" 상태(FR-009) 노출 위치 — 목록 배지 vs 상세 배너 (양쪽 모두로 명세)

**02-USER-FLOW.md**
- [ ] 세션 만료(쿠키 만료) 시 처리 — 모든 보호 라우트에서 `/login?next={route}` 리다이렉트로 통일할지
- [ ] DOCX "변환 중" 상태에서 guest 폴링 주기 (수동 새로고침 vs 자동 폴링)
- [ ] 관리자 강제 삭제 시 업로더 알림 채널 — v1은 화면 내 상태 표시만인지, 이메일 알림 포함인지 (PRD Flow C의 Notify 노드)

**03-SCREEN-SPEC.md**
- [ ] 로그인 후 리다이렉트: 항상 `/`인지, 진입 시도했던 보호 라우트(`?next=`)로 복귀인지 (세션 만료 처리 항목과 함께 결정 권장)
- [ ] "나의 문서" 우선 정렬 vs 전체 최신순 (v1은 전체 최신순으로 명세)
- [ ] 업로드 중 페이지 이탈 시 확인 다이얼로그 여부
- [ ] 공유 링크 URL 마스킹 표기 (생성 이후에는 해시만 있으므로 `…/s/ab12…` 프리픽스 표시 방식)
- [ ] viewUrl(5분) 만료 시 재발급 UX — 무중단 자동 갱신 vs "다시 불러오기" 버튼
- [ ] 격리(quarantined) 문서에 대한 관리자 액션 범위 — v1은 조회·삭제만인지, 격리 해제가 필요한지
- [ ] 로그 CSV 내보내기 필요 여부 (PRD 범위 밖 — v2 후보)

**규칙**: 이 질문들은 `/implement` 진행 중 즉시 결정하거나, 결정 보류 시 코드 주석으로 TODO 표시.

## 8. Acceptance Mapping for /implement

`/implement`가 PRD Acceptance Criteria(§2.2)를 task로 분해할 때 참조:

| Scenario | Implementation Tasks |
|----------|---------------------|
| Scenario 1: 팀원 문서 업로드 성공 → `/docs/{id}` 이동 + 목록 "나의 문서" 표시 | FR-001(세션), FR-002(업로드 201), FR-003(목록 표시), FR-004(상세 이동) tasks |
| Scenario 2: 위장 실행 파일 업로드 거부 (400 INVALID_FILE_TYPE) | FR-002(서버 매직 넘버 검증 + inline 에러 "PDF 또는 DOCX 파일만 업로드할 수 있습니다.") tasks |
| Scenario 3: 공유 링크 생성 (만료 7일, 토큰 URL + 복사 버튼 + 만료 일시 표시) | FR-005(CSPRNG 토큰 + 1회 노출 모달 + 복사), FR-013(scanStatus=clean 게이트 — 409) tasks |
| Scenario 4: 외부인 링크 열람 + 열람 이벤트 감사 로그 기록 | FR-006(비로그인 뷰어 렌더), FR-010(view 이벤트 — token_id·시각·IP·UA) tasks |
| Scenario 5: 만료 링크 차단 (410 LINK_EXPIRED, 메타데이터 비노출) | FR-007(만료 검증 + ShareErrorScreen — 제목·파일명 비노출) tasks |
| Scenario 6: 관리자 강제 삭제 → 링크 즉시 무효화 → 404 + 감사 로그 | FR-009(사유 필수 soft delete), FR-007(전체 링크 연쇄 무효화 → 404), FR-010(delete 이벤트 — 관리자 ID·사유·시각) tasks |
| Scenario 7: 타인 문서 삭제 403 FORBIDDEN | FR-008(서버 측 소유자 검사 — 클라이언트 role 불신, 403 응답 + 문서 미삭제 검증 테스트) tasks |
