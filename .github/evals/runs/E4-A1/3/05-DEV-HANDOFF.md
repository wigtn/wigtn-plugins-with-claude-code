# Dev Handoff — internal-document-sharing (사내 문서 공유 서비스)

> **Generated from**: 01-IA.md + 02-USER-FLOW.md + 03-SCREEN-SPEC.md + 04-WIREFRAME.html
> **Target**: `/implement internal-document-sharing`
> **Created**: 2026-07-26

## 1. FR ↔ Screen ↔ Component Mapping

| FR | Description | Screens | Components | Estimated Tasks |
|----|------------|---------|-----------|----------------|
| FR-001 | 사내 이메일 도메인 화이트리스트 + Magic Link 로그인/로그아웃 | `/login` | MagicLinkForm, ErrorBanner, Toast | 도메인 화이트리스트 검증, `POST /auth/login`·`POST /auth/verify` 연동, 세션 쿠키(HttpOnly+Secure+SameSite=Lax) 발급, 429 재발송 제한 UI |
| FR-002 | PDF/DOCX 업로드 (≤50MB, 확장자+매직 넘버 이중 검증, 5GB 쿼터) | `/upload` | FileDropzone, UploadProgress, ErrorBanner, Toast | 드롭존+클라이언트 사전 검사, multipart 업로드+진행률, 서버 매직 넘버 검증(백엔드), 400/413/507 inline 에러 처리 |
| FR-003 | 조직 문서 목록 조회 + 파일명/업로더/기간 필터 + 20건 페이지네이션 | `/` | DocumentTable, DocumentCardList(모바일), FilterBar, DateRangePicker, SkeletonTable, EmptyState, ErrorBanner | `GET /documents` 커서 페이지네이션, 필터 쿼리 동기화, "나의 문서" 배지, 반응형 테이블↔카드 전환 |
| FR-004 | 문서 상세 조회 + 원본 다운로드 (presigned URL) | `/docs/{id}` | 메타 패널, StatusBadge(scanStatus), CopyButton | `GET /documents/{id}`, `GET /documents/{id}/download`(5분 presigned), 404/409/423 분기 |
| FR-005 | 공유 링크 생성 (CSPRNG 토큰, 만료 기본 7일·최대 90일) | `/docs/{id}` | ShareLinkCreateModal, ShareLinkList, CopyButton, Toast | `POST /documents/{id}/share-links`, 토큰 원문 1회 노출 모달, 만료일 select 검증(1~90) |
| FR-006 | guest 링크 열람 (로그인 없음, 브라우저 뷰어 + 다운로드) | `/s/{token}` | PdfViewer, 상단 얇은 바, 하단 고정 다운로드 바(모바일) | `GET /share/{token}`, viewUrl/downloadUrl 5분 만료 처리, DOCX "변환 중" 안내, noindex/no-referrer 헤더 |
| FR-007 | 링크 무효화 3경로 (만료·폐기·문서 삭제) 즉시 반영, 메타데이터 미노출 | `/docs/{id}` (폐기), `/s/{token}` (차단 안내) | ShareLinkList(폐기 버튼), ConfirmDialog, 오류 전용 화면 | `DELETE /share-links/{linkId}`, 404/410 오류 화면(문서 정보 미노출), 통합 테스트(3경로) |
| FR-008 | 본인 문서 삭제 (soft delete + 전체 링크 무효화) | `/docs/{id}` | ConfirmDialog(무효화 링크 수 고지), Toast | `DELETE /documents/{id}`, 서버 측 소유자 검사, 삭제 후 `/` 이동 + 토스트 |
| FR-009 | admin 전체 문서 조회 + 사유 필수 강제 삭제 | `/admin` (+ `/docs/{id}`의 "관리자에 의해 삭제됨" 표시) | AdminDocumentTable, StatusBadge(deleted=red/quarantined=amber), DeleteReasonModal, Toast | `GET /admin/documents` 상태 필터, 삭제 사유 모달(≤500자, 400 REASON_REQUIRED), 업로더 알림 |
| FR-010 | 감사 로그 기록 (append-only) | **API/Backend 전용** — 기록은 서버 책임 (조회 UI는 `/admin/audit`) | - | 이벤트 훅(업로드/링크 생성·폐기/열람/다운로드/삭제), 액터·IP·UA 수집, append-only 보장(UPDATE/DELETE 미제공) |
| FR-011 | admin 감사 로그 문서별·기간별 조회 | `/admin/audit` | AuditLogTable, FilterBar, DateRangePicker, SkeletonTable, EmptyState | `GET /admin/audit-logs` 커서 페이지네이션, 액션 enum 필터, rate_limit_warn amber 강조 |
| FR-012 | 공유 링크 접근 제한 옵션 (비밀번호, 최대 열람 횟수) | `/docs/{id}` (설정), `/s/{token}` (검사) | ShareLinkCreateModal(password·maxViews 필드), 비밀번호 입력 폼 | 비밀번호 8자 검증, `X-Share-Password` 헤더 전달, 401/403/410 VIEW_LIMIT_EXCEEDED 분기 |
| FR-013 | 백그라운드 악성코드 스캔 + 격리 + 알림 | **Backend 워커 전용** — FE는 `/upload`·`/docs/{id}`에서 scanStatus 표시만 | StatusBadge("검사 중" amber), 안내 문구 | 스캔 워커(백엔드), scanStatus polling, 스캔 완료 전 공유/다운로드 버튼 비활성(409 SCAN_IN_PROGRESS), 격리 시 423 안내 |
| FR-014 | 공유 엔드포인트 IP 레이트 리밋 (분당 30회) + 경고 로깅 | **Backend 전용** — FE는 `/s/{token}` 429 안내, `/admin/audit` rate_limit_warn 표시만 | ErrorBanner(429) | 레이트 리미터(백엔드), 429 응답 UI, rate_limit_warn 감사 로그 기록 |
| FR-015 | admin 삭제 문서 30일 내 복원 (링크는 무효 유지) | `/admin` | 복원 버튼(deleted 행), ConfirmDialog, Toast | `POST /admin/documents/{id}/restore`, 30일 경과 410 RETENTION_EXPIRED 안내, 복원 후 "링크 재발급 필요" 토스트 |
| FR-016 | 문서 보존 정책 (기본 1년) + 만료 배치 자동 정리 | **API/Backend 전용 — FE 화면 없음** | - | `expires_at` 정책 저장, 만료 문서 정리 배치(cron), soft delete 30일 후 물리 삭제 배치 |

### Coverage Check

- 모든 FR 매핑 여부: ✓ (FR-001~FR-016 16개 전부 — FR-010/013/014/016은 백엔드 전용 책임을 명시하고 FE 표시 지점을 함께 매핑)
- 모든 화면이 1+ FR 연결 여부: ✓ (7개 화면 모두 — `/login`=FR-001, `/`=FR-003, `/upload`=FR-002·013, `/docs/{id}`=FR-004·005·007·008·012, `/s/{token}`=FR-006·007·012·014, `/admin`=FR-009·015, `/admin/audit`=FR-010·011)
- 매핑 누락 FR: 없음

## 2. Component Inventory

### Reusable (다른 기능에서도 재사용 가능)

- FileDropzone — 드래그&드롭 + 파일 선택 (accept/최대 크기 prop)
- DocumentTable / DocumentCardList — 데스크톱 테이블 ↔ 모바일 카드 리스트 전환 목록
- FilterBar — 검색어·select·기간 필터 조합 컨테이너 (쿼리스트링 동기화)
- DateRangePicker — from/to ISO date, from ≤ to 검증
- ConfirmDialog — 파괴적 액션 확인 (삭제/폐기/복원 공용)
- Toast — success/error 알림 (전역 큐)
- StatusBadge — active(중립)/deleted(red)/quarantined(amber)/검사 중(amber)/clean(green)
- CopyButton — 클립보드 복사 + "복사되었습니다" 피드백
- SkeletonTable — 로딩 스켈레톤 (행 수 prop: 목록 5행, 감사 로그 8행)
- EmptyState — 안내 문구 + CTA 버튼 슬롯
- ErrorBanner — 상단 배너 (재시도 버튼 슬롯, red/amber variant)
- PdfViewer — PDF 인라인 렌더 (viewUrl 만료 시 재발급 요청)
- useBreakpoint — Desktop(≥1024)/Tablet(768~1023)/Mobile(<768) 분기 hook

### Feature-specific

- MagicLinkForm — 이메일 입력 + 발송/재발송 + 성공 확인 화면 (`/login`)
- UploadProgress — 진행률 바 + "업로드 중…" + "검사 중" 배지 (`/upload`)
- ShareLinkCreateModal — 만료 기간·비밀번호·최대 열람 횟수 + 토큰 1회 노출 결과 (`/docs/{id}`)
- ShareLinkList — 링크 행(URL 마스킹·만료일·열람 수·비밀번호 여부) + 폐기 (`/docs/{id}`)
- DeleteReasonModal — 삭제 사유 textarea(필수, ≤500자) + 삭제 확정 (`/admin`)
- AuditLogTable — 읽기 전용 로그 테이블 + rate_limit_warn amber 강조 (`/admin/audit`)
- SharePasswordForm — 열람 비밀번호 입력 폼 (`/s/{token}`, 문서 정보 미노출)

## 3. State Management

> 아래는 **제안**이며, 프로젝트 기존 컨벤션이 있으면 그것을 우선한다.

| Scope | Library | Note |
|-------|---------|------|
| Auth | 세션 쿠키 기반 — Next.js middleware + 서버 검증 (제안) | HttpOnly+Secure+SameSite=Lax 쿠키. 클라이언트는 user/role을 서버 응답으로만 수신, admin 판정은 DB role 컬럼 (PRD §4.5) |
| Form | react-hook-form + zod (제안) | `/login`(이메일), `/upload`(파일·제목), ShareLinkCreateModal(만료·비밀번호·maxViews), DeleteReasonModal(사유 ≤500자) |
| Server data | TanStack Query (제안) | `/`·`/admin`·`/admin/audit` 커서 페이지네이션(useInfiniteQuery), `/docs/{id}` 상세 + scanStatus polling, mutation 후 invalidate |
| UI state | zustand 또는 Context (제안) | 모달 열림 상태, 전역 Toast 큐, 모바일 필터 패널 접힘 |

## 4. Data Fetching Patterns

| Screen | API | Strategy |
|--------|-----|----------|
| `/login` | `POST /api/v1/auth/login`, `POST /api/v1/auth/verify` | mutation (발송 → 성공 확인 화면), verify는 콜백 진입 시 1회 mutation 후 `/` 리다이렉트. 429 시 재발송 버튼 잠금 |
| `/` | `GET /api/v1/documents` | query + filter(q/uploaderId/from/to) + cursor pagination (limit 20, "더 보기") |
| `/upload` | `POST /api/v1/documents` | mutation (multipart, onUploadProgress로 진행률), 201 → `/docs/{id}` 라우팅 + 토스트 |
| `/docs/{id}` | `GET /api/v1/documents/{id}` · `GET /api/v1/documents/{id}/download` · `POST /api/v1/documents/{id}/share-links` · `DELETE /api/v1/share-links/{linkId}` · `DELETE /api/v1/documents/{id}` | 상세 query (+ `scanStatus=pending`이면 polling, 예: 5s 간격 — Open Question 참조). 다운로드는 클릭 시 presigned URL 발급 mutation. 링크 생성/폐기/문서 삭제는 mutation + 상세 invalidate |
| `/s/{token}` | `GET /api/v1/share/{token}` | query (cache 없음, `X-Share-Password` 헤더 재시도). 401→비밀번호 폼, 403→inline 에러, 404/410/423/429→전용 오류 화면(메타데이터 미노출). viewUrl/downloadUrl 5분 만료 시 재요청 |
| `/admin` | `GET /api/v1/admin/documents` · `DELETE /api/v1/documents/{id}` · `POST /api/v1/admin/documents/{id}/restore` | query + status/q/uploaderId/from/to filter + cursor pagination. 강제 삭제(사유 포함)·복원은 mutation + 목록 invalidate |
| `/admin/audit` | `GET /api/v1/admin/audit-logs` | query + filter(documentId/actorId/action/from/to) + cursor pagination (읽기 전용) |

## 5. Routing

Next.js App Router 기준:

```
app/
├── page.tsx                    # / (문서 목록) — FR-003
├── login/page.tsx              # /login — FR-001
├── upload/page.tsx             # /upload — FR-002, FR-013(표시)
├── docs/[id]/page.tsx          # /docs/{id} — FR-004, FR-005, FR-008
├── s/[token]/page.tsx          # /s/{token} — FR-006, FR-007, FR-012, FR-014(표시) · 네비 없는 단독 레이아웃
├── admin/page.tsx              # /admin — FR-009, FR-015 · Desktop only
└── admin/audit/page.tsx        # /admin/audit — FR-010(조회), FR-011 · Desktop only
```

- Auth middleware: `middleware.ts` — **`/login`과 `/s/*`를 제외한 모든 라우트 보호** (미인증 → `/login` 리다이렉트). `/admin/*`은 추가로 DB role=admin 검증(서버 측 — 요청 파라미터·헤더로 승격 불가), 실패 시 `/` 리다이렉트 + "관리자만 접근할 수 있습니다" 토스트.
- `/s/[token]` 전용 헤더 (PRD §4.5): `<meta name="robots" content="noindex, nofollow">` + `X-Robots-Tag: noindex` + `Referrer-Policy: no-referrer`. 별도 레이아웃(네비게이션·Footer 미포함).
- 무효 토큰 응답은 상태 코드만 다르고 본문에 문서 메타데이터를 포함하지 않는다.

> **모바일(`--platform=mobile`)인 경우**: 해당 없음 — PRD §1.3에서 네이티브 앱은 Non-Goal, 반응형 웹으로 대응.

## 6. Suggested Implementation Order

Task Plan(`docs/todo_plan/PLAN_internal-document-sharing.md`)에 반영할 순서 — PRD §6 Phase 1–3과 정렬:

1. **Phase 1: MVP (PRD §6 Phase 1)**
   - 프로젝트 부트스트랩 (Next.js App Router + Tailwind) + DB 스키마·RLS (users/documents/share_links/audit_logs)
   - 인증: 도메인 화이트리스트 + Magic Link + 세션 쿠키 + middleware.ts → `/login` 화면 (FR-001)
   - 업로드: multipart + 확장자·매직 넘버 이중 검증 + 50MB/5GB 제한 → `/upload` 화면 (FR-002)
   - 문서 목록/상세/다운로드 → `/`, `/docs/{id}` 화면 (FR-003, FR-004)
   - 공유 링크 생성(CSPRNG 토큰·해시 저장·만료일) + ShareLinkCreateModal (FR-005)
   - 공유 열람 `/s/{token}` + noindex/no-referrer 헤더 + 단독 레이아웃 (FR-006)
   - 링크 무효화 3경로(만료·폐기·문서 삭제) + 본인 문서 삭제 (FR-007, FR-008) — 통합 테스트 필수 (PRD §4.6)
   - 관리자 전체 문서 조회 + 사유 필수 강제 삭제 → `/admin` 화면 (FR-009)
   - 감사 로그 기록 (append-only, 서버) (FR-010)

2. **Phase 2: Enhancement (PRD §6 Phase 2)**
   - 감사 로그 조회 UI → `/admin/audit` 화면 (FR-011)
   - 공유 링크 비밀번호 / 최대 열람 횟수 + `/s/{token}` 비밀번호 폼 (FR-012)
   - 백그라운드 악성코드 스캔 + 격리 + "검사 중" 배지·scanStatus polling (FR-013)
   - 공유 엔드포인트 IP 레이트 리밋 + rate_limit_warn 경고 로깅·amber 표시 (FR-014)
   - DOCX → PDF 변환 파이프라인 + "변환 중" 상태 UI

3. **Phase 3: Operations (PRD §6 Phase 3)**
   - 관리자 문서 복원(30일 보존) + 410 RETENTION_EXPIRED 처리 (FR-015)
   - 문서 보존 정책(기본 1년) + 만료 자동 정리 배치 (FR-016)
   - 업타임/에러 모니터링, 일 1회 백업 자동화
   - 부하 테스트(50 RPS) 및 p95 SLA 검증

4. **Phase 4: Polish**
   - 반응형 마무리 (테이블↔카드 전환, 모바일 하단 고정 다운로드 바)
   - 전 화면 loading/empty/error/no-permission 상태 검수 (§5.4.1 매트릭스 대조)
   - 접근성 점검 (label 연결, aria, 키보드 포커스)

## 7. Open Questions Carried Over

01-IA / 02-USER-FLOW / 03-SCREEN-SPEC에서 결정되지 않은 항목 통합:

- [ ] (01-IA) `/docs/{id}` 공유 링크 생성 UI — 인라인 패널 vs 모달 (03·04는 **모달**로 가정하고 작성됨)
- [ ] (01-IA) `/admin` 모바일 접근 처리 — PRD §5.4 Desktop only. 04는 "관리 기능은 PC 환경에서 이용해 주세요." 안내로 가정
- [ ] (01-IA) 관리자 강제 삭제된 본인 문서를 `/` 목록에 표시할지 여부 — 03·04는 `/docs/{id}` 직접 진입 시에만 "관리자에 의해 삭제됨" 안내로 가정
- [ ] (02-USER-FLOW) 세션 만료 분기 — 보호 라우트 접근 시 `/login` 리다이렉트 + "세션이 만료되었습니다" 안내로 가정
- [ ] (02-USER-FLOW) 업로드 중 페이지 이탈 시 취소 확인 다이얼로그 필요 여부
- [ ] (02-USER-FLOW) DOCX 변환 중 `/s/{token}` 접근 시 폴링 vs 수동 새로고침 (03은 "잠시 후 새로고침해 주세요" 문구로 수동 새로고침 가정)
- [ ] (03-SCREEN-SPEC) 격리(quarantined) 문서의 관리자 원본 확인 경로 제공 여부 (v1은 미제공 가정)

**규칙**: 이 질문들은 `/implement` 진행 중 즉시 결정하거나, 결정 보류 시 코드 주석으로 TODO 표시.

## 8. Acceptance Mapping for /implement

`/implement`가 PRD Acceptance Criteria(§2.2)를 task로 분해할 때 참조 (02-USER-FLOW Coverage 표 기준):

| Scenario | Flow | Implementation Tasks |
|----------|------|---------------------|
| Scenario 1 — 사내 팀원이 문서를 업로드한다 | Flow A | FR-001(로그인) + FR-002(업로드) + FR-003("나의 문서" 표시) + FR-004(상세 이동) tasks |
| Scenario 2 — 허용되지 않은 파일 형식 업로드를 거부한다 | Flow A (Validate FAIL) | FR-002 서버 매직 넘버 검증 + 400 INVALID_FILE_TYPE "PDF 또는 DOCX 파일만 업로드할 수 있습니다." inline 에러 tasks |
| Scenario 3 — 공유 링크를 생성한다 | Flow A (MakeLink) | FR-005(CSPRNG 토큰·만료 7일·URL 생성) + CopyButton·만료 일시 표시 + FR-013(스캔 완료 전 차단 409) tasks |
| Scenario 4 — 외부인이 링크로 문서를 열람한다 | Flow B | FR-006(무로그인 뷰어) + FR-010(열람 이벤트: 토큰·시각·IP·UA 감사 로그) tasks |
| Scenario 5 — 만료된 링크는 열람할 수 없다 | Flow B (Expired) | FR-007(410 LINK_EXPIRED + "이 링크는 만료되었습니다. 공유한 담당자에게 문의하세요." + 문서 메타데이터 미노출) tasks |
| Scenario 6 — 관리자가 부적절한 문서를 삭제한다 | Flow C | FR-009(사유 필수 강제 soft delete) + FR-007(전체 링크 즉시 무효화 → 404) + FR-010(관리자 ID·사유·시각 로그) tasks |
| Scenario 7 — 다른 팀원의 문서는 삭제할 수 없다 | Flow A (Owner FAIL) | FR-008 서버 측 소유자 검사(uploader_id) + 403 FORBIDDEN + no-permission amber 배너 tasks |

## 9. Interview Decisions

> **추론 모드** (`--interview` 미실시) — 03-SCREEN-SPEC.md 상단에 선언된 추론 기본값을 그대로 기록. `/implement` 시 프로젝트 컨벤션이 있으면 우선한다.

| 의사결정 | 선택 (추론 기본값) | 적용 화면 |
|---------|------|----------|
| 네비게이션 패턴 | top (로그인 후 상단 바 · `/s/{token}`은 네비 없음) | 전체 |
| 정보 밀도 | compact | `/` 문서 목록, `/admin`, `/admin/audit` 테이블 |
| 에러 톤 | 공식적 (코드·스택 미노출, 정중한 안내문) | 모든 에러 메시지 |
| 빈 상태 철학 | 최소 (문구 + CTA 버튼) | `/`, `/admin`, `/admin/audit` empty state |
| 전환 방식 | page 전환 기본 + **공유 링크 생성만 modal** | 폼/상세 전반, `/docs/{id}` ShareLinkCreateModal |
| 모바일 우선순위 | desktop-first (관리 화면은 Desktop only, 나머지 반응형) | 반응형 분기 전체 |
| 첫 화면 후크 | action (로그인 직후 문서 목록 + [문서 업로드] CTA) | `/` |
