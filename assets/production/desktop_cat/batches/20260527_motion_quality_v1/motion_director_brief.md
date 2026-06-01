# Motion Director Brief

Batch: `20260527_motion_quality_v1`

Purpose: replace the current unacceptable full-frame actions with QQ-pet-like
motion quality. The current `blink` action is the only acceptable natural
reference. `happy`, `cute`, `sleep_in`, `wake`, and `walk` must be regenerated or
hand-cleaned before promotion.

Current asset intake:

- `pose_sheets/happy_cute_keyposes_v1_chromakey.png`: first real redrawn
  key-pose sheet for `happy` and `cute`, generated from the locked kitten
  identity instead of using transformed idle frames.
- `raw/happy_cute_keyposes_v1/keyposes`: cleaned 512x512 transparent keyposes.
- `raw/happy_cute_keyposes_v1/happy` and `raw/happy_cute_keyposes_v1/cute`:
  playable candidate sequences assembled from the keyposes. They are suitable
  for runtime preview and QA, but not final promotion until in-between poses
  are generated or hand-cleaned.

## Global Rules

- Same 512x512 transparent canvas.
- Same kitten identity, face, eyes, stripes, bow, bell, tail, and scale.
- No extra limbs, missing ears, broken paws, warped bow, or disappearing bell.
- Keep body volume consistent. Do not squash the whole cat flat as a shortcut.
- Maintain contact with the implied floor unless the pose intentionally bounces.
- Every action must start and end close to idle unless it intentionally chains
  into another state.

## Happy

Current failure: reads like one frame with paw up and one frame with paw down.

Required motion:

- Anticipation: body dips slightly before excitement.
- Paw lift: one front paw raises through multiple readable in-betweens.
- Expression: eyes and cheeks brighten gradually, not a single pop.
- Overshoot: paw and head bounce gently once.
- Settle: returns to idle over several frames.
- No duplicate paw, no detached paw, no sudden scale jump.

Target: 40-56 frames, 18-24 fps, non-looping.

## Cute

Required motion:

- Small anticipation bounce.
- Soft blink or bright-eyed look.
- Gentle side-to-side head/body tilt.
- One or both paws tucked near the bow, if the source art supports it.
- Tail flick or delayed secondary motion.
- Return to idle without snapping.

Target: 36-48 frames, 18-24 fps, non-looping.

## Sleep In

Current failure: cat becomes flat and collapses unnaturally.

Required motion:

- Sleepy blink or slow eye-close before body changes.
- Head lowers first, then shoulders/body settle.
- Front paws tuck or relax naturally.
- Body rotates/leans into sleeping pose while preserving volume.
- Tail follows with delayed secondary motion.
- End frame must match the sleep loop first frame.

Target: 18-24 frames, 10-12 fps, non-looping.

## Wake

Current failure: jumps directly from sleep to sitting.

Required motion:

- Eyes open first, small head lift.
- Body pushes up gradually with front paws.
- Ears perk after head rise.
- Tail has a delayed small flick.
- End frame must match idle closely.

Target: 18-24 frames, 10-12 fps, non-looping.

## Walk

Current failure: in-place stepping only, with no desktop movement before the
runtime fix.

Required motion:

- Four-step readable cycle with alternating paws.
- Body bob is subtle and periodic.
- Tail and bell lag slightly behind the body.
- Loop must be seamless.
- Provide right and left directions, either distinct or correctly mirrored.

Target: 12-16 frames per direction, 12-14 fps, looping-capable.

## Rejection Rules

Reject the batch if:

- The cat flattens, melts, or stretches unnaturally.
- A paw appears from nowhere or disappears abruptly.
- Pose changes happen in fewer than three visible in-between frames.
- Wake or sleep has a one-frame jump.
- Walk has no convincing foot alternation.
- Bow or bell disappears in any frame.
