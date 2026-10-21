"""Freeze the dirty mote tree and skill inputs; never reset or edit mote."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AB = ROOT / "ab/2026-10-21"
MOTE = Path("Z:/voxelgame")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def prepare():
    if (AB / "protocol.json").exists():
        raise SystemExit("Snapshot already exists; preserve this run's starting state.")
    snapshot = AB / "snapshot"
    snapshot.mkdir()
    paths = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"],
                           cwd=MOTE, check=True, capture_output=True).stdout.split(b"\0")
    entries = {}
    for name in paths:
        if not name:
            continue
        relative = name.decode("utf-8")
        if relative.split("/")[0] in {"target", "saves", ".git", ".claude-flow", ".claude"}:
            continue
        source = MOTE / relative
        if not source.is_file():
            continue
        raw = source.read_bytes()
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        entries[relative] = sha(raw)
    variants = AB / "variants"
    variants.mkdir()
    prose = ROOT.parent / "skills/technologic/SKILL.md"
    logic = ROOT / "source/technologic.md"
    (variants / "prose-3.2.md").write_bytes(prose.read_bytes())
    (variants / "wren.3.md").write_bytes(logic.read_bytes())
    protocol = {
        "date": "2026-10-21", "live_tree": str(MOTE), "snapshot_files": entries,
        "head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=MOTE,
                               check=True, capture_output=True, text=True).stdout.strip(),
        "dirty_status": subprocess.run(["git", "status", "--short"], cwd=MOTE,
                                       check=True, capture_output=True, text=True).stdout,
        "prose_sha256": sha(prose.read_bytes()), "wren3_sha256": sha(logic.read_bytes()),
        "validator_sha256": sha(Path("Z:/SkillWren/src/skillwren/validator.py").read_bytes()),
        "detector_sha256": sha((prose.parent / "scripts/detect_project.py").read_bytes()),
        "snapshot_policy": "tracked plus nonignored untracked; excludes saves, target, git and agent config",
    }
    (AB / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    print(f"Frozen {len(entries)} files without changing the live tree.")


if __name__ == "__main__":
    prepare()
