# STATUS

**Current Phase:** v3.1. Has been field-tested once, on a build/verify run of mote (`results/2026-10-20-mote-build.md`), and tuned based on that run.

**Active Focus:** Test the paths no run has exercised yet: Fix (hypothesis loop and regression test), Speed up (measure first), Clean up (behavior unchanged), Deep (working map and integration checks).

**Architecture Summary:** TECHNologic is one Claude Code skill in `skills/technologic/`: `SKILL.md` plus a dependency-free `scripts/detect_project.py`. `SKILL.md` sets the depth (Fast/Standard/Deep), runs Understand → Execute → Prove → Finish, adjusts per job, and decides when to ask and when to act. The detector inventories a repo (stack, defined commands, CI steps, buildable units, uncommitted changes) so the skill uses the project's real commands and can check coverage. Install by copying the folder to `~/.claude/skills/`. Public at github.com/takku1/technologic.

**Key Decisions:**
- **Rules stay general** (v3.1, from the mote field test): no special cases for one ecosystem. A single *coverage* check (what exists vs. what ran) replaced the workspace and orphan-crate rules. The detector takes inventory instead of interpreting layouts, and never crashes on unreadable paths. Commands come from docs first, then CI, then stack defaults.
- **Risk-adaptive depth** (v3): Fast/Standard/Deep replaced the fixed pipeline. Bugs get hypothesis-driven investigation, performance work is measured first, and there are iteration limits. The metric is cost per *verified* change. No `verify_changes.py` / `change_impact.py`: `rg` handles impact search, and choosing what to verify is judgment.
- **Scope:** for building software, not Claude skills. The concept comes from the lifecycle verbs of Daft Punk's "Technologic", which became the job table. That reference stays in the README; the skill itself has none.
- Destructive or outward-facing actions (commits, pushes, deploys, deletions, real-data migrations, paid APIs) need approval.
- Field-test reports go in `results/`, and each finding goes back into the skill as a general rule.

**Deprecated/Legacy:** None kept. The v1 skill validator and the original brainstorm were deleted rather than archived; `SKILL.md` is the source of truth.

**Last Updated:** 2026-10-20
