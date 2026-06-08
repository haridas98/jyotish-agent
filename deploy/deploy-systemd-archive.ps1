param(
  [string]$HostName = $env:JYOTISH_DEPLOY_HOST,
  [string]$UserName = $env:JYOTISH_DEPLOY_USER,
  [string]$Password = $env:JYOTISH_DEPLOY_PASSWORD,
  [string]$HostKey = $env:JYOTISH_DEPLOY_HOSTKEY,
  [string]$PublicHealthUrl = $env:JYOTISH_PUBLIC_HEALTH_URL,
  [string]$PublicFrontendUrl = $env:JYOTISH_PUBLIC_FRONTEND_URL,
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

function Invoke-HttpCheck {
  param(
    [string]$Url,
    [switch]$PrintContent,
    [string]$ExpectedDeployCommit = ""
  )
  if (-not $Url) {
    return
  }

  $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 20
  Write-Host "HTTP $($response.StatusCode) $Url"
  if ($ExpectedDeployCommit) {
    $health = $response.Content | ConvertFrom-Json
    if ($health.deploy_commit -ne $ExpectedDeployCommit) {
      throw "Deploy commit mismatch for $Url. Expected $ExpectedDeployCommit, got $($health.deploy_commit)."
    }
  }
  if ($PrintContent) {
    Write-Host $response.Content
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

$remoteHealthCheckCommand = @'
health=$(curl -fsS http://127.0.0.1:18100/api/health)
echo "$health"
case "$health" in *deploy_commit*__DEPLOY_COMMIT__*) ;; *) echo "deploy_commit mismatch: expected __DEPLOY_COMMIT__" >&2; exit 1;; esac
'@ -replace "`r?`n", "; "
$remoteHealthCheckCommand = $remoteHealthCheckCommand.Replace("__DEPLOY_COMMIT__", $commit)

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
  $remoteHealthCheckCommand,
  "curl -I --max-time 15 http://127.0.0.1:13130/ >/dev/null"
) -join "; "

Invoke-Checked "plink.exe" ($sshArgs + @("${UserName}@${HostName}", $remoteCommand))

Invoke-HttpCheck -Url $PublicHealthUrl -PrintContent -ExpectedDeployCommit $commit
Invoke-HttpCheck -Url $PublicFrontendUrl

Write-Host "Deployed $commit to $HostName"
