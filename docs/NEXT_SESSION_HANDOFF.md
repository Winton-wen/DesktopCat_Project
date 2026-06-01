# DesktopCat 新窗口交接说明

更新日期：2026-06-01

## 一句话目标

这是一个 Windows 桌面宠物小猫项目，仓库路径是：

```text
E:\Project\DesktopPig_Project
```

最终目标是做出接近 QQ 宠物级别的“活物感”：角色稳定、动作自然、可拖拽、可交互、可打包运行。当前优先级是动画资产和视觉 QA，不是养成系统、商城、联网、账号或复杂设置。

## 当前 Git / GitHub 状态

- 本地已初始化 Git 仓库。
- 当前分支：`main`
- GitHub 远端：`https://github.com/Winton-wen/DesktopCat_Project.git`
- 当前提交：`e544c6c Initial DesktopCat project`
- 本地 `main` 已推送并跟踪 `origin/main`。
- `.gitignore` 已排除 `.petvenv/`、`build/`、`dist/`、`backups/`、QA 生成物、smoke 临时配置、缓存和 `*_before_synth/`。
- GitHub CLI 已安装并登录为 `Winton-wen`；如果当前终端找不到 `gh`，重开终端即可。

常用习惯：每完成一个小阶段就提交，阶段可运行时再推送。用户不想死记命令，可以直接让 Codex “提交并推送当前版本”。

## 必须先读的文档

新窗口开始时请读取：

```text
docs/NEXT_SESSION_HANDOFF.md
docs/character-spec.md
docs/animation-contract-v2.md
docs/asset-production-pipeline.md
assets/production/desktop_cat/batch_manifest.json
```

## 角色锁定

主角是一只 3D Q 版奶油橘白小猫：

- 大头短圆身体，软萌玩偶比例。
- 大而亮的深棕色眼睛。
- 小粉鼻、淡腮红。
- 橘白虎斑，白色嘴套、胸腹、爪子。
- 蓬松环纹尾巴。
- 粉棕格纹大蝴蝶结。
- 蝴蝶结中心有金色铃铛。

蝴蝶结、铃铛、眼睛颜色、橘白纹路、尾巴形状是身份锚点，不能在动作之间漂移、消失或换样式。

## 当前运行入口

稳定版和候选版都保留，不要删除。

候选预览入口：

```powershell
python candidate_launcher.py 20260527_motion_quality_v1
```

已打包候选 exe：

```text
dist\DesktopCatCandidatePreview\DesktopCatCandidatePreview.exe
```

稳定/历史版本入口：

```text
dist\DesktopCat\DesktopCat.exe
dist\DesktopCatStablePreview\DesktopCatStablePreview.exe
```

## 当前技术路线

当前实际路线是 **polished sprite pet first**，也就是先用完整透明 PNG 帧把动作质量做上去。曾经尝试过伪 Live2D/rig，但早期切层造成过耳朵缺角、爪子缺口、挥手凭空多一只手等问题，所以不要一上来替换运行时。

长期路线可以是：

1. 先把完整 sprite 动作做到自然、可播放、可 QA。
2. 等关键动作稳定后，再考虑伪 Live2D / Spine / Live2D 风格的分层 rig。

## 当前资产结构

核心目录：

```text
assets/sprites/
assets/production/desktop_cat/
assets/production/desktop_cat/batches/stable_v2_baseline/
assets/production/desktop_cat/batches/20260526_batch1_idle_blink_wave/
assets/production/desktop_cat/batches/20260527_motion_quality_v1/
assets/rig_parts/desktop_cat/
src/desktop_cat/
tools/
tests/
```

生产批次说明：

- `stable_v2_baseline`：受保护的稳定基线，不要覆盖。
- `20260526_batch1_idle_blink_wave`：可运行候选批次，但动作质量不是最终。
- `20260527_motion_quality_v1`：当前主力候选批次，目标是替换 happy、cute、sleep_in、wake、walk 等动作。

## 当前已知动作问题

用户最近明确指出的问题：

1. `happy` 和 `cute` 播放时小猫尺寸明显比其他动作小很多。
2. 用户认为 `happy/cute` 这个尺寸更合适，因此下一步应把所有动作统一到这个视觉尺寸，而不是把 happy/cute 放大。
3. `happy`、`cute` 帧率观感很低。原因不是 FPS 数字太低，而是真实不同姿态数量太少，很多帧只是重复保持。
4. `walk` 帧率观感低，而且有点鬼畜，需要真实步态和更平稳位移。
5. `sleep_in` / `wake` 仍然不合格：旧版像小猫变扁/突然坐起，不像自然入睡或醒来。

当前量化状态，来自 `20260527_motion_quality_v1/clean`：

```text
idle      16 frames, visible height about 430
blink     10 frames, visible height about 430
wave      17 frames, visible height about 430
clicked    9 frames, visible height about 430
happy     48 frames, visible height about 184-323
cute      44 frames, visible height about 284-305
sleep_in  11 frames, visible height about 341-430
sleep     11 frames, visible height about 339-344
wake      11 frames, visible height about 341-430
walk      14 frames, visible height about 430
walk_left 14 frames, visible height about 430
drag       8 frames, visible height about 430
```

结论：必须做视觉尺寸统一，目标高度大约 300px 左右，接近 `cute`。

## 最近已经做但未完成的工作

已经生成了高密度 v2 姿态表，保存在：

```text
assets/production/desktop_cat/batches/20260527_motion_quality_v1/pose_sheets/happy_24poses_v2_chromakey.png
assets/production/desktop_cat/batches/20260527_motion_quality_v1/pose_sheets/cute_24poses_v2_chromakey.png
assets/production/desktop_cat/batches/20260527_motion_quality_v1/pose_sheets/sleep_in_24poses_v2_chromakey.png
assets/production/desktop_cat/batches/20260527_motion_quality_v1/pose_sheets/wake_24poses_v2_chromakey.png
assets/production/desktop_cat/batches/20260527_motion_quality_v1/pose_sheets/walk_right_16poses_v2_chromakey.png
```

其中 `sleep_in_24poses_v2_chromakey.png` 已视觉检查过：它是逐步犯困、低头、趴下、蜷睡，不是变扁。

已更新导入工具：

```text
tools/import_keypose_sheet.py
```

它现在支持：

- `--action`
- `--frames`
- `--mirror-action`
- `--target-extent`
- 绿幕转 alpha
- 只保留最大 alpha 连通主体，避免邻格碎片

但注意：**v2 姿态表还没有完整导入到 clean 动作目录，没有跑完整 QA，也没有重新打包。** 新窗口下一步应从这里继续。

## 推荐下一步

第一阶段：完成尺寸统一和 v2 动作导入。

建议顺序：

1. 用 `tools/import_keypose_sheet.py` 把 v2 姿态表导入到临时 raw 目录，目标 `--target-extent 300`。
2. 把 `happy` 从 24 姿态表扩展/导入到 manifest 所需 48 帧，或更新 manifest 到真实 24 帧并同步 runtime/test。优先推荐保留 48 帧，但用 24 姿态均匀重复，每个姿态 2 帧。
3. 把 `cute` 从 24 姿态表扩展到 44 帧，或调整 manifest；优先避免大量无意义重复。
4. 把 `sleep_in` / `wake` 由 11 帧提升为 24 帧时，要同步更新：
   - `assets/production/desktop_cat/batch_manifest.json`
   - `src/desktop_cat/sprite_manifest.py`
   - `src/desktop_cat/rig_app.py` 里的 `ACTION_FPS` 和 `action_frame_count`
   - tests
5. 把 `walk_right_16poses_v2_chromakey.png` 导入为 `walk`，并镜像为 `walk_left`。
6. 把其他动作 `idle/blink/wave/clicked/drag/sleep` 统一缩放到和 `cute` 接近的尺寸，建议目标可见最大边约 300px。
7. 生成 contact sheet 和 gif：
   ```powershell
   python tools\run_production_batch_qa.py --batch 20260527_motion_quality_v1 --actions idle,blink,wave,clicked,happy,sleep_in,sleep,wake,walk,walk_left,cute,drag
   ```
8. 自己查看 QA 图和 GIF，重点看：
   - 是否仍有尺寸跳变。
   - 是否有绿边/碎片/缺耳缺爪。
   - `happy/cute` 是否还是低帧率感。
   - `sleep_in/wake` 是否自然。
   - `walk/walk_left` 是否抖动或方向错。
9. 通过后再打包 candidate，并 smoke test。

## 重要原则

- 不要删除稳定 exe 或稳定资产。
- 不要把 `assets/sprites` 稳定基线当实验场乱改；优先在 `assets/production/desktop_cat/batches/20260527_motion_quality_v1` 里做候选。
- 不要把位移、缩放、旋转 idle 图当作正式动作资产。
- 动作合格标准以视觉 QA 为准，不只是测试通过。
- 每完成一个阶段，建议提交并推送到 GitHub。

## 新窗口推荐提示词

请在新窗口直接粘贴下面这段：

```text
请先读取并遵循 E:\Project\DesktopPig_Project\docs\NEXT_SESSION_HANDOFF.md。

我们继续 DesktopCat / DesktopPig 项目，仓库路径是 E:\Project\DesktopPig_Project。目标是做出接近 QQ 宠物级别的桌面小猫，当前路线是 polished sprite pet first，先把完整透明 PNG 动作资产做到自然和稳定，再考虑伪 Live2D/Spine。请不要删除或破坏已有稳定可运行版本，也不要把 stable 基线当实验场。

当前最新问题是：
1. happy/cute 的小猫尺寸更合适，但其他动作明显大很多，所以要把所有动作统一到 happy/cute 接近的视觉尺寸。
2. happy/cute 的帧率观感仍低，需要用已生成的 24 姿态 v2 表继续导入/补帧，而不是 idle 变形。
3. walk 低帧率且鬼畜，需要使用 walk_right_16poses_v2_chromakey.png 重做 walk，并镜像 walk_left。
4. sleep_in/wake 旧版仍像变扁和突然坐起，需要使用 sleep_in_24poses_v2_chromakey.png 和 wake_24poses_v2_chromakey.png 重做。

请先做上下文恢复：
- 读取 docs/NEXT_SESSION_HANDOFF.md
- 读取 docs/character-spec.md
- 读取 docs/animation-contract-v2.md
- 查看 assets/production/desktop_cat/batch_manifest.json
- 查看 tools/import_keypose_sheet.py
- 检查当前 git status

然后继续下一步：在 20260527_motion_quality_v1 批次中完成尺寸统一、导入 v2 动作、生成 QA contact sheet/GIF，边看边改，直到 candidate preview 可打开检查。完成一个阶段后帮我提交并推送到 GitHub。
```
