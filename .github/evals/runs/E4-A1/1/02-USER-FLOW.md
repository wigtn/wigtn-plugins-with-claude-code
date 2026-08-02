# User Flow — internal-doc-sharing (사내 문서 공유 서비스)

> **Generated from**: input-prd.md §5.5 (Flow A/B/C를 분기 조건까지 확장)
> **Created**: 2026-07-26
> **Status**: Draft

> **Mermaid 룰**: 라우트(`/`)/특수문자(`?`, `=`, `:`)를 포함하는 노드 텍스트는 항상 `["..."]` 큰따옴표로 감싼다. valid한 shape만 사용: `[]` `()` `(())` `{}` `[(...)]`.

## Flow A: member — 로그인 → 업로드 → 공유 링크 생성

> Acceptance Criteria 매핑: Scenario 1(업로드), 2(형식 거부), 3(링크 생성), 7(타인 문서 삭제 거부)

```mermaid
flowchart TD
  Start([팀원 진입]) --> Login["/login"]
  Login -->|이메일 입력| Domain{"허용 도메인? (화이트리스트)"}
  Domain -->|No → 403 DOMAIN_NOT_ALLOWED| NoPerm[no-permission 안내<br/>사내 이메일로만 로그인 가능]
  Domain -->|Yes → 200| Mail["Magic Link 발송 안내<br/>(계정 존재 여부 무관 동일 응답)"]
  Mail -->|메일 링크 클릭 /auth/verify| Verify{"토큰 유효? (15분 내)"}
  Verify -->|410 TOKEN_EXPIRED| Login
  Verify -->|200 + 세션 쿠키| List["/ (문서 목록)"]
  List -->|업로드 버튼| Upload["/upload"]
  Upload -->|파일 선택| CV{"클라이언트 검증<br/>확장자 pdf·docx AND ≤50MB"}
  CV -->|FAIL| Upload
  CV -->|PASS → POST /api/v1/documents| SV{서버 검증}
  SV -->|400 INVALID_FILE_TYPE 매직 넘버 불일치| Upload
  SV -->|413 FILE_TOO_LARGE| Upload
  SV -->|507 QUOTA_EXCEEDED 5GB 초과| Upload
  SV -->|201 scanStatus=pending| Detail["/docs/{id} (상세)<br/>검사 중 배지"]
  Detail -->|공유 링크 만들기| ScanOK{"scanStatus = clean?"}
  ScanOK -->|pending → 409 SCAN_IN_PROGRESS| Detail
  ScanOK -->|clean| MakeLink["만료일(기본 7일, 최대 90일)<br/>비밀번호·최대 열람 횟수 설정(옵션)"]
  MakeLink -->|201| Copy["URL /s/{token} 1회 표시<br/>클립보드 복사 → 외부 전달"]
  Detail -->|삭제 버튼| Own{"소유자 본인? (서버 검사)"}
  Own -->|No → 403 FORBIDDEN| Forbidden[삭제 불가 안내<br/>버튼 자체는 타인 문서에서 미노출]
  Own -->|Yes → 200| SoftDel[("soft delete<br/>+ 전체 공유 링크 즉시 무효화")]
  SoftDel --> List
```

## Flow B: guest — 공유 링크 열람

> Acceptance Criteria 매핑: Scenario 4(외부 열람), 5(만료 링크 차단)

```mermaid
flowchart TD
  S([외부인 링크 클릭]) --> Open["/s/{token} 접속 (로그인 불필요)"]
  Open --> Rate{"IP 분당 30회 이내?"}
  Rate -->|초과 → 429 RATE_LIMITED| TooMany[잠시 후 다시 시도 안내]
  Rate -->|OK| Token{토큰 유효?}
  Token -->|"없음/폐기 → 404 LINK_NOT_FOUND"| NotFound["404 안내<br/>문서 제목·파일명·업로더 미노출"]
  Token -->|"만료 → 410 LINK_EXPIRED"| Expired[만료 안내<br/>담당자에게 문의 유도]
  Token -->|"열람 초과 → 410 VIEW_LIMIT_EXCEEDED"| Limit[열람 한도 초과 안내]
  Token -->|"격리 → 423 DOCUMENT_QUARANTINED"| Quar[열람 불가 안내<br/>사유 미노출]
  Token -->|유효| Pw{비밀번호 설정됨?}
  Pw -->|Yes → 401 PASSWORD_REQUIRED| Input[비밀번호 입력 폼<br/>no-permission 상태]
  Input -->|"틀림 → 403 PASSWORD_INCORRECT"| Input
  Input -->|맞음| Render{"파일 형식?"}
  Pw -->|No| Render
  Render -->|PDF| View[인라인 PDF 뷰어]
  Render -->|"DOCX 변환 완료"| View
  Render -->|"DOCX 변환 중"| Converting["변환 중 안내 (loading)<br/>완료 후 자동 렌더"]
  Converting --> View
  View --> Log[("열람 감사 로그 기록<br/>token_id, 시각, IP, UA<br/>view_count 증가")]
  View -->|다운로드 버튼| Presign["5분 만료 presigned URL 발급"]
```

## Flow C: admin — 전체 문서 관리 · 강제 삭제 · 복원

> Acceptance Criteria 매핑: Scenario 6(부적절 문서 삭제)

```mermaid
flowchart TD
  A([admin 로그인]) --> Role{"role = admin? (DB role 컬럼 판정)"}
  Role -->|No| NoPerm2["no-permission 안내 후 / 리다이렉트"]
  Role -->|Yes| All["/admin (전체 문서: active·deleted·quarantined)"]
  All -->|"필터: 상태·업로더·기간·파일명"| Pick[문서 선택]
  Pick -->|부적절 판단 → 삭제| Reason{"삭제 사유 입력됨? (≤500자)"}
  Reason -->|"미입력 → 400 REASON_REQUIRED"| Pick
  Reason -->|입력 + 확인| Force[("강제 soft delete<br/>+ 전체 링크 즉시 무효화<br/>+ 감사 로그(관리자 ID·사유·시각)")]
  Force --> Notify[업로더 화면에 관리자에 의해 삭제됨 표시]
  All -->|감사 로그 메뉴| Audit["/admin/audit (문서별·기간별 조회)"]
  All -->|"deleted 문서 선택 → 복원"| Ret{"삭제 후 30일 이내?"}
  Ret -->|"초과 → 410 RETENTION_EXPIRED"| Gone[복원 불가 안내<br/>물리 삭제됨]
  Ret -->|이내 → 200| Restore[("문서 복원<br/>공유 링크는 무효 유지 → 재발급 필요")]
```

## Flow Coverage Check

| Acceptance Criteria (PRD §2.2) | Flow |
|--------------------|------|
| Scenario 1: 팀원 문서 업로드 성공 | Flow A (Upload → SV 201 → Detail) |
| Scenario 2: 위장 실행 파일 업로드 거부 | Flow A (SV → 400 INVALID_FILE_TYPE) |
| Scenario 3: 공유 링크 생성 (만료 7일) | Flow A (MakeLink → Copy) |
| Scenario 4: 외부인 링크 열람 + 감사 로그 | Flow B (View → Log) |
| Scenario 5: 만료 링크 차단 (410, 메타데이터 미노출) | Flow B (Token → Expired) |
| Scenario 6: 관리자 강제 삭제 + 링크 즉시 무효화 | Flow C (Reason → Force) |
| Scenario 7: 타인 문서 삭제 403 | Flow A (Own → Forbidden) |

- 모든 Acceptance Criteria가 1+ Flow에 매핑됨 ✓
- 모든 Flow 내 라우트가 01-IA.md 페이지와 일치함 ✓ (`/login`, `/`, `/upload`, `/docs/{id}`, `/s/{token}`, `/admin`, `/admin/audit`)

## Branch Conditions Reference

| 분기 노드 | 조건 | 처리 |
|----------|------|------|
| 허용 도메인 | `email.domain ∈ whitelist` | Magic Link 발송 / 403 DOMAIN_NOT_ALLOWED (no-permission) |
| Magic Link 토큰 | 발급 후 15분 이내 + 미사용 | 세션 발급 / 410 TOKEN_EXPIRED → 재요청 |
| 클라이언트 파일 검증 | 확장자 `.pdf`·`.docx` AND `size ≤ 50MB` | PASS / inline error |
| 서버 파일 검증 | 매직 넘버 일치 + 50MB + 쿼터 5GB | 201 / 400 / 413 / 507 |
| 스캔 상태 | `scanStatus === 'clean'` | 공유 링크 생성 허용 / 409 SCAN_IN_PROGRESS (버튼 비활성 + 안내) |
| 소유자 검사 | `document.uploader_id === session.user_id \|\| role === 'admin'` (서버 측) | 삭제 허용 / 403 FORBIDDEN |
| 공유 토큰 검증 | 해시 일치 + 미폐기 + 미만료 + 열람 횟수 미초과 | 뷰어 / 404 · 410 · 410 · 423 |
| 공유 비밀번호 | `password_hash` 존재 시 `X-Share-Password` 검증 | 뷰어 / 401 → 입력 폼 / 403 → 재입력 |
| 레이트 리밋 | IP 분당 ≤ 30회 | 통과 / 429 RATE_LIMITED |
| admin 판정 | DB `users.role = 'admin'` (요청 파라미터로 승격 불가) | `/admin` 허용 / no-permission → `/` 리다이렉트 |
| 복원 보존 기간 | `deleted_at + 30일 > now` | 복원 / 410 RETENTION_EXPIRED |

## Open Questions

- [ ] 세션 만료(쿠키 만료) 시 처리 — 모든 보호 라우트에서 `/login?next={route}` 리다이렉트로 통일할지
- [ ] DOCX "변환 중" 상태에서 guest 폴링 주기 (수동 새로고침 vs 자동 폴링)
- [ ] 관리자 강제 삭제 시 업로더 알림 채널 — v1은 화면 내 상태 표시만인지, 이메일 알림 포함인지 (PRD Flow C의 Notify 노드)
