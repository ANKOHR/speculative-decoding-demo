"""Local-file CLI with atomic result/report writes."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import SchemaError, evaluate
from .fixtures import generate
from .report import render


class InputError(ValueError):
    pass


def read_records(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f"MissingInput: {directory}: use sdd fixtures --out <dir>")
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in (".csv", ".yaml", ".yml", ".json") and path.name != "expectations.json":
            raise InputError(f"SchemaError: {path}: line 1: unsupported format; use records.jsonl")
    records = []
    for path in sorted(directory.glob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip() or line.startswith("#"):
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise InputError(f"ParseError: {path}: line {line_number}, column {error.colno}: {error.msg}") from error
            try:
                from .core import validate
                validate(record)
                if any(r["id"] == record["id"] for r in records):
                    raise SchemaError("id: duplicate " + record["id"])
            except SchemaError as error:
                raise InputError(f"SchemaError: {path}: line {line_number}: {error}") from error
            records.append(record)
    return records


def atomic_write(path, text):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description="CPU-only deterministic toy speculative decoder")
    sub = parser.add_subparsers(dest="command", required=True)
    fixtures = sub.add_parser("fixtures", help="Generate 200 labelled synthetic records", epilog="Example: sdd fixtures --out demo")
    fixtures.add_argument("--out", required=True)
    run = sub.add_parser("run", help="Decode all JSONL records", epilog="Example: sdd run --input demo")
    run.add_argument("--input", required=True)
    run.add_argument("--results", default=".sdd-results.json")
    report = sub.add_parser("report", help="Render counts and provenance", epilog="Example: sdd report --format md")
    report.add_argument("--format", choices=["md", "json"], default="md")
    report.add_argument("--results", default=".sdd-results.json")
    report.add_argument("--out")
    for name, help_text in (("decode", "Show token outputs and acceptance traces"), ("compare", "Compare toy verifier calls with greedy baseline calls")):
        item = sub.add_parser(name, help=help_text, epilog=f"Example: sdd {name} --input demo")
        item.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 synthetic fixture records (synthetic: true).")
        elif args.command in ("run", "decode", "compare"):
            data = evaluate(read_records(args.input))
            data["inputs"] = [str(p) for p in sorted(Path(args.input).glob("*.jsonl"))]
            if args.command == "run":
                atomic_write(args.results, json.dumps(data, ensure_ascii=True, sort_keys=True, indent=2) + "\n")
                print(render(data, "md"), end="")
            else:
                print(render(data, "json" if args.command == "decode" else "md"), end="")
        else:
            data = json.loads(Path(args.results).read_text(encoding="utf-8"))
            text = render(data, args.format)
            if args.out:
                atomic_write(args.out, text)
            else:
                print(text, end="")
        return 0
    except (InputError, SchemaError, OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        # ASCII escaping also prevents user-provided punctuation violating output policy.
        message = str(error).encode("ascii", "backslashreplace").decode("ascii")
        print(f"{type(error).__name__}: {message}. Check input schema and output path; see sdd --help.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
