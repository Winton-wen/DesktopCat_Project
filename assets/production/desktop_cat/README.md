# DesktopCat Production Asset Pipeline

This folder is the production intake area for future DesktopCat assets.

The current runnable baseline is protected:

- `dist/DesktopCat/DesktopCat.exe`
- `dist/DesktopCatStablePreview/DesktopCatStablePreview.exe`
- `assets/sprites`

New art must enter this folder first. Do not copy new frames into
`assets/sprites` until a production batch passes audit and visual QA.

## Folder Roles

- `source_refs/`: canonical reference images and approved identity anchors.
- `pose_sheets/`: raw pose sheets, turnarounds, or generated strips.
- `clean_frames/`: reviewed transparent PNG frames ready for audit.
- `rejected/`: failed images with notes; keep failures for comparison.
- `qa/`: contact sheets, GIFs, and audit reports for production batches.
- `batches/`: one subfolder per production batch.

## Baseline

`stable_v2_baseline` records the current stable full-frame sprite route. It is
not a request to overwrite the baseline; it is the measuring stick for future
quality.
