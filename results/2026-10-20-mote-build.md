# TECHNologic field test: "build mote"

> **Resolved in v3.1.** The fixes below were made general instead of case by case. Findings 1–2 became the *coverage* rule plus the detector's inventory of buildable units, CI commands and uncommitted changes. Finding 3 became the "least invasive reading" rule. Finding 5 became "find the unattended run". Findings 4 and 6 went in as suggested. See `docs/STATUS.md`.

- **Date:** 2026-10-20
- **Invocation:** `/technologic build mote`
- **Target:** `Z:\voxelgame`, a Rust Cargo workspace (mote-core, mote-render, mote-game) that is a procedural planet game.
- **Starting state:** branch `master` with a large uncommitted working tree: about 45 modified files and several new modules.
- **Model:** Claude Opus 5.5 in Claude Code on Windows 11, using Git Bash and PowerShell.

## Outcome

The run was a success. The workspace built, every test passed, and a headless run of the real game binary worked. No files were changed.

| Check | Command | Result |
|---|---|---|
| Build | `cargo build --release --workspace` | ok, 8 s (cached) |
| Tests | `cargo test --release --workspace` | 285 passed, 0 failed, 2 ignored |
| Format | `cargo fmt --check` | clean |
| Lint | `cargo clippy --release --workspace --all-targets` | ~26 style warnings, 0 errors |
| Real run | `mote --script "fwd:3,turn:90,fwd+run:2" --capture smoke.bmp` | ran on RTX 4090/Vulkan; walked 12 m; captured frame looked correct |

**Left open:** `crates/mote-tools` is on disk but is not a workspace member. It has uncommitted changes that no command above builds.

## How each phase went

| Phase | What the skill made happen | Verdict |
|---|---|---|
| Ask vs. act | Asked no questions, made no commits, changed no files. | Correct for this request |
| Depth | I effectively ran it at **Fast/Standard**: build, test, then run. | Appropriate |
| Understand | Ran `detect_project.py` and read `docs/STATUS.md`. | Useful, but see findings 1–2 |
| Baseline | The build-and-test run served as both baseline and result. | Fine for a build-only job |
| Prove: run it | The rule "type checks are not running it" pushed me past `cargo test` to a headless game run with a frame capture, which I then looked at. | **Strongest part of the skill** |
| Prove: break it | Not applicable; nothing was changed. | n/a |
| Finish/report | The four-line template kept the report short. | Good, see finding 4 |

## Findings

### 1. `detect_project.py` recommends `cargo build`, which skips crates when `default-members` is set (high)
mote's root `Cargo.toml` sets `default-members = ["crates/mote-game"]`. That means a bare `cargo build` or `cargo test` covers only the game crate and its dependencies. The script prints exactly those bare commands, so an agent that follows the skill's advice to "prefer those commands to guesses" would never test the render-only parts or the tests in the other crates. I added `--workspace` on my own judgment, not because the skill said to.

**Fix:** in `rust()`, if `workspace.default-members` exists, print `cargo build --workspace` / `cargo test --workspace` and say why.

### 2. The script doesn't notice crates that aren't workspace members (medium)
It printed "workspace: 3 members", which is true, but `crates/mote-tools/Cargo.toml` also exists. It has modified source files, and it fails `cargo check` with "may be fixable by adding to workspace.members". I found it by accident, because git status listed changes in it.

**Fix:** glob `**/Cargo.toml` (up to about two levels deep, skipping `target/`), compare against the members plus `exclude` list, and print `orphan crate: <path>` for any leftover. The same idea applies to npm/pnpm workspaces.

### 3. No rule for a vague verb on an existing project (medium)
On a finished project, "build X" could mean compile and verify it, or build out new features. The skill's "Build something new" row assumes a new project. I chose compile and verify, which turned out right, but by guesswork.

**Fix:** add a line under *When to ask vs. act* or *Adjust for the job*: "A bare 'build/run/check X' on an existing project means compile, test and run it, then report. Only treat it as feature work if a spec or backlog item is named."

### 4. The report template forces lines that may not apply (low)
`**Optimized:**` was empty filler on a build-only run.

**Fix:** "Omit **Optimized** when no performance work was done."

### 5. The real run deserves its own step for apps that have a headless mode (low, positive)
The headless capture was the most valuable evidence, because it proved the binary starts, the GPU path works, and the world builds. The skill only gets there through general advice ("the UI in a browser if one is available").

**Possible fix:** under *Understand*, have the agent look for headless, smoke or `--help` options (as mote's `--script`/`--capture` provide) and treat them as the preferred proof.

### 6. Minor notes
- Running the skill's Python script from the Bash tool on Windows worked fine. Nothing Windows-specific broke.
- The skill doesn't say whether lint warnings count against "done". I reported the clippy warnings without fixing them, which seems right for "build", but the *Done means* section could say "lint warnings that already existed are reported, not fixed, unless in scope."

## Suggested changes, by value

1. `detect_project.py`: use `--workspace` when `default-members` is set (finding 1).
2. `detect_project.py`: report orphan crates and packages (finding 2).
3. SKILL.md: a rule for "build X" on an existing project (finding 3).
4. SKILL.md: look for a headless or smoke mode as the preferred real run (finding 5).
5. SKILL.md: let the report skip the Optimized line; say how existing warnings are handled (findings 4 and 6).

## Next test runs worth doing
This run only covered the "Build/verify" path. The skill's riskier paths have not been tested yet:
- **Fix:** a real mote bug, to test the hypothesis loop and the "regression test fails before the fix" rule.
- **Speed up:** for example, vegetation chunk cost from mote's backlog, to test the "no measurement, no claim" rule.
- **Clean up:** the clippy warnings, to test the "behavior must not change" refactor rule with the tests as the guard.
- **Deep:** something that crosses the mote-core and mote-render boundary, to test the working map and integration checks.
