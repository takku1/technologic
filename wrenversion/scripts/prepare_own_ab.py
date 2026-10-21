"""Prepare independent local-agent trials without changing the live tree."""
from pathlib import Path
import shutil
import subprocess

base = Path(__file__).resolve().parents[1] / 'ab/2026-10-21'
for name, variant in {'prose': 'prose-3.2.md', 'fixed': 'wren.3-fixed.md', 'compressed': 'compressed-v2.md'}.items():
    target = base / 'runs' / ('own-' + name)
    if target.exists():
        raise SystemExit(f'Preserving existing run: {target}')
    shutil.copytree(base / 'snapshot', target)
    skill = target / '.benchmark-skill'
    (skill / 'scripts').mkdir(parents=True)
    shutil.copyfile(base / 'variants' / variant, skill / 'SKILL.md')
    shutil.copyfile(base.parents[2] / 'skills/technologic/scripts/detect_project.py', skill / 'scripts/detect_project.py')
    def git(*args):
        subprocess.run(['git', '-C', str(target), *args], check=True, capture_output=True)
    git('init', '-q')
    git('config', 'user.name', 'Local benchmark')
    git('config', 'user.email', 'benchmark@example.invalid')
    git('config', 'core.autocrlf', 'false')
    git('config', 'core.hooksPath', str(target / '.git/no-hooks'))
    git('add', '-A')
    git('commit', '-qm', 'Frozen dirty-tree snapshot')
    print(target)
