커밋 준비 제안:

- 범위: `app.py`의 파일 끝에 빈 줄과 `# user change` 주석 추가만 포함
- 제외: 그 외 파일 전체
- 커밋 메시지: `chore: add user change marker`
- 검증: `python3 -m unittest -v` 통과 (1개 테스트)
- 현재 상태: 스테이징·커밋·푸시 모두 수행하지 않음

`git diff --check`에서도 문제없습니다.