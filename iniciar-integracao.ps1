# Inicia a ponte do V&V TestLab (integration/vv_bridge.py, na raiz da ferramenta) para este repositório.
# Uso:  .\iniciar-integracao.ps1                    -> código corrigido: os 15 casos (22 testes) devem passar; mutação disponível
#       .\iniciar-integracao.ps1 -Versao original   -> código original (tag sut-original): os defeitos aparecem
#                                                      como falhas e viram DEF-xxx no painel
param([ValidateSet('corrigida', 'original')][string]$Versao = 'corrigida')

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = 'utf-8'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
# A ponte fica no V&V TestLab: este repositório dentro de output/ da ferramenta, ou ao lado dela (pacote de entrega).
$bridge = @('../../integration/vv_bridge.py', '../2-ferramenta-vv-testlab/integration/vv_bridge.py', '../vv-testlab/integration/vv_bridge.py') |
    ForEach-Object { Join-Path $PSScriptRoot $_ } | Where-Object { Test-Path $_ } | Select-Object -First 1
if (!(Test-Path $python)) { throw 'Execute .\setup_local.ps1 primeiro.' }
if (!$bridge) { throw 'Ponte integration/vv_bridge.py não encontrada: coloque este repositório em output/ do V&V TestLab ou ao lado da pasta da ferramenta.' }

$funcoes = 'reserve,cal_cost'
# O Windows procura "python" primeiro na pasta do cosmic-ray.exe (.venv-mutation, sem Flask); por isso a
# configuração usada pela ponte recebe o caminho absoluto do Python de .venv.
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot '.vvtestlab') | Out-Null
$pythonAbs = (Resolve-Path $python).Path.Replace('\', '/')
$config = (Get-Content (Join-Path $PSScriptRoot 'cosmic-ray.toml') -Raw -Encoding UTF8) -replace 'test-command = "python ', ('test-command = "\"' + $pythonAbs + '\" ')
[IO.File]::WriteAllText((Join-Path $PSScriptRoot '.vvtestlab/cosmic-ray-ponte.toml'), $config)
if ($Versao -eq 'original') {
    & $python -c "import sys; sys.path.insert(0, 'scripts'); import etapas; etapas.extrair_original()"
    $env:SUT_VERSAO = 'original'
    # --runxfail: no original, os casos marcados com defeito falham de verdade e são sincronizados como falhas.
    $pytestArgs = @('tests', '--runxfail', '-m', 'funcional or estrutural')
    Write-Host 'Ponte no CÓDIGO ORIGINAL (sut-original). Use "Executar e sincronizar"; a mutação só faz sentido no corrigido.'
} else {
    $env:SUT_VERSAO = 'corrigida'
    $funcoes += ',_sessao_autenticada,_periodos_conflitam,_quartos_ocupados,_ler_quartos'
    $pytestArgs = @('tests', '-m', 'funcional or estrutural or mutacao')
    Write-Host 'Ponte no CÓDIGO CORRIGIDO. "Executar e sincronizar" e "Executar mutação" (~4 min) disponíveis.'
}

& $python $bridge `
  --repo $PSScriptRoot `
  --port 8765 `
  --cov-source hotel.views `
  --cov-functions $funcoes `
  --mutation-tool cosmic-ray `
  --mutation-python .venv-mutation/Scripts/python.exe `
  --cosmic-ray-config .vvtestlab/cosmic-ray-ponte.toml `
  --cosmic-ray-selector scripts/selecionar_mutantes.py `
  --pytest-args @pytestArgs
