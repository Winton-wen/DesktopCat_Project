# Action-Bound Bubble Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every action-triggered speech bubble disappear when its matching animation ends or is replaced.

**Architecture:** Add an optional owner token to `RigSpeechBubble` and assign a new token whenever `RigDesktopCatApp` starts an action. Action-triggered copy uses the active token; action completion and replacement clear only that token, preserving independent reminders and state bubbles.

**Tech Stack:** Python, tkinter, unittest/pytest

---

### Task 1: Add Regression Coverage

**Files:**
- Modify: `tests/test_rig_preview.py`
- Modify: `tests/test_speech_bubble_polish.py`

- [ ] Add a test proving `finish_current_action()` clears the active action token.
- [ ] Add tests proving owner cleanup hides matching visible copy and removes matching queued copy.
- [ ] Add a test proving owner cleanup leaves unowned reminder copy visible.
- [ ] Run the focused tests and confirm they fail because owner-aware lifecycle methods do not exist.

### Task 2: Implement Owner-Aware Bubble Lifecycle

**Files:**
- Modify: `src/desktop_cat/rig_app.py`

- [ ] Store an optional owner token for the visible bubble and queued messages.
- [ ] Add a method that clears current and queued bubbles for one owner token.
- [ ] Generate a fresh token for every started action.
- [ ] Bind action-triggered speech to the active action token.
- [ ] Clear the previous token when an action finishes or is replaced.
- [ ] Keep fixed reminders and state-only bubbles unowned.

### Task 3: Verify

**Files:**
- Test: `tests/test_rig_preview.py`
- Test: `tests/test_speech_bubble_polish.py`
- Test: full test suite

- [ ] Run focused tests and confirm the regression cases pass.
- [ ] Run `python -m pytest -q`.
- [ ] Run `git diff --check`.
- [ ] Inspect `git status --short --branch` and confirm no unrelated file was changed.

