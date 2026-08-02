아래는 PRD 기반 구현팀 전달용 화면정의서입니다. 파일 생성 없이 응답 본문에만 담았습니다.

**1. IA**

Assumptions:
- 사용자 세션에는 `role`, `businessUnitId`, `userId`가 포함된다.
- 요청 작성자는 자기 요청을 작성/수정/재제출할 수 있다.
- 승인자는 자기 사업부 요청만 승인/반려할 수 있다.
- 감사자는 전체 또는 허용 범위의 감사 이력을 읽기 전용으로 조회한다.
- 기존 업체 링크는 `/vendors/{vendorId}`로 이동한다고 가정한다.

Routes:
| Page ID | 화면 | Route | 주요 역할 | 관련 FR |
|---|---|---|---|---|
| `REQ_LIST` | 요청 목록 | `/vendor-requests` | 요청자, 승인자, 감사자 | FR-103 |
| `REQ_FORM` | 요청 작성/편집 | `/vendor-requests/new`, `/vendor-requests/{id}/edit` | 요청자 | FR-101, FR-102 |
| `REQ_DETAIL` | 요청 상세/승인 | `/vendor-requests/{id}` | 요청자, 승인자, 감사자 | FR-103, FR-104, FR-105 |
| `AUDIT_LOG` | 감사 이력 | `/vendor-requests/{id}/audit`, `/audit/vendor-requests` | 감사자, 승인자 읽기 | FR-105 |

Navigation:
- 요청자: 요청 목록 → 새 요청 작성 → 상세 → 반려 상태면 편집/재제출
- 승인자: 요청 목록 `대기` 필터 → 상세/승인 → 승인 또는 반려
- 감사자: 감사 이력 목록 → 요청 상세 읽기

Status Model:
- `DRAFT` 초안
- `PENDING` 대기
- `APPROVED` 승인
- `REJECTED` 반려
- Allowed transitions:
  - `DRAFT → PENDING`
  - `PENDING → APPROVED`
  - `PENDING → REJECTED`
  - `REJECTED → PENDING`

**2. User Flow**

Flow A: 요청 제출, FR-101/FR-102
1. 요청자가 `/vendor-requests/new` 진입
2. 업체명, 사업자번호, 담당자 이메일 입력
3. `제출하기` 클릭
4. 클라이언트 필수값/형식 검증
5. 서버가 사업자번호 중복 확인
6. 중복 없음: 요청 생성 또는 업데이트 후 `PENDING` 전환, 상세 화면 이동
7. 중복 있음: 제출 중단, 기존 업체 링크 표시, 입력값 보존

Flow B: 반려 후 재제출
1. 요청자가 `REJECTED` 요청 상세 진입
2. 반려 사유 확인
3. `수정하기` 클릭
4. 요청 작성/편집 화면에서 값 수정
5. `다시 제출하기` 클릭
6. 서버 검증 통과 시 `PENDING` 전환, 감사 이력 기록

Flow C: 승인자 승인/반려, FR-103/FR-104/FR-105
1. 승인자가 요청 목록에서 `대기` 필터 선택
2. 자기 사업부 대기 요청 클릭
3. 상세 확인
4. 승인 시 `승인하기` 클릭 → 확인 모달 → 서버 권한 확인 → `APPROVED`
5. 반려 시 반려 사유 입력 → `반려하기` 클릭 → 서버 권한 확인 → `REJECTED`
6. 모든 상태 변경은 감사 이력에 기록

Flow D: 권한 없는 승인, Acceptance
1. 승인자가 다른 사업부 요청 승인 API 호출
2. 서버가 `businessUnitId` 불일치 확인
3. `403 Forbidden` 반환
4. 클라이언트는 “승인 권한이 없습니다” 표시
5. 요청 상태는 기존 상태 유지

Flow E: 네트워크 실패, Acceptance
1. 제출/승인/반려 요청 중 네트워크 실패
2. 입력값 또는 반려 사유 유지
3. 상단 오류 배너와 `재시도` 버튼 표시
4. 재시도 성공 시 정상 전환

**3. Screen Spec**

`REQ_LIST` 요청 목록
- Purpose: 역할별 요청 조회와 다음 행동 진입
- Components: 상태 탭, 사업부 필터, 검색, 요청 테이블/모바일 리스트, 새 요청 버튼
- Columns: 업체명, 사업자번호, 상태, 사업부, 요청자, 수정일, 액션
- Role behavior:
  - 요청자: 자기 요청 중심, `새 요청` 노출
  - 승인자: 자기 사업부 `PENDING` 요청 승인 대기 강조
  - 감사자: 액션 버튼 없이 읽기 전용
- States:
  - loading: 목록 skeleton
  - empty: “조건에 맞는 요청이 없습니다” + 필터 초기화, 요청자는 `새 요청 작성하기`
  - error: “요청 목록을 불러오지 못했습니다” + 재시도
  - no-permission: 접근 권한 없으면 권한 안내 화면
- FR: FR-103

`REQ_FORM` 요청 작성/편집
- Fields:
  - 업체명: required, max 100
  - 사업자번호: required, 숫자/하이픈 허용, 정규화 후 중복 체크
  - 담당자 이메일: required, email format
- Buttons:
  - `임시 저장하기`: `DRAFT`
  - `제출하기` 또는 `다시 제출하기`: `PENDING`
  - `취소`
- Validation:
  - 필수값 누락 시 필드 하단 inline 오류
  - 중복 사업자번호 시 제출 차단, 기존 업체 링크 표시
- Network failure:
  - 입력값 보존
  - 버튼 라벨 `재시도하기`
- States:
  - loading: 편집 진입 시 form skeleton
  - validation: 필드별 `aria-invalid`
  - error: 서버/네트워크 오류 배너
  - success: 제출 성공 toast 후 상세 이동
- FR: FR-101, FR-102

`REQ_DETAIL` 요청 상세/승인
- Sections: 요청 정보, 현재 상태, 반려 사유, 승인 액션, 감사 이력 요약
- 승인자 actions:
  - `승인하기`: 확인 모달 필요
  - `반려하기`: 반려 사유 required, min 5, max 500
- 요청자 actions:
  - `REJECTED` 상태에서 `수정하기`
- 감사자:
  - 모든 입력/액션 disabled 또는 숨김, 읽기 전용
- Unauthorized:
  - 권한 없는 승인/반려 시 403 메시지 표시, 상태 변경 없음
- Responsive:
  - Desktop ≥1024: 요청 정보와 승인 패널 2열
  - Mobile <768: 단일 열, 승인 패널이 요청 정보 아래 배치, 버튼 44px 이상
- States:
  - loading: 상세 skeleton
  - error: “요청 정보를 불러오지 못했습니다”
  - no-permission: “이 요청을 승인할 권한이 없습니다”
  - success: 승인/반려 완료 toast
- FR: FR-103, FR-104, FR-105

`AUDIT_LOG` 감사 이력
- Purpose: 상태 변경과 주요 이벤트 읽기 전용 조회
- Fields: 일시, 행위자, 역할, 변경 전 상태, 변경 후 상태, 사유, 요청 ID
- Filters: 요청 ID, 상태, 행위자, 기간
- Events:
  - 생성
  - 제출
  - 승인
  - 반려
  - 재제출
- States:
  - loading: table skeleton
  - empty: “아직 감사 이력이 없습니다”
  - error: “감사 이력을 불러오지 못했습니다” + 재시도
  - no-permission: 감사 조회 권한 안내
- FR: FR-105

**4. Lo-Fi HTML Wireframe**

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>공급업체 승인 Wireframe</title>
  <style>
    body { margin:0; font-family:system-ui,sans-serif; color:#222; background:#f7f7f7; }
    header, nav, main { padding:16px; }
    header { background:#fff; border-bottom:1px solid #ccc; }
    nav a { margin-right:12px; color:#222; }
    .toolbar, .panel, .card { background:#fff; border:1px solid #ccc; padding:16px; margin-bottom:16px; }
    .grid { display:grid; grid-template-columns: 1fr 320px; gap:16px; }
    label { display:block; margin-top:12px; font-weight:600; }
    input, textarea, select { width:100%; min-height:40px; box-sizing:border-box; margin-top:4px; }
    button { min-height:44px; padding:0 14px; margin:8px 8px 0 0; }
    table { width:100%; border-collapse:collapse; background:#fff; }
    th, td { border:1px solid #ccc; padding:10px; text-align:left; }
    .status-pending { color:#8a5a00; }
    .status-approved { color:#0b6b2b; }
    .status-rejected { color:#a32020; }
    .error { border-color:#a32020; background:#fff4f4; padding:12px; }
    .muted { color:#666; }
    @media (max-width: 767px) {
      .grid { grid-template-columns:1fr; }
      table, thead, tbody, tr, th, td { display:block; }
      th { display:none; }
      td { border-top:0; }
    }
  </style>
</head>
<body>
  <header>
    <h1>공급업체 등록 요청</h1>
  </header>
  <nav aria-label="주요 메뉴">
    <a href="#list">요청 목록</a>
    <a href="#form">요청 작성/편집</a>
    <a href="#detail">요청 상세/승인</a>
    <a href="#audit">감사 이력</a>
  </nav>
  <main>
    <section id="list" class="panel">
      <h2>요청 목록</h2>
      <div class="toolbar">
        <select aria-label="상태 필터"><option>대기</option><option>초안</option><option>승인</option><option>반려</option></select>
        <input aria-label="검색" placeholder="업체명 또는 사업자번호" />
        <button>새 요청 작성하기</button>
      </div>
      <table>
        <thead><tr><th>업체명</th><th>사업자번호</th><th>상태</th><th>사업부</th><th>액션</th></tr></thead>
        <tbody>
          <tr><td>예시상사</td><td>123-45-67890</td><td class="status-pending">대기</td><td>구매1팀</td><td><button>상세 보기</button></td></tr>
        </tbody>
      </table>
    </section>

    <section id="form" class="panel">
      <h2>요청 작성/편집</h2>
      <div class="error">중복 사업자번호입니다. <a href="/vendors/123">기존 업체 보기</a></div>
      <label for="vendorName">업체명</label>
      <input id="vendorName" placeholder="예: 예시상사" />
      <label for="businessNo">사업자번호</label>
      <input id="businessNo" placeholder="예: 123-45-67890" />
      <label for="email">담당자 이메일</label>
      <input id="email" type="email" placeholder="name@example.com" />
      <button>임시 저장하기</button><button>제출하기</button><button>취소</button>
    </section>

    <section id="detail" class="grid">
      <div class="panel">
        <h2>요청 상세</h2>
        <p><strong>업체명</strong> 예시상사</p>
        <p><strong>사업자번호</strong> 123-45-67890</p>
        <p><strong>담당자 이메일</strong> owner@example.com</p>
        <p><strong>상태</strong> <span class="status-pending">대기</span></p>
      </div>
      <aside class="panel" aria-label="승인 처리">
        <h2>승인 처리</h2>
        <label for="rejectReason">반려 사유</label>
        <textarea id="rejectReason" placeholder="반려 시 사유를 입력하세요"></textarea>
        <button>승인하기</button><button>반려하기</button>
        <p class="muted">권한 없는 승인 시 403 처리되며 상태는 유지됩니다.</p>
      </aside>
    </section>

    <section id="audit" class="panel">
      <h2>감사 이력</h2>
      <table>
        <thead><tr><th>일시</th><th>행위자</th><th>변경</th><th>사유</th></tr></thead>
        <tbody>
          <tr><td>2026-07-27 10:00</td><td>approver@corp</td><td>대기 → 반려</td><td>사업자번호 확인 필요</td></tr>
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
```

**5. Dev Handoff**

API Contracts:
| Action | Method/Path | Request | Success | Error |
|---|---|---|---|---|
| 요청 목록 | `GET /api/vendor-requests` | `status,businessUnitId,query` | `VendorRequest[]` | 401/403/5xx |
| 요청 생성 | `POST /api/vendor-requests` | `vendorName,businessNo,email,submit:boolean` | `201 VendorRequest` | 409 duplicate |
| 요청 수정 | `PATCH /api/vendor-requests/{id}` | 변경 필드 | `200 VendorRequest` | 403/409/422 |
| 제출/재제출 | `POST /api/vendor-requests/{id}/submit` | 없음 | `200 PENDING` | 409 duplicate |
| 승인 | `POST /api/vendor-requests/{id}/approve` | 없음 | `200 APPROVED` | 403 |
| 반려 | `POST /api/vendor-requests/{id}/reject` | `reason` | `200 REJECTED` | 403/422 |
| 감사 이력 | `GET /api/vendor-requests/{id}/audit` | 없음 | `AuditEvent[]` | 403 |

Data Model:
```ts
type VendorRequestStatus = 'DRAFT' | 'PENDING' | 'APPROVED' | 'REJECTED';

type VendorRequest = {
  id: string;
  vendorName: string;
  businessNo: string;
  contactEmail: string;
  businessUnitId: string;
  requesterId: string;
  status: VendorRequestStatus;
  rejectionReason?: string;
  createdAt: string;
  updatedAt: string;
};

type AuditEvent = {
  id: string;
  requestId: string;
  actorId: string;
  actorRole: 'REQUESTER' | 'APPROVER' | 'AUDITOR';
  fromStatus?: VendorRequestStatus;
  toStatus?: VendorRequestStatus;
  reason?: string;
  createdAt: string;
};
```

Implementation Notes:
- FR-104는 반드시 서버에서 검증한다. 클라이언트의 버튼 숨김은 보조 UX일 뿐이다.
- 중복 사업자번호는 정규화된 값으로 검사한다.
- `409 duplicate` 응답에는 `existingVendorId`와 표시 가능한 `existingVendorName`을 포함한다.
- 상태 변경 API는 트랜잭션 안에서 상태 업데이트와 감사 이력 생성을 함께 처리한다.
- 네트워크 실패 시 form state와 `rejectReason`을 초기화하지 않는다.
- 승인/반려는 optimistic update를 사용하지 않는다. 실패 시 상태 불일치 위험이 크다.
- 접근성: 모든 input label 연결, 오류 필드는 `aria-invalid`, 오류 메시지는 `aria-describedby`.
- 반응형: `REQ_DETAIL`은 desktop 2열, mobile 단일 열 필수.
- 테스트 우선순위:
  - 권한 없는 승인 `403` 및 상태 미변경
  - 중복 사업자번호 제출 차단 및 기존 업체 링크 표시
  - 네트워크 실패 후 입력값/반려 사유 보존
  - 모바일 승인 상세 단일 열 배치
  - 상태 변경 시 감사 이력 생성
- Requirement Coverage:
  - FR-101: `REQ_FORM`
  - FR-102: `REQ_FORM`
  - FR-103: `REQ_LIST`, `REQ_DETAIL`
  - FR-104: `REQ_DETAIL`, approval/reject API
  - FR-105: `REQ_DETAIL`, `AUDIT_LOG`, mutation APIs