param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^https://chatgpt\.com/')]
    [string]$ConversationUrl,

    [string]$RepoRoot,
    [int]$CdpPort = 9223,
    [switch]$LiveWake,
    [switch]$SkipInstall
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Step([string]$Message) {
    Write-Host "`n=== $Message ===" -ForegroundColor Cyan
}

function Fail([string]$Message) {
    throw "PULSE Windows acceptance failed: $Message"
}

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}

$PulseRoot = Join-Path $RepoRoot 'tools\pulse-lite'
if (-not (Test-Path (Join-Path $PulseRoot 'pyproject.toml'))) {
    Fail "could not locate tools/pulse-lite beneath $RepoRoot"
}

$PyLauncher = Get-Command py -ErrorAction SilentlyContinue
if ($PyLauncher) {
    $PythonExe = $PyLauncher.Source
    $PythonPrefixArgs = @('-3')
} else {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) { Fail 'Python 3 is required' }
    $PythonExe = $Python.Source
    $PythonPrefixArgs = @()
}

Step 'Verify GitHub CLI authentication'
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Fail 'gh CLI is required' }
& gh auth status
if ($LASTEXITCODE -ne 0) { Fail 'gh auth status failed' }
& gh api repos/vera-rubin/VISION-64 --jq '.full_name'
if ($LASTEXITCODE -ne 0) { Fail 'cannot read vera-rubin/VISION-64 with gh' }

Push-Location $PulseRoot
try {
    $Venv = Join-Path $PulseRoot '.venv-windows-acceptance'
    $VenvPython = Join-Path $Venv 'Scripts\python.exe'
    $PulseExe = Join-Path $Venv 'Scripts\pulse.exe'

    if (-not $SkipInstall) {
        Step 'Create isolated Python environment'
        if (-not (Test-Path $VenvPython)) {
            & $PythonExe @PythonPrefixArgs -m venv $Venv
            if ($LASTEXITCODE -ne 0) { Fail 'venv creation failed' }
        }

        Step 'Install PULSE Lite and test dependencies'
        & $VenvPython -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) { Fail 'pip upgrade failed' }
        & $VenvPython -m pip install -e '.[dev]'
        if ($LASTEXITCODE -ne 0) { Fail 'PULSE install failed' }
    }

    if (-not (Test-Path $PulseExe)) { Fail "pulse executable missing at $PulseExe" }

    Step 'Run local unit tests'
    & $VenvPython -m pytest
    if ($LASTEXITCODE -ne 0) { Fail 'unit tests failed' }

    $ProgramFilesX86 = [Environment]::GetFolderPath('ProgramFilesX86')
    $ChromeCandidates = @(
        (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
        $(if ($ProgramFilesX86) { Join-Path $ProgramFilesX86 'Google\Chrome\Application\chrome.exe' }),
        (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe'),
        (Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe'),
        $(if ($ProgramFilesX86) { Join-Path $ProgramFilesX86 'Microsoft\Edge\Application\msedge.exe' })
    ) | Where-Object { $_ -and (Test-Path $_) }

    if (-not $ChromeCandidates) { Fail 'Chrome or Edge not found' }
    $BrowserExe = $ChromeCandidates[0]
    $Profile = Join-Path $env:LOCALAPPDATA 'VISION64\pulse-lite\chrome-profile'
    New-Item -ItemType Directory -Force -Path $Profile | Out-Null

    Step 'Launch dedicated PULSE browser profile'
    $BrowserArgs = @(
        '--remote-debugging-address=127.0.0.1',
        "--remote-debugging-port=$CdpPort",
        "--user-data-dir=$Profile",
        '--no-first-run',
        '--no-default-browser-check',
        $ConversationUrl
    )
    Start-Process -FilePath $BrowserExe -ArgumentList $BrowserArgs | Out-Null

    $CdpUrl = "http://127.0.0.1:$CdpPort"
    $Deadline = (Get-Date).AddSeconds(20)
    $CdpReady = $false
    do {
        Start-Sleep -Milliseconds 500
        try {
            $null = Invoke-RestMethod -Uri "$CdpUrl/json/version" -TimeoutSec 2
            $CdpReady = $true
        } catch {
            $CdpReady = $false
        }
    } until ($CdpReady -or (Get-Date) -gt $Deadline)
    if (-not $CdpReady) { Fail "CDP did not become available at $CdpUrl" }

    Write-Host "`nA dedicated browser window is open." -ForegroundColor Yellow
    Write-Host 'If this PULSE profile is not signed into ChatGPT yet, sign in manually now.' -ForegroundColor Yellow
    Write-Host 'Make sure it is showing EXACTLY this conversation URL:' -ForegroundColor Yellow
    Write-Host $ConversationUrl -ForegroundColor White
    Read-Host 'Press Enter when the exact conversation is open and idle' | Out-Null

    Step 'Run PULSE doctor against the real ChatGPT page'
    & $PulseExe doctor --conversation-url $ConversationUrl --cdp-url $CdpUrl
    if ($LASTEXITCODE -ne 0) { Fail 'pulse doctor failed' }

    Step 'Verify deterministic wake and recovery prompts without submitting'
    $StateDir = Join-Path $env:LOCALAPPDATA 'VISION64\pulse-lite\windows-acceptance-state'
    if (Test-Path $StateDir) { Remove-Item -Recurse -Force $StateDir }

    & $PulseExe --state-dir $StateDir start `
        --conversation-url $ConversationUrl `
        --cdp-url $CdpUrl `
        --repository 'vera-rubin/VISION-64' `
        --result-issue 3 `
        --request-prefix 'rook-link-v1-ops-001' `
        --budget 1 `
        --session-id 'windows-acceptance' `
        --stuck-recovery `
        --stuck-seconds 180 `
        --recovery-budget 1
    if ($LASTEXITCODE -ne 0) { Fail 'pulse start failed' }

    & $PulseExe --state-dir $StateDir dry-run
    if ($LASTEXITCODE -ne 0) { Fail 'wake dry-run failed' }
    & $PulseExe --state-dir $StateDir dry-run --recovery
    if ($LASTEXITCODE -ne 0) { Fail 'recovery dry-run failed' }

    if ($LiveWake) {
        Step 'LIVE ACCEPTANCE: consume the existing Rook v1 result and wake this ChatGPT conversation once'
        Write-Host 'This submits exactly one pointer-only PULSE wake prompt into the configured conversation.' -ForegroundColor Yellow
        Write-Host 'Do not type in the ChatGPT composer during this step; user text always wins and blocks injection.' -ForegroundColor Yellow
        Read-Host 'Press Enter to send the one live acceptance wake' | Out-Null

        & $PulseExe --state-dir $StateDir once
        if ($LASTEXITCODE -ne 0) { Fail 'live PULSE cycle failed' }

        Step 'Inspect post-wake state'
        & $PulseExe --state-dir $StateDir status
        if ($LASTEXITCODE -ne 0) { Fail 'pulse status failed' }

        Write-Host "`nPASS candidate: this ChatGPT conversation should receive exactly one new message beginning 'PULSE micro-loop wake.'" -ForegroundColor Green
        Write-Host 'If it appeared once and wake_budget_remaining is 0, Windows live-wake acceptance passed.' -ForegroundColor Green
    } else {
        Write-Host "`nSAFE ACCEPTANCE PASSED through doctor + real browser inspection + dry-run." -ForegroundColor Green
        Write-Host 'Re-run this script with -LiveWake for the final one-message live injection test.' -ForegroundColor Green
    }
} finally {
    Pop-Location
}
