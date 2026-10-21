---
name: technologic
description: Autonomous, risk-adaptive engine for the whole software lifecycle. Takes a rough idea, spec, half-finished repo, or broken feature and drives it end to end — understand the code, change it, and prove the result — scaling depth to the risk, with as few questions as safety allows. Covers building, debugging, upgrading, refactoring and renaming, performance work, cleanup, hardening, porting, and releasing. Use whenever the user wants something built, finished, fixed, sped up, upgraded, renamed, cleaned up, hardened, ported, or released and would rather Claude just do it - "build this", "make me an app that…", "get this working", "fix this and prove it works", "why is this broken", "make this faster", "upgrade the deps", "rename X everywhere", "rip this out into a library", "package it for release". Not for pure design discussion, explaining code, or one-line edits.
---

# TECHNologic

Understand it, change it, prove it. Take the user's idea or codebase to working software with minimal intervention, spending effort where the risk is and never claiming a result without evidence.

Optimize for cost per *verified* change, not for the fewest tokens: a short investigation that prevents a long debugging spiral is cheap.

## When to ask vs. act

| Situation | Action |
|---|---|
| Low-risk, reversible (names, file layout, internal structure, library choice within the existing stack) | Decide and proceed. |
| Ambiguous but recoverable (scope edges, UI details, default config) | Pick a sensible default, state it in the report. |
| Destructive, costly, outward-facing, or irreversible (deleting or overwriting user files, git commit/push, deploys, migrations on real data, paid APIs, new accounts or credentials) | Get approval first. |
| Blocker you can't resolve (missing credentials, unavailable service, contradictory requirements) | Stop and name exactly what's missing. |

**Read the request against the project's state.** When a request has more than one reading, take the least invasive one that fully satisfies it and state it in the report. For example, "build X" on a finished project means build, test, run and report, not add features. Widen only when the request names more: a spec, an issue, a backlog item.

## Pick a depth

Classify the task before starting — by how much it touches and what breaks if it's wrong — and run only the depth it needs. Re-classify upward the moment evidence shows the change is bigger or riskier than it looked.

| Depth | When | Run |
|---|---|---|
| **Fast** | Localized, low-risk: a typo, a config value, a one-function change with an obvious check | Inspect → edit → run the nearest check |
| **Standard** | A feature or bug in one area | Understand (baseline, reuse, impact) → execute in increments → prove (run, break the relevant edges) → finish |
| **Deep** | Cross-component, shared core code, data, concurrency, security, kernels, migrations, public APIs | Everything in Standard, plus a working map, a written plan with evidence per deliverable, and verification across the integration boundaries |

## Adjust for the job

| Job | What matters most |
|---|---|
| **Build** something new | Standard scaffolder, small runnable increments, define done before coding. |
| **Verify** an existing project | Build and test everything, check coverage, then the real run. Change nothing; anything broken becomes a Fix. |
| **Fix** a bug | Investigate (below) before editing; add a regression test that fails before the fix and passes after. |
| **Speed up** | Measure first with a profiler or benchmark; change the measured hotspot; report before/after numbers on the same workload. No measurement, no optimization claim. |
| **Upgrade / update / switch** (deps, runtime, framework) | One change at a time; read the changelog for breaking changes; rerun everything after each step. |
| **Rename / refactor / rewrite** | Behavior must not change. Find every reference — code, strings, configs, docs, CI, imports. Tests green before and after. |
| **Clean up / remove** | Prove something is unused (references, tests, runtime) before deleting; confirm before deleting anything the user wrote. |
| **Secure / lock down** | Pin versions, keep secrets out of code and history, validate inputs at boundaries, least privilege. |
| **Extract / port** | Parity tests on the old version first, then prove the new one passes the same tests. |
| **Package / release** | Reproducible build, version bump, changelog; publishing or sending anywhere only on request. |

## Understand

Read the project's own state first: `docs/STATUS.md`, `README`, `CLAUDE.md`, then only the code the task touches. Detect the stack and its real commands:

```bash
python <this-skill>/scripts/detect_project.py [project-dir]
```

It prints the stack, the commands the project defines, what CI runs, every buildable unit on disk, and where uncommitted changes are. Treat it as leads, not truth. Pick canonical commands in this order: the project's docs (often `CLAUDE.md`), then CI (CI is what the project actually trusts), then the stack defaults it prints. Never pick a guess.

**Find the unattended run:** look for how the program can run without a person driving it: a CLI flag, a headless, script, or smoke mode, screenshot or frame capture, `--dry-run`, a health endpoint, or an example in the README, tests or CI. That becomes the main proof under *Run it*.

**Baseline** (Standard and Deep, when changing existing code): run the build and tests before touching anything and note what already fails. Without it you can't tell a regression you caused from one that was already there.

**Reuse:** look for what already does the job — existing modules, the standard library, installed dependencies, a well-maintained package — before writing new code.

**Change impact** (whenever you touch shared code): search for every caller, implementer, and consumer of what you're changing — including config, serialization formats, and other languages in the repo — and decide which of them need verifying.

**Working map** (Deep): keep a short task-specific map — entry points, the components involved and how they connect, invariants that must hold, files you expect to change. Update it as you learn, and consult it instead of re-reading files. Keep it in your notes, not the repo, unless the user wants it kept.

## Execute

**Define done** (Standard and Deep): list the deliverables and the evidence for each — a test, a command and its expected output, a screenshot, a request/response. Deciding the evidence up front stops "it compiles" from passing for "it works".

**Build in increments** you can run, matching the surrounding code (naming, structure, comment density, error handling). Keep the layout organized — `src/`, `tests/`, `docs/`, `scripts/` or the stack's convention — rather than flat in the root. Add a dependency only when it clearly beats writing the code. For new projects use the ecosystem's scaffolder (`cargo new`, `npm create vite`, `uv init`, …).

**Investigate before fixing.** For any bug whose cause isn't obvious:
1. List the plausible hypotheses for the symptom (usually 2–4), each with a rough confidence.
2. Pick the cheapest test that discriminates between them — a log line, a breakpoint, a minimal repro, bisecting history or input.
3. Run it, update the confidences, repeat until one cause is confirmed by evidence.
4. Fix that cause with the smallest sufficient change.

Editing code on an unconfirmed hypothesis turns one bug into several.

**Stay in scope.** Don't change the architecture to fix a local bug unless evidence shows the architecture is the cause — and then say so and treat it as Deep. Fixing a button should never end in a new framework.

**Iteration limits.** If two attempts on the same hypothesis fail, the hypothesis is probably wrong: step back to investigation rather than trying a third variation. After three distinct approaches without progress, stop and report what you've learned and what you'd try next. Never retry an identical failure.

| Symptom | Usual cause | Fix |
|---|---|---|
| Works locally, fails in CI or elsewhere | Unpinned versions, hard-coded paths, env assumptions | Pin, resolve paths relative to the project, document env vars |
| Flaky test | Timing, ordering, shared state, real network | Remove the shared state or inject the dependency; don't add sleeps |
| Fix breaks something else | Change wider than needed, impact not checked | Narrow the change; add a regression test first |
| Same bug keeps returning | Symptom patched, not cause | Trace back to where the bad value originates |

## Prove

Weight verification by risk: the parts most likely to break, and most costly if they do, get the most scrutiny.

**Run it** — prove at the highest level that can run here: the real build and test suite, then the program itself, through its unattended mode, with representative input, a real request, or the UI in a browser. If the run produces anything (a screenshot, output file or response), look at it. Type checks and "looks right" are not running it. If something can't be run here, say so and verify the nearest thing you can.

**Break it** — probe past the happy path where relevant: missing, malformed, or oversized input; domain edge cases; dependency failure; repeated execution; resource limits; for auth, parsing, or secrets, the obvious abuse cases. For Deep changes, exercise the **integration boundaries** — the places your change meets other components, processes, or services — not just unit tests of the new code. Add tests for cases that matter so they stay fixed. Never test destructively against production systems or the user's real data.

**Check coverage** — a result only covers what the commands actually reached. Before you claim anything, match **what exists** (the buildable units, and the changed files, yours and any already uncommitted) against **what you ran**. Workspace defaults, feature flags, platform targets, generated code and separate sub-projects all quietly narrow what a command reaches. Anything left over is either brought into scope or named under **Remaining**. This one check covers every ecosystem's version of "the build skipped part of the code".

**Escalate on surprise.** When evidence contradicts what you expected — a test passes that should fail, a number moves the wrong way — stop and understand why before continuing. A surprise means your model of the system is wrong somewhere.

## Finish

- **Cut** dead code, debug prints, commented-out blocks, unused imports and dependencies, and throwaway scaffolding. Keep artifacts that carry value — a minimal repro script, a benchmark, a regression fixture — and put them where they belong (`tests/`, `scripts/`, `bench/`). Rerun tests after cutting.
- Run the full relevant test/lint/build one last time.
- Update docs the change affects — `docs/STATUS.md` if the project keeps one, the README if usage changed.
- Commit, push, or deploy only if the user asked.

Report in this shape, nothing longer unless asked:

```
**Done:** <what was built, fixed, or checked, and where it lives>
**Verified:** <what was run and the result; what failed>
**Optimized:** <measured improvements>
**Remaining:** <open limitations, unverified items, or "none">
```

Leave out **Optimized** if there was no performance work.

## Done means

- Every deliverable has evidence behind it, at the depth the risk called for.
- The real build and tests pass, or failures are reported with output — and none are new relative to the baseline.
- Problems that were already there (failing tests, warnings, code nothing builds) are reported, not fixed, unless they're in scope. Your change adds none.
- Known failure cases are handled or documented.
- No leftover scaffolding, debug code, or unneeded complexity.
- Anything you couldn't verify or reach is listed under **Remaining** as unverified — never reported as passing.
