---
name: technologic
description: Risk-adaptive engine for the whole software lifecycle. Takes a rough idea, spec, half-finished repo, or broken feature and drives it end to end — understand, change, prove — scaling depth to the risk and asking as little as safety allows. Use whenever the user wants something built, finished, fixed, tested, sped up, upgraded, renamed, cleaned up, hardened, ported, or released and would rather Claude just do it - "build this", "make me an app that…", "get this working", "fix this and prove it works", "why is this broken", "make this faster", "upgrade the deps", "rename X everywhere", "rip this out into a library", "package it for release". Not for pure design discussion, explaining code, or one-line edits.
---

# TECHNologic

Understand it, change it, prove it. Spend effort where the risk is, and never claim a result without evidence. Optimize for cost per *verified* change: a short investigation that prevents a debugging spiral is cheap.

## Ask vs. act

| Situation | Action |
|---|---|
| Low-risk, reversible (names, layout, internal structure, library choice within the stack) | Decide and proceed. |
| Ambiguous but recoverable (scope edges, UI details, default config) | Pick a sensible default; state it in the report. |
| Destructive, outward-facing, or irreversible (deleting user files, commit/push, deploys, real-data migrations, paid APIs, new credentials) | Get approval first. |
| Unresolvable blocker (missing credentials, service down, contradictory requirements) | Stop and name exactly what's missing. |

**Read the request against the project's state.** Take the least invasive reading that fully satisfies it, and state it: "build X" on a finished project means build, test, run, report — not add features. Widen only when the request names more (a spec, an issue, a backlog item). With an **open mandate** ("fix things", "improve it"), take work from the project's own queue (backlog, STATUS "next", failing tests, TODOs) in its order, prefer items you can verify here, and say why you chose them.

## Depth

Classify by how much the task touches and what breaks if it's wrong. Re-classify upward as soon as evidence says it's bigger.

| Depth | When | Run |
|---|---|---|
| **Fast** | Localized, low-risk: typo, config value, one function with an obvious check | Inspect → edit → nearest check |
| **Standard** | A feature or bug in one area | Understand → Execute → Prove → Finish |
| **Deep** | Cross-component, shared core, data, concurrency, security, migrations, public APIs | Standard plus a working map, evidence per deliverable, and checks at integration boundaries |

## Job

| Job | What matters most |
|---|---|
| **Build** | Ecosystem scaffolder, small runnable increments, done defined before coding. |
| **Verify** | Build and test everything, check coverage, do the real run. Change nothing; anything broken becomes a Fix. |
| **Fix** | Investigate before editing; a regression test that fails before the fix and passes after. |
| **Validate / add tests** | Cite an independent source for each expected value. Show each new test can fail against a plausible wrong implementation (mutated input, the old version). Record measured values, not just pass/fail. |
| **Speed up** | Profile or benchmark first, change the measured hotspot, report before/after on the same workload. No measurement, no claim. |
| **Upgrade / switch** | One change at a time, read the changelog for breaking changes, rerun everything after each step. |
| **Rename / refactor** | Behavior unchanged. Find every reference: code, strings, configs, docs, CI. Tests green before and after. |
| **Clean up / remove** | Prove it's unused before deleting; confirm before deleting anything the user wrote. |
| **Secure** | Pin versions, secrets out of code and history, validate at boundaries, least privilege. |
| **Extract / port** | Parity tests on the old version first; the new one must pass them. |
| **Release** | Reproducible build, version bump, changelog; publish only on request. |

## Understand

Read `docs/STATUS.md`, `README`, `CLAUDE.md`, then only the code the task touches. Inventory the project:

```bash
python <this-skill>/scripts/detect_project.py [project-dir]
```

It lists the stack, defined commands, CI steps, buildable units, ignored/skipped tests, and uncommitted changes. Treat it as leads. Canonical commands come from the project's docs, then CI, then the printed defaults — never a guess.

- **Unattended run:** find how the program runs without a person — a CLI flag, headless or smoke mode, frame capture, `--dry-run`, a health endpoint, an example in README/tests/CI. It's the main proof under *Run it*.
- **Baseline** (Standard/Deep, existing code): run build and tests before touching anything and note what already fails.
- **Reuse:** existing modules, the standard library, installed dependencies, or a maintained package before new code.
- **Change impact** (shared code): find every caller, implementer and consumer, including config, serialization formats and other languages, and decide which need verifying.
- **Working map** (Deep): entry points, components and how they connect, invariants, files you expect to change. Update it as you learn; keep it in your notes unless the user wants it kept.

## Execute

**Define done** (Standard/Deep): each deliverable with its evidence — a test, a command and expected output, a screenshot, a request/response — so "it compiles" can't pass for "it works".

**Build in runnable increments** that match the surrounding code. Keep the layout organized (`src/`, `tests/`, `docs/`, `scripts/` or the stack's convention), not flat in the root. Add a dependency only when it clearly beats writing the code.

**Shared or dirty tree** (changes you didn't make, or someone editing now): put new work in new files where you can, and keep shared-file edits small and anchored. Format and lint-fix only your own files. Make temporary edits in a copy, or snapshot and verify the restore by diff. Never revert or reformat others' changes. A result that changes without your edits means someone else is working, not a flaky build.

**Investigate before fixing** when the cause isn't obvious: list 2–4 hypotheses with rough confidence, run the cheapest test that tells them apart (log line, breakpoint, minimal repro, bisect), repeat until evidence confirms one, then make the smallest fix for that cause. Editing on an unconfirmed hypothesis turns one bug into several.

**Stay in scope.** Change architecture only when evidence shows it's the cause — then say so and go Deep.

**Limits.** Two failed attempts on one hypothesis means it's probably wrong: go back to investigating. Three distinct approaches without progress: stop and report what you learned and what you'd try next. Never retry an identical failure. Time-box slow commands after estimating their cost; if one is cut off, report partial coverage ("65 of 128 seeds, no failures").

| Symptom | Usual cause | Fix |
|---|---|---|
| Fails in CI, works locally | Unpinned versions, hard-coded paths, env assumptions | Pin, use project-relative paths, document env vars |
| Flaky test | Timing, ordering, shared state, real network | Remove shared state or inject the dependency; no sleeps |
| Fix breaks something else | Change too wide, impact unchecked | Narrow it; regression test first |
| Bug keeps returning | Symptom patched | Trace to where the bad value originates |

## Prove

Scrutiny goes where breakage is likeliest and costliest.

**Run it** at the highest level that can run here and that your change can affect: the real build and tests, then the program through its unattended mode with representative input, a real request, or the UI in a browser. Look at whatever it produces. Type checks and "looks right" aren't running it. If something can't run here, say so and verify the nearest thing.

**Break it** where relevant: missing, malformed or oversized input, domain edge cases, dependency failure, repeated runs, resource limits, and for auth, parsing or secrets the obvious abuse cases. For Deep changes, exercise the integration boundaries, not just unit tests. Add tests for cases that matter; handle or document the known failure cases. Never test destructively against production or the user's real data.

**Check coverage.** A result covers only what the commands reached. Match **what exists** (buildable units, changed files — yours and already-uncommitted ones) against **what you ran**. Workspace defaults, feature flags, platform targets, generated code and sub-projects quietly narrow a command; ignored, skipped and feature-gated tests count as not run. Bring leftovers into scope or name them under **Remaining**.

**Escalate on surprise.** When evidence contradicts expectation — a test passes that should fail, a number moves the wrong way — stop and find out why. Your model of the system is wrong somewhere.

## Finish

- Cut dead code, debug prints, commented-out blocks, unused imports and dependencies, throwaway scaffolding. Keep valuable artifacts (repro script, benchmark, fixture) where they belong. Rerun tests after cutting.
- Run the full relevant build/test/lint once more. Nothing may fail that didn't fail at baseline; problems that were already there are reported, not fixed, unless in scope.
- Update docs the change affects (`docs/STATUS.md`, README if usage changed).
- Commit, push, or deploy only if asked.

Report in this shape, nothing longer unless asked (omit **Optimized** without performance work):

```
**Done:** <what was built, fixed, or checked, and where it lives>
**Verified:** <what was run and the result; what failed>
**Optimized:** <measured improvements>
**Remaining:** <limitations, unverified or unreached items — never reported as passing — or "none">
```
