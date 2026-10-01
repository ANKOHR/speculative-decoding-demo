# Speculative Decoding Demo

A deterministic Python CLI implementing greedy toy speculative decoding on explicit target and draft token sequences. CPU only, standard library only, no model calls, network calls or GPU packages.

## Quickstart

Python 3.10 or newer and pytest are required for development. If a user installation puts `sdd.exe` outside PATH, add the Python user Scripts directory to PATH or use the module invocation below. Installation is entirely local.

```powershell
python -m pip install --no-index --no-build-isolation --no-deps -e .
sdd fixtures --out demo
sdd run --input demo
sdd report --format md
python -m pytest -q
```

`python -m speculative_decoding_demo.cli` also works without installation.

## Input reference

A directory contains UTF-8 `*.jsonl` files, read in filename order and line order. Blank lines and lines starting with `#` are ignored. Each non-comment line is one object with exactly these fields:

```json
{"id":"hand-entered-1","synthetic":false,"target":["a","b","c"],"draft":["a","x","c"],"block_size":2}
```

`id` is unique across all files, 1..4096 characters. `synthetic` must be a boolean. `target` and `draft` contain up to 100000 string tokens each, with 1..16384 characters per token. `block_size` is an integer in 1..1024; booleans are rejected. Unicode and Windows path strings are supported. Unknown fields, including dates and amounts, are rejected instead of interpreted. Negative values and extreme strings fail validation. Duplicate IDs fail the entire run. Empty directories are valid and yield zero counts. CSV, YAML and JSON input files are rejected with a named schema error; `expectations.json` is reserved fixture metadata and never used by the engine.

For a tiny five-record example, see `examples/tiny/records.jsonl`. Its tokens are synthetic, not Henry's real data. Henry can enter his own target and draft observations by hand and mark them `synthetic:false`; real trial data should remain private and is not shipped.

## Decoder semantics

The target sequence is an explicit greedy oracle. Starting at the current target position, propose up to `block_size` draft tokens at the same absolute positions. Accept the matching prefix. At the first mismatch, discard the rest of the block and emit the correct target token. A fully accepted block emits one bonus target token if one remains. An exhausted draft falls back to one target token per call. Output always equals the supplied target.

Each iteration counts as one toy verifier call. The baseline counts one call per target token. Proposed counts include discarded trailing proposals; rejected counts count first mismatches only. Accepted, corrections and bonus reconcile exactly to output tokens. Traces include start, end, proposed and accepted for every iteration. This is a greedy educational algorithm, not probabilistic speculative sampling or a real inference benchmark.

## Commands

| Command | Example | Result |
| --- | --- | --- |
| fixtures | `sdd fixtures --out demo` | 200 labelled synthetic records plus independent expectations |
| run | `sdd run --input demo --results result.json` | Compute and atomically save all results |
| report | `sdd report --results result.json --format json --out report.json` | Render saved results with provenance |
| decode | `sdd decode --input demo` | JSON token outputs and acceptance traces |
| compare | `sdd compare --input demo` | Markdown toy verifier and greedy baseline counts |

Every subcommand provides `--help` and an example. Default results are stored in `.sdd-results.json`. Results contain input paths and per-record provenance. All output JSON escapes non-ASCII characters to preserve text and avoid forbidden punctuation in rendered output. Markdown reports contain counts, not user token strings.

## Architecture

```text
JSONL input -> CLI parser and validation -> pure core.decode/evaluate
                                               |
                                               v
                                    atomic results JSON -> report renderer
fixture generator -> labelled JSONL + hand-computed expectations -> tests only
```

## Hypothesis and acceptance evidence

A deterministic decoder can be trusted within its documented toy semantics when each behavior is tested against planted ground truth. Five patterns are repeated 40 times, with no randomness or seed: fully matching, fully mismatching, partially matching, exhausted draft, and empty target. Independent hand counts at block size two are:

| Pattern | Tokens | Accepted | Rejected | Proposed | Corrections | Bonus | Verifier calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Matching | 4 | 3 | 0 | 3 | 0 | 1 | 2 |
| Mismatching | 4 | 0 | 4 | 7 | 4 | 0 | 4 |
| Partial | 4 | 3 | 1 | 4 | 1 | 0 | 2 |
| Exhausted | 4 | 0 | 0 | 0 | 4 | 0 | 4 |
| Empty | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Multiply column sums by 40. Baseline calls equal 640, verifier calls equal 480, rejection records equal 80. Tests compare every total and the exact rejection ID set, so there are zero false positives and no missed planted rejection records. Corrupting a draft token changes computed rejection counts while preserving target output. The expectations file does not drive reporting.

See `EVIDENCE.md` for the measured local test and demo results.

## Honesty boundary and fixture policy

All figures come from explicit inputs. Toy call counts are computed counts, not measured runtime savings. Time saved, money saved and real model speedup are unmeasured and are not estimated. The target oracle is supplied, not discovered or predicted. A `synthetic:false` label is a user declaration, not independent proof of provenance. No real-use results have been measured.

Synthetic JSONL files have a header comment and every record has `synthetic:true`. Synthetic JSON expectations have `synthetic:true` plus a comment field because JSON forbids header comments. Every report carries synthetic and user-declared real counts. Repeated runs with identical input paths and inputs produce identical bytes; no timestamps enter results.

## Failure modes

Malformed JSONL yields ParseError with file, line and column. Invalid schema yields SchemaError with file, line and offending field. Missing directories yield MissingInput with a usage hint and exit code 2. Unsupported formats are rejected. I/O and encoding failures are named, with exit code 2. Writes use a temporary file in the destination directory and atomic replacement; failed writes remove temporary files and preserve any prior result. Output parents must already exist. CLI argument errors also exit nonzero. This program does not validate external claims about the correctness of the supplied target.

## Two-week improvement hook and verdict

The real-use window begins when Henry first records a real trial. Record date, input identifier, hand-checked output, mismatch count and whether the tool was used in a private local trial log. After two weeks, measure token output error rate against the hand-checked sample: mismatched tokens divided by checked tokens, with both counts recorded. Empty samples have no measurable error rate. If error exceeds 10 percent, fix the top measured failure cause or kill with the reason recorded. If it was never used, kill with that evidence.

Verdict is pending the two-week window, not invented now. Record an explicit expand / integrate / commercialise / maintain / kill verdict and reason in `VERDICT.md`: expand for daily use or revenue, integrate for substantial sibling overlap, commercialise for demonstrated willingness to pay, maintain as portfolio evidence otherwise, kill for no use or unmet acceptance criteria.
