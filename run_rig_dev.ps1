$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "$PSScriptRoot\src"
python "$PSScriptRoot\rig_launcher.py"
