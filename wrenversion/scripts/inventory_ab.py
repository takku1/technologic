"""Enumerate every operative rule and compare structurally matched compression."""
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, "Z:/SkillWren/src")
from skillwren.validator import build_tree, parse_fences, split_frontmatter, walk

AB = Path(__file__).resolve().parents[1] / "ab/2026-10-21"


def inventory(path):
    raw = Path(path).read_bytes()
    _, body, first = split_frontmatter(raw.decode("utf-8-sig"))
    flows, _, contract, appendix, diagnostics = parse_fences(body, first)
    if diagnostics:
        raise ValueError(diagnostics)
    rules = []
    section = None
    for line, text in contract["content"]:
        if text.strip() in ("always:", "never:"):
            section = text.strip()[:-1]
        elif section and text.strip():
            rules.append({"kind": section, "line": line, "text": text.strip()})
    for flow, block in flows.items():
        tree = build_tree(block["stmts"], [])
        for node in walk(tree):
            if node.kind == "root":
                continue
            parents = []
            parent = node.parent
            while parent and parent.kind != "root":
                parents.append(parent.kind)
                parent = parent.parent
            rules.append({"kind": node.kind, "verb": node.data if isinstance(node.data, str) else None,
                          "parents": parents, "flow": flow, "line": node.line, "text": node.text})
    for paragraph in re.split(r"\n\s*\n", appendix):
        if paragraph.strip() and not paragraph.lstrip().startswith("#"):
            for sentence in re.split(r"(?<=\.)\s+", " ".join(paragraph.split())):
                rules.append({"kind": "appendix", "text": sentence})
    for number, rule in enumerate(rules, 1):
        rule["id"] = f"R{number:03}"
    return {"sha256": hashlib.sha256(raw).hexdigest(), "rules": rules}


def freeze_fixed():
    variants = AB / "variants"
    path = variants / "wren.3-fixed.md"
    if path.exists():
        raise ValueError("Fixed variant is already frozen.")
    path.write_bytes((AB.parents[1] / "source/technologic.md").read_bytes())
    for label, skill in [("wren.3", variants / "wren.3.md"), ("wren.3-fixed", path)]:
        (AB / f"{label}-inventory.json").write_text(json.dumps(inventory(skill), indent=2) + "\n", encoding="utf-8")
    print(f"Frozen {len(inventory(path)['rules'])} fixed-variant rules before compression.")


if __name__ == "__main__":
    freeze_fixed()
