# 픽스처 eval 결과 — `baseline`

## 검출률 (심어둔 결함을 잡았는가)

| 픽스처 | 결함 | severity | 검출 | 비율 |
|---|---|---|---|---|
| `code-defective.ts` | C-D1 searchDocuments: 사용자 입력을 SQL 문자열에 직접 보 | critical | ✅ 3/3 | 100% |
| `code-defective.ts` | C-D2 SHARE_TOKEN_SECRET 이 소스에 하드코딩 | critical | ✅ 3/3 | 100% |
| `code-defective.ts` | C-D3 listDocumentsWithOwners: 루프 안에서 쿼리 (N+ | major | ✅ 3/3 | 100% |
| `code-defective.ts` | C-D4 deleteDocument / list / search: 세션·소유자 | critical | ✅ 3/3 | 100% |
| `code-defective.ts` | C-D5 deleteDocument: doc[0] 존재 확인 없이 접근 → 없 | major | ✅ 3/3 | 100% |
| `code-defective.ts` | C-D6 sign(): base64(JSON+secret)는 위조 가능. 만료 | critical | ✅ 3/3 | 100% |
| `prd-defective.md` | P-D1 §5.4.1 State Matrix 섹션 자체가 없음 (FE 페이지  | critical | ✅ 3/3 | 100% |
| `prd-defective.md` | P-D2 §5.5 User Flow(Mermaid) 섹션이 없음 | critical | ✅ 3/3 | 100% |
| `prd-defective.md` | P-D3 FR-003(로그인 없이 열람) vs FR-007(모든 조회 인증 필 | critical | ✅ 3/3 | 100% |
| `prd-defective.md` | P-D4 FR-005 관리자 삭제 엔드포인트에 인가(권한 검증) 명세 없음 | critical | ✅ 3/3 | 100% |
| `prd-defective.md` | P-D5 Scale Grade Startup인데 §4.1 성능 목표가 정성적( | major | ✅ 3/3 | 100% |

- **`code-defective.ts` 종합 검출률: 18/18 = 100%**
- **`prd-defective.md` 종합 검출률: 15/15 = 100%**

## 오탐 (깨끗한 픽스처에 무엇을 다는가)

> **critical 만 오탐 지표로 쓴다.** 게이트의 차단 조건이 `critical ≥1` 이고,
> 현실적인 PRD·코드에는 major/minor 지적거리가 늘 있기 때문이다 — 그건 리뷰가
> 하라고 있는 일이지 오탐이 아니다.

| 픽스처 | 실행 | critical | major | 판정 |
|---|---|---|---|---|
| `code-clean.ts` | 1 | 0 | 0 | ✅ 무결 |
| `code-clean.ts` | 2 | 0 | 0 | ✅ 무결 |
| `prd-clean.md` | 1 | 0 | 6 | ✅ 무결 |
| `prd-clean.md` | 2 | 0 | 3 | ✅ 무결 |

> 검출률과 오탐률은 **함께** 봐야 한다. 검출률만 올리는 가장 쉬운 방법은
> 모든 것을 critical로 찍는 것이고, 그러면 게이트가 무의미해진다.
