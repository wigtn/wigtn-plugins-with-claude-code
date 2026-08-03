# PRD 계약 — 단일 정본

> 이 파일이 "우리 PRD가 담아야 하는 것"의 **유일한 정본**이다.
> `/prd`(생성)와 `prd-reviewer`(검증)는 둘 다 이 파일을 읽고, 내용을 재진술하지 않는다.
> 재진술이 생기면 `.github/scripts/check_contracts.py`의 `check_prd_contract`가 CI에서 잡는다.
>
> **왜 계약만 남기는가**: 측정 결과 모델은 여기 적힌 항목들을 *요구받지 않으면 쓰지 않는다*
> (State Matrix·User Flow·수용기준·인가명세 = 하네스 없이 0/3). 반대로 "어떻게 찾아라"류
> 지시는 이미 포화라 이득이 없다. 그래서 이 파일에는 **무엇을 내놓아야 하는가만** 적는다.

## 문서 유형 (섹션 활성 규칙)

헤더에 `> **Type**:` 로 명시한다. `prd-reviewer`의 조건부 Critical 판정 입력이다.

| Type | §4.0~4.4 (Scale/SLA) | §5.4 Pages·§5.4.1·§5.5 |
|---|---|---|
| `product-feature` | 필수 | 필수 |
| `internal-backend` | 필수 | `N/A` 한 줄 |
| `refactor` | `N/A` 한 줄 | `N/A` 한 줄 |

모호하면 `product-feature`로 넓게 잡는다 — 섹션 누락이 과잉보다 위험하다.

## 골격

모든 섹션을 채운다. 해당 없으면 `N/A` 한 줄로 마감하되 **왜 N/A인지** 밝힌다.

### 1. Overview
- **1.1 Problem Statement** — 지금 무엇이 문제인가
- **1.2 Goals**
- **1.3 Non-Goals** — 명시적으로 범위 밖인 것
- **1.4 Scope** — 포함/제외 경계

### 2. User Stories
- **2.1 Primary User** — `As a [유형], I want to [행동] so that [이유]`
- **2.2 Acceptance Criteria** — Gherkin(`Given/When/Then`). 정상 경로뿐 아니라 **실패·만료·권한부족 시나리오도** 포함
- **2.3 User Roles** — Role Key를 **영문 소문자 단일 단어**(snake_case 허용)로 단일 선언. 이후 페이지 권한·API 인가·`/screen-spec` Audience가 이 키를 그대로 인용한다.

  | Role Key | 한국어 명칭 | 권한 범위 |
  |---|---|---|

### 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|---|---|---|---|
| FR-001 | | P0/P1/P2 | |

FR 간 **모순이 없어야** 한다(예: "비로그인 열람 허용"과 "모든 조회 인증 필수"는 공존 불가).
우선순위는 MoSCoW: P0 Must / P1 Should / P2 Could / P3 Won't.

### 4. Non-Functional Requirements
- **4.0 Scale Grade** — `Hobby | Startup | Growth | Enterprise` 중 하나 + 근거 한 줄.
  경계: DAU 1,000 미만 Hobby / 1,000~10,000 Startup / 10,000~100,000 Growth / 100,000 이상 Enterprise.
- **4.1 Performance** — **정량 목표**(p95 ms, req/s, 동시성). "빠르게" 같은 정성 표현 금지.
- **4.2 Availability** — 가용성 목표·장애 시 동작
- **4.3 Data** — 보관 기간·개인정보·삭제 정책
- **4.4 Recovery** — RTO/RPO (해당 시)
- **4.5 Security** — 인증 방식, **인가 규칙(어느 역할이 어느 리소스에)**, 전송·저장 보호, 입력 검증

### 5. Technical Design
- **5.1 API Specification** — 엔드포인트별 Request / Response / Error / **인가 주체**
- **5.2 Database Schema**
- **5.3 Architecture**

#### 5.4 Pages

| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|---|---|---|---|---|---|---|

- `Audience`는 §2.3의 Role Key를 그대로 쓴다
- **`Has FE Components: Yes` 행이 1개 이상이면 §5.4.1·§5.5는 필수**이고, `/screen-spec`을 권장한다
- 전부 `No`이거나 백엔드 전용이면 `N/A`

#### 5.4.1 Page State Matrix

**조건**: §5.4에 `Has FE Components: Yes`가 1개 이상일 때 필수.

| Route | loading | empty | error | success | no-permission | 비고 |
|---|---|---|---|---|---|---|

상태 정의 — `loading`: fetch 중 / `empty`: 정상 응답 0건 / `error`: 4xx·5xx 또는 검증 실패 / `success`: 결과 ≥1건 / `no-permission`: 인증됐으나 권한 부족.

#### 5.5 User Flow

**조건**: §5.4에 `Has FE Components: Yes`가 1개 이상일 때 필수.

```mermaid
flowchart TD
```
페이지 간 이동과 **분기 조건**을 노드로. §2.2 시나리오가 경로로 드러나야 한다.

### 6. Implementation Phases
Phase별 태스크와 **Deliverable**. FR 의존성 순서를 지킨다(P0 FR이 뒤 Phase에 배치되지 않도록).

### 7. Success Metrics

| Metric | Target | Measurement |
|---|---|---|

---

## 검증 계약 (`prd-reviewer`가 Critical로 취급하는 것)

아래는 **누락 시 Critical**이다. 조건부 항목은 조건이 성립할 때만 발화한다.

| ID | 항목 | 조건 |
|---|---|---|
| C-1 | §2.3 User Roles 선언 | 항상 |
| C-2 | §2.2 수용 기준(Gherkin) | 항상 |
| C-3 | §3 FR 테이블 + FR 간 무모순 | 항상 |
| C-4 | §4.1 정량 NFR | `refactor` 제외 |
| C-5 | §4.5 인가 규칙 명시 | 항상 |
| C-6 | §5.4 Pages 테이블 | `refactor` 제외 |
| C-7 | §5.4.1 Page State Matrix | `Has FE Components: Yes` ≥1 |
| C-8 | §5.5 User Flow (Mermaid) | `Has FE Components: Yes` ≥1 |
| C-9 | §1.3 Non-Goals | 항상 |
| C-10 | §6 Implementation Phases | 항상 |

> 이 10항목은 `.github/evals/score_prd.py`의 채점 항목과 1:1 대응한다.
> 계약을 고치면 채점기도 같이 고쳐야 하며, 불일치는 CI가 잡는다.
