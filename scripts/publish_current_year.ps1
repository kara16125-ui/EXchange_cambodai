[CmdletBinding()]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$Branch = "main",
    [switch]$IncludeTextArchive
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not (Test-Path ".git")) {
    throw "Not a Git repository: $RepoRoot"
}

$year = Get-Date -Format "yyyy"
$paths = @()

if (Test-Path $year) {
    $paths += $year
}

# The project may keep extracted values under txt/YYYY.
if ($IncludeTextArchive -and (Test-Path (Join-Path "txt" $year))) {
    $paths += (Join-Path "txt" $year)
}

if ($paths.Count -eq 0) {
    Write-Host "No current-year archive found for $year. Nothing to publish."
    exit 0
}

# Stage only archive output. Secrets and source changes are not included.
git add -- $paths
if ($LASTEXITCODE -ne 0) { throw "git add failed." }

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "No new archive changes to publish."
    exit 0
}

$stamp = Get-Date -Format "yyyy-MM-dd"
git commit -m "Update NBC exchange-rate archive - $stamp"
if ($LASTEXITCODE -ne 0) { throw "git commit failed." }

# Integrate remote commits before pushing. Auto-stash protects unrelated local edits.
git pull --rebase --autostash origin $Branch
if ($LASTEXITCODE -ne 0) {
    throw "git pull --rebase failed. Resolve the conflict before retrying."
}

git push origin $Branch
if ($LASTEXITCODE -ne 0) { throw "git push failed." }

Write-Host "Published the $year archive to origin/$Branch."
