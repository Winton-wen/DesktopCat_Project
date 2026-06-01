# Visual Review Checklist

Batch: `20260526_batch1_idle_blink_wave`

Scope: `idle`, `blink`, `wave`

Use this checklist after running:

```powershell
python tools\run_production_batch_qa.py --batch 20260526_batch1_idle_blink_wave --actions idle,blink,wave
```

Review these files:

- `assets/production/desktop_cat/qa/20260526_batch1_idle_blink_wave/contact_sheet.png`
- `assets/production/desktop_cat/qa/20260526_batch1_idle_blink_wave/idle.gif`
- `assets/production/desktop_cat/qa/20260526_batch1_idle_blink_wave/blink.gif`
- `assets/production/desktop_cat/qa/20260526_batch1_idle_blink_wave/wave.gif`
- `assets/production/desktop_cat/qa/20260526_batch1_idle_blink_wave/compare_to_baseline.png`
- `assets/production/desktop_cat/qa/20260526_batch1_idle_blink_wave/gate_report.json`

## Identity Lock

- [ ] Face shape stays round and kitten-like.
- [ ] Eyes stay glossy, large, symmetric, and consistent across frames.
- [ ] Orange tabby forehead/body stripes stay coherent.
- [ ] White muzzle, chest, paws, and belly are not erased or stained.
- [ ] Pink blush stays soft and does not flicker.
- [ ] Bow and bell remain present, centered, and stable.

## Cutout And Damage Checks

- [ ] Left ear has no missing corner.
- [ ] Right ear has no notch or bitten-looking cut.
- [ ] Left front paw has no missing edge.
- [ ] Right front paw has no missing edge.
- [ ] Tail outline is complete and not clipped by canvas.
- [ ] Fur edge stays soft; no harsh white/black halo.
- [ ] Transparent background has no colored debris.

## Motion Checks

- [ ] Idle loops without a jump on the last-to-first frame.
- [ ] Blink reads as eyelids closing, not face deformation.
- [ ] Wave uses the existing front paw only; no extra limb appears.
- [ ] Wave returns cleanly to the neutral pose.
- [ ] Scale and ground contact do not drift.
- [ ] Motion is readable at desktop size.

## Decision

- [ ] Accept as candidate.
- [ ] Needs manual cleanup.
- [ ] Reject and regenerate.

Notes:

