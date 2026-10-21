---
skill: technologic-logic
name: technologic-logic
description: Risk-adaptive software lifecycle: build, finish, fix, verify, test, speed up, upgrade, rename/refactor, clean up, harden, extract/port, release. Use for "build this", "get this working", "fix this and prove it works", "rename X everywhere", "rip this out into a library". Scale effort to risk and require executed proof. Excludes pure design discussion, explaining code, one-line edits.
version: 0.5
release: 3.2-wren.4-candidate
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
budget: { header: 400, body: 2151 }
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
  prioritize scrutiny by breakage likelihood/cost
  reversible defaults; report recoverable assumptions
  raise depth on new risk; explain architecture changes and evidenced causes
  new files or anchored edits in dirty trees; format only your work
  temporary edits in copies or diff-verified restored snapshots
  concurrent changes are not flakes; never revert others
  two failed attempts per hypothesis means reinvestigate; three stalled approaches means stop and report findings and next step
  estimate/time-box slow commands; record partial coverage
  surprising evidence means stop and investigate; never repeat identical failure
  exec appends status/output/failures/partial coverage; repairs obey stop limits
never:
  commit/push/deploy/publish unless requested; unapproved deletion, real-data migration, paid API, credential creation
  destructively test production/user data
  claim unavailable, skipped, or unreached checks passed
```

```logic
deliver:
  require request exists
    otherwise:
      abort with "Supply a request."
  read STATUS/README/CLAUDE/project instructions, then touched code from repo as context
  generate least-invasive scope/job using {context}: finished-project build means Verify; widen only for named spec/issue/backlog from request as plan
  if open mandate:
    generate backlog/STATUS-next/failing-test/TODO work in queue order; prefer locally verifiable, justify choice from plan as plan
  if destructive/outward-facing actions lack approval:
    show plan
    ask user to approve destructive or outward-facing actions
    require confirmation
      otherwise:
        abort with "Declined; nothing changed."
  if credentials, service outage, or contradictory requirements block progress:
    abort with "Name exactly what is missing."
  exec python <this-skill>/scripts/detect_project.py <project> from detector as inventory
  generate {plan} commands using {context}/{inventory}: docs then CI then detector defaults; no guesses from request as plan
  generate coverage inventory from inventory as coverage
  if touching shared code:
    generate caller/implementer/consumer search across code/config/serialization/other languages and affected checks from plan as plan
  if Fast: localized, low-risk, obvious check, job preconditions met, nearest check covers job proofs, excluding Verify:
    generate minimal edit from plan as change
    write change with repo
    exec nearest relevant check from repo as evidence
    return to report
  generate Standard one-area done/evidence criteria and unattended entry; reuse modules/stdlib/installed deps before maintained packages from plan as plan
  if cross-component/core/data/concurrency/security/migration/public-API risk:
    generate Deep entry-point/connection/invariant/file map; maintain in notes from plan as plan
  if Verify:
    exec full canonical build/tests and coverage audit without source edits from repo as evidence
    return to run
  exec existing-project baseline build/tests and record existing failures from repo as baseline
  generate baseline-only evidence ledger from baseline as evidence
  if Build:
    generate ecosystem-scaffolded runnable increments matching layout; dependencies only if clearly better from plan as plan
  if Fix and cause unclear:
    exec discriminate two to four confidence-ranked hypotheses using cheapest logs, breakpoint, repro, or bisect from scratch as probe
    verify originating cause is confirmed from probe
      otherwise:
        exec different probe; reinvestigate after two failed attempts; stop after three stalled approaches from scratch as probe
        retry
  if Fix:
    exec regression on original before fixing from scratch as regression
    verify regression fails for this defect from regression
      otherwise:
        abort with "Regression did not detect the defect; investigate."
  if Validate or add tests:
    generate cited independent expected values and plausible-wrong-implementation challenges; record measurements from plan as plan
  if Speed up:
    exec representative profile/benchmark from repo as measurement
    generate {plan} measured-hotspot-only change; identical before/after workload from measurement as plan
  if Upgrade or switch:
    generate migration from changelog breaking changes: one step, rerun everything, repeat from plan as plan
  if Rename or refactor:
    generate behavior-preserving change; search code/strings/config/docs/CI references; tests green before/after from plan as plan
  if Clean up or remove:
    exec prove candidates unused before deletion from repo as unused
    generate removal limited to {unused}; user-written files need approval from plan as plan
  if Secure:
    generate pinned versions, secrets absent from code/history, boundary validation, least privilege from plan as plan
  if Extract or port:
    exec parity tests against old version from scratch as parity
    generate implementation that must pass {parity} from plan as plan
  if Release:
    generate reproducible build/version bump/changelog; publish only if requested from plan as plan
  if CI-only failure:
    generate pinned versions/project-relative paths/documented environment from plan as plan
  if flaky tests:
    generate isolated timing/order/state/network dependencies; no sleeps from plan as plan
  generate small runnable increments matching style/layout and {plan}, with regression/oracle/parity proof from request as steps
  for each steps as step:
    generate smallest cause-backed {step} edit within scope/authorization from plan as change
    verify edit and commands require no new authorization from change
      otherwise:
        abort with "Present concrete pending action for approval before continuing."
    write change with repo
    exec job proofs/checks; challenge new tests with plausible wrong code from repo as evidence
    verify done/job proofs hold; no new failures versus {baseline} from evidence
      otherwise:
        exec trace recurring bugs to origin; narrow breaking fixes, regression first; obey attempt limits from scratch as probe
        generate different confirmed correction using {probe} from evidence as change
        write change with repo
        exec applicable checks from repo as evidence
        retry
  label run:
  exec highest runnable affected level with representative input: unattended CLI/smoke/health request/frame capture/browser; inspect output; unavailable: explain and run nearest proof from repo as runtime
  if not Verify:
    exec relevant malformed/missing/oversized/domain inputs, dependency failures/repeats/limits, auth/parser/secret abuse; Deep integration boundaries from repo as edges
    generate retain regressions and handle/document {edges}; cut dead code/debug prints/commented blocks/unused imports/deps/scaffolding; keep useful repros/benchmarks/fixtures; update affected STATUS/usage README from plan as finish
    write finish with repo
    exec final relevant build/tests/lint/job proofs after cleanup from repo as evidence
    verify final checks add no failures versus baseline from evidence
      otherwise:
        generate bounded in-scope correction from evidence as finish
        write finish with repo
        exec final relevant checks from repo as evidence
        retry
  generate {evidence}/{runtime} coverage: inventory units, all changed files incl prior edits, flags/targets/generated code/subprojects/ignored/skipped/gated tests versus executed commands from inventory as coverage
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
