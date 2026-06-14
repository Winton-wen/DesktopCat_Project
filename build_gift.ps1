$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".petvenv\Scripts\python.exe"
$AppName = "$([char]0x5446)$([char]0x5446)"
$BatchId = "20260527_motion_quality_v1"
$GiftDir = Join-Path $Root "assets\gift"
$GiftReadme = Get-ChildItem -LiteralPath $GiftDir -Filter "README_*.txt" | Select-Object -First 1
$GiftIcon = Join-Path $Root "assets\gift\desktopcat.ico"
$DistApp = Join-Path $Root "dist\$AppName"
$BuildApp = Join-Path $Root "build\$AppName"

if (-not (Test-Path $Python)) {
    throw "Missing .petvenv. Create the virtual environment and install requirements.txt first."
}
if ($null -eq $GiftReadme) {
    throw "Missing gift README in: $GiftDir"
}
if (-not (Test-Path $GiftIcon)) {
    throw "Missing gift icon: $GiftIcon"
}

$env:PYTHONNOUSERSITE = "1"

& $Python tools\run_production_batch_qa.py --batch $BatchId --actions idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,return_home,drag

if (Test-Path $DistApp) {
    Remove-Item -LiteralPath $DistApp -Recurse -Force
}
if (Test-Path $BuildApp) {
    Remove-Item -LiteralPath $BuildApp -Recurse -Force
}

& $Python -I -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name $AppName `
    --icon "$GiftIcon" `
    --add-data "$Root\assets\production\desktop_cat\batches\$BatchId\clean;assets\production\desktop_cat\batches\$BatchId\clean" `
    --add-data "$Root\assets\companion_messages;assets\companion_messages" `
    --add-data "$Root\assets\gift;assets\gift" `
    --paths "src" `
    --distpath "dist" `
    --workpath "build" `
    --specpath "build" `
    gift_launcher.py

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

Copy-Item -LiteralPath $GiftReadme.FullName -Destination (Join-Path $Root "dist\$AppName\$($GiftReadme.Name)") -Force

Write-Host ""
Write-Host "Gift build complete: dist\$AppName\$AppName.exe"
Write-Host "Batch: $BatchId"
