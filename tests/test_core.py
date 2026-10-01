import pytest
from speculative_decoding_demo.core import decode, evaluate, SchemaError


def record(**changes):
    return dict(id="one", synthetic=False, target=["a", "b", "c"], draft=["a", "x", "c"], block_size=2, **changes)


def test_prefix_rejection_and_correction():
    result = decode(record())
    assert result["output"] == ["a", "b", "c"]
    assert (result["accepted"], result["rejected"], result["verifier_calls"]) == (2, 1, 2)


@pytest.mark.parametrize("field,value", [("block_size", -1), ("block_size", True), ("block_size", 1025), ("target", [""]), ("draft", "bad"), ("synthetic", 1), ("id", ""), ("id", "x" * 4097)])
def test_rejects_adversarial_values(field, value):
    r = record(); r[field] = value
    with pytest.raises(SchemaError, match=field):
        decode(r)


def test_duplicate_ids():
    with pytest.raises(SchemaError, match="duplicate"):
        evaluate([record(), record()])


def test_handles_unicode_and_long_inputs():
    r = record(); r["id"] = "C:\\Users\\Henry\\中文"; r["target"] = ["雪" * 16000]; r["draft"] = r["target"]
    assert decode(r)["output"] == r["target"]


def test_unknown_amount_and_future_date_are_schema_errors():
    for field, value in (("amount", -1), ("date", "2099-01-01")):
        r = record(); r[field] = value
        with pytest.raises(SchemaError, match=field):
            decode(r)
