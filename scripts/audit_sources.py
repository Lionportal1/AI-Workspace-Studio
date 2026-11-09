#!/usr/bin/env python3
"""Audit the bundled skill index and definitions without relying on assert."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
COUNTS = {"minimal": 20, "balanced": 35, "max": 50}
SKILL_NAME = re.compile(r"[a-z0-9-]+")


def audit(root=ROOT):
    """Raise RuntimeError for any missing, invalid or inconsistent skill tier."""
    root = Path(root)
    index = root / "assets/profile-index.json"
    if not index.is_file() or index.is_symlink():
        raise RuntimeError("Missing or unsafe bundled skill index: " + str(index))
    try:
        tiers = json.loads(index.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise RuntimeError("Invalid bundled skill index: %s" % exc) from exc
    if not isinstance(tiers, dict):
        raise RuntimeError("Bundled skill index must be a JSON object")

    for tier, expected in COUNTS.items():
        names = tiers.get(tier)
        if not isinstance(names, list) or len(names) != expected:
            raise RuntimeError("Invalid %s tier: expected %d skill entries" % (tier, expected))
        if len(set(name for name in names if isinstance(name, str))) != expected:
            raise RuntimeError("Duplicate or non-string skill name in %s tier" % tier)
        for name in names:
            if not SKILL_NAME.fullmatch(name):
                raise RuntimeError("Invalid skill identifier in %s tier: %r" % (tier, name))

    minimal = set(tiers["minimal"])
    balanced = set(tiers["balanced"])
    maximum = set(tiers["max"])
    if not minimal <= balanced or not balanced <= maximum:
        raise RuntimeError("Skill tiers must be nested: minimal <= balanced <= max")

    skills_dir = root / "assets/scaffold/.agents/skills"
    if not skills_dir.is_dir() or skills_dir.is_symlink():
        raise RuntimeError("Missing or unsafe built-in skills directory")
    for name in sorted(maximum):
        file = skills_dir / name / "SKILL.md"
        if not file.is_file() or file.is_symlink():
            raise RuntimeError("Missing or unsafe skill definition: " + str(file))
        try:
            data = file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise RuntimeError("Cannot read skill definition: %s (%s)" % (file, exc)) from exc
        if not data.startswith("---\n") or "---" not in data[4:]:
            raise RuntimeError("Invalid skill frontmatter: " + str(file))
        header = data.split("---", 2)[1]
        if not re.search(r"(?m)^name:\s*\S+", header):
            raise RuntimeError("Skill frontmatter missing name: " + str(file))

    actual = {p.parent.name for p in skills_dir.glob("*/SKILL.md")}
    if actual != maximum:
        raise RuntimeError("Skill index does not match bundled skills; missing=%r unexpected=%r" %
                           (sorted(maximum - actual), sorted(actual - maximum)))
    return True


def main():
    try:
        audit()
    except RuntimeError as exc:
        print("Audit FAILED: " + str(exc), file=sys.stderr)
        return 1
    print("Audit OK: 50 built-in skills, 20/35/50 tiers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
