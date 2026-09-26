const stage = document.querySelector(".stage");
const L = window.ColliderLoop;

let data;

// Two explicit modes. Results are never shared between them.
//   ACTIVE   → local action server; every result is produced now, on click.
//   EVIDENCE → committed receipts only; nothing is executed by the browser.
let mode = "ACTIVE";
let server = null;           // /api/state payload when the action server is up
let busy = false;
let diffTab = "repair";
let guardTimers = [];

const sessions = {
  ACTIVE: { step: 0, decision: null, abstention: null, guard: null, guardPhase: 0 },
  EVIDENCE: { step: 0, decision: null, abstention: null, guard: null, guardPhase: 0 }
};

const labels = [
  "BASELINE",
  "CLASSIFY",
  "DECISION REQUIRED",
  "TARGETED REPAIR",
  "PROOF"
];

const $ = (id) => document.getElementById(id);
const S = () => sessions[mode];

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);

const reducedMotion = () =>
  window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

async function detectServer() {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 4000);
    const res = await fetch("./api/state", { signal: ctrl.signal, cache: "no-store" });
    clearTimeout(timer);
    if (!res.ok) return null;
    const body = await res.json();
    return L.acceptsResult("ACTIVE", body) ? body : null;
  } catch {
    return null;
  }
}

async function boot() {
  const response = await fetch("./evidence.json");
  if (!response.ok) throw new Error("Could not load canonical evidence.");
  data = await response.json();

  if (!L.acceptsResult("EVIDENCE", data.decisionReceipt)) {
    throw new Error("Committed decision receipt is not labelled as EVIDENCE.");
  }

  $("test-count").textContent = data.baseline.testsPassed;
  $("baseline-conflict-count").textContent = data.baseline.conflicts;
  $("canonical-question").textContent = data.classifications.customerIdentity.question;
  $("commit-short").textContent = `evidence ${data.evidenceCommit.slice(0, 8)}`;
  $("fairness-value").textContent =
    data.fairness.starting_workstream_artifacts_byte_identical ? "BYTE-IDENTICAL" : "FAILED";

  render();
  server = await detectServer();
  render();
}

function preGate() {
  if (mode === "EVIDENCE") return data.decisionReceipt.gate_before;
  return server ? server.gate : null;
}

async function post(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const out = await res.json();
  if (!res.ok) throw new Error(out.error || `HTTP ${res.status}`);
  if (!L.acceptsResult("ACTIVE", out)) throw new Error("Result is not ACTIVE-mode provenance.");
  return out;
}

async function decide(choice) {
  const s = sessions.ACTIVE;
  if (mode !== "ACTIVE" || !server || busy || s.decision || s.abstention) return;

  busy = true;
  $("decision-state").textContent =
    choice === "KEEP_UNKNOWN" ? "RECORDING ABSTENTION…" : "COMPILING account_id…";
  render();

  try {
    const result = await post("./api/decide", { choice });
    if (result.kind === "abstention") {
      s.abstention = result;
    } else {
      s.decision = result;
      s.step = 3;
    }
  } catch (error) {
    $("decision-note").textContent = `Action failed: ${error.message}`;
  } finally {
    busy = false;
    render();
  }
}

async function runGuard() {
  const s = sessions.ACTIVE;
  if (mode !== "ACTIVE" || busy || !s.decision || s.guard) return;

  busy = true;
  render();
  try {
    s.guard = await post("./api/guard", { decision_id: s.decision.decision.decision_id });
    revealGuard();
  } catch (error) {
    s.guardError = `Guard probe failed: ${error.message}`;
  } finally {
    busy = false;
    render();
  }
}

// Staged reveal of the real receipt. Every phase's content comes from it.
function revealGuard() {
  const s = sessions.ACTIVE;
  guardTimers.forEach(clearTimeout);
  guardTimers = [];
  if (reducedMotion()) {
    s.guardPhase = 4;
    return;
  }
  s.guardPhase = 1;
  [2, 3, 4].forEach((phase, i) => {
    guardTimers.push(setTimeout(() => {
      s.guardPhase = phase;
      render();
    }, 1300 * (i + 1)));
  });
}

function resetSession() {
  guardTimers.forEach(clearTimeout);
  guardTimers = [];
  sessions[mode] = { step: 0, decision: null, abstention: null, guard: null, guardPhase: 0 };
  diffTab = "repair";
}

function setMode(next) {
  if (next === mode || busy) return;
  mode = next;
  render();
}

// ---------------------------------------------------------------------------

function findingText(f) {
  if (f.kind === "SPEC_GAP") {
    const vals = Object.entries(f.candidates).map(([ws, v]) => `${ws}=${v}`).join(" · ");
    return `<b>SPEC_GAP</b> ${esc(f.concept)} — source silent, UNKNOWN · ${esc(vals)}`;
  }
  if (f.kind === "AGENT_DRIFT") {
    const vals = Object.entries(f.violations).map(([ws, v]) => `${ws}=${v}`).join(" · ");
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

const dl = (rows) =>
  rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("");

const short = (sha) => String(sha || "").slice(0, 12);

// ---------------------------------------------------------------------------

function renderMode() {
  const p = L.provenance(mode);
  document.querySelectorAll(".mode-switch button").forEach((b) => {
    b.setAttribute("aria-checked", String(b.dataset.mode === mode));
    b.disabled = busy;
  });
  document.body.dataset.mode = mode;
  $("truth-badge").textContent = [p.label, ...p.detail].join(" · ");

  const s = S();
  const activeUp = mode === "ACTIVE" && Boolean(server);
  const decided = Boolean(s.decision || s.abstention);

  $("decision-options").classList.toggle("hidden", mode !== "ACTIVE");
  $("evidence-decision").classList.toggle("hidden", mode !== "EVIDENCE");

  if (mode === "ACTIVE") {
    $("action-mode").textContent = server
      ? "LOCAL ACTION SERVER · your choice executes now"
      : "ACTIVE MODE UNAVAILABLE · start python3 demo-ui/server.py, or switch to EVIDENCE MODE";
    document.querySelectorAll(".decision-option").forEach((b) => {
      const chosen =
        (b.dataset.choice === "USE_ACCOUNT_ID" && s.decision) ||
        (b.dataset.choice === "KEEP_UNKNOWN" && s.abstention);
      b.classList.toggle("chosen", Boolean(chosen));
      b.disabled = !activeUp || busy || decided;
    });
  } else {
    const r = data.decisionReceipt;
    $("action-mode").textContent = "EVIDENCE MODE · committed receipt, not executed by this browser";
    $("evidence-decision-value").textContent =
      `${r.decision.concept} = ${r.decision.canonical_value}`;
    $("evidence-decision-note").textContent =
      `${r.receipt_dir} · human decision ${r.decision.human_decision_source}`;
  }
}

function renderDecisionState() {
  const s = S();
  if (busy && mode === "ACTIVE" && !s.decision && !s.abstention) return;
  if (s.abstention) {
    $("decision-state").textContent = "UNKNOWN · KEPT";
    $("decision-note").textContent = s.abstention.message;
  } else if (s.decision) {
    $("decision-state").textContent = `${s.decision.decision.canonical_value} · CANONICAL`;
    $("decision-note").textContent =
      `decision source: human · ${s.decision.decision.human_decision_source} · ${s.decision.decision.decision_id}`;
  } else {
    $("decision-state").textContent = "UNDECIDED · UNKNOWN";
    $("decision-note").textContent = "No canon exists. COLLIDER will not pick for you.";
  }
}

function renderStage() {
  const s = S();
  const decision = s.decision;
  const facts = decision?.gate_after?.facts;

  stage.dataset.step = String(s.step);
  stage.dataset.ready = String(
    Boolean(decision) && decision.manifest.integration_status_after === "INTEGRATION_READY"
  );

  $("step-label").textContent = s.abstention ? "UNKNOWN KEPT" : labels[s.step];
  $("step-counter").textContent = `${s.step + 1} / 5`;
  $("progress-fill").style.width = `${(s.step + 1) * 20}%`;

  $("prev").disabled = s.step === 0 || busy || Boolean(s.abstention);

  const awaitingDecision = s.step === 2 && !decision && !s.abstention;
  const canAdvance =
    mode === "EVIDENCE" || !awaitingDecision;

  $("next").disabled = busy || !canAdvance;
  $("next").textContent =
    s.abstention || s.step === 4
      ? "Reset session ↺"
      : s.step === 0
        ? "Run COLLIDER →"
        : awaitingDecision && mode === "ACTIVE"
          ? "Decide above to continue"
          : "Continue →";

  $("classification-grid").classList.toggle("hidden", s.step < 1);
  $("question-panel").classList.toggle("hidden", s.step < 2);

  const repaired = s.step >= 3 && Boolean(decision);
  const proved = s.step >= 4 && Boolean(decision);
  const changed = (ws) =>
    Boolean(decision?.manifest.workstreams.find((w) => w.workstream === ws && w.changed));

  $("ledger-repair").classList.toggle("hidden", !(repaired && changed("ledger")));
  $("api-repair").classList.toggle("hidden", !(repaired && changed("api")));
  $("api-identity").textContent = repaired ? facts.api_customer_identity_field : "email";
  $("ledger-identity").textContent = repaired ? facts.ledger_customer_identity_field : "account_id";
  $("ledger-field").textContent = repaired ? facts.ledger_money_field : "credit_amount";

  if (proved) {
    const m = decision.manifest;
    $("collision-number").textContent =
      `${m.integration_conflicts_before} → ${m.integration_conflicts_after}`;
    $("collision-title").textContent = "EXECUTABLE INTEGRATION CONFLICTS";
    $("collision-status").textContent =
      `${m.integration_status_after} · GATE ${decision.gate_after.verdict}`;
  } else {
    $("collision-number").textContent = data.baseline.conflicts;
    $("collision-title").textContent = "INTEGRATION CONFLICTS";
    $("collision-status").textContent = s.abstention
      ? `${data.baseline.status} · GATE ${s.abstention.gate_verdict}`
      : data.baseline.status;
  }

  // Section 03 is always the committed comparative receipt.
  if (s.step >= 4) {
    $("final-conflicts").textContent = data.result.conflicts;
    $("final-status").textContent = data.result.status;
    $("receipt-state").textContent = "COMMITTED EVIDENCE · local-resolved-004";
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
}

function renderLoop() {
  const s = S();
  const g0 = preGate();
  const decision = s.decision;
  const abst = s.abstention;
  const guard = s.guard;
  const status = L.loopState({ mode, decision, abstention: abst, guard });

  const text = {};
  const kinds = (g0?.findings || []).map((f) => f.kind).join(" · ");
  text.DETECT = g0 ? `${g0.integration.conflict_count} conflicts · ${kinds}` : "action server offline";
  text.REPLAY = "NOT_EXECUTED · PENDING_LIVE_BOB";

  if (abst) {
    text.DECIDE = "KEEP UNKNOWN · abstained";
    ["COMPILE", "PATCH", "VERIFY", "REMEMBER"].forEach((n) => { text[n] = "skipped · no canon"; });
    text.GUARD = abst.gate_verdict;
  } else if (decision) {
    const m = decision.manifest;
    const mem = decision.memory;
    const v = mem.verification;
    const changedWs = m.workstreams.filter((w) => w.changed).map((w) => w.workstream);
    const kept = m.workstreams.filter((w) => !w.changed).map((w) => w.workstream);
    text.DECIDE = `${decision.decision.canonical_value} · ${decision.decision.human_decision_source}`;
    text.COMPILE = "decision · spec patch · repair · contract";
    text.PATCH = `changed ${changedWs.join(", ") || "none"} · unchanged ${kept.join(", ") || "none"}`;
    text.VERIFY = v.tests_passed === null
      ? `not run · ${m.integration_conflicts_before} → ${m.integration_conflicts_after} conflicts`
      : `${v.tests_passed} passed · ${v.tests_failed} failed · ${m.integration_conflicts_before} → ${m.integration_conflicts_after} conflicts`;
    text.REMEMBER = `memory · ${mem.evidence_state}`;
    text.GUARD = {
      done: `${guard?.guard_verdict} → restored · ${guard?.gate_after_restore}`,
      failed: guard ? `${guard.guard_verdict} · restoration ${guard.restoration_verified}` : "—",
      waiting: "WAITING · probe not run",
      "not-in-evidence": "not in committed evidence",
      idle: "—"
    }[status.GUARD];
  } else {
    text.DECIDE = busy ? "working…" : "awaiting human";
    ["COMPILE", "PATCH", "VERIFY", "REMEMBER"].forEach((n) => { text[n] = "—"; });
    text.GUARD = g0 ? g0.verdict : "—";
  }

  document.querySelectorAll("#loop-strip li").forEach((li) => {
    const n = li.dataset.node;
    li.dataset.status = status[n];
    li.querySelector("span").textContent = text[n];
  });

  $("loop-source").textContent = decision
    ? mode === "ACTIVE"
      ? `LOCAL ACTIVE DEMO · receipts ${decision.receipt_dir}`
      : `COMMITTED EVIDENCE · ${decision.receipt_dir} · not executed in this browser`
    : abst
      ? `LOCAL ACTIVE DEMO · abstention receipt ${abst.receipt_dir}`
      : "NO DECISION YET";

  // Gate panel
  const verdict = decision ? decision.gate_after.verdict : abst ? abst.gate_verdict : g0?.verdict;
  const findings = decision ? decision.gate_after.findings : abst ? abst.gate_findings : g0?.findings;
  $("gate-verdict").dataset.verdict = verdict || "";
  $("gate-verdict-value").textContent = verdict || "—";
  $("gate-verdict-note").textContent = decision
    ? "gate on compiled workspace · python3 -m collider.gate --root <workspace>"
    : "gate on committed tree · python3 -m collider.gate";
  $("gate-findings").innerHTML = findings && findings.length
    ? findings.map((f) => `<li>${findingText(f)}</li>`).join("")
    : verdict ? "<li><b>NO FINDINGS</b> canon resolved · dependents conform</li>" : "";

  // Abstention
  $("abstained").classList.toggle("hidden", !abst);
  if (abst) {
    $("abstained-view").innerHTML = dl([
      ["concept", `${abst.concept} · epistemic state ${abst.epistemic_state}`],
      ["canon written", String(abst.canon_written)],
      ["decision memory written", String(abst.decision_memory_written)],
      ["spec patch written", String(abst.spec_patch_written)],
      ["repairs applied", abst.repairs_applied.length ? abst.repairs_applied.join(", ") : "none"],
      ["gate", `${abst.gate_verdict} · ${abst.integration.conflict_count} conflicts remain`],
      ["source tree untouched", String(abst.source_tree_untouched)],
      ["receipt", `${abst.receipt_dir}/abstention.json · ${abst.receipt_kind}`]
    ]);
  }

  renderGuard(status.GUARD);

  $("compiled").classList.toggle("hidden", !decision);
  if (decision) renderCompiled(decision);
}

function renderGuard(guardStatus) {
  const s = S();
  const decision = s.decision;
  const ready = decision && decision.gate_after.verdict === "SEMANTICALLY_READY";
  const panel = $("guard");
  panel.classList.toggle("hidden", !ready);
  if (!ready) return;

  const mem = decision.memory;
  const g = s.guard;
  const phase = g ? s.guardPhase : 0;
  panel.dataset.phase = String(phase);
  panel.dataset.status = guardStatus;

  const heading = !g || phase === 0
    ? ["SEMANTICALLY READY", "ready"]
    : phase <= 2
      ? ["CANON UNDER TEST", "violation"]
      : phase === 3
        ? ["RESTORING VERIFIED STATE…", "restoring"]
        : g.restoration_verified && g.gate_after_restore === "SEMANTICALLY_READY"
          ? ["SEMANTICALLY READY", "ready"]
          : [g.gate_after_restore, "violation"];
  $("guard-ready").textContent = heading[0];
  $("guard-ready").dataset.tone = heading[1];

  $("guard-memory").textContent = s.guardError ||
    `Decision Memory: ${mem.concept} = ${mem.canonical_value} · canon/decision-memory.json`;

  const btn = $("guard-run");
  if (mode === "EVIDENCE") {
    btn.disabled = true;
    btn.textContent = "GUARD PROBE · ACTIVE MODE ONLY";
  } else {
    btn.disabled = busy || Boolean(g);
    btn.textContent = busy && !g
      ? "RUNNING PROBE IN WORKSPACE…"
      : g ? "PROBE EXECUTED" : "TEST A FUTURE AGENT CHANGE";
  }

  document.querySelectorAll("#guard-phases li").forEach((li, i) => {
    li.classList.toggle("shown", phase >= i + 1);
  });
  if (!g) return;

  const sourceLines = g.probe_diff.split("\n")
    .filter((l) => /^[-+][A-Z_]/.test(l))
    .join("\n");
  $("guard-attempt").innerHTML = renderDiff(
    `- ${g.concept} = ${g.canonical_value}\n+ ${g.concept} = ${g.attempted_value}\n\n${sourceLines}`
  );
  $("guard-attempt-file").textContent =
    `${g.affected_file} · sha ${short(g.sha_before_probe)} → ${short(g.sha_during_probe)}`;

  const c = g.verification_during_probe.regression_contract;
  const blocked = g.guard_verdict === "MERGE_BLOCKED";
  $("guard-verdict").textContent = blocked ? "MERGE BLOCKED" : g.guard_verdict;
  $("guard-rule").textContent = `${g.concept} must remain ${g.decision_memory_value}`;
  $("guard-blocked-view").innerHTML = dl([
    ["gate during probe", g.gate_during_probe],
    ["finding", g.violation ? `${g.violation.kind} · ${g.violation.authority}` : "none"],
    ["attempted", g.attempted_value],
    ["canonical", g.canonical_value],
    ["regression contract", `${c.passed_count} passed · ${c.failed_count} failed`],
    ["integration", `${g.integration_during_probe.conflict_count} conflict · ${g.integration_during_probe.status}`]
  ]);

  $("guard-restoring").textContent = phase >= 4 ? "RESTORED VERIFIED STATE" : "RESTORING VERIFIED STATE…";
  $("guard-restore-view").innerHTML = dl([
    ["restoration applied", String(g.restoration_applied)],
    ["sha before probe", short(g.sha_before_probe)],
    ["sha after restore", short(g.sha_after_restore)],
    ["exact bytes restored", String(g.restored_exact_bytes)]
  ]);

  const ca = g.verification_after_restore.regression_contract;
  $("guard-final-1").textContent = g.restoration_verified
    ? "✓ WORKSPACE RESTORED" : "✗ RESTORATION NOT VERIFIED";
  $("guard-final-2").textContent = g.gate_after_restore === "SEMANTICALLY_READY"
    ? "✓ SEMANTICALLY READY" : `✗ ${g.gate_after_restore}`;
  $("guard-receipt").textContent =
    `${g.integration_after_restore.conflict_count} conflicts · contract ${ca.passed_count} passed · ` +
    `${ca.failed_count} failed · receipt ${g.receipt_path}`;
}

function renderCompiled(decision) {
  const m = decision.manifest;
  const mem = decision.memory;

  $("artifact-list").innerHTML = dl([
    ["canon decision", mem.decision_ref],
    ["spec patch", `${mem.spec_ref} + ${mem.spec_patch_ref}`],
    ["code repair", m.workstreams.filter((w) => w.changed).map((w) => w.path).join(", ") || "none"],
    ["regression contract", mem.regression_artifact_ref],
    ["decision memory", "canon/decision-memory.json"],
    ["receipts", decision.receipt_dir]
  ]);

  const diffs = { repair: decision.repair_patch, spec: decision.spec_diff, contract: decision.contract };
  $("diff-view").innerHTML = diffTab === "contract" ? esc(diffs.contract) : renderDiff(diffs[diffTab]);
  document.querySelectorAll(".diff-tabs button").forEach((b) => {
    b.classList.toggle("active", b.dataset.diff === diffTab);
  });

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

  $("memory-view").innerHTML = dl([
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
  ]);

  const r = decision.replay;
  $("replay-status").textContent = r.status;
  $("replay-runtime").textContent = r.runtime_state;
  $("replay-reason").textContent = r.reason;
  $("replay-contract").innerHTML =
    `<span>GIVEN</span><code>${esc(r.inputs.patched_spec)} · ${esc(r.inputs.decision_memory)}</code>` +
    `<span>WITHHELD</span><code>${esc(r.inputs.withheld.join(" · "))}</code>` +
    `<span>ACCEPTS ONLY</span><code>${esc(r.acceptance.execution_source_in.join(", "))}</code>` +
    `<span>NOT THE GUARD</span><code>the guard probe is a local change against canon, not an independent agent</code>`;
}

function render() {
  if (!data) return;
  renderMode();
  renderDecisionState();
  renderStage();
  renderLoop();
}

// ---------------------------------------------------------------------------

$("next").addEventListener("click", () => {
  const s = S();
  if (s.abstention || s.step === 4) {
    resetSession();
  } else {
    s.step += 1;
    // Evidence mode shows the committed decision receipt; nothing is clicked.
    if (mode === "EVIDENCE" && s.step === 3) s.decision = data.decisionReceipt;
  }
  render();
});

$("prev").addEventListener("click", () => {
  const s = S();
  s.step = Math.max(0, s.step - 1);
  render();
});

document.querySelectorAll(".decision-option").forEach((b) => {
  b.addEventListener("click", () => decide(b.dataset.choice));
});

document.querySelectorAll(".mode-switch button").forEach((b) => {
  b.addEventListener("click", () => setMode(b.dataset.mode));
});

$("guard-run").addEventListener("click", runGuard);

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
