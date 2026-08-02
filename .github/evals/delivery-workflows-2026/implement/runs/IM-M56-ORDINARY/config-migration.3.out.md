구현 완료했습니다.

- v1/v2 설정을 `CanonicalConfig`로 변환
- HTTPS endpoint 검증
- timeout 100~30000ms 검증 및 bool 배제
- 혼합 스키마, 알 수 없는 필드, 입력 타입 오류를 `ValueError` 처리
- v1 `enabled=True` 기본값 적용
- 입력 mapping 불변성 유지
- 기존 `notes/user-draft.txt` 변경 보존
- 커밋·push 없음

검증 결과:

```text
Ran 3 tests
OK
```

추가 경계 사례 16개와 `git diff --check`도 통과했습니다.

변경 파일: [config/migrate.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/config-migration-3/config/migrate.py)