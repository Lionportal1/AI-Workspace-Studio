"""Verify the MIT license accompanies all release distributions."""
import base64
import io
from pathlib import Path
import unittest
import zipfile

from scripts.build_release import source_paths, standalones

ROOT = Path(__file__).resolve().parents[1]


class ReleaseLicenseTests(unittest.TestCase):
    def test_source_archive_includes_mit_license(self):
        self.assertIn("LICENSE", source_paths())
        self.assertIn("Copyright (c) 2026 Lionportal1", (ROOT / "LICENSE").read_text())

    def test_standalone_embedded_payloads_include_license(self):
        windows, unix = standalones()
        for installer, encoded in (
            ("Windows PowerShell", windows.decode("utf-8").split("$Payload=@'\n", 1)[1].split("\n'@\n", 1)[0]),
            ("Unix Bash", unix.decode("utf-8").split("\n__AIWS_PAYLOAD__\n", 1)[1]),
        ):
            with self.subTest(installer=installer):
                self.assertIn(b"SPDX-License-Identifier: MIT", windows if installer.startswith("Windows") else unix)
                with zipfile.ZipFile(io.BytesIO(base64.b64decode("".join(encoded.split())))) as bundle:
                    license_text = bundle.read("LICENSE").decode("utf-8")
                    self.assertTrue(license_text.startswith("MIT License\n"))
                    self.assertIn("Copyright (c) 2026 Lionportal1", license_text)


if __name__ == "__main__":
    unittest.main()
