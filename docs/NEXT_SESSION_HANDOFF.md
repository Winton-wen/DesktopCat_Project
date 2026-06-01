# DesktopCat 新对话交接说明

更新日期：2026-05-26

## 项目目标

这是一个 Windows 桌面宠物项目，当前工程名仍在 `E:\Project\DesktopPig_Project`，产品目标是做成类似 QQ 宠物那种商业级“活物感”的桌面小猫。角色是一只 3D Q 版奶油橘白小猫，必须始终戴粉棕格纹大蝴蝶结和金色铃铛，拥有大圆深棕眼睛、粉色鼻子、淡粉腮红、短圆身体和蓬松环纹尾巴。

用户最在意的是动画质感和角色一致性，不是复杂养成系统。当前阶段只保留核心交互：点击、拖拽、冒泡、走路、睡觉/唤醒、托盘菜单。养成、联网、账号、商店、同步等都暂不做。

## 当前可运行版本

当前可运行 exe：

`E:\Project\DesktopPig_Project\dist\DesktopCat\DesktopCat.exe`

当前版本快照压缩包：

`E:\Project\DesktopPig_Project\backups\DesktopCat_v2_sprite_snapshot_20260526_111748.zip`

该压缩包包含源码、素材、文档、参考图、工具脚本和当前 `dist`，排除了 `.petvenv`、`build` 和 smoke 临时配置目录。

## 当前技术栈

- 运行时：Python + Tkinter + Pillow + pystray。
- 打包：PyInstaller，通过 `build.ps1` 输出 `dist\DesktopCat\DesktopCat.exe`。
- 素材处理：`tools/process_generated_strips.py`、`tools/stabilize_sprites.py`、`tools/make_motion_contact.py`、`tools/make_motion_gifs.py`。
- 当前不是 PySide6，也不是真正 Live2D/Spine。当前是 polished sprite pet，也就是透明 PNG 帧动画桌宠。

## 当前功能状态

当前版本已经具备：

- 透明置顶桌宠窗口。
- 托盘菜单：开心、挥手、睡觉、显示/隐藏、自启、重置位置、配置、退出。
- 可拖拽移动。
- 点击交互。
- 自适应黑框白底气泡，气泡尖角指向小猫中心。
- 拖拽时气泡跟随移动。
- 重置位置时气泡立即跟随新位置。
- 左右双向走路：`walk` 向右，`walk_left` 向左。
- 走路进入时随机方向，但靠近左边界只能向右，靠近右边界只能向左，避免边界处左右朝向抽搐。
- 睡觉状态机：
  - `sleep_in` 入睡过渡。
  - `sleep` 持续睡觉。
  - 睡觉期间随机冒泡静默。
  - 睡觉时点击会播放 `wake` 醒来，再回待机。

## 当前动作与素材

当前动作目录在：

`E:\Project\DesktopPig_Project\assets\sprites`

当前动作包括：

- `idle`：16 帧，基于 `blink/00` 开眼帧生成的轻微上下呼吸。尺寸和亮度与眨眼开眼帧一致。
- `blink`：10 帧眨眼。
- `clicked`：9 帧点击惊讶。
- `happy`：27 帧，举爪开心动作，通过关键帧重复延长举爪和放爪过程，避免一帧完成。
- `wave`：17 帧挥爪。
- `sleep_in`：11 帧入睡过渡。
- `sleep`：11 帧睡觉循环。
- `wake`：11 帧醒来过渡。
- `walk`：14 帧右走。
- `walk_left`：14 帧，由 `walk` 镜像生成。
- `drag`：8 帧稳定拖拽姿态。

QA 图：

- `E:\Project\DesktopPig_Project\assets\qa\motion_contact_sheet.png`
- `E:\Project\DesktopPig_Project\assets\qa\sprite_contact_sheet.png`
- `E:\Project\DesktopPig_Project\assets\qa\gifs\`

## 最近验证过的行为

最近一轮验证结果：

- `gui_sleep_random_silent_ok`：睡觉时随机冒泡静默，点击唤醒仍显示醒来气泡。
- `python_ast_ok`：Python 语法检查通过。
- `gui_state_machine_smoke_ok`：重置气泡、走路边界方向、睡眠唤醒状态机通过。
- `packaged_smoke_ok`：打包后的 exe 能启动并被关闭。

## 当前已知问题和限制

当前 sprite 路线仍有这些硬限制：

- 动作之间依然是整张图切换，无法达到真正 QQ 宠物那种连续骨骼生命感。
- `sleep_in`/`wake` 是工程过渡帧，不是真正手绘/骨骼过渡，能缓解但不能根治动作跳变。
- `happy` 目前通过重复关键帧延长动作，不是真正插值骨骼动画。
- Tkinter 透明窗口使用 transparent color，不是完美 per-pixel alpha，边缘抗锯齿和透明细节会受限制。
- 现有素材来自 AI 生成长条图，角色一致性已经做过很多修正，但继续做商业级效果会越来越吃力。

## 为什么要升级到伪 Live2D/Spine

用户最终目标是 QQ 宠物级“活物感”。当前整图 sprite 帧动画的问题是：

- 同一动作内部可以靠更多帧改善，但动作之间仍然会跳。
- 角色的头、身体、眼睛、爪子、尾巴、蝴蝶结、铃铛无法独立运动。
- 表情、眨眼、尾巴摆动、身体呼吸、铃铛摇摆无法自然叠加。

下一阶段应升级为“伪 Live2D/Spine 风格”：把角色拆成独立层，通过代码做层级骨骼、锚点、旋转、缩放、位移和缓动。目标不是立刻接入官方 Live2D/Spine runtime，而是在当前 Python 桌宠里先实现一套轻量 2D rig。

## 下一阶段建议路线

推荐分 5 步推进：

1. 资产分层
   - 从当前最稳定的正面小猫图生成或手工拆分层。
   - 至少拆出：身体、头、左耳、右耳、左眼、右眼、眼皮/眨眼层、嘴、腮红、左前爪、右前爪、后爪、尾巴分段、蝴蝶结左右片、蝴蝶结结心、铃铛。
   - 每层必须透明 PNG，保存到 `assets/rig_parts/desktop_cat/`。

2. 定义 rig 配置
   - 新建 `assets/rig_parts/desktop_cat/rig.json`。
   - 描述每层的 parent、pivot、default position、z-index、scale、rotation limit。
   - 所有动作通过 rig 配置驱动，而不是直接切整张图。

3. 实现伪骨骼渲染器
   - 新建 `src/desktop_cat/rig/`。
   - 用 Pillow 或 Tk Canvas 组合各个部件。
   - 每一帧根据时间计算各层 transform，再合成为一张透明图显示。
   - 初期可以继续用 Tkinter，后续如需要更好透明度再迁移 PySide6。

4. 动作系统重写
   - `idle`：身体轻微呼吸、尾巴慢摆、耳朵微动、铃铛轻微跟随。
   - `blink`：只动眼皮层，不换整只猫。
   - `happy`：身体弹跳、前爪上抬、眼睛高光/嘴部变化、尾巴加速摆动、铃铛摆动。
   - `walk`：身体水平移动、脚步层交替、尾巴反向摆动。
   - `sleep_in/sleep/wake`：头和身体缓慢压低/抬起，眼皮闭合/张开。
   - 动作之间用 easing 过渡，不直接切换图片。

5. QA 和打包
   - 保留现有 QA 流程，但增加 rig 动作录制 GIF。
   - 每个动作必须生成预览 GIF 和 contact sheet。
   - 每次打包后启动 exe 冒烟测试。

## 建议的新目录结构

建议新增：

```text
assets/
  rig_parts/
    desktop_cat/
      body.png
      head.png
      eye_left.png
      eye_right.png
      eyelid_left.png
      eyelid_right.png
      paw_front_left.png
      paw_front_right.png
      tail_01.png
      tail_02.png
      tail_03.png
      bow_left.png
      bow_right.png
      bow_center.png
      bell.png
      rig.json
src/
  desktop_cat/
    rig/
      __init__.py
      model.py
      renderer.py
      animation.py
      motions.py
tools/
  make_rig_preview.py
  export_rig_contact_sheet.py
```

## 给新对话的建议第一步

新对话开始后，建议直接说：

“请读取 `docs/NEXT_SESSION_HANDOFF.md`，我们从当前 DesktopCat v2 sprite 快照继续，开始升级到伪 Live2D/Spine 风格。第一步先做资产分层和 rig.json，不要先重写运行时。”

然后让新会话先完成：

1. 读取 `docs/NEXT_SESSION_HANDOFF.md`、`docs/character-spec.md`、`docs/animation-contract-v2.md`。
2. 检查 `assets/sprites/idle/00.png`、`assets/sprites/blink/00.png`、`assets/generated_strips_v2`。
3. 选择一张最稳定的正面图作为 rig 分层母图。
4. 生成或拆分第一版 `assets/rig_parts/desktop_cat/`。
5. 先做 `idle` 和 `blink` 的 rig 预览，不要一次性改完所有动作。

## 注意事项

- 不要删除当前 sprite 版本；它是可运行基线。
- 不要直接把现有运行时全部推倒重写。先做并行 rig preview，确认视觉效果后再切换运行时。
- 不要再用长条 AI 图硬切来追求商业级效果；下一阶段核心是“分层 + 骨骼 + 缓动”。
- 如果继续用 AI 生成素材，必须要求透明背景、单独部件、同一视角、同一光照、同一配饰，并逐层 QA。
