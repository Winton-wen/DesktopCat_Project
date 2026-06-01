$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".petvenv\Scripts\python.exe"
$AppName = "DesktopCat"

if (-not (Test-Path $Python)) {
    throw "Missing .petvenv. Create the virtual environment and install requirements.txt first."
}

$env:PYTHONNOUSERSITE = "1"

& $Python tools\prepare_sprite_workspace.py
& $Python tools\process_generated_strips.py
& $Python tools\stabilize_sprites.py
& $Python tools\make_action_preview.py
& $Python tools\make_motion_contact.py
& $Python tools\make_motion_gifs.py

& $Python -I -m PyInstaller `
    --noconfirm `
    --windowed `
    --name $AppName `
    --add-data "$Root\assets;assets" `
    --paths "src" `
    --distpath "dist" `
    --workpath "build" `
    --specpath "build" `
    launcher.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Build complete: dist\$AppName\$AppName.exe"
