$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

uv venv --python 3.9 .venv
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o ambiente Python 3.9.' }
uv pip install --python .venv/Scripts/python.exe -r requirements-test.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar as dependências dos testes.' }

uv venv --python 3.12 .venv-mutation
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o ambiente de mutação.' }
uv pip install --python .venv-mutation/Scripts/python.exe -r requirements-mutation.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar Cosmic Ray.' }

Write-Host 'Ambientes prontos com pytest, coverage.py e Cosmic Ray. Use .\testes.ps1, .\mutacao.ps1 ou .\executar.ps1.'
