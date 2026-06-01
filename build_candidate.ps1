$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".petvenv\Scripts\python.exe"
$AppName = "DesktopCatCandidatePreview"
$BatchId = if ($args.Count -gt 0) { $args[0] } else { "20260526_batch1_idle_blink_wave" }

if (-not (Test-Path $Python)) {
    throw "Missing .petvenv. Create the virtual environment and install requirements.txt first."
}

$env:PYTHONNOUSERSITE = "1"

& $Python tools\run_production_batch_qa.py --batch $BatchId --actions idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,drag

& $Python -I -m PyInstaller `
    --noconfirm `
    --windowed `
    --name $AppName `
    --add-data "$Root\assets;assets" `
    --paths "src" `
    --distpath "dist" `
    --workpath "build" `
    --specpath "build" `
    candidate_launcher.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Candidate preview build complete: dist\$AppName\$AppName.exe"
Write-Host "Batch: $BatchId"
