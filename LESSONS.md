# Lessons for KOML

The greedy toy decoder needs a correction on rejection and a bonus token after a fully accepted block. Counting all proposals as accepted would hide wasted work. Hand-derived fixtures distinguish proposed tokens, accepted tokens, first mismatches and verifier calls.

Validated locally: the explicit oracle lets deterministic prefix acceptance reproduce every target exactly, including mismatches and exhausted drafts. The tests demonstrate the narrow correctness hypothesis on synthetic data. They do not validate real model speedup or practical usefulness.

Operating rule: derive the expected counts independently of the implementation and mutate an input to prove the report responds. Keep operation-count evidence separate from runtime and real-use claims.
