# PRD 골격 (A2 — 실험용 lean 버전)

아래 구조로 PRD를 작성한다. **모든 섹션을 채운다.** 해당 없으면 "N/A" 한 줄로 마감하되, 왜 N/A인지 밝힌다.

---

## 1. Overview
- **1.1 Problem Statement** — 지금 무엇이 문제인가
- **1.2 Goals** — 무엇을 달성하는가
- **1.3 Non-Goals** — 명시적으로 범위 밖인 것
- **1.4 Scope** — 포함/제외 경계

## 2. User Stories
- **2.1 Primary User** — `As a [유형], I want to [행동] so that [이유]`
- **2.2 Acceptance Criteria** — Gherkin. 정상 경로뿐 아니라 **실패·만료·권한부족 시나리오도** 포함
  ```
  Scenario: [명]
    Given [전제]
    When [행동]
    Then [결과]
  ```
- **2.3 User Roles** — 역할 키를 영문 소문자로 **단일 선언**. 이후 페이지 권한·API 인가에서 이 키를 그대로 인용한다.

  | Role Key | 한국어 명칭 | 권한 범위 |
  |---|---|---|

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|---|---|---|---|
| FR-001 | | P0/P1/P2 | |

FR 간 **모순이 없어야** 한다(예: "비로그인 열람 허용"과 "모든 조회 인증 필수"가 공존할 수 없다).

## 4. Non-Functional Requirements
- **4.0 Scale Grade** — `Hobby | Startup | Growth | Scale` 중 하나를 명시. 근거(예상 사용자 수)를 한 줄로.
- **4.1 Performance** — **정량 목표**로 쓴다(p95 응답시간 ms, 처리량 req/s, 동시성). "빠르게", "기다릴 만한 수준" 같은 정성 표현 금지.
- **4.2 Availability** — 가용성 목표·장애 시 동작
- **4.3 Data** — 보관 기간·개인정보·삭제 정책
- **4.4 Recovery** — 백업·복구 (해당 시)
- **4.5 Security** — 인증 방식, **인가 규칙(어느 역할이 어느 리소스에)**, 전송·저장 보호, 입력 검증

## 5. Technical Design
- **5.1 API Specification** — 엔드포인트별 **인가 주체**를 함께 명시
- **5.2 Database Schema**
- **5.3 Architecture**

### 5.4 Pages

| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|---|---|---|---|---|---|---|

- `Audience`는 §2.3의 Role Key를 그대로 쓴다
- **`Has FE Components: Yes` 행이 1개 이상이면 §5.4.1·§5.5를 반드시 작성한다**
- 백엔드/API 전용이면 "N/A"

### 5.4.1 Page State Matrix

**조건**: §5.4에 `Has FE Components: Yes` 가 1개 이상일 때 필수.

| Route | loading | empty | error | success | no-permission | 비고 |
|---|---|---|---|---|---|---|

상태 정의 — `loading`: fetch 중 / `empty`: 정상 응답 0건 / `error`: 4xx·5xx 또는 검증 실패 / `success`: 결과 ≥1건 / `no-permission`: 인증됐으나 권한 부족.

### 5.5 User Flow

**조건**: §5.4에 `Has FE Components: Yes` 가 1개 이상일 때 필수.

```mermaid
flowchart TD
```
페이지 간 이동과 **분기 조건**을 노드로. §2.2 시나리오가 경로로 드러나야 한다.

## 6. Implementation Phases
Phase별 태스크와 **Deliverable**. FR 의존성 순서를 지킨다(P0 FR이 뒤 Phase에 배치되지 않도록).

## 7. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
