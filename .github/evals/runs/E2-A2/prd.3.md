# PRD — 사내 문서 공유 서비스 (Internal Document Sharing)

## 1. Overview

### 1.1 Problem Statement

현재 팀은 문서(PDF/DOCX)를 공유할 때 이메일 첨부, 개인 메신저, 개인 클라우드 드라이브 링크를 혼용한다. 이로 인해 세 가지 문제가 발생한다.

1. **최신본 추적 불가** — 같은 문서의 여러 사본이 돌아다녀 어느 것이 최신인지 알 수 없다. 외부 미팅에서 구버전 자료가 공유되는 사고가 반복된다.
2. **외부 공유 통제 불가** — 외부인(고객사, 파트너, 지원자)에게 자료를 보내려면 개인 드라이브 링크를 쓰게 되는데, 이 링크는 회사가 회수·만료·감사할 수 없다. 퇴사자 계정에 자료가 남는 리스크도 있다.
3. **부적절 문서에 대한 대응 수단 부재** — 개인정보가 포함된 문서, 오배포된 계약서 등이 유통되어도 관리자가 즉시 차단할 방법이 없다.

즉 문제는 "파일을 올릴 곳이 없다"가 아니라 **"회사가 통제할 수 있는 외부 공유 경로가 없다"** 이다.

### 1.2 Goals

| # | Goal | 성공의 모습 |
|---|---|---|
| G1 | 팀원이 문서를 올리고 **회사가 소유한 링크**로 공유 | 개인 드라이브 링크 사용 건수 감소 |
| G2 | 링크를 받은 **외부인이 로그인 없이 열람** | 외부 수신자 이탈(열람 실패) 없이 조회 |
| G3 | 링크에 **만료·회수** 통제 부여 | 모든 외부 공유 링크가 만료 시각을 갖는다 |
| G4 | 관리자가 부적절 문서를 **즉시 차단** | 삭제 후 기존 링크가 즉시 무효화 |
| G5 | 누가 무엇을 언제 열람했는지 **감사 가능** | 문서별 열람 로그 조회 가능 |

### 1.3 Non-Goals

- **문서 편집·공동 작성** — 본 서비스는 뷰어/배포 채널이다. 편집은 기존 도구(Google Docs, MS Office)에서 한다.
- **문서 내 전문 검색(full-text search)** — v1은 파일명·업로더·태그 기준 목록만 제공. OCR/파싱 인덱싱은 후속.
- **버전 관리(diff, 롤백)** — 재업로드는 "새 문서"로 취급한다. 버전 트리는 Non-Goal.
- **DRM/워터마크/다운로드 방지** — 열람 가능한 문서는 캡처·저장이 가능하다는 전제로 설계한다. 기술적 유출 방지는 범위 밖이며, 통제는 "링크 만료 + 감사 로그"로만 한다.
- **외부인 계정 발급 / SSO 연동(외부 조직)** — 외부인은 어떤 경우에도 계정을 만들지 않는다.
- **모바일 네이티브 앱** — 반응형 웹으로만 대응.
- **PDF/DOCX 외 포맷** — XLSX, PPTX, 이미지, ZIP은 v1 미지원(업로드 거부).

### 1.4 Scope

**포함**
- 사내 계정(SSO/이메일) 로그인, 문서 업로드(PDF/DOCX, ≤50MB)
- 문서 목록/상세, 브라우저 내 열람(PDF 렌더링, DOCX는 PDF 변환 후 렌더링)
- 공유 링크 생성(만료 기한 필수, 선택적 비밀번호), 링크 회수
- 링크 소지자(비로그인) 열람 페이지
- 관리자 문서 삭제(soft delete) + 링크 즉시 무효화
- 열람 감사 로그(문서·링크·시각·IP·User-Agent)

**제외**
- 폴더 계층/권한 상속 (v1은 flat + 태그)
- 문서 단위 사내 세부 권한(특정 팀만 열람) — v1은 "사내 로그인 사용자 전원 열람 가능" 단일 정책
- 코멘트/승인 워크플로
- 외부 스토리지 마운트(S3 버킷 연결 등)

**경계에 대한 명시적 결정**: "사내용이지만 외부인도 링크로 열람"이라는 요구는 **인증(authentication)과 인가(authorization)를 분리**해 해소한다. 문서 리소스에 대한 접근권은 (a) 사내 세션 또는 (b) 유효한 공유 링크 토큰 중 **하나**로 증명한다. 토큰은 "익명 사용자에게 발급된 단일 리소스 한정 자격증명"이며, "인증 없음"이 아니다. 이 원칙이 §3, §4.5, §5.1 전체를 관통한다.

---

## 2. User Stories

### 2.1 Primary User

- **As a** 팀원(member), **I want to** PDF/DOCX를 업로드하고 만료 기한이 있는 공유 링크를 만들고 싶다 **so that** 개인 드라이브를 쓰지 않고도 외부에 자료를 전달하고 나중에 회수할 수 있다.
- **As a** 링크 수신 외부인(link_viewer), **I want to** 받은 링크를 클릭해서 로그인이나 가입 없이 바로 문서를 보고 싶다 **so that** 계정 만드느라 시간 낭비하지 않고 자료를 확인할 수 있다.
- **As a** 관리자(admin), **I want to** 부적절한 문서를 즉시 삭제하고 그 문서의 모든 링크를 무효화하고 싶다 **so that** 유출 사고가 났을 때 확산을 몇 분 안에 멈출 수 있다.
- **As a** 팀원(member), **I want to** 내 문서가 언제 누구(IP/시각)에게 열렸는지 보고 싶다 **so that** 상대가 자료를 확인했는지 알고 후속 조치를 할 수 있다.

### 2.2 Acceptance Criteria

```
Scenario: 팀원이 PDF를 업로드한다 (정상 경로)
  Given 사내 계정으로 로그인한 member 사용자가 있고
    And 업로드할 파일이 12MB PDF이다
  When /documents/new 에서 파일을 선택하고 업로드를 실행하면
  Then 문서가 저장되고 상태는 ready 가 되며
    And 문서 상세 페이지로 이동하고
    And 목록 최상단에 해당 문서가 나타난다
```

```
Scenario: 지원하지 않는 포맷 업로드 (검증 실패)
  Given 로그인한 member 사용자가 있고
  When 확장자가 .xlsx 인 파일을 업로드하면
  Then 서버는 415 Unsupported Media Type 을 반환하고
    And "PDF와 DOCX만 업로드할 수 있어요" 메시지가 표시되며
    And 파일은 저장되지 않는다
```

```
Scenario: 용량 초과 업로드 (검증 실패)
  Given 로그인한 member 사용자가 있고
  When 80MB 파일을 업로드하면
  Then 서버는 413 Payload Too Large 를 반환하고
    And "파일은 50MB까지 올릴 수 있어요" 메시지가 표시된다
```

```
Scenario: 확장자를 위조한 파일 업로드 (검증 실패)
  Given 로그인한 member 사용자가 있고
    And 실제 내용은 실행 파일이지만 이름이 report.pdf 인 파일이 있다
  When 해당 파일을 업로드하면
  Then 서버가 매직 넘버(content sniffing)로 실제 타입을 판별해 415 를 반환하고
    And 파일은 영구 저장소에 남지 않는다
```

```
Scenario: 만료 기한이 있는 공유 링크 생성 (정상 경로)
  Given 로그인한 member 가 자신이 업로드한 문서 상세에 있고
  When 만료 7일을 선택하고 링크 생성을 누르면
  Then 추측 불가능한 토큰이 포함된 URL 이 발급되고
    And 만료 시각(UTC)이 함께 표시되며
    And 클립보드 복사 버튼이 활성화된다
```

```
Scenario: 외부인이 유효한 링크로 열람 (정상 경로 · 비로그인)
  Given 만료되지 않았고 회수되지 않은 공유 링크가 있고
    And 사용자는 로그인하지 않았다
  When 해당 링크를 열면
  Then 로그인 화면으로 리다이렉트되지 않고
    And 문서 뷰어가 렌더링되며
    And 열람 이벤트(링크ID, 시각, IP, User-Agent)가 감사 로그에 기록된다
```

```
Scenario: 만료된 링크 열람 (만료)
  Given 만료 시각이 현재보다 과거인 공유 링크가 있고
  When 외부인이 해당 링크를 열면
  Then 서버는 410 Gone 을 반환하고
    And "이 링크는 만료되었어요. 보낸 사람에게 새 링크를 요청해 주세요" 안내가 표시되며
    And 문서의 어떤 내용(파일명, 미리보기, 크기)도 노출되지 않는다
```

```
Scenario: 회수된 링크 열람 (권한 박탈)
  Given member 가 공유 링크를 회수(revoke)했고
  When 외부인이 이전에 받은 그 링크를 열면
  Then 서버는 410 Gone 을 반환하고
    And 만료 안내와 동일한 화면이 표시된다 (회수 여부를 구분해 노출하지 않는다)
```

```
Scenario: 존재하지 않는/추측된 토큰 (권한 부족)
  Given 유효하지 않은 임의의 토큰 문자열이 있고
  When 해당 URL 로 접근하면
  Then 서버는 404 Not Found 를 반환하고
    And 응답 시간은 유효 토큰 처리와 유의미하게 다르지 않다 (존재 여부 오라클 방지)
```

```
Scenario: 비밀번호 보호 링크에 잘못된 비밀번호 입력 (권한 부족)
  Given 비밀번호가 설정된 공유 링크가 있고
  When 외부인이 틀린 비밀번호를 입력하면
  Then 401 이 반환되고 뷰어는 렌더링되지 않으며
    And 동일 링크·동일 IP 기준 10회 실패 시 15분간 429 로 차단된다
```

```
Scenario: 관리자가 부적절 문서를 삭제 (정상 경로)
  Given admin 으로 로그인했고
    And 대상 문서에 활성 공유 링크 3개가 있다
  When 문서 삭제를 실행하면
  Then 문서 상태는 deleted 가 되고
    And 3개 링크 모두 즉시 revoked 가 되며
    And 이후 그 링크 접근은 410 을 반환하고
    And 삭제 행위가 감사 로그에 (관리자ID, 시각, 사유) 로 기록된다
```

```
Scenario: 팀원이 남의 문서를 삭제 시도 (권한 부족)
  Given member 로 로그인했고
    And 대상 문서의 업로더는 다른 사용자이다
  When 삭제 API 를 직접 호출하면
  Then 서버는 403 Forbidden 을 반환하고
    And 문서 상태는 변하지 않으며
    And 실패한 인가 시도가 감사 로그에 기록된다
```

```
Scenario: 링크 소지자가 다른 문서로 이동 시도 (인가 경계)
  Given 유효한 공유 링크 토큰으로 문서 A 를 열람 중이고
  When 문서 B 의 ID 로 API 를 호출하면
  Then 서버는 404 를 반환한다 (토큰은 단일 문서에만 유효)
```

```
Scenario: 문서 목록 접근 시 비로그인 (인증 필요)
  Given 로그인하지 않은 사용자가 있고
  When /documents 에 접근하면
  Then 로그인 페이지로 리다이렉트된다
    And 공유 링크 경로(/s/{token})는 이 리다이렉트 규칙의 예외이다
```

```
Scenario: 변환 실패한 DOCX (에러)
  Given DOCX 업로드 후 PDF 변환이 실패했고
  When 업로더가 문서 상세를 열면
  Then 상태는 failed 로 표시되고
    And "미리보기를 만들지 못했어요. 원본 다운로드는 가능해요" 안내와 함께 원본 다운로드 버튼이 제공되며
    And 해당 문서로는 공유 링크를 생성할 수 없다 (버튼 비활성)
```

```
Scenario: 스토리지 장애 중 업로드 (장애)
  Given 오브젝트 스토리지가 응답하지 않고
  When member 가 업로드를 시도하면
  Then 503 이 반환되고
    And "지금은 업로드가 어려워요. 잠시 후 다시 시도해 주세요" 가 표시되며
    And 이미 발급된 링크의 열람은 계속 동작한다 (읽기 경로 격리)
```

### 2.3 User Roles

| Role Key | 한국어 명칭 | 권한 범위 |
|---|---|---|
| `admin` | 관리자 | member 권한 전부 + 모든 문서 조회/삭제, 모든 링크 회수, 전사 감사 로그 조회, 사용자 역할 변경 |
| `member` | 팀원(사내 인증 사용자) | 문서 업로드, 사내 문서 전체 목록/열람, **자신이 업로드한** 문서의 링크 생성·회수·삭제, 자신의 문서 감사 로그 조회 |
| `link_viewer` | 링크 소지 외부 열람자 | 계정 없음. 유효한 공유 링크 토큰이 가리키는 **단일 문서 1건**에 한해 열람(및 링크 설정이 허용할 때 다운로드). 목록·검색·업로드·삭제 불가 |

> 역할 판정 규칙: 세션 쿠키가 있으면 `admin` 또는 `member`, 없고 유효 토큰만 있으면 `link_viewer`, 둘 다 없으면 `anonymous`(어떤 문서 리소스에도 접근 불가). `link_viewer` 는 DB 사용자 레코드가 아니라 **요청 컨텍스트로만 존재**한다.

---

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|---|---|---|---|
| FR-001 | 사내 계정 로그인/로그아웃(이메일+OTP 또는 Google Workspace SSO). 세션은 HttpOnly·Secure·SameSite=Lax 쿠키 | P0 | — |
| FR-002 | 역할 모델 `admin`/`member` 저장 및 판정. 첫 가입자 또는 시드 계정이 `admin` | P0 | FR-001 |
| FR-003 | 문서 업로드: PDF/DOCX, 최대 50MB. 확장자와 **매직 넘버 양쪽** 검증, 불일치 시 415 | P0 | FR-001 |
| FR-004 | 업로드 파일은 오브젝트 스토리지에 저장하고 원본 파일명·크기·MIME·업로더·업로드 시각을 DB에 기록 | P0 | FR-003 |
| FR-005 | DOCX는 비동기 워커가 PDF로 변환. 상태 `processing → ready | failed`. 변환 실패해도 원본 다운로드는 가능 | P1 | FR-004 |
| FR-006 | 문서 목록: 로그인 사용자에게 사내 전체 문서 노출(삭제된 문서 제외), 최신순 커서 페이지네이션, 파일명·업로더 부분 일치 필터 | P0 | FR-001, FR-004 |
| FR-007 | 문서 상세 + 브라우저 내 뷰어(PDF 렌더링). 원본은 짧은 수명의 서명 URL로만 스트리밍 | P0 | FR-004 |
| FR-008 | 공유 링크 생성: 128비트 이상 CSPRNG 토큰, **만료 시각 필수**(1h/24h/7d/30d 중 선택, 최대 30일), 선택적 비밀번호, 선택적 다운로드 허용 여부 | P0 | FR-007 |
| FR-009 | 공유 링크 열람: `GET /s/{token}` 은 **세션 없이 접근 가능**하며, 토큰이 유효할 때만 해당 문서 1건을 반환 | P0 | FR-008 |
| FR-010 | 만료/회수/미존재 토큰 처리: 만료·회수는 410, 미존재는 404. 어느 경우에도 파일명·크기·업로더를 노출하지 않는다 | P0 | FR-009 |
| FR-011 | 링크 비밀번호 검증. 실패 10회/15분/(링크×IP) 초과 시 429 | P1 | FR-008 |
| FR-012 | 링크 회수(revoke): 업로더 또는 `admin` 이 즉시 무효화. 서명 URL 잔여 수명(≤5분) 이후 완전 차단 | P0 | FR-008 |
| FR-013 | 문서 삭제: `admin` 은 모든 문서, `member` 는 자신이 업로더인 문서만. soft delete(`deleted_at`) + 연결된 모든 링크 자동 revoke | P0 | FR-002, FR-012 |
| FR-014 | 삭제 시 사유(자유 입력, ≤200자) 기록. `admin` 삭제는 사유 필수 | P1 | FR-013 |
| FR-015 | 감사 로그 기록: 업로드, 링크 생성/회수, 열람(사내·외부 구분), 삭제, 인가 실패. 각 레코드에 actor(user_id 또는 token_id), 시각, IP, User-Agent | P0 | FR-004, FR-009 |
| FR-016 | 문서별 열람 로그 조회: 업로더는 자기 문서, `admin` 은 전체 | P1 | FR-015 |
| FR-017 | soft delete 문서는 보관 30일 후 배치가 스토리지 객체를 영구 삭제. 감사 로그는 남는다 | P1 | FR-013 |
| FR-018 | 관리자 콘솔: 전체 문서·활성 링크 목록, 삭제/회수 액션, 사용자 역할 변경 | P1 | FR-002, FR-013 |

**FR 무모순 검증 노트**

- FR-001(로그인 필요)과 FR-009(비로그인 열람)는 충돌하지 않는다. **인증 필수 범위는 `/documents/*` 이하이며, `/s/{token}` 은 명시적 예외**로 선언한다(§4.5, §5.1의 인가 주체 열에 동일하게 반영).
- FR-013(soft delete)과 FR-017(영구 삭제)의 순서: soft delete → 30일 → purge. FR-010의 410 응답은 purge 이후에도 동일하게 유지된다(링크 레코드는 남기고 파일만 지운다).
- FR-006의 "사내 전체 문서 노출"은 §1.4 제외 항목("문서 단위 사내 세부 권한")과 정합한다. 팀 단위 제한은 v1에 없다.
- FR-008의 만료 필수 정책 때문에 "무기한 링크"는 존재할 수 없다. G3와 일치.

---

## 4. Non-Functional Requirements

### 4.0 Scale Grade

**Startup** — 사내 임직원 30~150명(월 활성 member ≤150), 외부 링크 열람자 포함 피크 동시 접속 ≤80, 문서 누적 ≤50,000건 / 총 1.5TB, 일 업로드 ≤300건을 12개월 기준으로 가정한다. 단일 리전·관리형 DB·오브젝트 스토리지로 충분하며 샤딩·멀티리전은 불필요하다.

### 4.1 Performance

| 지표 | 목표 |
|---|---|
| 문서 목록 API (`GET /api/documents`, 50건) | p95 ≤ 300ms, p99 ≤ 700ms |
| 문서 메타 조회 (`GET /api/documents/{id}`) | p95 ≤ 200ms |
| 공유 링크 해석 (`GET /s/{token}` HTML 응답) | p95 ≤ 400ms, p99 ≤ 900ms |
| 뷰어 첫 페이지 렌더 (LCP, 10MB PDF, 유선 100Mbps) | p95 ≤ 2.5s |
| 업로드 처리량 (50MB 파일, 서버 수신 완료까지) | p95 ≤ 25s |
| DOCX→PDF 변환 완료 (10MB 기준) | p95 ≤ 60s, p99 ≤ 180s |
| 삭제/회수 반영 지연 | ≤ 5s (서명 URL TTL 5분은 별도 명시) |
| 처리량 | 정상 25 req/s, 피크 80 req/s 를 오류율 <0.5%로 처리 |
| 동시성 | 동시 업로드 10건, 동시 변환 워커 4개 |

### 4.2 Availability

- 월간 가용성 목표 **99.5%** (월 허용 다운타임 ≈ 3시간 39분). 사내 업무시간(09–19 KST) 기준 99.9%를 내부 목표로 별도 추적.
- **읽기/쓰기 경로 격리**: 스토리지 쓰기(업로드) 장애 시에도 기존 문서 열람과 공유 링크 해석은 계속 동작해야 한다(§2.2 스토리지 장애 시나리오).
- 변환 워커 장애 시: 문서는 `processing` 유지, 큐에 적재되어 복구 후 자동 재처리(최대 3회 재시도, 이후 `failed`).
- DB 장애 시: 읽기 전용 모드로 degrade — 목록·열람 가능, 업로드/링크 생성/삭제는 503 + 안내 배너.
- 배포는 무중단(롤링), 마이그레이션은 backward-compatible 2단계.

### 4.3 Data

| 데이터 | 보관 | 비고 |
|---|---|---|
| 문서 원본/변환본 | 활성 무기한, soft delete 후 **30일** → 영구 삭제(FR-017) | 스토리지 SSE 암호화 |
| 공유 링크 레코드 | 만료/회수 후 **90일** 보관 후 익명화(토큰 해시만 유지) | 만료 링크의 410 응답 근거 |
| 감사 로그(열람/삭제/인가실패) | **1년** | 문서가 지워져도 유지 |
| 세션 | 유휴 12시간, 절대 만료 7일 | |
| 접근 로그(웹서버) | 30일 | IP 마지막 옥텟 마스킹 |

**개인정보 관점**: 서비스가 직접 수집하는 개인정보는 (a) 사내 사용자의 이메일·이름, (b) 외부 열람자의 IP·User-Agent 이다. (b)는 감사 목적의 정당한 이익 근거로 1년 보관하며, 링크 열람 페이지 하단에 "열람 기록이 기록됩니다" 고지를 노출한다. 문서 **내용물** 안의 개인정보는 업로더 책임 영역이며, 서비스는 파싱·색인하지 않는다(§1.3 full-text search Non-Goal과 정합).

**삭제 정책**: 사용자 계정 삭제 시 업로드 문서는 자동 삭제하지 않고 `admin` 소유로 이관한다(업무 자산 유실 방지). 문서 단위 삭제 요청은 FR-013 경로를 따른다.

### 4.4 Recovery

- DB: 자동 일일 스냅샷 + PITR 7일. **RPO 15분 / RTO 2시간**.
- 오브젝트 스토리지: 버저닝 활성화 + 30일 소프트 삭제 보호. 실수 삭제 복구 가능(단, FR-017 purge는 의도된 영구 삭제이므로 버전까지 제거).
- 분기 1회 복구 리허설(스냅샷에서 스테이징 복원 후 문서 10건 열람 검증).
- 감사 로그는 append-only 테이블 + 일일 콜드 스토리지 export.

### 4.5 Security

**인증(Authentication)**
- 사내: Google Workspace OIDC(우선) 또는 이메일 매직링크. 비밀번호 저장 없음.
- 세션: HttpOnly·Secure·SameSite=Lax, 서버측 세션 스토어, 로그아웃 시 즉시 폐기.
- 외부: 계정 없음. 공유 토큰이 자격증명 역할을 한다.

**인가(Authorization) — 역할 × 리소스 매트릭스** (역할 키는 §2.3 그대로)

| 리소스 / 액션 | `admin` | `member` | `link_viewer` | `anonymous` |
|---|---|---|---|---|
| 문서 목록 조회 | ✅ 전체 | ✅ 전체(삭제 제외) | ❌ 404 | ❌ 302 → 로그인 |
| 문서 업로드 | ✅ | ✅ | ❌ 401 | ❌ 401 |
| 문서 상세/뷰어 | ✅ 전체 | ✅ 전체 | ✅ **토큰이 가리키는 1건만** | ❌ |
| 원본 다운로드 | ✅ | ✅ | ⚠️ 링크의 `allow_download=true` 일 때만 | ❌ |
| 공유 링크 생성 | ✅ 전체 문서 | ✅ 본인 업로드 문서만 | ❌ | ❌ |
| 공유 링크 회수 | ✅ 전체 | ✅ 본인 문서의 링크만 | ❌ | ❌ |
| 문서 삭제 | ✅ 전체 (사유 필수) | ✅ 본인 업로드 문서만 | ❌ 403 | ❌ 401 |
| 감사 로그 조회 | ✅ 전사 | ✅ 본인 문서만 | ❌ | ❌ |
| 역할 변경 | ✅ | ❌ 403 | ❌ | ❌ |

- **인가는 서버에서만 판정한다.** UI 버튼 숨김은 보조 수단이며 모든 API가 독립적으로 역할·소유권을 재검증한다(§2.2 "남의 문서 삭제 시도" 시나리오).
- **토큰 스코프**: 공유 토큰은 `document_id` 에 바인딩된다. 토큰으로 다른 문서 ID를 호출하면 404(§2.2 인가 경계 시나리오).

**토큰 설계**
- 32바이트 CSPRNG → base64url(43자). DB에는 **SHA-256 해시만** 저장(유출 시 원문 토큰 복원 불가).
- 토큰은 URL 경로에 위치하므로 Referer 유출 방지를 위해 링크 페이지에 `Referrer-Policy: no-referrer` 적용.
- 공유 페이지는 `X-Robots-Tag: noindex, nofollow` + `robots.txt` 차단으로 검색엔진 색인 방지.

**전송·저장 보호**
- 전 구간 TLS 1.2+, HSTS(max-age 1년, preload).
- 저장 시 오브젝트 스토리지 서버측 암호화(AES-256), DB 저장 암호화.
- 원본 파일은 공개 버킷에 두지 않는다. 항상 TTL ≤5분 서명 URL 경유.

**입력 검증**
- 파일: 확장자 화이트리스트(.pdf/.docx) + 매직 넘버 검증 + 크기 상한 50MB. 파일명은 저장 시 UUID로 대체하고 원본명은 메타로만 보관(경로 순회·XSS 방지).
- 뷰어: PDF 렌더링은 샌드박스 iframe + `Content-Security-Policy` 로 스크립트 실행 차단(PDF 내장 JS 무력화).
- 모든 사용자 입력(파일명, 삭제 사유, 태그) 출력 시 이스케이프.
- 상태 변경 API는 CSRF 토큰 요구. 단 `GET /s/{token}` 은 상태 변경이 없으므로 예외.

**레이트 리밋**
- 링크 비밀번호 시도: 10회/15분/(링크×IP) → 429 (FR-011)
- 토큰 조회 실패(404): 60회/분/IP → 429 (열거 공격 방지)
- 업로드: 30건/시간/사용자

**로깅**: 감사 로그에 토큰 원문·파일 내용은 절대 기록하지 않는다(token_id만).

---

## 5. Technical Design

### 5.1 API Specification

| Method | Endpoint | 설명 | 인가 주체 | 주요 응답 |
|---|---|---|---|---|
| POST | `/api/auth/login` | OIDC 시작 / 매직링크 발송 | `anonymous` | 302, 202 |
| POST | `/api/auth/logout` | 세션 폐기 | `admin`,`member` | 204 |
| GET | `/api/me` | 현재 사용자·역할 | `admin`,`member` | 200, 401 |
| POST | `/api/documents` | 업로드(multipart) | `admin`,`member` | 201, 413, 415, 503 |
| GET | `/api/documents` | 목록(커서, 필터) | `admin`,`member` | 200, 401 |
| GET | `/api/documents/{id}` | 메타 조회 | `admin`,`member` | 200, 401, 404 |
| GET | `/api/documents/{id}/content-url` | 서명 URL 발급(TTL 5분) | `admin`,`member` | 200, 403, 404 |
| DELETE | `/api/documents/{id}` | soft delete + 링크 일괄 revoke | `admin`(전체·사유 필수), `member`(본인 업로드만) | 204, 403, 404 |
| GET | `/api/documents/{id}/audit` | 문서 열람 로그 | `admin`(전체), `member`(본인 문서) | 200, 403 |
| POST | `/api/documents/{id}/links` | 공유 링크 생성(만료 필수) | `admin`, `member`(본인 문서) | 201, 400(만료 누락), 403, 409(변환 failed) |
| GET | `/api/documents/{id}/links` | 링크 목록 | `admin`, `member`(본인 문서) | 200, 403 |
| DELETE | `/api/links/{link_id}` | 링크 회수 | `admin`, `member`(본인 문서) | 204, 403, 404 |
| GET | `/s/{token}` | **공유 열람 페이지(세션 불필요)** | `link_viewer` (유효 토큰 = 자격증명) | 200, 401(비번 필요), 404(미존재), 410(만료·회수) |
| POST | `/s/{token}/unlock` | 링크 비밀번호 검증 | `link_viewer` | 200, 401, 429 |
| GET | `/s/{token}/content-url` | 토큰 스코프 서명 URL(해당 문서 1건) | `link_viewer` | 200, 403(다운로드 비허용), 410 |
| GET | `/api/admin/documents` | 전체 문서·활성 링크 | `admin` | 200, 403 |
| PATCH | `/api/admin/users/{id}/role` | 역할 변경 | `admin` | 200, 403 |
| GET | `/api/admin/audit` | 전사 감사 로그 | `admin` | 200, 403 |

> 인가 규칙 요약: `/api/*` 는 세션 필수(401), `/s/*` 는 세션 금지가 아니라 **세션 불요** — 사내 사용자가 열어도 동일하게 동작하되 감사 로그의 actor 가 user_id 로 기록된다.

### 5.2 Database Schema

```sql
-- 사용자 (사내 계정만. link_viewer 레코드는 존재하지 않는다)
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         CITEXT UNIQUE NOT NULL,
  display_name  TEXT NOT NULL,
  role          TEXT NOT NULL CHECK (role IN ('admin','member')) DEFAULT 'member',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  deactivated_at TIMESTAMPTZ
);

CREATE TABLE documents (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  uploader_id    UUID NOT NULL REFERENCES users(id),
  original_name  TEXT NOT NULL,            -- 표시용. 저장 경로에는 쓰지 않음
  storage_key    TEXT NOT NULL,            -- UUID 기반 경로
  preview_key    TEXT,                     -- DOCX→PDF 변환 결과
  mime_type      TEXT NOT NULL CHECK (mime_type IN (
                   'application/pdf',
                   'application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
  size_bytes     BIGINT NOT NULL CHECK (size_bytes > 0 AND size_bytes <= 52428800),
  status         TEXT NOT NULL CHECK (status IN ('processing','ready','failed')) DEFAULT 'processing',
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at     TIMESTAMPTZ,              -- soft delete (FR-013)
  deleted_by     UUID REFERENCES users(id),
  delete_reason  TEXT CHECK (char_length(delete_reason) <= 200),
  purge_after    TIMESTAMPTZ               -- deleted_at + 30d (FR-017)
);
CREATE INDEX idx_documents_active ON documents (created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_documents_uploader ON documents (uploader_id, created_at DESC);

CREATE TABLE share_links (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id    UUID NOT NULL REFERENCES documents(id) ON DELETE RESTRICT,
  token_hash     BYTEA NOT NULL UNIQUE,    -- SHA-256(token). 원문 저장 금지
  created_by     UUID NOT NULL REFERENCES users(id),
  expires_at     TIMESTAMPTZ NOT NULL,     -- NOT NULL = 무기한 링크 불가 (FR-008)
  revoked_at     TIMESTAMPTZ,
  password_hash  TEXT,                     -- argon2id, NULL이면 비밀번호 없음
  allow_download BOOLEAN NOT NULL DEFAULT false,
  view_count     INTEGER NOT NULL DEFAULT 0,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT expiry_max_30d CHECK (expires_at <= created_at + INTERVAL '30 days')
);
CREATE INDEX idx_links_document ON share_links (document_id) WHERE revoked_at IS NULL;

-- 유효성 판정: revoked_at IS NULL AND expires_at > now() AND document.deleted_at IS NULL
CREATE TABLE audit_logs (
  id           BIGSERIAL PRIMARY KEY,
  event_type   TEXT NOT NULL,   -- upload|view_internal|view_external|link_create|link_revoke|delete|authz_fail
  document_id  UUID,            -- FK 없음: 문서 purge 후에도 로그 유지 (§4.3)
  link_id      UUID,
  actor_user_id UUID,           -- link_viewer 는 NULL
  ip_hash      BYTEA,           -- 원문 IP 대신 해시 + salt
  user_agent   TEXT,
  detail       JSONB,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_document ON audit_logs (document_id, created_at DESC);
CREATE INDEX idx_audit_created ON audit_logs (created_at DESC);
```

### 5.3 Architecture

```
[Browser: member/admin]        [Browser: link_viewer (비로그인)]
        |  session cookie              |  /s/{token}
        v                              v
   +----------------------------------------------+
   |  Web App (Next.js) — SSR + API routes         |
   |  · auth middleware: /api/* 세션 필수           |
   |  · /s/* 는 명시적 예외 → token guard 적용      |
   +----------------------------------------------+
        |            |                 |
        |            |                 +--> [Audit Logger] --> audit_logs (append-only)
        |            |
        |            +--> [Object Storage] (private bucket, SSE, versioning)
        |                     ^  signed URL TTL 5m
        |                     |
        |            [Convert Worker] <-- [Queue] (DOCX→PDF, 재시도 3회)
        v
   [PostgreSQL] (managed, PITR 7d)
        ^
        +-- [Purge Batch] (daily: deleted_at + 30d → storage delete)
```

- **모놀리식 단일 앱 + 비동기 워커 1종**. Scale Grade가 Startup이므로 MSA 불필요(§4.0).
- 인가 판정은 단일 미들웨어 계층에 모으고, 라우트별로 "세션 주체" 또는 "토큰 주체"를 결정해 핸들러에 주입한다. 핸들러는 주체 타입을 신뢰하고 리소스 소유권만 재확인한다.
- 읽기 경로(열람·링크 해석)와 쓰기 경로(업로드·변환)를 서로 다른 프로세스 풀로 분리해 §4.2의 격리 요구를 만족시킨다.

### 5.4 Pages

| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|---|---|---|---|---|---|---|
| `/login` | `anonymous` | 불필요 | FR-001 | Yes | empty(폼) | Yes |
| `/documents` | `member`, `admin` | 세션 필수 | FR-006, FR-013 | Yes | success(목록) | Yes |
| `/documents/new` | `member`, `admin` | 세션 필수 | FR-003, FR-004, FR-005 | Yes | empty(업로드 대기) | Yes |
| `/documents/{id}` | `member`, `admin` | 세션 필수 | FR-007, FR-008, FR-012, FR-013, FR-016 | Yes | success(뷰어) | Yes |
| `/documents/{id}/audit` | `member`(본인), `admin` | 세션 필수 | FR-015, FR-016 | Yes | success(로그 테이블) | Yes |
| `/s/{token}` | `link_viewer` | **세션 불요 · 토큰으로 인가** | FR-009, FR-010, FR-011 | Yes | success(뷰어) | Yes |
| `/admin` | `admin` | 세션 필수 + role=admin | FR-018, FR-013, FR-012 | Yes | success(관리 목록) | Yes |

### 5.4.1 Page State Matrix

| Route | loading | empty | error | success | no-permission | 비고 |
|---|---|---|---|---|---|---|
| `/login` | 인증 요청 중 스피너, 버튼 비활성 | 초기 폼(기본 상태) | "로그인에 실패했어요. 다시 시도해 주세요" + 재시도 | 로그인 후 `/documents` 리다이렉트 | 사내 도메인 아닌 계정: "사내 계정으로만 로그인할 수 있어요" | 이미 로그인 시 즉시 리다이렉트 |
| `/documents` | 목록 스켈레톤 10행 | "아직 올린 문서가 없어요" + 업로드 CTA | "목록을 불러오지 못했어요" + 재시도 버튼 | 문서 카드/행 목록 + 무한스크롤 | 해당 없음(로그인 사용자 전원 열람 가능) — 미인증은 `/login` 리다이렉트 | 필터 결과 0건도 empty로 처리(문구 구분) |
| `/documents/new` | 업로드 진행률 바(%) + 취소 | 파일 미선택 드롭존 | 415/413/503 각각 별도 문구, 파일 선택 상태 유지 | 완료 후 상세로 이동 | 업로드 한도(30/시간) 초과: "잠시 후 다시 시도해 주세요" | 변환 대기는 상세의 processing으로 인계 |
| `/documents/{id}` | 메타 스켈레톤 + 뷰어 자리 표시 | N/A(문서가 있어야 진입) | 변환 `failed`: 미리보기 대신 원본 다운로드 안내 / 5xx: 재시도 | 뷰어 렌더 + 링크 생성·회수 패널 | 삭제 버튼은 업로더·admin 외 비노출, 직접 호출 시 403 토스트 | `processing` 은 별도 상태: "미리보기 준비 중" 폴링 |
| `/documents/{id}/audit` | 테이블 스켈레톤 | "아직 열람 기록이 없어요" | "로그를 불러오지 못했어요" + 재시도 | 열람 기록 테이블(시각·주체·IP 마스킹) | 타인 문서 접근: 403 화면 "이 문서의 기록은 볼 수 없어요" | 외부 열람은 "링크 열람(외부)"로 표기 |
| `/s/{token}` | 토큰 검증 중 스피너(문서 정보 미노출) | N/A(단일 문서 고정) | 만료·회수: 410 화면 "이 링크는 만료되었어요" / 미존재: 404 "링크를 찾을 수 없어요" — **두 화면 모두 파일 정보 비노출** | 뷰어 렌더 + (허용 시) 다운로드 버튼 | 비밀번호 필요: 잠금 화면 / 오입력 401 / 10회 초과 429 "잠시 후 다시 시도해 주세요" | 열람 기록 고지 문구 하단 고정 |
| `/admin` | 목록 스켈레톤 | "관리할 문서가 없어요" | "불러오지 못했어요" + 재시도 | 문서·링크 목록 + 삭제/회수 액션 | `member` 접근 시 403 화면(메뉴에도 비노출) | 삭제 시 사유 입력 모달 필수 |

### 5.5 User Flow

```mermaid
flowchart TD
    A[진입] --> B{세션 있음?}
    B -- 아니오 --> C{경로가 /s/token ?}
    C -- 아니오 --> D[/login]
    D --> E{사내 도메인 계정?}
    E -- 아니오 --> D2[로그인 거부 안내]
    E -- 예 --> F[/documents 목록]
    B -- 예 --> F

    C -- 예 --> T{토큰 존재?}
    T -- 아니오 --> T404[404 링크를 찾을 수 없어요<br/>파일 정보 비노출]
    T -- 예 --> T2{만료 또는 회수 또는 문서 삭제됨?}
    T2 -- 예 --> T410[410 만료 안내<br/>회수/만료 구분 없음]
    T2 -- 아니오 --> T3{비밀번호 설정?}
    T3 -- 예 --> P[비밀번호 입력]
    P --> P2{일치?}
    P2 -- 아니오 --> P3{15분내 10회 초과?}
    P3 -- 예 --> P429[429 잠시 후 재시도]
    P3 -- 아니오 --> P
    P2 -- 예 --> V
    T3 -- 아니오 --> V[/s/token 뷰어 렌더]
    V --> VA[감사 로그: view_external 기록]
    VA --> VD{allow_download?}
    VD -- 예 --> VDL[원본 다운로드 가능]
    VD -- 아니오 --> VN[열람만 가능]

    F --> G[/documents/new 업로드]
    G --> H{확장자 + 매직넘버 + 50MB 검증}
    H -- 실패 --> H1[415 또는 413 오류 안내<br/>저장 안 함]
    H -- 통과 --> I{스토리지 정상?}
    I -- 아니오 --> I1[503 안내<br/>기존 문서 열람은 계속 동작]
    I -- 예 --> J{DOCX?}
    J -- 예 --> K[변환 큐 processing]
    K --> K2{변환 성공?}
    K2 -- 아니오 --> K3[failed: 원본 다운로드만<br/>링크 생성 불가]
    K2 -- 예 --> L
    J -- 아니오 --> L[/documents/id 상세 ready]

    F --> L
    L --> M[공유 링크 생성<br/>만료 필수 선택]
    M --> N[토큰 URL 발급 + 복사]
    N -.외부에 전달.-> C

    L --> R{링크 회수?}
    R -- 예 --> R1[revoked → 이후 접근 410]

    L --> S{삭제 시도}
    S --> S2{업로더 본인 또는 admin?}
    S2 -- 아니오 --> S3[403 권한 없음<br/>authz_fail 로그]
    S2 -- 예 --> S4[soft delete + 사유<br/>연결 링크 전부 revoke]
    S4 --> S5[30일 후 배치 영구 삭제<br/>감사 로그는 유지]

    F --> AD{role = admin?}
    AD -- 예 --> ADM[/admin 콘솔<br/>전체 문서·링크 관리]
    AD -- 아니오 --> ADX[메뉴 비노출<br/>직접 접근 시 403]
```

---

## 6. Implementation Phases

### Phase 1 — 인증·업로드·열람 기반 (P0 핵심)

| Task | Linked FR |
|---|---|
| OIDC/매직링크 로그인, 세션 쿠키, 인증 미들웨어 | FR-001 |
| users 테이블 + 역할 판정(`admin`/`member`) | FR-002 |
| 업로드 API: 확장자+매직넘버+50MB 검증 | FR-003 |
| 오브젝트 스토리지 저장 + documents 메타 기록 | FR-004 |
| 문서 목록(커서 페이지네이션·필터) | FR-006 |
| 문서 상세 + PDF 뷰어 + 서명 URL(TTL 5분) | FR-007 |
| audit_logs 스키마 + 업로드/열람 이벤트 기록 | FR-015(부분) |

**Deliverable**: 사내 사용자가 로그인해 PDF를 올리고 브라우저에서 열람할 수 있다. 외부 공유는 아직 없다. 스테이징에서 §2.2의 업로드 정상/415/413/위조 확장자 시나리오가 통과한다.

### Phase 2 — 공유 링크 + 관리자 삭제 (P0 완성)

| Task | Linked FR |
|---|---|
| share_links 스키마 + 토큰 생성(CSPRNG, 해시 저장), 만료 필수 | FR-008 |
| `/s/{token}` 공개 라우트 + 토큰 guard(인증 미들웨어 예외 처리) | FR-009 |
| 410/404 분기 및 정보 비노출 응답 | FR-010 |
| 링크 회수 | FR-012 |
| 문서 삭제(soft) + 연결 링크 일괄 revoke + 소유권 인가 | FR-013 |
| 링크 열람/회수/삭제/인가실패 감사 이벤트 | FR-015(완성) |
| 보안 헤더: noindex, no-referrer, CSP, HSTS / 토큰 404 레이트리밋 | §4.5 |

**Deliverable**: 외부인이 로그인 없이 링크로 문서를 열람하고, 만료·회수·삭제가 즉시 반영된다. §2.2의 만료·회수·미존재·인가경계 시나리오 전부 통과. **여기까지가 MVP 출시 가능선** — P0 FR(001·002·003·004·006·007·008·009·010·012·013·015)이 모두 Phase 1–2 안에 있다.

### Phase 3 — DOCX 변환 + 링크 보호 + 감사 조회 (P1)

| Task | Linked FR |
|---|---|
| 변환 워커 + 큐 + `processing/ready/failed` 상태머신, 재시도 3회 | FR-005 |
| 링크 비밀번호(argon2id) + 시도 제한 429 | FR-011 |
| 삭제 사유 기록(admin 필수) | FR-014 |
| 문서별 열람 로그 조회 페이지 | FR-016 |

**Deliverable**: DOCX 업로드가 실사용 가능해지고, 민감 링크에 비밀번호를 걸 수 있으며, 업로더가 열람 이력을 확인한다.

### Phase 4 — 운영 성숙 (P1)

| Task | Linked FR |
|---|---|
| purge 배치(deleted_at+30d) + 링크 90일 익명화 | FR-017, §4.3 |
| 관리자 콘솔(전체 문서·활성 링크·역할 변경) | FR-018 |
| 백업/복구 리허설, 읽기 전용 degrade 모드, 성능 목표 부하 테스트 | §4.2, §4.4, §4.1 |

**Deliverable**: 보관 정책이 자동 집행되고, 관리자가 콘솔에서 전사 통제를 수행하며, §4.1 정량 목표가 부하 테스트로 검증된다.

> 순서 근거: FR-008/009(링크)는 FR-007(뷰어)에 의존하므로 Phase 2. FR-013(삭제)은 FR-012(회수)와 같은 Phase에 둬야 "삭제 시 링크 무효화"가 한 번에 성립한다. P1인 FR-005(DOCX 변환)를 Phase 3으로 미뤄도 Phase 2 시점에 PDF 단독으로 전체 가치사슬이 닫힌다.

---

## 7. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| 외부 링크 열람 성공률 | ≥ 98% (유효 링크 요청 중 200 응답 비율) | `/s/{token}` 응답 코드 분포 (만료·회수 제외) |
| 개인 드라이브 링크 대체율 | 출시 8주 내 외부 자료 공유의 ≥ 70%가 본 서비스 경유 | 주간 생성 공유 링크 수 / 팀 설문(격주) 교차 검증 |
| 활성 member 채택률 | 출시 4주 내 임직원의 ≥ 60%가 최소 1건 업로드 | `documents` distinct uploader_id / 전체 사용자 |
| 링크 만료 통제 커버리지 | 100% (무기한 링크 0건) | `share_links.expires_at NOT NULL` 제약 위반 0 + 주간 쿼리 검증 |
| 삭제 반영 지연 | p95 ≤ 5s (삭제 → 링크 410 전환) | 삭제 이벤트와 첫 410 응답 간 시간차 계측 |
| 부적절 문서 대응 시간 | 신고~삭제 완료 중앙값 ≤ 30분 | admin 삭제 감사 로그 vs 신고 시각 |
| 열람 뷰어 LCP | p95 ≤ 2.5s | RUM(Real User Monitoring) |
| 업로드 실패율 | < 2% (5xx 기준, 검증 실패 4xx 제외) | `POST /api/documents` 응답 코드 분포 |
| 감사 로그 완전성 | 열람 이벤트 누락 0건 | 주간 샘플링: 뷰어 요청 수 vs audit_logs 카운트 대조 |
| 보안 사고 | 무단 접근으로 인한 문서 유출 0건 | authz_fail 로그 이상 탐지 + 분기 침투 점검 |
