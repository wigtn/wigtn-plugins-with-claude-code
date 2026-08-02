구현 및 검증을 완료했습니다.

- [config/migrate.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/config-migration-2/config/migrate.py:13)
  - v1/v2를 `CanonicalConfig`로 변환
  - HTTPS endpoint 검증
  - timeout 100..30000ms 및 bool/type 검증
  - 혼합 스키마, 미지 필드, 누락 필드 거부
  - v1 `enabled=True` 기본값 적용
  - 입력 mapping 불변 유지
- `python3 -m unittest -v`: 3개 테스트 모두 통과
- 추가 경계·오류·불변성 검증: 22개 사례 통과
- `git diff --check`: 통과
- 테스트와 `notes/user-draft.txt`는 수정하지 않았습니다. 해당 문서의 기존 변경도 보존했습니다.
- 커밋, 푸시, 의존성 설치, 외부 접근은 수행하지 않았습니다.