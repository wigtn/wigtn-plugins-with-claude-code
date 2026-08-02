커밋 준비 결과:

- 범위: `app.py`만 포함
  - 빈 줄 및 `# user change` 주석 추가
  - 2줄 추가, 기능 변경 없음
- 제안 메시지: `chore: add user change marker`
- 검증: `python3 -m unittest -v` 통과 (1 test)
- 리뷰 이슈: 없음
- 현재 상태: staged 파일 없음, commit/push 미실행
- 참고: `main` 브랜치에 upstream이 설정되어 있지 않음

테스트가 생성한 `__pycache__/`는 정리했으며, 사용자 변경은 보존했습니다.