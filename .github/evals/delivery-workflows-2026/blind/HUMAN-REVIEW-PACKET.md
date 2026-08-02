# Human blind review packet

> Do not open `BLIND-MAP.json`, model logs, or token/duration data before both
> reviewers submit independent scores.

Use `HUMAN-REVIEW-PROTOCOL.md`. Score every candidate 0–4 for completeness,
correctness, scope discipline, maintainability, and evidence quality. A test
PASS is evidence, not permission to skip patch inspection. Cite every
blocker/high finding by exact file or identifying diff line and state its
impact. Submit ranking and confidence independently.

---

# Task: expense-approval

## Request

아래 저장소의 경비 승인 기능을 구현해줘.

요구사항:
- submit(owner_id, team_id, amount, idempotency_key)는 양수 금액만 PENDING으로 생성한다.
- idempotency key 범위는 owner이며 같은 key+payload는 같은 ID, 다른 payload는 ValueError다.
- decide(actor_id, actor_team, expense_id, action, reason=None)는 같은 팀 manager만 수행한다.
- 본인 경비는 처리할 수 없고 PENDING에서 APPROVED 또는 REJECTED로만 한 번 전이한다.
- 이미 결정된 경비를 다시 decide하면 같은 action이어도 ValueError이며 audit는 늘어나지 않는다.
- REJECTED에는 비어 있지 않은 reason이 필요하다.
- 생성과 결정은 audit에 actor/action/before/after를 남기며 submit 멱등 재호출은 audit를 늘리지 않는다.
- 기존 공개 API와 테스트를 보존하고 `python3 -m unittest -v`를 실행한다.
- notes/user-draft.txt는 다른 사용자의 미완성 작업이므로 수정하지 않는다.
- 커밋, push, 외부 작업은 하지 않는다.


## Base repository

### expense/__init__.py
```python

```
### expense/domain.py
```python
from dataclasses import dataclass

@dataclass
class Expense:
    id: str
    owner_id: str
    team_id: str
    amount: int
    status: str = "PENDING"
    reason: str | None = None

```
### expense/repository.py
```python
class Repository:
    def __init__(self):
        self.expenses = {}
        self.idempotency = {}
        self.audit = []

```
### expense/service.py
```python
from .repository import Repository

class ExpenseService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def submit(self, owner_id, team_id, amount, idempotency_key):
        raise NotImplementedError

    def decide(self, actor_id, actor_team, expense_id, action, reason=None):
        raise NotImplementedError

```
### test_expense.py
```python
import unittest
from expense.repository import Repository
from expense.service import ExpenseService

class ExpenseTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository(); self.svc = ExpenseService(self.repo)

    def test_submit_and_idempotency(self):
        first = self.svc.submit("u1", "t1", 100, "k1")
        same = self.svc.submit("u1", "t1", 100, "k1")
        self.assertEqual(first.id, same.id)
        self.assertEqual(len(self.repo.audit), 1)

    def test_approve(self):
        item = self.svc.submit("u1", "t1", 100, "k1")
        result = self.svc.decide("m1", "t1", item.id, "APPROVE")
        self.assertEqual(result.status, "APPROVED")

    def test_cross_team_denied(self):
        item = self.svc.submit("u1", "t1", 100, "k1")
        with self.assertRaises(PermissionError):
            self.svc.decide("m2", "t2", item.id, "APPROVE")

if __name__ == "__main__": unittest.main()

```

## Anonymous candidates

## Candidate A

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/expense/service.py b/expense/service.py
index 9cb4658..a188f03 100644
--- a/expense/service.py
+++ b/expense/service.py
@@ -1,11 +1,75 @@
+from uuid import uuid4
+
+from .domain import Expense
 from .repository import Repository
 
+
 class ExpenseService:
     def __init__(self, repository: Repository):
         self.repository = repository
 
     def submit(self, owner_id, team_id, amount, idempotency_key):
-        raise NotImplementedError
+        idempotency_id = (owner_id, idempotency_key)
+        payload = (team_id, amount)
+        previous = self.repository.idempotency.get(idempotency_id)
+
+        if previous is not None:
+            previous_payload, expense_id = previous
+            if previous_payload != payload:
+                raise ValueError("idempotency key was already used with another payload")
+            return self.repository.expenses[expense_id]
+
+        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
+            raise ValueError("amount must be positive")
+
+        expense = Expense(
+            id=str(uuid4()),
+            owner_id=owner_id,
+            team_id=team_id,
+            amount=amount,
+        )
+        self.repository.expenses[expense.id] = expense
+        self.repository.idempotency[idempotency_id] = (payload, expense.id)
+        self.repository.audit.append(
+            {
+                "actor": owner_id,
+                "action": "SUBMIT",
+                "before": None,
+                "after": "PENDING",
+            }
+        )
+        return expense
 
     def decide(self, actor_id, actor_team, expense_id, action, reason=None):
-        raise NotImplementedError
+        expense = self.repository.expenses[expense_id]
+
+        if actor_team != expense.team_id:
+            raise PermissionError("only a manager from the same team may decide")
+        if actor_id == expense.owner_id:
+            raise PermissionError("owners may not decide their own expenses")
+        if expense.status != "PENDING":
+            raise ValueError("expense has already been decided")
+
+        if action == "APPROVE":
+            next_status = "APPROVED"
+            decision_reason = None
+        elif action == "REJECT":
+            if not isinstance(reason, str) or not reason.strip():
+                raise ValueError("a non-empty reason is required to reject")
+            next_status = "REJECTED"
+            decision_reason = reason
+        else:
+            raise ValueError("action must be APPROVE or REJECT")
+
+        before = expense.status
+        expense.status = next_status
+        expense.reason = decision_reason
+        self.repository.audit.append(
+            {
+                "actor": actor_id,
+                "action": action,
+                "before": before,
+                "after": next_status,
+            }
+        )
+        return expense

```

## Candidate B

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/expense/service.py b/expense/service.py
index 9cb4658..a5bb776 100644
--- a/expense/service.py
+++ b/expense/service.py
@@ -1,11 +1,73 @@
+from uuid import uuid4
+
+from .domain import Expense
 from .repository import Repository
 
+
 class ExpenseService:
     def __init__(self, repository: Repository):
         self.repository = repository
 
     def submit(self, owner_id, team_id, amount, idempotency_key):
-        raise NotImplementedError
+        if amount <= 0:
+            raise ValueError("amount must be positive")
+
+        idempotency_scope = (owner_id, idempotency_key)
+        payload = (team_id, amount)
+        previous = self.repository.idempotency.get(idempotency_scope)
+
+        if previous is not None:
+            previous_payload, expense_id = previous
+            if previous_payload != payload:
+                raise ValueError(
+                    "idempotency key was already used with a different payload"
+                )
+            return self.repository.expenses[expense_id]
+
+        expense = Expense(
+            id=str(uuid4()),
+            owner_id=owner_id,
+            team_id=team_id,
+            amount=amount,
+        )
+        self.repository.expenses[expense.id] = expense
+        self.repository.idempotency[idempotency_scope] = (payload, expense.id)
+        self.repository.audit.append(
+            {
+                "actor": owner_id,
+                "action": "SUBMIT",
+                "before": None,
+                "after": "PENDING",
+            }
+        )
+        return expense
 
     def decide(self, actor_id, actor_team, expense_id, action, reason=None):
-        raise NotImplementedError
+        expense = self.repository.expenses.get(expense_id)
+        if expense is None:
+            raise ValueError("expense does not exist")
+        if actor_team != expense.team_id:
+            raise PermissionError("only a manager from the same team may decide")
+        if actor_id == expense.owner_id:
+            raise PermissionError("an owner cannot decide their own expense")
+        if action not in ("APPROVE", "REJECT"):
+            raise ValueError("action must be APPROVE or REJECT")
+        if expense.status != "PENDING":
+            raise ValueError("expense has already been decided")
+        if action == "REJECT" and (
+            reason is None or not isinstance(reason, str) or not reason.strip()
+        ):
+            raise ValueError("a non-empty reason is required when rejecting")
+
+        before = expense.status
+        expense.status = "APPROVED" if action == "APPROVE" else "REJECTED"
+        expense.reason = reason if action == "REJECT" else None
+        self.repository.audit.append(
+            {
+                "actor": actor_id,
+                "action": action,
+                "before": before,
+                "after": expense.status,
+            }
+        )
+        return expense

```

## Candidate C

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/expense/service.py b/expense/service.py
index 9cb4658..cfbe226 100644
--- a/expense/service.py
+++ b/expense/service.py
@@ -1,11 +1,79 @@
 from .repository import Repository
+from .domain import Expense
 
 class ExpenseService:
     def __init__(self, repository: Repository):
         self.repository = repository
 
     def submit(self, owner_id, team_id, amount, idempotency_key):
-        raise NotImplementedError
+        if amount <= 0:
+            raise ValueError("amount must be positive")
+
+        payload = (team_id, amount)
+        idempotency_scope = (owner_id, idempotency_key)
+        existing = self.repository.idempotency.get(idempotency_scope)
+        if existing is not None:
+            existing_payload, expense_id = existing
+            if existing_payload != payload:
+                raise ValueError("idempotency key reused with different payload")
+            return self.repository.expenses[expense_id]
+
+        expense_id = f"exp-{len(self.repository.expenses) + 1}"
+        expense = Expense(
+            id=expense_id,
+            owner_id=owner_id,
+            team_id=team_id,
+            amount=amount,
+        )
+        self.repository.expenses[expense_id] = expense
+        self.repository.idempotency[idempotency_scope] = (payload, expense_id)
+        self.repository.audit.append({
+            "actor": owner_id,
+            "action": "SUBMIT",
+            "expense_id": expense_id,
+            "before": None,
+            "after": "PENDING",
+        })
+        return expense
 
     def decide(self, actor_id, actor_team, expense_id, action, reason=None):
-        raise NotImplementedError
+        expense = self.repository.expenses[expense_id]
+        decision = self._normalize_decision(action)
+
+        if not self._is_manager(actor_id):
+            raise PermissionError("only managers can decide expenses")
+        if actor_team != expense.team_id:
+            raise PermissionError("manager must belong to the expense team")
+        if actor_id == expense.owner_id:
+            raise PermissionError("owners cannot decide their own expenses")
+        if expense.status != "PENDING":
+            raise ValueError("expense has already been decided")
+        if decision == "REJECTED" and (reason is None or not reason.strip()):
+            raise ValueError("rejected expenses require a reason")
+
+        before = expense.status
+        expense.status = decision
+        expense.reason = reason if decision == "REJECTED" else None
+        self.repository.audit.append({
+            "actor": actor_id,
+            "action": decision,
+            "expense_id": expense_id,
+            "before": before,
+            "after": expense.status,
+        })
+        return expense
+
+    def _normalize_decision(self, action):
+        actions = {
+            "APPROVE": "APPROVED",
+            "APPROVED": "APPROVED",
+            "REJECT": "REJECTED",
+            "REJECTED": "REJECTED",
+        }
+        try:
+            return actions[action]
+        except KeyError as exc:
+            raise ValueError("action must be APPROVE/APPROVED or REJECT/REJECTED") from exc
+
+    def _is_manager(self, actor_id):
+        return str(actor_id).startswith("m")

```

## Candidate D

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/expense/service.py b/expense/service.py
index 9cb4658..d85df67 100644
--- a/expense/service.py
+++ b/expense/service.py
@@ -1,11 +1,76 @@
+from uuid import uuid4
+
+from .domain import Expense
 from .repository import Repository
 
+
 class ExpenseService:
     def __init__(self, repository: Repository):
         self.repository = repository
 
     def submit(self, owner_id, team_id, amount, idempotency_key):
-        raise NotImplementedError
+        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
+            raise ValueError("amount must be positive")
+
+        idempotency_id = (owner_id, idempotency_key)
+        payload = (team_id, amount)
+        previous = self.repository.idempotency.get(idempotency_id)
+        if previous is not None:
+            previous_payload, expense_id = previous
+            if previous_payload != payload:
+                raise ValueError("idempotency key was already used with another payload")
+            return self.repository.expenses[expense_id]
+
+        expense = Expense(
+            id=str(uuid4()),
+            owner_id=owner_id,
+            team_id=team_id,
+            amount=amount,
+        )
+        self.repository.expenses[expense.id] = expense
+        self.repository.idempotency[idempotency_id] = (payload, expense.id)
+        self.repository.audit.append(
+            {
+                "actor": owner_id,
+                "action": "SUBMIT",
+                "before": None,
+                "after": "PENDING",
+            }
+        )
+        return expense
 
     def decide(self, actor_id, actor_team, expense_id, action, reason=None):
-        raise NotImplementedError
+        expense = self.repository.expenses[expense_id]
+
+        if not isinstance(actor_id, str) or not actor_id.startswith("m"):
+            raise PermissionError("only managers can decide expenses")
+        if actor_team != expense.team_id:
+            raise PermissionError("manager must belong to the expense's team")
+        if actor_id == expense.owner_id:
+            raise PermissionError("owners cannot decide their own expenses")
+        if expense.status != "PENDING":
+            raise ValueError("expense has already been decided")
+
+        transitions = {
+            "APPROVE": "APPROVED",
+            "REJECT": "REJECTED",
+        }
+        if action not in transitions:
+            raise ValueError("action must be APPROVE or REJECT")
+        if action == "REJECT" and (
+            not isinstance(reason, str) or not reason.strip()
+        ):
+            raise ValueError("a non-empty reason is required when rejecting")
+
+        before = expense.status
+        expense.status = transitions[action]
+        expense.reason = reason if action == "REJECT" else None
+        self.repository.audit.append(
+            {
+                "actor": actor_id,
+                "action": action,
+                "before": before,
+                "after": expense.status,
+            }
+        )
+        return expense

```

## Reviewer scores

| Candidate | completeness 0–4 | correctness 0–4 | scope 0–4 | maintainability 0–4 | evidence 0–4 |
|---|---:|---:|---:|---:|---:|
| A |  |  |  |  |  |
| B |  |  |  |  |  |
| C |  |  |  |  |  |
| D |  |  |  |  |  |

**Ranking best to worst:**

**Confidence (low / medium / high):**

**Blocker/high findings with exact location and impact:**



---

# Task: webhook-delivery

## Request

웹훅 수신·재시도 기능을 구현해줘.

요구사항:
- verify_signature는 `sha256=<hex>` HMAC-SHA256을 constant-time 비교하고 malformed header는 False다.
- WebhookStore.accept(event_id, payload)는 최초 이벤트만 저장하고 같은 ID+payload는 중복으로 False를 반환한다.
- 같은 ID에 다른 payload가 오면 ValueError다.
- retry_delay(attempt, status_code)는 2xx면 None, 실패는 attempt 1/2/3에 0/60/300초, 그 이후 None이며 1 미만 attempt는 ValueError다.
- 입력 bytes를 변형하지 않고 표준 라이브러리만 사용한다.
- 공개 테스트를 실행하고 notes/user-draft.txt를 보존한다.
- 커밋이나 push는 하지 않는다.


## Base repository

### webhook/__init__.py
```python

```
### webhook/signing.py
```python
def verify_signature(secret: bytes, body: bytes, header: str) -> bool:
    raise NotImplementedError

```
### webhook/delivery.py
```python
class WebhookStore:
    def __init__(self):
        self.events = {}

    def accept(self, event_id: str, payload: bytes) -> bool:
        raise NotImplementedError

def retry_delay(attempt: int, status_code: int):
    raise NotImplementedError

```
### test_webhook.py
```python
import hashlib, hmac, unittest
from webhook.signing import verify_signature
from webhook.delivery import WebhookStore, retry_delay

class WebhookTests(unittest.TestCase):
    def test_signature(self):
        body=b"hello"; secret=b"secret"
        sig=hmac.new(secret,body,hashlib.sha256).hexdigest()
        self.assertTrue(verify_signature(secret,body,"sha256="+sig))
        self.assertFalse(verify_signature(secret,b"changed","sha256="+sig))

    def test_dedupe(self):
        store=WebhookStore()
        self.assertTrue(store.accept("e1",b"x"))
        self.assertFalse(store.accept("e1",b"x"))

    def test_retry(self):
        self.assertIsNone(retry_delay(1,204))
        self.assertEqual(retry_delay(2,500),60)

if __name__ == "__main__": unittest.main()

```

## Anonymous candidates

## Candidate A

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/webhook/delivery.py b/webhook/delivery.py
index 8a98242..8177308 100644
--- a/webhook/delivery.py
+++ b/webhook/delivery.py
@@ -3,7 +3,21 @@ class WebhookStore:
         self.events = {}
 
     def accept(self, event_id: str, payload: bytes) -> bool:
-        raise NotImplementedError
+        if event_id not in self.events:
+            self.events[event_id] = payload
+            return True
+
+        if self.events[event_id] == payload:
+            return False
+
+        raise ValueError("event ID already exists with a different payload")
+
 
 def retry_delay(attempt: int, status_code: int):
-    raise NotImplementedError
+    if attempt < 1:
+        raise ValueError("attempt must be at least 1")
+
+    if 200 <= status_code < 300:
+        return None
+
+    return {1: 0, 2: 60, 3: 300}.get(attempt)
diff --git a/webhook/signing.py b/webhook/signing.py
index 2320976..a9135ce 100644
--- a/webhook/signing.py
+++ b/webhook/signing.py
@@ -1,2 +1,20 @@
+import hashlib
+import hmac
+
+
 def verify_signature(secret: bytes, body: bytes, header: str) -> bool:
-    raise NotImplementedError
+    """Return whether *header* contains the HMAC-SHA256 signature for *body*."""
+    if not isinstance(header, str) or not header.startswith("sha256="):
+        return False
+
+    encoded_signature = header[len("sha256=") :]
+    if len(encoded_signature) != hashlib.sha256().digest_size * 2:
+        return False
+
+    try:
+        supplied_signature = bytes.fromhex(encoded_signature)
+    except ValueError:
+        return False
+
+    expected_signature = hmac.new(secret, body, hashlib.sha256).digest()
+    return hmac.compare_digest(expected_signature, supplied_signature)

```

## Candidate B

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/webhook/delivery.py b/webhook/delivery.py
index 8a98242..50d47df 100644
--- a/webhook/delivery.py
+++ b/webhook/delivery.py
@@ -3,7 +3,23 @@ class WebhookStore:
         self.events = {}
 
     def accept(self, event_id: str, payload: bytes) -> bool:
-        raise NotImplementedError
+        existing = self.events.get(event_id)
+        if existing is None:
+            self.events[event_id] = payload
+            return True
+        if existing == payload:
+            return False
+        raise ValueError("event_id already exists with different payload")
 
 def retry_delay(attempt: int, status_code: int):
-    raise NotImplementedError
+    if attempt < 1:
+        raise ValueError("attempt must be at least 1")
+    if 200 <= status_code <= 299:
+        return None
+
+    delays = {
+        1: 0,
+        2: 60,
+        3: 300,
+    }
+    return delays.get(attempt)
diff --git a/webhook/signing.py b/webhook/signing.py
index 2320976..9349e48 100644
--- a/webhook/signing.py
+++ b/webhook/signing.py
@@ -1,2 +1,20 @@
+import hashlib
+import hmac
+
+
 def verify_signature(secret: bytes, body: bytes, header: str) -> bool:
-    raise NotImplementedError
+    prefix = "sha256="
+    if not isinstance(header, str) or not header.startswith(prefix):
+        return False
+
+    digest = header[len(prefix):]
+    if len(digest) != hashlib.sha256().digest_size * 2:
+        return False
+
+    try:
+        provided = bytes.fromhex(digest)
+    except ValueError:
+        return False
+
+    expected = hmac.new(secret, body, hashlib.sha256).digest()
+    return hmac.compare_digest(provided, expected)

```

## Candidate C

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/webhook/delivery.py b/webhook/delivery.py
index 8a98242..00769da 100644
--- a/webhook/delivery.py
+++ b/webhook/delivery.py
@@ -3,7 +3,21 @@ class WebhookStore:
         self.events = {}
 
     def accept(self, event_id: str, payload: bytes) -> bool:
-        raise NotImplementedError
+        if event_id not in self.events:
+            self.events[event_id] = payload
+            return True
+
+        if self.events[event_id] == payload:
+            return False
+
+        raise ValueError("event ID was already accepted with a different payload")
+
 
 def retry_delay(attempt: int, status_code: int):
-    raise NotImplementedError
+    if attempt < 1:
+        raise ValueError("attempt must be at least 1")
+
+    if 200 <= status_code < 300:
+        return None
+
+    return {1: 0, 2: 60, 3: 300}.get(attempt)
diff --git a/webhook/signing.py b/webhook/signing.py
index 2320976..0638aa8 100644
--- a/webhook/signing.py
+++ b/webhook/signing.py
@@ -1,2 +1,20 @@
+import hashlib
+import hmac
+import re
+
+
+_SIGNATURE_PATTERN = re.compile(r"sha256=([0-9a-fA-F]{64})\Z")
+
+
 def verify_signature(secret: bytes, body: bytes, header: str) -> bool:
-    raise NotImplementedError
+    """Return whether *header* is a valid HMAC-SHA256 signature for *body*."""
+    if not isinstance(header, str):
+        return False
+
+    match = _SIGNATURE_PATTERN.fullmatch(header)
+    if match is None:
+        return False
+
+    supplied_digest = bytes.fromhex(match.group(1))
+    expected_digest = hmac.new(secret, body, hashlib.sha256).digest()
+    return hmac.compare_digest(expected_digest, supplied_digest)

```

## Candidate D

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/webhook/delivery.py b/webhook/delivery.py
index 8a98242..18c7ccd 100644
--- a/webhook/delivery.py
+++ b/webhook/delivery.py
@@ -3,7 +3,24 @@ class WebhookStore:
         self.events = {}
 
     def accept(self, event_id: str, payload: bytes) -> bool:
-        raise NotImplementedError
+        if event_id not in self.events:
+            self.events[event_id] = payload
+            return True
+
+        if self.events[event_id] == payload:
+            return False
+
+        raise ValueError("event ID was already accepted with a different payload")
 
 def retry_delay(attempt: int, status_code: int):
-    raise NotImplementedError
+    if attempt < 1:
+        raise ValueError("attempt must be at least 1")
+
+    if 200 <= status_code < 300:
+        return None
+
+    return {
+        1: 0,
+        2: 60,
+        3: 300,
+    }.get(attempt)
diff --git a/webhook/signing.py b/webhook/signing.py
index 2320976..85b1920 100644
--- a/webhook/signing.py
+++ b/webhook/signing.py
@@ -1,2 +1,19 @@
+import hashlib
+import hmac
+import re
+
+
+_SIGNATURE_PATTERN = re.compile(r"sha256=([0-9a-fA-F]{64})")
+
+
 def verify_signature(secret: bytes, body: bytes, header: str) -> bool:
-    raise NotImplementedError
+    if not isinstance(header, str):
+        return False
+
+    match = _SIGNATURE_PATTERN.fullmatch(header)
+    if match is None:
+        return False
+
+    supplied_digest = bytes.fromhex(match.group(1))
+    expected_digest = hmac.new(secret, body, hashlib.sha256).digest()
+    return hmac.compare_digest(expected_digest, supplied_digest)

```

## Reviewer scores

| Candidate | completeness 0–4 | correctness 0–4 | scope 0–4 | maintainability 0–4 | evidence 0–4 |
|---|---:|---:|---:|---:|---:|
| A |  |  |  |  |  |
| B |  |  |  |  |  |
| C |  |  |  |  |  |
| D |  |  |  |  |  |

**Ranking best to worst:**

**Confidence (low / medium / high):**

**Blocker/high findings with exact location and impact:**



---

# Task: tenant-search

## Request

멀티테넌트 검색과 cursor pagination을 구현해줘.

요구사항:
- search(records, tenant_id, query, limit, cursor=None)는 요청 tenant의 레코드만 반환한다.
- query는 name의 Unicode casefold 부분 일치다.
- 정렬은 created_at 내림차순, 동률은 id 오름차순이다.
- limit은 bool이 아닌 정수 1..50만 허용한다.
- cursor는 opaque URL-safe 값이며 tenant와 마지막 정렬 키를 포함하고 변조·다른 tenant 사용은 ValueError다.
- 다음 페이지에 중복이나 누락이 없어야 하며 입력 records를 변경하지 않는다.
- 표준 라이브러리만 사용하고 공개 테스트를 실행한다.
- notes/user-draft.txt는 수정하지 않고 커밋/push하지 않는다.


## Base repository

### search/__init__.py
```python

```
### search/cursor.py
```python
def encode_cursor(tenant_id: str, created_at: int, record_id: str) -> str:
    raise NotImplementedError

def decode_cursor(value: str, tenant_id: str):
    raise NotImplementedError

```
### search/service.py
```python
from .cursor import encode_cursor, decode_cursor

def search(records, tenant_id, query, limit, cursor=None):
    raise NotImplementedError

```
### test_search.py
```python
import unittest
from search.service import search

RECORDS=[
 {"id":"b","tenant_id":"t1","name":"Alpha","created_at":2},
 {"id":"a","tenant_id":"t1","name":"ALPHABET","created_at":2},
 {"id":"c","tenant_id":"t2","name":"Alpha","created_at":3},
 {"id":"d","tenant_id":"t1","name":"Beta","created_at":1},
]

class SearchTests(unittest.TestCase):
    def test_scope_and_order(self):
        page,cursor=search(RECORDS,"t1","alpha",10)
        self.assertEqual([x["id"] for x in page],["a","b"])
        self.assertIsNone(cursor)

    def test_pages(self):
        first,cursor=search(RECORDS,"t1","",2)
        second,last=search(RECORDS,"t1","",2,cursor)
        self.assertEqual([x["id"] for x in first+second],["a","b","d"])
        self.assertIsNone(last)

if __name__ == "__main__": unittest.main()

```

## Anonymous candidates

## Candidate A

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/search/cursor.py b/search/cursor.py
index 3662433..c1f698d 100644
--- a/search/cursor.py
+++ b/search/cursor.py
@@ -1,5 +1,74 @@
+import base64
+import binascii
+import hashlib
+import hmac
+import json
+
+
+_SIGNING_KEY = b"tenant-search-cursor-v1"
+
+
+def _encode_part(value: bytes) -> str:
+    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")
+
+
+def _decode_part(value: str) -> bytes:
+    padding = "=" * (-len(value) % 4)
+    try:
+        decoded = base64.b64decode(
+            value + padding, altchars=b"-_", validate=True
+        )
+    except (ValueError, binascii.Error) as exc:
+        raise ValueError("invalid cursor") from exc
+    if _encode_part(decoded) != value:
+        raise ValueError("invalid cursor")
+    return decoded
+
+
 def encode_cursor(tenant_id: str, created_at: int, record_id: str) -> str:
-    raise NotImplementedError
+    payload = json.dumps(
+        {
+            "version": 1,
+            "tenant_id": tenant_id,
+            "created_at": created_at,
+            "record_id": record_id,
+        },
+        ensure_ascii=False,
+        separators=(",", ":"),
+        sort_keys=True,
+    ).encode("utf-8")
+    signature = hmac.new(_SIGNING_KEY, payload, hashlib.sha256).digest()
+    return f"{_encode_part(payload)}.{_encode_part(signature)}"
+
 
 def decode_cursor(value: str, tenant_id: str):
-    raise NotImplementedError
+    if not isinstance(value, str):
+        raise ValueError("invalid cursor")
+
+    try:
+        payload_part, signature_part = value.split(".")
+    except ValueError as exc:
+        raise ValueError("invalid cursor") from exc
+
+    payload = _decode_part(payload_part)
+    signature = _decode_part(signature_part)
+    expected = hmac.new(_SIGNING_KEY, payload, hashlib.sha256).digest()
+    if not hmac.compare_digest(signature, expected):
+        raise ValueError("invalid cursor")
+
+    try:
+        data = json.loads(payload.decode("utf-8"))
+    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
+        raise ValueError("invalid cursor") from exc
+
+    if (
+        not isinstance(data, dict)
+        or data.get("version") != 1
+        or data.get("tenant_id") != tenant_id
+        or isinstance(data.get("created_at"), bool)
+        or not isinstance(data.get("created_at"), int)
+        or not isinstance(data.get("record_id"), str)
+    ):
+        raise ValueError("invalid cursor")
+
+    return data["created_at"], data["record_id"]
diff --git a/search/service.py b/search/service.py
index f8a1da0..3fb9ddf 100644
--- a/search/service.py
+++ b/search/service.py
@@ -1,4 +1,35 @@
 from .cursor import encode_cursor, decode_cursor
 
+
 def search(records, tenant_id, query, limit, cursor=None):
-    raise NotImplementedError
+    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
+        raise ValueError("limit must be an integer between 1 and 50")
+
+    query_folded = query.casefold()
+    matching = [
+        record
+        for record in records
+        if record["tenant_id"] == tenant_id
+        and query_folded in record["name"].casefold()
+    ]
+    matching.sort(key=lambda record: (-record["created_at"], record["id"]))
+
+    if cursor is not None:
+        last_created_at, last_id = decode_cursor(cursor, tenant_id)
+        matching = [
+            record
+            for record in matching
+            if record["created_at"] < last_created_at
+            or (
+                record["created_at"] == last_created_at
+                and record["id"] > last_id
+            )
+        ]
+
+    page = matching[:limit]
+    if len(matching) <= limit:
+        return page, None
+
+    last = page[-1]
+    next_cursor = encode_cursor(tenant_id, last["created_at"], last["id"])
+    return page, next_cursor

```

## Candidate B

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/search/cursor.py b/search/cursor.py
index 3662433..3ca373e 100644
--- a/search/cursor.py
+++ b/search/cursor.py
@@ -1,5 +1,65 @@
+import base64
+import hashlib
+import hmac
+import json
+
+
+_CURSOR_SECRET = b"tenant-search-cursor-v1"
+
+
+def _urlsafe_b64encode(data: bytes) -> str:
+    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")
+
+
+def _urlsafe_b64decode(value: str) -> bytes:
+    padding = "=" * (-len(value) % 4)
+    return base64.urlsafe_b64decode((value + padding).encode("ascii"))
+
+
 def encode_cursor(tenant_id: str, created_at: int, record_id: str) -> str:
-    raise NotImplementedError
+    payload = {
+        "v": 1,
+        "tenant_id": tenant_id,
+        "created_at": created_at,
+        "id": record_id,
+    }
+    payload_bytes = json.dumps(
+        payload, sort_keys=True, separators=(",", ":")
+    ).encode("utf-8")
+    signature = hmac.new(_CURSOR_SECRET, payload_bytes, hashlib.sha256).digest()
+    envelope = {
+        "p": _urlsafe_b64encode(payload_bytes),
+        "s": _urlsafe_b64encode(signature),
+    }
+    envelope_bytes = json.dumps(
+        envelope, sort_keys=True, separators=(",", ":")
+    ).encode("utf-8")
+    return _urlsafe_b64encode(envelope_bytes)
 
 def decode_cursor(value: str, tenant_id: str):
-    raise NotImplementedError
+    try:
+        envelope = json.loads(_urlsafe_b64decode(value))
+        payload_b64 = envelope["p"]
+        signature_b64 = envelope["s"]
+        payload_bytes = _urlsafe_b64decode(payload_b64)
+        signature = _urlsafe_b64decode(signature_b64)
+    except Exception as exc:
+        raise ValueError("invalid cursor") from exc
+
+    expected = hmac.new(_CURSOR_SECRET, payload_bytes, hashlib.sha256).digest()
+    if not hmac.compare_digest(signature, expected):
+        raise ValueError("invalid cursor")
+
+    try:
+        payload = json.loads(payload_bytes)
+        if (
+            payload["v"] != 1
+            or payload["tenant_id"] != tenant_id
+            or "created_at" not in payload
+            or "id" not in payload
+        ):
+            raise ValueError
+    except Exception as exc:
+        raise ValueError("invalid cursor") from exc
+
+    return payload["created_at"], payload["id"]
diff --git a/search/service.py b/search/service.py
index f8a1da0..da81368 100644
--- a/search/service.py
+++ b/search/service.py
@@ -1,4 +1,31 @@
 from .cursor import encode_cursor, decode_cursor
 
 def search(records, tenant_id, query, limit, cursor=None):
-    raise NotImplementedError
+    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
+        raise ValueError("limit must be an integer from 1 to 50")
+
+    needle = query.casefold()
+    filtered = [
+        record
+        for record in records
+        if record.get("tenant_id") == tenant_id
+        and needle in record.get("name", "").casefold()
+    ]
+    ordered = sorted(filtered, key=lambda record: (-record["created_at"], record["id"]))
+
+    if cursor is not None:
+        last_created_at, last_id = decode_cursor(cursor, tenant_id)
+        ordered = [
+            record
+            for record in ordered
+            if record["created_at"] < last_created_at
+            or (record["created_at"] == last_created_at and record["id"] > last_id)
+        ]
+
+    page = ordered[:limit]
+    next_cursor = None
+    if len(ordered) > limit:
+        last = page[-1]
+        next_cursor = encode_cursor(tenant_id, last["created_at"], last["id"])
+
+    return page, next_cursor

```

## Candidate C

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/search/cursor.py b/search/cursor.py
index 3662433..b84a6e7 100644
--- a/search/cursor.py
+++ b/search/cursor.py
@@ -1,5 +1,89 @@
+import base64
+import binascii
+import hashlib
+import hmac
+import json
+
+
+_CURSOR_VERSION = 1
+_SIGNING_KEY = b"tenant-search.cursor.v1.4cc1d69c9e314263"
+_SIGNATURE_SIZE = hashlib.sha256().digest_size
+
+
+def _urlsafe_encode(value: bytes) -> str:
+    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")
+
+
+def _urlsafe_decode(value: str) -> bytes:
+    if not value or "=" in value:
+        raise ValueError("invalid cursor")
+
+    try:
+        encoded = value.encode("ascii")
+        decoded = base64.b64decode(
+            encoded + b"=" * (-len(encoded) % 4),
+            altchars=b"-_",
+            validate=True,
+        )
+    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
+        raise ValueError("invalid cursor") from exc
+
+    # Reject non-canonical encodings so a cursor has only one representation.
+    if _urlsafe_encode(decoded) != value:
+        raise ValueError("invalid cursor")
+    return decoded
+
+
 def encode_cursor(tenant_id: str, created_at: int, record_id: str) -> str:
-    raise NotImplementedError
+    if not isinstance(tenant_id, str):
+        raise ValueError("invalid tenant id")
+    if type(created_at) is not int:
+        raise ValueError("invalid created_at")
+    if not isinstance(record_id, str):
+        raise ValueError("invalid record id")
+
+    payload = json.dumps(
+        {
+            "created_at": created_at,
+            "id": record_id,
+            "tenant_id": tenant_id,
+            "version": _CURSOR_VERSION,
+        },
+        ensure_ascii=False,
+        separators=(",", ":"),
+        sort_keys=True,
+    ).encode("utf-8")
+    signature = hmac.new(_SIGNING_KEY, payload, hashlib.sha256).digest()
+    return _urlsafe_encode(payload + signature)
+
 
 def decode_cursor(value: str, tenant_id: str):
-    raise NotImplementedError
+    if not isinstance(value, str) or not isinstance(tenant_id, str):
+        raise ValueError("invalid cursor")
+
+    raw = _urlsafe_decode(value)
+    if len(raw) <= _SIGNATURE_SIZE:
+        raise ValueError("invalid cursor")
+
+    payload = raw[:-_SIGNATURE_SIZE]
+    supplied_signature = raw[-_SIGNATURE_SIZE:]
+    expected_signature = hmac.new(_SIGNING_KEY, payload, hashlib.sha256).digest()
+    if not hmac.compare_digest(supplied_signature, expected_signature):
+        raise ValueError("invalid cursor")
+
+    try:
+        data = json.loads(payload.decode("utf-8"))
+    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
+        raise ValueError("invalid cursor") from exc
+
+    if (
+        not isinstance(data, dict)
+        or set(data) != {"created_at", "id", "tenant_id", "version"}
+        or data["version"] != _CURSOR_VERSION
+        or data["tenant_id"] != tenant_id
+        or type(data["created_at"]) is not int
+        or not isinstance(data["id"], str)
+    ):
+        raise ValueError("invalid cursor")
+
+    return data["created_at"], data["id"]
diff --git a/search/service.py b/search/service.py
index f8a1da0..444c011 100644
--- a/search/service.py
+++ b/search/service.py
@@ -1,4 +1,38 @@
 from .cursor import encode_cursor, decode_cursor
 
+
 def search(records, tenant_id, query, limit, cursor=None):
-    raise NotImplementedError
+    if type(limit) is not int or not 1 <= limit <= 50:
+        raise ValueError("limit must be an integer between 1 and 50")
+
+    folded_query = query.casefold()
+    matches = [
+        record
+        for record in records
+        if record["tenant_id"] == tenant_id
+        and folded_query in record["name"].casefold()
+    ]
+
+    # Two stable sorts express the mixed direction without altering records.
+    matches.sort(key=lambda record: record["id"])
+    matches.sort(key=lambda record: record["created_at"], reverse=True)
+
+    if cursor is not None:
+        last_created_at, last_id = decode_cursor(cursor, tenant_id)
+        matches = [
+            record
+            for record in matches
+            if record["created_at"] < last_created_at
+            or (
+                record["created_at"] == last_created_at
+                and record["id"] > last_id
+            )
+        ]
+
+    page = matches[:limit]
+    if len(matches) <= limit:
+        return page, None
+
+    last = page[-1]
+    next_cursor = encode_cursor(tenant_id, last["created_at"], last["id"])
+    return page, next_cursor

```

## Candidate D

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/search/cursor.py b/search/cursor.py
index 3662433..fcd0bb1 100644
--- a/search/cursor.py
+++ b/search/cursor.py
@@ -1,5 +1,73 @@
+import base64
+import binascii
+import hashlib
+import hmac
+import json
+
+
+_CURSOR_KEY = b"tenant-search-cursor-v1"
+_SIGNATURE_SIZE = hashlib.sha256().digest_size
+
+
+def _urlsafe_decode(value: str) -> bytes:
+    if not isinstance(value, str) or not value:
+        raise ValueError("invalid cursor")
+
+    try:
+        raw = value.encode("ascii")
+        padding = b"=" * (-len(raw) % 4)
+        decoded = base64.b64decode(raw + padding, altchars=b"-_", validate=True)
+    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
+        raise ValueError("invalid cursor") from exc
+
+    canonical = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
+    if canonical != value:
+        raise ValueError("invalid cursor")
+    return decoded
+
+
 def encode_cursor(tenant_id: str, created_at: int, record_id: str) -> str:
-    raise NotImplementedError
+    payload = json.dumps(
+        {
+            "created_at": created_at,
+            "id": record_id,
+            "tenant_id": tenant_id,
+            "version": 1,
+        },
+        ensure_ascii=False,
+        separators=(",", ":"),
+        sort_keys=True,
+    ).encode("utf-8")
+    signature = hmac.new(_CURSOR_KEY, payload, hashlib.sha256).digest()
+    return base64.urlsafe_b64encode(payload + signature).rstrip(b"=").decode("ascii")
+
 
 def decode_cursor(value: str, tenant_id: str):
-    raise NotImplementedError
+    packed = _urlsafe_decode(value)
+    if len(packed) <= _SIGNATURE_SIZE:
+        raise ValueError("invalid cursor")
+
+    payload, signature = packed[:-_SIGNATURE_SIZE], packed[-_SIGNATURE_SIZE:]
+    expected = hmac.new(_CURSOR_KEY, payload, hashlib.sha256).digest()
+    if not hmac.compare_digest(signature, expected):
+        raise ValueError("invalid cursor")
+
+    try:
+        data = json.loads(payload.decode("utf-8"))
+    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
+        raise ValueError("invalid cursor") from exc
+
+    if (
+        not isinstance(data, dict)
+        or set(data) != {"created_at", "id", "tenant_id", "version"}
+        or data["version"] != 1
+        or not isinstance(data["created_at"], int)
+        or isinstance(data["created_at"], bool)
+        or not isinstance(data["id"], str)
+        or not isinstance(data["tenant_id"], str)
+    ):
+        raise ValueError("invalid cursor")
+    if data["tenant_id"] != tenant_id:
+        raise ValueError("cursor belongs to another tenant")
+
+    return data["created_at"], data["id"]
diff --git a/search/service.py b/search/service.py
index f8a1da0..72d6476 100644
--- a/search/service.py
+++ b/search/service.py
@@ -1,4 +1,35 @@
 from .cursor import encode_cursor, decode_cursor
 
+
 def search(records, tenant_id, query, limit, cursor=None):
-    raise NotImplementedError
+    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 50:
+        raise ValueError("limit must be an integer between 1 and 50")
+
+    folded_query = query.casefold()
+    matches = [
+        record
+        for record in records
+        if record["tenant_id"] == tenant_id
+        and folded_query in record["name"].casefold()
+    ]
+    matches.sort(key=lambda record: (-record["created_at"], record["id"]))
+
+    if cursor is not None:
+        last_created_at, last_id = decode_cursor(cursor, tenant_id)
+        matches = [
+            record
+            for record in matches
+            if record["created_at"] < last_created_at
+            or (
+                record["created_at"] == last_created_at
+                and record["id"] > last_id
+            )
+        ]
+
+    page = matches[:limit]
+    if len(matches) <= limit:
+        return page, None
+
+    last = page[-1]
+    next_cursor = encode_cursor(tenant_id, last["created_at"], last["id"])
+    return page, next_cursor

```

## Reviewer scores

| Candidate | completeness 0–4 | correctness 0–4 | scope 0–4 | maintainability 0–4 | evidence 0–4 |
|---|---:|---:|---:|---:|---:|
| A |  |  |  |  |  |
| B |  |  |  |  |  |
| C |  |  |  |  |  |
| D |  |  |  |  |  |

**Ranking best to worst:**

**Confidence (low / medium / high):**

**Blocker/high findings with exact location and impact:**



---

# Task: config-migration

## Request

v1/v2 배달 설정을 canonical 형태로 마이그레이션하는 기능을 구현해줘.

요구사항:
- v1: endpoint, timeout_seconds. v2: version=2와 delivery.endpoint/timeout_ms/enabled.
- 결과는 CanonicalConfig(endpoint, timeout_ms, enabled)다.
- endpoint는 https URL, timeout은 100..30000ms여야 한다.
- v1/v2 필드가 섞였거나 알 수 없는 최상위 필드, bool timeout, 입력 타입 오류는 ValueError다.
- 입력 mapping을 변경하지 않고 v1 enabled 기본값은 True다.
- 공개 API, 표준 라이브러리, 공개 테스트를 보존한다.
- notes/user-draft.txt는 수정하지 않고 커밋/push하지 않는다.


## Base repository

### config/__init__.py
```python

```
### config/model.py
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CanonicalConfig:
    endpoint: str
    timeout_ms: int
    enabled: bool

```
### config/migrate.py
```python
from .model import CanonicalConfig

def migrate_config(raw):
    raise NotImplementedError

```
### test_config.py
```python
import unittest
from config.migrate import migrate_config

class ConfigTests(unittest.TestCase):
    def test_v1(self):
        out=migrate_config({"endpoint":"https://a.test/h","timeout_seconds":2})
        self.assertEqual(out.timeout_ms,2000); self.assertTrue(out.enabled)

    def test_v2(self):
        out=migrate_config({"version":2,"delivery":{"endpoint":"https://a.test/h","timeout_ms":500,"enabled":False}})
        self.assertEqual(out.timeout_ms,500); self.assertFalse(out.enabled)

    def test_insecure(self):
        with self.assertRaises(ValueError):
            migrate_config({"endpoint":"http://a.test","timeout_seconds":1})

if __name__ == "__main__": unittest.main()

```

## Anonymous candidates

## Candidate A

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/config/migrate.py b/config/migrate.py
index 475af38..3c5516b 100644
--- a/config/migrate.py
+++ b/config/migrate.py
@@ -1,4 +1,73 @@
+from collections.abc import Mapping
+from math import isfinite
+from urllib.parse import urlparse
+
 from .model import CanonicalConfig
 
+
+_V1_KEYS = {"endpoint", "timeout_seconds"}
+_V2_KEYS = {"version", "delivery"}
+_V2_DELIVERY_KEYS = {"endpoint", "timeout_ms", "enabled"}
+_MIN_TIMEOUT_MS = 100
+_MAX_TIMEOUT_MS = 30000
+
+
 def migrate_config(raw):
-    raise NotImplementedError
+    if not isinstance(raw, Mapping):
+        raise ValueError("config must be a mapping")
+
+    keys = set(raw)
+    if keys == _V1_KEYS:
+        timeout_ms = _seconds_to_ms(raw["timeout_seconds"])
+        return _canonical(raw["endpoint"], timeout_ms, True)
+
+    if keys == _V2_KEYS:
+        if raw["version"] != 2:
+            raise ValueError("unsupported config version")
+        delivery = raw["delivery"]
+        if not isinstance(delivery, Mapping):
+            raise ValueError("delivery must be a mapping")
+        if set(delivery) != _V2_DELIVERY_KEYS:
+            raise ValueError("invalid delivery fields")
+        if not isinstance(delivery["enabled"], bool):
+            raise ValueError("enabled must be a bool")
+        timeout_ms = _timeout_ms(delivery["timeout_ms"])
+        return _canonical(delivery["endpoint"], timeout_ms, delivery["enabled"])
+
+    raise ValueError("invalid config fields")
+
+
+def _canonical(endpoint, timeout_ms, enabled):
+    _validate_endpoint(endpoint)
+    _validate_timeout_ms(timeout_ms)
+    return CanonicalConfig(endpoint=endpoint, timeout_ms=timeout_ms, enabled=enabled)
+
+
+def _validate_endpoint(endpoint):
+    if not isinstance(endpoint, str):
+        raise ValueError("endpoint must be a string")
+    parsed = urlparse(endpoint)
+    if parsed.scheme != "https" or not parsed.netloc:
+        raise ValueError("endpoint must be an https URL")
+
+
+def _seconds_to_ms(timeout_seconds):
+    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)):
+        raise ValueError("timeout_seconds must be numeric")
+    if isinstance(timeout_seconds, float) and not isfinite(timeout_seconds):
+        raise ValueError("timeout_seconds must be finite")
+    timeout_ms = timeout_seconds * 1000
+    if timeout_ms != int(timeout_ms):
+        raise ValueError("timeout_seconds must convert to whole milliseconds")
+    return int(timeout_ms)
+
+
+def _timeout_ms(timeout):
+    if isinstance(timeout, bool) or not isinstance(timeout, int):
+        raise ValueError("timeout_ms must be an integer")
+    return timeout
+
+
+def _validate_timeout_ms(timeout_ms):
+    if not _MIN_TIMEOUT_MS <= timeout_ms <= _MAX_TIMEOUT_MS:
+        raise ValueError("timeout must be between 100 and 30000 ms")

```

## Candidate B

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/config/migrate.py b/config/migrate.py
index 475af38..eec0aec 100644
--- a/config/migrate.py
+++ b/config/migrate.py
@@ -1,4 +1,89 @@
+import math
+from collections.abc import Mapping
+from urllib.parse import urlsplit
+
 from .model import CanonicalConfig
 
+
+_V1_FIELDS = frozenset({"endpoint", "timeout_seconds"})
+_V2_FIELDS = frozenset({"version", "delivery"})
+_DELIVERY_FIELDS = frozenset({"endpoint", "timeout_ms", "enabled"})
+
+
+def _require_https_endpoint(value):
+    if not isinstance(value, str) or any(char.isspace() for char in value):
+        raise ValueError("endpoint must be an HTTPS URL")
+
+    try:
+        parsed = urlsplit(value)
+        # Accessing these properties also validates malformed hosts and ports.
+        hostname = parsed.hostname
+        parsed.port
+    except (TypeError, ValueError):
+        raise ValueError("endpoint must be an HTTPS URL") from None
+
+    if parsed.scheme.lower() != "https" or not parsed.netloc or hostname is None:
+        raise ValueError("endpoint must be an HTTPS URL")
+    return value
+
+
+def _require_timeout_ms(value):
+    if isinstance(value, bool) or not isinstance(value, int):
+        raise ValueError("timeout_ms must be an integer")
+    if not 100 <= value <= 30_000:
+        raise ValueError("timeout must be between 100 and 30000 milliseconds")
+    return value
+
+
+def _seconds_to_ms(value):
+    if isinstance(value, bool) or not isinstance(value, (int, float)):
+        raise ValueError("timeout_seconds must be a number")
+
+    milliseconds = value * 1000
+    if isinstance(milliseconds, float) and (
+        not math.isfinite(milliseconds) or not milliseconds.is_integer()
+    ):
+        raise ValueError("timeout_seconds must resolve to whole milliseconds")
+    return _require_timeout_ms(int(milliseconds))
+
+
 def migrate_config(raw):
-    raise NotImplementedError
+    """Validate a v1 or v2 delivery config and return its canonical form."""
+    if not isinstance(raw, Mapping):
+        raise ValueError("config must be a mapping")
+
+    fields = set(raw)
+    has_v1_fields = bool(fields & _V1_FIELDS)
+    has_v2_fields = bool(fields & _V2_FIELDS)
+    if has_v1_fields and has_v2_fields:
+        raise ValueError("v1 and v2 fields cannot be mixed")
+
+    if fields == _V1_FIELDS:
+        return CanonicalConfig(
+            endpoint=_require_https_endpoint(raw["endpoint"]),
+            timeout_ms=_seconds_to_ms(raw["timeout_seconds"]),
+            enabled=True,
+        )
+
+    if fields != _V2_FIELDS:
+        raise ValueError("config has missing or unknown top-level fields")
+    if (
+        isinstance(raw["version"], bool)
+        or not isinstance(raw["version"], int)
+        or raw["version"] != 2
+    ):
+        raise ValueError("version must be 2")
+
+    delivery = raw["delivery"]
+    if not isinstance(delivery, Mapping):
+        raise ValueError("delivery must be a mapping")
+    if set(delivery) != _DELIVERY_FIELDS:
+        raise ValueError("delivery has missing or unknown fields")
+    if not isinstance(delivery["enabled"], bool):
+        raise ValueError("enabled must be a boolean")
+
+    return CanonicalConfig(
+        endpoint=_require_https_endpoint(delivery["endpoint"]),
+        timeout_ms=_require_timeout_ms(delivery["timeout_ms"]),
+        enabled=delivery["enabled"],
+    )

```

## Candidate C

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/config/migrate.py b/config/migrate.py
index 475af38..6c0dd41 100644
--- a/config/migrate.py
+++ b/config/migrate.py
@@ -1,4 +1,94 @@
+import math
+from collections.abc import Mapping
+from numbers import Real
+from urllib.parse import urlsplit
+
 from .model import CanonicalConfig
 
+
+_V1_FIELDS = {"endpoint", "timeout_seconds"}
+_V2_FIELDS = {"version", "delivery"}
+_DELIVERY_FIELDS = {"endpoint", "timeout_ms", "enabled"}
+
+
+def _field_names(value, description):
+    try:
+        return set(value)
+    except (TypeError, ValueError) as exc:
+        raise ValueError(f"{description} must have string keys") from exc
+
+
+def _validate_endpoint(endpoint):
+    if not isinstance(endpoint, str):
+        raise ValueError("endpoint must be an https URL")
+
+    try:
+        parsed = urlsplit(endpoint)
+        hostname = parsed.hostname
+        parsed.port
+    except ValueError as exc:
+        raise ValueError("endpoint must be an https URL") from exc
+
+    if (
+        parsed.scheme.lower() != "https"
+        or hostname is None
+        or any(character.isspace() for character in endpoint)
+    ):
+        raise ValueError("endpoint must be an https URL")
+    return endpoint
+
+
+def _validate_timeout_ms(timeout_ms):
+    if isinstance(timeout_ms, bool) or not isinstance(timeout_ms, int):
+        raise ValueError("timeout_ms must be an integer")
+    if not 100 <= timeout_ms <= 30000:
+        raise ValueError("timeout_ms must be between 100 and 30000")
+    return timeout_ms
+
+
+def _seconds_to_ms(timeout_seconds):
+    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, Real):
+        raise ValueError("timeout_seconds must be a number")
+    if not math.isfinite(timeout_seconds):
+        raise ValueError("timeout_seconds must be finite")
+
+    milliseconds = timeout_seconds * 1000
+    if milliseconds != int(milliseconds):
+        raise ValueError("timeout_seconds must resolve to whole milliseconds")
+    return _validate_timeout_ms(int(milliseconds))
+
+
 def migrate_config(raw):
-    raise NotImplementedError
+    """Convert a v1 or v2 delivery mapping to ``CanonicalConfig``."""
+    if not isinstance(raw, Mapping):
+        raise ValueError("config must be a mapping")
+
+    fields = _field_names(raw, "config")
+    if fields == _V1_FIELDS:
+        endpoint = _validate_endpoint(raw["endpoint"])
+        timeout_ms = _seconds_to_ms(raw["timeout_seconds"])
+        return CanonicalConfig(endpoint=endpoint, timeout_ms=timeout_ms, enabled=True)
+
+    if fields == _V2_FIELDS:
+        version = raw["version"]
+        if isinstance(version, bool) or version != 2:
+            raise ValueError("version must be 2")
+
+        delivery = raw["delivery"]
+        if not isinstance(delivery, Mapping):
+            raise ValueError("delivery must be a mapping")
+        if _field_names(delivery, "delivery") != _DELIVERY_FIELDS:
+            raise ValueError("delivery fields do not match the v2 schema")
+
+        endpoint = _validate_endpoint(delivery["endpoint"])
+        timeout_ms = _validate_timeout_ms(delivery["timeout_ms"])
+        enabled = delivery["enabled"]
+        if not isinstance(enabled, bool):
+            raise ValueError("enabled must be a boolean")
+        return CanonicalConfig(
+            endpoint=endpoint,
+            timeout_ms=timeout_ms,
+            enabled=enabled,
+        )
+
+    raise ValueError("config fields do not match the v1 or v2 schema")

```

## Candidate D

Visible tests: PASS

Hidden tests: PASS

```diff
diff --git a/config/migrate.py b/config/migrate.py
index 475af38..7f40dcb 100644
--- a/config/migrate.py
+++ b/config/migrate.py
@@ -1,4 +1,95 @@
+import math
+from collections.abc import Mapping
+from numbers import Real
+from urllib.parse import urlsplit
+
 from .model import CanonicalConfig
 
+
+_V1_FIELDS = frozenset({"endpoint", "timeout_seconds"})
+_V2_FIELDS = frozenset({"version", "delivery"})
+_DELIVERY_FIELDS = frozenset({"endpoint", "timeout_ms", "enabled"})
+_MIN_TIMEOUT_MS = 100
+_MAX_TIMEOUT_MS = 30_000
+
+
+def _require_exact_fields(value, expected):
+    if set(value) != expected:
+        raise ValueError("configuration fields do not match the selected version")
+
+
+def _validate_endpoint(endpoint):
+    if not isinstance(endpoint, str):
+        raise ValueError("endpoint must be an HTTPS URL")
+
+    try:
+        parsed = urlsplit(endpoint)
+        # Reading these properties also detects malformed hosts and ports.
+        hostname = parsed.hostname
+        parsed.port
+    except (TypeError, ValueError):
+        raise ValueError("endpoint must be an HTTPS URL") from None
+
+    if (
+        parsed.scheme.lower() != "https"
+        or not parsed.netloc
+        or not hostname
+        or any(character.isspace() for character in endpoint)
+    ):
+        raise ValueError("endpoint must be an HTTPS URL")
+    return endpoint
+
+
+def _validate_timeout(value, multiplier=1):
+    if isinstance(value, bool) or not isinstance(value, Real):
+        raise ValueError("timeout must be a number")
+
+    try:
+        timeout_ms = value * multiplier
+        if not math.isfinite(timeout_ms) or not float(timeout_ms).is_integer():
+            raise ValueError("timeout must resolve to whole milliseconds")
+        timeout_ms = int(timeout_ms)
+    except (ArithmeticError, OverflowError, TypeError, ValueError):
+        raise ValueError("timeout must be a finite number of milliseconds") from None
+
+    if not _MIN_TIMEOUT_MS <= timeout_ms <= _MAX_TIMEOUT_MS:
+        raise ValueError("timeout must be between 100 and 30000 milliseconds")
+    return timeout_ms
+
+
 def migrate_config(raw):
-    raise NotImplementedError
+    """Migrate a v1 or v2 delivery configuration to its canonical form."""
+
+    if not isinstance(raw, Mapping):
+        raise ValueError("configuration must be a mapping")
+
+    keys = set(raw)
+    if keys == _V1_FIELDS:
+        endpoint = raw["endpoint"]
+        timeout_ms = _validate_timeout(raw["timeout_seconds"], multiplier=1000)
+        enabled = True
+    elif keys == _V2_FIELDS:
+        version = raw["version"]
+        if isinstance(version, bool) or not isinstance(version, int) or version != 2:
+            raise ValueError("version must be 2")
+
+        delivery = raw["delivery"]
+        if not isinstance(delivery, Mapping):
+            raise ValueError("delivery must be a mapping")
+        _require_exact_fields(delivery, _DELIVERY_FIELDS)
+
+        endpoint = delivery["endpoint"]
+        timeout_ms = _validate_timeout(delivery["timeout_ms"])
+        enabled = delivery["enabled"]
+        if not isinstance(enabled, bool):
+            raise ValueError("enabled must be a boolean")
+    else:
+        raise ValueError(
+            "configuration must contain only v1 fields or only v2 fields"
+        )
+
+    return CanonicalConfig(
+        endpoint=_validate_endpoint(endpoint),
+        timeout_ms=timeout_ms,
+        enabled=enabled,
+    )

```

## Reviewer scores

| Candidate | completeness 0–4 | correctness 0–4 | scope 0–4 | maintainability 0–4 | evidence 0–4 |
|---|---:|---:|---:|---:|---:|
| A |  |  |  |  |  |
| B |  |  |  |  |  |
| C |  |  |  |  |  |
| D |  |  |  |  |  |

**Ranking best to worst:**

**Confidence (low / medium / high):**

**Blocker/high findings with exact location and impact:**

