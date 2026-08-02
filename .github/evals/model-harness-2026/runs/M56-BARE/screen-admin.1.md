아래 문서는 PRD의 요구사항을 구현 가능한 화면·상태·API 동작으로 구체화한 화면정의서다.

전제:

- 요청자의 목록 범위는 본인이 작성한 요청으로 가정한다.
- 승인자의 목록 범위는 서버가 권한을 확인한 사업부 요청으로 제한한다.
- 감사자는 전체 이력을 조회할 수 있다고 가정한다. 조회 범위 제한이 필요하다면 권한 정책을 추가해야 한다.
- 사업자번호는 화면에서는 구분기호를 허용하되, 비교할 때 숫자만 남겨 정규화한다.

---

# 1. IA

## 1.1 정보 구조

```text
공급업체 승인
├─ 요청 목록                         [요청자, 승인자, 감사자]
│  ├─ 검색/필터
│  ├─ 요청 상세
│  └─ 새 요청
├─ 요청 작성/편집                    [요청자]
│  ├─ 업체 정보 입력
│  ├─ 임시 저장
│  ├─ 중복 업체 확인
│  └─ 제출 / 재제출
├─ 요청 상세/승인                    [역할별 액션 차등]
│  ├─ 요청 정보
│  ├─ 상태 및 반려 사유
│  ├─ 상태 변경 이력
│  └─ 승인 / 반려
└─ 감사 이력                         [감사자, 필요 시 관리자]
   ├─ 조건 검색
   ├─ 변경 이력 목록
   └─ 대상 요청 상세
```

## 1.2 역할별 접근 권한

| 기능 | 요청자 | 승인자 | 감사자 |
|---|---:|---:|---:|
| 본인 요청 목록 조회 | 가능 | 정책에 따라 읽기 가능 | 가능 |
| 자기 사업부 대기 요청 조회 | 불가 | 가능 | 가능 |
| 요청 작성 | 가능 | 불가 | 불가 |
| 초안/반려 요청 편집 | 본인 요청만 가능 | 불가 | 불가 |
| 요청 제출/재제출 | 본인 요청만 가능 | 불가 | 불가 |
| 요청 승인/반려 | 불가 | 자기 사업부 대기 요청만 가능 | 불가 |
| 감사 이력 조회 | 본인 요청의 상세 이력만 | 담당 요청의 상세 이력만 | 전체 조회 가능 |
| 데이터 변경 | 제한적 | 승인/반려만 | 불가 |

화면에서 버튼을 숨기거나 비활성화하더라도 최종 권한 검증은 서버가 수행한다.

## 1.3 주요 객체

### 공급업체 요청

| 필드 | 설명 |
|---|---|
| `requestId` | 요청 식별자 |
| `vendorName` | 업체명 |
| `businessNumber` | 정규화된 사업자번호 |
| `contactEmail` | 담당자 이메일 |
| `businessUnitId` | 요청 및 승인 권한 기준 사업부 |
| `requesterId` | 요청자 |
| `status` | `DRAFT`, `PENDING`, `APPROVED`, `REJECTED` |
| `rejectionReason` | 최근 반려 사유 |
| `version` | 동시 수정 방지용 버전 |
| `createdAt`, `updatedAt` | 생성·수정 일시 |
| `submittedAt` | 최근 제출 일시 |
| `decidedAt` | 승인 또는 반려 일시 |

### 감사 이력

| 필드 | 설명 |
|---|---|
| `auditId` | 이력 식별자 |
| `requestId` | 대상 요청 |
| `fromStatus`, `toStatus` | 변경 전·후 상태 |
| `action` | 생성, 제출, 승인, 반려, 재제출 등 |
| `actorId`, `actorRole` | 수행자 |
| `reason` | 반려 사유 등 |
| `occurredAt` | 서버 기준 발생 시각 |
| `businessUnitId` | 사업부 |
| `requestVersion` | 변경 후 요청 버전 |

---

# 2. User Flow

## 2.1 요청 생성 및 제출

```text
[요청 목록]
    │ 새 요청
    ▼
[요청 작성]
    │ 업체명/사업자번호/이메일 입력
    ├─ 임시 저장 ────────────────▶ [초안]
    │
    └─ 제출
        │
        ▼
    [클라이언트 유효성 검사]
        ├─ 실패 → 항목별 오류 표시, 입력 유지
        └─ 통과
            │
            ▼
    [서버 중복·권한·유효성 검사]
        ├─ 중복 사업자번호
        │    → 제출 중단
        │    → 기존 업체 링크 표시
        │    → 입력 유지
        ├─ 네트워크 실패
        │    → 입력 유지
        │    → 재시도 제공
        └─ 성공
             → DRAFT → PENDING
             → 감사 이력 기록
             → 상세 화면 이동
```

중복 검사는 입력 중 사전 확인할 수 있지만, 제출 시 서버가 다시 검사한 결과가 최종 기준이다.

## 2.2 승인

```text
[자기 사업부 대기 목록]
    │ 요청 선택
    ▼
[요청 상세]
    │ 승인
    ▼
[확인 다이얼로그]
    │ 최종 승인
    ▼
[서버 사업부 권한 + 현재 상태 검사]
    ├─ 403 → 상태 변경 없음, 권한 오류 표시
    ├─ 409 → 이미 처리됨, 최신 데이터 다시 조회
    ├─ 네트워크 실패 → 현재 화면 유지, 재시도
    └─ 성공
         → PENDING → APPROVED
         → 감사 이력 기록
         → 처리 완료 상태 표시
```

## 2.3 반려 및 재제출

```text
[요청 상세]
    │ 반려
    ▼
[반려 사유 입력]
    ├─ 빈 값 → 제출 차단
    └─ 반려 확정
         ├─ 403 → 상태 변경 없음, 사유 유지
         ├─ 네트워크 실패 → 사유 유지, 재시도
         └─ 성공
              → PENDING → REJECTED
              → 감사 이력 기록

[요청자가 반려 요청 조회]
    │ 수정
    ▼
[요청 편집]
    │ 반려 사유 확인 후 수정
    └─ 재제출
         ├─ 중복 → 제출 차단, 기존 업체 링크
         └─ 성공
              → REJECTED → PENDING
              → 감사 이력 기록
```

## 2.4 감사 조회

```text
[감사 이력]
    │ 기간/상태/행위자/요청번호/사업부 필터
    ▼
[감사 이력 결과]
    │ 행 선택
    ▼
[요청 상세 - 읽기 전용]
```

---

# 3. Screen Spec

## 3.1 공통 정책

### 상태 표시

| 상태 | 표시명 | 권장 색상 의미 |
|---|---|---|
| `DRAFT` | 초안 | 중립 |
| `PENDING` | 승인 대기 | 주의 |
| `APPROVED` | 승인 | 성공 |
| `REJECTED` | 반려 | 오류 |

색상만으로 상태를 구분하지 않고 항상 텍스트를 함께 표시한다.

### 공통 로딩·오류

- 최초 로딩: 목록 스켈레톤 또는 상세 로딩 표시.
- 액션 처리 중: 해당 버튼에 진행 상태를 표시하고 중복 클릭을 막는다.
- 네트워크 실패: 사용자가 입력한 값은 삭제하지 않는다.
- 재시도 버튼은 실패한 동작만 다시 수행한다.
- 서버 오류 메시지를 그대로 노출하지 않고 사용자용 문구와 추적 ID를 표시한다.
- 인증 만료는 로그인 화면으로 이동하되, 작성 중 값은 세션 저장소 등에 임시 보존한다.

---

## 3.2 S-01 요청 목록

### 목적

역할에 맞는 요청을 조회하고 작성 또는 상세 처리 화면으로 진입한다.

### 구성

| 영역 | 요소 | 동작 |
|---|---|---|
| 헤더 | 화면명, 새 요청 버튼 | 요청자에게만 새 요청 노출 |
| 탭 | 내 요청 / 승인 대기 | 권한에 따라 노출 |
| 검색 | 업체명, 사업자번호, 요청번호 | Enter 또는 검색 버튼으로 실행 |
| 필터 | 상태, 사업부, 요청일 | 역할에 따라 허용 범위 제한 |
| 목록 | 요청번호, 업체명, 사업자번호, 사업부, 요청자, 상태, 수정일 | 행 선택 시 상세 이동 |
| 페이지 | 페이지 번호 또는 커서 | 필터 유지 |
| 빈 상태 | 안내 문구 및 새 요청 CTA | 요청자에게만 CTA 표시 |

### 기본 정렬

- 승인 대기: 오래된 제출 건 우선.
- 내 요청: 최근 수정일 내림차순.
- 감사자 조회: 최근 변경일 내림차순.

### 예외

- 목록 조회 403: 접근 불가 화면.
- 검색 결과 없음: “조건에 맞는 요청이 없습니다.”
- 목록 갱신 실패: 기존 목록이 있으면 유지하고 상단에 재시도 배너 표시.

---

## 3.3 S-02 요청 작성/편집

### 진입 조건

- 신규 작성: 요청자.
- 편집: 본인의 `DRAFT` 또는 `REJECTED` 요청.
- `PENDING`, `APPROVED` 요청은 읽기 전용이다.

### 입력 필드

| 필드 | 필수 | 규칙 | 오류 문구 예시 |
|---|---:|---|---|
| 업체명 | 예 | 앞뒤 공백 제거, 1~100자 | 업체명을 입력해 주세요. |
| 사업자번호 | 예 | 화면 형식 `000-00-00000`, 저장·비교 시 숫자 10자리 | 올바른 사업자번호를 입력해 주세요. |
| 담당자 이메일 | 예 | 이메일 형식, 최대 254자 | 올바른 이메일 주소를 입력해 주세요. |

### 반려 요청 편집

- 화면 상단에 최근 반려 사유와 반려 일시를 표시한다.
- 기존 입력값을 그대로 불러온다.
- 재제출 전에 중복 사업자번호를 다시 검증한다.

### 주요 액션

| 액션 | 결과 |
|---|---|
| 임시 저장 | 신규 요청을 `DRAFT`로 생성하거나 기존 초안을 갱신 |
| 제출 | 유효성·중복 검사 성공 시 `PENDING`으로 전환 |
| 재제출 | `REJECTED`에서 `PENDING`으로 전환 |
| 취소 | 변경 내용이 있으면 이탈 확인 |

### 중복 사업자번호

- 해당 필드 아래에 인라인 오류를 표시한다.
- “기존 업체 보기” 링크를 제공한다.
- 제출 API도 중복을 최종 검증하며 요청 상태는 바뀌지 않아야 한다.
- 중복 결과는 다른 필드의 입력을 초기화하지 않는다.

### 네트워크 실패

- 입력 전체를 유지한다.
- “저장/제출하지 못했습니다. 다시 시도해 주세요.” 배너를 표시한다.
- 같은 요청을 재시도할 때 중복 생성되지 않도록 idempotency key를 사용한다.

---

## 3.4 S-03 요청 상세/승인

### 공통 표시 정보

- 요청번호 및 상태
- 업체명
- 사업자번호
- 담당자 이메일
- 사업부
- 요청자 및 요청일
- 최근 반려 사유
- 상태 변경 이력 요약

### 역할 및 상태별 액션

| 사용자 | 상태 | 액션 |
|---|---|---|
| 요청자 | `DRAFT` | 편집, 제출 |
| 요청자 | `REJECTED` | 편집, 재제출 |
| 요청자 | `PENDING`, `APPROVED` | 없음 |
| 권한 있는 승인자 | `PENDING` | 승인, 반려 |
| 권한 없는 승인자 | 모든 상태 | 변경 액션 미노출 |
| 감사자 | 모든 상태 | 없음 |

### 승인

- 승인 버튼 선택 시 확인 다이얼로그를 표시한다.
- 요청번호와 업체명을 포함해 대상 오인을 방지한다.
- 성공 시 상태와 이력 영역을 즉시 갱신한다.

### 반려

| 항목 | 정책 |
|---|---|
| 반려 사유 | 필수 |
| 길이 | 1~500자 권장 |
| 공백만 입력 | 허용하지 않음 |
| 실패 시 | 다이얼로그와 입력 사유 유지 |
| 성공 시 | 다이얼로그 닫기, 상태와 이력 갱신 |

### 오류 처리

- `403 FORBIDDEN_BUSINESS_UNIT`: “이 사업부 요청을 처리할 권한이 없습니다.” 상태는 그대로 유지하고 최신 요청을 다시 조회한다.
- `409 INVALID_STATUS`: “다른 사용자가 이미 요청을 처리했습니다.” 최신 정보 표시.
- 네트워크 실패: 승인 확인 또는 반려 사유를 유지하고 재시도 제공.

### 반응형

- 데스크톱: 요청 정보와 처리/이력 패널을 2열로 배치.
- 모바일: 모든 영역을 단일 열로 재배치.
- 모바일 액션 영역은 화면 하단에 고정할 수 있으나 본문이나 오류 메시지를 가리지 않아야 한다.
- 확인 다이얼로그는 모바일에서 하단 시트 또는 전체 너비 모달로 표시한다.

---

## 3.5 S-04 감사 이력

### 목적

누가, 언제, 어떤 요청의 상태를 어떻게 변경했는지 읽기 전용으로 조회한다.

### 검색 조건

- 기간
- 요청번호
- 업체명 또는 사업자번호
- 사업부
- 행위자
- 변경 후 상태
- 액션: 제출, 재제출, 승인, 반려

### 목록 컬럼

| 컬럼 | 설명 |
|---|---|
| 변경 일시 | 서버 기준 일시, 사용자 시간대로 표시 |
| 요청번호 | 상세 링크 |
| 업체명 | 변경 당시 또는 현재 표시 정책 명시 필요 |
| 사업부 | 대상 사업부 |
| 변경 | 예: 승인 대기 → 반려 |
| 행위자 | 이름 및 식별자 |
| 역할 | 요청자/승인자 |
| 사유 | 반려 사유 요약 |

### 상세 조회

- 감사 이력 자체는 수정하거나 삭제할 수 없다.
- 요청 상세로 이동해 전체 타임라인을 조회할 수 있다.
- 민감정보가 추가될 경우 감사자 역할에도 필드별 마스킹 정책이 필요하다.

---

# 4. lo-fi HTML Wireframe

아래 코드는 네 화면과 승인·반려 상태를 한 페이지에서 검토할 수 있는 정적 와이어프레임이다. 실제 구현에서는 라우팅, 데이터 바인딩, 권한 처리를 연결한다.

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
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 24px;
      border-bottom: 1px solid #bbb;
      background: #fff;
    }
    nav {
      display: flex;
      gap: 16px;
      padding: 12px 24px;
      border-bottom: 1px solid #ccc;
      background: #fff;
      overflow-x: auto;
    }
    nav a { color: #222; white-space: nowrap; }
    main {
      width: min(1180px, calc(100% - 32px));
      margin: 24px auto;
    }
    section {
      margin-bottom: 48px;
      padding: 24px;
      border: 2px solid #888;
      background: #fff;
    }
    h1, h2, h3 { margin-top: 0; }
    .toolbar, .actions, .filters {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: end;
    }
    .toolbar { justify-content: space-between; margin-bottom: 16px; }
    .filters {
      padding: 12px;
      border: 1px dashed #999;
      margin-bottom: 16px;
    }
    .field {
      display: grid;
      gap: 6px;
      min-width: 180px;
      margin-bottom: 16px;
    }
    input, select, textarea, button {
      min-height: 40px;
      padding: 8px 10px;
      border: 1px solid #777;
      background: #fff;
      font: inherit;
    }
    textarea { min-height: 100px; resize: vertical; }
    button { cursor: pointer; }
    .primary { color: #fff; background: #222; }
    .danger { border-color: #900; color: #900; }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      border: 1px solid #777;
      border-radius: 999px;
      font-size: 12px;
    }
    .error {
      padding: 10px;
      border: 1px solid #a00;
      color: #800;
      background: #fff5f5;
    }
    .notice {
      padding: 12px;
      border: 1px solid #997b00;
      background: #fffbe6;
    }
    .grid {
      display: grid;
      grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr);
      gap: 16px;
    }
    .panel {
      padding: 16px;
      border: 1px solid #999;
    }
    .data-row {
      display: grid;
      grid-template-columns: 140px 1fr;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid #ddd;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 10px;
      border: 1px solid #aaa;
      text-align: left;
    }
    tr[data-link] { cursor: pointer; }
    .timeline {
      margin: 0;
      padding-left: 20px;
    }
    .timeline li { margin-bottom: 12px; }
    .modal {
      max-width: 520px;
      margin: 24px auto 0;
      padding: 20px;
      border: 3px solid #555;
      background: #fafafa;
    }
    .mobile-action-note {
      margin-top: 12px;
      color: #555;
      font-size: 12px;
    }
    @media (max-width: 720px) {
      main { width: min(100% - 16px, 1180px); margin-top: 8px; }
      section { padding: 16px; }
      .grid { grid-template-columns: 1fr; }
      .data-row { grid-template-columns: 1fr; gap: 2px; }
      .table-wrap { overflow-x: auto; }
      .filters > *, .filters .field { width: 100%; }
      .actions button { flex: 1; }
    }
  </style>
</head>
<body>
  <header>
    <strong>공급업체 승인</strong>
    <span>홍길동 · 요청자</span>
  </header>

  <nav aria-label="주 메뉴">
    <a href="#request-list">요청 목록</a>
    <a href="#request-form">요청 작성</a>
    <a href="#request-detail">요청 상세/승인</a>
    <a href="#audit-log">감사 이력</a>
  </nav>

  <main>
    <!-- S-01 요청 목록 -->
    <section id="request-list">
      <div class="toolbar">
        <div>
          <h2>S-01 요청 목록</h2>
          <button aria-pressed="true">내 요청</button>
          <button>승인 대기</button>
        </div>
        <button class="primary">+ 새 요청</button>
      </div>

      <div class="filters">
        <label class="field">
          검색
          <input placeholder="업체명, 사업자번호, 요청번호">
        </label>
        <label class="field">
          상태
          <select>
            <option>전체</option>
            <option>초안</option>
            <option>승인 대기</option>
            <option>승인</option>
            <option>반려</option>
          </select>
        </label>
        <button>검색</button>
        <button>초기화</button>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>요청번호</th>
              <th>업체명</th>
              <th>사업자번호</th>
              <th>사업부</th>
              <th>상태</th>
              <th>수정일</th>
            </tr>
          </thead>
          <tbody>
            <tr data-link>
              <td>VR-2026-0012</td>
              <td>예시상사</td>
              <td>123-45-67890</td>
              <td>플랫폼사업부</td>
              <td><span class="badge">승인 대기</span></td>
              <td>2026-07-27 10:20</td>
            </tr>
            <tr data-link>
              <td>VR-2026-0011</td>
              <td>샘플테크</td>
              <td>111-22-33333</td>
              <td>플랫폼사업부</td>
              <td><span class="badge">반려</span></td>
              <td>2026-07-26 17:10</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- S-02 요청 작성/편집 -->
    <section id="request-form">
      <div class="toolbar">
        <h2>S-02 요청 작성/편집</h2>
        <span class="badge">초안</span>
      </div>

      <div class="notice">
        반려 사유: 사업자번호를 다시 확인해 주세요.
      </div>

      <form>
        <label class="field">
          업체명 *
          <input value="예시상사" maxlength="100" required>
        </label>

        <label class="field">
          사업자번호 *
          <input
            value="123-45-67890"
            inputmode="numeric"
            aria-describedby="business-number-error"
            aria-invalid="true"
            required>
        </label>
        <div id="business-number-error" class="error" role="alert">
          이미 등록된 사업자번호입니다.
          <a href="#">기존 업체 보기: V-000184</a>
        </div>

        <label class="field">
          담당자 이메일 *
          <input type="email" value="manager@example.com" required>
        </label>

        <div class="actions">
          <button type="button">취소</button>
          <button type="button">임시 저장</button>
          <button type="submit" class="primary">제출</button>
        </div>
      </form>
    </section>

    <!-- S-03 요청 상세/승인 -->
    <section id="request-detail">
      <div class="toolbar">
        <div>
          <h2>S-03 요청 상세/승인</h2>
          <strong>VR-2026-0012</strong>
        </div>
        <span class="badge">승인 대기</span>
      </div>

      <div class="grid">
        <article class="panel">
          <h3>요청 정보</h3>
          <div class="data-row"><strong>업체명</strong><span>예시상사</span></div>
          <div class="data-row"><strong>사업자번호</strong><span>123-45-67890</span></div>
          <div class="data-row"><strong>담당자 이메일</strong><span>manager@example.com</span></div>
          <div class="data-row"><strong>사업부</strong><span>플랫폼사업부</span></div>
          <div class="data-row"><strong>요청자</strong><span>홍길동</span></div>
          <div class="data-row"><strong>제출일</strong><span>2026-07-27 10:20</span></div>
        </article>

        <aside class="panel">
          <h3>처리 및 이력</h3>
          <ol class="timeline">
            <li>2026-07-27 10:20<br>초안 → 승인 대기 · 홍길동</li>
            <li>2026-07-27 09:50<br>초안 생성 · 홍길동</li>
          </ol>
          <div class="actions">
            <button class="danger">반려</button>
            <button class="primary">승인</button>
          </div>
          <div class="mobile-action-note">
            모바일에서는 요청 정보 아래에 단일 열로 배치됩니다.
          </div>
        </aside>
      </div>

      <!-- 반려 버튼 선택 후 표시되는 예시 다이얼로그 -->
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="reject-title">
        <h3 id="reject-title">요청 반려</h3>
        <p>VR-2026-0012 · 예시상사</p>
        <label class="field">
          반려 사유 *
          <textarea maxlength="500"
            placeholder="요청자가 수정할 내용을 구체적으로 입력하세요.">사업자번호를 다시 확인해 주세요.</textarea>
        </label>
        <div class="error" role="alert">
          네트워크 문제로 반려하지 못했습니다. 입력한 사유는 보존되었습니다.
        </div>
        <div class="actions">
          <button>취소</button>
          <button class="danger">다시 시도</button>
        </div>
      </div>
    </section>

    <!-- S-04 감사 이력 -->
    <section id="audit-log">
      <h2>S-04 감사 이력</h2>

      <div class="filters">
        <label class="field">
          시작일
          <input type="date" value="2026-07-01">
        </label>
        <label class="field">
          종료일
          <input type="date" value="2026-07-27">
        </label>
        <label class="field">
          요청번호/업체
          <input placeholder="요청번호, 업체명, 사업자번호">
        </label>
        <label class="field">
          변경 상태
          <select>
            <option>전체</option>
            <option>승인 대기</option>
            <option>승인</option>
            <option>반려</option>
          </select>
        </label>
        <button>조회</button>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>변경 일시</th>
              <th>요청번호</th>
              <th>업체명</th>
              <th>사업부</th>
              <th>변경</th>
              <th>행위자</th>
              <th>사유</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>2026-07-27 10:20</td>
              <td><a href="#">VR-2026-0012</a></td>
              <td>예시상사</td>
              <td>플랫폼사업부</td>
              <td>초안 → 승인 대기</td>
              <td>홍길동 · 요청자</td>
              <td>-</td>
            </tr>
            <tr>
              <td>2026-07-26 17:10</td>
              <td><a href="#">VR-2026-0011</a></td>
              <td>샘플테크</td>
              <td>플랫폼사업부</td>
              <td>승인 대기 → 반려</td>
              <td>김승인 · 승인자</td>
              <td>사업자번호 재확인 필요</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
```

---

# 5. Dev Handoff

## 5.1 상태 전이 규칙

| 현재 상태 | 액션 | 다음 상태 | 수행 가능 역할 |
|---|---|---|---|
| 없음 | 요청 생성 | `DRAFT` | 요청자 |
| `DRAFT` | 제출 | `PENDING` | 해당 요청자 |
| `REJECTED` | 수정 저장 | `REJECTED` | 해당 요청자 |
| `REJECTED` | 재제출 | `PENDING` | 해당 요청자 |
| `PENDING` | 승인 | `APPROVED` | 해당 사업부 승인자 |
| `PENDING` | 반려 | `REJECTED` | 해당 사업부 승인자 |

그 외 전이는 서버에서 `409 INVALID_STATUS_TRANSITION`으로 거부한다.

## 5.2 권장 API

| Method | Endpoint | 용도 |
|---|---|---|
| `GET` | `/api/vendor-requests` | 역할·검색 조건별 요청 목록 |
| `POST` | `/api/vendor-requests` | 초안 생성 |
| `GET` | `/api/vendor-requests/{id}` | 요청 상세 |
| `PATCH` | `/api/vendor-requests/{id}` | 초안/반려 요청 수정 |
| `POST` | `/api/vendor-requests/{id}/submit` | 제출 또는 재제출 |
| `POST` | `/api/vendor-requests/{id}/approve` | 승인 |
| `POST` | `/api/vendor-requests/{id}/reject` | 반려 |
| `GET` | `/api/vendors/duplicates?businessNumber=...` | 입력 중 중복 사전 확인 |
| `GET` | `/api/audit-events` | 감사 이력 조회 |

승인·반려 요청 예시:

```json
{
  "expectedVersion": 4,
  "idempotencyKey": "0fbab70f-70e5-4b27-a4d6-2ca32f9aebdf"
}
```

```json
{
  "reason": "사업자번호를 다시 확인해 주세요.",
  "expectedVersion": 4,
  "idempotencyKey": "b24dc8f4-ecbf-4f4d-90d6-269cf665cd8a"
}
```

## 5.3 오류 응답 규약

```json
{
  "code": "DUPLICATE_BUSINESS_NUMBER",
  "message": "이미 등록된 사업자번호입니다.",
  "traceId": "tr_01J...",
  "details": {
    "existingVendorId": "V-000184",
    "existingVendorUrl": "/vendors/V-000184"
  }
}
```

| HTTP | 코드 | 클라이언트 처리 |
|---:|---|---|
| 400 | `VALIDATION_ERROR` | 필드별 오류 표시 |
| 403 | `FORBIDDEN_BUSINESS_UNIT` | 상태 변경 없음, 권한 오류 표시 후 상세 재조회 |
| 404 | `REQUEST_NOT_FOUND` | 목록으로 이동 가능한 오류 화면 |
| 409 | `DUPLICATE_BUSINESS_NUMBER` | 제출 차단, 기존 업체 링크 표시 |
| 409 | `VERSION_CONFLICT` | 최신 데이터 재조회 안내 |
| 409 | `INVALID_STATUS_TRANSITION` | 이미 처리된 요청 안내 |
| 5xx | `INTERNAL_ERROR` | 입력 보존, 재시도 및 추적 ID 제공 |
| 응답 없음 | 네트워크 오류 | 입력·반려 사유 보존, 같은 액션 재시도 |

## 5.4 서버 구현 필수사항

- 사업자번호는 숫자만 남긴 값으로 유일성을 검사한다.
- 중복 검사는 사전 조회와 무관하게 제출 트랜잭션 안에서 다시 수행한다.
- 승인·반려 시 토큰의 사용자 사업부 권한을 서버가 직접 확인한다.
- 권한 검사, 현재 상태 검사, 상태 변경, 감사 이력 저장을 하나의 트랜잭션으로 처리한다.
- `403` 또는 다른 실패가 발생하면 상태와 감사 이력이 모두 변경되지 않아야 한다.
- 상태 변경과 감사 이력 기록 중 하나만 성공하는 부분 완료를 허용하지 않는다.
- `expectedVersion`을 이용해 동시 승인을 방지한다.
- 재시도로 같은 변경이 두 번 기록되지 않도록 idempotency key를 지원한다.
- 감사 이력은 애플리케이션의 일반 수정 API로 변경·삭제할 수 없게 한다.
- 시간은 서버에서 UTC로 저장하고 화면에서 사용자 시간대로 변환한다.

## 5.5 클라이언트 상태 보존

- 작성값은 컴포넌트 상태뿐 아니라 세션 단위 임시 저장소에도 보존하는 것을 권장한다.
- 저장 키에는 사용자 ID와 요청 ID를 포함해 사용자 간 데이터가 섞이지 않게 한다.
- 제출 또는 저장 성공 후에만 임시 데이터를 제거한다.
- 반려 모달은 API 성공 전까지 닫지 않으며 실패 시 사유를 그대로 유지한다.
- 승인·반려 버튼 처리 중에는 같은 액션의 중복 실행을 막되, 실패 후 다시 활성화한다.
- 페이지 새로고침 후 복원 시 서버 버전과 충돌하면 사용자가 복원 여부를 선택하도록 한다.

## 5.6 접근성 및 반응형 기준

- 모든 입력에는 연결된 `label`을 제공한다.
- 필드 오류는 `aria-describedby`, `aria-invalid`로 연결한다.
- 비동기 성공·오류 메시지는 `aria-live` 영역으로 전달한다.
- 모달이 열리면 포커스를 내부로 이동하고 닫힐 때 실행 버튼으로 복귀한다.
- 키보드만으로 승인·반려·재시도가 가능해야 한다.
- 모바일 기준점은 우선 `720px` 이하로 정의하되 디자인 시스템 기준에 맞춰 조정한다.
- 승인 상세는 모바일에서 정보 → 반려 사유 → 이력 → 액션 순서의 단일 열로 표시한다.
- 터치 대상은 최소 44×44px을 권장한다.

## 5.7 감사 이벤트 최소 기록값

상태가 변경될 때 다음 값을 변경 후 즉시 기록한다.

```json
{
  "requestId": "VR-2026-0012",
  "action": "REJECT",
  "fromStatus": "PENDING",
  "toStatus": "REJECTED",
  "actorId": "user-481",
  "actorRole": "APPROVER",
  "businessUnitId": "bu-platform",
  "reason": "사업자번호를 다시 확인해 주세요.",
  "requestVersion": 5,
  "occurredAt": "2026-07-27T01:20:00Z"
}
```

감사 로그에는 인증 토큰, 세션 ID, 불필요한 개인정보를 저장하지 않는다.

## 5.8 수용 기준 추적표

| 수용 기준 | 화면 검증 | 서버 검증 |
|---|---|---|
| 권한 없는 승인 시 403, 상태 불변 | 권한 오류 표시, 상세 재조회 | 사업부 권한 검사 후 403, 트랜잭션 롤백 |
| 중복 사업자번호에서 제출 차단 | 필드 오류와 기존 업체 링크, 입력 유지 | 제출 트랜잭션 내 중복 재검사 |
| 네트워크 실패 시 입력 보존 | 작성값·반려 사유 유지, 재시도 제공 | idempotency key로 중복 처리 방지 |
| 모바일 승인 상세 단일 열 | 720px 이하 레이아웃 검증 | 해당 없음 |
| 모든 상태 변경 감사 기록 | 상세 타임라인 및 감사 화면 표시 | 상태 변경과 감사 저장을 단일 트랜잭션 처리 |

## 5.9 핵심 테스트 시나리오

1. 요청자가 정상 정보를 제출하면 `DRAFT → PENDING` 이력 1건이 생성된다.
2. 기존 업체와 같은 정규화 사업자번호를 제출하면 `409`가 반환되고 요청 상태는 유지된다.
3. 다른 사업부 승인자가 승인 API를 직접 호출하면 `403`이며 상태·버전·감사 이력이 모두 변하지 않는다.
4. 승인자 두 명이 같은 버전으로 동시에 처리하면 한 건만 성공하고 나머지는 `409`가 된다.
5. 반려 요청 중 네트워크를 끊으면 작성한 사유가 남고, 재연결 후 동일 내용으로 재시도할 수 있다.
6. 반려된 요청을 수정해 재제출하면 `REJECTED → PENDING` 이력이 별도로 생성된다.
7. 감사자는 변경 API를 호출할 수 없으며 모든 화면이 읽기 전용이다.
8. 모바일 너비에서 상세 정보와 처리 패널이 가로 스크롤 없이 단일 열로 표시된다.