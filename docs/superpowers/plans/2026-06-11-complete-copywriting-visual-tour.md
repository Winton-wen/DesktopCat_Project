# DesktopCat Complete Copywriting Visual Tour Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the incomplete candidate QA tour with a manual, exhaustive visual tour for every recipient-visible DesktopCat message.

**Architecture:** A new standalone tool builds `TourItem` records directly from runtime text constants, reminder constants, and the configured companion message pack. A controller drives the real `CandidateDesktopCatApp`, replaces the current bubble on manual navigation, and isolates all config writes in a temporary directory.

**Tech Stack:** Python 3, tkinter, existing DesktopCat runtime classes, unittest/pytest.

---

### Task 1: Define exhaustive tour collection behavior

**Files:**
- Delete: `tests/test_candidate_feature_qa_script.py`
- Create: `tests/test_copywriting_visual_tour.py`

- [ ] **Step 1: Write failing collection tests**

Add tests that import `build_tour_items()` and assert:

```python
text_templates = {
    (key, template)
    for key, templates in TEXT.items()
    for template in templates
}
tour_templates = {
    (item.source_id, item.text)
    for item in build_tour_items()
    if item.group == "interaction"
}
self.assertEqual(text_templates, tour_templates)
```

Also compare reminder keys against all four reminder constants and compare companion message IDs against the complete default pack.

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
python -m pytest tests/test_copywriting_visual_tour.py -q
```

Expected: import failure because `tools/run_copywriting_visual_tour.py` does not exist.

- [ ] **Step 3: Add failing special-date tests**

Assert every special-day `TourItem` has `current`, its formatted date matches either `month_day` or the 2026 lunar conversion table, and the anniversary item renders “二周年”.

- [ ] **Step 4: Run tests and verify they still fail for the missing feature**

Run the same focused pytest command and confirm the failure is caused by the missing tour module.

### Task 2: Implement tour item collection

**Files:**
- Create: `tools/run_copywriting_visual_tour.py`
- Test: `tests/test_copywriting_visual_tour.py`

- [ ] **Step 1: Define `TourItem`**

Create an immutable dataclass with:

```python
@dataclass(frozen=True)
class TourItem:
    id: str
    source_id: str
    group: str
    category: str
    text: str
    action: str
    current: datetime | None = None
    button_text: str | None = None
```

- [ ] **Step 2: Implement interaction and state collection**

Flatten every value in `TEXT`, assigning stable IDs such as `interaction:pet:01`. Add first-launch and the three state messages as explicit items because they are runtime strings rather than message-pack entries.

- [ ] **Step 3: Implement reminder collection**

Build one item for each reminder constant with the real dismiss-button label:

```text
谢谢呆呆的关心，不用再提醒啦
```

- [ ] **Step 4: Implement companion collection**

Load the default pack and preserve every message’s ID, category, text and action. For public special dates, use year 2026 with the configured month/day. For lunar special dates, reverse the 2026 lookup table to obtain the matching Gregorian date.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_copywriting_visual_tour.py -q
```

Expected: all collection and special-date tests pass.

### Task 3: Implement manual navigation controller

**Files:**
- Modify: `tools/run_copywriting_visual_tour.py`
- Test: `tests/test_copywriting_visual_tour.py`

- [ ] **Step 1: Write failing navigation tests**

Use a fake app and assert:

```python
tour.show(0)
tour.next()
self.assertEqual(1, tour.index)
tour.previous()
self.assertEqual(0, tour.index)
tour.previous()
self.assertEqual(0, tour.index)
```

At the final item, `next()` must remain at the final index. `replay()` must preserve the index while invoking the same action again.

- [ ] **Step 2: Run tests and verify RED**

Expected: failure because `CopywritingVisualTour` is missing.

- [ ] **Step 3: Implement controller**

The controller must:

- clear queued bubbles before each display;
- cancel the current bubble timeout;
- render the real text with the item’s test date;
- prefix `[current/total] source_id · category · action`;
- show the optional real reminder button;
- bind next, previous, replay and quit methods without mutating config.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_copywriting_visual_tour.py -q
```

Expected: all navigation tests pass.

### Task 4: Add CLI and temporary config isolation

**Files:**
- Modify: `tools/run_copywriting_visual_tour.py`
- Modify: `tests/test_copywriting_visual_tour.py`

- [ ] **Step 1: Write failing CLI tests**

Test argument parsing for:

```text
--list
--smoke
--batch
```

Patch app construction and assert `--list` does not instantiate Tk. Assert the runtime sets `DESKTOPCAT_CONFIG_DIR` to a temporary directory and restores the prior value afterward.

- [ ] **Step 2: Run tests and verify RED**

Expected: CLI/isolation assertions fail.

- [ ] **Step 3: Implement CLI**

Default command opens the manual tour. `--list` prints tab-separated index, ID, category, action and test date. `--smoke` shows the first item and exits after 3000 ms. `--batch` defaults to `20260527_motion_quality_v1`.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_copywriting_visual_tour.py -q
python tools/run_copywriting_visual_tour.py --list
```

Expected: tests pass and the list contains every collected item without opening a GUI.

### Task 5: Remove obsolete tour and update operational docs

**Files:**
- Delete: `tools/run_candidate_feature_qa.py`
- Modify: `docs/NEXT_SESSION_HANDOFF.md`

- [ ] **Step 1: Delete obsolete files**

Remove the old candidate feature QA script and its old test after the replacement focused tests pass.

- [ ] **Step 2: Update handoff**

Replace current “Must Read First” and useful-command references with:

```powershell
python tools\run_copywriting_visual_tour.py
python tools\run_copywriting_visual_tour.py --list
python tools\run_copywriting_visual_tour.py --smoke
```

Preserve historical validation records as historical facts, but mark the old script as removed and superseded by the complete manual visual tour.

- [ ] **Step 3: Check stale current references**

Run:

```powershell
rg -n "run_candidate_feature_qa|test_candidate_feature_qa_script" tools tests docs\NEXT_SESSION_HANDOFF.md
```

Expected: no current executable or test references remain; historical report names may remain only where explicitly labeled historical.

### Task 6: Full verification

**Files:**
- Verify all changed files

- [ ] **Step 1: Run focused tests**

```powershell
python -m pytest tests/test_copywriting_visual_tour.py -q
```

- [ ] **Step 2: Run full suite**

```powershell
python -m pytest -q
```

- [ ] **Step 3: Run collection mode**

```powershell
python tools/run_copywriting_visual_tour.py --list
```

Confirm the output includes every interaction template, all four reminders, every normal companion message, and every special-day message.

- [ ] **Step 4: Run GUI smoke**

```powershell
python tools/run_copywriting_visual_tour.py --smoke
```

Confirm the candidate pet opens, the first labeled bubble is visible, and the process exits cleanly.

- [ ] **Step 5: Run static checks**

```powershell
git diff --check
git status --short --branch
```

Confirm there are no whitespace errors, no stash restoration, no changes to `raw/wake_*`, and no staged, committed or pushed files.

## Execution Constraint

The repository owner explicitly requested no commit or push. Ignore commit steps normally required by the planning workflow; leave all work local and unstaged.
