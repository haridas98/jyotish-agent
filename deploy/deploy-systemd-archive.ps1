param(
  [string]$HostName = $env:JYOTISH_DEPLOY_HOST,
  [string]$UserName = $env:JYOTISH_DEPLOY_USER,
  [string]$Password = $env:JYOTISH_DEPLOY_PASSWORD,
  [string]$HostKey = $env:JYOTISH_DEPLOY_HOSTKEY,
  [string]$AppPath = "/srv/jyotish-agent/app",
  [switch]$BackendOnly,
  [switch]$AllowDirty
)

$ErrorActionPreference = "Stop"

if (-not $HostName) {
  throw "Set -HostName or JYOTISH_DEPLOY_HOST."
}
if (-not $UserName) {
  $UserName = "root"
}

function Invoke-Checked {
  param(
    [string]$FilePath,
    [string[]]$Arguments
  )
  & $FilePath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "$FilePath failed with exit code $LASTEXITCODE"
  }
}

$status = (& git status --porcelain)
if ($status -and -not $AllowDirty) {
  throw "Working tree is not clean. Commit or stash changes, or pass -AllowDirty."
}

$commit = (& git rev-parse --short HEAD).Trim()
if (-not $commit) {
  throw "Cannot resolve git commit."
}

New-Item -ItemType Directory -Path ".tmp" -Force | Out-Null
$archive = Join-Path ".tmp" "deploy-jyotish-agent-$commit.tar"
$remoteArchive = "/tmp/deploy-jyotish-agent-$commit.tar"

Invoke-Checked "git" @("archive", "--format=tar", "--output=$archive", "HEAD")

$sshArgs = @("-batch")
if ($HostKey) {
  $sshArgs += @("-hostkey", $HostKey)
}
if ($Password) {
  $sshArgs += @("-pw", $Password)
}

$target = "${UserName}@${HostName}:${remoteArchive}"
Invoke-Checked "pscp.exe" ($sshArgs + @($archive, $target))

$restartCommand = if ($BackendOnly) {
  "systemctl restart jyotish-agent-backend.service"
} else {
  "cd ../frontend && npm run build && systemctl restart jyotish-agent-backend.service jyotish-agent-frontend.service"
}

$remoteCommand = @(
  "set -e",
  "cd $AppPath",
  "cp .deploy-commit .deploy-commit.prev 2>/dev/null || true",
  "tar -xf $remoteArchive -C $AppPath",
  "echo $commit > .deploy-commit",
  "cd backend",
  "./.venv/bin/python manage.py check",
  "./.venv/bin/python manage.py migrate --noinput",
  $restartCommand,
  "sleep 2",
  "curl -fsS http://127.0.0.1:18100/api/health",
  "curl -I --max-time 15 http://127.0.0.1:13130/ >/dev/null"
) -join "; "

Invoke-Checked "plink.exe" ($sshArgs + @("${UserName}@${HostName}", $remoteCommand))

Write-Host "Deployed $commit to $HostName"
