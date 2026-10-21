# TECHNologic field test: Fix longitude wrapping (three-way A/B)

- **Date:** 2026-10-21
- **Task:** Fix the A008 finite-longitude periodicity defect in `mote-core`; preserve the `[-180, 180)` convention; add a regression that detects the original defect.
- **Target:** `Z:\voxelgame`, frozen into `wrenversion/ab/2026-10-21/snapshot/` with 157 files. The live dirty tree was not modified.
- **Starting state:** Same dirty-tree snapshot for all variants; baseline `cargo test --offline --release -p mote-core --lib`: 191 passed, 2 ignored.
- **Runner:** Three independent local Codex-agent tasks with the same prompt and default settings. Exact model identifier, interaction turns, token usage, and cost were not exposed. The agent service hit its usage limit before it returned formal reports.

## Outcome

All three variants found a working fix, added a regression, and passed the same complete `mote-core` library suite after the change. The compressed variant is selected for the main skill because it preserved the reviewed rule/control inventory and used the fewest measured prompt tokens.

| Variant | Skill tokens (cl100k_base) | Fix / regression | Core suite | Fix wall time |
|---|---:|---|---|---:|
| Prose v3.2 | 2,205 | Passed; regression checks large positive/negative values, observer/almanac equivalence, interval and non-finite edges. Its run log does not retain a pre-fix cargo invocation; the exact original function separately fails the frozen baseline reproducer. | 191 passed, 2 ignored | Not retained |
| Wren 3.2-wren.3 fixed | 2,077 | Regression explicitly failed before the patch (`1e20`: 100 vs -80), then passed; covers `Observer` and large finite values. | 191 passed, 2 ignored | Not retained |
| Compressed 3.2-wren.4 | 1,970 shipped (1,976 candidate) | Regression failed on the frozen original function and passed after; covers modulo equivalence, `Observer`, interval boundaries, tiny values, and finite extremes. | 191 passed, 2 ignored | Not retained |

The independent source-extraction reproducer from the frozen baseline fails at `1e20` (100 vs -80). The selected patch reduces modulo 360 before adjusting into the half-open interval. New observer checks show equivalent longitudes produce equal normalized observer coordinates. The bug affects almanac coordinates through `Observer::new`.

## Coverage and limits

All three runs used the same affected-unit suite and added regression. The orphan `crates/mote-tools` was explicitly checked in two captured runs; Cargo confirms it is excluded from the workspace and refuses to check it as a member. It remains untested, as do full workspace/render/game, GPU, and unattended application paths. Existing ignored tests remain ignored. No detector change was made.

The compressed candidate inventory contains 124 entries covering every `always`/`never`, flow action, branch, gate, and appendix requirement. Structural inventory counts and flow/parent relations match the fixed variant; manual review records lexical rewrites. This is review evidence, not proof of semantic equivalence. Model-token, dollar-cost, turn, and repair-loop comparisons are unavailable because the local agent service stopped at its usage limit. The three code fixes were valid; that limit affected measurement/report completeness, not test results.

## Selected change

`skills/technologic/SKILL.md` is now the compressed logic version, release `3.2-wren.4`. Its description includes routing phrases; shared-code impact search runs for Standard as well as Deep. Prose v3.2 is retained at `docs/technologic-prose-3.2.md`.
