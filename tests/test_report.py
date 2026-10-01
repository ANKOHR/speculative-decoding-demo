import json
from speculative_decoding_demo.fixtures import generate, EXPECTATIONS
from speculative_decoding_demo.cli import read_records
from speculative_decoding_demo.core import evaluate
from speculative_decoding_demo.report import render


def test_report_matches_ground_truth_exact(tmp_path):
    generate(tmp_path)
    assert json.loads(render(evaluate(read_records(tmp_path)), "json"))["totals"] == EXPECTATIONS


def test_report_zero_false_positives(tmp_path):
    generate(tmp_path)
    results = evaluate(read_records(tmp_path))["results"]
    planted = json.loads((tmp_path / "expectations.json").read_text())["rejection_ids"]
    assert {r["id"] for r in results if r["rejected"]} == set(planted)


def test_report_carries_provenance_banner():
    for fmt in ("md", "json"):
        assert "Data provenance:" in render(evaluate([]), fmt)


def test_hypothetical_figures_labelled():
    text = render(evaluate([]))
    assert "unmeasured" in text and "no estimates" in text


def test_no_em_dashes_in_outputs():
    for fmt in ("md", "json"):
        assert chr(0x2014) not in render(evaluate([]), fmt)
