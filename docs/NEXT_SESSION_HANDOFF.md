# DesktopCat / DesktopPig Next Session Handoff

Updated: 2026-06-05 16:10 +08:00

## Project

- Repo path: `E:\Project\DesktopPig_Project`
- Remote: `https://github.com/Winton-wen/DesktopCat_Project.git`
- Branch: `main`
- Current functional pushed HEAD: `15c1ae4 Polish DesktopCat gift package`
- `main` is aligned with `origin/main` at `15c1ae4` before this handoff-only update.

## Current Goal

Continue building a QQ-pet-level desktop cat for a long-distance relationship:
**polished sprite pet first -> low-burden companion behaviors -> gift-quality packaging**.

The pet should feel gentle, personal, non-disruptive, and gift-like. Avoid heavy
raising systems, shops, currencies, high-frequency notifications, AI chat as the
main experience, and anything that makes the partner maintain another app.

## Must Read First

At the start of the next window, read:

```text
docs/NEXT_SESSION_HANDOFF.md
docs/character-spec.md
docs/animation-contract-v2.md
docs/companion-experience-roadmap.md
assets/production/desktop_cat/batch_manifest.json
candidate_launcher.py
gift_launcher.py
build_gift.ps1
tools/run_candidate_feature_qa.py
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
- Do not delete or break stable runnable versions.
- Keep the current route: full transparent PNG sprite assets remain stable and QA-able.
- Visual QA matters more than tests alone for animation/UI behavior.
- Preserve untracked `raw/wake_*` experiment assets unless the user explicitly asks to clean them.
- Do not accidentally stage `raw/wake_*`.
- `docs/NEXT_SESSION_HANDOFF.md` may be updated and committed only when the user requests handoff.
- The Supabase live-message prototype is deferred. Do not restore `stash@{0}` unless explicitly asked.
- Prefer offline-first companion value before networked features.
- Low-distraction mode exists, but the user explicitly rejected making it the default.

## Current Git State

Last checked before this handoff update:

```text
## main...origin/main
 M docs/NEXT_SESSION_HANDOFF.md
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_12poses_v4_generated_chromakey.png
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_12poses_v4_generated_keyposes/
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_16poses_v7_clean_eyes_chromakey.png
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_16poses_v7_clean_eyes_keyposes/
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_20poses_v5_generated_chromakey.png
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_20poses_v5_generated_keyposes/
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_38poses_v6_generated_chromakey.png
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_38poses_v6_generated_keyposes/
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_eye_open_settle_v1_chromakey.png
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_eye_open_settle_v1_keyposes/
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_front_middle_v9_chromakey.png
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_front_middle_v9_keyposes/
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_front_middle_v9_keyposes_scaled/
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_full_v8_generated_chromakey.png
?? assets/production/desktop_cat/batches/20260527_motion_quality_v1/raw/wake_full_v8_generated_keyposes/
```

Recent commits:

```text
15c1ae4 (HEAD -> main, origin/main) Polish DesktopCat gift package
384f862 Add gift-ready DesktopCat packaging
fd1fd88 Queue pet actions and speech bubbles
5d2ed19 Add return home animation action
d31191d Add candidate feature QA tour
ea7a2b1 Add gift-ready companion config flow
3f22b4d Move reminder dismiss button below pet
a007fac Repeat reminders until dismissed
```

Deferred stash:

```text
stash@{0}: On main: cat messaging mvp WIP
```

Do not apply this stash unless the user explicitly asks to resume Supabase partner messaging.

## Accepted Current State

### Active Candidate Batch

- Active candidate batch: `20260527_motion_quality_v1`
- Runtime preview: `candidate_launcher.py`
- Gift runtime entrypoint: `gift_launcher.py`
- Source frames: `assets/production/desktop_cat/batches/20260527_motion_quality_v1/clean`
- Wake remains `80` frames at `32fps`.
- The rejected `96` frame wake expansion remains rejected; do not resume that direction.

### Runtime Behavior

- Non-idle actions now queue instead of interrupting current non-idle actions.
- Speech bubbles now queue instead of immediately replacing visible bubbles.
- Queued bubbles use the current pet anchor when displayed, fixing post-drag bubble jumps.
- Drag remains immediate and responsive.
- Sleep-loop click can still wake immediately.
- `return_home` uses the committed lively jump-back behavior; the attempted walk-only replacement was reverted.
- Reset-to-corner still prefers `return_home` when returning to the right-side default corner.
- Last valid on-screen position is restored on restart; off-screen saved positions fall back to the default corner.

### Gift Package

Current polished gift artifact:

```text
dist/DesktopCatGift_20260605_polished.zip
```

Size:

```text
82,798,481 bytes
```

Unzipped executable:

```text
dist/DesktopCatGift/DesktopCatGift.exe
```

Partner-facing README:

```text
dist/DesktopCatGift/README_先看我.txt
assets/gift/README_先看我.txt
```

Gift polish now includes:

- Partner-facing README instructions.
- Kitten app icon: `assets/gift/desktopcat.ico`.
- Slimmed packaging: `build_gift.ps1` packages only the active batch clean frames, companion messages, and gift assets.
- Warmer first-launch message with delayed companion-message start.
- Right-click couple interactions:
  - `我想他了`
  - `今天辛苦啦`
- Chinese runtime strings verified as readable in Python; terminal mojibake is a display issue unless UI text is visibly wrong.

### Offline Companion Flow

- Offline message pack: `assets/companion_messages/partner_default.json`
- User-editable copy is created at config-time as `companion_messages/partner_custom.json`.
- Bad configured custom packs fall back to default:
  - malformed JSON
  - empty `messages`
  - all-invalid message entries

### Low-Distraction And Time Rhythm

- `low_distraction_mode` exists in config and can be toggled from the context menu.
- Do not make low-distraction mode default unless the user reverses the decision.
- Candidate preview examples:

```powershell
python candidate_launcher.py 20260527_motion_quality_v1 --low-distraction
python candidate_launcher.py 20260527_motion_quality_v1 --test-rhythm-time 02:30
python candidate_launcher.py 20260527_motion_quality_v1 --test-rhythm-time 20:30 --low-distraction
```

## Validation Already Run

Full relevant tests:

```powershell
python -m pytest tests\test_stable_sprite_route.py tests\test_production_pipeline.py tests\test_rig_preview.py tests\test_companion_messages.py tests\test_low_distraction_mode.py tests\test_time_rhythm.py tests\test_speech_bubble_polish.py tests\test_gift_config_experience.py tests\test_candidate_feature_qa_script.py
```

Result:

```text
115 passed
```

Gift build:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_gift.ps1
```

Result:

```text
production_batch_full_qa_ok batch=20260527_motion_quality_v1 actions=idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,return_home,drag
Gift build complete: dist\DesktopCatGift\DesktopCatGift.exe
Batch: 20260527_motion_quality_v1
```

Zip package smoke:

```powershell
tar -xf dist\DesktopCatGift_20260605_polished.zip -C desktopcat_zip_extract_smoke_polished_20260605
.\desktopcat_zip_extract_smoke_polished_20260605\DesktopCatGift\DesktopCatGift.exe --smoke-ms 3000
```

Result:

```text
No lingering DesktopCatGift process.
desktopcat_smoke_config_gift_polished_zip_exe/config.json was generated.
```

Candidate visible smoke:

```powershell
python tools\run_candidate_feature_qa.py --smoke
```

Result:

```text
candidate_feature_qa_report=E:\Project\DesktopPig_Project\qa_reports\candidate_feature_qa_20260605_160220.txt
71 passed in smoke pytest subset
production_batch_full_qa_ok batch=20260527_motion_quality_v1 actions=idle,blink,wake,return_home
```

## Known Issues / Watch Points

- `raw/wake_*` files are experiment material. Do not stage them by accident.
- `docs/NEXT_SESSION_HANDOFF.md` is expected to be changed only by handoff requests.
- Some PowerShell output displays Chinese as mojibake. Check actual UI/runtime strings before treating it as a bug.
- QA tools write to shared `assets/production/desktop_cat/qa/<batch>` directories. Avoid running multiple production QA scopes in parallel.
- `return_home` is accepted as lively jump-back behavior for now, but it is still synthesized, not a final hand-authored pose-sheet action.
- `dist/` and zip files are ignored. The deliverable exists locally but is not committed.
- PyInstaller may need elevated permission in this environment because it can hit permission errors reading user site-packages.

## Next Recommended Steps

The project is now ready to deliver the polished gift package:

```text
dist/DesktopCatGift_20260605_polished.zip
```

Recommended next work, only after the user wants more polish:

1. Manually test the polished zip on the target machine if possible.
2. Confirm first-launch UI text, right-click menu Chinese text, drag behavior, reset-to-corner, and quit behavior visually.
3. If the gift is accepted, stop adding features for now.
4. If continuing development, add only low-burden personal touches such as special-day messages or a meet-again countdown.
5. Resume Supabase/network messaging only when both computers can be configured directly.

## Useful Commands

Manual candidate preview:

```powershell
python candidate_launcher.py 20260527_motion_quality_v1
```

Gift build:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_gift.ps1
```

Gift smoke from built executable:

```powershell
$env:DESKTOPCAT_CONFIG_DIR = Join-Path (Get-Location) 'desktopcat_smoke_config_gift_exe'
.\dist\DesktopCatGift\DesktopCatGift.exe --smoke-ms 3000
Remove-Item Env:DESKTOPCAT_CONFIG_DIR
```

Candidate feature QA:

```powershell
python tools\run_candidate_feature_qa.py --smoke
python tools\run_candidate_feature_qa.py --backend-only --fast
```

Full relevant tests:

```powershell
python -m pytest tests\test_stable_sprite_route.py tests\test_production_pipeline.py tests\test_rig_preview.py tests\test_companion_messages.py tests\test_low_distraction_mode.py tests\test_time_rhythm.py tests\test_speech_bubble_polish.py tests\test_gift_config_experience.py tests\test_candidate_feature_qa_script.py
```

Full candidate production QA:

```powershell
python tools\run_production_batch_qa.py --batch 20260527_motion_quality_v1 --actions idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,return_home,drag
```

## New Window Prompt

```text
请先读取并遵循 E:\Project\DesktopPig_Project\docs\NEXT_SESSION_HANDOFF.md。

我们继续 DesktopCat / DesktopPig 项目，仓库路径是 E:\Project\DesktopPig_Project。当前路线是 polished sprite pet first -> low-burden companion behaviors -> gift-quality packaging，目标是给异地对象一个温柔、不打扰、像礼物一样的小猫桌宠。

请先恢复上下文：读取 docs/NEXT_SESSION_HANDOFF.md、docs/character-spec.md、docs/animation-contract-v2.md、docs/companion-experience-roadmap.md、assets/production/desktop_cat/batch_manifest.json、candidate_launcher.py、gift_launcher.py、build_gift.ps1、tools/run_candidate_feature_qa.py、src/desktop_cat/rig_app.py、src/desktop_cat/config.py、src/desktop_cat/companion_messages.py、src/desktop_cat/time_reminders.py；然后检查 git status --short --branch、git log -8 --oneline --decorate、git stash list -n 5。

当前功能版已推送到 main/origin/main：15c1ae4 Polish DesktopCat gift package。最新可交付礼物包是 dist/DesktopCatGift_20260605_polished.zip，已通过 115 个相关测试、build_gift.ps1 构建、zip 解压 smoke、candidate visible smoke。Supabase 传话原型仍在 stash@{0}: cat messaging mvp WIP，不要恢复，除非我明确要求。raw/wake_* 实验素材不要误提交。

下一步优先级：如果只是交付礼物，先不要继续加功能；如需继续优化，先做目标机器手动验收，确认首次启动、右键菜单、拖拽、回角落、退出、中文 UI 文案都正常。
```
