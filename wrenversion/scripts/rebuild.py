#!/usr/bin/env python3
"""Rebuild the TECHNologic SkillWren package from the current main skill."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

WREN = Path(__file__).resolve().parents[1]
PROJECT = WREN.parent
MAIN = PROJECT / "skills" / "technologic"
ORIGINAL = PROJECT / "docs" / "technologic-prose-3.2.md"
SOURCE = WREN / "source" / "technologic.md"
AUDIT = WREN / "source" / "coverage.json"
OUTPUT = WREN / "skills" / "technologic-logic"


def record(data):
    return {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "base64": base64.b64encode(data).decode("ascii")}


def validate_coverage(original, logic, audit):
    """Check review bookkeeping; this does not prove semantic equivalence."""
    if audit.get("original_sha256") != hashlib.sha256(original).hexdigest():
        raise ValueError("main skill changed: review the logic conversion and coverage map before rebuilding")
    if audit.get("logic_sha256") != hashlib.sha256(logic).hexdigest():
        raise ValueError("logic changed: update the reviewed coverage map before rebuilding")
    lines = original.decode("utf-8-sig").splitlines()
    text = logic.decode("utf-8-sig")
    covered, identifiers = set(), set()
    for item in audit.get("requirements", []):
        identifier = item.get("id")
        if not identifier or identifier in identifiers:
            raise ValueError("coverage map has a missing or duplicate requirement id")
        identifiers.add(identifier)
        start, end = item["original_lines"]
        if not 1 <= start <= end <= len(lines):
            raise ValueError(f"invalid original span: {identifier}")
        anchors = item.get("logic_contains", [])
        if not anchors or any(not anchor or anchor not in text for anchor in anchors):
            raise ValueError(f"missing logic coverage: {identifier}")
        covered.update(range(start, end + 1))
    missing = [number for number, line in enumerate(lines, 1) if line.strip() and number not in covered]
    if missing:
        raise ValueError(f"unmapped original lines: {missing}")


def render_package(output, skillwren_root, main=MAIN, source=SOURCE, audit_path=AUDIT):
    """Render into a new directory; source/main inputs are never modified."""
    skillwren_root = Path(skillwren_root).resolve()
    compiler_path = skillwren_root / "src"
    if not (compiler_path / "skillwren" / "compiler.py").is_file():
        raise ValueError(f"SkillWren compiler not found at {compiler_path}")
    sys.path.insert(0, str(compiler_path))
    from skillwren.compiler import build

    main = Path(main)
    skill_bytes = (main / "SKILL.md").read_bytes()
    original_bytes = ORIGINAL.read_bytes()
    detector_bytes = (main / "scripts" / "detect_project.py").read_bytes()
    source_bytes = Path(source).read_bytes()
    audit_bytes = Path(audit_path).read_bytes()
    audit = json.loads(audit_bytes)
    validate_coverage(original_bytes, source_bytes, audit)
    with tempfile.TemporaryDirectory(prefix="technologic-source-") as temporary:
        entry = Path(temporary) / "SKILL.md"
        entry.write_bytes(source_bytes)
        manifest = build(entry, output)
    output = Path(output)
    (output / "scripts").mkdir()
    (output / "scripts" / "detect_project.py").write_bytes(detector_bytes)
    manifest["sources"]["scripts/detect_project.py"] = record(detector_bytes)
    manifest["sources"]["audit/original-skill.md"] = record(original_bytes)
    manifest["sources"]["audit/coverage.json"] = record(audit_bytes)
    manifest["translation"] = {"kind": "reviewed-logic-conversion",
                               "original_in_prompt": False, "coverage": audit}
    manifest["upstream"] = {
        "skill": "docs/technologic-prose-3.2.md",
        "skill_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "detector_sha256": hashlib.sha256(detector_bytes).hexdigest(),
    }
    manifest["packaged_resources"] = {
        "scripts/detect_project.py": hashlib.sha256(detector_bytes).hexdigest()}
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skillwren-root", type=Path, default=PROJECT.parent / "SkillWren")
    parser.add_argument("--check", action="store_true", help="check reproducibility without changing files")
    args = parser.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix="technologic-wren-") as temporary:
            staged = Path(temporary) / "package"
            manifest = render_package(staged, args.skillwren_root)
            files = ["SKILL.md", "manifest.json", "scripts/detect_project.py"]
            if args.check:
                changed = [name for name in files if not (OUTPUT / name).is_file()
                           or (OUTPUT / name).read_bytes() != (staged / name).read_bytes()]
                if changed:
                    print("stale or missing build: " + ", ".join(changed), file=sys.stderr)
                    return 1
                print("reproducible: compact logic, reviewed source archive, and detector match")
            else:
                # Publish only the three managed artifacts; preserve other local files.
                for name in files:
                    target = OUTPUT / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(staged / name, target)
                print(f"rebuilt {OUTPUT}")
            for warning in manifest["warnings"]:
                print(f"warning {warning['rule']}: {warning['message']}")
    except (OSError, ValueError) as error:
        print(f"technologic rebuild: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
