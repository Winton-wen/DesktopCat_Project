# Exit Entry, Sleep Silence, And Gift Name Design

## Scope

This change has three recipient-facing goals:

1. Normal menu exit walks the kitten out through the nearest horizontal screen
   edge, and the next launch walks it back in from that side.
2. The kitten never displays automatic companion or fixed-time reminder speech
   while `sleep_in` or `sleep` is active.
3. The packaged folder and executable are named `呆呆`.

Existing companion copy that contains the pronoun `你` is unchanged.

## Exit And Entry

- Menu exit interrupts the current action, hides all speech windows, disables
  further interaction, and selects the nearest left or right edge.
- The kitten uses `walk_left` for a left exit and `walk` for a right exit.
- The window moves until it is fully outside the screen, then stores
  `last_exit_side` and `last_exit_y` before destroying the Tk windows.
- On the next launch, valid exit metadata places the window just outside the
  same edge. It walks inward until fully visible at `SCREEN_MARGIN`, then
  returns to idle.
- The saved vertical coordinate is clamped to the current screen.
- First-launch speech and scheduled checks wait until entry is complete.
- Direct shutdown remains available for automated smoke timers and internal
  teardown.

## Sleep Silence

- `check_companion_message()` schedules its next check but does not select,
  display, or consume cooldown while the action is `sleep_in` or `sleep`.
- `check_time_reminder()` schedules its next check but does not display or mark
  a reminder as shown while sleeping.
- Suppressed messages are not queued for wake-up.
- A later scheduled check may display a still-valid reminder after the kitten
  wakes.
- Manual click-to-wake behavior remains unchanged.

## Gift Name

- PyInstaller app name: `呆呆`.
- Build output: `dist/呆呆/呆呆.exe`.
- The final delivery ZIP keeps its existing outer filename so the known handoff
  path remains stable.
- README, acceptance docs, build tests, and smoke commands use the Chinese
  executable name.

