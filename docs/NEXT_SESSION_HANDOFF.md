# DesktopCat / DesktopPig Next Session Handoff

Updated: 2026-06-12 +08:00

## Project

- Repo path: `E:\Project\DesktopPig_Project`
- Remote: `https://github.com/Winton-wen/DesktopCat_Project.git`
- Branch: `main`
- Latest functional release commit: `ee8785b Polish DesktopCat companion gift experience`
- The 2026-06-12 copywriting, anniversary, menu, visual-tour, icon, direction,
  bubble, reminder-button, tests, docs, and packaging changes are committed.

## Current Goal

Build a polished, gentle DesktopCat named “呆呆” as the electronic kitten that
麻麻 and 粑粑 raise together while living apart:

```text
polished sprite pet first -> low-burden companion behaviors -> gift-quality packaging
```

The pet should feel warm, personal, quiet, and gift-like. Avoid heavy raising
systems, currencies, shops, frequent notifications, maintenance burden, and AI
chat as the main experience.

## Must Read First

Read these before making changes:

```text
docs/NEXT_SESSION_HANDOFF.md
docs/character-spec.md
docs/animation-contract-v2.md
docs/companion-experience-roadmap.md
docs/copywriting-message-catalog.md
docs/target-machine-acceptance-checklist.md
assets/production/desktop_cat/batch_manifest.json
assets/companion_messages/partner_default.json
candidate_launcher.py
gift_launcher.py
build_gift.ps1
tools/run_copywriting_visual_tour.py
tools/generate_copywriting_catalog.py
src/desktop_cat/rig_app.py
src/desktop_cat/companion_messages.py
src/desktop_cat/config.py
src/desktop_cat/time_reminders.py
```

Then run:

```powershell
git status --short --branch
git log -8 --oneline --decorate
git stash list -n 5
```

## User Preferences And Safety Rules

- Do not commit or push unless the user explicitly asks.
- Do not restore `stash@{0}: cat messaging mvp WIP` unless explicitly asked.
- Do not delete, stage, or commit untracked `raw/wake_*` experiment assets.
- Do not break or replace the accepted sprite animation baseline.
- Keep the experience offline-first and low burden.
- Low-distraction mode must not be the default.
- In low-distraction mode, automatic companion speech is disabled.
- Visual/manual target-machine QA remains necessary even when tests pass.
- PowerShell may display valid UTF-8 Chinese as mojibake; verify actual files/UI
  before treating terminal output as corruption.

## Current Git State

Last checked on 2026-06-12 after release commit `ee8785b`:

```text
## main...origin/main [ahead 1 before the handoff commit and push]
```

The only intentional untracked files are experiment assets under:

```text
assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_*
```

Treat those as experiment material and never stage them accidentally.

Deferred stash:

```text
stash@{0}: On main: cat messaging mvp WIP
```

## Accepted Animation And Runtime Baseline

- Active batch: `20260527_motion_quality_v1`
- Gift entrypoint: `gift_launcher.py`
- Preview entrypoint: `candidate_launcher.py`
- Clean frames:
  `assets/production/desktop_cat/batches/20260527_motion_quality_v1/clean`
- Wake remains the accepted 80-frame, 32fps route.
- Do not resume the rejected 96-frame wake expansion.
- Non-idle actions and speech bubbles queue instead of interrupting each other.
- Drag remains immediate.
- Clicking during sleep can wake immediately.
- `return_home` remains the accepted lively jump-back behavior.
- Last valid screen position is restored; invalid/off-screen positions fall back
  to the default corner.

## Current Companion Narrative

- 呆呆 is not 粑粑’s avatar.
- 呆呆 is the electronic kitten that 麻麻 and 粑粑 raise together.
- Default identities:
  - `pet_name`: `呆呆`
  - `mama_nickname`: `麻麻`
  - `papa_nickname`: `粑粑`
- Full editable corpus and trigger documentation:
  `docs/copywriting-message-catalog.md`
- Runtime message pack:
  `assets/companion_messages/partner_default.json`
- Old `DEFAULT_MESSAGES` copy has been removed.

## Automatic Companion Message Rules

- Special-day messages have highest priority.
- Outside low-distraction mode, the candidate pool combines:
  - messages for the current time category
  - `miss_you`
  - `busy_support`
  - `comfort`
  - `encouragement`
- A random due message is selected from that combined pool.
- Messages from unrelated time-specific categories are not mixed in.
- Cooldowns still apply per message ID.
- In low-distraction mode, automatic companion messages are skipped entirely.
- Fixed lunch/dinner/bedtime/late-night reminders remain separate.

Time categories:

```text
morning:    07:00-11:30
lunch:      11:30-13:30
afternoon:  13:30-18:00
evening:    18:00-22:30
late_night: 01:30-05:00
bedtime:    all remaining times
```

Bubble durations:

```text
first launch:             10 seconds
basic/state interactions: 3 seconds
automatic companion:      3 seconds
fixed-time reminders:     15 seconds
```

## Special Days And Anniversary

Public/personal special-day copy includes:

- Anniversary: March 24
- 粑粑 birthday: September 12
- 麻麻 birthday: October 22
- New Year, Valentine’s Day, Labor Day, 520, National Day, Christmas, year end
- Lunar Spring Festival, Lantern Festival, Dragon Boat Festival, Qixi,
  Mid-Autumn Festival, Double Ninth Festival

Anniversary template:

```text
今天是{mama_nickname}和{papa_nickname}在一起的{anniversary_year_cn}周年纪念日，希望{mama_nickname}{papa_nickname}和{pet_name}可以永远在一起呀˶>ᗜ<˶
```

`{anniversary_year_cn}` is calculated from the system year using:

```text
anniversary number = current year - 2024
```

Examples:

```text
2026-03-24 -> 二周年
2027-03-24 -> 三周年
```

Lunar special-day conversion currently has an internal 2026-2030 table.

## Current Frontend Menu

Visible right-click commands:

```text
开心一下
卖萌一下
打个招呼
向左走两步
向右走两步
睡一会儿
呆呆安静一下 / 不用保持安静啦
回到屏幕角落
退出
```

These backend-oriented commands were intentionally removed from the visible
menu:

```text
打开配置文件
打开配置文件夹
编辑陪伴语料
```

Backend helper methods and config files still exist; only the recipient-facing
menu entries were removed.

## Gift Icon And Packaging

- EXE icon uses a close-up 呆呆 head rather than the full body:
  `assets/gift/desktopcat.ico`
- Icon generator: `tools/build_gift_icon.py`
- Preview images:
  - `assets/gift/desktopcat_icon_head_preview.png`
  - `assets/gift/desktopcat_icon_size_preview.png`
- Partner README no longer exposes backend/config editing commands.

Latest deliverable:

```text
dist/DesktopCatGift_20260612_polished.zip
```

Size:

```text
82,728,010 bytes
```

SHA256:

```text
2DA08358932C00531EF2480CF28BA091A1DA54414EF14F80944368BA8FBFFB81
```

Unzipped executable:

```text
dist/DesktopCatGift/DesktopCatGift.exe
```

`dist/` and zip files are ignored and are not committed.

## Validation Already Run

Direction, bubble, copy, and reminder-button polish completed on 2026-06-12:

- Explicit left/right menu commands no longer reverse at screen edges; they
  stay in the requested orientation and stop moving when blocked.
- Autonomous walking still turns inward at screen edges.
- The visual tour now uses the runtime happy-direction preparation on every
  happy display/replay.
- Visual-tour metadata is shown in a separate status window and no longer
  changes the real speech-bubble wrapping.
- Four reviewed emoticon messages use explicit line breaks.
- Reminder buttons use `#DCEEFF`, `#C4E2FF`, and `#28527A`.

Focused regression result:

```text
67 passed
```

Current full-suite result:

```text
158 passed
```

Current full suite after adding and polishing the exhaustive copywriting visual tour:

```powershell
python -m pytest -q
```

Result:

```text
158 passed
```

Copywriting visual-tour collection:

```powershell
python tools\run_copywriting_visual_tour.py --list
```

Result:

```text
copywriting_visual_tour_items=53
```

The 53 items include the first-launch message, every basic interaction template,
three state messages, four fixed reminders, every normal companion message, and
every Gregorian/lunar special-day message.

Copywriting visual-tour GUI smoke:

```powershell
python tools\run_copywriting_visual_tour.py --smoke
```

Result: the real candidate window opened, displayed the first labeled item,
closed automatically, and left no DesktopCat process running.

Previous gift-package validation, completed before the visual-tour replacement:

Full suite:

```powershell
python -m pytest -q
```

Result:

```text
149 passed
```

Focused final document/message suite:

```text
80 passed
```

Historical backend candidate QA, run before the old combined QA script was
replaced by the exhaustive copywriting visual tour:

```powershell
python tools\run_candidate_feature_qa.py --backend-only --fast
```

Result:

```text
[PASS] pytest
[PASS] production-batch-qa
qa_reports/candidate_feature_qa_20260610_215949.txt
```

Historical GUI candidate smoke from the same retired script:

```powershell
python tools\run_candidate_feature_qa.py --smoke --fast
```

Result:

```text
qa_reports/candidate_feature_qa_20260610_220442.txt
```

Gift build:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_gift.ps1
```

Result:

```text
production_batch_full_qa_ok
Gift build complete: dist\DesktopCatGift\DesktopCatGift.exe
```

Final zip was expanded successfully, contained the EXE and Chinese README, and
the extracted EXE passed:

```powershell
DesktopCatGift.exe --smoke-ms 3000
```

No lingering DesktopCat process remained.

`git diff --check` reported no whitespace errors; only expected Windows
LF/CRLF warnings.

## Known Issues / Watch Points

- Target-machine manual acceptance has not yet been performed on the recipient’s
  actual computer.
- Lunar holiday conversion stops after 2030 unless extended.
- `return_home` is accepted but synthesized rather than a final hand-authored
  pose-sheet action.
- PyInstaller or zip overwrite may require elevated workspace permissions.
- The full copywriting catalog is generated by
  `tools/generate_copywriting_catalog.py`; regenerate it after changing runtime
  copy, README text, menu labels, or trigger rules.
- Do not run multiple production QA scopes in parallel because they write to
  shared QA directories.

## Next Recommended Steps

The project passed local manual visual acceptance and release packaging on
2026-06-12. The remaining step is delivery and, if available, a final smoke on
the recipient's Windows machine.

1. Test `dist/DesktopCatGift_20260612_polished.zip` on the target Windows
   machine.
2. Confirm first launch, 10-second welcome, Chinese text, dragging, right-click
   menu, low-distraction toggle, return to corner, icon size, and clean exit.
3. Confirm the three backend menu entries are absent.
4. Confirm normal mode produces varied automatic speech over time and
   low-distraction mode produces no automatic companion speech.
5. Stop adding features unless target-machine acceptance finds a concrete
   release blocker.

## Useful Commands

Regenerate corpus documentation:

```powershell
$env:PYTHONPATH='src'
python tools\generate_copywriting_catalog.py
```

Full tests:

```powershell
python -m pytest -q
```

Production batch QA:

```powershell
python tools\run_production_batch_qa.py --batch 20260527_motion_quality_v1 --actions idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,return_home,drag
```

Complete copywriting visual tour:

```powershell
python tools\run_copywriting_visual_tour.py
```

List every visual-tour item without opening the GUI:

```powershell
python tools\run_copywriting_visual_tour.py --list
```

Visual-tour GUI smoke:

```powershell
python tools\run_copywriting_visual_tour.py --smoke
```

Build gift:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build_gift.ps1
```

Candidate preview:

```powershell
python candidate_launcher.py 20260527_motion_quality_v1
```

## New Window Prompt

```text
请先读取并遵循 E:\Project\DesktopPig_Project\docs\NEXT_SESSION_HANDOFF.md。

我们继续 DesktopCat / DesktopPig 项目，仓库路径是 E:\Project\DesktopPig_Project。目标是把麻麻和粑粑一起养的电子小猫“呆呆”做成温柔、不打扰、像礼物一样的桌宠。

请先恢复上下文：读取 handoff 中“Must Read First”列出的文件，然后检查 git status --short --branch、git log -8 --oneline --decorate、git stash list -n 5。

最新语料、周年计算、菜单精简、头像图标、全部语料视觉巡演和包装改动已完成。最新可交付包是 dist/DesktopCatGift_20260612_polished.zip，SHA256 为 2DA08358932C00531EF2480CF28BA091A1DA54414EF14F80944368BA8FBFFB81，已通过 158 个测试、53 条语料巡演 smoke、生产批次 QA、构建、zip 解压和构建版/解压版 exe smoke。

不要恢复 stash@{0}: cat messaging mvp WIP，不要处理或误提交 raw/wake_* 实验素材，不要提交或推送，除非我明确要求。下一步优先做目标机器手动验收；如果验收通过，就停止加功能并准备交付。
```
