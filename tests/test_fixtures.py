import json
from speculative_decoding_demo.fixtures import generate, EXPECTATIONS
from speculative_decoding_demo.cli import read_records
from speculative_decoding_demo.core import evaluate


def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    assert (tmp_path / "records.jsonl").read_text().startswith("# Synthetic")
    assert all(r["synthetic"] is True for r in read_records(tmp_path))
    assert json.loads((tmp_path / "expectations.json").read_text())["synthetic"] is True


def test_fixture_ground_truth_matches_hand_computed(tmp_path):
    generate(tmp_path)
    assert evaluate(read_records(tmp_path))["totals"] == EXPECTATIONS


def test_corrupted_fixture_changes_computed_output(tmp_path):
    generate(tmp_path)
    records = read_records(tmp_path)
    before = evaluate(records)
    records[0]["draft"][0] = "incorrect"
    after = evaluate(records)
    assert after["totals"]["rejected"] == before["totals"]["rejected"] + 1
    assert after["results"][0]["output"] == records[0]["target"]
