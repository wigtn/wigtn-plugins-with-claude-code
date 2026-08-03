# PRD — 사내 휴가 신청/승인 서비스 (Leave Management)

> **Type**: product-feature
> **Scale Grade**: Hobby (사내 팀 대상, 휴가 신청은 저빈도 이벤트 → DAU 1,000 미만)
> **Status**: Draft
> **Author**: contact@wigtn.com
> **Date**: 2026-08-03

---

## 1. Overview

### 1.1 Problem Statement
현재 휴가 신청·승인이 메신저/이메일/구두로 산발적으로 이루어져 다음 문제가 발생한다.
- 신청 이력과 잔여 연차가 어디에도 집계되지 않아 신청자·팀장이 매번 수기로 계산한다.
- 승인 여부와 반려 사유가 기록으로 남지 않아 분쟁·누락이 생긴다.
- 관리자가 팀별 휴가 현황과 잔여 연차를 한눈에 볼 방법이 없어 인력 계획이 어렵다.

### 1.2 Goals
- G1. 신청자가 잔여 연차를 확인하고 휴가를 신청할 수 있다.
- G2. 팀장이 자기 팀 신청 건을 승인/반려하고 사유를 남길 수 있다.
- G3. 관리자가 전체 팀의 휴가 현황·잔여 연차를 조회할 수 있다.
- G4. 모든 신청/처리 이력이 변경 불가능한 기록으로 남는다.

### 1.3 Non-Goals
- 급여·근태(출퇴근 타각) 연동 — 이번 범위 밖. 휴가 도메인만 다룬다.
- 외부 HR SaaS(예: 시프티, 플렉스) 양방향 동기화 — 하지 않는다.
- 결재선 다단계(팀장 → 본부장 → 대표) 커스터마이징 — 이번 버전은 **팀장 1단 승인** 고정. 다단계는 향후 과제.
- 휴가 종류별 복잡한 회계 규칙(반차 시간 단위, 대체휴무 이월) — v1은 연차/반차/무급 3종만.
- 모바일 네이티브 앱 — 반응형 웹으로 대응.
- 셀프서비스 비밀번호 재설정(이메일 링크) — v1 미포함. 초기 비밀번호 발급·분실 재설정은 **관리자가 수동 처리**(FR-015). 향후 과제.

### 1.4 Scope
**포함**: 로그인, 휴가 신청/취소, 승인/반려, 잔여 연차 계산, 관리자 현황 대시보드, 처리 이력.
**제외**: 급여 연동, 다단계 결재, 외부 HR 연동, 알림의 외부 채널(슬랙/카톡) 발송(v1은 인앱 알림 목록만).

---

## 2. User Stories

### 2.1 Primary User
- 신청자(팀원): "As a **팀원**, I want to **잔여 연차를 확인하고 날짜·종류를 골라 휴가를 신청** so that **승인 절차를 명확히 남기고 승인 결과를 추적**할 수 있다."
- 팀장: "As a **팀장**, I want to **내 팀의 대기 중 신청을 승인하거나 사유와 함께 반려** so that **팀 인력 공백을 관리**할 수 있다."
- 관리자: "As a **관리자**, I want to **전체 팀의 휴가 현황과 잔여 연차를 조회** so that **회사 차원의 인력 계획을 세울** 수 있다."

### 2.2 Acceptance Criteria (Gherkin)

**AC-1. 휴가 신청 (정상)**
```gherkin
Given 로그인한 팀원이고 잔여 연차가 5일이다
When 시작일 2026-09-01, 종료일 2026-09-02, 종류=연차로 신청한다
Then 신청이 PENDING 상태로 생성되고
And 소진 예정 2일이 "대기 중 차감"으로 표시되며
And 해당 팀 팀장에게 인앱 알림이 생성된다
```

**AC-2. 잔여 연차 부족 (실패)**
```gherkin
Given 로그인한 팀원이고 잔여 연차가 1일이다
When 연차 3일을 신청한다
Then 신청이 생성되지 않고
And "잔여 연차(1일)를 초과합니다" 오류가 반환된다(HTTP 422)
```

**AC-3. 기간 중복 신청 (실패)**
```gherkin
Given 팀원이 2026-09-01~09-02 승인 또는 대기 상태 휴가를 이미 가지고 있다
When 2026-09-02~09-03 휴가를 신청한다
Then "해당 기간에 이미 신청/승인된 휴가가 있습니다" 오류가 반환된다(HTTP 409)
```

**AC-4. 팀장 승인 (정상)**
```gherkin
Given 팀장이고 자기 팀원의 PENDING 신청이 있다
When 해당 신청을 승인한다
Then 상태가 APPROVED로 바뀌고
And 신청자의 잔여 연차가 확정 차감되며
And 신청자에게 승인 알림이 생성되고
And 처리 이력에 처리자·시각이 기록된다
```

**AC-5. 팀장 반려 (사유 필수)**
```gherkin
Given 팀장이고 자기 팀원의 PENDING 신청이 있다
When 반려하되 사유를 비워 둔다
Then "반려 사유는 필수입니다" 오류가 반환된다(HTTP 422)
When 사유를 입력하고 반려한다
Then 상태가 REJECTED로 바뀌고 대기 차감이 복원되며 신청자에게 반려 알림이 생성된다
```

**AC-6. 다른 팀 신청 승인 시도 (권한 부족)**
```gherkin
Given 팀장 A이고 다른 팀 소속 팀원의 PENDING 신청이 있다
When 그 신청을 승인하려 한다
Then 처리되지 않고 "권한이 없습니다" 오류가 반환된다(HTTP 403)
```

**AC-7. 신청 취소**
```gherkin
Given 팀원이 자신의 PENDING 신청을 가지고 있다
When 신청을 취소한다
Then 상태가 CANCELLED로 바뀌고 대기 차감이 복원된다
Given 이미 APPROVED된 신청이다
When 시작일이 지난 신청을 취소하려 한다
Then "이미 시작된 휴가는 취소할 수 없습니다" 오류가 반환된다(HTTP 422)
```

**AC-8. 세션 만료 (만료 시나리오)**
```gherkin
Given 세션 토큰이 만료된 사용자다
When 보호된 페이지에 접근한다
Then 로그인 페이지로 리다이렉트되고 만료 안내가 표시된다(HTTP 401)
```

### 2.3 User Roles

| Role Key | 한국어 명칭 | 권한 범위 |
|---|---|---|
| `member` | 신청자(팀원) | 본인 휴가 신청/취소, 본인 이력·잔여 연차 조회 |
| `manager` | 팀장 | `member` 권한 + **자기 팀** 신청 승인/반려, 자기 팀 현황 조회 |
| `admin` | 관리자 | 전체 팀 휴가 현황·잔여 연차 조회, 사용자/팀/연차 정책 관리. 일반 신청의 승인권은 없으나, **팀장 본인 휴가에 한해 예외적 승인권**을 가진다(FR-017) |

---

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|---|---|---|---|
| FR-001 | 이메일/비밀번호 로그인 및 세션 발급, 로그아웃 | P0 | — |
| FR-002 | 로그인 사용자의 역할(`member`/`manager`/`admin`)과 소속 팀을 조회 | P0 | FR-001 |
| FR-003 | 팀원이 시작일·종료일·종류(연차/반차/무급)·사유로 휴가 신청 생성 | P0 | FR-002 |
| FR-004 | 신청 시 잔여 연차 검증(연차/반차만 차감, 무급은 미차감) | P0 | FR-003 |
| FR-005 | 신청 시 동일 사용자 기간 중복 검증(PENDING·APPROVED와 겹치면 거부) | P0 | FR-003 |
| FR-006 | 팀원이 본인의 PENDING 신청 취소, APPROVED는 시작일 이전에만 취소 | P0 | FR-003 |
| FR-007 | 팀장이 자기 팀의 PENDING 신청을 승인 → 잔여 연차 확정 차감 | P0 | FR-003 |
| FR-008 | 팀장이 자기 팀의 PENDING 신청을 사유와 함께 반려 → 대기 차감 복원 | P0 | FR-003 |
| FR-009 | 승인/반려 시 처리자·처리시각·상태전이를 이력으로 기록(불변) | P0 | FR-007, FR-008 |
| FR-010 | 팀원 본인 신청 목록·상태·잔여 연차 조회 | P0 | FR-003 |
| FR-011 | 팀장의 팀 신청 목록 조회(상태·기간 필터) | P1 | FR-007 |
| FR-012 | 관리자의 전체 팀 휴가 현황 대시보드(팀별·상태별·기간별 필터) | P0 | FR-007 |
| FR-013 | 관리자의 전체 사용자 잔여 연차 조회 | P1 | FR-012 |
| FR-014 | 인앱 알림 목록(신청→팀장, 승인/반려→신청자) 및 읽음 처리 | P1 | FR-007, FR-008 |
| FR-015 | 관리자의 사용자·팀·연차 부여(연 부여일수) 관리 **및 비밀번호 수동 재발급** | P1 | FR-002 |
| FR-016 | 휴가 종류별 잔여/사용 요약(연차 사용일, 잔여일) 표시 | P2 | FR-010 |
| FR-017 | 팀장 본인 휴가는 `admin`이 승인/반려(자기승인 차단의 우회 경로) | P1 | FR-007, FR-008 |

**무모순 확인**: 모든 조회는 인증 필수(비로그인 열람 경로 없음). 일반 신청의 승인권은 `manager`의 **자기 팀·본인 제외**로 한정되고, 팀장 본인 휴가만 `admin`이 처리한다(FR-017) — 모든 신청 건에 정확히 한 승인 주체가 대응하며, 자기승인은 불가능하다.

---

## 4. Non-Functional Requirements

### 4.0 Scale Grade
**Hobby**. 근거: 사내 단일 회사 팀원 대상이며 휴가 신청은 인당 월 수 회 수준의 저빈도 이벤트로, 예상 DAU 1,000 미만.

### 4.1 Performance
- 목록/현황 조회 API p95 < 300ms (동시 사용자 50 기준).
- 신청·승인 쓰기 API p95 < 500ms.
- 관리자 대시보드 초기 렌더 LCP < 2.5s (100건 데이터 기준).
- 동시성: 피크 동시 요청 20 req/s를 오류율 < 0.5%로 처리.

### 4.2 Availability
- 목표 가용성 99.0% (월 다운타임 ≈ 7.3시간 허용). 업무시간(09–18시) 우선.
- 장애 시: 쓰기 실패는 사용자에게 재시도 가능 오류 표시, 부분 성공 없이 트랜잭션 롤백.

### 4.3 Data
- 휴가 신청/이력: 관계법(근로기준법상 임금·근태 관련 서류 3년 보존)에 준해 **최소 3년 보관**.
- 개인정보: 이름·이메일·소속만 저장, 민감정보(주민번호 등) 미수집.
- 삭제 정책: 퇴사자 계정은 비활성화(soft delete), 이력은 익명화 후 보존 기간까지 유지.

### 4.4 Recovery
- RPO ≤ 24h (일 1회 백업), RTO ≤ 4h. Hobby 등급 기준 관리형 DB 자동 백업에 의존.

### 4.5 Security
- **인증**: 이메일/비밀번호 + 서버 세션(또는 서명된 JWT, httpOnly 쿠키). 비밀번호는 bcrypt 등 단방향 해시.
- **무차별 대입 방어**: `POST /api/auth/login`에 (1) IP·계정별 시도 제한 **5회/분, 이후 지수 backoff**, (2) 계정별 연속 실패 **10회 시 15분 일시 잠금**, (3) 한도 초과 시 **429 Too Many Requests** 반환. Vercel Firewall/WAF rate-limit 규칙 또는 미들웨어 레벨에서 강제(§5.3).
- **인가 규칙 (역할 × 리소스)**:

  | 리소스 / 액션 | member | manager | admin |
  |---|---|---|---|
  | 본인 신청 생성/취소 | ✅ | ✅ | ❌(신청 주체 아님) |
  | 본인 신청·잔여 조회 | ✅ | ✅ | ✅(전체) |
  | 타인 신청 승인/반려 | ❌ | ✅ **자기 팀만, 본인 제외** | ⚠️ 팀장 본인 휴가에 한해 ✅ |
  | 팀 현황 조회 | ❌ | ✅ 자기 팀 | ✅ 전체 |
  | 사용자·팀·연차 정책 관리 | ❌ | ❌ | ✅ |

- 모든 승인/반려 요청은 서버에서 `요청자.team == 대상신청.team && 요청자.role == manager && 대상신청.applicant_id != 요청자.id` 재검증(클라이언트 신뢰 금지). **자기 자신의 신청은 승인/반려 불가** — 팀장 본인 휴가는 예외적으로 `admin`이 승인권을 가진다(§2.3·FR-017).
- **전송/저장**: 전 구간 HTTPS(TLS 1.2+). 세션 쿠키 `httpOnly`·`Secure`·`SameSite=Lax`.
- **입력 검증**: 날짜 형식·시작일≤종료일·종류 enum·사유 길이(≤500자) 서버 검증. 파라미터화 쿼리로 SQL 인젝션 차단.

---

## 5. Technical Design

### 5.1 API Specification

모든 엔드포인트는 인증 필요(비로그인 접근 불가). 공통 오류: 401(미인증), 403(권한부족), 422(검증실패).

---
**POST /api/auth/login** — 로그인 · 인가 주체: 누구나
- Request: `{ "email": "a@corp.com", "password": "..." }`
- Response 200: `{ "user": { "id", "name", "role", "teamId" }, "token": "..." }`
- Error: 401 `{ "error": "INVALID_CREDENTIALS" }`, 422 `{ "error": "VALIDATION", "fields": {...} }`, 429 `{ "error": "TOO_MANY_ATTEMPTS", "retryAfter": 900 }`(시도 제한/계정 잠금, §4.5)

---
**GET /api/me** — 내 프로필·잔여 연차 · 인가 주체: 인증 사용자 본인
- Response 200: `{ "id", "name", "role", "teamId", "leaveBalance": { "annualTotal": 15, "annualUsed": 3, "annualPending": 2, "annualRemaining": 10 } }`
- Error: 401

---
**POST /api/leaves** — 휴가 신청 · 인가 주체: `member`/`manager` 본인
- Request: `{ "startDate": "2026-09-01", "endDate": "2026-09-02", "type": "ANNUAL|HALF_DAY|UNPAID", "reason": "가족 여행" }`
- Response 201: `{ "id", "status": "PENDING", "days": 2, "createdAt" }`
- Error: 422 `{ "error": "INSUFFICIENT_BALANCE" }` / `{ "error": "VALIDATION" }`, 409 `{ "error": "OVERLAP" }`

---
**GET /api/leaves** — 내 신청 목록 · 인가 주체: 본인(자동으로 requester로 필터)
- Query: `?status=PENDING&from=2026-09-01&to=2026-09-30`
- Response 200: `{ "items": [ { "id", "startDate", "endDate", "type", "status", "reason", "decidedBy", "decidedAt" } ], "total": 12 }`
- Error: 401

---
**POST /api/leaves/{id}/cancel** — 신청 취소 · 인가 주체: 신청 소유자
- Response 200: `{ "id", "status": "CANCELLED" }`
- Error: 403(타인 신청), 422 `{ "error": "ALREADY_STARTED" }`, 404

---
**GET /api/team/leaves** — 팀 신청 목록 · 인가 주체: `manager`(자기 팀), `admin`(teamId 지정 시 전체)
- Query: `?status=PENDING&teamId=...`
- Response 200: `{ "items": [ { "id", "applicant": {"id","name"}, "startDate", "endDate", "type", "status" } ], "total" }`
- Error: 401, 403(자기 팀 아님)

---
**POST /api/leaves/{id}/approve** — 승인 · 인가 주체: 대상 신청 소속 팀의 `manager`(본인 신청 제외). **대상 신청자가 팀장 본인인 경우 `admin`** (FR-017)
- Response 200: `{ "id", "status": "APPROVED", "decidedBy", "decidedAt" }`
- Error: 403(자기 팀 아님/비팀장), 409 `{ "error": "NOT_PENDING" }`, 404

---
**POST /api/leaves/{id}/reject** — 반려 · 인가 주체: 대상 신청 소속 팀의 `manager`(본인 신청 제외). **대상 신청자가 팀장 본인인 경우 `admin`** (FR-017)
- Request: `{ "reason": "인력 부족 기간" }` (필수)
- Response 200: `{ "id", "status": "REJECTED", "decisionReason", "decidedBy", "decidedAt" }`
- Error: 403, 422 `{ "error": "REASON_REQUIRED" }`, 409 `{ "error": "NOT_PENDING" }`

---
**GET /api/admin/overview** — 전체 현황 대시보드 · 인가 주체: `admin`
- Query: `?teamId=&status=&from=&to=`
- Response 200: `{ "summary": { "pending": 4, "approved": 30, "rejected": 2 }, "byTeam": [ { "teamId", "teamName", "pending", "approved", "membersOnLeaveToday": 2 } ] }`
- Error: 401, 403

---
**GET /api/admin/balances** — 전체 잔여 연차 · 인가 주체: `admin`
- Response 200: `{ "items": [ { "userId", "name", "teamName", "annualRemaining", "annualUsed" } ] }`
- Error: 403

---
**GET /api/notifications** / **POST /api/notifications/{id}/read** — 인앱 알림 · 인가 주체: 본인
- GET Response 200: `{ "items": [ { "id", "type": "SUBMITTED|APPROVED|REJECTED", "leaveId", "read": false, "createdAt" } ], "unread": 3 }`
- Error: 401

### 5.2 Database Schema

```sql
-- 팀
CREATE TABLE teams (
  id           BIGSERIAL PRIMARY KEY,
  name         TEXT NOT NULL,
  manager_id   BIGINT,            -- users.id (팀장)
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 사용자
CREATE TABLE users (
  id            BIGSERIAL PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  name          TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role            TEXT NOT NULL CHECK (role IN ('member','manager','admin')),
  team_id         BIGINT REFERENCES teams(id),
  is_active       BOOLEAN NOT NULL DEFAULT true,
  failed_attempts INT NOT NULL DEFAULT 0,     -- 로그인 연속 실패(§4.5 계정 잠금)
  locked_until    TIMESTAMPTZ,                -- 잠금 해제 시각(NULL이면 미잠금)
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 연차 부여(연도별)
CREATE TABLE leave_grants (
  id           BIGSERIAL PRIMARY KEY,
  user_id      BIGINT NOT NULL REFERENCES users(id),
  year         INT NOT NULL,
  annual_total NUMERIC(4,1) NOT NULL DEFAULT 15,   -- 반차 대응 0.5 단위
  UNIQUE (user_id, year)
);

-- 휴가 신청
CREATE TABLE leave_requests (
  id              BIGSERIAL PRIMARY KEY,
  applicant_id    BIGINT NOT NULL REFERENCES users(id),
  team_id         BIGINT NOT NULL REFERENCES teams(id),   -- 신청 시점 소속 스냅샷
  type            TEXT NOT NULL CHECK (type IN ('ANNUAL','HALF_DAY','UNPAID')),
  start_date      DATE NOT NULL,
  end_date        DATE NOT NULL,
  days            NUMERIC(4,1) NOT NULL,                  -- 소진 일수
  reason          TEXT,
  status          TEXT NOT NULL DEFAULT 'PENDING'
                  CHECK (status IN ('PENDING','APPROVED','REJECTED','CANCELLED')),
  decided_by      BIGINT REFERENCES users(id),
  decided_at      TIMESTAMPTZ,
  decision_reason TEXT,                                   -- 반려 사유
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (start_date <= end_date)
);
CREATE INDEX idx_leave_applicant_status ON leave_requests(applicant_id, status);
CREATE INDEX idx_leave_team_status ON leave_requests(team_id, status);

-- 상태 전이 이력(불변, append-only)
CREATE TABLE leave_history (
  id          BIGSERIAL PRIMARY KEY,
  leave_id    BIGINT NOT NULL REFERENCES leave_requests(id),
  from_status TEXT,
  to_status   TEXT NOT NULL,
  actor_id    BIGINT NOT NULL REFERENCES users(id),
  note        TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 인앱 알림
CREATE TABLE notifications (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id),
  type        TEXT NOT NULL CHECK (type IN ('SUBMITTED','APPROVED','REJECTED')),
  leave_id    BIGINT REFERENCES leave_requests(id),
  is_read     BOOLEAN NOT NULL DEFAULT false,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```
- 잔여 = `annual_total − Σ(APPROVED days) − Σ(PENDING days)`로 계산(연차/반차만, 무급 제외).
- 승인/반려/취소는 `leave_requests` 상태 변경 + `leave_history` insert를 **단일 트랜잭션**으로 처리.
- **동시성(원자성)**: 신청 생성·승인 시 해당 사용자의 `leave_grants` 행을 `SELECT ... FOR UPDATE`로 비관적 잠금한 뒤 잔여 검증→차감을 같은 트랜잭션에서 수행한다. 동시 신청이 같은 잔여를 읽어 초과 차감(음수 잔여)되는 TOCTOU를 차단한다.

### 5.3 Architecture
- **프론트엔드**: Next.js(App Router) 반응형 웹 + React Server Components, 역할 기반 라우트 가드.
- **백엔드**: Next.js Route Handlers (Vercel Functions, Node.js 런타임). 서버에서 세션·인가 재검증.
- **DB**: 관리형 PostgreSQL(Vercel Marketplace: Neon 등). 마이그레이션은 SQL/ORM.
- **인증**: httpOnly 세션 쿠키. 미들웨어에서 인증 확인, 핸들러에서 인가 확인.
- **배포**: Vercel(프리뷰 + 프로덕션). 백업은 관리형 DB 자동 백업.

#### 5.4 Pages

| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|---|---|---|---|---|---|---|
| `/login` | member, manager, admin | No | FR-001 | Yes | form | Yes |
| `/` (내 대시보드) | member, manager | Yes | FR-010, FR-016 | Yes | success | Yes |
| `/leaves/new` | member, manager | Yes | FR-003, FR-004, FR-005 | Yes | form | Yes |
| `/leaves` (내 신청 목록) | member, manager | Yes | FR-010, FR-006 | Yes | success/empty | Yes |
| `/team` (팀 승인함) | manager | Yes | FR-011, FR-007, FR-008 | Yes | success/empty | Yes |
| `/admin/overview` | admin | Yes | FR-012 | Yes | success/empty | Yes |
| `/admin/balances` | admin | Yes | FR-013 | Yes | success | Yes |
| `/admin/users` | admin | Yes | FR-015 | Yes | success | Yes |
| `/notifications` | member, manager, admin | Yes | FR-014 | Yes | success/empty | Yes |

#### 5.4.1 Page State Matrix

| Route | loading | empty | error | success | no-permission | 비고 |
|---|---|---|---|---|---|---|
| `/login` | 버튼 스피너 | — | 자격증명 오류 배너 | 역할별 홈 리다이렉트 | — | 미인증 전용 |
| `/` | 스켈레톤 카드 | "신청 이력 없음" | 재시도 배너 | 잔여 연차+최근 신청 | — | |
| `/leaves/new` | — | — | 필드 오류(잔여부족/중복/형식) | 신청 완료 토스트→목록 | member/manager 외 접근 시 403 안내 | |
| `/leaves` | 스켈레톤 리스트 | "신청 내역이 없습니다" | 재시도 배너 | 신청 카드 목록 | — | |
| `/team` | 스켈레톤 리스트 | "대기 중 신청 없음" | 재시도 배너 | 승인 대기 목록 | 비팀장 접근 시 403 페이지 | |
| `/admin/overview` | 스켈레톤 대시보드 | "데이터 없음" | 재시도 배너 | 팀별 현황 카드/표 | 비관리자 403 페이지 | |
| `/admin/balances` | 스켈레톤 표 | "사용자 없음" | 재시도 배너 | 잔여 연차 표 | 비관리자 403 | |
| `/admin/users` | 스켈레톤 표 | "사용자 없음" | 저장 실패 배너 | 사용자 목록/편집 | 비관리자 403 | |
| `/notifications` | 스켈레톤 리스트 | "알림 없음" | 재시도 배너 | 알림 목록 | — | |

#### 5.5 User Flow

```mermaid
flowchart TD
    A[방문] --> B{세션 유효?}
    B -- 아니오 --> L[/login/]
    L -->|로그인 성공| C{역할}
    B -- 예 --> C
    C -- member/manager --> D[/ 내 대시보드]
    C -- admin --> O[/admin/overview]

    D --> N[/leaves/new 신청]
    N -->|잔여부족/중복| NE[오류 표시, 재입력]
    N -->|검증 통과| P[PENDING 생성 + 팀장 알림]
    P --> ML[/leaves 내 목록]
    ML -->|PENDING 취소| CX[CANCELLED, 대기차감 복원]

    C -- manager --> T[/team 팀 승인함]
    T -->|승인| AP[APPROVED, 연차 확정차감, 신청자 알림]
    T -->|반려+사유| RJ[REJECTED, 대기차감 복원, 신청자 알림]
    T -->|다른 팀 신청| F403[403 권한 없음]

    O --> BAL[/admin/balances 잔여 조회]
    O -->|필터: 팀/상태/기간| O

    AP --> ML
    RJ --> ML
```

---

## 6. Implementation Phases

### Phase 1 — 기반 & 인증 (Deliverable: 로그인 후 역할별 홈 진입)
- FR-001 로그인/세션/로그아웃
- FR-002 역할·팀 조회, 라우트 가드
- DB 스키마(teams, users, leave_grants) + 시드

### Phase 2 — 신청 핵심 (Deliverable: 팀원이 신청·취소하고 잔여 확인)
- FR-003 신청 생성
- FR-004 잔여 연차 검증
- FR-005 기간 중복 검증
- FR-006 취소
- FR-010 내 신청/잔여 조회
- 페이지: `/`, `/leaves/new`, `/leaves`

### Phase 3 — 승인 워크플로우 (Deliverable: 팀장 승인/반려 + 불변 이력)
- FR-007 승인(확정 차감)
- FR-008 반려(사유 필수, 대기 복원)
- FR-009 처리 이력 기록
- FR-011 팀 신청 목록
- FR-017 팀장 본인 휴가의 admin 승인 경로(자기승인 차단)
- 페이지: `/team`

### Phase 4 — 관리자 현황 (Deliverable: 관리자 전체 현황·잔여 조회)
- FR-012 전체 현황 대시보드
- FR-013 전체 잔여 조회
- FR-015 사용자/팀/연차 관리
- 페이지: `/admin/overview`, `/admin/balances`, `/admin/users`

### Phase 5 — 알림 & 마감 (Deliverable: 인앱 알림, 요약)
- FR-014 인앱 알림 목록/읽음
- FR-016 종류별 사용/잔여 요약
- 페이지: `/notifications`

---

## 7. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| 휴가 신청 온라인 처리율 | 3개월 내 신청의 90% 이상 서비스로 처리 | 신청 건수 로그 대비 채널 서베이 |
| 승인 처리 리드타임 | 신청→처리 중앙값 24h 이내 | `decided_at − created_at` 집계 |
| 잔여 연차 문의 감소 | 관리자 대상 수기 문의 월 50% 감소 | 도입 전후 문의 카운트 |
| 신청 오입력률 | 반려 사유 "정보 오류" 비율 < 5% | 반려 사유 분류 |
| 조회 API 성능 | p95 < 300ms | APM/서버 로그 |
| 가용성 | ≥ 99.0% (업무시간) | 업타임 모니터링 |
