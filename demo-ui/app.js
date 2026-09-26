const stage = document.querySelector(".stage");

let data;
let step = 0;

// Action state.
// mode LIVE    → local action server reachable; decisions really compile.
// mode RECEIPT → static hosting; the committed decision-001 receipt is shown,
//                labelled as such. Nothing is executed in the browser.
let mode = "RECEIPT";
let preGate = null;
let action = null;
let actionLabel = "";
let busy = false;
let diffTab = "repair";

const labels = [
  "BASELINE",
  "CLASSIFY",
  "DECISION REQUIRED",
  "TARGETED REPAIR",
  "PROOF"
];

const $ = (id) => document.getElementById(id);

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);

async function detectServer() {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 2500);
    const res = await fetch("./api/state", { signal: ctrl.signal, cache: "no-store" });
    clearTimeout(timer);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

async function boot() {
  const response = await fetch("./evidence.json");

  if (!response.ok) {
    throw new Error("Could not load canonical evidence.");
  }

  data = await response.json();

  $("test-count").textContent = data.baseline.testsPassed;
  $("baseline-conflict-count").textContent = data.baseline.conflicts;

  $("canonical-question").textContent =
    data.classifications.customerIdentity.question;

  $("commit-short").textContent =
    `evidence ${data.evidenceCommit.slice(0, 8)}`;

  $("fairness-value").textContent =
    data.fairness.starting_workstream_artifacts_byte_identical
      ? "BYTE-IDENTICAL"
      : "FAILED";

  const live = await detectServer();

  if (live) {
    mode = "LIVE";
    preGate = live.gate;
    $("action-mode").textContent =
      "LOCAL ACTION SERVER · choosing compiles for real (INTERACTIVE_LOCAL_UI)";
  } else {
    mode = "RECEIPT";
    preGate = data.decisionReceipt.gate_before;
    $("action-mode").textContent =
      "STATIC MODE · shows committed receipt decision-001 (PRESEEDED). " +
      "Run python3 demo-ui/server.py to execute.";
  }

  render();
}

async function decide(value) {
  if (busy || action) return;

  if (mode === "RECEIPT") {
    action = data.decisionReceipt;
    actionLabel =
      `COMMITTED RECEIPT · ${action.receipt_dir} · not executed in this browser`;
    step = 3;
    render();
    return;
  }

  busy = true;
  $("decision-state").textContent = `COMPILING ${value}…`;
  render();

  try {
    const res = await fetch("./api/decide", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ concept: "customer_identity", value })
    });
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || `HTTP ${res.status}`);
    action = body;
    actionLabel = `LIVE LOCAL ACTION · receipts ${body.receipt_dir}`;
    step = 3;
  } catch (error) {
    $("decision-note").textContent = `Compile failed: ${error.message}`;
  } finally {
    busy = false;
    render();
  }
}

function gateNow() {
  return action ? action.gate_after : preGate;
}

function findingText(f) {
  if (f.kind === "SPEC_GAP") {
    const vals = Object.entries(f.candidates)
      .map(([ws, v]) => `${ws}=${v}`).join(" · ");
    return `<b>SPEC_GAP</b> ${esc(f.concept)} — source silent, UNKNOWN · ${esc(vals)}`;
  }
  if (f.kind === "AGENT_DRIFT") {
    const vals = Object.entries(f.violations)
      .map(([ws, v]) => `${ws}=${v}`).join(" · ");
    const authority = f.authority === "RESOLVED_CANON" ? "resolved canon" : "explicit source";
    return `<b>AGENT_DRIFT</b> ${esc(f.concept)} — violates ${authority} ` +
      `<code>${esc(f.expected)}</code> · ${esc(vals)}`;
  }
  return `<b>${esc(f.kind)}</b> ${esc(f.concept)} — ${esc(f.note || "")}`;
}

function renderDiff(text) {
  return String(text || "(no changes)")
    .split("\n")
    .map((line) => {
      const cls =
        line.startsWith("+++") || line.startsWith("---") ? "meta"
          : line.startsWith("@@") ? "hunk"
            : line.startsWith("+") ? "add"
              : line.startsWith("-") ? "del" : "";
      return `<span class="${cls}">${esc(line)}</span>`;
    })
    .join("\n");
}

function renderLoop() {
  const g = gateNow();
  const out = (node, text) => {
    document.querySelector(`[data-out="${node}"]`).textContent = text;
  };

  const kinds = (preGate?.findings || []).map((f) => f.kind).join(" · ");
  out("DETECT", preGate
    ? `${preGate.integration.conflict_count} conflicts · ${kinds}`
    : "—");

  const done = new Set(["DETECT"]);
  const m = action?.manifest;
  const mem = action?.memory;

  if (action) {
    ["DECIDE", "COMPILE", "PATCH", "VERIFY", "REMEMBER", "GUARD"].forEach((n) => done.add(n));
    out("DECIDE", `${action.decision.canonical_value} · ${action.decision.human_decision_source}`);
    out("COMPILE", "decision · spec patch · repair · contract");
    const changed = m.workstreams.filter((w) => w.changed).map((w) => w.workstream);
    const kept = m.workstreams.filter((w) => !w.changed).map((w) => w.workstream);
    out("PATCH", `changed ${changed.join(", ") || "none"} · unchanged ${kept.join(", ") || "none"}`);
    const v = mem.verification;
    out("VERIFY", v.tests_passed === null
      ? `not run · ${m.integration_conflicts_before} → ${m.integration_conflicts_after} conflicts`
      : `${v.tests_passed} passed · ${v.tests_failed} failed · ${m.integration_conflicts_before} → ${m.integration_conflicts_after} conflicts`);
    out("REMEMBER", `memory · ${mem.evidence_state}`);
    out("GUARD", g.verdict);
    out("REPLAY", `${mem.replay.status} · ${mem.replay.runtime_state}`);
  } else {
    out("DECIDE", busy ? "compiling…" : "awaiting human");
    ["COMPILE", "PATCH", "VERIFY", "REMEMBER"].forEach((n) => out(n, "—"));
    out("GUARD", g ? g.verdict : "—");
    out("REPLAY", "NOT_EXECUTED · PENDING_LIVE_BOB");
  }

  document.querySelectorAll("#loop-strip li").forEach((li) => {
    const n = li.dataset.node;
    li.classList.toggle("done", done.has(n));
    li.classList.toggle("active", !action && n === "DECIDE" && step >= 2);
  });

  $("loop-source").textContent = action ? actionLabel : "NO DECISION YET";

  // Gate
  $("gate-verdict").dataset.verdict = g ? g.verdict : "";
  $("gate-verdict-value").textContent = g ? g.verdict : "—";
  $("gate-verdict-note").textContent = action
    ? "gate on compiled tree · python3 -m collider.gate --root <workspace>"
    : "gate on committed tree · python3 -m collider.gate";
  $("gate-findings").innerHTML = g && g.findings.length
    ? g.findings.map((f) => `<li>${findingText(f)}</li>`).join("")
    : g ? "<li><b>NO FINDINGS</b> canon resolved · dependents conform</li>" : "";

  $("compiled").classList.toggle("hidden", !action);
  if (!action) return;

  // Artifacts
  const rows = [
    ["canon decision", mem.decision_ref],
    ["spec patch", `${mem.spec_ref} + ${mem.spec_patch_ref}`],
    ["code repair", m.workstreams.filter((w) => w.changed).map((w) => w.path).join(", ") || "none"],
    ["regression contract", mem.regression_artifact_ref],
    ["decision memory", "canon/decision-memory.json"],
    ["receipts", action.receipt_dir]
  ];
  $("artifact-list").innerHTML = rows
    .map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("");

  const diffs = {
    repair: action.repair_patch,
    spec: action.spec_diff,
    contract: action.contract
  };
  $("diff-view").innerHTML = diffTab === "contract"
    ? esc(diffs.contract)
    : renderDiff(diffs[diffTab]);
  document.querySelectorAll(".diff-tabs button").forEach((b) => {
    b.classList.toggle("active", b.dataset.diff === diffTab);
  });

  // Verify
  const v = mem.verification;
  $("verify-counts").textContent = v.tests_passed === null
    ? "NOT RUN — structural gate failed first"
    : `${v.tests_passed} passed · ${v.tests_failed} failed`;
  $("verify-command").textContent = v.command || "";
  $("verify-box").dataset.ok = String(v.tests_passed !== null && v.tests_failed === 0);
  $("integration-counts").textContent =
    `${m.integration_conflicts_before} → ${m.integration_conflicts_after} conflicts`;
  $("integration-status").textContent = m.integration_status_after;
  $("integration-box").dataset.ok = String(m.integration_status_after === "INTEGRATION_READY");
  $("ws-state").innerHTML = m.workstreams.map((w) =>
    `<li data-changed="${w.changed}"><b>${esc(w.workstream)}</b>` +
    `<span>${w.changed ? "CHANGED" : "UNCHANGED"} · ${esc(w.role)}</span>` +
    `<code>${esc(w.sha256_before.slice(0, 8))} → ${esc(w.sha256_after.slice(0, 8))}</code></li>`
  ).join("");

  // Memory
  const memRows = [
    ["concept", mem.concept],
    ["canonical value", mem.canonical_value],
    ["decision source", `${mem.decision_source} · ${mem.human_decision_source}`],
    ["affected dependents", mem.affected_dependents.join(", ")],
    ["unaffected", mem.unaffected_workstreams.join(", ") || "none"],
    ["spec patch ref", mem.spec_patch_ref],
    ["regression ref", mem.regression_artifact_ref],
    ["evidence state", mem.evidence_state],
    ["provenance",
      `${mem.provenance.execution_environment} · interpretations ${mem.provenance.interpretation_source} · input ${mem.provenance.input_commit.slice(0, 8)}`]
  ];
  $("memory-view").innerHTML = memRows
    .map(([k, val]) => `<dt>${esc(k)}</dt><dd>${esc(val)}</dd>`).join("");

  // Replay
  const r = action.replay;
  $("replay-status").textContent = r.status;
  $("replay-runtime").textContent = r.runtime_state;
  $("replay-reason").textContent = r.reason;
  $("replay-contract").innerHTML =
    `<span>GIVEN</span><code>${esc(r.inputs.patched_spec)} · ${esc(r.inputs.decision_memory)}</code>` +
    `<span>WITHHELD</span><code>${esc(r.inputs.withheld.join(" · "))}</code>` +
    `<span>ACCEPTS ONLY</span><code>${esc(r.acceptance.execution_source_in.join(", "))}</code>`;
}

function render() {
  stage.dataset.step = String(step);

  const facts = action?.gate_after?.facts;
  const ready = action
    ? action.manifest.integration_status_after === "INTEGRATION_READY"
    : false;
  stage.dataset.ready = String(ready);

  $("step-label").textContent = labels[step];
  $("step-counter").textContent = `${step + 1} / 5`;
  $("progress-fill").style.width = `${(step + 1) * 20}%`;

  $("prev").disabled = step === 0 || busy;

  const awaitingDecision = step === 2 && !action;
  $("next").disabled = awaitingDecision || busy;

  $("next").textContent =
    step === 4
      ? "Reset ↺"
      : step === 0
        ? "Run COLLIDER →"
        : awaitingDecision
          ? "Decide above to continue"
          : "Continue →";

  const classified = step >= 1;
  const questioned = step >= 2;
  const repaired = step >= 3 && Boolean(action);
  const proved = step >= 4 && Boolean(action);

  $("classification-grid").classList.toggle("hidden", !classified);
  $("question-panel").classList.toggle("hidden", !questioned);

  document.querySelectorAll(".decision-option").forEach((b) => {
    b.classList.toggle("chosen", action?.decision.canonical_value === b.dataset.value);
    // Static mode can only show the committed account_id receipt.
    b.disabled = busy || Boolean(action) ||
      (mode === "RECEIPT" && b.dataset.value !== "account_id");
  });

  if (action) {
    $("decision-state").textContent =
      `${action.decision.canonical_value} · CANONICAL`;
    $("decision-note").textContent =
      `decision source: human · ${action.decision.human_decision_source} · ${action.decision.decision_id}`;
  } else if (!busy) {
    $("decision-state").textContent = "UNDECIDED · UNKNOWN";
    $("decision-note").textContent =
      "No canon exists. COLLIDER will not pick for you.";
  }

  const changed = (ws) =>
    Boolean(action?.manifest.workstreams.find((w) => w.workstream === ws && w.changed));

  $("ledger-repair").classList.toggle("hidden", !(repaired && changed("ledger")));
  $("api-repair").classList.toggle("hidden", !(repaired && changed("api")));

  $("api-identity").textContent =
    repaired ? facts.api_customer_identity_field : "email";
  $("ledger-identity").textContent =
    repaired ? facts.ledger_customer_identity_field : "account_id";
  $("ledger-field").textContent =
    repaired ? facts.ledger_money_field : "credit_amount";

  if (proved) {
    const m = action.manifest;
    $("collision-number").textContent =
      `${m.integration_conflicts_before} → ${m.integration_conflicts_after}`;
    $("collision-title").textContent = "EXECUTABLE INTEGRATION CONFLICTS";
    $("collision-status").textContent =
      `${m.integration_status_after} · GATE ${action.gate_after.verdict}`;
  } else {
    $("collision-number").textContent = data.baseline.conflicts;
    $("collision-title").textContent = "INTEGRATION CONFLICTS";
    $("collision-status").textContent = data.baseline.status;
  }

  // Section 03 stays bound to the canonical comparative receipt.
  if (step >= 4) {
    $("final-conflicts").textContent = data.result.conflicts;
    $("final-status").textContent = data.result.status;
    $("receipt-state").textContent = "OBSERVED / COMMITTED · local-resolved-004";
    $("api-hash-state").textContent =
      data.hashes.api.restored_to_input ? "CHANGED + RESTORED" : "CHECK FAILED";
    $("ledger-hash-state").textContent =
      data.hashes.ledger.restored_to_input ? "CHANGED + RESTORED" : "CHECK FAILED";
    $("notification-hash-state").textContent =
      data.hashes.notifications.changed ? "UNEXPECTED CHANGE" : "UNCHANGED";
  } else {
    $("final-conflicts").textContent = "—";
    $("final-status").textContent = "waiting";
    $("receipt-state").textContent = "WAITING FOR CANONICAL PROOF";
    $("api-hash-state").textContent = "—";
    $("ledger-hash-state").textContent = "—";
    $("notification-hash-state").textContent = "—";
  }

  renderLoop();
}

$("next").addEventListener("click", () => {
  if (step === 4) {
    step = 0;
    action = null;
    diffTab = "repair";
  } else {
    step += 1;
  }
  render();
});

$("prev").addEventListener("click", () => {
  step = Math.max(0, step - 1);
  render();
});

document.querySelectorAll(".decision-option").forEach((b) => {
  b.addEventListener("click", () => decide(b.dataset.value));
});

document.querySelectorAll(".diff-tabs button").forEach((b) => {
  b.addEventListener("click", () => {
    diffTab = b.dataset.diff;
    render();
  });
});

boot().catch((error) => {
  console.error(error);

  document.body.innerHTML = `
    <main style="padding:40px;font-family:system-ui">
      <h1>Evidence failed to load.</h1>
      <p>${esc(error.message)}</p>
    </main>
  `;
});
