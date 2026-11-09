"""Offline documentation tests for the stable release and source-of-truth entry pages."""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

from ai_workspace_portable import build_parser


ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "README.md",
    ROOT / "CHANGELOG.md",
    ROOT / "ROADMAP.md",
    ROOT / "WINDOWS_QUICKSTART.md",
    ROOT / "AI_WORKSPACE_GUIDE.md",
    ROOT / "docs/README.md",
]
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CLI_FLAG = re.compile(r"(?<![A-Za-z0-9-])--[a-z][a-z0-9-]*")


class DocumentationTests(unittest.TestCase):
    def test_documentation_entry_points_and_relative_links(self):
        for page in PAGES:
            with self.subTest(page=page.name):
                self.assertTrue(page.is_file(), page)
                text = page.read_text(encoding="utf-8")
                for target in LINK.findall(text):
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    local = unquote(target.split("#", 1)[0])
                    if not local:
                        continue
                    self.assertTrue((page.parent / local).is_file(),
                                    "%s contains broken local link: %s" % (page, target))

    def test_mentioned_cli_flags_exist(self):
        # --output belongs to scripts/build_release.py, not the installer.
        flags = set(build_parser()._option_string_actions) | {"--output"}
        for page in [ROOT / "README.md", ROOT / "AI_WORKSPACE_GUIDE.md",
                     ROOT / "WINDOWS_QUICKSTART.md", ROOT / "docs/README.md"]:
            text = page.read_text(encoding="utf-8")
            unknown = sorted(set(CLI_FLAG.findall(text)) - flags)
            self.assertEqual(unknown, [], "%s has unknown CLI flags" % page)

    def test_stable_release_is_not_described_as_unpublished(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        quickstart = (ROOT / "WINDOWS_QUICKSTART.md").read_text(encoding="utf-8")
        self.assertNotIn("candidate for its first GitHub release", readme)
        self.assertNotIn("No GitHub Release exists", changelog)
        self.assertIn("AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1", quickstart)
        self.assertIn("SHA256SUMS.txt", quickstart)
        self.assertIn("RemoteSigned", quickstart)


if __name__ == "__main__":
    unittest.main()
