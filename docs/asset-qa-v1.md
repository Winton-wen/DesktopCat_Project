# DesktopCat v1 Asset QA

## Reviewed Asset

- File: `assets/concept/desktopcat_action_sheet_v1.png`
- Purpose: visual direction and action reference for DesktopCat v1.
- Status: direction approved candidate, not production animation frames.

## Pass

- Character identity is much more stable than the earlier rough sprite attempts.
- Cream orange and white kitten palette matches the character spec.
- Large glossy brown eyes, pink nose, blush, white muzzle/chest/paws, and ringed tail are present.
- Pink-brown bow and gold bell remain visible across all poses.
- 3D plush toy rendering style is close to the intended cute desktop-pet look.
- The sheet covers the v1 action set direction: idle, blink, clicked/surprised, happy, wave, sleep, walk, and drag-like lifted pose.

## Not Ready For App Integration

- Background is light/white rather than transparent.
- The image is a contact sheet, not per-action animation frames.
- Poses are separated by layout, but not exported as same-size sprite cells.
- Scale, baseline, and facing direction are not normalized for animation playback.
- Some decorative marks appear near the clicked/happy poses and must not be included in production frames.
- Walk, idle, sleep, drag, and click actions still need multiple adjacent frames with small motion deltas.

## Decision

Do not wire this image into the desktop pet app as a sprite source.

Use it as the locked visual target for the next generation pass:

1. Generate each action as a dedicated transparent-background sprite strip.
2. Keep one fixed canvas size per frame.
3. Keep head size, bow size, bell position, body height, and paw proportions consistent.
4. Export a contact sheet for QA before replacing any runtime assets.
5. Only integrate actions after the sprite sheet passes visual QA.

## Next Production Batch

Minimum batch for the next app-quality pass:

- `idle`: 6 frames
- `blink`: 4 frames
- `clicked`: 5 frames
- `happy`: 6 frames
- `wave`: 6 frames
- `sleep`: 6 frames
- `walk`: 8 frames
- `drag`: 4 frames

Recommended canvas: `512x512` per frame, transparent background, full body visible, consistent floor baseline.
