# STATUS

**Current Phase:** v3.1. Has been field-tested once, on a build/verify run of mote (`results/2026-10-20-mote-build.md`), and tuned based on that run.

**Active Focus:** Test the paths no run has exercised yet: Fix (hypothesis loop and regression test), Speed up (measure first), Clean up (behavior unchanged), Deep (working map and integration checks).

**Architecture Summary:** TECHNologic is one Claude skill, `skills/technologic/`. `SKILL.md` covers risk-adaptive depth (Fast/Standard/Deep), an Understand → Execute → Prove → Finish flow, a job table, the ask-vs-act policy and the report format. `scripts/detect_project.py` has no dependencies. It prints a repo's stack, its real build/test/lint/run commands (workspace-wide where needed), an inventory of buildable units, CI commands, uncommitted-change areas, containers and which docs exist, so the skill uses the project's own commands instead of guessing. The installed copy lives at `~/.claude/skills/technologic/` and is copied from this repo.

**Key Decisions:**
- 2026-10-20 (v3.1, from the mote field test): **Rules stay general; no per-ecosystem special cases.** The mote findings were all one gap, results claimed for code the commands never reached, so the skill now has a single *coverage* rule: match what exists (buildable units plus changed files) against what was run, and name anything left over. `detect_project.py` takes inventory instead of interpreting layouts: it lists all buildable units in any ecosystem, the commands CI runs, and where uncommitted changes are; it doesn't crash on unreadable paths and caps long lists. Command priority is docs, then CI, then stack defaults. When a request has more than one reading, take the least invasive one that fully satisfies it. Prove at the highest level that runs unattended. Problems that already existed are reported, not fixed. Field-test reports live in `results/`.
- 2026-10-20 (v3): The fixed pipeline was replaced with risk-adaptive depth (Fast/Standard/Deep) and an Understand → Execute → Prove structure. Added hypothesis-driven investigation, change-impact checks, a working map for Deep tasks, profile-first performance work, iteration limits, a rule against architecture changes for local bugs, and keeping repro/benchmark artifacts. The success metric is cost per verified change, not token count. Decided against `verify_changes.py` and `change_impact.py`: impact analysis is a reference search (`rg` already does it), and choosing what to verify is a judgment call, not a script. No `references/` files until there's real content for them.
- 2026-10-20: The concept is the lifecycle verbs of a song lyric (buy/use/break/fix/upgrade/rename/lock/rip/burn/send/touch…), taken literally as software jobs. The skill gains a "job" table: build, fix, upgrade, refactor/rename, clean up, secure, extract/port, package/release. Every change to existing code starts with a baseline test run. The lyric text itself is not in the skill.
- 2026-10-20: The skill is for building projects and code, not skills. v1 had read the brainstorm's "Claude Skill Builder" subtitle literally.
- Destructive or outward-facing actions need approval: commits, pushes, deploys, deletions, real-data migrations and paid APIs.
- The trigger description stays clear of pure design discussion, explaining code and one-line edits.

**Deprecated/Legacy:** None kept. The v1 skill validator and the original brainstorm were deleted rather than archived; `SKILL.md` is the source of truth.

**Last Updated:** 2026-10-20
