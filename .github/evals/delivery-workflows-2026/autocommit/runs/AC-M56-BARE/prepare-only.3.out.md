커밋 준비 제안:

- 범위: `app.py`만 포함
- 변경: `value()` 아래에 `# user change` 주석 추가
- 제외: `unrelated.txt` 등 다른 파일
- 제안 메시지: `chore: add user change marker`
- 테스트: `python3 -m unittest -v` 통과 (1개)
- `git diff --check`: 이상 없음

stage, commit, push는 수행하지 않았습니다. 현재 작업 트리에는 수정된 `app.py`만 남아 있습니다.