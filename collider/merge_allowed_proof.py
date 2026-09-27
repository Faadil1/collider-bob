"""Non-semantic proof marker used by the MERGE_ALLOWED demonstration PR.

This module intentionally changes no registered COLLIDER concept and is not
imported by runtime code. Its presence lets the real pull-request Semantic CI
workflow execute a changed-file path while conventional workstream behavior
remains untouched.
"""

PROOF_KIND = "non_semantic_change"
