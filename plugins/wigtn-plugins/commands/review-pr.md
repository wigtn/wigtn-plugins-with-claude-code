---
argument-hint: "<PR번호 또는 URL>"
description: GitHub PR을 터미널에서 리뷰합니다. PR diff를 분석하고, 코드 리뷰 점수를 매기고, 리뷰 코멘트를 남깁니다. Trigger on "/review-pr", "PR 리뷰해줘", "리뷰해줘", "PR 봐줘", "코드 리뷰", "review this PR".
---

# Review PR

GitHub Pull Request를 터미널에서 리뷰하고 피드백을 남깁니다.

## Pipeline Position

`[/prd] → [/implement] → [/auto-commit] → PR 생성` 이후, 동료가 `[/review-pr #123]`으로 리뷰 결과 + 코멘트를 남기는 단계.

## Usage

```bash
/review-pr 123                        # PR #123 리뷰
/review-pr 123 --level 3              # 심층 리뷰 (Level 3)
/review-pr 123 --level 4              # 아키텍처 리뷰 (Level 4)
/review-pr 123 --approve              # 리뷰 후 자동 승인 (findings PASS 시)
/review-pr 123 --comment-only         # GitHub에 코멘트만, 승인/거절 안함
/review-pr https://github.com/org/repo/pull/123  # URL로도 가능
```

## Parameters

- `$ARGUMENTS`: PR 번호 또는 GitHub PR URL (필수)
- `--level <1-4>`: 리뷰 깊이 (기본: 2)
- `--approve`: findings 롤업 PASS(critical 0, major 0) 시 자동 Approve
- `--comment-only`: GitHub에 코멘트만 남기고 승인/거절 판단 안함
- `--no-comment`: GitHub에 코멘트 남기지 않음 (로컬 결과만)
- `--files <glob>`: 특정 파일만 리뷰 (예: `"src/**/*.ts"`)

## Protocol

### Step 1: PR 정보 수집

```bash
# PR 메타데이터 가져오기
gh pr view $PR_NUMBER --json title,body,author,baseRefName,headRefName,files,additions,deletions,changedFiles,reviewDecision,reviews,state

# PR diff 가져오기
gh pr diff $PR_NUMBER

# PR에 달린 기존 리뷰/코멘트 확인
gh pr view $PR_NUMBER --json comments,reviews
```

**PR 상태 확인:**
- `state: MERGED` → "이미 머지된 PR입니다. 리뷰를 계속할까요?" (AskUserQuestion)
- `state: CLOSED` → "닫힌 PR입니다. 리뷰를 계속할까요?" (AskUserQuestion)
- `state: OPEN` → 정상 진행

**정보 요약 출력:**

```
┌─────────────────────────────────────────────────────────────┐
│  PR #123: Add user authentication API                       │
├─────────────────────────────────────────────────────────────┤
│  Author: @username                                          │
│  Branch: feature/user-auth → main                           │
│  Files: 5 changed (+234, -12)                               │
│  Status: OPEN | Reviews: 0 approved, 0 changes requested    │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: 변경사항 분석

> **연동**: `pr-reviewer` 에이전트를 호출합니다.

**리뷰 레벨별 동작:**

| Level | 분석 범위 | 에이전트 |
|-------|----------|---------|
| 1 (Quick) | 린트 수준, 포맷팅, 명명 규칙 | `pr-reviewer` 단독 |
| 2 (Standard) | 5-Category 전체 평가 | `pr-reviewer` (병렬 이득이 크면 병렬) |
| 3 (Deep) | 호출 체인, 에지 케이스, 보안 | `pr-reviewer` + `deep-review` 스킬 |
| 4 (Architecture) | SOLID, 계층 위반, 확장성 | `pr-reviewer` + `architecture-review` 스킬 |

**병렬 리뷰 (Level 2+, 병렬 처리 이득이 클 때):** 3개 에이전트로 카테고리를 분담 — A(Readability+Maintainability /40), B(Performance+Testability /40), C(Best Practices /20 + Security 🔒) — 후 Score Merge로 병합.

### Step 3: 리뷰 결과 출력

#### Coverage-First 보고

findings는 severity로 사전 필터링하지 않고 전량 보고하되 각 finding에 `severity`(critical/major/minor/info)와 `confidence`(high/medium/low)를 표기한다(recall 우선, 취사선택은 하류에 위임).

```markdown
## PR Review Result

### PR #123: Add user authentication API

| 항목 | 점수 | 상태 |
|------|------|------|
| Readability | NN/20 | (상태) |
| Maintainability | NN/20 | (상태) |
| Performance | NN/20 | (상태) |
| Testability | NN/20 | (상태) |
| Best Practices | NN/20 | (상태) |
| **Total** | **NN/100** | **(등급)** |

### Findings

#### Critical (즉시 수정 필요)
- 없음

#### Major (수정 권장)
- `src/api/auth.ts:45` — 에러 응답에 내부 스택 트레이스 노출
  → try-catch에서 generic error message 반환 권장

#### Minor (개선 제안)
- `src/types/auth.ts:12` — `any` 타입 사용
  → 구체적인 타입 정의 권장

### Recommendation
✅ APPROVE — 전반적으로 양호한 품질. Major 이슈 1건 수정 권장.
```

### Step 4: GitHub 리뷰 제출 (선택)

> **조건**: `--no-comment` 옵션이 없을 때만 실행

**AskUserQuestion 호출:**

```yaml
question: "리뷰 결과를 GitHub PR에 남길까요?"
header: "Review Submit"
options:
  - label: "Approve + 코멘트"
    description: "승인하고 리뷰 코멘트를 남깁니다 (findings PASS 시)"
  - label: "Request Changes + 코멘트"
    description: "변경 요청과 함께 리뷰 코멘트를 남깁니다"
  - label: "코멘트만"
    description: "승인/거절 없이 코멘트만 남깁니다"
  - label: "남기지 않음"
    description: "로컬 결과만 확인하고 종료합니다"
```

**`--approve` 플래그 사용 시 (findings 롤업 기준 — 노이즈 큰 점수로 자동 승인하지 않음):**
- **PASS** (critical 0, major 0): 사용자 확인 없이 자동 Approve + 코멘트
- **WARN/FAIL** (major ≥1 또는 critical ≥1): AskUserQuestion으로 확인 (자동 승인 불가)
- 점수(NN/100)는 코멘트에 참고로만 표기

**GitHub 리뷰 제출:**

```bash
# Approve with comment
gh pr review $PR_NUMBER --approve --body "$(cat <<'EOF'
## Code Review (by Claude)

**Quality Score: NN/100 (등급)**

### Summary
- 전반적으로 양호한 코드 품질
- 인증 로직이 잘 분리되어 있음
- 테스트 커버리지 적절

### Findings
#### Major
- `src/api/auth.ts:45` — 에러 응답에 내부 스택 트레이스 노출

#### Minor
- `src/types/auth.ts:12` — `any` 타입 사용 → 구체적인 타입 정의 권장

---
🤖 Reviewed by Claude Code (`/review-pr`)
EOF
)"

# Request changes with comment
gh pr review $PR_NUMBER --request-changes --body "..."

# Comment only (no approve/reject)
gh pr review $PR_NUMBER --comment --body "..."
```

**파일별 인라인 코멘트 (Critical/Major 이슈):**

```bash
# Critical/Major 이슈에 대해 인라인 코멘트
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments \
  --method POST \
  -f body="⚠️ **Major**: 에러 응답에 내부 스택 트레이스가 노출됩니다. try-catch에서 generic error message를 반환하세요." \
  -f path="src/api/auth.ts" \
  -F line=45 \
  -f side="RIGHT" \
  -f commit_id="$(gh pr view $PR_NUMBER --json headRefOid -q .headRefOid)"
```

### Step 5: 결과 요약

```
┌─────────────────────────────────────────────────────────────┐
│  ✅ PR Review Complete                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PR #123: Add user authentication API                       │
│  Score: NN/100 (등급)                                       │
│  Decision: (판단)                                           │
│                                                             │
│  📝 GitHub Actions:                                         │
│  • Review comment posted                                    │
│  • 1 inline comment (Major issue)                           │
│  • Status: Approved                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Review Decision Matrix

| 점수 | 추천 판단 | 설명 |
|------|----------|------|
| **90+** | ✅ Approve | 즉시 머지 가능 |
| **80-89** | ✅ Approve (with suggestions) | 머지 가능, 사소한 개선점 |
| **70-79** | 💬 Comment | 머지 전 개선 권장 |
| **60-69** | ❌ Request Changes | 수정 후 재리뷰 필요 |
| **<60** | ❌ Request Changes | 상당한 수정 필요 |
| Security Critical | ❌ Request Changes (강제) | 보안 이슈 발견 시 점수와 무관하게 FAIL/차단 — 해결 필수 |

## Integration Points

### 호출하는 에이전트

| 구성요소 | 역할 | 호출 조건 |
|----------|------|----------|
| `pr-reviewer` 에이전트 | PR diff 기반 코드 리뷰 | 항상 |

### 외부 도구

| 도구 | 용도 |
|------|------|
| `gh pr view` | PR 메타데이터 조회 |
| `gh pr diff` | PR diff 가져오기 |
| `gh pr review` | 리뷰 제출 (approve/request-changes/comment) |
| `gh api` | 인라인 코멘트 |

## Rules

1. **사용자 확인 필수**: GitHub에 리뷰를 제출하기 전 반드시 AskUserQuestion으로 확인 (`--approve` 80+ 제외)
2. **증거 기반**: 모든 이슈는 파일명, 라인번호, 코드 스니펫, 수정 제안 포함
3. **건설적 피드백**: 비판이 아닌 개선 방향 제시
4. **기존 리뷰 존중**: 이미 달린 리뷰/코멘트를 확인하고 중복 피드백 회피
5. **Security Zero-Tolerance**: 보안 이슈(Security Critical) 발견 시 점수와 무관하게 FAIL/차단(Request Changes)
6. **인라인 코멘트**: Critical/Major 이슈만 인라인으로, Minor/Info는 본문에 포함
7. **PR 작성자 배려**: 긍정적인 부분도 언급, 학습 관점의 피드백
8. **점수는 근거와 함께**: 보고하는 모든 점수는 구체적 findings(파일/라인/근거)와 함께 제시 — 근거 없는 단순 숫자만 출력 금지

## Examples

### 기본 리뷰

```
입력: /review-pr 123

결과:
PR #123: Add user authentication API
Score: NN/100 (등급) — (판단)
- 1 Major issue (인라인 코멘트)
- 2 Minor suggestions
GitHub에 리뷰 코멘트를 남겼습니다.
```

### 심층 리뷰

```
입력: /review-pr 123 --level 3

결과:
PR #123: Add user authentication API
Score: NN/100 (등급) — COMMENT (수정 권장)
- 호출 체인 분석: AuthService → UserRepo → DB (3단계)
- 에지 케이스 3건 발견
- 동시성 이슈 1건
GitHub에 상세 리뷰 코멘트를 남겼습니다.
```

### 로컬만 확인

```
입력: /review-pr 123 --no-comment

결과:
PR #123: Add user authentication API
Score: NN/100 (등급)
(GitHub에 코멘트를 남기지 않았습니다)
```
