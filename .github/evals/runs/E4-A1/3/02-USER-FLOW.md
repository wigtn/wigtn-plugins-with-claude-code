# User Flow — internal-document-sharing (사내 문서 공유 서비스)

> **Generated from**: input-prd.md §5.5 (Flow A/B/C 확장 — 분기 조건 명시)
> **Created**: 2026-07-26
> **Status**: Draft

> **Mermaid 룰**: 라우트(`/`)/특수문자(`?`, `=`, `:`)를 포함하는 노드 텍스트는 항상 `["..."]` 큰따옴표로 감싼다. valid한 shape만 사용: `[]` `()` `(())` `{}` `[(...)]`. `{(...)}`는 존재하지 않는다.

## Flow A: member — 로그인 → 업로드 → 공유 링크 생성

> Acceptance Criteria 매핑: Scenario 1(업로드 성공), Scenario 2(파일 형식 거부), Scenario 3(공유 링크 생성), Scenario 7(타인 문서 삭제 403)

```mermaid
flowchart TD
  Start([팀원 진입]) --> Login["/login"]
  Login -->|이메일 입력| Domain{"허용 도메인? (화이트리스트)"}
  Domain -->|No — 403 DOMAIN_NOT_ALLOWED| NoPerm[no-permission 안내]
  Domain -->|Yes| Mail["Magic Link 발송 ({ sent: true })"]
  Mail -->|링크 클릭 15분 내| Verify{토큰 검증}
  Verify -->|410 TOKEN_EXPIRED| Login
  Verify -->|200 + 세션 쿠키| List["/ (문서 목록)"]
  List -->|업로드 버튼| Upload["/upload"]
  Upload -->|파일 선택| Validate{"형식·크기 검증 (PDF/DOCX, ≤50MB, 매직 넘버)"}
  Validate -->|"FAIL — 400 INVALID_FILE_TYPE / 413 FILE_TOO_LARGE / 507 QUOTA_EXCEEDED"| Upload
  Validate -->|PASS — 201| Detail["/docs/{id} 상세"]
  Detail --> ScanChk{"scanStatus?"}
  ScanChk -->|pending| ScanWait["'검사 중' 배지 — 공유 링크 생성 차단 (409 SCAN_IN_PROGRESS)"]
  ScanChk -->|infected| Quarantine[격리 안내 + 업로더·관리자 알림]
  ScanChk -->|clean| MakeLink["공유 링크 만들기 (만료일 기본 7일·최대 90일, 비밀번호·열람 한도 옵션)"]
  MakeLink -->|"201 — 토큰 원문 1회 노출"| Copy["/s/{token} URL 클립보드 복사 → 외부 전달"]
  Detail -->|삭제 버튼| Owner{"소유자 확인 (서버 측 uploader_id 검사)"}
  Owner -->|FAIL — 403 FORBIDDEN| NoPerm
  Owner -->|PASS| Revoke[("문서 soft delete + 전체 공유 링크 즉시 무효화")]
  Revoke --> List
```

## Flow B: guest — 공유 링크 열람

> Acceptance Criteria 매핑: Scenario 4(외부인 열람), Scenario 5(만료 링크 차단)

```mermaid
flowchart TD
  S([링크 클릭 — 비로그인 guest]) --> Rate{"IP 레이트 리밋 (분당 30회)"}
  Rate -->|초과 — 429 RATE_LIMITED| TooMany[잠시 후 재시도 안내]
  Rate -->|통과| Token{토큰 유효?}
  Token -->|"없음/폐기 — 404 LINK_NOT_FOUND"| NotFound["404 안내 (문서 메타데이터 미노출)"]
  Token -->|"만료 — 410 LINK_EXPIRED"| Expired["만료 안내 (문서 정보 미노출)"]
  Token -->|"열람 초과 — 410 VIEW_LIMIT_EXCEEDED"| Limit[열람 한도 초과 안내]
  Token -->|"격리 — 423 DOCUMENT_QUARANTINED"| Blocked[열람 불가 안내]
  Token -->|유효| Pw{비밀번호 설정됨?}
  Pw -->|"Yes — 401 PASSWORD_REQUIRED"| Input[비밀번호 입력 폼]
  Input -->|"틀림 — 403 PASSWORD_INCORRECT"| Input
  Input -->|맞음| View["문서 뷰어 렌더링 (PDF 인라인 / DOCX 변환본)"]
  Pw -->|No| View
  View --> Log[("열람 감사 로그 기록 + view_count 증가")]
  View -->|다운로드 버튼| Presign["5분 presigned URL 발급 → 다운로드"]
```

## Flow C: admin — 전체 문서 관리·강제 삭제·복원

> Acceptance Criteria 매핑: Scenario 6(관리자 강제 삭제)

```mermaid
flowchart TD
  A([admin 로그인]) --> Adm{"role = admin? (DB role 컬럼 판정)"}
  Adm -->|No — 403 FORBIDDEN| NoPerm2["no-permission — / 리다이렉트 + 토스트"]
  Adm -->|Yes| All["/admin (전체 문서: active·deleted·quarantined)"]
  All -->|필터: 상태·업로더·기간| Pick[문서 선택]
  Pick -->|부적절 판단| Reason["삭제 사유 입력 (필수, ≤500자)"]
  Reason -->|"사유 누락 — 400 REASON_REQUIRED"| Reason
  Reason -->|확인| Force[("강제 soft delete + 전체 링크 즉시 무효화 → 이후 링크 접근 404")]
  Force --> Notify["업로더에게 알림 + 감사 로그 기록 (관리자 ID·사유·시각)"]
  All -->|감사 로그 메뉴| Audit["/admin/audit (문서별·기간별 조회)"]
  All -->|삭제 문서 선택| Restore{"30일 보존 기간 내?"}
  Restore -->|"경과 — 410 RETENTION_EXPIRED"| Gone[복원 불가 안내]
  Restore -->|Yes| Back[("문서 복원 — 공유 링크는 무효 유지, 재발급 필요")]
```

## Flow Coverage Check

| Acceptance Criteria (PRD §2.2) | Flow |
|--------------------|------|
| Scenario 1 — 사내 팀원이 문서를 업로드한다 | Flow A |
| Scenario 2 — 허용되지 않은 파일 형식 업로드를 거부한다 | Flow A (Validate FAIL 분기) |
| Scenario 3 — 공유 링크를 생성한다 | Flow A (MakeLink) |
| Scenario 4 — 외부인이 링크로 문서를 열람한다 | Flow B |
| Scenario 5 — 만료된 링크는 열람할 수 없다 | Flow B (Expired 분기) |
| Scenario 6 — 관리자가 부적절한 문서를 삭제한다 | Flow C |
| Scenario 7 — 다른 팀원의 문서는 삭제할 수 없다 | Flow A (Owner FAIL 분기) |

**규칙**:
- 모든 Acceptance Criteria가 1+ Flow에 매핑되어야 함 — ✓ 7/7 매핑 완료
- 매핑되지 않는 시나리오 → Flow를 추가하거나 시나리오가 모호
- 모든 Flow 내 페이지(`/login`, `/`, `/upload`, `/docs/{id}`, `/s/{token}`, `/admin`, `/admin/audit`)는 01-IA.md 페이지와 1:1 매칭 — ✓

## Branch Conditions Reference

| 분기 노드 | 조건 | 처리 |
|----------|------|------|
| 허용 도메인 | 이메일 도메인 ∈ 화이트리스트 | Magic Link 발송 / 403 DOMAIN_NOT_ALLOWED |
| Magic Link 토큰 검증 | 발급 후 15분 이내 + 유효 토큰 | 세션 발급 / 400 INVALID_TOKEN·410 TOKEN_EXPIRED |
| 형식·크기 검증 | 확장자 + 매직 넘버 일치, ≤50MB, 쿼터 ≤5GB | 201 / 400·413·507 |
| scanStatus | `pending` \| `clean` \| `infected` | 공유 차단 / 허용 / 격리 |
| 소유자 확인 | `uploader_id = current_user_id` 또는 `admin` (서버 측 검사) | 삭제 진행 / 403 FORBIDDEN |
| IP 레이트 리밋 | 분당 30회 이하 | 통과 / 429 RATE_LIMITED |
| 토큰 유효성 | 해시 일치 + 미폐기 + 미만료 + 열람 한도 내 | 뷰어 / 404·410·423 |
| 공유 비밀번호 | `password_hash` 존재 시 입력 일치 | 뷰어 / 401·403 |
| admin 판정 | DB `users.role = 'admin'` (요청 파라미터로 승격 불가) | `/admin` 진입 / `/` 리다이렉트 |
| 복원 보존 기간 | soft delete 후 30일 이내 | 복원 / 410 RETENTION_EXPIRED |

## Open Questions

- [ ] 세션 만료 시 어디서 분기되는가? — 보호 라우트 접근 시 `/login` 리다이렉트 + "세션이 만료되었습니다" 안내로 가정
- [ ] 업로드 중 페이지 이탈 시 업로드 취소 확인 다이얼로그 필요 여부
- [ ] DOCX 변환 중(`변환 중` 상태) `/s/{token}` 접근 시 폴링 vs 수동 새로고침
