// COLLIDER loop state + provenance labels.
//
// Pure functions shared by the UI (window.ColliderLoop) and the test suite
// (node, module.exports). The UI never decides a node is complete on its own:
// a node is "done" only when the receipt for that step exists.

(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ColliderLoop = api;
})(typeof self !== "undefined" ? self : this, function () {
  const NODES = [
    "DETECT", "DECIDE", "COMPILE", "PATCH", "VERIFY", "REMEMBER", "GUARD", "REPLAY"
  ];

  const PROVENANCE = Object.freeze({
    ACTIVE: Object.freeze({
      mode: "ACTIVE",
      title: "ACTIVE MODE",
      label: "LOCAL ACTIVE DEMO",
      detail: Object.freeze(["PRESEEDED INTERPRETATIONS", "INTERACTIVE HUMAN DECISION"])
    }),
    EVIDENCE: Object.freeze({
      mode: "EVIDENCE",
      title: "EVIDENCE MODE",
      label: "COMMITTED EVIDENCE",
      detail: Object.freeze(["LOCAL / PRESEEDED"])
    })
  });

  function provenance(mode) {
    const p = PROVENANCE[mode];
    if (!p) throw new Error(`unknown provenance mode: ${mode}`);
    return p;
  }

  // A result may only be rendered in the mode that produced it.
  function acceptsResult(mode, result) {
    return Boolean(result) && result.provenance_mode === mode;
  }

  function guardCompleted(guard) {
    return Boolean(guard) &&
      guard.guard_verdict === "MERGE_BLOCKED" &&
      guard.restoration_verified === true &&
      guard.gate_after_restore === "SEMANTICALLY_READY";
  }

  // state: { mode, decision, abstention, guard }
  // returns { NODE: status } with status in
  //   done | waiting | idle | skipped | abstained | failed |
  //   not-in-evidence | pending
  function loopState(state) {
    const { mode, decision, abstention, guard } = state;
    const s = Object.fromEntries(NODES.map((n) => [n, "idle"]));
    s.DETECT = "done";
    s.REPLAY = "pending"; // NOT_EXECUTED / PENDING_LIVE_BOB, always

    if (abstention) {
      s.DECIDE = "abstained";
      ["COMPILE", "PATCH", "VERIFY", "REMEMBER"].forEach((n) => { s[n] = "skipped"; });
      s.GUARD = "idle";
      return s;
    }

    if (!decision) {
      s.DECIDE = "waiting";
      return s;
    }

    const ready = decision.gate_after && decision.gate_after.verdict === "SEMANTICALLY_READY";
    ["DECIDE", "COMPILE", "PATCH", "REMEMBER"].forEach((n) => { s[n] = "done"; });
    s.VERIFY = ready ? "done" : "failed";

    if (guard) s.GUARD = guardCompleted(guard) ? "done" : "failed";
    else if (mode === "EVIDENCE") s.GUARD = "not-in-evidence";
    else s.GUARD = ready ? "waiting" : "idle";
    return s;
  }

  return { NODES, PROVENANCE, provenance, acceptsResult, guardCompleted, loopState };
});
