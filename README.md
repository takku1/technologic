# TECHNologic

> *Buy it, use it, break it, fix it.*

A [Claude Code](https://claude.com/claude-code) skill that takes a rough idea, spec, half-finished repo, or broken feature and drives it end to end: **understand the code, change it, prove the result.** It scales effort to risk (Fast / Standard / Deep) and asks as few questions as safety allows.

It covers building, fixing, speeding up, upgrading, refactoring and renaming, cleanup, hardening, porting, and releasing. It is not for design discussion, explaining code, or one-line edits.

## Status: logic release 3.2-wren.4

The main skill is now the compact SkillWren conversion of prose v3.2.
Three isolated Fix trials on the same frozen mote snapshot covered the
prose, routing/impact-fixed, and compressed variants.

| Path | Status |
|---|---|
| **Build / verify** an existing project | Field-tested on a Rust/Cargo workspace ([report](results/2026-10-20-mote-build.md)). Every finding from that run has been folded back into the skill. |
| **Validate / add tests** (*prove it*: cited reference values, every new test shown able to fail) | Field-tested on the same workspace, in a tree the user was editing ([report](results/2026-10-20-mote-trial-v3.1.md)). Findings folded back in v3.2. |
| **Fix** a bug (*break it, fix it*: hypothesis loop, the regression test must fail before the fix) | Field-tested on a real longitude-wrap defect; all three variants added passing regressions and passed mote-core (191 passed, 2 ignored). [A/B report](results/2026-10-21-mote-fix-ab.md) |
| **Speed up** (*faster*, but only when measured: before/after on the same workload) | Not yet run |
| **Clean up / refactor** (*cut it, rename it*: behavior must not change) | Not yet run |
| **Deep** (all *around the world*: cross-component work, a working map, integration checks) | Not yet run |

Both field tests so far are Rust. `detect_project.py` also claims to handle npm/pnpm/yarn, Python (uv/poetry/pip), Go, .NET, Maven/Gradle, CMake and Make/just, but those haven't had a real run yet. A run on any of them, especially one of the untested paths, is the most useful thing you can contribute.

## Plug it, play it (install)

The skill is the `skills/technologic/` folder. Copy it into your Claude Code skills directory:

```bash
git clone https://github.com/takku1/technologic.git
cp -r technologic/skills/technologic ~/.claude/skills/
```

```powershell
git clone https://github.com/takku1/technologic.git
Copy-Item -Recurse technologic\skills\technologic $HOME\.claude\skills\
```

For one project only, copy it to `<project>/.claude/skills/` instead. The helper script needs Python 3.8+ and has no dependencies (3.11+ also parses `pyproject.toml` / `Cargo.toml`).

## Work it (use)

Start a new Claude Code session, then either invoke it directly:

```
/technologic build mote
/technologic fix the crash when the save file is empty, and prove it
/technologic make chunk generation faster
```

or just ask in plain language ("get this working", "upgrade the deps", "rename X everywhere") and Claude will pick it up from the skill description.

Destructive or outward-facing actions (commits, pushes, deploys, deletions, migrations on real data, paid APIs) always need your approval.

You can also run the detector on its own:

```bash
python ~/.claude/skills/technologic/scripts/detect_project.py path/to/repo
```

It prints the stack, the commands the project defines, what CI runs, every buildable unit on disk, and where uncommitted changes are.

## Harder, better, faster, stronger (how it works)

- **Understand:** read the project's docs, detect the stack, take a baseline (build and test before touching anything), look for reuse, check what the change impacts.
- **Execute:** define "done" as evidence, build in runnable increments, test hypotheses before fixing, stay in scope, stop after repeated failed attempts.
- **Prove:** run the real program at the highest level that works unattended, try to break it, and check **coverage**: every buildable unit and changed file is either covered by something that ran or named as unverified.
- **Finish:** cut scaffolding, run everything again, update docs, and give a short report.

The full instructions are in [`skills/technologic/SKILL.md`](skills/technologic/SKILL.md). Current state and design decisions are in [`docs/STATUS.md`](docs/STATUS.md).

## Touch it, send it (contributing a field test)

1. Run the skill on a real task in your own project.
2. Write up what happened in the shape of the [mote report](results/2026-10-20-mote-build.md): the target and starting state, the outcome table, how each phase went, findings ranked by severity, and suggested fixes.
3. Open a PR adding it as `results/YYYY-MM-DD-<project>-<path>.md`, or open an issue with the same content.

Findings that generalize (a rule that would have caught the problem in any stack) are worth more than special cases for one ecosystem.

## Random access memories (layout)

```
skills/technologic/   the skill (SKILL.md + scripts/detect_project.py)
results/              field-test reports
docs/STATUS.md        current phase, decisions, what's deprecated
```

## License

[MIT](LICENSE). Use it, fork it, break it, fix it. Field tests and PRs welcome.

---

*Robots write the code. Every claim still needs evidence: human after all.*
