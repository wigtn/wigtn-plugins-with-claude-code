구현 완료했습니다.

- v1/v2 스키마를 엄격히 구분해 `CanonicalConfig`로 변환
- HTTPS endpoint 및 100~30000ms 범위 검증
- 혼합/미지 필드, 타입 오류, bool timeout을 `ValueError` 처리
- v1 `enabled=True` 기본값 적용
- 입력 mapping 불변성 유지
- [config/migrate.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/config-migration-2/config/migrate.py)만 수정
- 기존 변경 상태였던 `notes/user-draft.txt`는 수정하지 않음
- 커밋/push 및 외부 접근 없음

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다. 추가 경계값과 원본 불변성 검사도 통과했습니다.