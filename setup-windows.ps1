# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Lionportal1
# Native Windows PowerShell 5.1/7 entry point (Python 3.8+ required).
# Python validates its own version. Do not run a separate native -c probe:
# that previously caused the wrapper to return without visible diagnostics.
$ErrorActionPreference = 'Stop'
$ArgsToPass = @($args)
$EntryPoint = Join-Path $PSScriptRoot 'ai_workspace_portable.py'

if (-not (Test-Path -LiteralPath $EntryPoint -PathType Leaf)) {
  throw "Missing AI Workspace Studio engine: $EntryPoint"
}

$Python = $null
$PythonName = $null
foreach ($name in @('py', 'python', 'python3')) {
  $candidate = Get-Command -Name $name -CommandType Application -ErrorAction SilentlyContinue |
    Select-Object -First 1
  if ($candidate) {
    $Python = $candidate.Source
    $PythonName = $name
    break
  }
}

if (-not $Python) {
  throw 'Python 3.8+ is required. Install Python and ensure py.exe or python.exe is on PATH.'
}

if ($PythonName -eq 'py') {
  & $Python -3 $EntryPoint @ArgsToPass
} else {
  & $Python $EntryPoint @ArgsToPass
}

$ExitCode = $LASTEXITCODE
if ($ExitCode -ne 0) {
  throw "AI Workspace Studio exited with code $ExitCode."
}
