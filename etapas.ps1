# Reproduz todas as etapas do estudo, na ordem Funcional -> Estrutural -> Correção -> Mutação.
# Pré-requisito: .\setup_local.ps1 (cria .venv e .venv-mutation) e git disponível.
# Uso: .\etapas.ps1            (tudo)
#      .\etapas.ps1 -SemMutacao (só pytest/coverage, ~30 s)
param([switch]$SemMutacao)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$mutPython = Join-Path $PSScriptRoot '.venv-mutation/Scripts/python.exe'
if (!(Test-Path $python)) { throw 'Execute .\setup_local.ps1 primeiro.' }

Write-Host '== Métricas de código (radon, pygount) sobre o upstream'
& $python scripts/metricas_codigo.py
if ($LASTEXITCODE -ne 0) { throw 'Falha nas métricas.' }

foreach ($etapa in 'funcional-original', 'estrutural-original', 'suite-corrigida') {
    Write-Host "== Etapa $etapa"
    & $python scripts/etapas.py $etapa
    if ($LASTEXITCODE -ne 0) { throw "Falha na etapa $etapa." }
}

if (!$SemMutacao) {
    if (!(Test-Path $mutPython)) { throw 'Execute .\setup_local.ps1 para instalar o Cosmic Ray.' }
    foreach ($rodada in 'inicial', 'final') {
        Write-Host "== Mutação ($rodada)"
        & $mutPython scripts/mutacao.py $rodada
        if ($LASTEXITCODE -ne 0) { throw "Falha na mutação $rodada." }
    }
}

Write-Host '== Suíte final'
& $python scripts/etapas.py final-corrigida
if ($LASTEXITCODE -ne 0) { throw 'Falha na suíte final.' }

& $python scripts/evolucao.py
Write-Host 'Evidências em .\evidencias\'
