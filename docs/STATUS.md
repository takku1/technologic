# STATUS

**Current Phase:** Logic release 3.2-wren.4 is installed as the main skill. Original prose v3.2 is preserved at `docs/technologic-prose-3.2.md`. The Fix path has been tested in three isolated variants against the same frozen mote bug; see `results/2026-10-21-mote-fix-ab.md`.

**Active Focus:** Speed up (measure first), Clean up (behavior unchanged), and Deep (working map and integration checks) still need field runs. A non-Rust stack is also untested. Cost and turn metrics were unavailable in the local Fix trials; the agent service hit its usage limit after code and test evidence was captured.

**Architecture Summary:** TECHNologic is a Claude Code skill in `skills/technologic/`: compact SkillWren `SKILL.md` plus a dependency-free `scripts/detect_project.py`. The logic uses existing SkillWren 0.5 syntax; the conversion inventory and prose source are archived outside the loaded instructions. `wrenversion/` holds the deterministic rebuild, reviewed coverage map, and A/B inputs. The detector inventories stack, commands, CI, buildable units, and uncommitted changes. Install by copying the folder to `~/.claude/skills/`. Public at github.com/takku1/technologic.

**Key Decisions:**
- **Tests must be shown able to fail** (v3.2, from the mote trial): a new *Validate / add tests* job requires cited reference values and a run against a wrong implementation. Also added: rules for shared or dirty trees (new files, format only your own files, no in-place temporary edits), an open-mandate rule (take work from the project's own queue), ignored/skipped tests counted as not run (the detector now lists them), time-boxing slow commands, and "the highest level your change can affect" for the real run.
- **Rules stay general** (v3.1, from the mote field test): no special cases for one ecosystem. A single *coverage* check (what exists vs. what ran) replaced the workspace and orphan-crate rules. The detector takes inventory instead of interpreting layouts, and never crashes on unreadable paths. Commands come from docs first, then CI, then stack defaults.
- **Risk-adaptive depth** (v3): Fast/Standard/Deep replaced the fixed pipeline. Bugs get hypothesis-driven investigation, performance work is measured first, and there are iteration limits. The metric is cost per *verified* change. No `verify_changes.py` / `change_impact.py`: `rg` handles impact search, and choosing what to verify is judgment.
- **Scope:** for building software, not Claude skills. The concept comes from the lifecycle verbs of Daft Punk's "Technologic", which became the job table. That reference stays in the README; the skill itself has none.
- Destructive or outward-facing actions (commits, pushes, deploys, deletions, real-data migrations, paid APIs) need approval.
- Field-test reports go in `results/`, and each finding goes back into the skill as a general rule.

**Deprecated/Legacy:** Prose v3.2 remains as provenance in `docs/technologic-prose-3.2.md`; the active source of truth is the compact logic skill. SkillWren rule inventories record a manual preservation review but do not prove semantic equivalence.

**Last Updated:** 2026-10-21
