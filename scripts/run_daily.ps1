[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("daily-rate", "historical", "telegram")]
    [string]$Job,

    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$PublishAfterRun,
    [switch]$IncludeTextArchive
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

$python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtual-environment Python not found: $python`nCreate it with: py -m venv .venv"
}

$scriptMap = @{
    "daily-rate" = "fetch_daily_rate.py"
    "historical" = "download_historical_rates.py"
    "telegram"   = "telegram_bot.py"
}

$target = Join-Path $RepoRoot $scriptMap[$Job]
if (-not (Test-Path $target)) {
    throw "Python script not found: $target"
}

$logDirectory = Join-Path $RepoRoot "logs"
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$logFile = Join-Path $logDirectory ("{0}-{1}.log" -f $Job, (Get-Date -Format "yyyy-MM-dd"))

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting $Job" | Tee-Object -FilePath $logFile -Append
& $python $target 2>&1 | Tee-Object -FilePath $logFile -Append
$pythonExitCode = $LASTEXITCODE

if ($pythonExitCode -ne 0) {
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Failed with exit code $pythonExitCode" | Tee-Object -FilePath $logFile -Append
    exit $pythonExitCode
}

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Completed $Job" | Tee-Object -FilePath $logFile -Append

if ($PublishAfterRun) {
    $publishScript = Join-Path $PSScriptRoot "publish_current_year.ps1"
    $publishArgs = @("-RepoRoot", $RepoRoot)
    if ($IncludeTextArchive) { $publishArgs += "-IncludeTextArchive" }

    & $publishScript @publishArgs 2>&1 | Tee-Object -FilePath $logFile -Append
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
