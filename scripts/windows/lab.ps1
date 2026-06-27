# SenseL Caldera Linux Lab — Windows helper (Docker Desktop + Linux containers).
# Usage: .\scripts\windows\lab.ps1 up | up-ndr | up-ndr-cloud | down | status | validate | test | clean
param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "up-ndr", "up-ndr-cloud", "down", "down-ndr", "down-ndr-cloud",
        "status", "status-ndr", "status-ndr-cloud", "validate", "test", "clean", "ndr-config", "ndr-cloud-config")]
    [string]$Action = "up"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

function Get-BashPath {
    $candidates = @(
        "$env:ProgramFiles\Git\bin\bash.exe",
        "${env:ProgramFiles(x86)}\Git\bin\bash.exe",
        "bash"
    )
    foreach ($path in $candidates) {
        if ($path -eq "bash") {
            $cmd = Get-Command bash -ErrorAction SilentlyContinue
            if ($cmd) { return $cmd.Source }
        }
        elseif (Test-Path $path) {
            return $path
        }
    }
    throw @"
Git Bash or WSL bash is required for NDR bootstrap scripts.
Install Git for Windows: https://git-scm.com/download/win
Or run this repo from WSL2 Ubuntu.
"@
}

function Invoke-Bash([string]$ScriptRel) {
    $bash = Get-BashPath
    $scriptPath = Join-Path $RepoRoot ($ScriptRel -replace '/', '\')
    & $bash $scriptPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Invoke-Compose([string[]]$ExtraArgs) {
    docker compose @ExtraArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$ComposeBase = @("-f", "compose.yml")
$ComposeNdr = @("-f", "compose.yml", "-f", "compose.ndr.yml")
$ComposeNdrCloud = @("-f", "compose.yml", "-f", "compose.ndr.yml", "-f", "compose.ndr.cloud.yml")

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

switch ($Action) {
    "up" {
        Invoke-Compose ($ComposeBase + @("up", "-d", "--build"))
    }
    "up-ndr" {
        Invoke-Compose ($ComposeNdr + @("up", "-d", "--build"))
    }
    "up-ndr-cloud" {
        Invoke-Bash "scripts/ensure-edge-sensor.sh"
        Invoke-Bash "scripts/bootstrap-ndr-cloud.sh"
        Invoke-Compose ($ComposeNdrCloud + @("up", "-d", "--build"))
        Write-Host ""
        Write-Host "Caldera UI:     http://127.0.0.1:8888"
        Write-Host "Edge Console:   http://127.0.0.1:8090  (Setup wizard — paste Portal invite code)"
    }
    "down" {
        Invoke-Compose ($ComposeBase + @("down"))
    }
    "down-ndr" {
        Invoke-Compose ($ComposeNdr + @("down"))
    }
    "down-ndr-cloud" {
        Invoke-Compose ($ComposeNdrCloud + @("down"))
    }
    "status" {
        Invoke-Compose ($ComposeBase + @("ps"))
        python scripts/trainingctl.py status
    }
    "status-ndr" {
        Invoke-Compose ($ComposeNdr + @("ps"))
        $env:ENABLE_NDR = "true"
        python scripts/trainingctl.py status --ndr
    }
    "status-ndr-cloud" {
        Invoke-Compose ($ComposeNdrCloud + @("ps"))
        $env:ENABLE_NDR = "true"
        python scripts/trainingctl.py status --ndr
    }
    "validate" {
        python scripts/trainingctl.py validate
        Invoke-Compose ($ComposeBase + @("config"))
    }
    "test" {
        python -m pytest -q
    }
    "clean" {
        python scripts/trainingctl.py cleanup
        Invoke-Compose ($ComposeBase + @("down", "-v"))
        docker compose -f compose.yml -f compose.ndr.yml down -v 2>$null
        docker compose -f compose.yml -f compose.ndr.yml -f compose.ndr.cloud.yml down -v 2>$null
    }
    "ndr-config" {
        Invoke-Compose ($ComposeNdr + @("config"))
    }
    "ndr-cloud-config" {
        Invoke-Bash "scripts/ensure-edge-sensor.sh"
        Invoke-Bash "scripts/bootstrap-ndr-cloud.sh"
        Invoke-Compose ($ComposeNdrCloud + @("config"))
    }
}
