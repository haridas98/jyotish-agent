[CmdletBinding()]
param(
    [int]$BackendPort = 8100,
    [int]$FrontendPort = 3130,
    [switch]$Install,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$TmpDir = Join-Path $Root ".tmp"
$Python = Join-Path $BackendDir ".venv\Scripts\python.exe"
$NpmCommand = Get-Command "npm.cmd" -ErrorAction SilentlyContinue
if (-not $NpmCommand) {
    $NpmCommand = Get-Command "npm" -ErrorAction SilentlyContinue
}

function Write-Step($Message) {
    Write-Host "[jyotish-agent] $Message" -ForegroundColor Cyan
}

function Invoke-Checked($WorkingDirectory, $FilePath, [string[]]$Arguments) {
    Push-Location $WorkingDirectory
    try {
        & $FilePath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed: $FilePath $($Arguments -join ' ')"
        }
    }
    finally {
        Pop-Location
    }
}

function Test-LocalPortOpen([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(250)) {
            return $false
        }
        $client.EndConnect($async)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
    }
}

New-Item -ItemType Directory -Force -Path $TmpDir | Out-Null

if ($Install) {
    if (-not (Test-Path $Python)) {
        Write-Step "Creating backend virtualenv"
        Invoke-Checked $BackendDir "python" @("-m", "venv", ".venv")
    }

    Write-Step "Installing backend dependencies"
    Invoke-Checked $BackendDir $Python @("-m", "pip", "install", "-e", ".[dev]")

    Write-Step "Installing frontend dependencies"
    if (-not $NpmCommand) {
        throw "npm is not installed or not in PATH"
    }
    Invoke-Checked $FrontendDir $NpmCommand.Source @("install")

    Write-Step "Running migrations and seed commands"
    Invoke-Checked $BackendDir $Python @("manage.py", "migrate")
    Invoke-Checked $BackendDir $Python @("manage.py", "seed_vaishnava_interpretations")
    Invoke-Checked $BackendDir $Python @("manage.py", "seed_shastra_catalog")
    Invoke-Checked $BackendDir $Python @("manage.py", "seed_yoga_catalog")
}

if (-not (Test-Path $Python)) {
    throw "Backend venv not found. Run: .\start-dev.ps1 -Install"
}

if (-not $NpmCommand) {
    throw "npm is not installed or not in PATH"
}

if (-not (Test-Path (Join-Path $FrontendDir "node_modules"))) {
    throw "Frontend node_modules not found. Run: .\start-dev.ps1 -Install"
}

if ($CheckOnly) {
    Write-Step "OK: dependencies are present"
    Write-Host "Backend:  http://127.0.0.1:$BackendPort"
    Write-Host "Frontend: http://127.0.0.1:$FrontendPort"
    exit 0
}

if (Test-LocalPortOpen $BackendPort) {
    throw "Port $BackendPort is already in use"
}

if (Test-LocalPortOpen $FrontendPort) {
    throw "Port $FrontendPort is already in use"
}

$BackendOut = Join-Path $TmpDir "backend-dev.out.log"
$BackendErr = Join-Path $TmpDir "backend-dev.err.log"
$FrontendOut = Join-Path $TmpDir "frontend-dev.out.log"
$FrontendErr = Join-Path $TmpDir "frontend-dev.err.log"
$PreviousApiBaseUrl = $env:NEXT_PUBLIC_API_BASE_URL
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:$BackendPort"

Write-Step "Starting backend on 127.0.0.1:$BackendPort"
$BackendProcess = Start-Process `
    -FilePath $Python `
    -ArgumentList @("manage.py", "runserver", "127.0.0.1:$BackendPort") `
    -WorkingDirectory $BackendDir `
    -RedirectStandardOutput $BackendOut `
    -RedirectStandardError $BackendErr `
    -WindowStyle Hidden `
    -PassThru

Write-Step "Starting frontend on 127.0.0.1:$FrontendPort"
$FrontendProcess = Start-Process `
    -FilePath $NpmCommand.Source `
    -ArgumentList @("run", "dev", "--", "--hostname", "127.0.0.1", "--port", "$FrontendPort") `
    -WorkingDirectory $FrontendDir `
    -RedirectStandardOutput $FrontendOut `
    -RedirectStandardError $FrontendErr `
    -WindowStyle Hidden `
    -PassThru

Write-Host ""
Write-Host "Frontend: http://127.0.0.1:$FrontendPort/" -ForegroundColor Green
Write-Host "Backend:  http://127.0.0.1:$BackendPort/" -ForegroundColor Green
Write-Host ""
Write-Host "Logs:"
Write-Host "  $BackendOut"
Write-Host "  $BackendErr"
Write-Host "  $FrontendOut"
Write-Host "  $FrontendErr"
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers."

try {
    while ($true) {
        Start-Sleep -Seconds 2
        if ($BackendProcess.HasExited) {
            throw "Backend stopped. Check $BackendErr"
        }
        if ($FrontendProcess.HasExited) {
            throw "Frontend stopped. Check $FrontendErr"
        }
    }
}
finally {
    Write-Step "Stopping dev servers"
    foreach ($Process in @($BackendProcess, $FrontendProcess)) {
        if ($Process -and -not $Process.HasExited) {
            Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
        }
    }
    $env:NEXT_PUBLIC_API_BASE_URL = $PreviousApiBaseUrl
}
