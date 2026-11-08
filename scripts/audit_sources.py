#!/usr/bin/env python3
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
tiers=json.loads((R/"assets/profile-index.json").read_text())
assert [len(tiers[x]) for x in ("minimal","balanced","max")]==[20,35,50]
assert set(tiers["minimal"])<=set(tiers["balanced"])<=set(tiers["max"])
for name in tiers["max"]:
    assert re.fullmatch(r"[a-z0-9-]+",name), name
    path=R/"assets/scaffold/.agents/skills"/name/"SKILL.md"
    assert path.is_file(),path
    data=path.read_text()
    assert data.startswith("---\n") and "name:" in data.split("---",2)[1],path
print("Audit OK: 50 built-in skills, 20/35/50 tiers")
