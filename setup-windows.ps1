# Native Windows PowerShell entry point (requires Python 3.8+).
$ErrorActionPreference = 'Stop'
$ArgsToPass = @($args)
$Script = Join-Path $PSScriptRoot 'ai_workspace_portable.py'
foreach ($cmd in @('py','python','python3')) {
  $exe = Get-Command $cmd -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $exe) { continue }
  $prefix = if ($cmd -eq 'py') { @('-3') } else { @() }
  $ver = & $exe.Source @prefix -c 'import sys;print(int(sys.version_info >= (3,8)))' 2>$null
  if ($LASTEXITCODE -eq 0 -and $ver -eq '1') {
    & $exe.Source @prefix $Script @ArgsToPass
    exit $LASTEXITCODE
  }
}
Write-Error 'Python 3.8+ is required.'
exit 2
