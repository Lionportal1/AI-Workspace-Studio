#!/usr/bin/env python3
"""Verify source ZIP/TAR.GZ contents and run their offline tests after extraction."""
import argparse
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_release import source_paths
from ai_workspace_portable import VERSION


def safe_path(root, name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts or "\\" in name:
        raise RuntimeError("Unsafe source archive path: " + name)
    return root.joinpath(*relative.parts)


def verify_contents(members, expected):
    names = [name for name, _ in members]
    if len(names) != len(set(names)):
        raise RuntimeError("Duplicate archive entries")
    if set(names) != expected:
        missing = sorted(expected - set(names))
        extra = sorted(set(names) - expected)
        raise RuntimeError("Archive manifest mismatch; missing=%r unexpected=%r" % (missing, extra))
    for name, data in members:
        original = (ROOT / name).read_bytes()
        if hashlib.sha256(data).digest() != hashlib.sha256(original).digest():
            raise RuntimeError("Archive bytes differ from source: " + name)


def run_checks(root):
    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
        [sys.executable, "scripts/audit_sources.py"],
        [sys.executable, "ai_workspace_portable.py", "--doctor"],
    ]
    if os.name != "nt":
        commands.append(["bash", "tests/test_cli.sh"])
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError("Archive test failed (%s):\n%s\n%s" % (
                " ".join(command), result.stdout[-3000:], result.stderr[-3000:]))


def check_zip(archive, expected, destination):
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad is not None:
            raise RuntimeError("Corrupt ZIP member: " + bad)
        if any(item.is_dir() for item in z.infolist()):
            raise RuntimeError("Unexpected directory entry in ZIP")
        members = [(item.filename, z.read(item)) for item in z.infolist()]
    verify_contents(members, expected)
    for name, data in members:
        file = safe_path(destination, name)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
    run_checks(destination)
    print("Verified ZIP: %d manifest files, extracted test suite passed" % len(members))


def check_tar(archive, expected, destination):
    with tarfile.open(archive, mode="r:gz") as t:
        members = []
        for item in t:
            if not item.isfile():
                raise RuntimeError("Non-regular TAR member: " + item.name)
            stream = t.extractfile(item)
            if stream is None:
                raise RuntimeError("Cannot read TAR member: " + item.name)
            members.append((item.name, stream.read()))
    verify_contents(members, expected)
    for name, data in members:
        file = safe_path(destination, name)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
    run_checks(destination)
    print("Verified TAR.GZ: %d manifest files, extracted test suite passed" % len(members))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", default="dist")
    args = parser.parse_args()
    dist = Path(args.dist).resolve()
    tag = "AI-Workspace-Studio-v" + VERSION
    expected = set(source_paths())
    if not any(name.startswith("tests/test_") and name.endswith(".py") for name in expected):
        raise RuntimeError("No Python regression tests in release manifest")
    if "tests/test_release_license.py" not in expected or "tests/test_cli.sh" not in expected:
        raise RuntimeError("Missing required archive test coverage")
    with tempfile.TemporaryDirectory(prefix="aiws-release-verification-") as temp:
        check_zip(dist / (tag + ".zip"), expected, Path(temp) / "zip")
        check_tar(dist / (tag + ".tar.gz"), expected, Path(temp) / "tar")
    print("Source archive verification passed")


if __name__ == "__main__":
    main()
