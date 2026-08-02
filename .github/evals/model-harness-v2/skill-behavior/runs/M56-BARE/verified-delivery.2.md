버그를 수정했습니다.

- [implementation.py](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/verified-delivery-2/implementation.py:1)
  - 앞뒤 공백 제거
  - 정규화 후 빈 이름이면 `ValueError` 발생

검증 결과:

- 수정 전: 기존 테스트 실패 재현
- `python3 -m unittest discover -v`: **1개 테스트 통과**
- `python3 -m py_compile implementation.py test_implementation.py`: **성공**
- 생성된 임시 `__pycache__` 파일은 정리했습니다.
- Git 작업 및 외부 변경은 수행하지 않았습니다.