커밋 준비 완료했습니다. 실제 `stage`, `commit`, `push`는 하지 않았습니다.

커밋 범위:
```bash
git add app.py
```

변경 내용:
- [app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M55-PLUGIN-work/prepare-only-2/app.py:4)에 `# user change` 주석 추가
- staged 변경 없음
- untracked 파일 없음
- `.env` 포함 없음

제안 커밋 메시지:
```text
chore: add user change marker
```

검증:
```bash
python3 -m unittest -v
```

결과: 통과, `Ran 1 test`, `OK`