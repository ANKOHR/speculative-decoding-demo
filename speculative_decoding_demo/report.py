"""Reports distinguish measured counts from hypothetical performance."""
import json

HONESTY = "Toy operation counts computed from inputs. Wall-clock speedup, time saved and money saved are unmeasured; no estimates are reported."


def render(data, format="md"):
    totals = data["totals"]
    banner = (f"Data provenance: {totals['synthetic_records']} synthetic fixture records; "
              f"{totals['real_records']} user-declared real records entered by the user. "
              "Real provenance is a declaration, not independently verified.")
    if format == "json":
        return json.dumps({"provenance": banner, "honesty": HONESTY, **data}, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    lines = ["# Speculative Decoding Demo", "", banner, "", HONESTY, "", "| Computed count | Value |", "| --- | ---: |"]
    lines += [f"| {key} | {value} |" for key, value in sorted(totals.items())]
    lines += ["", "Per-record output and verification traces are available in the JSON report."]
    return "\n".join(lines) + "\n"
