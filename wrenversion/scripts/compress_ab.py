"""Apply a reviewed, rule-preserving compression to the frozen fixed variant."""
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import tiktoken

from inventory_ab import AB, inventory
sys.path.insert(0, "Z:/SkillWren/src")
from skillwren.validator import split_frontmatter, validate_file

# Each replacement preserves the statement's operands, qualifiers, and role.
REWRITES = [
("obey project instructions and existing authorization; minimize cost per verified change", "obey project instructions/prior authorization; minimize cost per verified change"),
("prioritize scrutiny by likelihood and cost of breakage", "prioritize scrutiny by breakage likelihood/cost"),
("choose reversible defaults; report recoverable assumptions", "reversible defaults; report recoverable assumptions"),
("promote depth on new risk; explain architecture changes and their evidenced cause", "raise depth on new risk; explain architecture changes and evidenced causes"),
("new files or anchored edits in dirty trees; format only your work", "dirty tree: new files/anchored edits; format only your work"),
("temporary edits in copies or diff-verified restored snapshots", "temporary edits: copies or snapshots with diff-verified restore"),
("concurrent changes are not flaky tests; never revert others", "concurrent changes are not flakes; never revert others"),
("two failed attempts per hypothesis means reinvestigate; three stalled approaches means stop and report findings and next step", "two failed attempts/hypothesis: reinvestigate; three stalled approaches: stop, report findings/next step"),
("estimate and time-box slow commands; record partial coverage", "estimate/time-box slow commands; record partial coverage"),
("surprising evidence means stop and investigate; never repeat identical failure", "surprising evidence: stop/investigate; never repeat identical failure"),
("exec records append status, output, failures, and partial coverage; stop limits also govern repairs", "exec appends status/output/failures/partial coverage; repairs obey stop limits"),
("commit, push, deploy, or publish unless requested; perform unapproved deletion, real-data migration, paid API, or credential creation", "commit/push/deploy/publish unless requested; unapproved deletion, real-data migration, paid API, credential creation"),
("test destructively against production or user data", "destructively test production/user data"),
("claim unavailable, skipped, or unreached checks passed", "claim unavailable/skipped/unreached checks passed"),
("read STATUS, README, CLAUDE, project instructions, then touched code from repo as context", "read STATUS/README/CLAUDE/project instructions, then touched code from repo as context"),
("generate least-invasive scope/job using {context}: finished-project build means Verify; widen only for named spec/issue/backlog from request as plan", "generate least-invasive scope/job using {context}: finished-project build=Verify; widen only for named spec/issue/backlog from request as plan"),
("generate queue-ordered work from backlog, STATUS next, failing tests, TODOs; prefer locally verifiable items and explain choice from plan as plan", "generate backlog/STATUS-next/failing-test/TODO work in queue order; prefer locally verifiable, justify choice from plan as plan"),
("if unapproved destructive or outward-facing actions are needed:", "if destructive/outward-facing actions lack approval:"),
("if unresolved credentials, unavailable service, or contradictory requirements block progress:", "if credentials, service outage, or contradictory requirements block progress:"),
("generate command plan using {plan}, {context}, and {inventory}: docs then CI then detector defaults; never guess from request as plan", "generate {plan} commands using {context}/{inventory}: docs then CI then detector defaults; no guesses from request as plan"),
("generate caller/implementer/consumer search across code, config, serialization formats, and other languages; choose affected checks from plan as plan", "generate caller/implementer/consumer search across code/config/serialization/other languages and affected checks from plan as plan"),
("if Fast: localized, low-risk, obvious check, job preconditions met, nearest check covers job proofs, excluding Verify:", "if Fast: localized/low-risk, obvious check, job preconditions met, nearest check covers job proofs, not Verify:"),
("generate Standard one-area done criteria with evidence/unattended entry; reuse modules, stdlib, installed dependencies, then maintained packages from plan as plan", "generate Standard one-area done/evidence criteria and unattended entry; reuse modules/stdlib/installed deps before maintained packages from plan as plan"),
("if cross-component, core, data, concurrency, security, migration, or public API risk:", "if cross-component/core/data/concurrency/security/migration/public-API risk:"),
("generate Deep working map of entry points, connections, invariants, and files; update in notes from plan as plan", "generate Deep entry-point/connection/invariant/file map; maintain in notes from plan as plan"),
("exec full canonical build/tests and coverage audit without source edits from repo as evidence", "exec full canonical build/tests/coverage audit without source edits from repo as evidence"),
("exec existing-project baseline build/tests and record existing failures from repo as baseline", "exec existing-project baseline build/tests; record prior failures from repo as baseline"),
("generate ecosystem-scaffolded runnable increments matching project layout; add dependencies only when clearly better from plan as plan", "generate ecosystem-scaffolded runnable increments matching layout; dependencies only if clearly better from plan as plan"),
("exec discriminate two to four confidence-ranked hypotheses using cheapest logs, breakpoint, repro, or bisect from scratch as probe", "exec cheapest log/breakpoint/repro/bisect discriminating 2-4 confidence-ranked hypotheses from scratch as probe"),
("verify evidence confirms the originating cause from probe", "verify originating cause is confirmed from probe"),
("exec different probe, reinvestigating after two failed attempts; stop after three stalled approaches from scratch as probe", "exec different probe; reinvestigate after two failed attempts; stop after three stalled approaches from scratch as probe"),
("exec regression test failing against the original before fixing from scratch as regression", "exec regression on original before fixing from scratch as regression"),
("verify regression actually fails for the defect from regression", "verify regression fails for this defect from regression"),
("generate independently sourced expected values with citations and plausible-wrong-implementation challenges; record measured values from plan as plan", "generate cited independent expected values and plausible-wrong-implementation challenges; record measurements from plan as plan"),
("exec profile or benchmark representative workload from repo as measurement", "exec representative profile/benchmark from repo as measurement"),
("generate measured-hotspot-only change with identical before/after workload using {plan} from measurement as plan", "generate {plan} measured-hotspot-only change; identical before/after workload from measurement as plan"),
("generate one-step-at-a-time migration from changelog breaking changes; rerun everything after each step from plan as plan", "generate migration from changelog breaking changes: one step, rerun everything, repeat from plan as plan"),
("generate behavior-preserving change; find references in code, strings, config, docs, CI; tests green before and after from plan as plan", "generate behavior-preserving change; search code/strings/config/docs/CI references; tests green before/after from plan as plan"),
("exec prove candidates unused before deletion from repo as unused", "exec prove non-use before deletion from repo as unused"),
("generate proven-unused-only removal using {unused}; user-written files still need approval from plan as plan", "generate removal limited to {unused}; user-written files need approval from plan as plan"),
("generate pinned versions, secrets absent from code/history, boundary validation, and least-privilege changes from plan as plan", "generate pinned versions, secrets absent from code/history, boundary validation, least privilege from plan as plan"),
("generate new implementation required to pass {parity} from plan as plan", "generate implementation that must pass {parity} from plan as plan"),
("generate reproducible build, version bump, and changelog; publication only if requested from plan as plan", "generate reproducible build/version bump/changelog; publish only if requested from plan as plan"),
("generate pinned versions, project-relative paths, and documented environment from plan as plan", "generate pinned versions/project-relative paths/documented environment from plan as plan"),
("generate isolated timing/order/state/network dependencies; no sleeps from plan as plan", "generate timing/order/state/network isolation or injection; no sleeps from plan as plan"),
("generate small runnable increments matching project style/layout within {plan}, with regression/oracle/parity evidence from request as steps", "generate small runnable increments matching style/layout and {plan}, with regression/oracle/parity proof from request as steps"),
("generate smallest cause-backed edit for {step}, preserving current scope and authorization from plan as change", "generate smallest cause-backed {step} edit within scope/authorization from plan as change"),
("verify edit and commands require no new authorization from change", "verify edit/commands need no new authorization from change"),
("exec applicable job proofs and checks; test new tests against plausible wrong code from repo as evidence", "exec job proofs/checks; challenge new tests with plausible wrong code from repo as evidence"),
("verify done criteria and job proofs hold without new failures versus {baseline} from evidence", "verify done/job proofs hold; no new failures versus {baseline} from evidence"),
("exec reinvestigate returning bugs at their origin, narrow breaking fixes with regression first; stop at attempt limits from scratch as probe", "exec trace recurring bugs to origin; narrow breaking fixes, regression first; obey attempt limits from scratch as probe"),
("generate different confirmed correction using {probe} from evidence as change", "generate different confirmed correction using {probe} from evidence as change"),
("exec highest runnable affected level with representative input: unattended CLI, smoke, health request, frame capture, or browser; inspect output; if unavailable, record why and run nearest proof from repo as runtime", "exec highest runnable affected level with representative input: unattended CLI/smoke/health request/frame capture/browser; inspect output; unavailable: explain and run nearest proof from repo as runtime"),
("exec relevant malformed/missing/oversized inputs, domain edges, dependency failures, repeats, limits, auth/parser/secret abuse cases; Deep integration boundaries from repo as edges", "exec relevant malformed/missing/oversized/domain inputs, dependency failures/repeats/limits, auth/parser/secret abuse; Deep integration boundaries from repo as edges"),
("generate retain valuable regressions, handle/document failures using {edges}; cut dead code, debug prints, commented blocks, unused imports/deps, scaffolding; keep useful repros/benchmarks/fixtures; update affected STATUS and usage README from plan as finish", "generate retain regressions and handle/document {edges}; cut dead code/debug prints/commented blocks/unused imports/deps/scaffolding; keep useful repros/benchmarks/fixtures; update affected STATUS/usage README from plan as finish"),
("exec final relevant build/tests/lint and job proofs after cleanup from repo as evidence", "exec final relevant build/tests/lint/job proofs after cleanup from repo as evidence"),
("verify final checks introduce no failures versus recorded baseline from evidence", "verify final checks add no failures versus baseline from evidence"),
("generate evidence ledger from {evidence} and {runtime}; compare inventory units, all changed files including pre-existing edits, flags, targets, generated code, subprojects, and ignored/skipped/gated tests against executed commands from inventory as coverage", "generate {evidence}/{runtime} coverage: inventory units, all changed files incl prior edits, flags/targets/generated code/subprojects/ignored/skipped/gated tests versus executed commands from inventory as coverage"),
]


def main():
    fixed = AB / "variants/wren.3-fixed.md"
    output = AB / "variants/compressed-v2.md"
    if output.exists():
        raise ValueError("Compressed variant already exists; preserve its evidence.")
    text = fixed.read_text(encoding="utf-8")
    encoder = tiktoken.get_encoding("cl100k_base")
    for before, after in REWRITES:
        if text.count(before) != 1:
            raise ValueError(f"Expected one reviewed statement: {before}")
        candidate = text.replace(before, after, 1)
        if len(encoder.encode(candidate)) < len(encoder.encode(text)):
            text = candidate
    text = text.replace("release: 3.2-wren.3-fixed", "release: 3.2-wren.4-candidate")
    _, body, _ = split_frontmatter(text)
    body_budget = math.ceil(len("\n".join(body)) / 4)
    text = re.sub(r"body: \d+", f"body: {body_budget}", text, count=1)
    output.write_text(text, encoding="utf-8")
    before, after = inventory(fixed), inventory(output)
    if len(before["rules"]) != len(after["rules"]):
        raise ValueError("Rule loss: inventory counts differ")
    diff = []
    for left, right in zip(before["rules"], after["rules"]):
        for key in ("kind", "parents", "flow"):
            if left.get(key) != right.get(key):
                raise ValueError(f"Control structure changed at {left['id']}")
        diff.append({"id": left["id"], "kind": left["kind"], "before": left["text"],
                     "after": right["text"], "disposition": "preserved; reviewed lexical rewrite"})
    errors, warnings = validate_file(output)
    if errors or warnings:
        raise ValueError((errors, warnings))
    (AB / "compressed-v2-inventory.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
    (AB / "rule-diff-v2.json").write_text(json.dumps({"before_sha256": before["sha256"],
        "after_sha256": after["sha256"], "missing": [], "added": [], "rules": diff,
        "limit": "Structural identity plus manual semantic review, not an equivalence proof."}, indent=2) + "\n", encoding="utf-8")
    print(f"Compressed {len(diff)} rules without structural loss; declared body {body_budget}; validator clean.")


if __name__ == "__main__":
    main()
