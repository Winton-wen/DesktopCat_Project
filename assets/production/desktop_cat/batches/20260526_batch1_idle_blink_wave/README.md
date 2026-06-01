# 20260526_batch1_idle_blink_wave

Copy this folder when starting a new production batch.

Recommended naming:

`YYYYMMDD_<action-or-scope>_<source>`

Examples:

- `20260526_wave_regen`
- `20260526_batch1_idle_blink_wave`
- `20260526_spine_parts_test`

## Required Batch Layout

```text
batch_id/
  README.md
  raw/
  clean/
    idle/
    blink/
    wave/
    clicked/
    happy/
    sleep/
    drag/
  qa/
  notes.md
```

Do not promote the batch to `assets/sprites` until:

- `tools/audit_production_batch.py` passes for the batch after it is added to
  `batch_manifest.json`.
- Contact sheet and GIFs are visually reviewed.
- `tools/measure_production_batch.py` has produced shape metrics for bbox,
  transparent edge margin, alpha coverage, and center drift.
- `tools/compare_production_batch.py` has produced a side-by-side baseline
  comparison sheet and JSON report.
- `tools/gate_production_batch.py` passes after audit, metrics, and baseline
  comparison reports have been refreshed.
- First and last frames of non-idle actions are close enough to idle.
- Bow, bell, eyes, tail, ears, and white fur are intact in every frame.
