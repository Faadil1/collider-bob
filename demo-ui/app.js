// COLLIDER demo UI: ACTIVE MODE product workspace and EVIDENCE MODE explorer.
//
// Every value shown in ACTIVE MODE comes from a response of the local action
// server (same-origin, relative URLs). Every value in EVIDENCE MODE comes from
// committed receipts via evidence.json. Nothing is hard-coded as a result.

const L = window.ColliderLoop;
const $ = (id) => document.getElementById(id);

const API = {
  state: "./api/state",
  decide: "./api/decide",
  guard: "./api/guard"
};

// The fixed future-agent changes the guard can apply (ids match
// collider/guard_probe.py PROBES). Order: block, allow, discover.
const FUTURE_CHANGES = [
  { id: "IDENTITY_REVERT", title: "Revert API identity to email", file: "api/handlers/recover.py" },
  { id: "COMPATIBLE_CHANGE", title: "Reword the customer notice", file: "notifications/send_credit_notice.py" },
  { id: "MONEY_UNIT_DRIFT", title: "Store Ledger amounts in dollars", file: "ledger/credit_entry.py" }
];

const VERDICT_TEXT = {
  MERGE_BLOCKED: "MERGE BLOCKED",
  MERGE_ALLOWED: "MERGE ALLOWED",
  DECISION_REQUIRED: "DECISION REQUIRED"
};
const verdictText = (v) => VERDICT_TEXT[v] || v;

const COMPILE_STEP_MS = 230;
const GUARD_PHASE_MS = 1400;

let data = null;        // evidence.json (committed)
let server = null;      // /api/state payload (ACTIVE provenance) or null
let serverChecked = false;
let mode = "ACTIVE";
let drawerOpen = false;
let proofTab = "Code diff";
let evidenceTab = "Baseline";
let timers = [];

let active = freshSession();

function freshSession() {
  return {
    screen: "detect",       // detect | decide | abstained | compile | guard
    busy: false,
    error: "",
    decision: null,
    abstention: null,
    compileRevealed: 0,
    guards: {},             // probe id → guard receipt
    guardProbe: null,       // probe id currently shown
    guard: null,            // receipt currently shown
    guardRunning: false,
    guardPhase: 0
  };
}

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[c]);

const short = (sha, n = 12) => String(sha || "").slice(0, n);
const json = (obj) => esc(JSON.stringify(obj, null, 2));
const reducedMotion = () =>
  Boolean(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

function clearTimers() {
  timers.forEach(clearTimeout);
  timers = [];
}

function later(ms, fn) {
  timers.push(setTimeout(fn, ms));
}

// ---------------------------------------------------------------------------
// Network (relative, same-origin)
// ---------------------------------------------------------------------------

async function detectServer() {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 4000);
    const res = await fetch(API.state, { signal: ctrl.signal, cache: "no-store" });
    clearTimeout(timer);
    if (!res.ok) return null;
    const body = await res.json();
    if (!L.acceptsResult("ACTIVE", body)) return null;
    // Set only by the deployed Cloudflare Worker (absent on the local server).
    body.worker_version = res.headers.get("x-collider-worker-version");
    return body;
  } catch {
    return null;
  }
}

async function post(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  const out = await res.json();
  if (!res.ok) throw new Error(out.error || `HTTP ${res.status}`);
  if (!L.acceptsResult("ACTIVE", out)) throw new Error("Result is not ACTIVE-mode provenance.");
  return out;
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

function runCollider() {
  if (!server) return;
  active.screen = "decide";
  render();
}

async function decide(choice) {
  if (mode !== "ACTIVE" || !server || active.busy || active.decision || active.abstention) return;
  active.busy = true;
  active.error = "";
  if (choice === "USE_ACCOUNT_ID") {
    active.screen = "compile";
    active.compileRevealed = 0;
  }
  render();

  try {
    const result = await post(API.decide, { choice });
    if (result.kind === "abstention") {
      active.abstention = result;
      active.screen = "abstained";
    } else {
      active.decision = result;
      revealCompile();
    }
  } catch (error) {
    active.error = `Action failed: ${error.message}`;
    active.screen = "decide";
  } finally {
    active.busy = false;
    render();
  }
}

function revealCompile() {
  const total = L.COMPILE_ITEMS;
  if (reducedMotion()) {
    active.compileRevealed = total;
    return;
  }
  active.compileRevealed = 0;
  for (let i = 1; i <= total; i += 1) {
    later(COMPILE_STEP_MS * i, () => {
      active.compileRevealed = i;
      render();
    });
  }
}

function nextUntestedChange() {
  return FUTURE_CHANGES.find((c) => !active.guards[c.id]) || null;
}

async function runGuard(probeId) {
  const d = active.decision;
  if (mode !== "ACTIVE" || active.busy || !d || !compileComplete()) return;
  if (d.gate_after.verdict !== "SEMANTICALLY_READY") return;
  if (!FUTURE_CHANGES.some((c) => c.id === probeId)) return;

  clearTimers();
  active.screen = "guard";
  active.guardProbe = probeId;
  active.error = "";

  // Already judged in this session: show the recorded receipt again.
  if (active.guards[probeId]) {
    active.guard = active.guards[probeId];
    active.guardRunning = false;
    active.guardPhase = 4;
    render();
    return;
  }

  active.busy = true;
  active.guard = null;
  active.guardRunning = true;
  active.guardPhase = 0;
  render();

  try {
    const receipt = await post(API.guard, { decision_id: d.decision.decision_id, probe: probeId });
    active.guards[probeId] = receipt;
    active.guard = receipt;
    active.guardRunning = false;
    revealGuard();
  } catch (error) {
    active.guardRunning = false;
    active.error = `Guard probe failed: ${error.message}`;
  } finally {
    active.busy = false;
    render();
  }
}

// Staged reveal of the real receipt; the rail follows the displayed phase.
function revealGuard() {
  if (reducedMotion()) {
    active.guardPhase = 4;
    return;
  }
  active.guardPhase = 1;
  [2, 3, 4].forEach((phase, i) => {
    later(GUARD_PHASE_MS * (i + 1), () => {
      active.guardPhase = phase;
      render();
    });
  });
}

function resetSession() {
  clearTimers();
  active = freshSession();
  drawerOpen = false;
  proofTab = "Code diff";
  render();
}

function setMode(next) {
  if (next === mode || active.busy) return;
  mode = next;
  drawerOpen = false;
  render();
}

const compileComplete = () =>
  Boolean(active.decision) && active.compileRevealed >= L.COMPILE_ITEMS;

// ---------------------------------------------------------------------------
// Shared rendering helpers
// ---------------------------------------------------------------------------

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
  rows.map(([k, v, cls]) => `<dt>${esc(k)}</dt><dd class="${cls || ""}">${esc(v)}</dd>`).join("");

const section = (title, body) =>
  `<section class="proof-section"><h3>${esc(title)}</h3>${body}</section>`;

const pre = (content, cls = "") => `<pre class="code ${cls}">${content}</pre>`;

function findingRows(findings) {
  if (!findings || !findings.length) return "<p class=\"muted\">No findings.</p>";
  return `<ul class="findings">${findings.map((f) => {
    if (f.kind === "SPEC_GAP") {
      const v = Object.entries(f.candidates).map(([ws, x]) => `${ws}=${x}`).join(", ");
      return `<li><b>SPEC_GAP</b> ${esc(f.concept)}: source silent, UNKNOWN (${esc(v)})</li>`;
    }
    if (f.kind === "AGENT_DRIFT") {
      const v = Object.entries(f.violations).map(([ws, x]) => `${ws}=${x}`).join(", ");
      return `<li><b>AGENT_DRIFT</b> ${esc(f.concept)}: ${esc(f.authority)} expects <code>${esc(f.expected)}</code> (${esc(v)})</li>`;
    }
    return `<li><b>${esc(f.kind)}</b> ${esc(f.concept)}: ${esc(f.note || "")}</li>`;
  }).join("")}</ul>`;
}

// ---------------------------------------------------------------------------
// Top bar + mode
// ---------------------------------------------------------------------------

// Truth label for ACTIVE MODE comes from the action server that actually
// answered (LOCAL or CLOUDFLARE_CONTAINER); nothing is claimed before that.
function activeProvenance() {
  return L.provenance("ACTIVE", server ? server.execution_environment : undefined);
}

function activeLabel() {
  return activeProvenance().label;
}

function renderChrome() {
  document.body.dataset.mode = mode;
  document.body.dataset.screen = active.screen;
  if (mode === "ACTIVE" && !server) {
    $("truth-badge").textContent = serverChecked ? "Active mode unavailable" : "Connecting…";
  } else {
    const p = mode === "ACTIVE" ? activeProvenance() : L.provenance("EVIDENCE");
    $("truth-badge").innerHTML =
      `<b>${esc(p.label)}</b>` + p.detail.map((x) => `<span>${esc(x)}</span>`).join("");
  }

  document.querySelectorAll(".mode-switch button").forEach((b) => {
    b.setAttribute("aria-checked", String(b.dataset.mode === mode));
    b.disabled = active.busy;
  });

  $("workspace").classList.toggle("hidden", mode !== "ACTIVE");
  $("explorer").classList.toggle("hidden", mode !== "EVIDENCE");
  $("mobile-progress").classList.toggle("hidden", mode !== "ACTIVE");

  const toggle = $("proof-toggle");
  toggle.classList.toggle("hidden", mode !== "ACTIVE");
  toggle.setAttribute("aria-expanded", String(drawerOpen));
  toggle.classList.toggle("open", drawerOpen);

  $("drawer").classList.toggle("open", drawerOpen && mode === "ACTIVE");
  $("drawer").setAttribute("aria-hidden", String(!(drawerOpen && mode === "ACTIVE")));
}

// ---------------------------------------------------------------------------
// ACTIVE — rail + mobile progress
// ---------------------------------------------------------------------------

const SCREEN_NODE = {
  detect: "DETECT", decide: "DECIDE", abstained: "DECIDE", guard: "GUARD"
};

function loopStatus() {
  return L.loopState({
    mode: "ACTIVE",
    decision: active.decision,
    abstention: active.abstention,
    guard: active.guard,
    compileRevealed: active.decision ? active.compileRevealed : undefined,
    guardPhase: active.guard ? active.guardPhase : undefined,
    guardRunning: active.guardRunning
  });
}

function currentNode(status) {
  if (SCREEN_NODE[active.screen]) return SCREEN_NODE[active.screen];
  // compile screen: the node being revealed, else GUARD once everything is done
  const running = ["DECIDE", "COMPILE", "PATCH", "VERIFY", "REMEMBER"]
    .find((n) => status[n] === "running" || status[n] === "idle");
  return running || "GUARD";
}

const NODE_TEXT = {
  done: "✓", waiting: "waiting", running: "running", violation: "blocking",
  restoring: "restoring", idle: "", skipped: "skipped", abstained: "UNKNOWN kept",
  failed: "failed", pending: "pending"
};

function renderRail() {
  const status = loopStatus();
  const current = currentNode(status);

  document.querySelectorAll("#rail li").forEach((li) => {
    const n = li.dataset.node;
    let st = status[n];
    if (n === "DETECT" && active.screen === "detect") st = "current";
    li.dataset.status = st;
    li.classList.toggle("current", n === current);
    li.querySelector("span").textContent = st === "current" ? "now" : (NODE_TEXT[st] ?? st);
  });
  $("rail").querySelector(".rail-replay").dataset.status = status.REPLAY;

  // Mobile progress
  const nodes = L.NODES.filter((n) => n !== "REPLAY");
  const idx = nodes.indexOf(current) + 1;
  $("mp-label").textContent = `${idx}/7 ${current}`;
  $("mp-dots").innerHTML = nodes.map((n) => {
    const st = n === "DETECT" && active.screen === "detect" ? "current" : status[n];
    return `<i data-status="${st}" class="${n === current ? "current" : ""}"></i>`;
  }).join("");
}

// ---------------------------------------------------------------------------
// ACTIVE — screens
// ---------------------------------------------------------------------------

let lastScreen = null;

function renderScreens() {
  // A new step starts at its top; never inherit the previous step's scroll.
  if (active.screen !== lastScreen) {
    $("stage").scrollTop = 0;
    lastScreen = active.screen;
  }
  document.querySelectorAll("#stage .screen").forEach((el) => {
    el.classList.toggle("active", el.dataset.screen === active.screen);
  });
  renderDetect();
  renderDecide();
  renderAbstained();
  renderCompile();
  renderGuard();
}

// Replace markup only when it changed, so running reveal animations are not
// restarted by unrelated re-renders.
function html(el, markup) {
  if (el.dataset.rendered !== markup) {
    el.innerHTML = markup;
    el.dataset.rendered = markup;
  }
}

// Values shown in more than one place (desktop and mobile chamber).
function bind(key, value) {
  document.querySelectorAll(`[data-bind="${key}"]`).forEach((el) => { el.textContent = value; });
}

function renderDetect() {
  const g = server?.gate;
  $("d-tests").textContent = data.baseline.testsPassed;
  $("d-suites").textContent = `${data.baseline.suitesGreen}/3`;
  $("d-conflicts").textContent = g ? g.integration.conflict_count : "—";
  bind("api-identity", g ? g.facts.api_customer_identity_field : "—");
  bind("ledger-identity", g ? g.facts.ledger_customer_identity_field : "—");
  $("d-status").innerHTML = g
    ? `<b>${esc(g.integration.status)}</b><span>gate: ${esc(g.verdict)}</span>`
    : serverChecked ? "No live gate on this origin." : "Checking the gate…";
  $("unavailable").classList.toggle("hidden", !serverChecked || Boolean(server));
}

function renderDecide() {
  const g = server?.gate;
  const gap = g?.findings.find((f) => f.kind === "SPEC_GAP");
  const drift = g?.findings.find((f) => f.kind === "AGENT_DRIFT");
  $("g-api").textContent = gap ? gap.candidates.api : "—";
  $("g-ledger").textContent = gap ? gap.candidates.ledger : "—";
  $("g-question").textContent = gap ? gap.question : "";
  $("g-drift").textContent = drift
    ? `${Object.values(drift.violations).join(", ")} → ${drift.expected}`
    : "—";
  $("decision-error").textContent = active.error && active.screen === "decide" ? active.error : "";
  const assumption = g?.assumptions?.[0];
  $("assumption-strip").classList.toggle("hidden", !assumption);
  $("g-assume-label").textContent = assumption ? assumption.concept : "—";
  $("g-assume").textContent = assumption
    ? `${assumption.value}, ${assumption.workstreams.length} of ${assumption.workstreams.length} agree`
    : "—";

  const decided = Boolean(active.decision || active.abstention);
  document.querySelectorAll(".decision-option").forEach((b) => {
    b.disabled = !server || active.busy || decided || !gap;
  });
}

function renderAbstained() {
  const a = active.abstention;
  if (!a) return;
  $("a-gate").textContent = a.gate_verdict;
  $("a-conflicts").textContent =
    `${a.integration.conflict_count} conflicts remain.`;
  $("a-facts").innerHTML = dl([
    ["canon written", String(a.canon_written)],
    ["decision memory written", String(a.decision_memory_written)],
    ["spec patch written", String(a.spec_patch_written)],
    ["repairs applied", a.repairs_applied.length ? a.repairs_applied.join(", ") : "none"],
    ["source tree untouched", String(a.source_tree_untouched)],
    ["receipt", `${a.receipt_dir}/abstention.json`]
  ]);
}

function compileItems(d) {
  const repaired = (ws, concept) =>
    d.repairs.find((r) => r.workstream === ws && r.concept === concept && r.action === "repaired");
  const api = repaired("api", "customer_identity");
  const ledger = repaired("ledger", "field_name");
  const v = d.memory.verification;
  const ok = (x) => Boolean(x);
  return [
    ["Decision compiled", ok(d.decision), d.memory.decision_ref],
    ["Spec patched", ok(d.spec_patch?.marker), `${d.spec_patch.target}, collider:canon marker`],
    ["API repaired", ok(api), api ? `${api.file_modified}: ${api.prior_value} → ${api.canonical_value}` : "no repair"],
    ["Ledger drift repaired", ok(ledger), ledger ? `${ledger.file_modified}: ${ledger.prior_value} → ${ledger.canonical_value}` : "no repair"],
    ["Regression contract written", ok(d.contract), d.memory.regression_artifact_ref],
    ["Decision memory written", ok(d.memory), `canon/decision-memory.json (${d.memory.evidence_state})`],
    ["Verified", v.tests_failed === 0 && v.tests_passed !== null,
      v.tests_passed === null ? "not run" : `${v.tests_passed} passed, ${v.tests_failed} failed`]
  ];
}

const CHECK_LABELS = [
  "Decision compiled", "Spec patched", "API repaired", "Ledger drift repaired",
  "Regression contract written", "Decision memory written", "Verified"
];

function renderCompile() {
  const d = active.decision;
  const shown = d ? active.compileRevealed : 0;
  const items = d ? compileItems(d) : CHECK_LABELS.map((l) => [l, null, ""]);

  $("checklist").dataset.shown = String(shown);
  html($("checklist"), items.map(([label, ok, detail], i) => {
    const st = i < shown ? (ok ? "done" : "failed") : (i === shown && d ? "running" : "pending");
    return `<li data-status="${st}" data-step="${i + 1}"><i></i><b>${esc(label)}</b><small>${esc(i < shown ? detail : "")}</small></li>`;
  }).join(""));

  const done = compileComplete();
  const ready = done && d.gate_after.verdict === "SEMANTICALLY_READY";
  $("result").dataset.state = !done ? "pending" : ready ? "ready" : "failed";

  if (done) {
    const m = d.manifest;
    const v = d.memory.verification;
    html($("r-number"),
      `<span class="rn-from">${esc(m.integration_conflicts_before)}</span><i>→</i><span class="rn-to">${esc(m.integration_conflicts_after)}</span>`);
    $("r-verdict").textContent = d.gate_after.verdict.replace("_", " ");
    $("r-tests").textContent =
      v.tests_passed === null ? "verification not run" : `${v.tests_passed} passed, ${v.tests_failed} failed`;
    const mem = d.memory;
    $("m-check").textContent = mem.evidence_state === "OBSERVED" ? "✓" : "";
    $("m-value").textContent = `${mem.concept} = ${mem.canonical_value}`;
    $("m-source").textContent =
      mem.human_decision_source === "INTERACTIVE_LOCAL_UI" || mem.human_decision_source === "INTERACTIVE_WEB"
        ? "Set by an interactive human decision."
        : `Set by a human decision (${mem.human_decision_source}).`;
    $("m-protected").textContent = ready
      ? `Guards ${mem.affected_dependents.join(" and ")} with ${mem.regression_artifact_ref}`
      : "Not protected: verification did not pass.";
    // The canonical trace reaches only the workstreams the decision repaired.
    html($("ws-mini"), m.workstreams.map((w) =>
      `<li data-changed="${w.changed}" data-ws="${esc(w.workstream)}"><b>${esc(w.workstream)}</b><i aria-hidden="true"></i><span>${w.changed ? "canon applied" : "untouched"}</span></li>`
    ).join(""));
  } else {
    html($("r-number"), `<span class="rn-from">2</span><i>→</i><span class="rn-to">·</span>`);
    $("r-verdict").textContent = d ? "Verifying…" : "Compiling…";
    $("r-tests").innerHTML = "&nbsp;";
    $("m-check").textContent = "";
    $("m-value").textContent = "—";
    $("m-source").innerHTML = "&nbsp;";
    $("m-protected").innerHTML = "&nbsp;";
    html($("ws-mini"), "");
  }
  $("c-eyebrow").textContent = active.error && active.screen === "compile"
    ? active.error
    : "";
}

// Changed source lines of a unified diff, without the file headers.
function changedLines(diff) {
  return String(diff || "").split("\n")
    .filter((l) => /^[-+]/.test(l) && !/^(---|\+\+\+)/.test(l))
    .map((l) => l[0] + " " + l.slice(1).trim().replace(/\s+#.*$/, ""));
}

function renderPrList() {
  const ready = compileComplete() && active.decision?.gate_after.verdict === "SEMANTICALLY_READY";
  $("pr-list").innerHTML = FUTURE_CHANGES.map((c, i) => {
    const r = active.guards[c.id];
    // The current change shows its verdict only once the panel has revealed it.
    const revealing = active.guardProbe === c.id && (active.guardRunning || (r && active.guardPhase < 2));
    const status = revealing ? "running" : r ? verdictText(r.guard_verdict) : "not run";
    const verdict = revealing ? "RUNNING" : r ? r.guard_verdict : "NONE";
    return `<li data-verdict="${esc(verdict)}" data-current="${active.guardProbe === c.id}">` +
      `<button type="button" data-probe="${esc(c.id)}" aria-pressed="${active.guardProbe === c.id}" ${!ready || active.busy ? "disabled" : ""}>` +
      `<b>${String.fromCharCode(65 + i)}</b><span>${esc(c.title)}</span><code>${esc(c.file)}</code><small>${esc(status)}</small>` +
      `</button></li>`;
  }).join("");
  $("pr-list").querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => runGuard(b.dataset.probe));
  });
}

function renderGuard() {
  const g = active.guard;
  const phase = g ? active.guardPhase : 0;
  const court = $("phase-panel");
  court.dataset.phase = String(phase);
  court.dataset.verdict = g ? g.guard_verdict : "NONE";
  court.dataset.running = String(active.guardRunning);

  const mem = active.decision?.memory;
  $("p-protected").textContent = mem ? `${mem.concept} = ${mem.canonical_value}` : "—";
  renderPrList();

  const change = FUTURE_CHANGES.find((c) => c.id === active.guardProbe);
  $("p-idle-title").textContent = active.guardRunning && change
    ? `${change.title}…`
    : active.error && active.screen === "guard" ? active.error : "Pick a change above.";
  $("p-idle-text").textContent = active.guardRunning
    ? "Applying the change, running the tests, then the gate with and without decision memory."
    : "Each change runs in this session's workspace and is restored afterwards. They are scripted changes, not agents.";
  if (!g) {
    $("p-attempt-kicker").textContent = "Proposed change";
    $("p-inline").textContent = change ? change.file : "";
    $("p-attempt").innerHTML = "";
    $("p-attempt-file").textContent = "";
    return;
  }

  const v = g.guard_verdict;
  const suite = g.verification_during_probe.full_suite;
  const ca = g.verification_after_restore.regression_contract;
  const cf = g.counterfactual_without_memory;
  const lines = changedLines(g.probe_diff);
  const total = suite.passed_count + suite.failed_count;

  $("p-attempt-kicker").textContent = "Proposed change";
  $("p-attempt").innerHTML = renderDiff(lines.join("\n"));
  $("p-attempt-file").textContent =
    `${g.affected_file}, sha ${short(g.sha_before_probe)} → ${short(g.sha_during_probe)}`;
  // An undecided concept has no canonical value: show what the other
  // workstreams still assume.
  const assumed = g.violation?.candidates
    ? Object.entries(g.violation.candidates).find(([ws]) => ws !== g.affected_workstream)?.[1]
    : null;
  $("p-inline").textContent = g.concept
    ? `${g.concept}: ${g.canonical_value ?? `${assumed} (assumed)`} → ${g.attempted_value}`
    : `${g.affected_workstream}: wording only`;

  // Conventional CI: exactly what the test suite said about the changed tree.
  $("p-ci-count").textContent = `${suite.passed_count}/${total}`;
  $("p-ci-state").textContent = suite.failed_count ? `${suite.failed_count} FAILED` : "ALL TESTS PASS";
  court.dataset.tests = suite.failed_count ? "red" : "green";

  $("p-verdict-kicker").textContent = "SEMANTIC CI";
  $("p-verdict").textContent = verdictText(v);
  $("p-rule").textContent = v === "MERGE_BLOCKED"
    ? `Contradicts decision memory. ${g.concept} must stay ${g.decision_memory_value}.`
    : v === "DECISION_REQUIRED"
      ? `New SPEC_GAP on ${g.concept}. The brief never set it.`
      : "No semantic concept changed.";
  $("p-cf").innerHTML =
    `Without decision memory, the same change gets <b>${esc(cf.verdict)}</b>. ` +
    (g.memory_changed_verdict ? "Memory changed the verdict." : "No decision covers this concept yet.");
  // Only the new question deserves space under the verdict.
  $("p-violation").innerHTML = v === "DECISION_REQUIRED" && g.surfaced_question
    ? dl([["next question", g.surfaced_question]])
    : "";

  $("p-restore").innerHTML = dl([
    ["sha before", short(g.sha_before_probe)],
    ["sha after restore", short(g.sha_after_restore)],
    ["exact bytes", String(g.restored_exact_bytes)]
  ]);

  const tick = (ok, text) => `<li data-ok="${ok}">${ok ? "✓" : "✗"} ${esc(text)}</li>`;
  $("p-complete-kicker").textContent = phase >= 4 ? "Restored" : phase === 3 ? "Restoring…" : "Restore";
  $("p-complete-verdict").textContent = verdictText(v);
  $("p-complete-verdict").dataset.verdict = v;
  $("p-complete").innerHTML = [
    ...(g.as_expected === false ? [tick(false, `expected ${verdictText(g.expected_guard_verdict)}`)] : []),
    tick(g.restoration_verified && g.restored_exact_bytes, `exact bytes, sha ${short(g.sha_after_restore)}`),
    tick(g.gate_after_restore === "SEMANTICALLY_READY", g.gate_after_restore),
    tick(ca.passed && ca.failed_count === 0, `contract ${ca.passed_count}/${ca.passed_count + ca.failed_count}`)
  ].join("");
  $("p-receipt").textContent = `receipt ${g.receipt_path}`;
}

// ---------------------------------------------------------------------------
// ACTIVE — proof drawer
// ---------------------------------------------------------------------------

const PROOF_TABS = [
  "Code diff", "Spec patch", "Contract", "Decision memory",
  "Receipt", "Hashes", "Provenance"
];

function renderDrawer() {
  $("drawer-tabs").innerHTML = PROOF_TABS.map((t) =>
    `<button type="button" role="tab" data-tab="${esc(t)}" aria-selected="${t === proofTab}">${esc(t)}</button>`
  ).join("");
  $("drawer-tabs").querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => { proofTab = b.dataset.tab; renderDrawer(); });
  });

  const d = active.decision;
  const a = active.abstention;
  const guards = FUTURE_CHANGES.map((c) => active.guards[c.id]).filter(Boolean);
  $("drawer-source").textContent = d
    ? `${activeLabel()}, ${d.receipt_dir}`
    : a ? `${activeLabel()}, ${a.receipt_dir}` : "No action taken yet.";

  const none = (msg) => `<p class="muted">${esc(msg)}</p>`;
  let body = "";

  switch (proofTab) {
    case "Code diff":
      body = d
        ? section("repair.patch (compiled workspace)", pre(renderDiff(d.repair_patch), "diff")) +
          guards.map((g) => section(`${g.title}: ${verdictText(g.guard_verdict)}, then restored`, pre(renderDiff(g.probe_diff), "diff"))).join("")
        : none(a ? "UNKNOWN was kept. No code changed." : "No decision yet, so no code has changed.");
      break;
    case "Spec patch":
      body = d
        ? section("spec.diff", pre(renderDiff(d.spec_diff), "diff")) +
          section("spec-patch.json", pre(json(d.spec_patch)))
        : none(a ? "UNKNOWN was kept. No spec patch was written." : "No decision yet.");
      break;
    case "Contract":
      body = d
        ? section(d.memory.regression_artifact_ref, pre(esc(d.contract))) +
          section("verification command", pre(esc(d.memory.verification.command || "")))
        : none("No regression contract exists without a canonical decision.");
      break;
    case "Decision memory":
      body = d
        ? section("canon/decision-memory.json", pre(json({ schema: "collider.decision-memory/v1", decisions: [d.memory] })))
        : none(a ? "UNKNOWN was kept. No decision memory was written." : "No decision memory yet.");
      break;
    case "Receipt":
      body =
        guards.map((g) => section(g.receipt_path, pre(json(g)))).join("") +
        (d ? section("manifest.json", pre(json(d.manifest))) +
             section("gate before", findingRows(d.gate_before.findings)) +
             section("gate after", findingRows(d.gate_after.findings)) : "") +
        (a ? section("abstention.json", pre(json(a))) : "") +
        (!d && !a && server ? section("live gate on the committed tree", findingRows(server.gate.findings)) : "") ||
        none("No receipt yet.");
      break;
    case "Hashes":
      body = d
        ? section("workstreams in the compiled workspace",
            `<table class="hash-table"><thead><tr><th>workstream</th><th>before</th><th>after</th><th></th></tr></thead><tbody>${
              d.manifest.workstreams.map((w) =>
                `<tr><td>${esc(w.workstream)}</td><td><code>${esc(short(w.sha256_before, 16))}</code></td><td><code>${esc(short(w.sha256_after, 16))}</code></td><td>${w.changed ? "CHANGED" : "unchanged"}</td></tr>`
              ).join("")}</tbody></table>` +
            `<p class="muted">source tree untouched: ${esc(d.manifest.source_tree_untouched)}</p>`) +
          guards.map((g) => section(`${g.title}: ${g.affected_file}`, `<dl class="facts">${dl([
            ["before probe", g.sha_before_probe],
            ["during probe", g.sha_during_probe],
            ["after restore", g.sha_after_restore],
            ["exact bytes restored", String(g.restored_exact_bytes)],
            ["source tree untouched", String(g.source_tree_untouched)]
          ])}</dl>`)).join("")
        : a ? section("committed tree", `<dl class="facts">${dl(Object.entries(a.source_sha256))}</dl>`)
          : none("No hashes yet.");
      break;
    case "Provenance": {
      const p = activeProvenance();
      const r = d ? d.replay : null;
      body = section("truth label", `<p class="truth">${esc([p.label, ...p.detail].join(", "))}</p>`) +
        section("run", `<dl class="facts">${dl([
          ["execution", server ? server.execution_environment : "—"],
          ["worker version", server?.worker_version || "none (not served by a Cloudflare Worker)"],
          ["interpretations", "PRESEEDED"],
          ["human decision", d ? d.decision.human_decision_source : a ? `${a.human_decision_source} (abstained)` : "none yet"],
          ["input commit", d ? d.manifest.input_commit : a ? a.input_commit : "—"],
          ["receipts", d ? d.receipt_dir : a ? a.receipt_dir : "—"]
        ])}</dl>`) +
        section("Separate LIVE_BOB run (not this session)", `<dl class="facts">${dl([
          ["run", "live-bob-2026-09-27-01, three independent Bob agents, contamination check clean"],
          ["observed", "customer_identity classified SPEC_GAP / UNKNOWN before any human decision"],
          ["replay attempt 01", "REPLAY_FAIL, 5 passed and 2 failed (kept on record)", "danger"],
          ["replay attempt 02", "REPLAY_PASS 7/7, a targeted-repair replay with a general minimal-change constraint"],
          ["this demo's interpretations", "PRESEEDED, not generated live by Bob", "unknown"]
        ])}</dl><p class="muted">Cited from evidence/bob-sessions/. This page does not re-run it.</p>`) +
        section("Fresh-agent replay in this session", `<dl class="facts">${dl([
          ["status", "NOT_EXECUTED", "unknown"],
          ["runtime state", "PENDING_LIVE_BOB", "unknown"],
          ["reason", r ? r.reason : "Replay requires an independent live agent session; none exists in this environment."],
          ...(r ? [
            ["given", `${r.inputs.patched_spec}, ${r.inputs.decision_memory}`],
            ["withheld", r.inputs.withheld.join(", ")],
            ["accepts only", r.acceptance.execution_source_in.join(", ")]
          ] : []),
          ["guard probes", "Scripted changes run against decision memory in this session. They are not agents."]
        ])}</dl>`);
      break;
    }
    default:
      body = "";
  }
  $("drawer-body").innerHTML = body;
}

// ---------------------------------------------------------------------------
// ACTIVE — action bar
// ---------------------------------------------------------------------------

function setButton(el, label, handler, opts = {}) {
  el.textContent = label || "";
  el.classList.toggle("hidden", !label);
  el.disabled = Boolean(opts.disabled);
  el.onclick = handler || null;
}

function renderActiveActions() {
  const back = $("back");
  const primary = $("primary");
  const secondary = $("secondary");
  let status = "";
  const proofLabel = drawerOpen ? "Hide proof" : "Proof";
  const toggleProof = () => { drawerOpen = !drawerOpen; render(); };

  setButton(back, "", null);
  setButton(secondary, "", null);

  switch (active.screen) {
    case "detect":
      if (serverChecked && !server) {
        setButton(primary, "Active mode unavailable", null, { disabled: true });
        setButton(secondary, "Open Evidence", () => setMode("EVIDENCE"));
        status = "No action runtime on this origin.";
      } else {
        setButton(primary, "Run COLLIDER", runCollider, { disabled: !server });
        status = server ? "" : "Connecting to the runtime…";
      }
      break;
    case "decide": {
      // The same two real choices as the workspace buttons, kept in the
      // sticky bar so the decision is always reachable (mobile included).
      const gap = server?.gate.findings.some((f) => f.kind === "SPEC_GAP");
      const locked = !server || !gap || active.busy || Boolean(active.decision || active.abstention);
      setButton(back, "Back", () => { active.screen = "detect"; render(); }, { disabled: active.busy });
      setButton(secondary, "Keep UNKNOWN", () => decide("KEEP_UNKNOWN"), { disabled: locked });
      setButton(primary, active.busy ? "Working…" : "Use account_id", () => decide("USE_ACCOUNT_ID"), { disabled: locked });
      status = "Waiting for a human decision.";
      break;
    }
    case "abstained":
      setButton(secondary, proofLabel, toggleProof);
      setButton(primary, "Start over", resetSession);
      status = "UNKNOWN kept. The gate stays at DECISION_REQUIRED.";
      break;
    case "compile": {
      const done = compileComplete();
      const ready = done && active.decision.gate_after.verdict === "SEMANTICALLY_READY";
      setButton(secondary, done ? proofLabel : "", toggleProof);
      if (!done) setButton(primary, "Compiling…", null, { disabled: true });
      else if (ready) setButton(primary, "Test future changes", () => runGuard((nextUntestedChange() || FUTURE_CHANGES[0]).id), { disabled: active.busy });
      else setButton(primary, "Start over", resetSession);
      status = !done ? "Compiling in an isolated workspace." : ready ? "" : active.decision.gate_after.verdict;
      break;
    }
    case "guard": {
      const finished = active.guard && active.guardPhase >= 4;
      const next = nextUntestedChange();
      const judged = Object.keys(active.guards).length;
      setButton(back, "Back", () => { active.screen = "compile"; render(); }, { disabled: active.busy || !finished && active.guardRunning });
      setButton(secondary, finished ? proofLabel : "", toggleProof);
      if (active.guardRunning || (active.guard && !finished)) setButton(primary, "Running…", null, { disabled: true });
      else if (next) setButton(primary, `Next: ${next.title}`, () => runGuard(next.id), { disabled: active.busy });
      else setButton(primary, "Start over", resetSession);
      status = active.guardRunning || (active.guard && !finished) ? ""
        : !active.guard ? (active.error || "")
        : `${judged} of ${FUTURE_CHANGES.length} changes checked.`;
      break;
    }
    default:
      break;
  }
  $("action-status").textContent = status;
}

// ---------------------------------------------------------------------------
// EVIDENCE MODE — explorer (committed receipts only)
// ---------------------------------------------------------------------------

const EVIDENCE_TABS = ["Baseline", "Comparison", "Decision receipt", "Hashes", "Truth boundary"];

function renderExplorer() {
  $("explorer-nav").innerHTML =
    `<div class="explorer-label"><strong>Committed evidence</strong><span>LOCAL / PRESEEDED</span><small>Read from the repository. Nothing here runs in the browser.</small></div>` +
    EVIDENCE_TABS.map((t, i) =>
      `<button type="button" data-tab="${esc(t)}" aria-selected="${t === evidenceTab}"><i>${String(i + 1).padStart(2, "0")}</i>${esc(t)}</button>`
    ).join("");
  $("explorer-nav").querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", () => { evidenceTab = b.dataset.tab; render(); });
  });

  const b = data.baseline;
  const c = data.classifications;
  const r = data.result;
  const R = data.decisionReceipt;
  let html = "";

  switch (evidenceTab) {
    case "Baseline":
      html = `
        <header class="ex-head"><span class="kicker">baseline-001, without COLLIDER</span>
          <h2>Locally green. Integration blocked.</h2></header>
        <div class="ex-metrics">
          <div><strong>${esc(b.testsPassed)}</strong><span>local tests passed</span></div>
          <div><strong>${esc(b.suitesGreen)}/3</strong><span>workstreams green</span></div>
          <div class="danger"><strong>${esc(b.conflicts)}</strong><span>integration conflicts</span></div>
          <div class="danger"><strong class="mono">${esc(b.status)}</strong><span>status</span></div>
        </div>
        ${section("conflicts observed at integration", `<table class="hash-table"><thead><tr><th>conflict</th><th>api</th><th>ledger</th><th>classification</th></tr></thead><tbody>${
          b.conflictList.map((x) => `<tr><td>${esc(x.conflict_id)}</td><td><code>${esc(x.api_value)}</code></td><td><code>${esc(x.ledger_value)}</code></td><td>${esc(x.classification ?? "none (baseline does not classify)")}</td></tr>`).join("")
        }</tbody></table>`)}
        <p class="muted">evidence/runs/baseline-001, runtime input ${esc(short(b.commit))}</p>`;
      break;
    case "Comparison":
      html = `
        <header class="ex-head"><span class="kicker">baseline-001 vs local-resolved-004</span>
          <h2>${esc(b.conflicts)} → ${esc(r.conflicts)} <small>${esc(r.status)}</small></h2></header>
        ${section("classification", `<ul class="findings">
          <li><b>SPEC_GAP</b> ${esc(c.customerIdentity.concept)} is ${esc(c.customerIdentity.epistemicState)}, auto_resolve ${esc(c.customerIdentity.autoResolve)} (${esc(Object.entries(c.customerIdentity.values).map(([k, v]) => `${k}=${v}`).join(", "))})</li>
          <li><b>AGENT_DRIFT</b> ${esc(c.fieldName.concept)}: the source says <code>${esc(c.fieldName.authoritativeValue)}</code> (${esc(c.fieldName.source)})</li>
          <li><b>${esc(c.moneyRepresentation.subtype)}</b> ${esc(c.moneyRepresentation.concept)}: upgrades to fact ${esc(c.moneyRepresentation.upgradesToFact)}</li>
        </ul>`)}
        ${section("targeted repairs", `<table class="hash-table"><thead><tr><th>workstream</th><th>concept</th><th>before → after</th><th>source</th></tr></thead><tbody>${
          data.repairs.map((x) => `<tr><td>${esc(x.workstream)}</td><td>${esc(x.concept)}</td><td><code>${esc(x.before)} → ${esc(x.after)}</code></td><td>${esc(x.source)}</td></tr>`).join("")
        }</tbody></table><p class="muted">notifications: unchanged</p>`)}
        ${section("fairness", `<p>${data.fairness.starting_workstream_artifacts_byte_identical ? "Both runs started from byte-identical workstream artifacts." : "Fairness check FAILED."}</p><p class="muted">${esc(data.fairness.note)}</p>`)}
        <p class="muted">evidence/comparisons/baseline-001-vs-local-resolved-004, evidence commit ${esc(short(data.evidenceCommit))}</p>`;
      break;
    case "Decision receipt": {
      const m = R.manifest;
      const v = R.memory.verification;
      html = `
        <header class="ex-head"><span class="kicker">${esc(R.receipt_dir)}, human decision ${esc(R.decision.human_decision_source)}</span>
          <h2>${esc(R.decision.concept)} = ${esc(R.decision.canonical_value)}</h2></header>
        <div class="ex-metrics">
          <div><strong class="mono">${esc(m.gate_before)}</strong><span>gate before</span></div>
          <div class="ok"><strong class="mono">${esc(m.gate_after)}</strong><span>gate after</span></div>
          <div class="ok"><strong>${esc(m.integration_conflicts_before)} → ${esc(m.integration_conflicts_after)}</strong><span>conflicts</span></div>
          <div class="ok"><strong>${esc(v.tests_passed)} / ${esc(v.tests_failed)}</strong><span>passed / failed</span></div>
        </div>
        ${section("repair.patch", pre(renderDiff(R.repair_patch), "diff"))}
        ${section("spec.diff", pre(renderDiff(R.spec_diff), "diff"))}
        ${section("regression contract", pre(esc(R.contract)))}
        ${section("decision memory", pre(json(R.memory)))}
        ${section("not in this receipt", `<p>The guard probe runs only in ACTIVE MODE; no guard receipt is committed. Fresh-agent replay: <b>${esc(R.replay.status)} / ${esc(R.replay.runtime_state)}</b>.</p>`)}`;
      break;
    }
    case "Hashes":
      html = `
        <header class="ex-head"><span class="kicker">artifact hashes</span><h2>Before, after and restored</h2></header>
        ${section("local-resolved-004: repair captured, source restored", `<table class="hash-table"><thead><tr><th>workstream</th><th>before</th><th>after</th><th>restored</th><th></th></tr></thead><tbody>${
          Object.entries(data.hashes).map(([ws, h]) => `<tr><td>${esc(ws)}</td><td><code>${esc(short(h.before, 16))}</code></td><td><code>${esc(short(h.after, 16))}</code></td><td><code>${esc(short(h.restored, 16))}</code></td><td>${h.changed ? (h.restored_to_input ? "CHANGED + RESTORED" : "CHECK FAILED") : "UNCHANGED"}</td></tr>`).join("")
        }</tbody></table>`)}
        ${section("decision-001, compiled workspace", `<table class="hash-table"><thead><tr><th>workstream</th><th>before</th><th>after</th><th></th></tr></thead><tbody>${
          R.manifest.workstreams.map((w) => `<tr><td>${esc(w.workstream)}</td><td><code>${esc(short(w.sha256_before, 16))}</code></td><td><code>${esc(short(w.sha256_after, 16))}</code></td><td>${w.changed ? "CHANGED" : "UNCHANGED"}</td></tr>`).join("")
        }</tbody></table><p class="muted">source tree untouched: ${esc(R.manifest.source_tree_untouched)}</p>`)}`;
      break;
    case "Truth boundary":
      html = `
        <header class="ex-head"><span class="kicker">truth boundary</span><h2>What this evidence proves, and what it does not.</h2></header>
        ${section("proven locally", `<dl class="facts">${dl([
          ["execution", "LOCAL"],
          ["interpretations", "PRESEEDED"],
          ["human decision (decision-001)", R.decision.human_decision_source],
          ["classification", "deterministic, classifier_judgment_used = false"],
          ["canonical evidence modified", String(R.manifest.truth_boundary.canonical_evidence_modified)]
        ])}</dl>`)}
        ${section("not claimed", `<dl class="facts">${dl([
          ["LIVE_BOB generation (these receipts)", "NOT CLAIMED", "unknown"],
          ["fresh-agent replay (these receipts)", `${R.replay.status} / ${R.replay.runtime_state}`, "unknown"],
          ["wall-clock improvement", R.manifest.truth_boundary.wall_clock_improvement, "unknown"],
          ["percentage improvement", R.manifest.truth_boundary.percentage_improvement, "unknown"],
          ["browser execution", "none: this explorer only reads committed receipts", "unknown"]
        ])}</dl>`)}
        ${section("separate observed evidence (not these receipts)", `<dl class="facts">${dl([
          ["LIVE_BOB run", "live-bob-2026-09-27-01, three independent Bob agents, SPEC_GAP / UNKNOWN observed"],
          ["replay attempt 01", "REPLAY_FAIL 5/7, kept on record", "danger"],
          ["replay attempt 02", "REPLAY_PASS 7/7, a targeted-repair replay, not an unconstrained first try"]
        ])}</dl><p class="muted">From evidence/bob-sessions/. The receipts above stay LOCAL / PRESEEDED.</p>`)}`;
      break;
    default:
      html = "";
  }
  $("explorer-body").innerHTML = html;
  $("explorer-body").scrollTop = 0;
}

function renderEvidenceActions() {
  const i = EVIDENCE_TABS.indexOf(evidenceTab);
  setButton($("back"), "Previous", () => { evidenceTab = EVIDENCE_TABS[i - 1]; render(); }, { disabled: i === 0 });
  setButton($("secondary"), "", null);
  setButton($("primary"),
    i < EVIDENCE_TABS.length - 1 ? `Next: ${EVIDENCE_TABS[i + 1]}` : "Back to active mode",
    () => { if (i < EVIDENCE_TABS.length - 1) evidenceTab = EVIDENCE_TABS[i + 1]; else setMode("ACTIVE"); render(); });
  $("action-status").textContent = "Committed receipts. Nothing runs in this browser.";
}

// ---------------------------------------------------------------------------

function render() {
  if (!data) return;
  renderChrome();
  if (mode === "ACTIVE") {
    renderRail();
    renderScreens();
    renderDrawer();
    renderActiveActions();
  } else {
    renderExplorer();
    renderEvidenceActions();
  }
}

async function boot() {
  const response = await fetch("./evidence.json");
  if (!response.ok) throw new Error("Could not load committed evidence.");
  data = await response.json();
  if (!L.acceptsResult("EVIDENCE", data.decisionReceipt)) {
    throw new Error("Committed decision receipt is not labelled as EVIDENCE.");
  }
  render();
  server = await detectServer();
  serverChecked = true;
  render();
}

document.querySelectorAll(".mode-switch button").forEach((b) => {
  b.addEventListener("click", () => setMode(b.dataset.mode));
});
document.querySelectorAll(".decision-option").forEach((b) => {
  b.addEventListener("click", () => decide(b.dataset.choice));
});
$("proof-toggle").addEventListener("click", () => { drawerOpen = !drawerOpen; render(); });
$("drawer-close").addEventListener("click", () => { drawerOpen = false; render(); });
$("to-evidence").addEventListener("click", () => setMode("EVIDENCE"));
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && drawerOpen) { drawerOpen = false; render(); }
});

boot().catch((error) => {
  console.error(error);
  document.body.innerHTML = `
    <main class="boot-error">
      <h1>Evidence failed to load.</h1>
      <p>${esc(error.message)}</p>
    </main>`;
});
