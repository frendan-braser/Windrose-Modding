param(
    [switch]$BackupFirst = $true
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModDir = Split-Path -Parent $ScriptDir
$ModsRoot = Split-Path -Parent $ModDir
$RepoRoot = Split-Path -Parent $ModsRoot
$Cli = Join-Path $RepoRoot "modding_tools\windrose_mod_cli.py"
$RootConfigLocal = Join-Path $RepoRoot ".local\crocodile-bounty.build.json"
$ConfigLocal = Join-Path $ModDir "docs\build_config.local.json"
$ConfigDefault = Join-Path $ModDir "docs\build_config.json"
$ConfigExample = Join-Path $ModDir "docs\build_config.example.json"
$Config = if (Test-Path $RootConfigLocal) {
    $RootConfigLocal
} elseif (Test-Path $ConfigLocal) {
    $ConfigLocal
} elseif (Test-Path $ConfigDefault) {
    $ConfigDefault
} else {
    $ConfigExample
}

if ($BackupFirst) {
    python $Cli build-install --config $Config --backup-first
} else {
    python $Cli build-install --config $Config
}
