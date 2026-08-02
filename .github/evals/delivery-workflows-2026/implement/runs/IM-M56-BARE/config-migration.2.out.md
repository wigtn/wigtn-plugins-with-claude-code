구현 완료했습니다.

- v1/v2 설정을 `CanonicalConfig`로 변환
- HTTPS endpoint 검증
- timeout 100~30000ms 및 bool/비정상 숫자 거부
- 혼합 필드, 알 수 없는 필드, 타입 오류를 `ValueError`로 처리
- 입력 mapping 불변 및 v1 `enabled=True` 적용
- 표준 라이브러리만 사용

검증 결과: `python3 -m unittest -v` 전체 3개 테스트 통과.

변경 파일: [config/migrate.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/config-migration-2/config/migrate.py)

기존에 수정 상태였던 `notes/user-draft.txt`는 건드리지 않았으며 커밋·push도 하지 않았습니다.