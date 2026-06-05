$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".petvenv\Scripts\python.exe"
$AppName = "DesktopCatGift"
$BatchId = "20260527_motion_quality_v1"

if (-not (Test-Path $Python)) {
    throw "Missing .petvenv. Create the virtual environment and install requirements.txt first."
}

$env:PYTHONNOUSERSITE = "1"

& $Python tools\run_production_batch_qa.py --batch $BatchId --actions idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,return_home,drag

& $Python -I -m PyInstaller `
    --noconfirm `
    --windowed `
    --name $AppName `
    --add-data "$Root\assets;assets" `
    --paths "src" `
    --distpath "dist" `
    --workpath "build" `
    --specpath "build" `
    gift_launcher.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Gift build complete: dist\$AppName\$AppName.exe"
Write-Host "Batch: $BatchId"
