# PRD: 팀 일정 조율 서비스 (digging fixture)

> **Version**: 1.0 · **Type**: product-feature · **Scale Grade**: Growth

## 1. Overview

### 1.1 Problem Statement

여러 팀이 회의 시간을 잡을 때 메신저로 가능한 시간을 주고받느라 왕복이 길다.
참석자가 각자 가능 시간을 입력하면 겹치는 구간을 자동으로 찾아준다.

### 1.2 Goals
- 회의 조율 왕복을 1회로 줄인다
- 외부 참석자(고객사)도 로그인 없이 참여할 수 있다
- 캘린더(Google/Outlook)와 양방향 동기화한다

### 1.3 Non-Goals
- 화상회의 기능
- 회의록 작성

## 2. User Stories

### 2.1 Primary User
**주최자**: 회의를 만들고 후보 시간대를 연다.
**참석자**: 가능한 시간을 표시한다.
**외부 참석자**: 링크로 들어와 가능 시간만 표시한다.

### 2.2 Acceptance Criteria

```
Scenario: 회의 생성
  Given 로그인한 주최자가
  When 후보 시간대 5개를 선택하면
  Then 공유 링크가 발급된다

Scenario: 가능 시간 표시
  Given 참석자가 링크로 접근해
  When 가능한 시간을 체크하면
  Then 집계 화면에 즉시 반영된다
```

### 2.3 User Roles

| Role Key | 한국어 명칭 | 권한 범위 |
|----------|------------|----------|
| `organizer` | 주최자 | 회의 생성/수정/삭제, 전체 응답 조회 |
| `participant` | 사내 참석자 | 자기 응답 작성/수정 |
| `guest` | 외부 참석자 | 링크로 응답 작성 |

## 3. Functional Requirements

| ID | Requirement | Priority | Dependencies |
|----|------------|----------|--------------|
| FR-001 | 주최자는 후보 시간대를 최대 20개까지 등록한다 | P0 | - |
| FR-002 | 참석자는 각 후보에 가능/불가/미정을 표시한다 | P0 | FR-001 |
| FR-003 | 집계 결과는 참석자 응답이 바뀌면 **실시간(1초 이내)**으로 모든 접속자에게 반영된다 | P0 | FR-002 |
| FR-004 | 외부 참석자는 이메일 인증 없이 링크만으로 응답한다 | P0 | FR-002 |
| FR-005 | 주최자는 확정 시간을 선택하고 참석자 전원에게 메일을 보낸다 | P1 | FR-003 |
| FR-006 | Google/Outlook 캘린더와 **양방향 동기화**한다(외부 일정 변경이 후보 가용성에 반영) | P1 | FR-001 |
| FR-007 | 참석자는 자기 응답 이력을 조회한다 | P2 | FR-002 |
| FR-008 | 회의 데이터는 확정 후 **90일 뒤 자동 삭제**된다 | P2 | FR-005 |

## 4. Non-Functional Requirements

### 4.0 Scale Grade
Growth — 일일 활성 사용자 3만, 동시 접속 2,000, 회의 10만 건/월.

### 4.1 Performance SLA

| 지표 | 목표 |
|------|------|
| 집계 화면 로드 p95 | < 500ms |
| 응답 반영 지연 | < 1s |
| 동시 접속 | 2,000 |

### 4.2 Availability
월 99.5%.

### 4.3 Data Requirements
회의·응답 데이터는 PostgreSQL. 참석자 이메일은 확정 메일 발송에 사용.

### 4.5 Security
- 전 구간 HTTPS
- 공유 링크는 추측 불가능한 UUID v4
- 사내 참석자는 SSO 인증

## 5. Technical Design

### 5.1 Stack
Next.js 16 (App Router, 서버리스 배포) / PostgreSQL / Redis

### 5.2 API

| Method | Path | 인가 | 설명 |
|--------|------|------|------|
| POST | `/api/meetings` | organizer | 회의 생성 |
| GET | `/api/meetings/{id}` | organizer \| token | 상세 + 집계 |
| POST | `/api/meetings/{id}/responses` | participant \| token | 응답 저장 |
| GET | `/api/meetings/{id}/stream` | organizer \| token | 집계 실시간 스트림 |
| DELETE | `/api/meetings/{id}` | organizer | 삭제 |

### 5.4 Pages

| Route | Audience | Auth | Linked FRs | Has FE Components | Primary State | Responsive |
|-------|----------|------|-----------|-------------------|---------------|-----------|
| `/meetings/new` | organizer | Required | FR-001 | Yes | success | Desktop / Mobile |
| `/m/[token]` | participant, guest | Optional | FR-002, FR-004 | Yes | success / error | Desktop / Mobile |
| `/meetings/[id]` | organizer | Required | FR-003, FR-005 | Yes | success | Desktop / Mobile |

### 5.4.1 Page State Matrix

| Route | loading | empty | error | success | no-permission |
|-------|---------|-------|-------|---------|---------------|
| `/meetings/new` | ✓ | - | ✓ | ✓ | ✓ |
| `/m/[token]` | ✓ | - | ✓ | ✓ | ✓ |
| `/meetings/[id]` | ✓ | ✓ | ✓ | ✓ | ✓ |

### 5.5 User Flow

```mermaid
flowchart TD
  Start([주최자 로그인]) --> New[/meetings/new]
  New -->|후보 등록| Link[공유 링크 발급]
  Link --> Share[참석자에게 전달]
  Share --> Respond[/m/token 응답]
  Respond --> Agg[/meetings/id 집계]
  Agg -->|확정| Mail[전원 메일 발송]
```

## 6. Implementation Phases

### Phase 1: MVP
- [ ] FR-001, FR-002, FR-004
**Deliverable**: 회의 생성 + 링크 응답

### Phase 2
- [ ] FR-003, FR-005
**Deliverable**: 실시간 집계 + 확정 메일

### Phase 3
- [ ] FR-006, FR-007, FR-008
**Deliverable**: 캘린더 연동, 이력, 보존정책

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 조율 왕복 횟수 | 1회 | 회의당 평균 응답 라운드 |
| 링크 응답률 | 70% | 발송 대비 응답 |
