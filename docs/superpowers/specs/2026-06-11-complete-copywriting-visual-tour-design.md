# DesktopCat 全部语料视觉巡演设计

## 目标

增加一个专用于人工验收的视觉巡演工具，让开发者无需修改系统时间，也能亲眼检查 DesktopCat 所有收件人可见语料的：

- 中文显示是否正确；
- 气泡尺寸、换行和位置是否合适；
- 文案与动作搭配是否自然；
- 固定提醒按钮是否正确布局；
- 特殊日期和周年占位符是否正确渲染。

巡演使用正式候选批次、真实气泡绘制和真实动作播放链路，不创建另一套模拟界面。

## 范围

巡演必须包含：

1. 首次启动欢迎语。
2. `rig_app.TEXT` 中每一条基础互动文案，而不是每组随机抽取一条。
3. 开启低打扰、关闭低打扰和返回屏幕角落的状态文案。
4. 午饭、晚饭、睡前和深夜四条固定提醒，以及真实的停止提醒按钮。
5. `partner_default.json` 中每一条普通自动陪伴语料。
6. `partner_default.json` 中每一条公历特殊日语料。
7. `partner_default.json` 中每一条农历特殊日语料。

周年纪念文案使用 `2026-03-24` 作为测试日期，预期显示“二周年”。其他特殊日条目使用与其配置匹配的 2026 年测试日期；农历条目使用运行时内置的 2026 年换算表。

## 人工控制

巡演采用手动逐条确认模式：

- `空格` 或 `右方向键`：下一条；
- `左方向键`：上一条；
- `R`：重新播放当前文案对应的动作；
- `Esc`：退出巡演。

每条内容会一直显示，直到用户主动翻页。翻页时直接替换当前气泡，不进入正式运行时的气泡排队逻辑。

巡演气泡顶部增加仅测试时可见的标识：

```text
[17/43] comfort_02 · comfort · cute
麻麻今天辛苦啦……
```

标识用于核对条目 ID、分类和动作，不进入正式礼物版运行时。

## 架构

新增 `tools/run_copywriting_visual_tour.py`，其中包含三个清晰职责：

1. `TourItem` 描述一个可展示条目，包括 ID、分组、模板、动作、测试日期、气泡时长及可选按钮。
2. `build_tour_items()` 从真实运行时常量和语料 JSON 动态收集完整条目列表。
3. `CopywritingVisualTour` 负责当前索引、前后翻页、重播动作、气泡替换和退出。

脚本创建 `CandidateDesktopCatApp`，使用批次 `20260527_motion_quality_v1`，关闭自动提醒和自动陪伴调度。运行期间使用临时 `DESKTOPCAT_CONFIG_DIR`，避免修改用户日常配置、首次启动状态、低打扰状态和上次位置。

为了让人工验收和自动测试分离，脚本支持只收集不打开 GUI 的 `--list` 模式，用于输出条目总数及每条元数据。

## 动作和气泡

普通陪伴语料复用 `show_companion_message` 的动作映射：

- `sleep` 转换为 `sleep_in`；
- 不支持的动作回退到 `wave`；
- 其他动作按语料配置播放。

基础互动和状态语料使用其正式动作。固定提醒不强制播放额外动作，但使用真实提醒按钮文字和布局。

巡演显示时需要取消旧气泡的自动隐藏计时，并以不自动消失的方式显示当前条目。重新播放只重启动作，不改变索引。

## 删除和兼容

删除不完整的旧巡演：

- `tools/run_candidate_feature_qa.py`
- `tests/test_candidate_feature_qa_script.py`

新增对应测试：

- `tests/test_copywriting_visual_tour.py`

后台测试继续通过 `python -m pytest -q` 和 `tools/run_production_batch_qa.py` 独立运行。更新 `docs/NEXT_SESSION_HANDOFF.md` 的当前文件列表、推荐命令和说明，不修改历史计划文档。

## 测试策略

自动测试必须验证：

- `TEXT` 中每一条文案都被收集；
- 四条固定提醒都被收集；
- `partner_default.json` 中每一条语料都被收集且 ID 唯一；
- 每条特殊日语料都有匹配的测试日期；
- 周年条目在 2026 年渲染为“二周年”；
- 下一条、上一条和边界行为正确；
- 重播动作不改变当前索引；
- 脚本使用临时配置目录；
- `--list` 模式无需打开 Tk GUI。

完成后运行：

```powershell
python -m pytest tests/test_copywriting_visual_tour.py -q
python -m pytest -q
python tools/run_copywriting_visual_tour.py --list
python tools/run_copywriting_visual_tour.py --smoke
```

`--smoke` 仅用于确认 GUI 能打开、展示首条并自动退出，不替代完整人工逐条验收。

## 非目标

- 不修改正式礼物 EXE 的命令行参数。
- 不把巡演控制加入收件人右键菜单。
- 不修改语料内容、动画素材或正式气泡样式。
- 不恢复网络消息 stash。
- 不处理 `raw/wake_*` 实验素材。
- 不提交或推送任何改动。
