[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("daily-rate", "historical", "telegram")]
    [string]$Job,

    [string]$Time = "08:00",
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$PublishAfterRun,
    [switch]$IncludeTextArchive
)

$ErrorActionPreference = "Stop"

try {
    $runAt = [datetime]::ParseExact($Time, "HH:mm", $null)
}
catch {
    throw "Time must use 24-hour HH:mm format, for example 08:00 or 17:30."
}

$runner = Join-Path $PSScriptRoot "run_daily.ps1"
if (-not (Test-Path $runner)) { throw "Runner not found: $runner" }

$arguments = @(
    "-NoProfile"
    "-ExecutionPolicy", "Bypass"
    "-File", ('"{0}"' -f $runner)
    "-Job", $Job
    "-RepoRoot", ('"{0}"' -f $RepoRoot)
)
if ($PublishAfterRun) { $arguments += "-PublishAfterRun" }
if ($IncludeTextArchive) { $arguments += "-IncludeTextArchive" }

$taskName = "NBC Exchange Rate - $Job"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ($arguments -join " ") -WorkingDirectory $RepoRoot
$trigger = New-ScheduledTaskTrigger -Daily -At $runAt
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask `
    -TaskName $taskName `
    -Description "Runs the NBC exchange-rate $Job job every day." `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Force | Out-Null

Write-Host "Installed scheduled task: $taskName"
Write-Host "Daily time: $Time"
Write-Host "Repository: $RepoRoot"
Write-Host "Run it now with: Start-ScheduledTask -TaskName '$taskName'"
