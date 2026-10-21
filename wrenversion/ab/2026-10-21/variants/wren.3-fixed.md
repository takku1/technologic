---
skill: technologic-logic
name: technologic-logic
description: Risk-adaptive software lifecycle: build, finish, fix, verify, test, speed up, upgrade, rename/refactor, clean up, harden, extract/port, release. Use for "build this", "get this working", "fix this and prove it works", "rename X everywhere", "rip this out into a library". Scale effort to risk and require executed proof. Excludes pure design discussion, explaining code, one-line edits.
version: 0.5
release: 3.2-wren.3-fixed
accepts:
  request: { type: Text, required: true }
produces:
  report: { type: Text }
owns-when: [user wants software changed or verified end to end]
requires:
  deliver: [request exists]
flows: [deliver]
authority:
  user-decides: [approve destructive or outward-facing actions]
  system-decides: [scope, depth, job, commands, evidence]
  system-may: []
  system-must-not: [invent proof, expand scope, overwrite others]
effects:
  reads: [repo]
  creates: [repo, scratch]
  mutates: [repo]
  executes: [repo, detector, scratch]
risk: medium
cost: moderate
budget: { header: 400, body: 2500 }
---

```contract
resources:
  repo:
    path: current or requested project
    access: read+write
    glob: "**"
  detector:
    path: scripts/detect_project.py
    access: read
    immutable: true
  scratch:
    path: disposable project copy
    access: read+create
always:
  obey project instructions and existing authorization; minimize cost per verified change
  prioritize scrutiny by likelihood and cost of breakage
  choose reversible defaults; report recoverable assumptions
  promote depth on new risk; explain architecture changes and their evidenced cause
  new files or anchored edits in dirty trees; format only your work
  temporary edits in copies or diff-verified restored snapshots
  concurrent changes are not flaky tests; never revert others
  two failed attempts per hypothesis means reinvestigate; three stalled approaches means stop and report findings and next step
  estimate and time-box slow commands; record partial coverage
  surprising evidence means stop and investigate; never repeat identical failure
  exec records append status, output, failures, and partial coverage; stop limits also govern repairs
never:
  commit, push, deploy, or publish unless requested; perform unapproved deletion, real-data migration, paid API, or credential creation
  test destructively against production or user data
  claim unavailable, skipped, or unreached checks passed
```

```logic
deliver:
  require request exists
    otherwise:
      abort with "Supply a request."
  read STATUS, README, CLAUDE, project instructions, then touched code from repo as context
  generate least-invasive scope/job using {context}: finished-project build means Verify; widen only for named spec/issue/backlog from request as plan
  if open mandate:
    generate queue-ordered work from backlog, STATUS next, failing tests, TODOs; prefer locally verifiable items and explain choice from plan as plan
  if unapproved destructive or outward-facing actions are needed:
    show plan
    ask user to approve destructive or outward-facing actions
    require confirmation
      otherwise:
        abort with "Declined; nothing changed."
  if unresolved credentials, unavailable service, or contradictory requirements block progress:
    abort with "Name exactly what is missing."
  exec python <this-skill>/scripts/detect_project.py <project> from detector as inventory
  generate command plan using {plan}, {context}, and {inventory}: docs then CI then detector defaults; never guess from request as plan
  generate coverage inventory from inventory as coverage
  if touching shared code:
    generate caller/implementer/consumer search across code, config, serialization formats, and other languages; choose affected checks from plan as plan
  if Fast: localized, low-risk, obvious check, job preconditions met, nearest check covers job proofs, excluding Verify:
    generate minimal edit from plan as change
    write change with repo
    exec nearest relevant check from repo as evidence
    return to report
  generate Standard one-area done criteria with evidence/unattended entry; reuse modules, stdlib, installed dependencies, then maintained packages from plan as plan
  if cross-component, core, data, concurrency, security, migration, or public API risk:
    generate Deep working map of entry points, connections, invariants, and files; update in notes from plan as plan
  if Verify:
    exec full canonical build/tests and coverage audit without source edits from repo as evidence
    return to run
  exec existing-project baseline build/tests and record existing failures from repo as baseline
  generate baseline-only evidence ledger from baseline as evidence
  if Build:
    generate ecosystem-scaffolded runnable increments matching project layout; add dependencies only when clearly better from plan as plan
  if Fix and cause unclear:
    exec discriminate two to four confidence-ranked hypotheses using cheapest logs, breakpoint, repro, or bisect from scratch as probe
    verify evidence confirms the originating cause from probe
      otherwise:
        exec different probe, reinvestigating after two failed attempts; stop after three stalled approaches from scratch as probe
        retry
  if Fix:
    exec regression test failing against the original before fixing from scratch as regression
    verify regression actually fails for the defect from regression
      otherwise:
        abort with "Regression did not detect the defect; investigate."
  if Validate or add tests:
    generate independently sourced expected values with citations and plausible-wrong-implementation challenges; record measured values from plan as plan
  if Speed up:
    exec profile or benchmark representative workload from repo as measurement
    generate measured-hotspot-only change with identical before/after workload using {plan} from measurement as plan
  if Upgrade or switch:
    generate one-step-at-a-time migration from changelog breaking changes; rerun everything after each step from plan as plan
  if Rename or refactor:
    generate behavior-preserving change; find references in code, strings, config, docs, CI; tests green before and after from plan as plan
  if Clean up or remove:
    exec prove candidates unused before deletion from repo as unused
    generate proven-unused-only removal using {unused}; user-written files still need approval from plan as plan
  if Secure:
    generate pinned versions, secrets absent from code/history, boundary validation, and least-privilege changes from plan as plan
  if Extract or port:
    exec parity tests against old version from scratch as parity
    generate new implementation required to pass {parity} from plan as plan
  if Release:
    generate reproducible build, version bump, and changelog; publication only if requested from plan as plan
  if CI-only failure:
    generate pinned versions, project-relative paths, and documented environment from plan as plan
  if flaky tests:
    generate isolated timing/order/state/network dependencies; no sleeps from plan as plan
  generate small runnable increments matching project style/layout within {plan}, with regression/oracle/parity evidence from request as steps
  for each steps as step:
    generate smallest cause-backed edit for {step}, preserving current scope and authorization from plan as change
    verify edit and commands require no new authorization from change
      otherwise:
        abort with "Present concrete pending action for approval before continuing."
    write change with repo
    exec applicable job proofs and checks; test new tests against plausible wrong code from repo as evidence
    verify done criteria and job proofs hold without new failures versus {baseline} from evidence
      otherwise:
        exec reinvestigate returning bugs at their origin, narrow breaking fixes with regression first; stop at attempt limits from scratch as probe
        generate different confirmed correction using {probe} from evidence as change
        write change with repo
        exec applicable checks from repo as evidence
        retry
  label run:
  exec highest runnable affected level with representative input: unattended CLI, smoke, health request, frame capture, or browser; inspect output; if unavailable, record why and run nearest proof from repo as runtime
  if not Verify:
    exec relevant malformed/missing/oversized inputs, domain edges, dependency failures, repeats, limits, auth/parser/secret abuse cases; Deep integration boundaries from repo as edges
    generate retain valuable regressions, handle/document failures using {edges}; cut dead code, debug prints, commented blocks, unused imports/deps, scaffolding; keep useful repros/benchmarks/fixtures; update affected STATUS and usage README from plan as finish
    write finish with repo
    exec final relevant build/tests/lint and job proofs after cleanup from repo as evidence
    verify final checks introduce no failures versus recorded baseline from evidence
      otherwise:
        generate bounded in-scope correction from evidence as finish
        write finish with repo
        exec final relevant checks from repo as evidence
        retry
  generate evidence ledger from {evidence} and {runtime}; compare inventory units, all changed files including pre-existing edits, flags, targets, generated code, subprojects, and ignored/skipped/gated tests against executed commands from inventory as coverage
  label report:
  generate report using {coverage} from evidence as report
  return report as report
```

## Appendix

Reports use available executed evidence only.
Name existing/new failures, unavailable runtime proof, assumptions, queue choice,
and every unreached item; never fix unrelated baseline failures. Cover leftovers
or name them. "Done" includes location; "Verified" includes results/failures;
"Optimized" requires matched measurements; "Remaining" lists limits or none.
Use this short shape unless asked for detail. Compilation/type checks alone
never establish runtime correctness. No measurement means no speed claim.
Verify proposes Fix work without editing sources. Late approval suspends the
pending action until an authorized user turn.
