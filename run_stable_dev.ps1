$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "$PSScriptRoot\src"
python "$PSScriptRoot\stable_launcher.py"
