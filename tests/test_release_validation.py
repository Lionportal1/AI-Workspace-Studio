"""Verify release safeguards remain active when Python assertions are optimized out."""
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from scripts import build_release


ROOT = Path(__file__).resolve().parents[1]


def rewrite_archive(source, destination, replacement):
    with zipfile.ZipFile(source) as original:
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as modified:
            for name in original.namelist():
                data = replacement.get(name, original.read(name))
                if data is not None:
                    modified.writestr(name, data)


class ReleaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.valid = self.root / "valid.zip"
        self.valid.write_bytes(build_release.archive_zip(build_release.source_paths()))

    def test_unmodified_archive_passes(self):
        self.assertTrue(build_release.verify_source_zip(self.valid))

    def test_missing_license_fails_with_runtime_error(self):
        corrupted = self.root / "no-license.zip"
        corrupted.write_bytes(build_release.archive_zip(
            [name for name in build_release.source_paths() if name != "LICENSE"]))
        with self.assertRaisesRegex(RuntimeError, "missing the LICENSE"):
            build_release.verify_source_zip(corrupted)

    def test_tampered_license_fails(self):
        corrupted = self.root / "bad-license.zip"
        rewrite_archive(self.valid, corrupted, {"LICENSE": b"NOT A LICENSE\n"})
        with self.assertRaisesRegex(RuntimeError, "expected MIT License"):
            build_release.verify_source_zip(corrupted)

    def test_skill_tier_mismatch_fails_under_optimized_python(self):
        corrupted = self.root / "bad-index.zip"
        with zipfile.ZipFile(self.valid) as archive:
            tiers = json.loads(archive.read("assets/profile-index.json"))
        tiers["balanced"] = tiers["balanced"][:-1] + ["not-a-real-skill"]
        rewrite_archive(self.valid, corrupted, {
            "assets/profile-index.json": json.dumps(tiers).encode("utf-8")
        })
        result = subprocess.run(
            [sys.executable, "-O", "-c",
             "from scripts.build_release import verify_source_zip; "
             "verify_source_zip(__import__('sys').argv[1])", str(corrupted)],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Release ZIP", result.stderr)

    def test_missing_skill_definition_fails_under_optimized_python(self):
        fixture = self.root / "audit"
        (fixture / "assets").mkdir(parents=True)
        shutil.copy2(ROOT / "assets/profile-index.json", fixture / "assets/profile-index.json")
        shutil.copytree(ROOT / "assets/scaffold/.agents/skills",
                        fixture / "assets/scaffold/.agents/skills")
        missing = fixture / "assets/scaffold/.agents/skills/api-contract-review/SKILL.md"
        missing.unlink()
        result = subprocess.run(
            [sys.executable, "-O", "-c",
             "from scripts.audit_sources import audit; "
             "audit(__import__('sys').argv[1])", str(fixture)],
            cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing or unsafe skill definition", result.stderr)

    def test_missing_or_corrupt_archive_member_fails(self):
        corrupted = self.root / "corrupt.zip"
        corrupted.write_bytes(b"not a ZIP archive")
        with self.assertRaisesRegex(RuntimeError, "Invalid release ZIP"):
            build_release.verify_source_zip(corrupted)


if __name__ == "__main__":
    unittest.main()
