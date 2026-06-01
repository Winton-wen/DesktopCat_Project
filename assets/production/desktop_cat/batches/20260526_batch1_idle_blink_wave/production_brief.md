# Production Brief: 20260526_batch1_idle_blink_wave

## Goal

Create a new candidate asset batch for the first three core actions:

- `idle`
- `blink`
- `wave`

This batch must visibly beat the protected `stable_v2_baseline` before it can
be promoted. It must not overwrite `assets/sprites` while still in planned or
candidate status.

## Why This Scope

These three actions define whether the pet feels alive at rest:

- `idle` establishes character identity, scale, baseline, and breathing feel.
- `blink` proves facial motion can happen without a flash or identity drift.
- `wave` proves a readable interaction can start and end close to idle.

## Required Outputs

Each accepted frame must be:

- `512x512`
- transparent PNG
- full body visible
- same kitten identity as `character_lock.md`
- bow and bell present
- no guide marks, text, watermark, scenery, or cutout artifacts

Expected frame counts:

- `idle`: 16 frames
- `blink`: 10 frames
- `wave`: 17 frames

## QA Commands

After clean frames exist under `clean/<action>/`, run:

```powershell
python tools\audit_production_batch.py --batch 20260526_batch1_idle_blink_wave --actions idle,blink,wave
python tools\export_production_batch_qa.py --batch 20260526_batch1_idle_blink_wave --actions idle,blink,wave
```

## Visual Acceptance

- First and last `blink` frame must align with `idle`.
- First and last `wave` frame must align with `idle`.
- `wave` must lift exactly one front paw; no extra paws or duplicated limbs.
- Ear tips, paws, tail, bow, and bell must never be cropped.
- The contact sheet should look like one kitten, not several variants.
