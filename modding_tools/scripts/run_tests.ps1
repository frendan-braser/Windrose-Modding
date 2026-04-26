$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolsRoot = Split-Path -Parent $ScriptDir
$RepoRoot = Split-Path -Parent $ToolsRoot
$VenvPy = Join-Path $ToolsRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPy) {
    & $VenvPy -m pytest "$RepoRoot\modding_tools\tests"
} else {
    python -m pytest "$RepoRoot\modding_tools\tests"
}
