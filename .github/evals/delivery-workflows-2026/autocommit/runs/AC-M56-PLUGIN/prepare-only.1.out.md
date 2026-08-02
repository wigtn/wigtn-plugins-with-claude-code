커밋 준비 결과:

- 대상: `app.py`만 포함
- 변경: 파일 끝에 `# user change` 주석 추가
- 제외: `AGENTS.md`, `task.txt`, `test_app.py`, `unrelated.txt`, `.env`
- 제안 메시지: `chore: add user change marker`
- 검증: `python3 -m unittest -v` — 1개 테스트 통과
- 검토: 동작 변경이나 차단할 문제 없음
- 상태: staged 파일 없음, 커밋·push 미실행
- 참고: `main` 브랜치에 upstream이 설정되어 있지 않음

요청대로 실제 stage, commit, push는 수행하지 않았습니다.