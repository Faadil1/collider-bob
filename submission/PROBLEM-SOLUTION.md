# Problem & Solution
Problem
Parallel AI coding agents can each produce locally valid implementations while
silently making different choices about requirements the shared specification
never decided.
Those disagreements may not appear as Git conflicts, syntax errors, or failing
unit tests. Each workstream can be green in isolation and still become
incompatible when the pieces meet.
Our canonical fixture demonstrates exactly this failure mode. API, Ledger, and
Notifications all pass their local tests, yet integration reveals two
incompatible assumptions: API identifies the customer by email while Ledger
uses account_id, and API uses refund_amount while Ledger uses
credit_amount.
Treating both as generic integration failures loses the most useful
information: they have different causes.
Solution
COLLIDER uses independent implementation interpretations as ambiguity probes.
For each disagreement, it checks the source evidence and separates two cases:
AGENT_DRIFT — the specification already decided the question and an agent
deviated from it. In the canonical fixture, the brief explicitly specifies
refund_amount, so Ledger's credit_amount implementation is repaired directly
from source evidence without asking a human.
SPEC_GAP — multiple implementations are plausible because the source never
made the decision. API chooses email; Ledger chooses account_id; the brief
chooses neither. COLLIDER preserves the epistemic state as UNKNOWN, refuses to
auto-resolve, and asks one minimal clarification.
After the human decision selects account_id, COLLIDER writes a durable canon
patch and repairs only the implementation that depended on the missing
decision. Notifications remains unchanged.
In the canonical LOCAL/PRESEEDED comparison, the same starting workstream
artifacts move from 2 executable integration conflicts and
INTEGRATION_BLOCKED to 0 conflicts and INTEGRATION_READY.
COLLIDER does not claim live Bob-generated canonical interpretations, time
savings, percentage productivity improvement, or production-scale
generalization. Its current evidence proves the local classification,
abstention, canon, targeted-repair, integration, and evidence-binding loop.
