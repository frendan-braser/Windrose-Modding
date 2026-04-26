param(
    [Parameter(Mandatory = $true)]
    [string]$BackupDir,
    [switch]$ClearExisting = $true
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ModDir = Split-Path -Parent $ScriptDir
$ModsRoot = Split-Path -Parent $ModDir
$RepoRoot = Split-Path -Parent $ModsRoot
$Cli = Join-Path $RepoRoot "modding_tools\windrose_mod_cli.py"

if ($ClearExisting) {
    python $Cli restore-mods --backup-dir $BackupDir --clear-existing
} else {
    python $Cli restore-mods --backup-dir $BackupDir
}
