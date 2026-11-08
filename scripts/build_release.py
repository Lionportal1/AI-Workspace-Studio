#!/usr/bin/env python3
"""Build deterministic GitHub release archives and standalone installers."""
import argparse
import base64
import gzip
import hashlib
import io
from pathlib import Path
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai_workspace_portable import VERSION

CORE = ["ai_workspace_portable.py","lib/generate_profiles.py","assets/profile-index.json"]

def source_paths():
    names = set(CORE + ["README.md","AI_WORKSPACE_GUIDE.md","WINDOWS_QUICKSTART.md",
        "ANTIGRAVITY_50_SKILLS_CATALOG.md","CONTRIBUTING.md","SECURITY.md",
        "CHANGELOG.md","ROADMAP.md",".gitignore","ai-workspace-setup.sh","setup-windows.ps1",
        "start-windows.cmd","scripts/audit_sources.py","scripts/build_release.py",
        "tests/test_installer.py","tests/test_cli.sh"])
    for dirname in ("assets/scaffold","docs",".github"):
        names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/dirname).rglob("*") if p.is_file())
    for name in names:
        if not (ROOT/name).is_file() or (ROOT/name).is_symlink():
            raise RuntimeError("Missing or unsafe file: "+name)
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
    files=CORE+[p for p in source_paths() if p.startswith("assets/scaffold/")]
    data=archive_zip(files)
    payload=base64.b64encode(data).decode("ascii")
    payload="\n".join(payload[i:i+112] for i in range(0,len(payload),112))
    digest=hashlib.sha256(data).hexdigest()
    windows=r"""# Self-contained AI Workspace Studio PowerShell installer (Python 3.8+ required).
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
  foreach ($name in @('py','python','python3')) {
    $cmd=Get-Command -Name $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $cmd) { continue }
    $prefix=if ($name -eq 'py') {@('-3')} else {@()}
    $good=& $cmd.Source @prefix -c 'import sys;print(int(sys.version_info >= (3,8)))' 2>$null
    if ($LASTEXITCODE -eq 0 -and $good -eq '1') {
      & $cmd.Source @prefix (Join-Path $Temp 'source/ai_workspace_portable.py') @Forward
      exit $LASTEXITCODE
    }
  }
  throw 'Python 3.8+ is required.'
} catch {
  Write-Error $_.Exception.Message
  exit 2
} finally {
  Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue
}
""".replace("__PAYLOAD__",payload).replace("__HASH__",digest)
    unix=r"""#!/usr/bin/env bash
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

def build(out):
    out.mkdir(parents=True,exist_ok=True)
    tag="AI-Workspace-Studio-v"+VERSION
    ps,sh=standalones()
    assets={tag+".zip":archive_zip(source_paths()),tag+".tar.gz":archive_tar(source_paths()),
            tag+"-Windows-Standalone.ps1":ps,tag+"-Unix-Standalone.sh":sh}
    for name,data in assets.items(): (out/name).write_bytes(data)
    (out/"SHA256SUMS.txt").write_text("\n".join(
        hashlib.sha256(data).hexdigest()+"  "+name for name,data in sorted(assets.items()))+"\n")
    with zipfile.ZipFile(out/(tag+".zip")) as z:
        assert z.testzip() is None
        count=sum(n.startswith("assets/scaffold/.agents/skills/") and n.endswith("/SKILL.md") for n in z.namelist())
        assert count==50, "Unexpected skill count: "+str(count)
    print("Built 5 assets for v"+VERSION)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="dist")
    build(Path(parser.parse_args().output).resolve())
