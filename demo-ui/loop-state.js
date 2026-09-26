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

  // Rail order of the nodes the compile reveal walks through, and how many
  // compile checklist items must be displayed before each node is shown done.
  const COMPILE_NODES = ["DECIDE", "COMPILE", "PATCH", "VERIFY", "REMEMBER"];
  const COMPILE_REQUIRES = { DECIDE: 1, COMPILE: 1, PATCH: 4, REMEMBER: 6, VERIFY: 7 };
  const COMPILE_ITEMS = 7;

  // Display phase of the guard probe, synchronized with what the UI shows:
  //   0 = request in flight / not yet revealed, 1 = ATTEMPT, 2 = VIOLATION,
  //   3 = RESTORING, 4 = RESTORED. The receipt is never altered; the rail only
  //   waits until the corresponding phase is actually on screen.
  function guardStatus(guard, guardPhase, guardRunning) {
    if (!guard) return guardRunning ? "running" : null;
    const phase = guardPhase === undefined ? 4 : guardPhase;
    if (phase <= 0) return "running";
    if (phase <= 2) return "violation";
    if (phase === 3) return "restoring";
    return guardCompleted(guard) ? "done" : "failed";
  }

  // state: { mode, decision, abstention, guard,
  //          compileRevealed?, guardPhase?, guardRunning? }
  // The optional display parameters default to "fully revealed".
  // returns { NODE: status } with status in
  //   done | waiting | running | violation | restoring | idle | skipped |
  //   abstained | failed | not-in-evidence | pending
  function loopState(state) {
    const { mode, decision, abstention, guard, compileRevealed, guardPhase, guardRunning } = state;
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
    const shown = compileRevealed === undefined ? COMPILE_ITEMS : compileRevealed;

    COMPILE_NODES.forEach((n) => {
      if (shown >= COMPILE_REQUIRES[n]) s[n] = n === "VERIFY" && !ready ? "failed" : "done";
    });
    if (shown < COMPILE_ITEMS) {
      const next = COMPILE_NODES.find((n) => s[n] === "idle");
      if (next) s[next] = "running";
      s.GUARD = "idle";
      return s;
    }

    const g = guardStatus(guard, guardPhase, guardRunning);
    if (g) s.GUARD = g;
    else if (mode === "EVIDENCE") s.GUARD = "not-in-evidence";
    else s.GUARD = ready ? "waiting" : "idle";
    return s;
  }

  return {
    NODES, PROVENANCE, COMPILE_ITEMS, provenance, acceptsResult, guardCompleted, loopState
  };
});
