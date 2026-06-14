# Exit Entry, Sleep Silence, And Gift Name Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add nearest-edge exit/re-entry animation, suppress scheduled speech while sleeping, and package the app as `呆呆.exe`.

**Architecture:** Persist edge-relative exit metadata in `CatConfig`, keep edge and placement calculations in small pure helpers, and add explicit entering/exiting runtime states to `RigDesktopCatApp`. Scheduled message checks short-circuit during sleep, while the build script changes only the PyInstaller application name and output paths.

**Tech Stack:** Python, tkinter, JSON, PowerShell, PyInstaller, pytest

---

### Task 1: Persist Exit Metadata

**Files:**
- Modify: `src/desktop_cat/config.py`
- Test: `tests/test_gift_config_experience.py`

- [ ] Add failing round-trip tests for `last_exit_side` and `last_exit_y`.
- [ ] Validate that only `left` or `right` and integer Y values are accepted.
- [ ] Add `update_exit_state(side, y)` and persist both fields.
- [ ] Run focused configuration tests.

### Task 2: Add Exit And Entry Motion

**Files:**
- Modify: `src/desktop_cat/rig_app.py`
- Test: `tests/test_rig_preview.py`
- Test: `tests/test_gift_config_experience.py`

- [ ] Add failing pure-helper tests for nearest edge, clamped entry Y, outside
  start X, and visible target X.
- [ ] Add failing runtime tests for exit direction, persisted metadata, and
  startup entry placement.
- [ ] Implement entering/exiting flags and movement steps using existing walk
  actions.
- [ ] Delay first-launch and scheduled callbacks until entry completes.
- [ ] Preserve direct shutdown for smoke and internal teardown.
- [ ] Run focused runtime tests.

### Task 3: Suppress Scheduled Speech During Sleep

**Files:**
- Modify: `src/desktop_cat/rig_app.py`
- Test: `tests/test_companion_messages.py`
- Test: `tests/test_gift_config_experience.py`

- [ ] Add failing tests proving companion checks do not select or consume
  cooldown during `sleep_in` or `sleep`.
- [ ] Add failing tests proving fixed reminders are not shown or marked during
  sleep.
- [ ] Implement early scheduling-only returns.
- [ ] Run focused reminder and companion tests.

### Task 4: Rename Gift Executable

**Files:**
- Modify: `build_gift.ps1`
- Modify: `assets/gift/README_先看我.txt`
- Modify: `tools/generate_copywriting_catalog.py`
- Modify: `docs/target-machine-acceptance-checklist.md`
- Test: `tests/test_gift_config_experience.py`

- [ ] Change build expectations from `DesktopCatGift` to `呆呆`.
- [ ] Update recipient-facing paths and smoke commands.
- [ ] Regenerate copywriting and acceptance documentation.
- [ ] Run focused packaging/document tests.

### Task 5: Verify And Package

**Files:**
- Modify: `docs/NEXT_SESSION_HANDOFF.md`
- Build: `dist/呆呆/呆呆.exe`
- Replace: `dist/DesktopCatGift_20260613_final.zip`

- [ ] Run the complete test suite.
- [ ] Run `git diff --check`.
- [ ] Build with `build_gift.ps1`.
- [ ] Smoke the built and extracted `呆呆.exe`.
- [ ] Confirm no lingering process.
- [ ] Record final ZIP size and SHA256 in the handoff.

