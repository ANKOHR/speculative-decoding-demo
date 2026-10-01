# Local acceptance evidence

Measured on 2026-10-01, Windows, Python 3.12.10, CPU only.

- pytest: 29 tests passed.
- Installed sdd console entry point: fixtures, run, report completed in 0.9891 seconds total, measured with perf_counter around three subprocesses.
- 200 synthetic records; 640 output tokens; 240 accepted draft tokens; 200 first mismatches; 560 proposed tokens; 360 corrections; 40 bonus tokens.
- 480 toy verifier calls versus 640 toy baseline calls. These are computed operation counts, not measured speedup.
- Exactly 80 planted rejection records found; zero false positives and zero misses against independent expectations.
- All per-record outputs equal supplied targets. Input corruption changes computed counts.
- Empty inputs, malformed input, schema errors, duplicate IDs, Unicode, long tokens, missing directories, unsupported formats, atomic write failure, deterministic bytes, provenance and output punctuation covered by tests.

Timing is a local observation, not a portable performance guarantee. No real-use error rate, real model benchmark, time saved or money saved has been measured. No external network or model calls were used by the project.
