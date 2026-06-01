# DesktopCat Asset Production Pipeline

The stable sprite build is the protected baseline. Future QQ-pet-level work
should improve assets through audited production batches, not by replacing
runtime code first.

## Current Protected Baselines

- `dist/DesktopCat/DesktopCat.exe`
- `dist/DesktopCatStablePreview/DesktopCatStablePreview.exe`
- `assets/sprites`
- `assets/qa/stable/stable_sprite_contact_sheet.png`

## Batch Workflow

1. Copy `assets/production/desktop_cat/batches/next_candidate_template`.
2. Rename it with a dated batch id.
3. Put raw pose sheets or generated strips in `raw/`.
4. Put reviewed transparent frames in `clean/<action>/`.
5. Add the batch to `assets/production/desktop_cat/batch_manifest.json`.
6. Import reviewed action frames with `tools/import_production_action.py`.
7. Run `tools/audit_production_batch.py --batch <batch_id>`.
8. Generate contact sheet and GIFs for visual review.
9. Run `tools/measure_production_batch.py` to record bbox, edge margin,
   alpha coverage, and center drift.
10. Run `tools/compare_production_batch.py` against the protected baseline.
11. Run `tools/gate_production_batch.py` for the automated QA gate.
12. Promote to `assets/sprites` only after visual QA beats the stable baseline.

For a scoped first-pass batch, use:

```powershell
python tools\import_production_action.py --batch-root assets\production\desktop_cat\batches\<batch_id> --action idle --source <reviewed_idle_frames> --expected-count 16 --canvas-size 512x512
python tools\export_production_batch_qa.py --batch <batch_id> --actions idle,blink,wave
python tools\audit_production_batch.py --batch <batch_id> --actions idle,blink,wave --report assets\production\desktop_cat\qa\<batch_id>\audit_report.json
python tools\measure_production_batch.py --batch <batch_id> --actions idle,blink,wave --report assets\production\desktop_cat\qa\<batch_id>\shape_metrics.json
python tools\compare_production_batch.py --batch <batch_id> --actions idle,blink,wave --report assets\production\desktop_cat\qa\<batch_id>\compare_to_baseline.json
python tools\gate_production_batch.py --batch <batch_id> --actions idle,blink,wave --report assets\production\desktop_cat\qa\<batch_id>\gate_report.json
```

Or run the full QA sequence in one command:

```powershell
python tools\run_production_batch_qa.py --batch <batch_id> --actions idle,blink,wave
```

After the command passes, complete the batch's `qa/visual_review_checklist.md`
before promotion. The automated gate cannot replace the ear, paw, bow, bell,
and "extra limb" checks.

## Candidate Runtime Preview

Preview an audited production batch in the desktop window without replacing
the stable sprite assets:

```powershell
.\run_candidate_dev.ps1 20260526_batch1_idle_blink_wave
```

For a short launch smoke test that opens the candidate window and exits
automatically:

```powershell
python .\candidate_launcher.py 20260526_batch1_idle_blink_wave --smoke-ms 1000
```

The candidate launcher reads from:

```text
assets/production/desktop_cat/batches/<batch_id>/clean
```

It does not write to `assets/sprites` and does not replace the stable packaged
preview. Use this only after `run_production_batch_qa.py` passes for the same
action scope.

## Quality Direction

For the next serious upgrade, prioritize full-frame polished sprite batches:

- idle
- blink
- wave
- clicked
- happy
- sleep
- drag

Only return to pseudo-Live2D/Spine when source assets are truly layered from the
start. Do not cut layered parts out of finished full-body frames for production.
