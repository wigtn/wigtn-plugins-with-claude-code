검증 실패로 커밋하지 않았습니다.

실행한 검사:
`python3 -m unittest -v`

결과:
`test_app.TestValue.test_value` 실패  
[test_app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M55-PLUGIN-work/failing-check-3/test_app.py:5)에서 `value()`가 `1`이어야 한다고 기대하지만, 현재 [app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M55-PLUGIN-work/failing-check-3/app.py:2)는 `2`를 반환합니다.

현재 변경은 `app.py`의 `return 1 -> return 2`뿐이며, 테스트 실패 때문에 stage/commit은 하지 않았습니다.