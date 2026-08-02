차단급(Blocker)은 없습니다. 다만 다음은 High 수준입니다.

1. **[High] Unicode 검증 규칙이 구현 간 일관되게 판정될 만큼 정의되지 않았습니다.**  
   `grapheme cluster`, `공백`, `일반 공백`, `제어문자`의 Unicode 버전·속성·분할 알고리즘이 명시되지 않았습니다. 예를 들어 NBSP, 줄바꿈 문자, zero-width/format 문자, 결합 문자와 emoji sequence의 허용 여부가 구현체마다 달라질 수 있습니다. 최소한 Unicode 버전, UAX #29 extended grapheme cluster 기준, trim 대상 코드포인트/속성, 금지할 Unicode category를 계약으로 고정해야 합니다.

2. **[High] P0 Unicode 요구사항을 acceptance criteria가 실제로 검증하지 못합니다.**  
   AC-101의 `"홍길동"`은 이미 NFC이므로 정규화 수행 여부를 입증하지 않습니다. AC-104도 ASCII 1/41자로 통과할 수 있어 code point가 아닌 grapheme cluster를 세는지 검증하지 못합니다. 분해형 문자, 결합 문자, ZWJ emoji 등으로 명시적인 테스트 벡터와 기대 결과가 필요합니다.

3. **[High] PATCH 요청·응답 및 오류 계약이 불완전합니다.**  
   `displayName`의 타입, `null`/누락 값 처리, 성공 status/body, 422 필드 오류의 구조·안정적인 오류 코드가 없습니다. 그런데 UI는 “저장된 정규화 이름”과 “서버 메시지”를 표시해야 하므로 프런트엔드가 정규화 결과와 오류를 안정적으로 식별할 방법이 정해지지 않았습니다. 이 상태에서는 팀별 구현이 서로 달라도 AC를 동일하게 해석할 수 있습니다.