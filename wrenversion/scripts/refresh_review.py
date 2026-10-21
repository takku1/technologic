"""Bind the final compact source to its preserved prose and reviewed rules."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
project = root.parent
original = project / 'docs/technologic-prose-3.2.md'
source = root / 'source/technologic.md'
audit_path = root / 'source/coverage.json'
source.write_bytes((project / 'skills/technologic/SKILL.md').read_bytes())
audit = json.loads(audit_path.read_text(encoding='utf-8'))
anchors = {
 'identity-purpose':['Risk-adaptive software lifecycle','minimize cost per verified change','Excludes pure design discussion'],
 'authority':['reversible defaults; report recoverable assumptions','ask user to approve destructive or outward-facing actions','credential creation'],
 'scope-queue':['finished-project build means Verify; widen only for named spec/issue/backlog','prefer locally verifiable, justify choice from plan'],
 'depth':['raise depth on new risk','if Fast:','Standard one-area','Deep entry-point/connection/invariant/file map'],
 'job-routing':['if Build:','if Verify:','if Fix:','if Release:'],
 'build':['ecosystem-scaffolded runnable increments'],
 'verify':['full canonical build/tests and coverage audit without source edits','Verify proposes Fix work without editing sources'],
 'fix-regression':['exec regression on original before fixing','verify regression fails for this defect'],
 'test-oracles':['cited independent expected values and plausible-wrong-implementation challenges','record measurements','challenge new tests with plausible wrong code'],
 'performance':['representative profile/benchmark','identical before/after workload','No measurement means no speed claim'],
 'upgrade':['migration from changelog breaking changes: one step, rerun everything, repeat'],
 'refactor':['behavior-preserving change; search code/strings/config/docs/CI references','tests green before/after'],
 'remove':['prove candidates unused before deletion','user-written files need approval'],
 'secure':['pinned versions, secrets absent from code/history, boundary validation, least privilege'],
 'port':['parity tests against old version','implementation that must pass'],
 'release':['reproducible build/version bump/changelog','publish only if requested'],
 'project-reading-inventory':['read STATUS/README/CLAUDE/project instructions','docs then CI then detector defaults; no guesses'],
 'unattended-entry':['unattended CLI/smoke/health request/frame capture/browser'],
 'baseline':['existing-project baseline build/tests and record existing failures'],
 'reuse':['reuse modules/stdlib/installed deps before maintained packages'],
 'impact-map':['caller/implementer/consumer search across code/config/serialization/other languages','affected checks'],
 'done-evidence':['Standard one-area done/evidence criteria','Compilation/type checks alone','never establish runtime correctness'],
 'increment-layout':['small runnable increments matching style/layout','dependencies only if clearly better'],
 'dirty-tree':['new files or anchored edits in dirty trees','never revert others'],
 'investigate':['two to four confidence-ranked hypotheses','verify originating cause is confirmed','smallest cause-backed'],
 'architecture-scope':['explain architecture changes and evidenced causes','raise depth on new risk'],
 'attempt-time-limits':['two failed attempts per hypothesis','three stalled approaches','estimate/time-box slow commands','repairs obey stop limits'],
 'ci-environment':['pinned versions/project-relative paths/documented environment'],
 'flakiness':['isolated timing/order/state/network dependencies','no sleeps'],
 'breaking-fix':['narrow breaking fixes, regression first'],
 'recurring-bug':['trace recurring bugs to origin'],
 'risk-weighted-proof':['prioritize scrutiny by breakage likelihood/cost'],
 'real-runtime-proof':['highest runnable affected level with representative input','unavailable: explain and run nearest proof'],
 'edge-integration-proof':['malformed/missing/oversized/domain inputs','auth/parser/secret abuse','Deep integration boundaries','destructively test production/user data'],
 'coverage-accounting':['all changed files incl prior edits','flags/targets/generated code/subprojects/ignored/skipped/gated tests','Cover leftovers'],
 'surprising-evidence':['surprising evidence means stop and investigate'],
 'finish-cleanup':['cut dead code/debug prints/commented blocks/unused imports/deps/scaffolding','final relevant build/tests/lint/job proofs after cleanup'],
 'final-baseline':['final checks add no failures versus baseline'],
 'affected-docs':['update affected STATUS/usage README'],
 'publication-authority':['commit/push/deploy/publish unless requested'],
 'report':['Done','Verified','Optimized','Remaining','short shape unless asked for detail']
}
text=source.read_text(encoding='utf-8')
for item in audit['requirements']:
    item['logic_contains']=anchors[item['id']]
    missing=[a for a in item['logic_contains'] if a not in text]
    if missing: raise SystemExit(f"{item['id']} anchors missing: {missing}")
audit['original_sha256']=hashlib.sha256(original.read_bytes()).hexdigest()
audit['logic_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
audit['review']='Manual line-span and control-flow inventory review for compact release 3.2-wren.4. Hashes, spans, and anchors verify bookkeeping; they do not prove semantic equivalence or model adherence.'
audit_path.write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f"Refreshed {len(audit['requirements'])} reviewed requirements")
