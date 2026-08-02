커밋 준비 결과입니다. 실제 `stage`, `commit`, `push`는 하지 않았습니다.

커밋 범위:
```bash
app.py
```

포함할 변경:
```diff
 def value():
     return 1
+
+# user change
```

제안 커밋 메시지:
```text
Add user change marker
```

검증:
```bash
python3 -m unittest -v
```
결과: 통과, `Ran 1 test`, `OK`

참고:
- 현재 브랜치: `main`
- upstream: 설정 없음
- staged 파일 없음
- 제외할 파일 없음
- 테스트 실행으로 생긴 `__pycache__/`는 제거했습니다.