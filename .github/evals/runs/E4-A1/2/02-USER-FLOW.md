# User Flow — internal-doc-sharing (사내 문서 공유)

> **Generated from**: input-prd.md §5.5
> **Created**: 2026-07-26
> **Status**: Draft

> **Mermaid 룰**: 라우트(`/`)/특수문자(`?`, `=`, `:`)를 포함하는 노드 텍스트는 항상 `["..."]` 큰따옴표로 감싼다. valid한 shape만 사용: `[]` `()` `(())` `{}` `[(...)]`. `{(...)}`는 존재하지 않는다.

## Flow A: member — 로그인 → 업로드 → 공유 → 삭제

> Acceptance Criteria 매핑: Scenario 1(업로드), 2(형식 거부), 3(링크 생성), 7(타인 문서 삭제 거부)

```mermaid
flowchart TD
  Start([팀원 진입]) --> Login["/login"]
  Login -->|이메일 입력| Domain{"허용 도메인? (화이트리스트)"}
  Domain -->|No: 403 DOMAIN_NOT_ALLOWED| NoPerm["no-permission 안내<br/>사내 이메일로만 로그인 가능"]
  NoPerm --> Login
  Domain -->|Yes| Mail["Magic Link 발송<br/>{ sent: true } — 계정 열거 방지 동일 응답"]
  Mail -->|링크 클릭, 15분 내| Verify{"토큰 검증"}
  Verify -->|410 TOKEN_EXPIRED| Login
  Verify -->|200 + 세션 쿠키| List["/ (문서 목록)"]
  List -->|업로드 버튼| Upload["/upload"]
  Upload -->|파일 선택| Validate{"클라 검증: 확장자 pdf/docx<br/>AND 크기 ≤ 50MB"}
  Validate -->|"FAIL: 형식/크기 오류 inline 표시"| Upload
  Validate -->|PASS → 업로드| Server{"서버 검증: 매직 넘버<br/>+ 용량 쿼터"}
  Server -->|400 INVALID_FILE_TYPE| Upload
  Server -->|413 FILE_TOO_LARGE| Upload
  Server -->|507 QUOTA_EXCEEDED| Upload
  Server -->|"201 (scanStatus: pending)"| Detail["/docs/{id} (상세)"]
  Detail --> ScanChk{"scanStatus?"}
  ScanChk -->|pending| ScanWait["'검사 중' 배지<br/>공유 버튼 비활성 (409 SCAN_IN_PROGRESS)"]
  ScanChk -->|infected| Quarantine["격리 안내 + 업로더·관리자 알림"]
  ScanChk -->|clean| MakeLink["공유 링크 만들기 모달<br/>만료일(기본 7·최대 90일)·비밀번호·최대 열람 횟수"]
  MakeLink -->|400 INVALID_EXPIRY| MakeLink
  MakeLink -->|"201: 토큰 원문 1회 노출"| Copy["URL 복사 + 만료 일시 표시<br/>→ 외부 전달"]
  Detail -->|삭제 버튼| Owner{"소유자 확인 (서버 측)"}
  Owner -->|"FAIL: 403 FORBIDDEN (타인 문서)"| NoPerm2["삭제 불가 안내<br/>(타인 문서엔 버튼 자체 미노출)"]
  Owner -->|PASS| Confirm["삭제 확인 다이얼로그"]
  Confirm -->|확인| SoftDel[("soft delete<br/>+ 전체 공유 링크 즉시 무효화")]
  SoftDel --> List
```

## Flow B: guest — 공유 링크 열람

> Acceptance Criteria 매핑: Scenario 4(외부 열람), 5(만료 링크)

```mermaid
flowchart TD
  S([공유 링크 클릭]) --> Rate{"IP 레이트 리밋<br/>분당 30회 이내?"}
  Rate -->|"초과: 429 RATE_LIMITED"| RateErr["잠시 후 다시 시도 안내<br/>+ 감사 로그 경고"]
  Rate -->|OK| Token{"토큰 유효?"}
  Token -->|"없음/폐기: 404 LINK_NOT_FOUND"| NotFound["문서를 찾을 수 없음 안내<br/>메타데이터 미노출"]
  Token -->|"만료: 410 LINK_EXPIRED"| Expired["만료 안내: 공유한 담당자에게 문의<br/>파일명·내용 미노출"]
  Token -->|"열람 초과: 410 VIEW_LIMIT_EXCEEDED"| Limit["열람 한도 초과 안내"]
  Token -->|"격리: 423 DOCUMENT_QUARANTINED"| Blocked["열람 불가 안내"]
  Token -->|유효| Pw{"비밀번호 설정됨?"}
  Pw -->|Yes| Input["비밀번호 입력 폼 (no-permission)"]
  Input -->|"403 PASSWORD_INCORRECT"| Input
  Input -->|맞음| ConvChk{"DOCX 변환 완료?"}
  Pw -->|No| ConvChk
  ConvChk -->|"변환 중 (≤20s)"| Converting["'변환 중' 상태 표시 → 폴링"]
  Converting --> ConvChk
  ConvChk -->|완료 또는 PDF 원본| View["문서 뷰어 렌더링<br/>(5분 만료 viewUrl)"]
  View --> Log[("열람 감사 로그 기록<br/>토큰·시각·IP·UA + view_count 증가")]
  View -->|다운로드 버튼| Presign["5분 presigned downloadUrl 발급"]
```

## Flow C: admin — 전체 문서 관리·강제 삭제·복원

> Acceptance Criteria 매핑: Scenario 6(관리자 강제 삭제)

```mermaid
flowchart TD
  A([admin 로그인 완료]) --> Adm{"role = admin?<br/>(DB role 컬럼 기준)"}
  Adm -->|"No: 403 FORBIDDEN"| NoPerm["no-permission<br/>/ 로 리다이렉트 + 토스트"]
  Adm -->|Yes| All["/admin (전체 문서: active·deleted·quarantined)"]
  All -->|"필터: 상태·업로더·기간·파일명"| Pick["문서 선택"]
  Pick -->|부적절 판단| Reason["삭제 사유 입력 (필수, ≤500자)"]
  Reason -->|"미입력: 400 REASON_REQUIRED"| Reason
  Reason -->|확인| Force[("강제 soft delete<br/>+ 전체 링크 즉시 무효화<br/>+ 감사 로그(관리자 ID·사유·시각)")]
  Force --> Notify["업로더 화면에 '관리자에 의해 삭제됨' 표시"]
  Force --> DeadLink["이후 해당 링크 접속 → 404 DOCUMENT_NOT_FOUND"]
  All -->|감사 로그 메뉴| Audit["/admin/audit"]
  Audit -->|"필터: 문서·액터·액션·기간"| AuditList["로그 목록 (append-only 조회 전용)"]
  All -->|삭제 문서 선택| RestoreChk{"30일 보존 기간 내?"}
  RestoreChk -->|"경과: 410 RETENTION_EXPIRED"| Gone["복원 불가 안내 (물리 삭제됨)"]
  RestoreChk -->|Yes| Restore["문서 복원<br/>공유 링크는 무효 유지 — 재발급 필요"]
```

## Flow Coverage Check

| Acceptance Criteria (§2.2) | Flow |
|--------------------|------|
| Scenario 1 — 문서 업로드 성공 | Flow A (Upload → Server 201 → Detail) |
| Scenario 2 — 위장 실행 파일 거부 | Flow A (Server → 400 INVALID_FILE_TYPE) |
| Scenario 3 — 공유 링크 생성 | Flow A (MakeLink → Copy) |
| Scenario 4 — 외부인 링크 열람 | Flow B (Token 유효 → View → Log) |
| Scenario 5 — 만료 링크 차단 | Flow B (Token → 410 Expired) |
| Scenario 6 — 관리자 강제 삭제 | Flow C (Reason → Force → DeadLink) |
| Scenario 7 — 타인 문서 삭제 403 | Flow A (Owner → FAIL 403) |

**규칙**: 모든 Acceptance Criteria가 1+ Flow에 매핑됨 ✓ (7/7)

## Branch Conditions Reference

| 분기 노드 | 조건 | 처리 |
|----------|------|------|
| 허용 도메인 | `email domain ∈ whitelist` | Magic Link 발송 / 403 DOMAIN_NOT_ALLOWED |
| Magic Link 토큰 | 발급 후 15분 이내 + 미사용 | 세션 발급 / 410 TOKEN_EXPIRED |
| 클라이언트 파일 검증 | 확장자 ∈ {pdf, docx} AND size ≤ 50MB | PASS / inline FAIL |
| 서버 파일 검증 | 매직 넘버 일치 AND 쿼터 ≤ 5GB | 201 / 400 · 413 · 507 |
| scanStatus | `pending` \| `clean` \| `infected` | 공유 차단 / 허용 / 격리 |
| 공유 토큰 | 해시 일치 AND 미폐기 AND 미만료 AND 열람 수 미초과 | 뷰어 / 404 · 410 · 410 · 423 |
| 공유 비밀번호 | `password_hash` 존재 시 검증 | 뷰어 / 401 PASSWORD_REQUIRED · 403 PASSWORD_INCORRECT |
| IP 레이트 리밋 | 분당 ≤ 30회 | 통과 / 429 RATE_LIMITED |
| 문서 소유자 | `uploader_id = current_user_id` OR `role = admin` | 삭제 허용 / 403 FORBIDDEN |
| admin 판정 | DB `users.role = 'admin'` (요청 파라미터 승격 불가) | `/admin*` 허용 / `/` 리다이렉트 |
| 복원 보존 기간 | `deleted_at + 30일 > now` | 복원 / 410 RETENTION_EXPIRED |

## Open Questions

- [ ] 세션 만료 시 분기 — 어느 페이지에서든 401 수신 시 `/login` 리다이렉트 + "다시 로그인해주세요" 토스트로 통일하는가?
- [ ] Flow B의 DOCX "변환 중" 폴링 주기 — 폴링 vs 수동 새로고침 안내 (PRD §4.1은 변환 ≤20s 비동기만 명시)
- [ ] 격리(quarantined) 문서의 업로더 알림 채널 — 이메일 vs 화면 내 배너 (FR-013 "알린다"의 채널 미지정)
