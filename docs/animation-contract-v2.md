# DesktopCat Animation Contract V2

V2 moves from short GIF-like clips to a polished sprite motion graph. The goal is that the kitten feels like one living desktop companion, not separate animations being swapped.

## Core Rule

Every non-idle action must start from an idle-compatible pose and end on an idle-compatible pose.

The runtime may still switch sprite folders, but visually the first and last frames of each action must line up with `idle`.

## V2 Batch 1

| Action | Frames | FPS | Loop | Runtime Use | Notes |
| --- | ---: | ---: | --- | --- | --- |
| idle | 16 | 10 | yes | default base state | subtle breathing, slow tail sway, no sudden head/body shifts |
| blink | 10 | 10 | no | idle insert | open -> half -> closed hold -> open, gentle and slow |
| wave | 16 | 12 | no | double-click/random greeting | idle -> paw lift -> 2-3 small waves -> paw down -> idle |

## V2 Batch 2

| Action | Frames | FPS | Loop | Runtime Use | Notes |
| --- | ---: | ---: | --- | --- | --- |
| walk | 16 | 12 | yes | optional roaming | full tail visible in every frame, body baseline stable |
| clicked | 10 | 12 | no | click reaction | surprise pop, then settle into idle-compatible pose |
| drag | 8 | 6 | yes while dragging | drag reaction | slow soft dangling, no fast head shaking |
| sleep | 12 | 8 | yes/short | random rest | curled breathing, return via idle |
| happy | 12 | 12 | no | random/click variant | bounce but begins/ends close to idle |

## Motion Graph

Allowed transitions:

- `idle -> blink -> idle`
- `idle -> wave -> idle`
- `idle -> clicked -> idle`
- `idle -> happy -> idle`
- `idle -> sleep -> idle`
- `idle -> walk -> idle`
- `drag` may interrupt any state while the mouse is held, then returns to `idle`.

Disallowed transitions:

- `walk -> blink`
- `sleep -> wave`
- `happy -> walk`
- any non-idle action directly into another non-idle action

Busy-request policy:

- Ordinary action requests are accepted only while the pet is idle.
- A request received during another non-idle action is discarded immediately.
- Discarded requests do not queue, do not display their paired speech bubble,
  and are not replayed after the current action ends.
- Drag, wake-from-sleep, return-home recovery, first launch, and visual-tour
  force paths remain explicit exceptions.

## Acceptance

- No action may visually jump at the first or last frame.
- `blink` must not feel like a flash; it needs a closed-eye hold.
- `wave` must include paw lift and paw return, not only paw wiggle.
- `walk` must keep the full tail visible in every frame.
- All frames remain `512x512` transparent PNGs before runtime scaling.
