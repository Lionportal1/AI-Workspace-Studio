"""Traceable, non-executing community skill import and read-only inventory.

A cloned SKILL.md is only a copied definition, not a native plugin or proof
that a coding agent has discovered or activated the skill.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

MANIFEST_PATH = ".agents/skill-sources.lock.json"
SCHEMA_VERSION = 2
VALID_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")


def skill_path(name):
    return ".agents/skills/%s/SKILL.md" % name


def source_title(vendor):
    return {"superpowers": "Superpowers", "caveman": "Caveman",
            "matt": "Matt Pocock", "vercel": "Vercel", "anthropic": "Anthropic",
            "copilot": "Awesome Copilot", "julius": "Julius"}.get(
                vendor, vendor.replace("-", " ").title())


def _safe_parent(workspace, target):
    if workspace.is_symlink():
        raise RuntimeError("Refusing symlinked workspace")
    current = workspace
    for name in target.relative_to(workspace).parts:
        current = current / name
        if current.is_symlink():
            raise RuntimeError("Refusing symlinked import path: " + str(current))


def read_manifest(workspace):
    path = workspace / MANIFEST_PATH
    _safe_parent(workspace, path)
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "sources": []}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise RuntimeError("Invalid community skill manifest: %s" % exc) from exc
    if not isinstance(document, dict) or not isinstance(document.get("sources"), list):
        raise RuntimeError("Community skill manifest must contain a sources array")
    if document.get("schema_version") == SCHEMA_VERSION:
        return document
    if document.get("schema_version") == 1:
        sources = []
        for old in document["sources"]:
            if not isinstance(old, dict):
                raise RuntimeError("Invalid legacy skill source entry")
            vendor = old.get("vendor", "unknown")
            if not isinstance(vendor, str):
                raise RuntimeError("Invalid legacy vendor name")
            names = old.get("new_skills_copied", [])
            if not isinstance(names, list):
                raise RuntimeError("Invalid legacy skill inventory")
            skills = []
            for name in names:
                if not isinstance(name, str) or not VALID_NAME.fullmatch(name):
                    raise RuntimeError("Invalid legacy skill name")
                skills.append({"name": name, "display_name": source_title(vendor) + " / " + name,
                               "installed_path": skill_path(name), "source_path": None,
                               "status": "previously_recorded", "license": "unverified",
                               "sha256": None})
            sources.append({"vendor": vendor, "url": old.get("url"),
                            "commit": old.get("commit"), "fetched": None,
                            "status": "legacy", "reason": "Imported with old v1 record; provenance incomplete",
                            "skills": skills})
        return {"schema_version": SCHEMA_VERSION, "sources": sources}
    raise RuntimeError("Unsupported community skill manifest version")


def _write_manifest(workspace, document):
    target = workspace / MANIFEST_PATH
    _safe_parent(workspace, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".skill-sources-", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _frontmatter(skill_file):
    try:
        data = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, "Cannot read SKILL.md: %s" % exc
    if not data.startswith("---\n") or "\n---" not in data[4:]:
        return None, "Missing YAML frontmatter in SKILL.md"
    header = data.split("---", 2)[1]
    fields = {}
    for line in header.splitlines():
        match = re.match(r"^([a-zA-Z][a-zA-Z-]*):\s*(.*?)\s*$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip("\"'")
    name = fields.get("name")
    description = fields.get("description")
    if not name or not VALID_NAME.fullmatch(name):
        return None, "Missing or invalid frontmatter name"
    if not description:
        return None, "Missing frontmatter description"
    if description in ("|", ">", "|-", ">-", "|+", ">+"):
        # Folded/literal YAML block scalars are common in published skill sets.
        # Require a nonempty indented continuation without evaluating YAML.
        lines = header.splitlines()
        position = next((i for i, line in enumerate(lines)
                         if re.match(r"^description:\\s*[|>][+-]?\\s*$", line)), None)
        if position is None:
            return None, "Malformed frontmatter description block"
        continuation = []
        for line in lines[position + 1:]:
            if line and not line[0].isspace():
                break
            continuation.append(line)
        if not any(line.strip() for line in continuation):
            return None, "Empty frontmatter description block"
    if name != skill_file.parent.name:
        return None, "Frontmatter name differs from skill folder"
    return fields, None


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _counts(skills):
    categories = ("copied", "unchanged", "preserved", "conflict", "invalid", "failed")
    counts = {key: sum(skill["status"] == key for skill in skills) for key in categories}
    counts["discovered"] = len(skills)
    counts["verified"] = sum(skill.get("validated", False) for skill in skills)
    return counts


def _source_result(vendor, url, subdir):
    return {"vendor": vendor, "url": url, "subdir": subdir, "requested": True,
            "commit": None, "fetched": False, "status": "failed", "reason": None,
            "skills": [], "counts": _counts([])}


def _import_source(workspace, dest, vendor, url, subdir, previous):
    result = _source_result(vendor, url, subdir)
    skills = result["skills"]
    source = dest / subdir
    if source.is_symlink() or not source.is_dir():
        result["reason"] = "Missing or unsafe skills directory: " + subdir
        return result
    license_candidates = [p for p in dest.iterdir()
                          if p.is_file() and not p.is_symlink()
                          and p.name.lower().startswith(("license", "licence", "copying"))]
    license_file = sorted(license_candidates)[0].name if license_candidates else None
    found = sorted(source.rglob("SKILL.md"))
    if not found:
        result["reason"] = "No SKILL.md files found under " + subdir
        return result

    known = {s.get("name"): s for s in previous.get("skills", [])
             if isinstance(s, dict) and isinstance(s.get("name"), str)}
    used = set()
    for file in found:
        folder, name = file.parent, file.parent.name
        record = {"name": name, "display_name": source_title(vendor) + " / " + name,
                  "source_path": file.relative_to(dest).as_posix(),
                  "installed_path": skill_path(name),
                  "status": "invalid", "reason": None, "license": "unverified",
                  "license_file": license_file, "sha256": None, "validated": False}
        skills.append(record)
        if not VALID_NAME.fullmatch(name):
            record["reason"] = "Unsafe or unsupported skill folder name"
            continue
        if name in used:
            record.update(status="conflict", reason="Duplicate name within the same source")
            continue
        used.add(name)
        nested = folder.relative_to(dest).parts
        parts = [dest.joinpath(*nested[:i]) for i in range(1, len(nested) + 1)]
        if file.is_symlink() or any(p.is_symlink() for p in parts) or any(
                p.is_symlink() for p in folder.rglob("*")):
            record["reason"] = "Symlink in source skill directory"
            continue
        fields, invalid = _frontmatter(file)
        if invalid:
            record["reason"] = invalid
            continue
        record["license"] = fields.get("license", "unverified") or "unverified"
        record["validated"] = True
        digest = _digest(file)
        target = workspace / record["installed_path"]
        destination = target.parent
        _safe_parent(workspace, destination)
        if destination.exists():
            old = known.get(name)
            if old and old.get("installed_path") == record["installed_path"]:
                if target.is_file() and not target.is_symlink() and old.get("sha256") == _digest(target):
                    record["status"] = "unchanged" if digest == _digest(target) else "preserved"
                    record["reason"] = None if record["status"] == "unchanged" else "Upstream differs; installed version preserved"
                else:
                    record.update(status="preserved", reason="Existing skill or local edits preserved")
                record["sha256"] = old.get("sha256")
            else:
                record.update(status="conflict", reason="Destination already exists (another source or built-in skill)")
            continue
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(folder, destination, symlinks=False)
        except (OSError, shutil.Error) as exc:
            if destination.exists():
                shutil.rmtree(destination)
            record.update(status="failed", reason="Unable to copy skill: %s" % exc)
            continue
        record.update(status="copied", reason=None, sha256=digest)

    result["counts"] = _counts(skills)
    good = sum(result["counts"][key] for key in ("copied", "unchanged", "preserved"))
    bad = sum(result["counts"][key] for key in ("invalid", "failed", "conflict"))
    if good == 0:
        result["status"] = "failed"
        result["reason"] = "No usable skills installed from this source; inspect per-skill reasons"
    elif bad:
        result["status"] = "partial"
        result["reason"] = "%d skipped or failed skill(s)" % bad
    else:
        result["status"] = "copied_or_preserved"
    return result


def import_community(workspace, sources, strict=False, log=print):
    """Import declarative folders only. Persist every source outcome, even failures."""
    workspace = Path(workspace)
    old = read_manifest(workspace)
    previous = {s.get("vendor"): s for s in old["sources"]
                if isinstance(s, dict) and isinstance(s.get("vendor"), str)}
    current = []
    git = shutil.which("git")
    with tempfile.TemporaryDirectory(prefix="ai-studio-community-") as temp:
        for vendor, url, subdir in sources:
            result = _source_result(vendor, url, subdir)
            if not git:
                result["reason"] = "Git is not installed"
            else:
                dest = Path(temp) / vendor
                log("Fetching community skills: " + vendor)
                try:
                    proc = subprocess.run([git, "clone", "--quiet", "--depth", "1", "--", url, str(dest)],
                                          capture_output=True, text=True, timeout=120)
                    if proc.returncode:
                        result["reason"] = "Git clone failed: " + proc.stderr.strip()[:240]
                    else:
                        result["fetched"] = True
                        commit = subprocess.run([git, "-C", str(dest), "rev-parse", "HEAD"],
                                                capture_output=True, text=True, timeout=15)
                        candidate = commit.stdout.strip()
                        if commit.returncode == 0 and SHA.fullmatch(candidate):
                            result["commit"] = candidate
                            result = _import_source(workspace, dest, vendor, url, subdir,
                                                    previous.get(vendor, {}))
                            result["fetched"] = True
                            result["commit"] = candidate
                        else:
                            result["reason"] = "Could not verify source Git commit"
                except (OSError, subprocess.TimeoutExpired) as exc:
                    result["reason"] = "Unable to fetch source: %s" % exc
            result["counts"] = _counts(result["skills"])
            current.append(result)
            c = result["counts"]
            log("Community %s: %s; fetched=%s discovered=%d verified=%d copied=%d unchanged=%d preserved=%d conflict=%d invalid=%d failed=%d%s" %
                (vendor, result["status"], "yes" if result["fetched"] else "no",
                 c["discovered"], c["verified"], c["copied"], c["unchanged"], c["preserved"],
                 c["conflict"], c["invalid"], c["failed"],
                 ("; " + result["reason"]) if result["reason"] else ""))
    selected = {s["vendor"] for s in current}
    retained = [s for s in old["sources"] if s.get("vendor") not in selected]
    document = {"schema_version": SCHEMA_VERSION, "sources": retained + current}
    _write_manifest(workspace, document)
    failures = [r["vendor"] for r in current if r["status"] in ("failed", "partial")]
    copied = sum(r["counts"]["copied"] for r in current)
    log("Community skills copied: %d; source records: %s" % (copied, MANIFEST_PATH))
    log("Skill copies are not native plugins and do not prove agent discovery.")
    if failures and strict:
        raise RuntimeError("Community import incomplete for %s (see %s)" %
                           (", ".join(failures), MANIFEST_PATH))
    return copied


def community_report(workspace, out=print):
    """Display local evidence without modifying the workspace or using the network."""
    workspace = Path(workspace)
    document = read_manifest(workspace)
    out("Community skill inventory (read-only): " + str(workspace / MANIFEST_PATH))
    if not document["sources"]:
        out("No imported community sources recorded.")
        return
    for source in document["sources"]:
        vendor = source.get("vendor", "unknown")
        out("%s [%s] commit=%s" % (source_title(vendor), source.get("status", "unknown"),
                                   source.get("commit") or "unverified"))
        if source.get("reason"):
            out("  Note: " + source["reason"])
        for skill in source.get("skills", []):
            rel = skill.get("installed_path") or skill_path(skill["name"])
            path = workspace / rel
            present = path.is_file() and not path.is_symlink()
            out("  %s | %s | present=%s | license=%s | %s" %
                (skill.get("display_name", skill.get("name")), skill.get("status", "unknown"),
                 "yes" if present else "no", skill.get("license", "unverified"), rel))
    out("Copied files are not proof of agent discovery, native plugin installation, or activation.")
