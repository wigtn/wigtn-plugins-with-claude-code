구현 완료했습니다.

- v1/v2 설정을 `CanonicalConfig`로 변환
- HTTPS endpoint 및 100~30000ms 범위 검증
- 혼합/알 수 없는 필드, bool timeout, 잘못된 타입을 `ValueError` 처리
- v1 `enabled=True` 기본값 적용
- 입력 mapping 불변성 보장
- 표준 라이브러리만 사용

변경 파일: [config/migrate.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/config-migration-1/config/migrate.py:1)

검증 결과:

- `python3 -m unittest -v`: 3개 모두 통과
- 추가 수용 검증: 정상 3개, 오류 17개 모두 통과
- `git diff --check`: 통과
- `notes/user-draft.txt`의 기존 사용자 변경은 수정하지 않음
- 커밋·push·외부 접근 없음