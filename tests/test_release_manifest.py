"""Regression checks for the declarative release source manifest."""
import base64
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import build_release, verify_release_archives


ROOT = Path(__file__).resolve().parents[1]


class ReleaseManifestTests(unittest.TestCase):
    def test_all_maintained_tests_are_in_source_manifest(self):
        paths = set(build_release.source_paths())
        expected = {
            entry.relative_to(ROOT).as_posix()
            for entry in (ROOT / "tests").rglob("*")
            if entry.is_file() and entry.suffix in (".py", ".sh")
            and "__pycache__" not in entry.parts
        }
        self.assertTrue(expected <= paths, sorted(expected - paths))
        self.assertIn("tests/test_release_license.py", paths)
        self.assertIn("tests/test_release_manifest.py", paths)

    def test_new_tests_are_discovered_and_generated_cache_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = [
                "ai_workspace_portable.py",
                "lib/generate_profiles.py",
                "assets/profile-index.json",
                "LICENSE",
                "tests/test_cli.sh",
                "tests/test_future_feature.py",
            ]
            for name in files:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture", encoding="utf-8")
            cached = root / "tests/__pycache__/test_cached.pyc"
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(b"python cache")
            (root / "tests/test_ignored.pyc").write_bytes(b"cached")
            manifest = {
                "schema_version": 1,
                "files": files[:5] + ["release-manifest.json"],
                "trees": ["tests"],
                "exclude_directories": ["__pycache__"],
                "exclude_suffixes": [".pyc"],
            }
            (root / "release-manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8")
            with patch.object(build_release, "ROOT", root):
                paths = build_release.source_paths()
            self.assertIn("tests/test_future_feature.py", paths)
            self.assertNotIn("tests/__pycache__/test_cached.pyc", paths)
            self.assertNotIn("tests/test_ignored.pyc", paths)

            # A manifest that omits a mandatory runtime/license file must fail,
            # even if that file happens to exist on disk.
            manifest["files"].remove("LICENSE")
            (root / "release-manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8")
            with patch.object(build_release, "ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "omits required files"):
                    build_release.source_paths()

    def test_extract_test_execution_requires_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(verify_release_archives.subprocess, "run") as runner:
                with self.assertRaisesRegex(RuntimeError, "--allow-exec"):
                    verify_release_archives.run_checks(Path(directory))
                runner.assert_not_called()

    def test_standalone_embeds_only_runtime_files(self):
        windows, _ = build_release.standalones()
        encoded = windows.decode("utf-8").split("$Payload=@'\n", 1)[1].split("\n'@\n", 1)[0]
        with zipfile.ZipFile(io.BytesIO(base64.b64decode("".join(encoded.split())))) as archive:
            names = set(archive.namelist())
        self.assertIn("LICENSE", names)
        self.assertTrue(set(build_release.CORE) <= names)
        self.assertFalse(any(n.startswith("tests/") for n in names))
        self.assertNotIn("release-manifest.json", names)


if __name__ == "__main__":
    unittest.main()
