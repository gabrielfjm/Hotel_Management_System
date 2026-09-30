$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path $python)) { throw 'Execute .\setup_local.ps1 primeiro.' }
& $python -m scripts.seed_demo
if ($LASTEXITCODE -ne 0) { throw 'Falha ao preparar a base local.' }
& $python app.py
