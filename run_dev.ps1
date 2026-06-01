$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".petvenv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "未找到 .petvenv，请先创建虚拟环境并安装 requirements.txt"
}

& $Python tools\prepare_sprite_workspace.py
& $Python tools\generate_reference_sprites.py
& $Python launcher.py
