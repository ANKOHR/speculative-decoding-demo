"""Pure greedy speculative decoding over explicitly supplied token sequences.
Target tokens are an oracle input, not predictions. Calls are toy operation counts.
"""
class SchemaError(ValueError):
    """Input violates the documented schema."""


def validate(record):
    if not isinstance(record, dict):
        raise SchemaError("record: expected object")
    required = {"id", "synthetic", "target", "draft", "block_size"}
    if set(record) != required:
        raise SchemaError("fields: missing or unknown " + str(sorted(set(record) ^ required)))
    if not isinstance(record["id"], str) or not 1 <= len(record["id"]) <= 4096:
        raise SchemaError("id: expected nonempty string of at most 4096 characters")
    if type(record["synthetic"]) is not bool:
        raise SchemaError("synthetic: expected boolean")
    if type(record["block_size"]) is not int or not 1 <= record["block_size"] <= 1024:
        raise SchemaError("block_size: expected integer in 1..1024")
    for field in ("target", "draft"):
        value = record[field]
        if not isinstance(value, list) or len(value) > 100000:
            raise SchemaError(field + ": expected token list of at most 100000 tokens")
        if any(not isinstance(t, str) or not 1 <= len(t) <= 16384 for t in value):
            raise SchemaError(field + ": tokens must be nonempty strings of at most 16384 characters")
    return record


def decode(record):
    """Accept matching draft prefixes; on rejection emit the target correction.
    Draft is indexed by absolute target position. A fully accepted block emits
    a bonus target token when one remains. Each block is one toy verifier call.
    """
    validate(record)
    target, draft, k = record["target"], record["draft"], record["block_size"]
    pos = accepted = rejected = calls = proposed = corrections = bonus = 0
    output, trace = [], []
    while pos < len(target):
        start = pos
        candidates = draft[pos:min(pos + k, len(target))]
        calls += 1
        proposed += len(candidates)
        matched = 0
        for token in candidates:
            if token != target[pos]:
                rejected += 1
                break
            output.append(token)
            pos += 1
            accepted += 1
            matched += 1
        if pos < len(target):
            output.append(target[pos])
            pos += 1
            if matched == len(candidates) and candidates:
                bonus += 1
            else:
                corrections += 1
        trace.append({"start": start, "proposed": len(candidates), "accepted": matched, "end": pos})
    return {"id": record["id"], "synthetic": record["synthetic"], "output": output,
            "tokens": len(output), "accepted": accepted, "rejected": rejected,
            "proposed": proposed, "corrections": corrections, "bonus": bonus,
            "verifier_calls": calls, "baseline_calls": len(target), "trace": trace}


def evaluate(records):
    seen, results = set(), []
    for record in records:
        validate(record)
        if record["id"] in seen:
            raise SchemaError("id: duplicate " + record["id"])
        seen.add(record["id"])
        results.append(decode(record))
    fields = ("tokens", "accepted", "rejected", "proposed", "corrections", "bonus", "verifier_calls", "baseline_calls")
    totals = {field: sum(r[field] for r in results) for field in fields}
    totals.update(records=len(results), synthetic_records=sum(r["synthetic"] for r in results),
                  real_records=sum(not r["synthetic"] for r in results),
                  records_with_rejection=sum(r["rejected"] > 0 for r in results))
    return {"totals": totals, "results": results}
