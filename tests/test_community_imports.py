"""Offline community import, inventory and safety regression tests (no network)."""
from contextlib import contextmanager
import os
import json
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lib import community_imports as imports

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "c" * 40


class CommunityImportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.repository = self.root / "upstream"
        self.repository.mkdir()
        (self.repository / "LICENSE").write_text("Example upstream license", encoding="utf-8")

    def add_skill(self, name, folder=None, content=None):
        relative = folder or name
        path = self.repository / "skills" / relative / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if content is not None else (
            "---\nname: %s\ndescription: \"Useful %s instructions\"\n---\n\n# %s\n" %
            (name, name, name)), encoding="utf-8")
        return path

    @contextmanager
    def fake_git(self, failure_url=None):
        def execute(args, **kwargs):
            if args[1] == "clone":
                if failure_url and args[-2] == failure_url:
                    return subprocess.CompletedProcess(args, 1, "", "network unavailable")
                shutil.copytree(self.repository, Path(args[-1]), symlinks=True)
                return subprocess.CompletedProcess(args, 0, "", "")
            if "rev-parse" in args:
                return subprocess.CompletedProcess(args, 0, COMMIT + "\n", "")
            self.fail("Unexpected command invoked by community importer: " + repr(args))
        with patch.object(imports.shutil, "which", return_value="/fake/git"), \
             patch.object(imports.subprocess, "run", side_effect=execute):
            yield

    def source(self, vendor="superpowers", subdir="skills", url=None):
        return (vendor, url or ("https://github.com/example/" + vendor + ".git"), subdir)

    def manifest(self):
        return json.loads((self.workspace / imports.MANIFEST_PATH).read_text(encoding="utf-8"))

    def test_nested_collection_inventory_and_read_only_cli(self):
        self.add_skill("brainstorming", "planning/brainstorming")
        self.add_skill("debugging", "workflow/debugging")
        with self.fake_git():
            copied = imports.import_community(self.workspace, [self.source()], log=lambda _: None)
        self.assertEqual(copied, 2)
        report = self.manifest()
        self.assertEqual(report["schema_version"], 2)
        result = report["sources"][0]
        self.assertTrue(result["fetched"])
        self.assertEqual(result["commit"], COMMIT)
        self.assertEqual(result["counts"]["copied"], 2)
        self.assertEqual(result["counts"]["verified"], 2)
        self.assertEqual(result["status"], "copied_or_preserved")
        inventory = {s["name"]: s for s in result["skills"]}
        self.assertEqual(inventory["brainstorming"]["source_path"],
                         "skills/planning/brainstorming/SKILL.md")
        self.assertEqual(inventory["brainstorming"]["installed_path"],
                         ".agents/skills/brainstorming/SKILL.md")
        self.assertEqual(inventory["brainstorming"]["display_name"], "Superpowers / brainstorming")
        self.assertEqual(inventory["brainstorming"]["license"], "unverified")
        self.assertEqual(inventory["brainstorming"]["license_file"], "LICENSE")
        report_file = self.workspace / imports.MANIFEST_PATH
        before = report_file.read_bytes()
        result = subprocess.run(
            [sys.executable, str(ROOT / "ai_workspace_portable.py"),
             str(self.workspace), "--community-report"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Superpowers / brainstorming", result.stdout)
        self.assertIn("present=yes", result.stdout)
        self.assertIn("not proof of agent discovery", result.stdout)
        self.assertEqual(report_file.read_bytes(), before)

    def test_caveman_folded_description_frontmatter_is_valid(self):
        self.add_skill("caveman-review", content=(
            "---\nname: caveman-review\ndescription: >\n"
            "  Short first line.\n"
            "  Longer second line that remains part of the description.\n"
            "---\n\n# Caveman Review\n"))
        self.add_skill("caveman-empty", content=(
            "---\nname: caveman-empty\ndescription: >\n---\n\n# Empty\n"))
        with self.fake_git():
            copied = imports.import_community(self.workspace, [self.source("caveman")],
                                              log=lambda _: None)
        self.assertEqual(copied, 1)
        statuses = {skill["name"]: skill["status"]
                    for skill in self.manifest()["sources"][0]["skills"]}
        self.assertEqual(statuses["caveman-review"], "copied")
        self.assertEqual(statuses["caveman-empty"], "invalid")

    def test_repeated_import_preserves_existing_and_local_edits(self):
        self.add_skill("brainstorming")
        with self.fake_git():
            self.assertEqual(imports.import_community(self.workspace, [self.source()], log=lambda _: None), 1)
            self.assertEqual(imports.import_community(self.workspace, [self.source()], log=lambda _: None), 0)
        entry = self.manifest()["sources"][0]["skills"][0]
        self.assertEqual(entry["status"], "unchanged")
        local = self.workspace / ".agents/skills/brainstorming/SKILL.md"
        local.write_text("locally edited", encoding="utf-8")
        with self.fake_git():
            self.assertEqual(imports.import_community(self.workspace, [self.source()], log=lambda _: None), 0)
        entry = self.manifest()["sources"][0]["skills"][0]
        self.assertEqual(entry["status"], "preserved")
        self.assertEqual(local.read_text(encoding="utf-8"), "locally edited")

    def test_conflicting_builtin_and_malformed_skill_are_reported(self):
        self.add_skill("brainstorming")
        self.add_skill("broken", content="No YAML frontmatter")
        installed = self.workspace / ".agents/skills/brainstorming/SKILL.md"
        installed.parent.mkdir(parents=True)
        installed.write_text("built-in user file", encoding="utf-8")
        with self.fake_git():
            copied = imports.import_community(self.workspace, [self.source()], log=lambda _: None)
        self.assertEqual(copied, 0)
        self.assertEqual(installed.read_text(encoding="utf-8"), "built-in user file")
        result = self.manifest()["sources"][0]
        statuses = {s["name"]: s["status"] for s in result["skills"]}
        self.assertEqual(statuses, {"brainstorming": "conflict", "broken": "invalid"})
        self.assertEqual(result["status"], "failed")
        self.assertIn("No usable skills", result["reason"])

    def test_missing_source_and_clone_failure_persist_even_in_strict_mode(self):
        self.add_skill("brainstorming")
        bad_url = "https://github.com/example/failing.git"
        sources = [self.source(), self.source("failing", url=bad_url),
                   self.source("empty", subdir="no-such-folder")]
        with self.fake_git(failure_url=bad_url):
            with self.assertRaisesRegex(RuntimeError, "Community import incomplete"):
                imports.import_community(self.workspace, sources, strict=True, log=lambda _: None)
        results = {s["vendor"]: s for s in self.manifest()["sources"]}
        self.assertEqual(results["superpowers"]["status"], "copied_or_preserved")
        self.assertEqual(results["failing"]["status"], "failed")
        self.assertFalse(results["failing"]["fetched"])
        self.assertIn("Git clone failed", results["failing"]["reason"])
        self.assertTrue(results["empty"]["fetched"])
        self.assertIn("Missing or unsafe skills directory", results["empty"]["reason"])

    def test_all_community_sources_are_reported_skipped_when_offline(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "ai_workspace_portable.py"), str(self.workspace),
             "--agent", "antigravity", "--preset", "minimal", "--mcp", "none",
             "--community", "all", "--offline", "--no-git"],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(self.manifest()["sources"]), 7)
        self.assertTrue(all(source["status"] == "skipped"
                            for source in self.manifest()["sources"]))
        self.assertTrue(all("Disabled by --offline" in source["reason"]
                            for source in self.manifest()["sources"]))
        self.assertIn("Community superpowers: skipped", result.stdout)
        report = subprocess.run(
            [sys.executable, str(ROOT / "ai_workspace_portable.py"),
             str(self.workspace), "--community-report"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(report.returncode, 0, report.stdout + report.stderr)
        self.assertIn("Caveman [skipped]", report.stdout)

    def test_missing_git_persists_all_requested_sources(self):
        with patch.object(imports.shutil, "which", return_value=None), \
             patch.object(imports.subprocess, "run") as runner:
            self.assertEqual(imports.import_community(
                self.workspace, [self.source(), self.source("caveman")], log=lambda _: None), 0)
            runner.assert_not_called()
        self.assertEqual([s["status"] for s in self.manifest()["sources"]], ["failed", "failed"])
        self.assertEqual(self.manifest()["sources"][1]["reason"], "Git is not installed")

    def test_v1_lock_migration_and_windows_path_format(self):
        lock = self.workspace / imports.MANIFEST_PATH
        lock.parent.mkdir(parents=True)
        lock.write_text(json.dumps({"schema_version": 1, "sources": [
            {"vendor": "caveman", "url": "https://example.test/caveman",
             "commit": COMMIT, "new_skills_copied": ["review"]}]}), encoding="utf-8")
        converted = imports.read_manifest(self.workspace)
        self.assertEqual(converted["schema_version"], 2)
        self.assertEqual(converted["sources"][0]["skills"][0]["status"], "previously_recorded")
        self.assertEqual(PureWindowsPath(imports.skill_path("review")).parts,
                         (".agents", "skills", "review", "SKILL.md"))
        lines = []
        imports.community_report(self.workspace, out=lines.append)
        self.assertIn("Caveman / review", "\n".join(lines))

    def test_symlink_in_skill_is_rejected_without_copying(self):
        self.add_skill("brainstorming")
        link = self.repository / "skills/brainstorming/surprise"
        try:
            link.symlink_to(self.repository / "LICENSE")
        except (OSError, NotImplementedError):
            self.skipTest("Host does not allow symlink creation")
        with self.fake_git():
            imports.import_community(self.workspace, [self.source()], log=lambda _: None)
        result = self.manifest()["sources"][0]
        self.assertEqual(result["skills"][0]["status"], "invalid")
        self.assertFalse((self.workspace / ".agents/skills/brainstorming").exists())

    def test_failed_copy_does_not_delete_existing_or_partial_destination(self):
        self.add_skill("brainstorming")
        actual_copytree = shutil.copytree

        def simulated_copy(src, dst, *args, **kwargs):
            if ".agents" in Path(dst).parts:
                target = Path(dst)
                target.mkdir(parents=True)
                (target / "user-note.txt").write_text("preserve", encoding="utf-8")
                raise OSError("simulated partial copy")
            return actual_copytree(src, dst, *args, **kwargs)

        with self.fake_git(), patch.object(imports.shutil, "copytree",
                                          side_effect=simulated_copy):
            imports.import_community(self.workspace, [self.source()], log=lambda _: None)
        self.assertEqual(self.manifest()["sources"][0]["skills"][0]["status"], "failed")
        note = self.workspace / ".agents/skills/brainstorming/user-note.txt"
        self.assertEqual(note.read_text(encoding="utf-8"), "preserve")

    def test_read_only_report_refuses_path_traversal_in_manifest(self):
        path = self.workspace / imports.MANIFEST_PATH
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({
            "schema_version": 2,
            "sources": [{"vendor": "untrusted", "status": "copied", "commit": COMMIT,
                         "skills": [{"name": "bad", "status": "copied",
                                     "installed_path": "../../outside/SKILL.md"}]}]
        }), encoding="utf-8")
        messages = []
        imports.community_report(self.workspace, out=messages.append)
        self.assertIn("Unsafe installed path in manifest ignored", "\n".join(messages))

    def test_invalid_source_root_reports_no_skills(self):
        (self.repository / "skills").mkdir()
        with self.fake_git():
            imports.import_community(self.workspace, [self.source()], log=lambda _: None)
        self.assertIn("No SKILL.md", self.manifest()["sources"][0]["reason"])


class OptionalUpstreamLayoutTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("AIWS_TEST_COMMUNITY_UPSTREAM") == "1",
                         "Upstream network integration requires explicit opt-in")
    def test_superpowers_and_caveman_public_skill_layout(self):
        if not shutil.which("git"):
            self.skipTest("Git unavailable")
        with tempfile.TemporaryDirectory(prefix="aiws-upstream-verification-") as root:
            workspace = Path(root) / "workspace"
            workspace.mkdir()
            selected = [
                ("superpowers", "https://github.com/obra/superpowers.git", "skills"),
                ("caveman", "https://github.com/JuliusBrussee/caveman.git", "skills"),
            ]
            imports.import_community(workspace, selected, strict=True, log=lambda _: None)
            manifest = imports.read_manifest(workspace)
            self.assertEqual(len(manifest["sources"]), 2)
            for entry in manifest["sources"]:
                with self.subTest(vendor=entry["vendor"]):
                    self.assertTrue(entry["fetched"])
                    self.assertGreater(entry["counts"]["verified"], 0)
                    self.assertGreater(entry["counts"]["copied"], 0)


if __name__ == "__main__":
    unittest.main()
