"""
Gate registry consistency — product/GATEWAY-REGISTRY.md vs state/HANDOVER.yaml.

A consistency check, not a truth check: it cannot prove a gate, but it fails
when the canonical documents disagree with each other, use an unknown status,
cite a PROVEN receipt that does not exist, or mark a gate N/A without a reason.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "product/GATEWAY-REGISTRY.md"
HANDOVER = ROOT / "state/HANDOVER.yaml"
CURRENT = ROOT / "state/CURRENT.yaml"

STATUSES = {"PROVEN", "PROVISIONAL_PASS", "ACTIVE", "PENDING", "BLOCKED", "N/A"}
PATH_RE = re.compile(r"\b((?:product|demo|evidence|fixtures|state|tests|cloudflare|collider|submission)/[\w./-]+\.(?:md|py|yaml|json))")


def registry_rows() -> dict:
    rows = {}
    for line in REGISTRY.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] in ("Gateway / Gate", "---") or set(cells[0]) <= {"-"}:
            continue
        if not line.startswith("|"):
            continue
        rows[cells[0]] = {"status": cells[1], "reason": cells[2]}
    return rows


def yaml_block(path: Path, key: str) -> dict:
    """Parse a flat `key:` block of `  "Name": STATUS` lines (no YAML dependency)."""
    out, inside = {}, False
    for line in path.read_text().splitlines():
        if re.match(rf"^{key}:\s*$", line):
            inside = True
            continue
        if inside:
            if line and not line.startswith(" "):
                break
            m = re.match(r'^\s+"([^"]+)":\s*([A-Z_/]+)', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


class TestGateRegistry(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = registry_rows()
        cls.handover = yaml_block(HANDOVER, "gateway_status")
        cls.current = yaml_block(CURRENT, "gateway_status")

    def test_registry_parses(self):
        self.assertGreaterEqual(len(self.rows), 25)
        for gate in ("Truth Boundary", "Negative Path", "Public Runtime / Live Proof",
                     "Real-User / Outsider Break Test", "x402"):
            self.assertIn(gate, self.rows)

    def test_statuses_are_from_the_vocabulary(self):
        for gate, row in self.rows.items():
            with self.subTest(gate=gate):
                self.assertIn(row["status"], STATUSES)

    def test_proven_gates_cite_existing_receipts(self):
        for gate, row in self.rows.items():
            if row["status"] != "PROVEN":
                continue
            with self.subTest(gate=gate):
                cited = PATH_RE.findall(row["reason"])
                for rel in cited:
                    self.assertTrue((ROOT / rel).exists(), f"{gate}: {rel} does not exist")

    def test_not_applicable_needs_a_reason(self):
        for gate, row in self.rows.items():
            if row["status"] == "N/A":
                with self.subTest(gate=gate):
                    self.assertGreater(len(row["reason"]), 10)

    def test_handover_and_current_agree_with_registry(self):
        for name, block in (("HANDOVER", self.handover), ("CURRENT", self.current)):
            self.assertGreaterEqual(len(block), 15, name)
            for gate, status in block.items():
                with self.subTest(doc=name, gate=gate):
                    self.assertIn(gate, self.rows, f"{name} names an unregistered gate")
                    self.assertEqual(status, self.rows[gate]["status"])

    def test_interpretations_are_never_recorded_as_live_bob(self):
        for doc in (REGISTRY, HANDOVER, CURRENT):
            text = doc.read_text()
            self.assertNotRegex(text, r"interpretation_source:\s*LIVE_BOB")


if __name__ == "__main__":
    unittest.main()
