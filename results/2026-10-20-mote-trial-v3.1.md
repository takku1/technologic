# TECHNologic field test 2: open-scope trial on mote (v3.1)

- **Date:** 2026-10-20
- **Invocation:** `/technologic trial run on mote: implement/fix things using the updated skill`
- **Target:** `Z:\voxelgame`, a Rust workspace for a procedural planet game. The working tree was dirty (86 uncommitted paths), and the user was editing it during the run.
- **Skill version:** v3.1 (after the fixes from [test 1](2026-10-20-mote-build.md))
- **Model:** Claude Opus 5.5 in Claude Code on Windows 11

## Outcome

| Task | Job type | Depth | Result |
|---|---|---|---|
| **A008: astronomy reference validation**, the next open item in mote's backlog | Build (validation tests) | Standard | 10 new tests, all passing, each shown to fail on a wrong model; docs updated |
| "NO LOOP FOUND" in a seed sweep | Fix (suspected) | Fast | Not a bug: documented behaviour. No change made |
| `crates/mote-tools` that nothing builds | Coverage | Fast | Retired on purpose (commit `df2ae60`); put under Remaining, not fixed |

**Files changed:** a new `crates/mote-core/tests/astronomy_reference.rs`, plus edits to `docs/current/astronomy.md` (a table of measured values in §10 and three status lines), `docs/current/backlog.md` (A008 set to Partial, with an evidence entry) and `docs/STATUS.md` (a key-decision line). I edited no source file that had uncommitted changes. Nothing was committed.

**Final checks:**
- `cargo test --release --workspace`: 295 passed, 0 failed, 2 ignored (the baseline was 285 plus the 10 new tests).
- The new file is rustfmt-clean, and clippy reports nothing in it.

**What the tests measured** (all within tolerance):
- The equation of time came out at -14.24 / +16.42 min, against USNO's -14.2 / +16.4.
- Perihelion fell on day 289.0 at 0.98330 AU, against Jan 3 at 0.98329 AU.
- Day length at 45 N came out at 15h37.1m and 8h46.0m, against 15h37m and 8h46m.
- The solar day was 235.90 s longer than the sidereal day, against 235.91 s.
- Polar insolation was 524.2 W/m2, and the south/north ratio 1.0673.

## How the v3.1 changes performed

| v3.1 change | What happened here | Verdict |
|---|---|---|
| Detector prints `--workspace` commands | Printed `cargo build/test --workspace` and `clippy --all-targets`. I used them as given. | **Fixed** |
| Detector lists buildable units and uncommitted areas | Listed `crates/mote-tools` among the units, and showed uncommitted changes in it and in `tools/`. | **Fixed**, and it surfaced the issue without help |
| Coverage rule | Made me account for mote-tools. Git history showed it was retired on purpose, so it went under Remaining instead of becoming a "fix". | Worked; it avoided re-adding a crate the user had dropped |
| Least-invasive reading | The request was broad ("implement/fix things"), so the rule applied only loosely. See finding 1. | Partly applicable |
| Find the unattended run | I already knew the headless mode. I skipped the game run because no runtime code changed. See finding 4. | Unclear for test-only changes |
| Problems already present: report, don't fix | I left the clippy style warnings and the retired crate alone. | Worked |
| Optional Optimized line | Not needed. | Fine |

## How the rest of the skill performed

- **Escalate on surprise was the most valuable rule this run.** All 10 new tests passed on the first try. I treated that as a surprise, and swapped two wrong orbit models into the test fixture: the old astronomy model, and a perturbed tilt and pole. Nine of the ten tests failed under at least one of them. The tenth, seek consistency, should hold for any orbit. Without that check, the tests could have been useless while looking good.
- **Investigate before fixing stopped a false fix.** Many seeds in the panic sweep printed "NO LOOP FOUND". Reading the function's doc comment and its callers took about a minute and showed that None is the documented result when continents block a circumnavigation. The only code that calls the function is the retired viewer and tests. So nothing was changed.
- **Define done up front made the write-up easy.** Deciding the evidence first ("each §10 quantity against a cited reference; record measured accuracy") meant the docs table came straight from the probe output.
- **Change impact was handled by isolation.** `orbit.rs` had uncommitted user edits, so the tests went in a new integration-test file that uses only the public API. Nothing shared was touched.

## Findings

### 1. No guidance for choosing work when the scope is open (medium)
"Implement/fix things" names no task. The least-invasive rule covers vague requests to *verify*, not free rein to *work*. I picked the next open item in the project's own backlog, in its dependency order (A008). That felt right, but it was my own judgment.

**Suggested rule:** "With an open mandate, take work from the project's own queue (backlog, STATUS 'next', failing tests, TODOs), in its order. Prefer items you can verify here, and say why you chose them."

### 2. Validation and test-writing work has no row in the job table, and no "make it fail" rule (high)
A008 was pure test-writing against reference values. The Fix row has "the regression test fails before the fix", but nothing says that *new tests must be shown able to fail*. I only did the mutation check because "escalate on surprise" fired on an all-green first run. If one test had failed first and been tuned to pass, that rule would never have fired.

**Suggested row:** "**Validate / add tests**: cite an independent source for each expected value; prove each test can fail by running it against a plausible wrong implementation (mutate an input, swap in the old model); record the measured values, not just pass/fail."

### 3. The coverage rule doesn't mention ignored or skipped tests (medium)
"2 ignored" is a narrowing of coverage just like workspace defaults are. Neither the detector nor the coverage rule mentions it. I only noticed because I went looking for bugs. Running one of the ignored tests took over 9 minutes and timed out, which is why it's ignored. Still, a claim of "all tests pass" doesn't cover it.

**Suggestion:** under Coverage, add "ignored, skipped, or feature-gated tests count as not run; name them or run them." The detector could count `#[ignore]`, `@skip`, `it.skip` and similar.

### 4. "Prove at the highest level" is ambiguous for test-only changes (low)
The skill says to prove at the highest level that can run here. For A008 I changed no runtime code, so a game run would have proved nothing new, and I skipped it. That seems right, but the text reads as if the game run is always required.

**Suggested wording:** "the highest level *your change can affect*."

### 5. No rules for working in a tree someone else is editing (high)
The user was editing during the run. `mote-game` recompiled between my builds, and test 1's report changed on disk. Several of my actions were risky in that setting, and only my own caution kept them safe:
- **Temporary mutation and probe edits:** I edited the test file in place for the mutation checks, with a backup and a restore verified by diff. A crash halfway would have left a mutated file behind.
- **Formatting:** `cargo fmt --all` would have reformatted the user's in-progress files. I ran `rustfmt` on my own file only.
- **Docs edits:** STATUS, backlog and astronomy.md are files the user edits too. I made small, anchored edits instead of rewrites.

**Suggested section:** "In a shared or dirty tree, put new work in new files where you can. Format and lint-fix only the files you changed. Do temporary edits in a copy or scratch location, or snapshot and verify the restore. Never revert or reformat changes you didn't make. If a build or test result changes between runs without your edits, assume someone else is working, not that the build is flaky."

### 6. Long diagnostics need a time budget (low)
The ignored sweep test runs for "minutes at Earth scale". I gave it about 10 minutes, and it was killed after 65 of its 128 seeds. The skill has iteration limits for attempts, but no guidance on time-boxing a single expensive command.

**Suggestion:** "Before a slow command, estimate its cost. Time-box it, and report partial coverage (here, 65 of 128 seeds with no panics) rather than none."

## Suggested changes, by value

1. Job row **Validate / add tests**, with the "prove each test can fail" rule (finding 2).
2. A section on shared or dirty working trees (finding 5).
3. Coverage: ignored and skipped tests count as not run; the detector counts them (finding 3).
4. Open-mandate rule: take work from the project's own queue (finding 1).
5. Wording: "the highest level your change can affect" (finding 4); time-box slow commands (finding 6).

## Next test runs worth doing

These paths are still untested:
- **Fix** with a real, reproducible bug: the hypothesis loop and a regression test that fails before the fix. Nothing broken turned up this run.
- **Speed up**: for example, vegetation chunk cost (backlog A065), for the "measure first" rule.
- **Deep**: a change across mote-core and mote-render, for the working map and the integration-boundary checks.
- **Rename/refactor**: for example, collapsing the clippy warnings with the tests as the guard, once the user's tree is quiet.
