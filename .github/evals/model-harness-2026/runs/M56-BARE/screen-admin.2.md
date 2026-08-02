아래 문서는 별도 디자인 해석 없이 구현에 착수할 수 있도록 화면, 권한, 상태 전이, 오류 처리와 API 계약까지 연결한 화면정의서다.

## 1. IA

### 1.1 정보 구조

```text
공급업체 승인
├─ 요청 목록
│  ├─ 상태/검색 필터
│  ├─ 요청 작성
│  └─ 요청 상세
├─ 요청 작성/편집
│  ├─ 업체 정보
│  ├─ 중복 업체 확인
│  └─ 임시 저장/제출/재제출
├─ 요청 상세/승인
│  ├─ 업체 및 요청 정보
│  ├─ 승인/반려
│  └─ 상태 변경 이력
└─ 감사 이력
   ├─ 이력 검색/필터
   └─ 변경 상세
```

### 1.2 역할별 접근 권한

| 기능 | 요청자 | 승인자 | 감사자 |
|---|---:|---:|---:|
| 본인 요청 목록 조회 | 가능 | 선택적으로 가능 | 읽기 전용 |
| 요청 작성 | 가능 | 불가 | 불가 |
| 초안 수정 | 본인 요청만 | 불가 | 불가 |
| 반려 요청 수정/재제출 | 본인 요청만 | 불가 | 불가 |
| 대기 요청 상세 조회 | 본인 요청 | 자기 사업부 | 읽기 전용 |
| 승인/반려 | 불가 | 자기 사업부 대기 요청만 | 불가 |
| 감사 이력 조회 | 본인 요청 범위 | 자기 사업부 범위 | 전체 또는 부여된 감사 범위 |
| 상태 변경 | 제출/재제출 | 승인/반려 | 불가 |

화면에서 버튼을 숨기는 것과 별개로, 모든 읽기·쓰기 권한은 서버에서 다시 검증한다.

### 1.3 상태와 허용 동작

| 현재 상태 | 요청자 동작 | 승인자 동작 | 다음 상태 |
|---|---|---|---|
| 초안 | 수정, 제출 | 없음 | 대기 |
| 대기 | 조회 | 승인, 반려 | 승인 또는 반려 |
| 반려 | 수정, 재제출 | 조회 | 대기 |
| 승인 | 조회 | 조회 | 변경 없음 |

상태 코드 권장값은 `DRAFT`, `PENDING`, `APPROVED`, `REJECTED`이다.

---

## 2. User Flow

### 2.1 요청 등록 및 중복 확인

```text
요청 목록
  → [새 요청]
  → 업체명/사업자번호/담당자 이메일 입력
  → [제출]
      ├─ 입력 오류
      │    → 필드 오류 표시 → 수정
      ├─ 중복 사업자번호
      │    → 제출 중단 → 기존 업체 링크 표시
      ├─ 네트워크 실패
      │    → 입력 보존 → [다시 시도]
      └─ 성공
           → 상태를 대기로 변경
           → 감사 이력 기록
           → 요청 상세로 이동
```

중복 검사는 사업자번호 입력 완료 시 사전 확인할 수 있으나, 제출 시 서버가 반드시 최종 확인해야 한다.

### 2.2 승인

```text
승인자 요청 목록
  → 자기 사업부의 대기 요청 선택
  → 요청 상세 검토
  → [승인]
  → 확인 다이얼로그
      ├─ 403 권한 오류
      │    → 상태 유지 → 권한 오류 표시
      ├─ 네트워크 실패
      │    → 상태 유지 → [다시 시도]
      └─ 성공
           → 승인 상태
           → 감사 이력 기록
```

### 2.3 반려

```text
요청 상세
  → [반려]
  → 반려 사유 입력
  → [반려 확정]
      ├─ 사유 없음 → 제출 차단
      ├─ 403 → 상태 및 사유 입력값 유지
      ├─ 네트워크 실패 → 사유 유지 → [다시 시도]
      └─ 성공 → 반려 상태 → 감사 이력 기록

요청자
  → 반려 요청 상세
  → [수정]
  → 내용 수정
  → [재제출]
  → 대기 상태 + 감사 이력 기록
```

### 2.4 동시 변경 처리

승인자가 상세 화면을 연 뒤 다른 사용자가 먼저 처리한 경우:

1. 서버가 `409 Conflict`를 반환한다.
2. 승인/반려를 적용하지 않는다.
3. “이미 처리된 요청입니다”를 표시한다.
4. 최신 상세 및 감사 이력을 다시 조회한다.

---

## 3. Screen Spec

공통 표기:

- 필수 필드는 라벨과 함께 `*` 및 스크린리더용 필수 정보를 제공한다.
- 날짜는 화면에서 `YYYY-MM-DD HH:mm`, API에서는 ISO 8601을 사용한다.
- 사업자번호는 화면에서 `000-00-00000`, 서버 전송 시 숫자 10자리 사용을 권장한다.
- 로딩 중 중복 요청을 막기 위해 주요 실행 버튼을 비활성화한다.
- 성공 메시지는 토스트로 제공하되, 변경된 상태는 본문에도 표시한다.

### S-01 요청 목록

**목적:** 접근 가능한 요청을 상태별로 조회하고 다음 업무로 진입한다.

| 영역 | 명세 |
|---|---|
| 헤더 | 화면명, 사용자 역할, 사업부 표시 |
| 주요 액션 | 요청자에게만 `새 요청` 표시 |
| 검색 | 업체명, 사업자번호, 요청 ID |
| 필터 | 상태, 요청일 범위. 승인자의 기본 상태는 `대기` |
| 목록 열 | 요청 ID, 업체명, 사업자번호, 사업부, 요청자, 상태, 최종 변경일 |
| 정렬 | 기본값 `최종 변경일 내림차순` |
| 행 동작 | 행 선택 시 상세 이동 |
| 페이지 처리 | 페이지네이션 또는 커서 기반 더보기 |
| 빈 상태 | “조건에 맞는 요청이 없습니다”와 필터 초기화 제공 |
| 오류 상태 | 목록 재조회 버튼 제공 |

역할별 데이터 범위는 서버가 적용한다. 클라이언트가 사업부 ID를 임의로 바꿔 조회 범위를 확대할 수 없어야 한다.

### S-02 요청 작성/편집

**진입 조건:**

- 신규 작성
- 본인의 `DRAFT`
- 본인의 `REJECTED`

| 필드 | 필수 | 규칙 |
|---|---:|---|
| 업체명 | 예 | 앞뒤 공백 제거, 1~100자 |
| 사업자번호 | 예 | 숫자 10자리, 하이픈 자동 표시 |
| 담당자 이메일 | 예 | 이메일 형식, 최대 254자 |
| 요청 사업부 | 서버 결정 | 로그인 사용자 기준, 읽기 전용 표시 |

**버튼:**

- `임시 저장`: 작성 중인 내용을 `DRAFT`로 저장한다.
- `제출`: 신규/초안에서 `PENDING`으로 전환한다.
- `재제출`: 반려 요청에서만 표시하고 `PENDING`으로 전환한다.
- `취소`: 변경 사항이 있으면 이탈 확인 다이얼로그를 표시한다.

**중복 사업자번호:**

- 입력 완료 또는 포커스 이탈 시 선택적으로 사전 검사한다.
- 중복이면 사업자번호 아래 오류를 표시한다.
- “이미 등록된 업체입니다: {업체명}”과 `기존 업체 보기` 링크를 제공한다.
- 중복 상태에서는 제출/재제출하지 않는다.
- 최종 판단은 제출 API의 서버 검사 결과를 따른다.

**네트워크 실패:**

- 모든 입력값을 화면 상태에 보존한다.
- 오류 배너와 `다시 시도`를 제공한다.
- 재시도는 같은 입력값과 동일한 idempotency key를 사용한다.
- 사용자가 새로고침할 가능성까지 고려하면 세션 저장소 기반 복구를 권장한다. 민감정보 보존 정책은 조직 보안 정책을 따른다.

### S-03 요청 상세/승인

**상단 요약:**

- 요청 ID
- 현재 상태
- 업체명
- 사업자번호
- 담당자 이메일
- 요청 사업부
- 요청자
- 요청일 및 최종 변경일

**승인자 액션 노출 조건:**

```text
role = APPROVER
AND request.businessUnitId = session.businessUnitId
AND request.status = PENDING
```

이는 UI 조건일 뿐이며 서버는 동일한 조건을 독립적으로 검증한다.

#### 승인

- `승인` 선택 시 업체명과 승인 결과를 포함한 확인 다이얼로그를 표시한다.
- 성공 후 상태 배지를 `승인`으로 변경하고 액션 버튼을 제거한다.
- 실패 시 상세 데이터를 유지한다.

#### 반려

| 항목 | 명세 |
|---|---|
| 입력 방식 | 반려 다이얼로그 또는 인라인 패널 |
| 사유 | 필수, 앞뒤 공백 제거, 1~500자 |
| 버튼 | 취소, 반려 확정 |
| 실패 처리 | 입력한 사유를 그대로 보존하고 재시도 제공 |
| 성공 처리 | 상태를 반려로 갱신하고 사유를 상세에 표시 |

#### 오류 코드별 UI

| 응답 | UI 동작 |
|---|---|
| `400` | 입력 또는 상태 오류를 해당 영역에 표시 |
| `403` | “이 요청을 처리할 권한이 없습니다” 표시, 상태 유지 |
| `404` | 요청 없음 또는 접근 불가 안내 후 목록 이동 제공 |
| `409` | 이미 변경된 요청 안내 후 최신 데이터 다시 조회 |
| `5xx`/네트워크 오류 | 입력 보존, 재시도 제공 |

**반응형:**

- 데스크톱: 요청 정보와 승인 영역을 2열로 표시한다.
- 모바일: 정보 → 반려 사유/이력 → 승인 액션 순서의 단일 열로 재배치한다.
- 모바일 하단 액션이 고정되는 경우 콘텐츠를 가리지 않도록 하단 여백을 확보한다.

### S-04 감사 이력

| 항목 | 명세 |
|---|---|
| 검색 | 요청 ID, 업체명, 사업자번호 |
| 필터 | 변경 상태, 수행자, 사업부, 기간 |
| 목록 열 | 발생 시각, 요청 ID, 업체명, 이전 상태, 이후 상태, 수행자, 사업부, 사유 |
| 정렬 | 발생 시각 내림차순 |
| 상세 | 이벤트 ID, 수행자 ID, 역할, 변경 전후 값, 반려 사유, 요청 추적 ID |
| 동작 | 읽기 전용, 수정/삭제 기능 없음 |

감사 이력은 최소한 다음 이벤트를 기록한다.

- 초안 생성
- 제출
- 승인
- 반려
- 반려 요청 수정
- 재제출

권한 없는 승인 시도는 요청의 상태 변경 이력에는 포함하지 않는다. 별도의 보안 감사 로그가 있다면 실패한 권한 검사도 기록하는 것을 권장한다.

---

## 4. Lo-fi HTML Wireframe

다음은 네 화면과 모바일 단일 열 재배치를 한 파일에서 확인할 수 있는 정적 와이어프레임이다. 실제 구현에서는 각 `<section>`을 별도 라우트로 분리한다.

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>공급업체 승인 와이어프레임</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: #222;
      background: #f5f5f5;
      font: 14px/1.5 system-ui, sans-serif;
    }
    header, main { max-width: 1120px; margin: auto; }
    header {
      display: flex;
      justify-content: space-between;
      padding: 20px 16px;
      background: #fff;
      border-bottom: 1px solid #bbb;
    }
    nav { padding-top: 8px; }
    nav a { margin-left: 16px; color: #222; }
    main { padding: 24px 16px; }
    section {
      margin-bottom: 32px;
      padding: 20px;
      background: #fff;
      border: 1px solid #aaa;
    }
    .toolbar, .actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: space-between;
      margin: 16px 0;
    }
    .fields {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    label { display: block; font-weight: 700; }
    input, select, textarea, button {
      width: 100%;
      min-height: 40px;
      margin-top: 6px;
      padding: 8px;
      font: inherit;
    }
    button { width: auto; border: 1px solid #555; background: #eee; }
    .primary { color: #fff; background: #333; }
    .danger { color: #fff; background: #777; }
    .error {
      margin-top: 6px;
      color: #8b0000;
      font-weight: 400;
    }
    .banner {
      margin: 12px 0;
      padding: 12px;
      border: 2px solid #555;
      background: #fafafa;
    }
    .detail-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
    }
    .panel { padding: 16px; border: 1px solid #aaa; }
    dl {
      display: grid;
      grid-template-columns: 140px 1fr;
      gap: 10px;
    }
    dt { font-weight: 700; }
    dd { margin: 0; }
    table { width: 100%; border-collapse: collapse; }
    th, td {
      padding: 10px;
      text-align: left;
      border: 1px solid #aaa;
    }
    .status { padding: 3px 8px; border: 1px solid #555; }
    .muted { color: #666; }
    @media (max-width: 720px) {
      header { display: block; }
      nav a { margin: 0 12px 0 0; }
      .fields, .detail-grid { grid-template-columns: 1fr; }
      dl { grid-template-columns: 1fr; gap: 2px; }
      dd { margin-bottom: 10px; }
      table { display: block; overflow-x: auto; }
      .approval-panel { order: 2; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <strong>공급업체 승인</strong>
      <div class="muted">구매사업부 · 승인자 홍길동</div>
    </div>
    <nav aria-label="주 메뉴">
      <a href="#list">요청 목록</a>
      <a href="#form">요청 작성</a>
      <a href="#detail">요청 상세</a>
      <a href="#audit">감사 이력</a>
    </nav>
  </header>

  <main>
    <section id="list">
      <h1>요청 목록</h1>

      <div class="toolbar">
        <div>
          <label>
            검색
            <input type="search" placeholder="업체명, 사업자번호, 요청 ID">
          </label>
        </div>
        <div>
          <label>
            상태
            <select>
              <option>전체</option>
              <option selected>대기</option>
              <option>초안</option>
              <option>승인</option>
              <option>반려</option>
            </select>
          </label>
        </div>
        <button class="primary" type="button">새 요청</button>
      </div>

      <table>
        <thead>
          <tr>
            <th>요청 ID</th>
            <th>업체명</th>
            <th>사업자번호</th>
            <th>사업부</th>
            <th>상태</th>
            <th>최종 변경일</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><a href="#detail">VR-2026-0142</a></td>
            <td>대한부품</td>
            <td>123-45-67890</td>
            <td>구매사업부</td>
            <td><span class="status">대기</span></td>
            <td>2026-07-27 10:30</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section id="form">
      <h1>공급업체 요청 작성</h1>
      <p><span aria-hidden="true">*</span> 표시는 필수 입력 항목입니다.</p>

      <form>
        <div class="fields">
          <label>
            업체명 *
            <input required value="대한부품">
          </label>

          <label>
            사업자번호 *
            <input required inputmode="numeric"
                   aria-describedby="duplicate-error"
                   value="123-45-67890">
            <span id="duplicate-error" class="error">
              이미 등록된 사업자번호입니다.
              <a href="/vendors/V-0091">기존 업체 보기</a>
            </span>
          </label>

          <label>
            담당자 이메일 *
            <input required type="email" value="vendor@example.com">
          </label>

          <label>
            요청 사업부
            <input readonly value="구매사업부">
          </label>
        </div>

        <div class="banner" role="alert">
          네트워크 연결에 실패했습니다. 입력 내용은 보존되었습니다.
          <button type="button">다시 시도</button>
        </div>

        <div class="actions">
          <button type="button">취소</button>
          <div>
            <button type="button">임시 저장</button>
            <button class="primary" type="submit" disabled>
              제출
            </button>
          </div>
        </div>
      </form>
    </section>

    <section id="detail">
      <h1>
        요청 상세
        <span class="status">대기</span>
      </h1>

      <div class="detail-grid">
        <article class="panel">
          <h2>요청 정보</h2>
          <dl>
            <dt>요청 ID</dt><dd>VR-2026-0142</dd>
            <dt>업체명</dt><dd>대한부품</dd>
            <dt>사업자번호</dt><dd>123-45-67890</dd>
            <dt>담당자 이메일</dt><dd>vendor@example.com</dd>
            <dt>사업부</dt><dd>구매사업부</dd>
            <dt>요청자</dt><dd>김요청</dd>
            <dt>요청일</dt><dd>2026-07-27 10:30</dd>
          </dl>

          <h2>최근 이력</h2>
          <ol>
            <li>2026-07-27 10:30 · 제출 · 김요청</li>
            <li>2026-07-27 10:12 · 초안 생성 · 김요청</li>
          </ol>
        </article>

        <aside class="panel approval-panel">
          <h2>승인 처리</h2>
          <p>처리 결과는 감사 이력에 기록됩니다.</p>

          <label>
            반려 사유
            <textarea rows="5"
                      placeholder="반려 시 사유를 입력하세요"></textarea>
          </label>

          <div class="banner" role="alert">
            처리에 실패하면 입력한 반려 사유를 유지하고
            다시 시도 버튼을 표시합니다.
          </div>

          <div class="actions">
            <button class="danger" type="button">반려</button>
            <button class="primary" type="button">승인</button>
          </div>
        </aside>
      </div>
    </section>

    <section id="audit">
      <h1>감사 이력</h1>

      <div class="toolbar">
        <label>
          요청 검색
          <input type="search" placeholder="요청 ID, 업체명, 사업자번호">
        </label>
        <label>
          변경 상태
          <select>
            <option>전체</option>
            <option>제출</option>
            <option>승인</option>
            <option>반려</option>
            <option>재제출</option>
          </select>
        </label>
      </div>

      <table>
        <thead>
          <tr>
            <th>발생 시각</th>
            <th>요청 ID</th>
            <th>이전 → 이후</th>
            <th>수행자</th>
            <th>사업부</th>
            <th>사유</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>2026-07-27 10:30</td>
            <td><a href="#detail">VR-2026-0142</a></td>
            <td>초안 → 대기</td>
            <td>김요청</td>
            <td>구매사업부</td>
            <td>—</td>
          </tr>
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
```

---

## 5. Dev Handoff

### 5.1 권장 라우트

| 화면 | 라우트 |
|---|---|
| 요청 목록 | `/vendor-requests` |
| 요청 작성 | `/vendor-requests/new` |
| 요청 편집 | `/vendor-requests/:requestId/edit` |
| 요청 상세/승인 | `/vendor-requests/:requestId` |
| 감사 이력 | `/audit/vendor-requests` |
| 기존 업체 상세 | `/vendors/:vendorId` |

### 5.2 API 계약 예시

| 기능 | 메서드 및 경로 | 핵심 응답 |
|---|---|---|
| 목록 조회 | `GET /api/vendor-requests` | 역할/사업부로 필터링된 목록 |
| 상세 조회 | `GET /api/vendor-requests/:id` | 상세, 권한, 가능한 동작 |
| 초안 생성 | `POST /api/vendor-requests` | 생성된 요청 |
| 초안/반려 수정 | `PATCH /api/vendor-requests/:id` | 수정된 요청 |
| 중복 확인 | `GET /api/vendors/by-registration-number/:number` | 기존 업체 또는 `404` |
| 제출/재제출 | `POST /api/vendor-requests/:id/submit` | `PENDING` 요청 |
| 승인 | `POST /api/vendor-requests/:id/approve` | `APPROVED` 요청 |
| 반려 | `POST /api/vendor-requests/:id/reject` | `REJECTED` 요청 |
| 감사 이력 | `GET /api/audit/vendor-requests` | 읽기 전용 이벤트 목록 |

상세 응답에 클라이언트의 권한 추론을 줄이는 다음 필드를 포함하는 방식을 권장한다.

```json
{
  "id": "VR-2026-0142",
  "status": "PENDING",
  "version": 3,
  "permissions": {
    "canEdit": false,
    "canSubmit": false,
    "canApprove": true,
    "canReject": true
  }
}
```

### 5.3 오류 응답 규격

```json
{
  "code": "DUPLICATE_REGISTRATION_NUMBER",
  "message": "이미 등록된 사업자번호입니다.",
  "field": "registrationNumber",
  "existingVendor": {
    "id": "V-0091",
    "name": "대한부품",
    "url": "/vendors/V-0091"
  },
  "traceId": "tr_01J..."
}
```

주요 오류 코드:

- `VALIDATION_ERROR`
- `DUPLICATE_REGISTRATION_NUMBER`
- `FORBIDDEN_BUSINESS_UNIT`
- `INVALID_STATE_TRANSITION`
- `REQUEST_VERSION_CONFLICT`
- `REQUEST_NOT_FOUND`

### 5.4 서버 구현 필수사항

- 승인/반려 시 로그인 사용자의 역할과 사업부를 서버에서 검사한다.
- 사업부 불일치 시 `403`을 반환하고 요청 상태를 변경하지 않는다.
- 사업자번호는 정규화한 숫자 10자리를 기준으로 유일성을 검사한다.
- 중복 업체 생성 방지를 위해 DB unique constraint를 함께 둔다.
- 상태 변경과 감사 이벤트 저장은 하나의 트랜잭션으로 처리한다.
- 상태 변경 API는 현재 상태와 `version`을 함께 검사해 동시 처리를 방지한다.
- 재시도 중 중복 변경을 막기 위해 idempotency key를 지원한다.
- 감사 이벤트는 수정·삭제할 수 없는 append-only 구조를 권장한다.
- 반려 사유는 `REJECTED` 전환에서만 필수로 검증한다.

### 5.5 감사 이벤트 최소 스키마

```json
{
  "eventId": "AE-9021",
  "requestId": "VR-2026-0142",
  "action": "REJECTED",
  "fromStatus": "PENDING",
  "toStatus": "REJECTED",
  "actorId": "U-102",
  "actorRole": "APPROVER",
  "businessUnitId": "BU-20",
  "reason": "계좌 정보 확인 필요",
  "occurredAt": "2026-07-27T10:45:00+09:00",
  "traceId": "tr_01J..."
}
```

### 5.6 QA 체크리스트

- 동일 사업자번호 제출 시 요청이 `PENDING`으로 바뀌지 않고 기존 업체 링크가 표시된다.
- 타 사업부 승인자가 승인/반려하면 `403`이며 상태와 감사 상태 변경 이력이 생기지 않는다.
- 제출 성공 시 요청 상태와 감사 이력이 함께 저장된다.
- 감사 이력 저장 실패 시 요청 상태도 변경되지 않는다.
- 반려 사유 없이 반려할 수 없다.
- 네트워크 실패 후 업체 입력값과 반려 사유가 유지된다.
- 재시도 또는 더블클릭으로 상태 변경이 두 번 기록되지 않는다.
- 두 승인자가 동시에 처리하면 한 건만 성공하고 다른 요청은 `409`를 받는다.
- 반려 요청은 요청자만 수정·재제출할 수 있다.
- 승인 요청은 더 이상 수정하거나 상태 변경할 수 없다.
- 모바일 너비에서 상세 정보와 승인 패널이 단일 열로 표시된다.
- 키보드만으로 필드, 오류, 기존 업체 링크, 승인/반려 다이얼로그를 조작할 수 있다.
- 오류 메시지가 색상만으로 전달되지 않고 입력 필드와 프로그램적으로 연결된다.