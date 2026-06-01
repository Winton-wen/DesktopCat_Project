$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$batchId = if ($args.Count -gt 0) { $args[0] } else { "20260526_batch1_idle_blink_wave" }
$extraArgs = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
python .\candidate_launcher.py $batchId @extraArgs
