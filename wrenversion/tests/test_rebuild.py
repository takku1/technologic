"""Offline evidence for retention, reproducibility, dispatch, and static gates."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

WREN = Path(__file__).resolve().parents[1]
PROJECT = WREN.parent
SKILLWREN = PROJECT.parent / "SkillWren"
sys.path.insert(0, str(SKILLWREN / "src"))
from skillwren.validator import (build_cfg, build_tree, parse_fences, split_frontmatter,
                                 validate_file)

spec = importlib.util.spec_from_file_location("technologic_rebuild", WREN / "scripts/rebuild.py")
rebuild = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rebuild)


def trees(text):
    _, body, first = split_frontmatter(text)
    logics, _, _, _, diagnostics = parse_fences(body, first)
    if diagnostics:
        raise AssertionError(diagnostics)
    return {name: build_tree(block["stmts"], []) for name, block in logics.items()}


def scenario_actions(text, job, fast=False):
    """Explore CFG branches under explicit job/depth assumptions, not an LLM."""
    root = trees(text)["deliver"]
    successors, _ = build_cfg(root, [], [])
    seen, pending, actions = set(), [root.children[0]], []
    while pending:
        node = pending.pop()
        if node in seen or node not in successors:
            continue
        seen.add(node)
        if node.kind == "action":
            actions.append(node)
        edges = successors[node]
        decision = None
        if node.kind == "branch":
            if node.text == "if Verify:":
                decision = job == "Verify"
            elif node.text == "if not Verify:":
                decision = job != "Verify"
            elif node.text.startswith("if Fast:"):
                decision = fast and job != "Verify"
        pending.extend(edges if decision is None else [edges[0 if decision else 1]])
    return actions


class TestPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.output = cls.root / "package"
        cls.before = {name: (rebuild.MAIN / name).read_bytes()
                      for name in ("SKILL.md", "scripts/detect_project.py")}
        cls.original = rebuild.ORIGINAL.read_bytes()
        cls.manifest = rebuild.render_package(cls.output, SKILLWREN)
        cls.text = (cls.output / "SKILL.md").read_text(encoding="utf-8")

    def test_main_inputs_are_unchanged(self):
        for name, original in self.before.items():
            self.assertEqual((rebuild.MAIN / name).read_bytes(), original)

    def test_original_is_archived_outside_the_prompt(self):
        compiled = (self.output / "SKILL.md").read_bytes()
        self.assertEqual(self.manifest["contexts"], [])
        self.assertNotIn(self.original, compiled)
        self.assertEqual(base64.b64decode(self.manifest["sources"]["audit/original-skill.md"]["base64"]),
                         self.original)

    def test_detector_is_exact_and_archived(self):
        actual = (self.output / "scripts/detect_project.py").read_bytes()
        self.assertEqual(actual, self.before["scripts/detect_project.py"])
        self.assertEqual(base64.b64decode(self.manifest["sources"]["scripts/detect_project.py"]["base64"]), actual)

    def test_output_hash_is_correct(self):
        self.assertEqual(self.manifest["output_sha256"], hashlib.sha256(
            (self.output / "SKILL.md").read_bytes()).hexdigest())

    def test_static_validation_has_no_errors_or_warnings(self):
        errors, warnings = validate_file(self.output / "SKILL.md")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_rebuild_is_deterministic(self):
        another = self.root / "another"
        rebuild.render_package(another, SKILLWREN)
        for name in ("SKILL.md", "manifest.json", "scripts/detect_project.py"):
            self.assertEqual((another / name).read_bytes(), (self.output / name).read_bytes())

    def test_verify_never_calls_a_source_writing_flow(self):
        actions = scenario_actions(self.text, "Verify")
        self.assertFalse({"write", "save"} & {node.data for node in actions})

    def test_verify_guard_detects_an_accidental_write(self):
        changed = self.text.replace(
            "  if Verify:\n", "  if Verify:\n    write plan with repo\n", 1)
        actions = scenario_actions(changed, "Verify")
        self.assertIn("write", {node.data for node in actions})

    def test_fast_route_skips_baseline_and_full_pipeline(self):
        actions = scenario_actions(self.text, "Build", fast=True)
        executions = [node.text for node in actions if node.data == "exec"]
        self.assertEqual(len(executions), 2)  # Inventory and nearest check only.
        self.assertFalse(any("baseline" in text for text in executions))

    def test_fast_guard_detects_removed_early_return(self):
        changed = self.text.replace("    return to report\n", "", 1)
        actions = scenario_actions(changed, "Build", fast=True)
        self.assertTrue(any(node.data == "exec" and "baseline" in node.text for node in actions))

    def test_protected_context_mutation_is_rejected(self):
        broken = self.text.replace("write change with repo", "write change with detector", 1)
        path = self.root / "immutable.md"
        path.write_text(broken, encoding="utf-8")
        errors, _ = validate_file(path)
        self.assertIn("E3", {error.rule for error in errors})

    def test_unconfirmed_approval_is_rejected(self):
        broken = self.text.replace("    ask user to approve destructive or outward-facing actions\n", "", 1)
        path = self.root / "approval.md"
        path.write_text(broken, encoding="utf-8")
        errors, _ = validate_file(path)
        self.assertIn("A2", {error.rule for error in errors})

    def test_detector_runs_on_the_sample_project(self):
        result = subprocess.run([sys.executable, str(self.output / "scripts/detect_project.py"),
                                 str(WREN / "tests/sample-project")],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(WREN / "tests/sample-project"), result.stdout)
        self.assertIn("test dirs: tests", result.stdout)

    def test_changed_original_requires_a_new_translation_review(self):
        new_bytes = self.original + b"\nPreserve this newly added requirement.\n"
        audit = json.loads(rebuild.AUDIT.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "main skill changed"):
            rebuild.validate_coverage(new_bytes, rebuild.SOURCE.read_bytes(), audit)

    def test_unmapped_original_requirement_fails_review_check(self):
        audit = json.loads(rebuild.AUDIT.read_text(encoding="utf-8"))
        audit["requirements"] = [item for item in audit["requirements"] if item["id"] != "performance"]
        with self.assertRaisesRegex(ValueError, "unmapped original"):
            rebuild.validate_coverage(self.original, rebuild.SOURCE.read_bytes(), audit)

    def test_changed_logic_requires_review(self):
        audit = json.loads(rebuild.AUDIT.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "logic changed"):
            rebuild.validate_coverage(self.original, rebuild.SOURCE.read_bytes() + b"changed", audit)

    def test_prompt_tokens_are_below_original(self):
        try:
            import tiktoken
        except ImportError:
            self.skipTest("Optional tiktoken is required for the exact token regression")
        encoder = tiktoken.get_encoding("cl100k_base")
        original = len(encoder.encode(self.original.decode("utf-8-sig")))
        compiled = len(encoder.encode(self.text))
        self.assertLess(compiled, original)


if __name__ == "__main__":
    unittest.main()
