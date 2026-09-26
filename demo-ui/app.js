const stage = document.querySelector(".stage");

let data;
let step = 0;

const labels = [
  "BASELINE",
  "CLASSIFY",
  "ABSTAIN",
  "TARGETED REPAIR",
  "PROOF"
];

const $ = (id) => document.getElementById(id);

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

  render();
}

function render() {
  stage.dataset.step = String(step);

  $("step-label").textContent = labels[step];
  $("step-counter").textContent = `${step + 1} / 5`;
  $("progress-fill").style.width = `${(step + 1) * 20}%`;

  $("prev").disabled = step === 0;

  $("next").textContent =
    step === 4
      ? "Replay proof ↺"
      : step === 0
        ? "Run COLLIDER →"
        : "Continue →";

  const classified = step >= 1;
  const questioned = step >= 2;
  const repaired = step >= 3;
  const proved = step >= 4;

  $("classification-grid").classList.toggle(
    "hidden",
    !classified
  );

  $("question-panel").classList.toggle(
    "hidden",
    !questioned
  );

  $("ledger-repair").classList.toggle(
    "hidden",
    !repaired
  );

  $("api-repair").classList.toggle(
    "hidden",
    !repaired
  );

  $("api-identity").textContent =
    repaired ? "account_id" : "email";

  $("ledger-field").textContent =
    repaired ? "refund_amount" : "credit_amount";

  if (proved) {
    $("collision-number").textContent =
      `${data.baseline.conflicts} → ${data.result.conflicts}`;

    $("collision-title").textContent =
      "EXECUTABLE INTEGRATION CONFLICTS";

    $("collision-status").textContent =
      data.result.status;

    $("final-conflicts").textContent =
      data.result.conflicts;

    $("final-status").textContent =
      data.result.status;

    $("receipt-state").textContent =
      "OBSERVED / COMMITTED";

    $("api-hash-state").textContent =
      data.hashes.api.restored_to_input
        ? "CHANGED + RESTORED"
        : "CHECK FAILED";

    $("ledger-hash-state").textContent =
      data.hashes.ledger.restored_to_input
        ? "CHANGED + RESTORED"
        : "CHECK FAILED";

    $("notification-hash-state").textContent =
      data.hashes.notifications.changed
        ? "UNEXPECTED CHANGE"
        : "UNCHANGED";
  } else {
    $("collision-number").textContent =
      data.baseline.conflicts;

    $("collision-title").textContent =
      "INTEGRATION CONFLICTS";

    $("collision-status").textContent =
      data.baseline.status;

    $("final-conflicts").textContent = "—";
    $("final-status").textContent = "waiting";
    $("receipt-state").textContent =
      "WAITING FOR CANONICAL PROOF";
    $("api-hash-state").textContent = "—";
    $("ledger-hash-state").textContent = "—";
    $("notification-hash-state").textContent = "—";
  }
}

$("next").addEventListener("click", () => {
  step = step === 4 ? 0 : step + 1;
  render();
});

$("prev").addEventListener("click", () => {
  step = Math.max(0, step - 1);
  render();
});

boot().catch((error) => {
  console.error(error);

  document.body.innerHTML = `
    <main style="padding:40px;font-family:system-ui">
      <h1>Evidence failed to load.</h1>
      <p>${error.message}</p>
    </main>
  `;
});
