"""Install the audited A/B winner as the main technologic instruction file."""
from pathlib import Path
import hashlib
import json
import shutil

wren = Path(__file__).resolve().parents[1]
project = wren.parent
candidate = wren / 'ab/2026-10-21/variants/compressed-v2.md'
main = project / 'skills/technologic/SKILL.md'
archive = project / 'docs/technologic-prose-3.2.md'
raw = main.read_bytes()
if archive.exists() and archive.read_bytes() != raw:
    raise SystemExit('Prose archive exists with different bytes; refusing overwrite')
archive.parent.mkdir(parents=True, exist_ok=True)
archive.write_bytes(raw)
text = candidate.read_text(encoding='utf-8')
text = text.replace('skill: technologic-logic', 'skill: technologic', 1)
text = text.replace('name: technologic-logic', 'name: technologic', 1)
text = text.replace('release: 3.2-wren.4-candidate', 'release: 3.2-wren.4', 1)
main.write_text(text, encoding='utf-8', newline='\n')
print(json.dumps({'prose_sha256': hashlib.sha256(raw).hexdigest(),
                  'logic_sha256': hashlib.sha256(main.read_bytes()).hexdigest(),
                  'archive': str(archive), 'skill': str(main)}, indent=2))
