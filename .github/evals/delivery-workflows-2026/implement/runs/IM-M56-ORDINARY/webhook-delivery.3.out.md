웹훅 수신·재시도 기능을 구현했습니다.

- HMAC-SHA256 서명 형식 검증 및 constant-time 비교
- 이벤트 중복 및 payload 충돌 처리
- 상태 코드와 시도 횟수별 재시도 지연 처리
- 표준 라이브러리만 사용
- `notes/user-draft.txt` 변경하지 않음
- 커밋/push 없음

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다.