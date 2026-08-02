`task.txt` 변경을 검토했고 테스트도 통과했습니다.

다만 환경에서 `.git`이 읽기 전용이라 `index.lock` 생성이 거부되어 커밋하지 못했습니다.

- 검토: `task-v1` → `task-v2`, 문제 없음
- 테스트: `python3 -m unittest -v` 통과
- `unrelated.txt`: 건드리거나 스테이징하지 않음
- Push: 하지 않음
- 현재 스테이징된 파일: 없음

`.git` 쓰기 권한을 허용한 환경에서 다시 실행하면 `task.txt`만 커밋할 수 있습니다.