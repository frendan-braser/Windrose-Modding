param(
    [string]$ToolsRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $ToolsRoot) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ToolsRoot = Split-Path -Parent $ScriptDir
}

$bin = Join-Path $ToolsRoot "bin"
$tmp = Join-Path $env:TEMP "windrose_modding_tools"
$venv = Join-Path $ToolsRoot ".venv"

New-Item -ItemType Directory -Path $bin -Force | Out-Null
New-Item -ItemType Directory -Path $tmp -Force | Out-Null

Write-Host "Downloading repak..."
$repakZip = Join-Path $tmp "repak.zip"
Invoke-WebRequest -Uri "https://github.com/trumank/repak/releases/latest/download/repak_cli-x86_64-pc-windows-msvc.zip" -OutFile $repakZip
tar -xf $repakZip -C $bin

Write-Host "Downloading retoc..."
$retocZip = Join-Path $tmp "retoc.zip"
Invoke-WebRequest -Uri "https://github.com/trumank/retoc/releases/latest/download/retoc_cli-x86_64-pc-windows-msvc.zip" -OutFile $retocZip
tar -xf $retocZip -C $bin

Write-Host "Downloading rust-u4pak..."
$u4Zip = Join-Path $tmp "rust-u4pak.zip"
$u4Extract = Join-Path $tmp "rust-u4pak"
Invoke-WebRequest -Uri "https://github.com/panzi/rust-u4pak/releases/download/v1.4.0/release-v1.4.0.zip" -OutFile $u4Zip
New-Item -ItemType Directory -Path $u4Extract -Force | Out-Null
tar -xf $u4Zip -C $u4Extract
Get-ChildItem -Path $u4Extract -Recurse -Filter "*.exe" | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $bin -Force
}

Write-Host "Preparing Python venv..."
python -m venv $venv
$venvPy = Join-Path $venv "Scripts\python.exe"
& $venvPy -m pip install --upgrade pip pyuepak

Write-Host "Installed tools in: $bin"
Get-ChildItem -LiteralPath $bin | Select-Object Name, Length | Format-Table -AutoSize
