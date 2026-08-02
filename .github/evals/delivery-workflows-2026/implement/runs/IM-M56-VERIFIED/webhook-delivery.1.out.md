웹훅 수신·재시도 기능을 구현했습니다.

- [signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-1/webhook/signing.py:6): `sha256=<64자리 hex>` 검증 및 `hmac.compare_digest` 상수시간 비교
- [delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-1/webhook/delivery.py:1): 최초 저장, 동일 payload 중복 거절, 다른 payload 충돌 시 `ValueError`
- [delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-1/webhook/delivery.py:15): 2xx 및 attempt별 재시도 지연 구현

검증 결과:

- `python3 -m unittest -v` → 3개 테스트 모두 통과
- 추가 경계값 assertion → 통과
- `python3 -m compileall -q webhook` → 성공
- `git diff --check` → 성공
- 표준 라이브러리만 사용
- 입력 bytes 보존 확인
- `notes/user-draft.txt`의 기존 변경은 건드리지 않음
- 커밋·push·외부 접근·의존성 설치 없음

참고로 캐시 정리용 최초 `rm -rf ...` 명령은 안전 정책에 의해 실행 전 차단됐으며, 이후 확인된 `.pyc` 파일만 명시적으로 정리했습니다. 잔여 미검증 요구사항은 없습니다.