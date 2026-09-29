# omni-agents Windows Installer
# Usage: irm https://raw.githubusercontent.com/TheCheepeer/omni-agent/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "  omni-agents Installer (omni-agents CLI)" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Check if Python is available in PATH
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $PythonCmd) {
    Write-Host "[x] Python was not found on your system." -ForegroundColor Red
    Write-Host "    Please install Python 3.10 or higher before proceeding:" -ForegroundColor Yellow
    Write-Host "    https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check recommended isolated package managers (uv > pipx > pip)
$UvCmd = Get-Command uv -ErrorAction SilentlyContinue
$PipxCmd = Get-Command pipx -ErrorAction SilentlyContinue

if ($UvCmd) {
    Write-Host "-> Installing via 'uv tool'..." -ForegroundColor Green
    & uv tool install omni-agents --force
} elseif ($PipxCmd) {
    Write-Host "-> Installing via 'pipx'..." -ForegroundColor Green
    & pipx install omni-agents --force
} else {
    Write-Host "-> 'pipx' or 'uv' not found. Installing via user 'pip'..." -ForegroundColor Yellow
    & python -m pip install --upgrade --user omni-agents
}

Write-Host ""
Write-Host "[OK] omni-agents installed successfully!" -ForegroundColor Green
Write-Host "     Run 'omni-agents' in any terminal to get started." -ForegroundColor Cyan
Write-Host ""
