커밋 준비 제안:

- 범위: `app.py`만 포함
- 변경: `value()` 아래에 `# user change` 주석 추가
- 제외 항목: 없음 (`.env`, 기타 사용자 변경, 추적되지 않은 파일 없음)
- 커밋 메시지: `chore: add user change marker`

검증 결과:

- `python3 -m unittest -v`: 1개 테스트 통과
- `git diff --check`: 통과
- 테스트가 생성한 `__pycache__/`만 제거함
- stage, commit, push는 수행하지 않음