# Complete Copy Catalog And Head Icon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a truly complete, user-editable copy catalog and replace the gift executable's full-body icon with a reproducible Daidai head, bow, and bell icon.

**Architecture:** Treat runtime source files as the copy truth and the Markdown catalog as a hand-editing artifact. Generate the ICO deterministically from the canonical production idle frame, keeping the existing `build_gift.ps1` icon path unchanged.

**Tech Stack:** Python 3.12, Pillow, Markdown, unittest/pytest, PyInstaller, PowerShell.

---

### Task 1: Catalog Coverage Tests

**Files:**
- Modify: `tests/test_gift_config_experience.py`

- [ ] Add a test that reads `docs/copywriting-message-catalog.md` and requires:
  `修改后文案`, `修改后触发条件/时间`, the six category time windows, all 14
  default message IDs, the reminder dismiss button, and every nonblank line of
  both README sources.
- [ ] Run the focused test and confirm it fails against the current summary-only
  catalog.

### Task 2: Complete Editable Catalog

**Files:**
- Replace: `docs/copywriting-message-catalog.md`

- [ ] Rewrite the document with exact template text and default rendered text.
- [ ] Add a separate editable block for each speech bubble and reminder.
- [ ] Add exact selection windows:
  `morning 07:00-11:30`, `lunch 11:30-13:30`,
  `afternoon 13:30-18:00`, `evening 18:00-22:30`,
  `late_night 01:30-05:00`, and `bedtime` for all remaining times.
- [ ] Fully expand config README and gift README line by line.
- [ ] Keep `sprite_app.py` in a clearly excluded appendix.
- [ ] Run the focused catalog test and confirm it passes.

### Task 3: Reproducible Head Icon

**Files:**
- Create: `tools/build_gift_icon.py`
- Create: `assets/gift/desktopcat_icon_head_preview.png`
- Replace: `assets/gift/desktopcat.ico`
- Modify: `tests/test_gift_config_experience.py`

- [ ] Add a failing test requiring the generator, preview, canonical source
  path, 512 x 512 RGBA preview, visible alpha content, and ICO sizes
  16/24/32/48/64/128/256.
- [ ] Implement a Pillow crop from production `idle/00.png` that includes the
  head, bow, and bell while excluding the lower body and tail.
- [ ] Generate the preview and multi-size ICO.
- [ ] Render representative 16, 32, and 256 px icon frames and inspect them
  visually.
- [ ] Run the icon test and confirm it passes.

### Task 4: Full Verification And Package

**Files:**
- Rebuild: `dist/DesktopCatGift`
- Replace: `dist/DesktopCatGift_20260605_polished.zip`

- [ ] Run `python -m pytest`.
- [ ] Run `python tools/run_candidate_feature_qa.py --backend-only --fast`.
- [ ] Run `powershell -ExecutionPolicy Bypass -File .\build_gift.ps1`.
- [ ] Confirm the built executable embeds the new icon.
- [ ] Run the built EXE with an isolated config directory and `--smoke-ms 3000`.
- [ ] Recreate the delivery ZIP.
- [ ] Extract the ZIP to a fresh directory and repeat the EXE smoke.
- [ ] Confirm no `DesktopCatGift.exe` process remains.
- [ ] Confirm `stash@{0}` and `raw/wake_*` remain untouched.
