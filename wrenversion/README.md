# TECHNologic in SkillWren

A compact logic conversion of the [main skill](../skills/technologic/SKILL.md).
The actual flow carries the requirements. The original is retained in an
audit manifest and is not embedded or loaded as a second instruction set.

## Measured prompt size

Measured with the same `cl100k_base` tokenizer on complete SKILL.md files:

| Version | Lines | Tokens |
|---|---:|---:|
| Original TECHNologic | 110 | 2,205 |
| Previous Wren build with embedded original | 355 | 4,334 |
| Prose/impact-fixed Wren candidate | 176 | 2,077 |
| Compressed release 3.2-wren.4 | 176 | 1,970 |

The shipped prompt saves **235 tokens (10.7%)** versus the original. It is 181
bytes smaller and 369 words shorter; line count rises because indentation,
gates, declarations, and branches take separate lines. Earlier Wren.3 used
2,007 tokens before the routing, shared-impact, and compression revisions.
Counts use cl100k_base and do not predict every host tokenizer or total task cost.

These figures include the entire loaded header, contract, flow, and short
report appendix. No additional instruction file is deferred to hide its cost.
Both versions use the same detector; its code is executed rather than
automatically included in either prompt.

## Files

- `source/technologic.md`: editable control-language source.
- `source/coverage.json`: reviewed requirement map and original/logic hashes.
- `scripts/rebuild.py`: validates the review and compiles the package.
- `scripts/measure_context.py`: measures original and compiled prompts.
- `scripts/prepare_own_ab.py`: prepares identical isolated task copies for a local agent comparison.
- `skills/technologic-logic/`: compiled skill, detector, audit manifest.
- `tests/test_rebuild.py`: offline package, branch, mutation, and size checks.
- `tests/sample-project/`: existing runtime-test fixture, unchanged.

The generated SKILL.md is the compact source compiled without context imports.
The detector is copied byte for byte. The manifest archives exact originals,
authoring source, detector, and review map for traceability. Audit material is
not a runtime instruction dependency.

## Rebuild and verify

From Z:\technologic:

```powershell
python wrenversion/scripts/rebuild.py
python wrenversion/scripts/rebuild.py --check
python -m unittest discover -s wrenversion/tests -p 'test_*.py'
python wrenversion/scripts/measure_context.py
```

The default compiler is the sibling Z:\SkillWren checkout. Override it with
`--skillwren-root C:/path/to/SkillWren`. Compilation needs only the standard
library plus that checkout. Exact measurement uses optional tiktoken and its
vocabulary; the measurement command exits nonzero if the result is not smaller.

The builder stages and validates before replacing its three managed outputs.
Other local files and the original skill remain untouched. The check option
recompiles temporarily without modifying package files and detects stale output.
The package is not installed automatically.

## Preserving the concepts

One deliver flow selects scope and depth, handles approval, then branches by
job. Fast reaches the nearest check only when job preconditions are met and
that check covers its proof obligations. Verify bypasses writes and reports
Fix candidates. Standard/Deep work takes a baseline and applies explicit
Build, Fix, Validate, Speed up, Upgrade, Rename, Remove, Secure, Port, and Release
branches before bounded implementation increments.

The flow contains pre-change regression/parity evidence, independent test
oracles, matched performance workloads, per-upgrade checks, unchanged-behavior
requirements, non-use checks before deletion, and publication limits.
Global contracts carry shared-tree ownership, risk-based depth/scrutiny,
iteration limits, partial coverage, and surprise handling. Runtime, edge,
coverage, cleanup, documentation, and final-check stages preserve the original
proof obligations. The appendix defines the short report and evidence limits.

The 41-part requirement map connects every nonblank original line to reviewed
logic anchors. Its hashes bind the review to both files. If either the main
skill or compact logic changes, review the conversion and update the map before
rebuilding. The builder checks hashes, spans, IDs, anchor presence, and complete
source-line accounting; those checks cannot prove prose equivalence.

## Evidence and limits

The offline suite checks exact original recovery outside the prompt, detector
equality, deterministic output/hashes, original preservation, static gates,
and branch reachability under explicit Verify/Fast assumptions. Mutants add a
Verify write, remove Fast's early return, remove approval, mutate the immutable
detector, and omit a mapped requirement to show these guards can fail.
An exact-token regression requires the compiled prompt to stay below the
original when tiktoken is available. SkillWren validation has no errors or
warnings and uses its default 2500-token body ceiling.

Three local Codex-agent trials tested Fix on the same frozen mote bug across
the prose, fixed, and compressed variants. All three passed `mote-core` (191
passed, 2 ignored); the report is `results/2026-10-21-mote-fix-ab.md`. The
compressed inventory has 124 entries and no structural differences from the
fixed candidate. The local agent service hit its usage limit before it exposed
per-run turns, token use, cost, or complete reports. These are structural and
task checks, not observations of a model performing every job. The broad repository
glob does not enforce scope or filesystem containment. The sample's existing
empty-input bug remains; its ordinary tests do not cover that case.
