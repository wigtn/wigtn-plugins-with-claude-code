# PRD: 사내 문서 공유 (defective fixture)

> **Version**: 1.0 · **Type**: feature · **Scale Grade**: Startup

## 1. Overview

### 1.1 Problem Statement

팀원들이 문서를 이메일과 메신저로 주고받아 최신본이 어느 것인지 알 수 없다.
사내 문서를 한 곳에 모으고 링크로 공유한다.

### 1.2 Goals

- 문서 업로드·조회·공유를 한 화면에서
- 최신본이 무엇인지 항상 명확
- 외부 유출 방지

### 1.3 Non-Goals

- 실시간 공동 편집
- 오프라인 동기화

## 2. User Stories

### 2.1 Primary User

**사내 구성원**: 문서를 올리고 링크로 공유한다.
**관리자**: 부적절한 문서를 삭제한다.

### 2.2 Acceptance Criteria

```
Scenario: 문서 업로드
  Given 로그인한 사용자가
  When 파일을 업로드하면
  Then 문서 목록에 나타난다

Scenario: 링크 공유
  Given 업로드된 문서가 있고
  When 공유 링크를 생성하면
  Then 링크를 받은 사람이 문서를 볼 수 있다
```

### 2.3 User Roles

| Role Key | 한국어 명칭 | 권한 범위 |
|----------|------------|----------|
| `member` | 사내 구성원 | 업로드, 자기 문서 조회/삭제, 공유 링크 생성 |
| `admin` | 관리자 | 전체 문서 조회, 임의 문서 삭제 |
| `guest` | 링크 수신자 | 공유 링크로 문서 열람 |

## 3. Functional Requirements

| ID | Requirement | Priority |
|----|------------|----------|
| FR-001 | 사용자는 파일(PDF/DOCX, 최대 50MB)을 업로드할 수 있다 | P0 |
| FR-002 | 업로드된 문서는 목록에 최신순으로 표시된다 | P0 |
| FR-003 | 공유 링크를 받은 사람은 **로그인 없이** 문서를 열람할 수 있다 | P0 |
| FR-004 | 사용자는 자기가 올린 문서를 삭제할 수 있다 | P1 |
| FR-005 | 관리자는 `DELETE /api/documents/{id}` 로 임의의 문서를 삭제할 수 있다 | P1 |
| FR-006 | 문서 검색(제목 부분 일치)을 제공한다 | P2 |
| FR-007 | **모든 문서 조회 요청은 인증을 거쳐야 한다** | P0 |

## 4. Non-Functional Requirements

### 4.1 Performance

- 업로드는 사용자가 기다릴 만한 수준이어야 한다.

### 4.2 Security

- HTTPS 적용
- 업로드 파일 확장자 검사

## 5. Technical Design

### 5.1 Stack

- Next.js 16 (App Router) / PostgreSQL / S3 호환 스토리지

### 5.2 API

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/documents` | 업로드 |
| GET | `/api/documents` | 목록 |
| GET | `/api/documents/{id}` | 상세 |
| DELETE | `/api/documents/{id}` | 삭제 |
| POST | `/api/documents/{id}/share` | 공유 링크 생성 |

### 5.4 Pages

| Page | Route | Has FE Components | 설명 |
|------|-------|-------------------|------|
| 문서 목록 | `/documents` | Yes | 업로드 + 목록 + 검색 |
| 문서 상세 | `/documents/[id]` | Yes | 미리보기 + 공유 |
| 공유 열람 | `/s/[token]` | Yes | 링크 수신자용 열람 화면 |

## 6. Implementation Phases

- [ ] Phase 1: 업로드·목록
- [ ] Phase 2: 공유 링크
- [ ] Phase 3: 검색·관리자 삭제
