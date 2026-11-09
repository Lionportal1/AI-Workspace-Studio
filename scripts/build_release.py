#!/usr/bin/env python3
"""Build deterministic GitHub release archives and standalone installers."""
import argparse
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai_workspace_portable import VERSION

CORE = ["ai_workspace_portable.py", "lib/generate_profiles.py", "assets/profile-index.json"]


def source_paths():
    """Resolve the explicit release-manifest.json policy, including all maintained tests."""
    manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise RuntimeError("Unsupported release source manifest schema")
    names = set(manifest["files"])
    ignored_directories = set(manifest.get("exclude_directories", []))
    ignored_filenames = set(manifest.get("exclude_files", []))
    ignored_suffixes = set(manifest.get("exclude_suffixes", []))
    for dirname in manifest["trees"]:
        base = ROOT / dirname
        if not base.is_dir() or base.is_symlink():
            raise RuntimeError("Missing or unsafe source tree: " + dirname)
        for path in base.rglob("*"):
            relative = path.relative_to(ROOT)
            if any(part in ignored_directories for part in relative.parts):
                continue
            if path.name in ignored_filenames or path.suffix in ignored_suffixes:
                continue
            if path.is_symlink():
                raise RuntimeError("Unsafe symlink in release source tree: " + relative.as_posix())
            if path.is_file():
                names.add(relative.as_posix())
    required = set(CORE + ["LICENSE", "release-manifest.json", "tests/test_cli.sh"])
    if not required <= names:
        raise RuntimeError("Release manifest omits required files: %r" % sorted(required - names))
    for name in names:
        parsed = PurePosixPath(name)
        if parsed.is_absolute() or ".." in parsed.parts or not parsed.parts or "\\" in name:
            raise RuntimeError("Unsafe release source path: " + name)
        if not (ROOT / name).is_file() or (ROOT / name).is_symlink():
            raise RuntimeError("Missing or unsafe file: " + name)
    return sorted(names)


def archive_zip(paths):
    memory=io.BytesIO()
    with zipfile.ZipFile(memory,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in paths:
            i=zipfile.ZipInfo(name,(2020,1,1,0,0,0))
            i.compress_type=zipfile.ZIP_DEFLATED
            i.external_attr=(0o100755 if name.endswith(".sh") else 0o100644)<<16
            z.writestr(i,(ROOT/name).read_bytes())
    return memory.getvalue()

def archive_tar(paths):
    memory=io.BytesIO()
    with gzip.GzipFile(fileobj=memory,mode="wb",filename="",mtime=0) as g:
        with tarfile.open(fileobj=g,mode="w",format=tarfile.USTAR_FORMAT) as t:
            for name in paths:
                data=(ROOT/name).read_bytes()
                i=tarfile.TarInfo(name)
                i.size=len(data)
                i.mtime=0
                i.uid=i.gid=0
                i.uname=i.gname=""
                i.mode=0o755 if name.endswith(".sh") else 0o644
                t.addfile(i,io.BytesIO(data))
    return memory.getvalue()

def standalones():
    files=["LICENSE"]+CORE+[p for p in source_paths() if p.startswith("assets/scaffold/")]
    data=archive_zip(files)
    payload=base64.b64encode(data).decode("ascii")
    payload="\n".join(payload[i:i+112] for i in range(0,len(payload),112))
    digest=hashlib.sha256(data).hexdigest()
    windows=r"""# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Lionportal1
# Self-contained AI Workspace Studio PowerShell installer (Python 3.8+ required).
$ErrorActionPreference='Stop'
$Forward=@($args)
$Payload=@'
__PAYLOAD__
'@
$Expected='__HASH__'
$Temp=Join-Path ([System.IO.Path]::GetTempPath()) ('aiws-'+[guid]::NewGuid().ToString('N'))
try {
  New-Item -ItemType Directory -Path $Temp -Force | Out-Null
  $Zip=Join-Path $Temp 'bundle.zip'
  [System.IO.File]::WriteAllBytes($Zip,[Convert]::FromBase64String(($Payload -replace '\s','')))
  if ((Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Expected) {
    throw 'Embedded archive checksum mismatch'
  }
  Expand-Archive -LiteralPath $Zip -DestinationPath (Join-Path $Temp 'source') -Force
  $Python=$null
  $PythonName=$null
  foreach ($name in @('py','python','python3')) {
    $cmd=Get-Command -Name $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd) {
      $Python=$cmd.Source
      $PythonName=$name
      break
    }
  }
  if (-not $Python) { throw 'Python 3.8+ is required.' }
  $EntryPoint=Join-Path (Join-Path $Temp 'source') 'ai_workspace_portable.py'
  if ($PythonName -eq 'py') {
    & $Python -3 $EntryPoint @Forward
  } else {
    & $Python $EntryPoint @Forward
  }
  if ($LASTEXITCODE -ne 0) { throw "AI Workspace Studio exited with code $LASTEXITCODE." }
} catch {
  throw
} finally {
  Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue
}
""".replace("__PAYLOAD__",payload).replace("__HASH__",digest)
    unix=r"""#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Lionportal1
set -Eeuo pipefail
command -v python3 >/dev/null || { echo 'Python 3.8+ required' >&2; exit 2; }
TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
python3 - "$0" "$TMP" <<'EXTRACT_PYTHON'
import base64,hashlib,io,pathlib,sys,zipfile
text=pathlib.Path(sys.argv[1]).read_text()
data=base64.b64decode(''.join(text.split('__AIWS_PAYLOAD__\n',1)[1].split()))
if hashlib.sha256(data).hexdigest() != '__HASH__': raise SystemExit('Checksum mismatch')
root=pathlib.Path(sys.argv[2])
with zipfile.ZipFile(io.BytesIO(data)) as z:
    for member in z.namelist():
        path=pathlib.PurePosixPath(member)
        if path.is_absolute() or '..' in path.parts: raise SystemExit('Unsafe ZIP path')
        target=root/member
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(z.read(member))
EXTRACT_PYTHON
python3 "$TMP/ai_workspace_portable.py" "$@"
exit $?
__AIWS_PAYLOAD__
__PAYLOAD__
""".replace("__PAYLOAD__",payload).replace("__HASH__",digest)
    return windows.encode(),unix.encode()

def verify_source_zip(path):
    """Reject corrupt/missing release payload members and inconsistent skill tiers."""
    import json
    import re
    try:
        with zipfile.ZipFile(path) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise RuntimeError("Corrupt release ZIP member: " + bad)
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise RuntimeError("Duplicate release ZIP member names")
            try:
                license_text = archive.read("LICENSE").replace(b"\r\n", b"\n")
            except KeyError as exc:
                raise RuntimeError("Release ZIP is missing the LICENSE") from exc
            if not license_text.startswith(b"MIT License\n"):
                raise RuntimeError("Release ZIP does not contain the expected MIT License")
            try:
                tiers = json.loads(archive.read("assets/profile-index.json").decode("utf-8"))
            except (KeyError, UnicodeError, ValueError) as exc:
                raise RuntimeError("Release ZIP is missing a valid skill index") from exc
            if not isinstance(tiers, dict):
                raise RuntimeError("Release ZIP skill index must be a JSON object")
            for preset, expected in (("minimal", 20), ("balanced", 35), ("max", 50)):
                items = tiers.get(preset)
                if not isinstance(items, list) or len(items) != expected or len(set(
                        item for item in items if isinstance(item, str))) != expected:
                    raise RuntimeError("Release ZIP has invalid %s skill tier" % preset)
                if any(not isinstance(item, str) or not re.fullmatch(r"[a-z0-9-]+", item)
                       for item in items):
                    raise RuntimeError("Release ZIP has invalid %s skill IDs" % preset)
            if not set(tiers["minimal"]) <= set(tiers["balanced"]) <= set(tiers["max"]):
                raise RuntimeError("Release ZIP skill tiers are not nested")
            prefix = "assets/scaffold/.agents/skills/"
            found = {name[len(prefix):-len("/SKILL.md")] for name in names
                     if name.startswith(prefix) and name.endswith("/SKILL.md")}
            if found != set(tiers["max"]):
                raise RuntimeError("Release ZIP skill count/index mismatch: %d entries" % len(found))
            if len(found) != 50:
                raise RuntimeError("Unexpected release ZIP skill count: %d" % len(found))
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise RuntimeError("Invalid release ZIP: %s" % exc) from exc
    return True


def build(out):
    # Validations must remain active with python -O.
    from scripts.audit_sources import audit
    audit(ROOT)
    out.mkdir(parents=True, exist_ok=True)
    tag = "AI-Workspace-Studio-v" + VERSION
    ps, sh = standalones()
    assets = {tag+".zip": archive_zip(source_paths()), tag+".tar.gz": archive_tar(source_paths()),
              tag+"-Windows-Standalone.ps1": ps, tag+"-Unix-Standalone.sh": sh}
    for name, data in assets.items():
        (out / name).write_bytes(data)
    (out / "SHA256SUMS.txt").write_text("\n".join(
        hashlib.sha256(data).hexdigest()+"  "+name for name,data in sorted(assets.items()))+"\n")
    verify_source_zip(out / (tag+".zip"))
    print("Built 5 assets for v"+VERSION)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="dist")
    build(Path(parser.parse_args().output).resolve())
