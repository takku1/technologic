#!/usr/bin/env python3
"""Inventory a project: its stack, the commands it already defines, and what exists to be covered.

  detect_project.py [dir]   (default: current directory)

Output is a starting point, not ground truth. CI and the project's docs say which
commands are canonical; the inventory says what those commands must cover.
"""

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

LOCKFILES = [("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"),
             ("bun.lock", "bun"), ("package-lock.json", "npm")]
NPM_KEYS = ("dev", "start", "build", "test", "lint", "typecheck", "format")
DOCS = ["docs/STATUS.md", "README.md", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md"]
# Files that mark a buildable unit, in any ecosystem.
MANIFESTS = ("Cargo.toml", "package.json", "pyproject.toml", "setup.py", "go.mod", "pom.xml",
             "build.gradle", "build.gradle.kts", "CMakeLists.txt", "Makefile", "meson.build",
             "*.csproj", "*.fsproj", "Package.swift", "mix.exs", "Gemfile", "composer.json", "pubspec.yaml")
SKIP_DIRS = {"target", "node_modules", "dist", "build", "out", "vendor", "venv", "__pycache__"}


def load_toml(path):
    if not tomllib:
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def is_file(p):
    try:
        return p.is_file()
    except OSError:  # broken links, permission errors, odd filesystems
        return False


def subdirs(p):
    try:
        return [d for d in p.iterdir() if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith(".")]
    except OSError:
        return []


def node(root, out):
    pkg = root / "package.json"
    if not pkg.is_file():
        return
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        out.append(("node", "package.json unreadable"))
        return
    pm = next((m for f, m in LOCKFILES if (root / f).exists()), "npm")
    scripts = data.get("scripts", {})
    out.append(("node", f"package manager: {pm}"))
    for k in NPM_KEYS:
        if k in scripts:
            out.append(("node", f"{pm} run {k}    # {scripts[k]}"))
    if "workspaces" in data or (root / "pnpm-workspace.yaml").exists():
        out.append(("node", "monorepo: root scripts may not reach every package (see inventory)"))


def python(root, out):
    py = root / "pyproject.toml"
    if not (py.is_file() or (root / "setup.py").is_file() or (root / "requirements.txt").is_file()):
        return
    data = load_toml(py) if py.is_file() else {}
    tool = data.get("tool", {})
    runner = "uv run " if (root / "uv.lock").exists() else "poetry run " if "poetry" in tool else ""
    out.append(("python", f"env: {'uv' if runner.startswith('uv') else 'poetry' if runner else 'pip/venv'}"))
    text = "".join(p.read_text(encoding="utf-8", errors="ignore")
                   for p in (py, root / "requirements.txt", root / "requirements-dev.txt") if p.is_file())
    if "pytest" in tool or "pytest" in text or (root / "pytest.ini").exists():
        out.append(("python", f"{runner}pytest"))
    for linter in ("ruff", "mypy", "black"):
        if linter in tool or linter in text:
            out.append(("python", f"{runner}{linter}{' check .' if linter == 'ruff' else ' .'}"))
    for name in data.get("project", {}).get("scripts", {}):
        out.append(("python", f"{runner}{name}    # entry point"))


def rust(root, out):
    cargo = load_toml(root / "Cargo.toml") if (root / "Cargo.toml").is_file() else None
    if cargo is None:
        return
    # --workspace is harmless on a plain workspace and required when default-members or a root package narrow it.
    flag = " --workspace" if "workspace" in cargo else ""
    if (root / ".cargo" / "config.toml").exists() or (root / "xtask").is_dir():
        out.append(("rust", "custom build: see .cargo/config.toml or xtask/"))
    out += [("rust", c) for c in (f"cargo build{flag}", f"cargo test{flag}",
                                  f"cargo clippy{flag} --all-targets", "cargo fmt --all --check")]


def simple(root, out):
    if (root / "go.mod").is_file():
        out += [("go", "go build ./..."), ("go", "go test ./..."), ("go", "go vet ./...")]
    if list(root.glob("*.sln")) or list(root.glob("*.csproj")):
        out += [("dotnet", "dotnet build"), ("dotnet", "dotnet test")]
    if (root / "pom.xml").is_file():
        out += [("java", "mvn package"), ("java", "mvn test")]
    if (root / "build.gradle").is_file() or (root / "build.gradle.kts").is_file():
        gw = "./gradlew" if (root / "gradlew").exists() else "gradle"
        out += [("java", f"{gw} build"), ("java", f"{gw} test")]
    if (root / "CMakeLists.txt").is_file():
        out += [("cmake", "cmake -B build && cmake --build build"), ("cmake", "ctest --test-dir build")]
    for mk, tool in (("Makefile", "make"), ("justfile", "just"), ("Justfile", "just")):
        f = root / mk
        if f.is_file():
            targets = re.findall(r"^([A-Za-z][\w-]*):(?!=)", f.read_text(encoding="utf-8", errors="ignore"), re.M)
            out.append(("tasks", f"{tool}: {' '.join(dict.fromkeys(targets)) or '(no targets found)'}"))


def infra(root, out):
    for f in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml", "Dockerfile",
              ".env.example"):
        if (root / f).exists():
            out.append(("infra", f))
    ci = sorted((root / ".github" / "workflows").glob("*.y*ml")) + [p for p in (root / ".gitlab-ci.yml",) if p.is_file()]
    for f in ci:
        runs = re.findall(r"^\s*(?:-\s*)?(?:run|script):\s*[|>]?\s*(\S.*)?$", f.read_text(encoding="utf-8", errors="ignore"), re.M)
        out.append(("ci", f"{f.relative_to(root).as_posix()}: " + ("; ".join(r for r in runs if r)[:300] or "(multi-line steps)")))


def inventory(root, depth=3):
    """Every directory holding a build manifest, up to `depth` levels below root."""
    found, level = [], [root]
    for _ in range(depth):
        level = [d for p in level for d in subdirs(p)]
        for d in level:
            try:
                names = sorted({m.name for pat in MANIFESTS for m in d.glob(pat)})
            except OSError:
                continue
            if names:
                found.append(f"{d.relative_to(root).as_posix()} ({', '.join(names)})")
    return found


def dirty(root):
    """Uncommitted paths, grouped two levels deep."""
    try:
        res = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                             capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if res.returncode:
        return None
    paths = [l[3:].strip('"').split(" -> ")[-1] for l in res.stdout.splitlines() if l]
    return Counter("/".join(p.split("/")[:2]) for p in paths)


def main(argv):
    root = Path(argv[0] if argv else ".").resolve()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2
    out = []
    for detect in (node, python, rust, simple, infra):
        try:
            detect(root, out)
        except OSError as e:
            out.append((detect.__name__, f"skipped: {e}"))
    print(f"project: {root}")
    print("docs: " + (", ".join(d for d in DOCS if is_file(root / d)) or "none"))
    tests = [d for d in ("tests", "test", "__tests__", "spec") if (root / d).is_dir()]
    if tests:
        print("test dirs: " + ", ".join(tests))
    if out:
        for kind, line in out:
            print(f"[{kind}] {line}")
    else:
        top = sorted(p.name for p in subdirs(root))[:20]
        print("stack: not detected; top-level entries: " + (", ".join(top) or "(empty)"))
    units = inventory(root)
    if units:
        print("\nbuildable units below root (confirm the commands above reach each one):")
        print("\n".join(f"  {u}" for u in units[:40]))
        if len(units) > 40:
            print(f"  ... {len(units) - 40} more (often vendored or reference code; decide what's in scope)")
    changes = dirty(root)
    if changes is None:
        print("\ngit: no")
    elif changes:
        print(f"\nuncommitted: {sum(changes.values())} paths (confirm something you run covers each area):")
        print("\n".join(f"  {n:4} {d}" for d, n in changes.most_common(15)))
    else:
        print("\ngit: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
