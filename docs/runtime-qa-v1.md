# DesktopCat Runtime QA V1

## Current Integrated Actions

- `idle`: 16 transparent frames, v2 motion-graph base state
- `blink`: 10 transparent frames, v2 one-shot idle insert
- `clicked`: 5 transparent frames
- `happy`: 6 transparent frames
- `wave`: 16 transparent frames, v2 one-shot greeting
- `sleep`: 6 transparent frames
- `walk`: 8 transparent frames
- `drag`: 4 transparent frames

## Runtime Scope

The app is intentionally reduced to a clean desktop pet v1:

- transparent always-on-top pet window
- draggable pet
- click reaction
- double-click wave
- random idle actions
- one-shot actions return to idle instead of looping like GIFs
- speech bubbles
- tray menu for show/hide, happy, wave, sleep, autostart, reset, config, and quit

Deferred systems remain removed from runtime: feeding, water, status panel, mood stats, shop, mini-games, and complex养成 logic.

## Known Asset Notes

- The character is consistent enough for v1 testing.
- `idle`, `blink`, and `wave` have been upgraded to v2 longer-frame clips.
- `walk`, `clicked`, `happy`, `sleep`, and `drag` are still v1 clips and should be regenerated as v2 batches.
- `walk` still has occasional tail shortening from the generated source strip, not from runtime window cropping.
- Chroma-key removal is clean enough for desktop testing, but final polish should use native transparent renders or manual edge repair.
