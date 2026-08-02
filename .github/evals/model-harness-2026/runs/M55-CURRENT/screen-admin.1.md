## 1. IA

### Roles
- 요청자: 공급업체 등록 요청 생성, 초안 수정, 제출, 반려 요청 재제출
- 승인자: 자기 사업부의 대기 요청 조회, 승인, 반려
- 감사자: 감사 이력 읽기 전용 조회

### Navigation
```text
공급업체 승인
├─ 요청 목록
│  ├─ 내 요청
│  └─ 사업부 대기 요청
├─ 요청 작성/편집
├─ 요청 상세/승인
└─ 감사 이력
```

### Pages
| Page ID | 화면 | Route 예시 | 주요 역할 | 관련 요구사항 |
|---|---|---|---|---|
| SUP-001 | 요청 목록 | `/supplier-requests` | 요청자, 승인자 | FR-101, FR-103 |
| SUP-002 | 요청 작성/편집 | `/supplier-requests/new`, `/supplier-requests/:id/edit` | 요청자 | FR-101, FR-102 |
| SUP-003 | 요청 상세/승인 | `/supplier-requests/:id` | 요청자, 승인자, 감사자 | FR-103, FR-104, FR-105 |
| SUP-004 | 감사 이력 | `/supplier-requests/:id/audit-log` | 감사자, 승인자 | FR-105 |

### Status Model
```text
초안 → 대기 → 승인
          └→ 반려 → 초안/편집 → 대기
```

### Assumptions
- 요청자는 자기 요청만 작성/수정 가능하다.
- 승인자는 자기 사업부 요청만 승인/반려 가능하다.
- 감사자는 요청 본문과 감사 이력을 읽을 수 있지만 변경 액션은 없다.
- 중복 사업자번호 검사는 제출 시 서버에서 최종 검증하고, 입력 중에는 보조 검증으로만 사용한다.

---

## 2. User Flow

### Flow A. 요청 작성 및 제출
1. 요청자가 `요청 목록`에서 `새 요청 작성` 선택
2. `요청 작성/편집` 진입
3. 업체명, 사업자번호, 담당자 이메일 입력
4. `제출하기` 클릭
5. 서버가 사업자번호 중복 확인
6. 중복 없음: 상태 `대기`로 저장, 상세 화면으로 이동
7. 중복 있음: 제출 차단, 기존 업체 링크 표시

관련 요구사항: FR-101, FR-102  
수용 기준: 중복 사업자번호에서는 제출되지 않는다.

### Flow B. 반려 요청 수정 후 재제출
1. 요청자가 `요청 목록`에서 상태 `반려` 요청 선택
2. `요청 상세`에서 반려 사유 확인
3. `수정하기` 선택
4. 입력값 수정
5. `다시 제출하기` 클릭
6. 상태 `대기`로 전환
7. 감사 이력에 재제출 기록 생성

관련 요구사항: FR-101, FR-105

### Flow C. 승인자 승인
1. 승인자가 `요청 목록`의 `사업부 대기 요청` 탭 진입
2. 대기 요청 선택
3. `요청 상세/승인`에서 정보 확인
4. `승인하기` 클릭
5. 서버가 사업부 권한 확인
6. 권한 있음: 상태 `승인`으로 변경
7. 감사 이력에 승인 기록 생성

관련 요구사항: FR-103, FR-104, FR-105

### Flow D. 승인자 반려
1. 승인자가 대기 요청 상세 진입
2. `반려하기` 선택
3. 반려 사유 입력
4. `반려 확정` 클릭
5. 서버가 사업부 권한 확인
6. 권한 있음: 상태 `반려`로 변경
7. 감사 이력에 반려 사유 포함 기록 생성

관련 요구사항: FR-103, FR-104, FR-105  
수용 기준: 네트워크 실패 시 반려 사유를 보존하고 재시도할 수 있다.

### Flow E. 권한 없는 승인 시도
1. 승인자가 URL 직접 접근 또는 오래된 링크로 타 사업부 요청 상세 진입
2. 승인 버튼 클릭
3. 서버가 403 반환
4. 화면은 권한 없음 메시지 표시
5. 요청 상태는 변경되지 않음

관련 요구사항: FR-104  
수용 기준: 권한 없는 승인 시 403이고 상태가 바뀌지 않는다.

### Flow F. 감사 이력 조회
1. 감사자가 요청 상세 진입
2. `감사 이력 보기` 선택
3. 상태 변경 이력, 수행자, 시각, 사유 조회
4. 변경 액션은 표시하지 않음

관련 요구사항: FR-105

---

## 3. Screen Spec

### SUP-001 요청 목록

#### Purpose
공급업체 등록 요청을 상태별로 탐색하고, 새 요청 작성 또는 승인 대상 상세로 이동한다.

#### Layout
- Header: 화면 제목 `공급업체 요청`
- Primary CTA: `새 요청 작성`
- Tabs:
  - `내 요청`
  - `사업부 대기 요청`
- Filters:
  - 상태: 전체, 초안, 대기, 승인, 반려
  - 검색: 업체명, 사업자번호
- List columns:
  - 업체명
  - 사업자번호
  - 상태
  - 사업부
  - 요청자
  - 최근 변경일
  - 액션: `상세 보기`

#### Actions
| 액션 | 조건 | 결과 |
|---|---|---|
| 새 요청 작성 | 요청자 | SUP-002 이동 |
| 상세 보기 | 조회 권한 있음 | SUP-003 이동 |
| 필터 적용 | 모든 역할 | 목록 갱신 |
| 사업부 대기 요청 탭 | 승인자 | 자기 사업부의 `대기` 요청만 표시 |

#### States
- loading: 목록 skeleton row 5개 표시
- empty: `조건에 맞는 요청이 없습니다.` + `필터 초기화`
- error: `요청 목록을 불러오지 못했습니다.` + `다시 시도`
- success: 목록 표시
- no-permission: 승인자 탭 접근 권한 없으면 탭 숨김 또는 `권한이 없습니다.` 안내

---

### SUP-002 요청 작성/편집

#### Purpose
요청자가 업체 등록 요청을 작성, 저장, 제출, 재제출한다.

#### Fields
| 필드 | 타입 | 필수 | 검증 |
|---|---:|---:|---|
| 업체명 | text | Y | 1자 이상, 앞뒤 공백 제거 |
| 사업자번호 | text | Y | 숫자 10자리 또는 하이픈 포함 형식 허용 후 정규화 |
| 담당자 이메일 | email | Y | 이메일 형식 |
| 반려 사유 | readonly text | N | 반려 상태 편집 시 표시 |

#### Buttons
| 버튼 | 조건 | 동작 |
|---|---|---|
| 임시 저장 | 신규/초안/반려 | 상태 `초안` 저장 |
| 제출하기 | 신규/초안 | 중복 검사 후 상태 `대기` |
| 다시 제출하기 | 반려 | 중복 검사 후 상태 `대기` |
| 취소 | 항상 | 목록 또는 상세로 복귀 |

#### Duplicate Handling
- 제출 시 서버에서 중복 사업자번호 확인
- 중복이면 저장/제출하지 않음
- 상단 배너: `이미 등록된 사업자번호입니다.`
- 기존 업체 링크: `기존 업체 보기`
- 사업자번호 필드에 inline error 표시

#### Network Failure
- 입력값을 화면 상태에 보존
- 버튼 loading 해제
- 배너: `네트워크 연결 문제로 제출하지 못했습니다. 입력 내용은 유지됩니다.`
- CTA: `다시 시도`

#### States
- loading: 편집 대상 로딩 시 form skeleton
- validation: 필드별 inline error
- error: 저장/제출 실패 배너 + 재시도
- success: 저장 성공 toast, 제출 성공 시 SUP-003 이동
- no-permission: 자기 요청이 아니거나 수정 불가 상태면 읽기 전용 안내

---

### SUP-003 요청 상세/승인

#### Purpose
요청 정보, 현재 상태, 반려 사유, 승인/반려 액션을 제공한다.

#### Layout
- Summary:
  - 상태 badge
  - 업체명
  - 사업자번호
  - 담당자 이메일
  - 사업부
  - 요청자
  - 생성일/최근 변경일
- Status timeline:
  - 초안
  - 대기
  - 승인 또는 반려
- Approval panel:
  - `승인하기`
  - `반려하기`
  - 반려 사유 textarea
- Secondary actions:
  - `수정하기`
  - `감사 이력 보기`

#### Role Rules
| 역할 | 상태 | 허용 액션 |
|---|---|---|
| 요청자 | 초안 | 수정, 제출 |
| 요청자 | 반려 | 수정, 다시 제출 |
| 요청자 | 대기/승인 | 읽기 |
| 승인자 | 대기 + 자기 사업부 | 승인, 반려 |
| 승인자 | 타 사업부 | 읽기 또는 403 |
| 감사자 | 모든 허용 범위 | 읽기, 감사 이력 |

#### Approval / Reject Rules
- 승인/반려 요청은 반드시 서버 권한 검사를 통과해야 한다.
- 반려 사유는 필수이며 1자 이상 입력해야 한다.
- 승인/반려 성공 시 감사 이력 생성.
- 403 응답 시 상태는 이전 값으로 유지하고 화면에 권한 오류 표시.

#### Responsive
- Desktop ≥1024px: 상세 정보와 승인 패널 2열
- Mobile <768px: 단일 열, 승인 패널은 상세 정보 아래 배치
- 모바일 버튼 터치 영역 최소 44px

#### States
- loading: 상세 영역 skeleton
- error: `요청 정보를 불러오지 못했습니다.` + `다시 시도`
- validation: 반려 사유 미입력 시 textarea inline error
- success: 상세 정보 표시
- no-permission: 403 시 `이 요청을 승인할 권한이 없습니다.` + `목록으로 돌아가기`

---

### SUP-004 감사 이력

#### Purpose
요청의 모든 상태 변경 기록을 읽기 전용으로 제공한다.

#### Columns
| 컬럼 | 설명 |
|---|---|
| 일시 | 변경 발생 시각 |
| 수행자 | 사용자명/이메일 |
| 역할 | 요청자/승인자/시스템 |
| 변경 전 상태 | 초안/대기/승인/반려 |
| 변경 후 상태 | 초안/대기/승인/반려 |
| 사유 | 반려 사유 또는 시스템 메시지 |
| 요청 ID | 추적용 |

#### States
- loading: timeline skeleton
- empty: `아직 상태 변경 이력이 없습니다.`
- error: `감사 이력을 불러오지 못했습니다.` + `다시 시도`
- success: timeline/table 표시
- no-permission: 감사 이력 조회 권한 없으면 권한 안내

---

## 4. Lo-fi HTML Wireframe

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>공급업체 승인 Wireframe</title>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; color: #222; background: #f6f6f6; }
    header, nav, main { padding: 16px; }
    header { background: #fff; border-bottom: 1px solid #ddd; }
    nav { display: flex; gap: 8px; flex-wrap: wrap; background: #fafafa; border-bottom: 1px solid #ddd; }
    button, input, select, textarea, a.button {
      min-height: 44px; padding: 8px 12px; border: 1px solid #999; background: #fff; color: #222;
    }
    .primary { background: #222; color: #fff; }
    .danger { border-color: #a33; color: #a33; }
    .success { border-color: #286b3b; color: #286b3b; }
    .page { display: none; max-width: 1120px; margin: 0 auto; }
    .page:target { display: block; }
    .page:first-of-type { display: block; }
    .toolbar { display: flex; gap: 8px; flex-wrap: wrap; margin: 16px 0; }
    .panel { background: #fff; border: 1px solid #ddd; padding: 16px; margin: 16px 0; }
    .grid { display: grid; grid-template-columns: 1fr 360px; gap: 16px; }
    .row { display: grid; grid-template-columns: 1.2fr 1fr .7fr .8fr .8fr; gap: 8px; padding: 12px 0; border-bottom: 1px solid #ddd; }
    label { display: block; margin-top: 12px; font-weight: 600; }
    input, select, textarea { width: 100%; box-sizing: border-box; margin-top: 4px; }
    .badge { display: inline-block; padding: 4px 8px; border: 1px solid #777; background: #eee; }
    .error { border-left: 4px solid #a33; background: #fff5f5; padding: 12px; }
    .muted { color: #666; }
    @media (max-width: 767px) {
      .grid, .row { display: block; }
      .row > div { padding: 4px 0; }
      .toolbar { display: grid; grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>공급업체 승인</h1>
  </header>

  <nav aria-label="주요 화면">
    <a class="button" href="#list">요청 목록</a>
    <a class="button" href="#form">요청 작성/편집</a>
    <a class="button" href="#detail">요청 상세/승인</a>
    <a class="button" href="#audit">감사 이력</a>
  </nav>

  <main>
    <section id="list" class="page" aria-labelledby="list-title">
      <h2 id="list-title">요청 목록</h2>
      <div class="toolbar">
        <button class="primary">새 요청 작성</button>
        <select aria-label="상태 필터">
          <option>전체 상태</option><option>초안</option><option>대기</option><option>승인</option><option>반려</option>
        </select>
        <input aria-label="검색어" placeholder="업체명 또는 사업자번호" />
        <button>필터 적용</button>
      </div>
      <div class="panel">
        <div class="row" aria-label="요청 행">
          <div>ABC 산업</div><div>123-45-67890</div><div><span class="badge">대기</span></div><div>구매사업부</div><div><a href="#detail">상세 보기</a></div>
        </div>
        <div class="row">
          <div>한빛테크</div><div>987-65-43210</div><div><span class="badge">반려</span></div><div>구매사업부</div><div><a href="#detail">상세 보기</a></div>
        </div>
      </div>
    </section>

    <section id="form" class="page" aria-labelledby="form-title">
      <h2 id="form-title">요청 작성/편집</h2>
      <div class="panel error">
        이미 등록된 사업자번호입니다. <a href="#">기존 업체 보기</a>
      </div>
      <form class="panel">
        <label for="supplier-name">업체명</label>
        <input id="supplier-name" placeholder="예: ABC 산업" required />

        <label for="business-number">사업자번호</label>
        <input id="business-number" placeholder="예: 123-45-67890" required aria-invalid="true" />

        <label for="contact-email">담당자 이메일</label>
        <input id="contact-email" type="email" placeholder="name@example.com" required />

        <label for="reject-reason">반려 사유</label>
        <textarea id="reject-reason" readonly>사업자번호 확인이 필요합니다.</textarea>

        <div class="toolbar">
          <button type="button">임시 저장</button>
          <button type="submit" class="primary">제출하기</button>
          <button type="button">취소</button>
        </div>
      </form>
    </section>

    <section id="detail" class="page" aria-labelledby="detail-title">
      <h2 id="detail-title">요청 상세/승인</h2>
      <div class="grid">
        <article class="panel">
          <span class="badge">대기</span>
          <h3>ABC 산업</h3>
          <p>사업자번호: 123-45-67890</p>
          <p>담당자 이메일: owner@example.com</p>
          <p>사업부: 구매사업부</p>
          <p class="muted">초안 → 대기 → 승인/반려</p>
          <a href="#audit">감사 이력 보기</a>
        </article>

        <aside class="panel" aria-label="승인 패널">
          <h3>승인 처리</h3>
          <button class="success">승인하기</button>
          <label for="reason">반려 사유</label>
          <textarea id="reason" placeholder="반려 사유를 입력하세요"></textarea>
          <button class="danger">반려 확정</button>
          <div class="error">이 요청을 승인할 권한이 없습니다.</div>
        </aside>
      </div>
    </section>

    <section id="audit" class="page" aria-labelledby="audit-title">
      <h2 id="audit-title">감사 이력</h2>
      <div class="panel">
        <ol>
          <li>2026-07-27 09:10 요청자: 초안 → 대기</li>
          <li>2026-07-27 10:05 승인자: 대기 → 반려, 사유: 사업자번호 확인 필요</li>
          <li>2026-07-27 11:20 요청자: 반려 → 대기</li>
        </ol>
      </div>
    </section>
  </main>
</body>
</html>
```

---

## 5. Dev Handoff

### API Contracts

#### Create / Save Draft
```http
POST /api/supplier-requests
```

Request:
```json
{
  "supplierName": "ABC 산업",
  "businessNumber": "1234567890",
  "contactEmail": "owner@example.com",
  "submit": false
}
```

Response:
```json
{
  "id": "sr_123",
  "status": "DRAFT"
}
```

#### Submit
```http
POST /api/supplier-requests/{id}/submit
```

Success:
```json
{
  "id": "sr_123",
  "status": "PENDING"
}
```

Duplicate:
```http
409 Conflict
```
```json
{
  "code": "DUPLICATE_BUSINESS_NUMBER",
  "message": "이미 등록된 사업자번호입니다.",
  "existingSupplierId": "sup_456",
  "existingSupplierUrl": "/suppliers/sup_456"
}
```

#### Approve
```http
POST /api/supplier-requests/{id}/approve
```

Unauthorized:
```http
403 Forbidden
```
상태 변경 없음.

#### Reject
```http
POST /api/supplier-requests/{id}/reject
```

Request:
```json
{
  "reason": "사업자번호 확인이 필요합니다."
}
```

Validation:
```http
422 Unprocessable Entity
```
반려 사유가 비어 있으면 반환.

#### Audit Log
```http
GET /api/supplier-requests/{id}/audit-log
```

Response:
```json
[
  {
    "id": "log_1",
    "actorEmail": "approver@example.com",
    "actorRole": "APPROVER",
    "fromStatus": "PENDING",
    "toStatus": "REJECTED",
    "reason": "사업자번호 확인이 필요합니다.",
    "createdAt": "2026-07-27T10:05:00+09:00"
  }
]
```

### Frontend State Requirements
- 제출/승인/반려 mutation 중 버튼 disabled + `처리 중...` 라벨 사용
- 네트워크 실패 시 form state 유지
- 반려 모달 또는 패널의 textarea 값은 실패 후에도 유지
- 403 발생 시 optimistic update 금지 또는 즉시 rollback
- 목록은 mutation 성공 후 invalidate/refetch

### Validation Rules
| Field | Rule | Message |
|---|---|---|
| supplierName | required | 업체명을 입력하세요. |
| businessNumber | required, normalized 10 digits | 사업자번호 10자리를 입력하세요. |
| contactEmail | required, email | 올바른 이메일을 입력하세요. |
| rejectReason | reject 시 required | 반려 사유를 입력하세요. |

### Access Control
- 클라이언트는 버튼 표시를 역할/상태 기준으로 제한한다.
- 서버는 반드시 사업부 권한을 재검증한다.
- 승인/반려 API는 권한 없는 요청에 403을 반환하고 상태를 변경하지 않는다.
- 감사 이력은 모든 상태 변경마다 서버에서 append-only로 기록한다.

### Acceptance Mapping
| 수용 기준 | 구현 포인트 |
|---|---|
| 권한 없는 승인 시 403이고 상태가 바뀌지 않는다 | approve/reject 서버 권한 검증, 클라이언트 rollback |
| 중복 사업자번호에서는 제출되지 않는다 | submit API 409, 기존 업체 링크 노출 |
| 네트워크 실패 시 입력과 반려 사유를 보존하고 재시도할 수 있다 | local form state 유지, retry CTA |
| 모바일에서는 승인 상세가 단일 열로 재배치된다 | SUP-003 `<768px` 단일 column |

### A11y / Responsive Checklist
- 모든 input/textarea에 label 연결
- loading/error 상태에 `aria-busy`, `aria-invalid` 적용
- 모바일 터치 타깃 44px 이상
- 모바일 상세 화면은 1열, 가로 스크롤 없음
- 아이콘 버튼을 쓰는 경우 `aria-label` 필수

### Open Questions
- 기존 업체 링크는 공급업체 마스터 상세로 이동하는지, 등록 요청 상세로 이동하는지 확인 필요
- 승인자가 타 사업부 요청 상세를 볼 수 있는지, 아예 403 처리할지 정책 결정 필요
- 임시 저장이 필수 기능인지, 제출 전 클라이언트 초안만 허용할지 결정 필요