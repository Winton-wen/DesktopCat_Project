# DesktopCat / DesktopPig Next Session Handoff

Updated: 2026-06-13 +08:00

## Project

- Repo path: `E:\Project\DesktopPig_Project`
- Remote: `https://github.com/Winton-wen/DesktopCat_Project.git`
- Branch: `main`
- The final release work is committed and pushed on `main`.
- The 2026-06-12 copywriting, anniversary, menu, visual-tour, icon, direction,
  bubble, reminder-button, tests, docs, and packaging changes are committed.
- The busy-action request drop behavior, action-bound bubble lifecycle,
  full-cat white-background icon, legacy `奶糖猫/宝贝` config migration,
  first-launch entry, exit/re-entry, sleep silence, and versioned welcome are
  implemented, verified, committed, pushed, and packaged.

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

Expected after the final release commit and local artifact cleanup:

```text
## main...origin/main
```

The source tree, engineering documentation, accepted production batch, reference
images, and final recipient ZIP are retained. Generated build directories, old
ZIPs, old extracted smoke copies, local backups, caches, and experimental
`raw/wake_*` material are removed locally to reduce disk usage.

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
- Ordinary action-and-bubble requests are accepted only while the pet is idle.
- Requests received during a non-idle action are discarded immediately rather
  than queued, and their paired bubbles are not shown later.
- Action-triggered bubbles are owned by their matching action. They disappear
  when that action finishes or is replaced, including when clicking transitions
  into dragging.
- Idle click feedback is confirmed on mouse release only when no drag occurred,
  so pressing and dragging never flashes the `clicked` action or petting bubble.
- Queued action bubbles are discarded if their action finishes before they are
  shown.
- The speech-bubble queue remains independent for no-action messages such as
  fixed reminders, so one visible bubble is not overwritten by another.
- Drag remains immediate.
- Clicking during sleep can wake immediately.
- `return_home` remains the accepted lively jump-back behavior.
- Last valid screen position is restored; invalid/off-screen positions fall back
  to the default corner.
- On the true first launch, the kitten starts beyond the lower-right screen
  edge, walks left into the default lower-right position, and only then shows
  the first-launch welcome action and bubble.
- Welcome completion is versioned. Existing configs with the legacy
  `first_launch_completed=true` but no current `welcome_version` receive the
  current welcome once, then persist the version so it does not repeat.
- Normal menu exit interrupts the current action and walks through the nearest
  left or right screen edge before shutdown.
- The next launch walks in from the same edge near the saved vertical position,
  then consumes the saved exit state and returns to idle.
- Automatic companion messages and fixed-time reminders are suppressed during
  `sleep_in` and `sleep`; suppressed speech is not queued or marked as shown.

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
- Automatic messages rejected because the pet is busy are not shown and do not
  consume their cooldown.
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

- EXE icon uses the complete seated cat from `参考图/1.png` on its original
  warm-white background, tightly cropped to fill a normal desktop icon:
  `assets/gift/desktopcat.ico`
- Icon generator: `tools/build_gift_icon.py`
- Preview images:
  - `assets/gift/desktopcat_icon_head_preview.png`
  - `assets/gift/desktopcat_icon_size_preview.png`
- Partner README no longer exposes backend/config editing commands.

Latest deliverable containing all current uncommitted changes:

```text
dist/DesktopCatGift_20260613_final.zip
```

Size:

```text
83,344,029 bytes
```

SHA256:

```text
B383ED1FD450EA4AA52ED434CD3FE08DA11F5EB4802A861AD0F3968E8C11DFAD
```

Unzipped executable:

```text
dist/呆呆/呆呆.exe
```

`dist/` and zip files are ignored and are not committed.

This package contains the busy-request behavior, action-bound bubble lifecycle,
nearest-edge exit/re-entry animation, sleep-time speech suppression, the
`呆呆/呆呆.exe` recipient-facing name, first-launch right-edge entry, full-cat
icon, current `麻麻/呆呆/粑粑` defaults, and automatic migration of the historical
`奶糖猫/宝贝` defaults.

## Validation Already Run

Exit/re-entry, sleep silence, and Chinese gift naming completed locally on
2026-06-14:

- Menu exit interrupts the current action and walks through the nearest
  horizontal screen edge before shutdown.
- A fresh first launch starts beyond the lower-right screen edge, walks into
  the default corner position, and defers the welcome action and bubble until
  entry completes.
- The next launch starts outside the saved side, walks fully into view near the
  saved vertical position, then consumes the saved exit metadata.
- Automatic companion and fixed-time reminders do not display or consume state
  during `sleep_in` or `sleep`.
- The build output and ZIP contents are `呆呆/呆呆.exe`; directory and executable
  Unicode code points were verified after extraction.
- Fresh full-suite result: `193 passed`.
- Production batch QA, build, fresh-start smoke, saved-entry smoke, ZIP
  extraction, and extracted EXE smoke passed.

Action-bound bubble lifecycle completed locally on 2026-06-13:

- Action-triggered interaction, first-launch, and automatic companion bubbles
  are bound to the action token that created them.
- Natural action completion and forced action replacement clear only matching
  current or queued bubbles.
- Starting a drag clears the click action bubble immediately.
- Fixed reminders and state-only bubbles remain unowned and keep their
  independent timers.
- Focused result: `117 passed`.
- Fresh full-suite result: `176 passed`.
- Production batch QA and gift rebuild passed.
- Rebuilt and extracted EXE smoke both exited with no lingering process after
  allowing for PyInstaller startup time.

Busy-action request drop behavior completed locally on 2026-06-12:

- Removed the runtime action queue.
- Ordinary action-and-bubble requests received while the pet is non-idle are
  discarded immediately and are never replayed.
- An idle mouse press waits for release. If no drag occurred, release starts
  `clicked` immediately; dragging starts without any petting action or bubble.
- Rejected happy and walk requests do not mutate direction or motion state.
- Automatic companion messages rejected while busy do not show a bubble and do
  not consume cooldown.
- Drag, wake-from-sleep, return-home, first-launch, and visual-tour force paths
  remain available.
- The independent speech-bubble queue remains for no-action messages.

Focused behavior result:

```text
131 passed
```

Fresh full-suite result after icon and legacy-config migration:

```text
169 passed
```

Fresh visual-tour GUI smoke:

```text
copywriting_visual_tour_items=53
desktopcat_lingering_processes=0
```

Fresh gift-package validation:

```text
production_batch_full_qa_ok
built_smoke_exit=0 migrated=True pet_name=呆呆 mama_nickname=麻麻
zip_smoke_exit=0 migrated=True pet_name=呆呆 mama_nickname=麻麻
desktopcat_lingering_processes=0
```

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
169 passed
```

Current full suite after adding and polishing the exhaustive copywriting visual tour:

```powershell
python -m pytest -q
```

Result:

```text
169 passed
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
Gift build complete: dist\呆呆\呆呆.exe
```

Final zip was expanded successfully, contained the EXE and Chinese README, and
the extracted EXE passed:

```powershell
呆呆.exe --smoke-ms 3000
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
- The final ZIP remains ignored by Git and is retained locally for direct
  delivery.

## Next Recommended Steps

The project passed local visual acceptance and release packaging on 2026-06-13.
The remaining step is target-machine manual acceptance. Do not add more features
unless that acceptance finds a concrete release blocker.

1. Test `dist/DesktopCatGift_20260613_final.zip` on the target Windows
   machine.
2. Confirm first launch, action-synchronized welcome bubble, Chinese text,
   dragging, right-click menu, low-distraction toggle, return to corner, icon
   size, and clean exit.
3. Confirm every action-triggered bubble disappears when its matching action
   ends, while fixed reminders remain visible for their independent duration.
4. Confirm menu exit walks through the nearest edge and the next launch walks
   back in from that same side near the saved vertical position.
5. Confirm no automatic or fixed-time speech appears while the kitten is
   entering sleep or sleeping.
6. Confirm the extracted folder and executable are `呆呆/呆呆.exe`.
7. Confirm the three backend menu entries are absent.
8. Confirm normal mode produces varied automatic speech over time and
   low-distraction mode produces no automatic companion speech.
9. Confirm a machine with an old `奶糖猫/宝贝` config starts as `呆呆/麻麻`.
10. If target-machine acceptance passes, stop changing the package and wait for
   an explicit request before committing or pushing the local changes.

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

最终发布内容已经提交并推送到 main。忙碌动作请求丢弃、动作结束同步关闭对应气泡、拖拽不触发摸头反馈、首次启动右侧入场、旧配置补显示一次当前欢迎语、退出/再次入场动画、睡眠静默、`呆呆.exe` 中文交付名、完整猫猫白底图标和旧“奶糖猫/宝贝”到“呆呆/麻麻”的配置迁移均已完成。最新可交付包是 dist/DesktopCatGift_20260613_final.zip，大小 83,344,029 bytes，SHA256 为 B383ED1FD450EA4AA52ED434CD3FE08DA11F5EB4802A861AD0F3968E8C11DFAD，已通过 193 个测试、53 条语料巡演 smoke、生产批次 QA、构建、zip 解压、旧配置迁移、首次启动右侧入场、旧配置欢迎版本升级、入场状态消费和构建版/解压版 exe smoke。

不要恢复 stash@{0}: cat messaging mvp WIP，不要处理、删除或误提交 raw/wake_* 实验素材，不要提交或推送，除非我明确要求。下一步只做目标机器手动验收，重点检查图标大小、中文文案、旧配置迁移、动作请求丢弃和干净退出；如果验收通过，就停止修改并准备交付。
```
