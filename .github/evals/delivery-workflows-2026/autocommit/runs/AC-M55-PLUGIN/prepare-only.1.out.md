커밋 준비만 완료했습니다. 실제 `stage`, `commit`, `push`는 하지 않았습니다.

**제안 범위**
- 포함: [app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M55-PLUGIN-work/prepare-only-1/app.py:4)
- 변경 내용: 파일 끝에 `# user change` 주석 추가
- 제외: 없음
- 현재 상태: `app.py`만 unstaged 수정 상태
- 브랜치: `main`
- upstream: 설정 없음

**제안 커밋 메시지**
```text
chore: add user change marker
```

**검증**
- `python3 -m unittest -v` 통과: 1개 테스트 OK
- `git diff --check` 통과
- 테스트로 생성된 `__pycache__/`는 정리했습니다.