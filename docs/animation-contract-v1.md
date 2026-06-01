# DesktopCat Animation Contract V1

All actions use the same character bible in `docs/character-spec.md`.

| Action | Frames | FPS | Loop | Trigger | Notes |
| --- | ---: | ---: | --- | --- | --- |
| idle | 6-8 | 6 | yes | default | subtle breathing, blink/tail micro-motion |
| blink | 4 | 10 | no | idle insert | same pose and baseline |
| clicked | 4-5 | 12 | no | mouse click | surprise pop, then return to idle |
| happy | 6 | 10 | no | after click/random | tiny bounce, happy expression |
| wave | 6 | 10 | no | random/click variant | paw pose must be real, not dirty cutout |
| sleep | 6-8 | 5 | yes/short loop | random idle | curled/lying, no cropping |
| walk | 8 | 10 | yes | optional roaming | alternating legs, no sliding-only illusion |
| drag | 4 | 8 | yes while dragging | mouse drag | soft hanging posture |

## Acceptance

- Same canvas size for all frames.
- Same visual identity in every action.
- Same scale and ground baseline unless action intentionally bounces.
- Transparent frames only after the source action sheet is visually accepted.
- No app integration until an action sheet/contact sheet passes visual QA.
