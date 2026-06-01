$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".petvenv\Scripts\python.exe"
$AppName = "DesktopCatStablePreview"

if (-not (Test-Path $Python)) {
    throw "Missing .petvenv. Create the virtual environment and install requirements.txt first."
}

$env:PYTHONNOUSERSITE = "1"

& $Python tools\export_stable_sprite_contact_sheet.py

& $Python -I -m PyInstaller `
    --noconfirm `
    --windowed `
    --name $AppName `
    --add-data "$Root\assets;assets" `
    --paths "src" `
    --distpath "dist" `
    --workpath "build" `
    --specpath "build" `
    stable_launcher.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Stable preview build complete: dist\$AppName\$AppName.exe"
