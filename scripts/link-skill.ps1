<#
.SYNOPSIS
    Vincula uma ou mais skills deste repositório a um workspace específico.
.DESCRIPTION
    Localiza a skill em qualquer categoria da biblioteca (stacks, planning, docs, frontend, meta)
    e cria uma Junction no diretório .agents/skills/ do projeto de destino.
.EXAMPLE
    .\scripts\link-skill.ps1 -Skill svelte5 -ProjectPath "D:\Projetos\meu-app"
    .\scripts\link-skill.ps1 -Skill rust, salsa
#>
param (
    [Parameter(Mandatory = $true, Position = 0)]
    [string[]]$Skill,

    [Parameter(Position = 1)]
    [string]$ProjectPath = (Get-Location).Path
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$TargetSkillsDir = Join-Path $ProjectPath ".agents\skills"

if (-not (Test-Path $TargetSkillsDir)) {
    New-Item -ItemType Directory -Path $TargetSkillsDir -Force | Out-Null
    Write-Host "[+] Diretório criado: $TargetSkillsDir" -ForegroundColor Cyan
}

foreach ($s in $Skill) {
    # Procura a pasta da skill dentro de skills/
    $Found = Get-ChildItem -Path (Join-Path $RepoRoot "skills") -Recurse -Directory -Filter $s | 
             Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } | 
             Select-Object -First 1

    if (-not $Found) {
        Write-Warning "Skill '$s' não encontrada na biblioteca em $RepoRoot\skills\"
        continue
    }

    $DestPath = Join-Path $TargetSkillsDir $s

    if (Test-Path $DestPath) {
        Write-Host "[i] A skill '$s' já está presente em $DestPath" -ForegroundColor Yellow
        continue
    }

    New-Item -ItemType Junction -Path $DestPath -Target $Found.FullName | Out-Null
    Write-Host "[OK] Skill '$s' vinculada com sucesso:" -ForegroundColor Green
    Write-Host "     Origem:  $($Found.FullName)"
    Write-Host "     Destino: $DestPath"
}
