# DesktopCat Drop Busy Action Requests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove queued pet actions so ordinary action-and-bubble requests made while the cat is busy are discarded, while a new request made after the current action finishes starts immediately.

**Architecture:** Keep `RigDesktopCatApp.set_action()` as the single admission gate and preserve its boolean result. Remove all action queue state, make action-and-bubble entry points display text only after admission succeeds, and have automatic companion checks record cooldown only after a message was actually shown. Preserve force-only recovery paths and the independent speech-bubble queue.

**Tech Stack:** Python 3.12, Tkinter event handlers, `unittest`/pytest, existing DesktopCat sprite runtime.

**Repository rule:** Do not commit or push during implementation unless the user explicitly asks. Do not stage or modify `raw/wake_*` experiment assets.

---

## File Map

- Modify `src/desktop_cat/rig_app.py`
  - Remove action queue state and processing.
  - Admit or reject each ordinary action immediately.
  - Couple action admission with its interaction bubble.
  - Return message-display success to the automatic scheduler.
- Modify `tests/test_rig_preview.py`
  - Replace queue expectations with immediate rejection and post-finish acceptance.
  - Cover the first-click/drag transition that previously depended on the queue.
- Modify `tests/test_companion_messages.py`
  - Cover automatic message rejection, successful display, and cooldown recording.
- Modify `tests/test_gift_config_experience.py`
  - Cover menu/gift interaction bubbles being suppressed when their actions are rejected.
  - Adjust existing test doubles so `set_action()` returns an explicit boolean.
- Modify `tests/test_stable_sprite_route.py`
  - Keep sleep wake, drag, reset-position, and other force-path regression expectations.
- Modify `docs/animation-contract-v2.md`
  - Document that disallowed non-idle transitions are dropped rather than queued.
- Modify `docs/NEXT_SESSION_HANDOFF.md`
  - Record the new busy-request behavior and fresh verification results.

### Task 1: Replace Action Queue With Immediate Admission

**Files:**
- Modify: `tests/test_rig_preview.py`
- Modify: `src/desktop_cat/rig_app.py`

- [ ] **Step 1: Replace the old queue tests with failing rejection tests**

Replace `test_non_idle_actions_queue_instead_of_interrupting_current_action` and
`test_queued_action_starts_after_current_non_idle_action_finishes` with tests
equivalent to:

```python
def test_non_idle_action_rejects_new_action_without_queueing(self) -> None:
    from desktop_cat import rig_app

    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.action = "happy"
    app.frame = 12
    app.resetting_position = False
    app.drag_start = None
    app.happy_start = (10, 10)
    app.draw = lambda: None

    started = app.set_action("wave", 2.2)

    self.assertFalse(started)
    self.assertEqual("happy", app.action)
    self.assertEqual(12, app.frame)
    self.assertFalse(hasattr(app, "pending_actions"))


def test_finished_action_returns_to_natural_chain_without_old_requests(self) -> None:
    from desktop_cat import rig_app

    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.action = "happy"
    app.frame = 47
    app.action_until = 0.0
    app.happy_start = (10, 10)

    app.finish_current_action(123.0)

    self.assertEqual("idle", app.action)
    self.assertEqual(0, app.frame)
    self.assertGreater(app.action_until, 123.0)


def test_new_action_starts_immediately_after_previous_action_finishes(self) -> None:
    from desktop_cat import rig_app

    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.action = "happy"
    app.frame = 47
    app.action_until = 0.0
    app.resetting_position = False
    app.drag_start = None
    app.happy_start = (10, 10)
    app.draw = lambda: None

    app.finish_current_action(123.0)
    started = app.set_action("wave", 2.2)

    self.assertTrue(started)
    self.assertEqual("wave", app.action)
    self.assertEqual(0, app.frame)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -m pytest tests/test_rig_preview.py -q
```

Expected: the new tests fail because `pending_actions` is still initialized,
busy requests are still queued, and `finish_current_action()` still consumes
the queue.

- [ ] **Step 3: Remove the runtime action queue**

In `src/desktop_cat/rig_app.py`:

```python
# Delete:
MAX_PENDING_ACTIONS = 8
```

Delete from `RigDesktopCatApp.__init__`:

```python
self.pending_actions: list[tuple[str, float]] = []
```

Delete `queue_action()`. Change the admission and finish methods to:

```python
def action_can_start_immediately(self, action: str, force: bool) -> bool:
    if force or action in {"idle", "drag"}:
        return True
    return self.action == "idle" and not self.resetting_position


def set_action(self, action: str, seconds: float, force: bool = False) -> bool:
    if not self.action_can_start_immediately(action, force):
        return False
    self.start_action_now(action, seconds)
    return True


def finish_current_action(self, now: float) -> None:
    self.action = ACTION_CHAIN.get(self.action, "idle")
    self.frame = 0
    self.action_until = now + random.uniform(1.2, 2.2)
```

The removal of `not self.drag_start` is intentional: `on_press()` records the
pointer before requesting `clicked`, so the first idle click must remain
admissible. A real drag still takes over in `on_drag()`.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_rig_preview.py -q
```

Expected: all `test_rig_preview.py` tests pass.

### Task 2: Make Manual Action And Bubble Requests Atomic

**Files:**
- Modify: `tests/test_rig_preview.py`
- Modify: `tests/test_gift_config_experience.py`
- Modify: `src/desktop_cat/rig_app.py`

- [ ] **Step 1: Add failing tests for click, menu-style actions, and happy state**

Add focused tests using `RigDesktopCatApp.__new__` and lightweight fakes:

```python
def test_idle_mouse_press_starts_clicked_and_shows_one_bubble(self) -> None:
    from desktop_cat import rig_app

    shown: list[object] = []
    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.action = "idle"
    app.resetting_position = False
    app.drag_start = None
    app.root = type(
        "Root",
        (),
        {"winfo_x": lambda _self: 10, "winfo_y": lambda _self: 20},
    )()
    app.draw = lambda: None
    app.say = shown.append

    event = type("Event", (), {"x_root": 100, "y_root": 120})()
    app.on_press(event)

    self.assertEqual("clicked", app.action)
    self.assertEqual(1, len(shown))


def test_busy_mouse_press_drops_clicked_action_and_bubble(self) -> None:
    from desktop_cat import rig_app

    shown: list[object] = []
    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.action = "happy"
    app.frame = 5
    app.resetting_position = False
    app.drag_start = None
    app.root = type(
        "Root",
        (),
        {"winfo_x": lambda _self: 10, "winfo_y": lambda _self: 20},
    )()
    app.draw = lambda: None
    app.say = shown.append

    event = type("Event", (), {"x_root": 100, "y_root": 120})()
    app.on_press(event)

    self.assertEqual("happy", app.action)
    self.assertEqual([], shown)


def test_rejected_cute_action_does_not_show_bubble(self) -> None:
    from desktop_cat import rig_app

    shown: list[object] = []
    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.set_action = lambda *_args, **_kwargs: False
    app.say = shown.append

    app.cute()

    self.assertEqual([], shown)


def test_rejected_happy_does_not_mutate_motion_state_or_show_bubble(self) -> None:
    from desktop_cat import rig_app

    shown: list[object] = []
    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.happy_direction = -1
    app.happy_start = (40, 50)
    app.action = "wave"
    app.resetting_position = False
    app.drag_start = None
    app.next_horizontal_direction = lambda *_args: 1
    app.root = type(
        "Root",
        (),
        {"winfo_x": lambda _self: 100, "winfo_y": lambda _self: 120},
    )()
    app.draw = lambda: None
    app.say = shown.append

    app.happy()

    self.assertEqual(-1, app.happy_direction)
    self.assertEqual((40, 50), app.happy_start)
    self.assertEqual([], shown)


def test_rejected_walk_left_does_not_mutate_direction_or_show_bubble(self) -> None:
    from desktop_cat import rig_app

    shown: list[object] = []
    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.walk_direction = 1
    app.walk_can_reverse = True
    app.set_action = lambda *_args, **_kwargs: False
    app.say = shown.append

    app.walk_left()

    self.assertEqual(1, app.walk_direction)
    self.assertTrue(app.walk_can_reverse)
    self.assertEqual([], shown)
```

Add a gift-interaction regression in
`tests/test_gift_config_experience.py`:

```python
def test_rejected_gift_interaction_does_not_show_bubble(self) -> None:
    from desktop_cat import rig_app

    shown: list[object] = []
    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.set_action = lambda *_args, **_kwargs: False
    app.render_text = lambda text: text
    app.pet_anchor = lambda: (20, 30)
    app.bubble = type(
        "Bubble",
        (),
        {"show": lambda *_args, **_kwargs: shown.append(True)},
    )()

    app.show_gift_interaction("ignored", action="cute")

    self.assertEqual([], shown)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -m pytest tests/test_rig_preview.py tests/test_gift_config_experience.py -q
```

Expected: rejected actions still call `say()` or `bubble.show()`, and
`prepare_happy_action()` mutates direction/start before admission.

- [ ] **Step 3: Gate all manual bubbles on successful action admission**

Update `src/desktop_cat/rig_app.py` so action methods follow this pattern:

```python
def cute(self) -> None:
    if self.set_action("cute", 1.9):
        self.say(TEXT["cute"])
```

Apply the same boolean guard to:

```python
wave()
sleep()
walk_right()
walk_left()
walk()
show_gift_interaction()
```

For `walk_right()`, `walk_left()`, and `walk()`, only commit
`walk_direction`/`walk_can_reverse` after admission succeeds. Compute the
candidate action and direction in locals first.

Change the happy flow so state is committed only on success:

```python
def happy(self) -> None:
    if self.prepare_happy_action():
        self.say(TEXT["happy"])


def prepare_happy_action(self, force: bool = False) -> bool:
    direction = self.next_horizontal_direction()
    start = (self.root.winfo_x(), self.root.winfo_y())
    if not self.set_action(
        self.happy_action_for_direction(direction),
        2.0,
        force=force,
    ):
        return False
    self.happy_direction = direction
    self.happy_start = start
    return True
```

Change `on_press()` to show text only when the requested action starts:

```python
if self.action in {"sleep", "sleep_in"}:
    if self.set_action("wake", 4.0, force=self.action == "sleep"):
        self.say(TEXT["wake"])
elif self.set_action("clicked", 1.4):
    self.say(TEXT["pet"])
```

Preserve `on_drag()` as the immediate drag takeover and preserve forced
`idle` on drag release.

- [ ] **Step 4: Make existing test doubles return explicit success**

Where an existing test expects an action-and-bubble method to show text, change
test doubles from:

```python
app.set_action = lambda *_args, **_kwargs: None
```

or:

```python
app.set_action = lambda action, duration: action_calls.append((action, duration))
```

to:

```python
def accept_action(action, duration, force=False):
    action_calls.append((action, duration, force))
    return True
```

Do not change forced first-launch tests that only inspect the call unless their
fake is used as a boolean admission result.

- [ ] **Step 5: Run the focused tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_rig_preview.py tests/test_gift_config_experience.py tests/test_stable_sprite_route.py -q
```

Expected: all focused tests pass, including drag, sleep wake, and reset-position
regressions.

### Task 3: Drop Busy Automatic Companion Messages Without Consuming Cooldown

**Files:**
- Modify: `tests/test_companion_messages.py`
- Modify: `src/desktop_cat/rig_app.py`

- [ ] **Step 1: Add failing automatic-message admission tests**

Update the existing rendering test so accepted `set_action()` returns `True`,
then add:

```python
def test_busy_companion_message_is_not_shown(self) -> None:
    from desktop_cat.rig_app import CompanionMessage, RigDesktopCatApp

    bubble_calls: list[object] = []
    app = RigDesktopCatApp.__new__(RigDesktopCatApp)
    app.set_action = lambda *_args, **_kwargs: False
    app.bubble = type(
        "Bubble",
        (),
        {"show": lambda *_args, **_kwargs: bubble_calls.append(True)},
    )()
    message = CompanionMessage(
        id="busy",
        category="comfort",
        text="ignored",
        cooldown_hours=12,
        action="wave",
    )

    shown = app.show_companion_message(message)

    self.assertFalse(shown)
    self.assertEqual([], bubble_calls)


def test_companion_check_records_cooldown_only_after_message_is_shown(self) -> None:
    from desktop_cat import rig_app

    current = datetime(2026, 6, 12, 20, 0)
    message = rig_app.CompanionMessage(
        id="comfort",
        category="comfort",
        text="hello",
        cooldown_hours=12,
        action="wave",
    )
    scheduled: list[int] = []
    app = rig_app.RigDesktopCatApp.__new__(rig_app.RigDesktopCatApp)
    app.store = SimpleNamespace(config=SimpleNamespace(low_distraction_mode=False))
    app.root = SimpleNamespace(after=lambda delay, _callback: scheduled.append(delay))
    app.companion_pack = SimpleNamespace(messages=[message])
    app.companion_messages_last_shown_at = {}
    app.show_companion_message = lambda *_args, **_kwargs: False

    with patch.object(rig_app, "select_companion_message", return_value=message):
        app.check_companion_message(current)

    self.assertEqual({}, app.companion_messages_last_shown_at)
    self.assertEqual([rig_app.DEFAULT_COMPANION_CHECK_MS], scheduled)
```

Add the success counterpart with
`app.show_companion_message = lambda *_args, **_kwargs: True` and assert:

```python
self.assertEqual(
    {"comfort": current},
    app.companion_messages_last_shown_at,
)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -m pytest tests/test_companion_messages.py -q
```

Expected: `show_companion_message()` returns `None`, still shows its bubble
after rejection, and `check_companion_message()` records cooldown before
display admission.

- [ ] **Step 3: Return display success and move cooldown recording**

Change `show_companion_message()` to:

```python
def show_companion_message(
    self,
    message: CompanionMessage,
    current: datetime | None = None,
) -> bool:
    action = message.action if message.action in ACTION_FPS else "wave"
    if action == "sleep":
        action = "sleep_in"
    if not self.set_action(action, 2.4):
        return False
    text = self.render_text(message.text, current=current)
    self.bubble.show(
        text,
        *self.pet_anchor(),
        hide_ms=COMPANION_MESSAGE_HIDE_MS,
    )
    return True
```

Change `check_companion_message()` to:

```python
if message is not None and self.show_companion_message(message, current=current):
    self.companion_messages_last_shown_at[message.id] = current
```

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_companion_messages.py tests/test_speech_bubble_polish.py -q
```

Expected: automatic-message tests pass and the independent speech-bubble queue
tests remain unchanged.

### Task 4: Synchronize Contract And Handoff

**Files:**
- Modify: `docs/animation-contract-v2.md`
- Modify: `docs/NEXT_SESSION_HANDOFF.md`

- [ ] **Step 1: Update the animation transition contract**

Add this runtime rule under `Motion Graph`:

```markdown
Busy-request policy:

- Ordinary action requests are accepted only while the pet is idle.
- A request received during another non-idle action is discarded immediately.
- Discarded requests do not queue, do not display their paired speech bubble,
  and are not replayed after the current action ends.
- Drag, wake-from-sleep, return-home recovery, first launch, and visual-tour
  force paths remain explicit exceptions.
```

- [ ] **Step 2: Update the handoff behavior and validation sections**

In `docs/NEXT_SESSION_HANDOFF.md`:

- Replace statements saying non-idle actions and bubbles queue together.
- State that ordinary busy-time action-and-bubble requests are dropped.
- State that the independent bubble queue remains for no-action messages.
- Add the fresh focused/full test and visual-tour smoke results from Task 5.
- Do not change package SHA256 unless a new package is actually built.

- [ ] **Step 3: Check documentation consistency**

Run:

```powershell
rg -n "pending_actions|actions queue|动作排队|排队" docs src tests
```

Expected: references remain only where documenting removed historical behavior
or the independent speech-bubble queue.

### Task 5: Full Verification

**Files:**
- Verify all modified files.

- [ ] **Step 1: Run all focused behavior tests**

Run:

```powershell
python -m pytest tests/test_rig_preview.py tests/test_companion_messages.py tests/test_gift_config_experience.py tests/test_stable_sprite_route.py tests/test_speech_bubble_polish.py -q
```

Expected: all focused tests pass.

- [ ] **Step 2: Run the complete test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass with zero failures.

- [ ] **Step 3: Run the visual-tour GUI smoke**

Run:

```powershell
python tools\run_copywriting_visual_tour.py --smoke
```

Expected:

```text
copywriting_visual_tour_items=53
```

The window opens, displays the first item, closes automatically, and leaves no
DesktopCat process running.

- [ ] **Step 4: Check formatting and forbidden files**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected:

- No whitespace errors other than normal LF/CRLF warnings.
- Only intended source, test, and documentation files are modified.
- No `raw/wake_*` file is modified, staged, or deleted.
- No commit or push is performed without a new explicit user request.
