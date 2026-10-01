"""Synthetic fixtures, no randomness. Expectations derived by hand per pattern."""
import json
from pathlib import Path

LABEL = "# Synthetic fixture data: synthetic: true"
PATTERNS = [
    (["a", "b", "c", "d"], ["a", "b", "c", "d"]),
    (["a", "b", "c", "d"], ["x", "x", "x", "x"]),
    (["a", "b", "c", "d"], ["a", "x", "c", "d"]),
    (["a", "b", "c", "d"], []),
    ([], []),
]
# Each pattern occurs 40 times: hand-counted at block size 2.
EXPECTATIONS = {"records": 200, "synthetic_records": 200, "real_records": 0,
    "tokens": 640, "accepted": 240, "rejected": 200, "proposed": 560,
    "corrections": 360, "bonus": 40, "verifier_calls": 480,
    "baseline_calls": 640, "records_with_rejection": 80}


def generate(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    records = [{"id": f"synthetic-{i:03d}", "synthetic": True,
                "target": PATTERNS[i % 5][0], "draft": PATTERNS[i % 5][1], "block_size": 2}
               for i in range(200)]
    (out / "records.jsonl").write_text(LABEL + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n", encoding="utf-8")
    (out / "expectations.json").write_text(json.dumps({"synthetic": True,
        "comment": "Synthetic hand-computed expectations, 40 copies of each of five patterns",
        "totals": EXPECTATIONS, "rejection_ids": [r["id"] for i, r in enumerate(records) if i % 5 in (1, 2)]}, indent=2) + "\n", encoding="utf-8")
