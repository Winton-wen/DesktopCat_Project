# DesktopCat Complete Copy Catalog And Head Icon Design

## Goal

Produce one editable document containing every user-visible string used by the
current gift executable, with its real trigger conditions and editable trigger
parameters. Replace the full-body executable icon with a close crop of Daidai's
head, bow, and bell.

## Copy Catalog

The catalog at `docs/copywriting-message-catalog.md` is the hand-editing source
for the user. It must reflect the current `gift_launcher.py` ->
`RigDesktopCatApp` route rather than historical implementations.

Each runtime item must include:

- Stable catalog ID.
- Source field or runtime key.
- Exact template stored in the project.
- Default rendered text using `呆呆` / `麻麻` / `粑粑`.
- Exact trigger, time window, cooldown, action, or date when applicable.
- An empty `修改后文案` field.
- An empty `修改后触发条件/时间` field where the trigger is configurable.

The document must fully expand:

- Identity defaults and placeholder rules.
- Basic interaction bubbles.
- First-launch and state feedback.
- Right-click menu labels.
- Tired-today random replies.
- Time reminders, dismiss button, check/repeat timing.
- All 14 default companion messages.
- Companion category time windows and fallback selection behavior.
- Every line of the generated config README.
- Every line of the gift README.
- The legacy `sprite_app.py` text in a clearly excluded appendix.
- The JSON format for adding normal and special-day messages.

The catalog is a review document only. The user's future edits will be applied
to runtime files in a later pass.

## Icon

Use the canonical production frame:

`assets/production/desktop_cat/batches/20260527_motion_quality_v1/clean/idle/00.png`

Crop the visible character to the head, bow, and bell. Do not include the paws,
body, or tail. Preserve transparency and identity. Center the crop on a square
transparent canvas with enough safety margin for Windows icon masks.

Create:

- `assets/gift/desktopcat_icon_head_preview.png` at 512 x 512 for inspection.
- `assets/gift/desktopcat.ico` with 16, 24, 32, 48, 64, 128, and 256 pixel
  variants.
- `tools/build_gift_icon.py` so the icon can be regenerated from the canonical
  production frame.

The build continues to use `assets/gift/desktopcat.ico`; no build-script path
change is needed.

## Verification

- Automated tests assert that the catalog contains every runtime copy group,
  editable fields, exact category time windows, all 14 message IDs, and fully
  expanded README text.
- Icon tests assert source/crop outputs, RGBA preview size, nonempty alpha,
  multiple ICO sizes, and the use of the canonical production frame.
- Visually inspect the 512 px preview and small-size icon renders.
- Run the full test suite.
- Rebuild the gift executable.
- Verify the executable icon and run packaged EXE and ZIP extraction smoke
  tests.

## Non-Goals

- Do not rewrite the user's copy before the user returns the edited catalog.
- Do not alter companion selection behavior.
- Do not restore the Supabase stash.
- Do not touch or stage `raw/wake_*` experiment assets.
- Do not commit or push without an explicit request.
