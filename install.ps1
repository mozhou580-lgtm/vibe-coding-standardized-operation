param(
  [ValidateSet('Codex', 'Claude', 'Both')]
  [string]$Target = 'Codex'
)

$ErrorActionPreference = 'Stop'
$PackageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

function Install-Skills([string]$Tool) {
  if ($Tool -eq 'Codex') {
    $TargetRoot = Join-Path $HOME '.codex'
  } else {
    $TargetRoot = Join-Path $HOME '.claude'
  }

  $SkillRoot = Join-Path $TargetRoot 'skills'
  $BackupRoot = Join-Path $TargetRoot 'backups/vibe-coding/skills'

  foreach ($Skill in @('prd-master', 'design-master', 'tdd-master')) {
    $SourceDir = Join-Path $PackageRoot "skills/$Skill"
    $SourceFile = Join-Path $SourceDir 'SKILL.md'
    $TargetDir = Join-Path $SkillRoot $Skill
    $BackupDir = Join-Path $BackupRoot "$Skill/$Stamp"

    if (-not (Test-Path -LiteralPath $SourceFile -PathType Leaf)) {
      throw "源文件不可读，停止安装: $SourceFile"
    }

    New-Item -ItemType Directory -Force -Path $SkillRoot | Out-Null
    if (Test-Path -LiteralPath $TargetDir) {
      New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
      Move-Item -LiteralPath $TargetDir -Destination $BackupDir -Force
      Write-Host "已备份: $TargetDir -> $BackupDir"
    }

    Copy-Item -LiteralPath $SourceDir -Destination $TargetDir -Recurse -Force
    Write-Host "已安装: $TargetDir"
  }
}

if ($Target -eq 'Both') {
  Install-Skills 'Codex'
  Install-Skills 'Claude'
} else {
  Install-Skills $Target
}

Write-Host '安装完成。请重启当前工具，然后使用：开始 PRD'
