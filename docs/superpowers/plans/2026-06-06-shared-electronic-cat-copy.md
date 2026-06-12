# Shared Electronic Cat Copy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe DesktopCat as “呆呆”, the electronic kitten jointly raised by 麻麻 and 粑粑, with configurable family nicknames, safe message placeholders, updated companion copy, and backward-compatible configuration.

**Architecture:** Extend the existing `CatConfig` model without replacing its storage format, add one focused safe-template renderer to `companion_messages.py`, and render message text at the UI boundary in `RigDesktopCatApp`. Keep timing, animation, packaging, and message-selection behavior unchanged; only identity fields, copy, menu surface, and documentation change.

**Tech Stack:** Python 3.12, `dataclasses`, JSON, Tkinter, `unittest`/pytest, PyInstaller, PowerShell.

**Repository rule:** Do not commit or push unless the user explicitly asks. The checkpoints below replace the writing-plans skill’s normal per-task commit steps.

---

## File Map

**Modify:**

- `src/desktop_cat/config.py`
  - Define default names `呆呆`、`麻麻`、`粑粑`.
  - Add `mama_nickname` and `papa_nickname`.
  - Migrate old `partner_nickname` safely.
  - Update generated configuration README.
- `src/desktop_cat/companion_messages.py`
  - Add safe placeholder rendering for the three supported names.
- `src/desktop_cat/rig_app.py`
  - Use the renderer before showing companion messages.
  - Update basic/first-launch/status copy.
  - Remove `我想他了`.
  - Rename `今天辛苦啦` to `麻麻辛苦啦`.
- `src/desktop_cat/time_reminders.py`
  - Replace old “小猪猪” reminders with 呆呆/麻麻 wording.
- `assets/companion_messages/partner_default.json`
  - Rewrite default daily and special-day messages around the shared-kitten narrative.
- `assets/gift/README_先看我.txt`
  - Explain 呆呆’s identity and editable family nicknames/placeholders.
- `docs/copywriting-message-catalog.md`
  - Make the catalog match the new narrative and remove the deleted interaction.
- `tests/test_gift_config_experience.py`
  - Cover defaults, migration, persistence, menu removal/rename, readable copy, README.
- `tests/test_companion_messages.py`
  - Cover safe placeholder rendering and the revised default pack.
- `tests/test_stable_sprite_route.py`
  - Update exact reminder copy assertions.

**Do not modify:**

- `stash@{0}` or any Supabase messaging prototype.
- `assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_*`.
- Animation frames, action timing, random-action weights, or packaging asset scope.

---

### Task 1: Add Family Identity Fields With Backward-Compatible Migration

**Files:**

- Modify: `tests/test_gift_config_experience.py`
- Modify: `src/desktop_cat/config.py`

- [ ] **Step 1: Update the default-config test to require the new identity**

Replace the identity assertions in `test_default_config_includes_partner_facing_fields` with:

```python
self.assertEqual("呆呆", store.config.pet_name)
self.assertEqual("麻麻", store.config.mama_nickname)
self.assertEqual("粑粑", store.config.papa_nickname)
self.assertEqual("麻麻", store.config.partner_nickname)
self.assertIn("mama_nickname", raw)
self.assertIn("papa_nickname", raw)
self.assertIn("partner_nickname", raw)
```

- [ ] **Step 2: Add a failing old-config migration test**

Add:

```python
def test_old_partner_nickname_migrates_to_mama_nickname(self) -> None:
    from desktop_cat.config import ConfigStore

    with self.with_config_dir() as temp_dir:
        old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
        os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
        try:
            path = Path(temp_dir) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "pet_name": "旧名字",
                        "partner_nickname": "姐姐",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            config = ConfigStore().config

            self.assertEqual("旧名字", config.pet_name)
            self.assertEqual("姐姐", config.mama_nickname)
            self.assertEqual("粑粑", config.papa_nickname)
            self.assertEqual("姐姐", config.partner_nickname)
        finally:
            if old_config_dir is None:
                os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
            else:
                os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir
```

- [ ] **Step 3: Add a failing new-field round-trip test**

Add:

```python
def test_family_nicknames_round_trip(self) -> None:
    from desktop_cat.config import ConfigStore

    with self.with_config_dir() as temp_dir:
        old_config_dir = os.environ.get("DESKTOPCAT_CONFIG_DIR")
        os.environ["DESKTOPCAT_CONFIG_DIR"] = temp_dir
        try:
            store = ConfigStore()
            store.config.pet_name = "小呆"
            store.config.mama_nickname = "妈妈"
            store.config.papa_nickname = "爸爸"
            store.save()

            loaded = ConfigStore().config

            self.assertEqual("小呆", loaded.pet_name)
            self.assertEqual("妈妈", loaded.mama_nickname)
            self.assertEqual("爸爸", loaded.papa_nickname)
        finally:
            if old_config_dir is None:
                os.environ.pop("DESKTOPCAT_CONFIG_DIR", None)
            else:
                os.environ["DESKTOPCAT_CONFIG_DIR"] = old_config_dir
```

- [ ] **Step 4: Run the three config tests and verify RED**

Run:

```powershell
python -m pytest `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_default_config_includes_partner_facing_fields `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_old_partner_nickname_migrates_to_mama_nickname `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_family_nicknames_round_trip -q
```

Expected: FAIL because `mama_nickname` and `papa_nickname` do not exist and defaults are still `奶糖猫`/`宝贝`.

- [ ] **Step 5: Implement constants and dataclass fields**

In `src/desktop_cat/config.py`, replace the identity constants with:

```python
PET_NAME = "呆呆"
MAMA_NICKNAME = "麻麻"
PAPA_NICKNAME = "粑粑"
PARTNER_NICKNAME = MAMA_NICKNAME
```

Update `CatConfig`:

```python
@dataclass
class CatConfig:
    pet_name: str = PET_NAME
    mama_nickname: str = MAMA_NICKNAME
    papa_nickname: str = PAPA_NICKNAME
    partner_nickname: str = PARTNER_NICKNAME
    messages: list[str] = field(default_factory=lambda: DEFAULT_MESSAGES.copy())
    autostart: bool = False
    low_distraction_mode: bool = False
    first_launch_completed: bool = False
    companion_message_pack: str = DEFAULT_COMPANION_MESSAGE_PACK
    last_position: dict[str, int] | None = None
```

- [ ] **Step 6: Implement migration-aware loading**

Replace the nickname load block with:

```python
config.pet_name = self._text_or_default(raw.get("pet_name"), config.pet_name)
legacy_partner_nickname = self._text_or_default(
    raw.get("partner_nickname"),
    config.partner_nickname,
)
config.mama_nickname = self._text_or_default(
    raw.get("mama_nickname"),
    legacy_partner_nickname,
)
config.papa_nickname = self._text_or_default(
    raw.get("papa_nickname"),
    config.papa_nickname,
)
config.partner_nickname = legacy_partner_nickname
```

This preserves the exact old value for compatibility while making `mama_nickname` the runtime-facing field.

- [ ] **Step 7: Save the new fields**

Add to the `payload` in `ConfigStore.save`:

```python
"mama_nickname": self.config.mama_nickname,
"papa_nickname": self.config.papa_nickname,
```

Keep:

```python
"partner_nickname": self.config.partner_nickname,
```

- [ ] **Step 8: Update malformed-field expectations**

In `test_malformed_field_types_fall_back_to_safe_defaults`, include malformed values:

```python
"mama_nickname": {},
"papa_nickname": [],
```

Assert:

```python
self.assertEqual("呆呆", config.pet_name)
self.assertEqual("麻麻", config.mama_nickname)
self.assertEqual("粑粑", config.papa_nickname)
self.assertEqual("麻麻", config.partner_nickname)
```

- [ ] **Step 9: Run config tests and verify GREEN**

Run:

```powershell
python -m pytest tests\test_gift_config_experience.py -q
```

Expected: Tests may still fail only where old copy/menu assertions have not yet been updated. The new identity/migration tests must pass.

- [ ] **Step 10: Checkpoint without committing**

Run:

```powershell
git diff -- src\desktop_cat\config.py tests\test_gift_config_experience.py
```

Confirm no unrelated files and no `raw/wake_*` paths are staged.

---

### Task 2: Add Safe Dynamic Placeholder Rendering

**Files:**

- Modify: `tests/test_companion_messages.py`
- Modify: `src/desktop_cat/companion_messages.py`
- Modify: `src/desktop_cat/rig_app.py`

- [ ] **Step 1: Write failing renderer tests**

Add to `tests/test_companion_messages.py`:

```python
def test_render_companion_text_replaces_supported_family_placeholders(self) -> None:
    from desktop_cat.companion_messages import render_companion_text

    rendered = render_companion_text(
        "{pet_name}提醒{mama_nickname}吃饭，{papa_nickname}也会放心。",
        pet_name="呆呆",
        mama_nickname="麻麻",
        papa_nickname="粑粑",
    )

    self.assertEqual("呆呆提醒麻麻吃饭，粑粑也会放心。", rendered)

def test_render_companion_text_preserves_unknown_placeholders(self) -> None:
    from desktop_cat.companion_messages import render_companion_text

    rendered = render_companion_text(
        "{pet_name}和{unknown_name}一起玩。",
        pet_name="呆呆",
        mama_nickname="麻麻",
        papa_nickname="粑粑",
    )

    self.assertEqual("呆呆和{unknown_name}一起玩。", rendered)
```

- [ ] **Step 2: Run renderer tests and verify RED**

Run:

```powershell
python -m pytest `
  tests\test_companion_messages.py::CompanionMessageTests::test_render_companion_text_replaces_supported_family_placeholders `
  tests\test_companion_messages.py::CompanionMessageTests::test_render_companion_text_preserves_unknown_placeholders -q
```

Expected: FAIL with import error because `render_companion_text` does not exist.

- [ ] **Step 3: Implement a focused safe renderer**

Add to `src/desktop_cat/companion_messages.py`:

```python
class _CompanionTextValues(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def render_companion_text(
    text: str,
    *,
    pet_name: str,
    mama_nickname: str,
    papa_nickname: str,
) -> str:
    values = _CompanionTextValues(
        pet_name=pet_name,
        mama_nickname=mama_nickname,
        papa_nickname=papa_nickname,
    )
    try:
        return text.format_map(values)
    except ValueError:
        return text
```

The `ValueError` fallback protects old custom text containing unmatched braces.

- [ ] **Step 4: Run renderer tests and verify GREEN**

Run:

```powershell
python -m pytest tests\test_companion_messages.py -q
```

Expected: All companion-message tests pass.

- [ ] **Step 5: Write a failing runtime integration assertion**

Extend `test_rig_app_has_companion_message_runtime_flow`:

```python
self.assertIn("render_companion_text", source)
self.assertIn("mama_nickname", source)
self.assertIn("papa_nickname", source)
```

- [ ] **Step 6: Run the integration assertion and verify RED**

Run:

```powershell
python -m pytest tests\test_companion_messages.py::CompanionMessageTests::test_rig_app_has_companion_message_runtime_flow -q
```

Expected: FAIL because `RigDesktopCatApp` does not call the renderer.

- [ ] **Step 7: Render at the UI boundary**

Import the renderer in `src/desktop_cat/rig_app.py`:

```python
from .companion_messages import (
    DEFAULT_COMPANION_CHECK_MS,
    CompanionMessage,
    load_default_companion_pack,
    load_companion_pack,
    render_companion_text,
    select_companion_message,
)
```

Replace `show_companion_message` text display with:

```python
text = render_companion_text(
    message.text,
    pet_name=self.store.config.pet_name,
    mama_nickname=self.store.config.mama_nickname,
    papa_nickname=self.store.config.papa_nickname,
)
self.bubble.show(text, *self.pet_anchor(), hide_ms=12000)
```

- [ ] **Step 8: Run the companion tests and verify GREEN**

Run:

```powershell
python -m pytest tests\test_companion_messages.py -q
```

Expected: PASS.

- [ ] **Step 9: Checkpoint without committing**

Run:

```powershell
git diff -- src\desktop_cat\companion_messages.py src\desktop_cat\rig_app.py tests\test_companion_messages.py
```

---

### Task 3: Rewrite Runtime Copy and Remove the Obsolete Interaction

**Files:**

- Modify: `tests/test_gift_config_experience.py`
- Modify: `src/desktop_cat/rig_app.py`

- [ ] **Step 1: Replace the old menu test with the new behavior**

Replace `test_rig_menu_has_couple_specific_gift_interactions` with:

```python
def test_rig_menu_uses_shared_kitten_interaction(self) -> None:
    from desktop_cat import rig_app

    source = inspect.getsource(rig_app.RigDesktopCatApp)
    menu_source = inspect.getsource(rig_app.RigDesktopCatApp.on_menu)

    self.assertNotIn("miss_partner", source)
    self.assertNotIn("MISS_PARTNER_MESSAGES", inspect.getsource(rig_app))
    self.assertNotIn("我想他了", menu_source)
    self.assertIn("tired_today", source)
    self.assertIn("麻麻辛苦啦", menu_source)
```

- [ ] **Step 2: Add a failing copy-identity test**

Add:

```python
def test_runtime_copy_treats_daidai_as_shared_kitten(self) -> None:
    from desktop_cat import rig_app

    first_launch_source = inspect.getsource(rig_app.RigDesktopCatApp.show_first_launch_message)
    all_runtime_copy = "\n".join(
        [
            *rig_app.TEXT.values(),
            *rig_app.TIRED_TODAY_MESSAGES,
            first_launch_source,
        ]
    )

    self.assertIn("呆呆", all_runtime_copy)
    self.assertIn("麻麻", all_runtime_copy)
    self.assertNotIn("替他陪你", all_runtime_copy)
    self.assertNotIn("当我抱你", all_runtime_copy)
```

- [ ] **Step 3: Run both tests and verify RED**

Run:

```powershell
python -m pytest `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_rig_menu_uses_shared_kitten_interaction `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_runtime_copy_treats_daidai_as_shared_kitten -q
```

Expected: FAIL because the old menu/list still exists and runtime copy has not been rewritten.

- [ ] **Step 4: Rewrite `TEXT`**

Use:

```python
TEXT = {
    "pet": "摸摸头，我在呢。",
    "happy": "麻麻看，呆呆跳一下！",
    "cute": "呆呆今天也可爱吗？",
    "wave": "麻麻，看这里呀。",
    "sleep": "呆呆先贴着睡一会儿。",
    "wake": "醒啦，继续陪麻麻。",
    "walk_left": "我去左边转两步。",
    "walk_right": "我去右边转两步。",
}
```

- [ ] **Step 5: Remove the obsolete miss-partner behavior**

Delete:

```python
MISS_PARTNER_MESSAGES = [...]
```

Delete:

```python
def miss_partner(self) -> None:
    ...
```

Delete the menu command:

```python
menu.add_command(label="我想他了", command=self.miss_partner)
```

- [ ] **Step 6: Rewrite the tired-today replies**

Use:

```python
TIRED_TODAY_MESSAGES = [
    "麻麻今天辛苦啦，先摸摸呆呆，慢慢呼吸一下。",
    "忙完这一阵就休息一会儿吧，呆呆在这里陪麻麻。",
    "麻麻已经很努力啦。喝点水，今晚也要对自己温柔一点。",
]
```

Keep `tired_today` using `action="cute"`.

- [ ] **Step 7: Rename the menu item**

Use:

```python
menu.add_command(label="麻麻辛苦啦", command=self.tired_today)
```

- [ ] **Step 8: Rewrite first-launch and status copy**

Use:

```python
self.bubble.show(
    f"{self.store.config.pet_name}来啦！以后就是{self.store.config.mama_nickname}和"
    f"{self.store.config.papa_nickname}一起养的电子小猫啦。",
    *self.pet_anchor(),
    hide_ms=9000,
)
```

Use:

```python
self.say(
    "呆呆会安静一点陪麻麻。"
    if enabled
    else "呆呆恢复正常陪伴啦。"
)
```

Use:

```python
self.bubble.show(
    "呆呆跳回屏幕角落啦。",
    target_x + WIDTH // 2,
    target_y + (HEIGHT - DISPLAY_SIZE) // 2,
)
```

- [ ] **Step 9: Rename the gift quit menu label**

Replace:

```python
label="退出 rig 预览"
```

with:

```python
label="退出"
```

This removes developer-facing wording from the gift runtime without changing quit behavior.

- [ ] **Step 10: Run runtime/gift tests**

Run:

```powershell
python -m pytest tests\test_gift_config_experience.py tests\test_speech_bubble_polish.py tests\test_rig_preview.py -q
```

Expected: PASS after old exact-copy assertions are updated in the same test file.

- [ ] **Step 11: Checkpoint without committing**

Run:

```powershell
git diff -- src\desktop_cat\rig_app.py tests\test_gift_config_experience.py
```

---

### Task 4: Rewrite Time Reminders Without Changing Scheduling

**Files:**

- Modify: `tests/test_stable_sprite_route.py`
- Modify: `tests/test_gift_config_experience.py`
- Modify: `src/desktop_cat/time_reminders.py`

- [ ] **Step 1: Update the exact expected reminder strings**

In `test_time_reminders_match_requested_companion_windows`, use:

```python
self.assertEqual("麻麻要记得按时吃午饭呀，呆呆会监督你的。", reminder_for_time(time(11, 30)).message)
self.assertEqual("麻麻要记得按时吃午饭呀，呆呆会监督你的。", reminder_for_time(time(13, 29)).message)
self.assertIsNone(reminder_for_time(time(13, 30)))
self.assertEqual("麻麻该吃晚饭啦，不可以随便糊弄过去。", reminder_for_time(time(17, 0)).message)
self.assertEqual("麻麻该吃晚饭啦，不可以随便糊弄过去。", reminder_for_time(time(18, 59)).message)
self.assertEqual("已经很晚啦，呆呆想让麻麻早点休息。", reminder_for_time(time(0, 0)).message)
self.assertEqual("已经很晚啦，呆呆想让麻麻早点休息。", reminder_for_time(time(1, 29)).message)
self.assertEqual(
    "麻麻还在忙吗？呆呆陪你收个尾，然后我们早点睡觉吧。",
    reminder_for_time(time(1, 30)).message,
)
self.assertEqual(
    "麻麻还在忙吗？呆呆陪你收个尾，然后我们早点睡觉吧。",
    reminder_for_time(time(4, 59)).message,
)
self.assertIsNone(reminder_for_time(time(5, 0)))
```

- [ ] **Step 2: Update the readable-Chinese test**

Import and include all four reminders:

```python
from desktop_cat.time_reminders import (
    BEDTIME_REMINDER,
    DINNER_REMINDER,
    LATE_NIGHT_REMINDER,
    LUNCH_REMINDER,
)
```

Assert `麻麻` and `呆呆` are present and `小猪猪` is absent.

- [ ] **Step 3: Run reminder tests and verify RED**

Run:

```powershell
python -m pytest `
  tests\test_stable_sprite_route.py::StableSpriteRouteTests::test_time_reminders_match_requested_companion_windows `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_default_partner_facing_text_is_readable_chinese -q
```

Expected: FAIL with old reminder strings.

- [ ] **Step 4: Replace reminder constants**

In `src/desktop_cat/time_reminders.py`:

```python
LUNCH_REMINDER = TimeReminder(
    "lunch",
    "麻麻要记得按时吃午饭呀，呆呆会监督你的。",
)
DINNER_REMINDER = TimeReminder(
    "dinner",
    "麻麻该吃晚饭啦，不可以随便糊弄过去。",
)
BEDTIME_REMINDER = TimeReminder(
    "bedtime",
    "已经很晚啦，呆呆想让麻麻早点休息。",
)
LATE_NIGHT_REMINDER = TimeReminder(
    "late_night",
    "麻麻还在忙吗？呆呆陪你收个尾，然后我们早点睡觉吧。",
)
```

- [ ] **Step 5: Run reminder tests and verify GREEN**

Run:

```powershell
python -m pytest tests\test_stable_sprite_route.py tests\test_gift_config_experience.py -q
```

Expected: PASS apart from any later README/catalog assertions not yet updated.

- [ ] **Step 6: Checkpoint without committing**

Run:

```powershell
git diff -- src\desktop_cat\time_reminders.py tests\test_stable_sprite_route.py
```

---

### Task 5: Rewrite the Default Companion Pack Around the Shared Kitten

**Files:**

- Modify: `tests/test_companion_messages.py`
- Modify: `assets/companion_messages/partner_default.json`

- [ ] **Step 1: Add a failing narrative/placeholder test**

Add:

```python
def test_default_pack_uses_shared_kitten_narrative_and_placeholders(self) -> None:
    from desktop_cat.companion_messages import load_companion_pack

    pack = load_companion_pack(ROOT / "assets" / "companion_messages" / "partner_default.json")
    combined = "\n".join(message.text for message in pack.messages)

    self.assertIn("{mama_nickname}", combined)
    self.assertIn("{papa_nickname}", combined)
    self.assertIn("{pet_name}", combined)
    self.assertNotIn("替我", combined)
    self.assertNotIn("当我抱你", combined)
    self.assertNotIn("我一直站在你这边", combined)
```

- [ ] **Step 2: Run the new test and verify RED**

Run:

```powershell
python -m pytest tests\test_companion_messages.py::CompanionMessageTests::test_default_pack_uses_shared_kitten_narrative_and_placeholders -q
```

Expected: FAIL because the current pack has none of the new placeholders and still contains old proxy wording.

- [ ] **Step 3: Replace the pack messages**

Keep IDs, categories, cooldowns, actions, and special dates stable. Replace only text:

```json
[
  {
    "id": "morning_01",
    "text": "早上好呀，{mama_nickname}。{pet_name}来陪你慢慢开始今天啦。"
  },
  {
    "id": "morning_02",
    "text": "{mama_nickname}先伸个懒腰吧，{pet_name}也要醒醒啦。"
  },
  {
    "id": "lunch_01",
    "text": "{mama_nickname}要好好吃午饭，{pet_name}会认真监督你的。"
  },
  {
    "id": "afternoon_01",
    "text": "下午也辛苦啦。累了就和{pet_name}一起发一会儿呆。"
  },
  {
    "id": "evening_01",
    "text": "{mama_nickname}忙完一天啦，{pet_name}来贴贴你。{papa_nickname}也会想让你好好休息。"
  },
  {
    "id": "bedtime_01",
    "text": "很晚啦，{pet_name}想和{mama_nickname}一起早点睡觉。"
  },
  {
    "id": "late_night_01",
    "text": "{mama_nickname}还没睡吗？{pet_name}要皱眉啦，我们忙完就休息吧。"
  },
  {
    "id": "miss_you_01",
    "text": "{pet_name}也想{papa_nickname}啦。等以后住在一起，我们就能天天在一个家里啦。"
  },
  {
    "id": "busy_support_01",
    "text": "{mama_nickname}先忙你的，{pet_name}会安安静静待在这里。"
  },
  {
    "id": "comfort_01",
    "text": "不顺利也没关系。{pet_name}先陪{mama_nickname}缓一缓。"
  },
  {
    "id": "encouragement_01",
    "text": "{mama_nickname}今天已经做得很好啦，{pet_name}看见了。"
  },
  {
    "id": "special_valentine_0214",
    "text": "今天是很适合贴贴的一天。{pet_name}要把{mama_nickname}和{papa_nickname}都记在小心心里。"
  },
  {
    "id": "special_love_day_0520",
    "text": "今天的{pet_name}要更黏人一点，因为我们是一起养大的一家人呀。"
  },
  {
    "id": "special_year_end_1231",
    "text": "今年辛苦啦。{pet_name}会陪着{mama_nickname}和{papa_nickname}一起走进新的一年。"
  }
]
```

Apply these text values inside the existing JSON objects; do not replace metadata or reorder IDs.

- [ ] **Step 4: Validate JSON and run message tests**

Run:

```powershell
python -c "import json, pathlib; json.loads(pathlib.Path('assets/companion_messages/partner_default.json').read_text(encoding='utf-8')); print('partner_default_json_ok')"
python -m pytest tests\test_companion_messages.py -q
```

Expected:

```text
partner_default_json_ok
```

and all companion tests pass.

- [ ] **Step 5: Checkpoint without committing**

Run:

```powershell
git diff -- assets\companion_messages\partner_default.json tests\test_companion_messages.py
```

---

### Task 6: Update Generated README, Gift README, and Copy Catalog

**Files:**

- Modify: `tests/test_gift_config_experience.py`
- Modify: `src/desktop_cat/config.py`
- Modify: `assets/gift/README_先看我.txt`
- Modify: `docs/copywriting-message-catalog.md`

- [ ] **Step 1: Add failing README assertions**

Extend `test_open_config_file_creates_readme_for_non_developers`:

```python
self.assertIn("mama_nickname", text)
self.assertIn("papa_nickname", text)
self.assertIn("{pet_name}", text)
self.assertIn("{mama_nickname}", text)
self.assertIn("{papa_nickname}", text)
```

Extend `test_gift_readme_is_partner_facing`:

```python
self.assertIn("呆呆", text)
self.assertIn("麻麻", text)
self.assertIn("粑粑", text)
self.assertIn("一起养", text)
```

Add:

```python
def test_copywriting_catalog_matches_shared_kitten_narrative(self) -> None:
    text = (ROOT / "docs" / "copywriting-message-catalog.md").read_text(encoding="utf-8")

    self.assertIn("呆呆", text)
    self.assertIn("mama_nickname", text)
    self.assertIn("papa_nickname", text)
    self.assertIn("{mama_nickname}", text)
    self.assertNotIn("## E. 右键“我想他了”随机回复", text)
    self.assertIn("麻麻辛苦啦", text)
```

- [ ] **Step 2: Run README/catalog tests and verify RED**

Run:

```powershell
python -m pytest `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_open_config_file_creates_readme_for_non_developers `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_gift_readme_is_partner_facing `
  tests\test_gift_config_experience.py::GiftConfigExperienceTests::test_copywriting_catalog_matches_shared_kitten_narrative -q
```

Expected: FAIL because documentation still describes the old fields/narrative.

- [ ] **Step 3: Replace generated configuration README**

Update `README_TEXT` in `src/desktop_cat/config.py` to explain:

```text
DesktopCat 配置说明

呆呆是麻麻和粑粑一起养的电子小猫。

config.json 里的称呼设置：
- pet_name: 小猫名字，默认“呆呆”。
- mama_nickname: 呆呆对她的称呼，默认“麻麻”。
- papa_nickname: 呆呆对你的称呼，默认“粑粑”。
- partner_nickname: 旧版本兼容字段，一般不用再修改。

其他设置：
- low_distraction_mode: true 表示更安静，false 表示正常陪伴。
- companion_message_pack: 当前使用的陪伴语料文件路径。
- first_launch_completed: 是否已经显示过首次欢迎语。
- last_position: 呆呆上次停留的位置。

companion_messages/partner_custom.json 是可编辑陪伴语料。
text 支持 {pet_name}、{mama_nickname}、{papa_nickname}。
也可以调整 category、cooldown_hours、action。
特殊日子使用 category=special_day 和 MM-DD 格式的 month_day。
如果改坏了，删除 partner_custom.json，再从右键菜单点“编辑陪伴语料”重新生成。
```

- [ ] **Step 4: Rewrite the gift README**

Use concise partner-facing copy:

```text
这是麻麻和粑粑一起养的电子小猫“呆呆”。

现在我们还不能一起养一只真正的小猫，所以先让呆呆住在你的桌面上，陪你学习、工作、吃饭和休息。

第一次使用：
1. 先解压整个 DesktopCatGift 文件夹。
2. 双击 DesktopCatGift.exe，呆呆会出现在桌面角落。
3. 可以左键摸摸呆呆，也可以拖着它换位置。
4. 右键呆呆可以互动、回到角落、编辑陪伴语料或退出。

默认称呼：
- 小猫：呆呆
- 你：麻麻
- 我：粑粑

右键点“打开配置文件”可以修改 pet_name、mama_nickname 和 papa_nickname。
右键点“编辑陪伴语料”可以修改呆呆说的话。
语料支持 {pet_name}、{mama_nickname}、{papa_nickname}。

如果呆呆跑到奇怪的位置，右键点“回到屏幕角落”。
如果想关闭，右键点“退出”。

希望电子呆呆能先陪我们慢慢等到真正一起生活、一起养猫的那一天。
```

- [ ] **Step 5: Rewrite the catalog to match runtime truth**

In `docs/copywriting-message-catalog.md`:

- Change defaults to `呆呆`、`麻麻`、`粑粑`.
- Document `mama_nickname` and `papa_nickname`.
- Remove the entire `我想他了` section.
- Rename `今天辛苦啦` to `麻麻辛苦啦`.
- Replace all B/C/F/G/H entries with the exact runtime/default-pack text from Tasks 3-5.
- Document the three placeholders near the top and in JSON examples.
- Preserve stable item IDs where possible; renumber section letters only if needed for clarity.
- Mark `partner_nickname` as compatibility-only.

- [ ] **Step 6: Run README/catalog tests and verify GREEN**

Run:

```powershell
python -m pytest tests\test_gift_config_experience.py -q
```

Expected: PASS.

- [ ] **Step 7: Checkpoint without committing**

Run:

```powershell
git diff -- src\desktop_cat\config.py assets\gift\README_先看我.txt docs\copywriting-message-catalog.md tests\test_gift_config_experience.py
```

---

### Task 7: Full Regression, QA, Build, and Deliverable Smoke

**Files:**

- No planned source edits unless verification exposes a reproducible defect.
- Generated/ignored outputs:
  - `qa_reports/candidate_feature_qa_*.txt`
  - `dist/DesktopCatGift/`
  - `dist/DesktopCatGift_20260605_polished.zip`

- [ ] **Step 1: Run focused copy/config tests**

Run:

```powershell
python -m pytest `
  tests\test_companion_messages.py `
  tests\test_gift_config_experience.py `
  tests\test_stable_sprite_route.py `
  tests\test_speech_bubble_polish.py `
  tests\test_rig_preview.py -q
```

Expected: all selected tests pass.

- [ ] **Step 2: Run the full relevant suite**

Run:

```powershell
python -m pytest `
  tests\test_stable_sprite_route.py `
  tests\test_production_pipeline.py `
  tests\test_rig_preview.py `
  tests\test_companion_messages.py `
  tests\test_low_distraction_mode.py `
  tests\test_time_rhythm.py `
  tests\test_speech_bubble_polish.py `
  tests\test_gift_config_experience.py `
  tests\test_candidate_feature_qa_script.py
```

Expected: zero failures. The count must be at least the current 118 tests plus newly added tests.

- [ ] **Step 3: Run candidate backend fast QA**

Run:

```powershell
python tools\run_candidate_feature_qa.py --backend-only --fast
```

Expected:

```text
[PASS] pytest
[PASS] production-batch-qa
```

- [ ] **Step 4: Build the gift**

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_gift.ps1
```

Expected:

```text
production_batch_full_qa_ok batch=20260527_motion_quality_v1 ...
Gift build complete: dist\DesktopCatGift\DesktopCatGift.exe
```

If Windows denies deletion of old `dist/DesktopCatGift`, rerun the same build command with approved non-sandbox permission. Do not change the build script to work around an environment permission issue.

- [ ] **Step 5: Verify packaged assets contain the new narrative**

Run:

```powershell
python -c "import json, pathlib; root=pathlib.Path('dist/DesktopCatGift'); data=json.loads((root/'_internal/assets/companion_messages/partner_default.json').read_text(encoding='utf-8')); text='\n'.join(x['text'] for x in data['messages']); print('呆呆' in text or '{pet_name}' in text); print('{mama_nickname}' in text); print('{papa_nickname}' in text); print('我想他了' not in text)"
```

Expected:

```text
True
True
True
True
```

- [ ] **Step 6: Run built-exe smoke with isolated config**

Run:

```powershell
$env:DESKTOPCAT_CONFIG_DIR = Join-Path (Get-Location) 'desktopcat_smoke_config_shared_kitten'
.\dist\DesktopCatGift\DesktopCatGift.exe --smoke-ms 3000
Remove-Item Env:DESKTOPCAT_CONFIG_DIR
```

Then verify:

```powershell
python -c "import json, pathlib; c=json.loads(pathlib.Path('desktopcat_smoke_config_shared_kitten/config.json').read_text(encoding='utf-8')); print(c['pet_name'], c['mama_nickname'], c['papa_nickname'])"
Get-Process | Where-Object { $_.ProcessName -like '*DesktopCatGift*' }
```

Expected Unicode values: `呆呆 麻麻 粑粑`; no process output.

- [ ] **Step 7: Rebuild the polished zip**

Run:

```powershell
Compress-Archive `
  -LiteralPath 'dist\DesktopCatGift' `
  -DestinationPath 'dist\DesktopCatGift_20260605_polished.zip' `
  -Force
```

If overwrite is denied by the sandbox, rerun this exact command with approved non-sandbox permission.

- [ ] **Step 8: Run zip extraction smoke**

Run:

```powershell
Expand-Archive `
  -LiteralPath 'dist\DesktopCatGift_20260605_polished.zip' `
  -DestinationPath 'desktopcat_zip_smoke_shared_kitten' `
  -Force

$env:DESKTOPCAT_CONFIG_DIR = Join-Path (Get-Location) 'desktopcat_zip_smoke_config_shared_kitten'
.\desktopcat_zip_smoke_shared_kitten\DesktopCatGift\DesktopCatGift.exe --smoke-ms 3000
Remove-Item Env:DESKTOPCAT_CONFIG_DIR
```

Verify:

```powershell
Test-Path 'desktopcat_zip_smoke_config_shared_kitten\config.json'
Get-Process | Where-Object { $_.ProcessName -like '*DesktopCatGift*' }
```

Expected: `True`; no process output.

- [ ] **Step 9: Clean only this plan’s temporary smoke directories**

Before deletion, resolve and verify these exact paths are inside `E:\Project\DesktopPig_Project`:

```text
desktopcat_smoke_config_shared_kitten
desktopcat_zip_smoke_shared_kitten
desktopcat_zip_smoke_config_shared_kitten
```

Use PowerShell `Remove-Item -LiteralPath ... -Recurse -Force`. If deletion is denied for packaged exe/assets, request approved non-sandbox execution for these exact directories only.

- [ ] **Step 10: Final worktree audit**

Run:

```powershell
git status --short --branch
git diff --stat
git diff --check
git stash list -n 5
```

Confirm:

- `stash@{0}: cat messaging mvp WIP` remains untouched.
- `raw/wake_*` remains untracked and unstaged.
- No smoke directories remain.
- No commit or push has occurred.
- Only the intended source, tests, JSON, README, design, plan, catalog, and acceptance-checklist changes are present.

---

## Completion Checklist

- [ ] Default identity is `呆呆 / 麻麻 / 粑粑`.
- [ ] Old `partner_nickname` configs migrate without breaking.
- [ ] Three safe placeholders render correctly.
- [ ] Unknown/malformed placeholders do not crash the app.
- [ ] `我想他了` and its reply list are removed.
- [ ] `麻麻辛苦啦` works with three 呆呆 replies.
- [ ] Runtime copy consistently treats 呆呆 as the jointly raised kitten.
- [ ] Reminders address 麻麻 naturally.
- [ ] Default pack uses the new family narrative.
- [ ] Config README, gift README, and catalog are synchronized.
- [ ] Full tests, candidate QA, gift build, exe smoke, and zip smoke pass.
- [ ] Supabase stash and `raw/wake_*` remain untouched.
- [ ] No commit or push is made without explicit user instruction.
