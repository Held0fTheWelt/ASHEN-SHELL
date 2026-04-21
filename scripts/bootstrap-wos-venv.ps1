#Requires -Version 5.1
<#
.SYNOPSIS
  Create a repository-local .venv for World of Shadows using a real CPython (py launcher), not WindowsApps stubs.

.DESCRIPTION
  PyCharm/terminal often pick Microsoft Store shims under WindowsApps; this script uses `py -3.x` first,
  then creates `.venv` at the repo root and runs `pip install -e .` for the hub package.

.PARAMETER RepoRoot
  Absolute path to the repository root. Defaults to the parent of this script directory.

.EXAMPLE
  .\scripts\bootstrap-wos-venv.ps1
#>
param(
    [string] $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $RepoRoot

function Find-PyLauncherVersion {
    foreach ($v in @('3.13', '3.12', '3.11', '3.10')) {
        & py "-$v" -c 'import sys' 2>$null
        if ($LASTEXITCODE -eq 0) { return $v }
    }
    return $null
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Error 'Python launcher ``py`` not found. Install Python from https://www.python.org/downloads/windows/ and include the py launcher.'
}

$ver = Find-PyLauncherVersion
if (-not $ver) {
    Write-Error 'No usable CPython 3.10-3.13 found via ``py -3.x``. Install python.org Python or repair the installation.'
}

$baseExe = (& py "-$ver" -c 'import sys; print(sys.executable)').Trim()
if ($baseExe -match '(?i)WindowsApps') {
    Write-Error @"
Resolved base Python is a WindowsApps stub (not runnable):
  $baseExe
Install CPython from https://www.python.org/downloads/windows/ (tick 'py launcher'), then re-run.
Disable Store aliases: Settings -> Apps -> App execution aliases -> turn off python.exe / python3.exe.
"@
}

Write-Host "Using base interpreter: $baseExe"
$venvPy = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPy)) {
    Write-Host 'Creating .venv ...'
    & $baseExe -m venv (Join-Path $RepoRoot '.venv')
}

& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -e .
Write-Host ''
Write-Host 'Done. In PyCharm: Settings -> Python Interpreter -> Add -> Existing -> select:'
Write-Host "  $venvPy"
