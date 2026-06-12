# DesktopCat Direction, Bubble, And Reminder Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct explicit movement directions, make happy direction testing faithful, preserve four emoticons through line breaks, and apply the approved blue reminder-button palette.

**Architecture:** Keep direction policy in `RigDesktopCatApp`, expose one shared happy preparation method for runtime and tour use, and keep visual-tour metadata in a separate Tk window. Continue sourcing copy from runtime constants and the JSON pack.

**Tech Stack:** Python 3, tkinter, pytest/unittest, existing DesktopCat sprite runtime.

---

### Task 1: Add regression tests

**Files:**
- Modify: `tests/test_stable_sprite_route.py`
- Modify: `tests/test_copywriting_visual_tour.py`
- Modify: `tests/test_speech_bubble_polish.py`
- Modify: `tests/test_companion_messages.py`

- [ ] Add tests proving explicit left/right movement never reverses at an edge while autonomous movement can reverse.
- [ ] Add tests proving tour happy playback calls the runtime happy preparation method.
- [ ] Add tests proving tour metadata is not included in the real speech bubble.
- [ ] Add exact copy tests for the four newline-separated emoticons.
- [ ] Add exact palette tests for `#DCEEFF`, `#C4E2FF`, and `#28527A`.
- [ ] Run focused tests and confirm RED for each missing behavior.

### Task 2: Fix direction and happy behavior

**Files:**
- Modify: `src/desktop_cat/rig_app.py`
- Modify: `tools/run_copywriting_visual_tour.py`

- [ ] Track whether the active walk may auto-reverse.
- [ ] Make explicit menu walks preserve their requested direction.
- [ ] Keep autonomous walks edge-aware.
- [ ] Extract a shared happy direction preparation method.
- [ ] Make visual-tour happy entries and replay use that method.
- [ ] Run focused direction and tour tests.

### Task 3: Separate tour status and update copy

**Files:**
- Modify: `tools/run_copywriting_visual_tour.py`
- Modify: `src/desktop_cat/rig_app.py`
- Modify: `src/desktop_cat/time_reminders.py`
- Modify: `assets/companion_messages/partner_default.json`
- Modify: `tests/test_companion_messages.py`
- Modify: `tests/test_stable_sprite_route.py`

- [ ] Add a small topmost tour-status window.
- [ ] Send metadata to the status window and only final rendered copy to the speech bubble.
- [ ] Insert explicit newlines in the four approved templates.
- [ ] Run the copywriting catalog generator to synchronize documentation.
- [ ] Run focused copy and tour tests.

### Task 4: Apply blue reminder palette

**Files:**
- Modify: `src/desktop_cat/rig_app.py`
- Modify: `tests/test_speech_bubble_polish.py`

- [ ] Introduce named reminder-button color constants.
- [ ] Apply them to the button window and button normal, active, and text colors.
- [ ] Run focused speech-bubble tests.

### Task 5: Verify

- [ ] Run all focused tests.
- [ ] Run `python -m pytest -q`.
- [ ] Run `python tools/run_copywriting_visual_tour.py --list`.
- [ ] Run `python tools/run_copywriting_visual_tour.py --smoke`.
- [ ] Run `git diff --check` and inspect `git status --short --branch`.

## Execution Constraint

Do not commit or push. Do not restore the deferred stash or touch `raw/wake_*` experiment assets.
