from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from desktop_cat.config import (
    MAMA_NICKNAME,
    PAPA_NICKNAME,
    PET_NAME,
    README_TEXT,
)
from desktop_cat.companion_messages import render_companion_text
from desktop_cat.rig_app import (
    COMPANION_MESSAGE_HIDE_MS,
    FIRST_LAUNCH_HIDE_MS,
    SHORT_BUBBLE_HIDE_MS,
    TEXT,
    low_distraction_menu_label,
)
from desktop_cat.time_reminders import (
    BEDTIME_REMINDER,
    DINNER_REMINDER,
    LATE_NIGHT_REMINDER,
    LUNCH_REMINDER,
)


ROOT = Path(__file__).resolve().parents[1]


def render(text: str) -> str:
    return render_companion_text(
        text,
        pet_name=PET_NAME,
        mama_nickname=MAMA_NICKNAME,
        papa_nickname=PAPA_NICKNAME,
        current=datetime.now(),
    )


def inline_text(text: str) -> str:
    return text.replace("\n", "\\n")


def write_copywriting_catalog() -> None:
    pack = json.loads(
        (ROOT / "assets" / "companion_messages" / "partner_default.json").read_text(
            encoding="utf-8"
        )
    )
    gift_readme_path = next((ROOT / "assets" / "gift").glob("README_*.txt"))
    gift_readme = gift_readme_path.read_text(encoding="utf-8")

    out: list[str] = []

    def line(text: str = "") -> None:
        out.append(text)

    line("# DesktopCat 全部语料与触发条件修改稿")
    line()
    line(
        "这份文档列出当前礼物版 DesktopCat 会用到的全部语料、菜单文字、README 文案和触发条件。"
        "你可以逐条修改“修改后文案”和“修改后触发条件/时间”，再交给我同步到工程。"
    )
    line()
    line(
        "当前礼物 EXE 的入口是 `gift_launcher.py` -> `RigDesktopCatApp`。"
        "旧版备用语料已经不再列入，也不会再作为后续修改对象。"
    )
    line()
    line("## 0. 怎么填写")
    line()
    line("- **工程模板**：实际存入工程的文字。")
    line("- **默认显示**：使用默认称呼时，她实际看到的文字。")
    line("- **当前触发条件/时间**：现在什么情况下出现。")
    line("- **修改后文案**：直接写你想要的新文字；不改可以留空。")
    line("- **修改后触发条件/时间**：想改触发时间、日期、冷却或动作时填写；不改可以留空。")
    line()
    line("可用占位符：")
    line()
    line("- `{pet_name}`：默认显示为“呆呆”。")
    line("- `{mama_nickname}`：默认显示为“麻麻”。")
    line("- `{papa_nickname}`：默认显示为“粑粑”。")
    line("- `{anniversary_year_cn}`：周年纪念日自动计算出的中文周年数。")
    line()
    line(
        "新增普通自动语料时，建议使用 `category`、`text`、`cooldown_hours`、`action`。"
        "新增特殊日子语料时，公历用 `month_day: \"MM-DD\"`，农历用 `lunar_month_day: \"MM-DD\"`。"
    )
    line("可用动作：`wave` 招手，`cute` 卖萌，`happy` 开心跳跃，`blink` 眨眼，`sleep` 睡眠。")
    line()

    line("## A. 默认称呼")
    line()
    identities = [
        ("pet_name", PET_NAME, "小猫名字，替换所有 `{pet_name}`。"),
        ("mama_nickname", MAMA_NICKNAME, "呆呆对她的称呼，替换所有 `{mama_nickname}`。"),
        ("papa_nickname", PAPA_NICKNAME, "呆呆对你的称呼，替换所有 `{papa_nickname}`。"),
        ("partner_nickname", MAMA_NICKNAME, "旧配置兼容字段，新文案不建议继续使用。"),
    ]
    for index, (field, value, desc) in enumerate(identities, 1):
        line(f"### A-{index:02d} `{field}`")
        line()
        line(f"- 当前默认值：`{value}`")
        line(f"- 用途：{desc}")
        line("- 修改后默认值：")
        line()

    line("## B. 基础互动气泡")
    line()
    trigger_map = {
        "pet": ("左键点击呆呆；如果正在睡觉则优先触发唤醒。", "clicked"),
        "happy": ("右键点“开心一下”；随机待机也可能触发开心动作并随机显示其中一条气泡。", "happy"),
        "cute": ("右键点“卖萌一下”；随机待机可能播放卖萌动作，但只有主动菜单会显示这组气泡。", "cute"),
        "wave": ("右键点“打个招呼”，或双击呆呆。", "wave"),
        "sleep": ("右键点“睡一会儿”。", "sleep_in -> sleep"),
        "wake": ("呆呆处于睡眠动作时左键点击。", "wake"),
        "walk_left": ("右键点“向左走两步”。", "walk_left"),
        "walk_right": ("右键点“向右走两步”。", "walk"),
    }
    for index, key in enumerate(TEXT, 1):
        values = TEXT[key]
        trigger, action = trigger_map[key]
        line(f"### B-{index:02d} `{key}`")
        line()
        line(f"- 工程 key：`{key}`")
        line("- 工程模板：")
        for value in values:
            line(f"  - `{inline_text(value)}`")
        line("- 默认显示：")
        for value in values:
            line(f"  - `{inline_text(render(value))}`")
        line(
            f"- 当前触发条件/时间：{trigger} 同一 key 下多条文案会随机选择一条；"
            f"气泡显示约 {SHORT_BUBBLE_HIDE_MS // 1000} 秒。"
        )
        line(f"- 动作：`{action}`")
        line("- 修改后文案：")
        line("- 修改后触发条件/时间：")
        line()

    line("## C. 首次启动与状态气泡")
    line()
    state_items = [
        (
            "first_launch",
            f"{PET_NAME}来啦！我以后就是{MAMA_NICKNAME}的桌面小猫啦",
            f"第一次运行时，启动约 1.2 秒后显示；正常只显示一次；气泡显示约 {FIRST_LAUNCH_HIDE_MS // 1000} 秒。",
            "wave",
        ),
        (
            "low_distraction_on",
            "{pet_name}会乖乖安静地陪着{mama_nickname}\n꜀(^. .^꜀  )꜆੭",
            f"右键点“{low_distraction_menu_label(False)}”；气泡显示约 {SHORT_BUBBLE_HIDE_MS // 1000} 秒。",
            "idle",
        ),
        (
            "low_distraction_off",
            "呆呆要和麻麻玩！",
            f"右键点“{low_distraction_menu_label(True)}”；气泡显示约 {SHORT_BUBBLE_HIDE_MS // 1000} 秒。",
            "idle",
        ),
        (
            "return_corner_done",
            "{pet_name}跳回屏幕角落啦。",
            f"右键点“回到屏幕角落”，返回动画完成后显示；气泡显示约 {SHORT_BUBBLE_HIDE_MS // 1000} 秒。",
            "idle",
        ),
    ]
    for index, (key, text, trigger, action) in enumerate(state_items, 1):
        line(f"### C-{index:02d} `{key}`")
        line()
        line(f"- 工程模板：`{inline_text(text)}`")
        line(f"- 默认显示：`{inline_text(render(text))}`")
        line(f"- 当前触发条件/时间：{trigger}")
        line(f"- 动作：`{action}`")
        line("- 修改后文案：")
        line("- 修改后触发条件/时间：")
        line()

    line("## D. 右键菜单文字")
    line()
    menu_items = [
        ("开心一下", "播放开心动作并显示 B-02。"),
        ("卖萌一下", "播放卖萌动作并显示 B-03。"),
        ("打个招呼", "播放招手动作并显示 B-04。"),
        ("向左走两步", "向左移动并显示 B-07。"),
        ("向右走两步", "向右移动并显示 B-08。"),
        ("睡一会儿", "进入睡眠并显示 B-05。"),
        (low_distraction_menu_label(False), "当前为正常模式时显示，点击后进入更安静的陪伴模式。"),
        (low_distraction_menu_label(True), "当前为低打扰模式时显示，点击后恢复正常陪伴。"),
        ("回到屏幕角落", "让呆呆返回默认角落。"),
        ("退出", "关闭呆呆和气泡窗口。"),
    ]
    for index, (label, usage) in enumerate(menu_items, 1):
        line(f"### D-{index:02d}")
        line()
        line(f"- 当前文字：`{label}`")
        line(f"- 用途：{usage}")
        line("- 修改后菜单文字：")
        line("- 修改后触发条件/时间：")
        line()
    line("说明：右键菜单中已删除单独的安慰入口；原先三条安慰文案已并入 F 组普通自动语料。")
    line()

    line("## E. 固定时间提醒")
    line()
    reminders = [
        ("lunch", LUNCH_REMINDER.message, "每天 11:45-12:15 附近；当天只提醒一次；气泡显示约 15 秒。"),
        ("dinner", DINNER_REMINDER.message, "每天 18:00-19:00 附近；当天只提醒一次；气泡显示约 15 秒。"),
        ("bedtime", BEDTIME_REMINDER.message, "每天 23:00-23:45 附近；当天只提醒一次；气泡显示约 15 秒。"),
        ("late_night", LATE_NIGHT_REMINDER.message, "每天 00:30-02:00 附近；当天只提醒一次；气泡显示约 15 秒。"),
    ]
    for index, (key, text, trigger) in enumerate(reminders, 1):
        line(f"### E-{index:02d} `{key}`")
        line()
        line(f"- 工程模板：`{inline_text(text)}`")
        line(f"- 默认显示：`{inline_text(render(text))}`")
        line(f"- 当前触发条件/时间：{trigger}")
        line("- 按钮文字：`谢谢呆呆的关心，不用再提醒啦`")
        line("- 修改后文案：")
        line("- 修改后触发条件/时间：")
        line()

    line("## F. 自动陪伴语料")
    line()
    line("时间段分类：")
    line()
    for key, desc in [
        ("morning", "07:00-11:30"),
        ("lunch", "11:30-13:30"),
        ("afternoon", "13:30-18:00"),
        ("evening", "18:00-22:30"),
        ("late_night", "01:30-05:00"),
        ("bedtime", "其余时间"),
    ]:
        line(f"- `{key}`: {desc}")
    line()
    line(
        f"特殊日子优先于全部普通语料。非低打扰状态下，程序会把当前时间段语料与"
        f"`miss_you`、`busy_support`、`comfort`、`encouragement` 通用语料合并，"
        f"再从冷却结束的候选中随机选择一条；气泡显示约 {COMPANION_MESSAGE_HIDE_MS // 1000} 秒。"
        "低打扰状态不播放自动陪伴语料。`cooldown_hours` 表示同一条语料再次出现前至少等待多少小时。"
    )
    line()
    for index, item in enumerate(pack["messages"], 1):
        message_id = item["id"]
        category = item["category"]
        text = item["text"]
        cooldown = item.get("cooldown_hours", 24)
        action = item.get("action", "wave")
        month_day = item.get("month_day")
        lunar_month_day = item.get("lunar_month_day")
        line(f"### F-{index:02d} `{message_id}`")
        line()
        line(f"- category：`{category}`")
        if month_day:
            line(f"- month_day：`{month_day}`")
        if lunar_month_day:
            line(f"- lunar_month_day：`{lunar_month_day}`")
        line(f"- 工程模板：`{inline_text(text)}`")
        line(f"- 默认显示：`{inline_text(render(text))}`")
        line(f"- cooldown_hours：`{cooldown}`")
        line(f"- action：`{action}`")
        if category == "special_day":
            if month_day:
                trigger = f"每年公历 {month_day}，当天优先于全部普通语料。"
            else:
                trigger = f"每年农历 {lunar_month_day}，换算到对应公历日期后当天优先于全部普通语料。"
        else:
            if category in {"miss_you", "busy_support", "comfort", "encouragement"}:
                trigger = "任意时间段均可作为通用语料参与随机选择。"
            else:
                trigger = f"当前时间属于 `{category}` 时参与随机选择。"
        line(f"- 当前触发条件/时间：{trigger} 同 ID 距上次显示至少 {cooldown} 小时。")
        line("- 修改后文案：")
        line("- 修改后触发条件/时间：")
        line()

    line("## G. 自动生成的配置 README")
    line()
    line(
        "来源：`src/desktop_cat/config.py` 的 `README_TEXT`。首次创建用户配置目录时写入 `README.txt`，"
        "已经存在的 README 不会被自动覆盖。"
    )
    line()
    line("当前全文：")
    line()
    line("```text")
    line(README_TEXT.rstrip())
    line("```")
    line()
    line("修改后全文：")
    line()
    line("```text")
    line("")
    line("```")
    line()
    line("修改后触发条件/写入方式：")
    line()

    line("## H. 礼物包 README")
    line()
    line(f"来源：`{gift_readme_path.relative_to(ROOT).as_posix()}`。她解压礼物包后可以直接看到。")
    line()
    line("当前全文：")
    line()
    line("```text")
    line(gift_readme.rstrip())
    line("```")
    line()
    line("修改后全文：")
    line()
    line("```text")
    line("")
    line("```")
    line()
    line("修改后触发条件/放置方式：")
    line()

    line("## I. 新增自动语料格式")
    line()
    line("### I-01 普通时间段语料")
    line()
    line("```json")
    line("{")
    line('  "id": "evening_02",')
    line('  "category": "evening",')
    line('  "text": "{pet_name}来陪{mama_nickname}休息一下，{papa_nickname}也希望你别太累。",')
    line('  "cooldown_hours": 24,')
    line('  "action": "cute"')
    line("}")
    line("```")
    line()
    line("### I-02 公历特殊日子语料")
    line()
    line("```json")
    line("{")
    line('  "id": "special_visit_0718",')
    line('  "category": "special_day",')
    line('  "month_day": "07-18",')
    line('  "text": "今天是特别的日子，{pet_name}要陪{mama_nickname}和{papa_nickname}一起记住。",')
    line('  "cooldown_hours": 72,')
    line('  "action": "happy"')
    line("}")
    line("```")
    line()
    line("### I-03 农历特殊日子语料")
    line()
    line("```json")
    line("{")
    line('  "id": "special_mid_autumn",')
    line('  "category": "special_day",')
    line('  "lunar_month_day": "08-15",')
    line('  "text": "中秋快乐呀，{pet_name}想陪{mama_nickname}和{papa_nickname}一起看月亮。",')
    line('  "cooldown_hours": 72,')
    line('  "action": "happy"')
    line("}")
    line("```")
    line()
    line("填写规则：同一天最好只放一条特殊日语料；当前程序会按 `id` 排序并只选第一条可用语料。")
    line("农历特殊日当前内置 2026-2030 年换算表。")
    line()
    line("### I-04 可以直接复制的空白模板")
    line()
    line("```text")
    line("新增语料名称：")
    line("希望出现的日期或时间段：")
    line("文案：")
    line("希望动作：")
    line("同一条多久最多出现一次：")
    line("是否只在特殊日期出现：")
    line("```")
    line()

    (ROOT / "docs" / "copywriting-message-catalog.md").write_text(
        "\n".join(out), encoding="utf-8"
    )


def write_acceptance_checklist() -> None:
    text = """# DesktopCat 目标机器验收清单

这份清单用于把当前礼物包交给她之前，在真实 Windows 电脑上快速检查一遍。重点不是继续加功能，而是确认礼物包能稳定启动、中文正常、能退出、不打扰。

## 要测的包

- 礼物包：`dist/DesktopCatGift_20260612_polished.zip`。
- 解压后程序：`DesktopCatGift/DesktopCatGift.exe`
- 不要把 `raw/wake_*` 实验素材放进礼物包，也不要误提交。

## 准备

- 先把整个 zip 解压出来，不要在压缩包预览窗口里直接运行。
- 如果电脑上已经开着旧版 DesktopCat/DesktopCatGift，先退出。
- 确认 `README_先看我.txt` 和 `DesktopCatGift.exe` 在同一个解压后的文件夹里。
- 如果 Windows SmartScreen 或杀软提示拦截，记录提示内容；能手动确认启动即可。

## 首次启动

- 双击 `DesktopCatGift.exe`。
- 确认呆呆出现在桌面角落附近。
- 确认首次启动欢迎气泡出现一次，约 10 秒后消失，中文 UI 可读，不是乱码。
- 确认会自动生成 `config.json`。
- 退出后再启动一次，确认首次欢迎语不会每次都重复刷屏。

## 基础互动

- 左键点击呆呆：确认有反应，不冻结；基础互动气泡约 3 秒后消失。
- 拖拽呆呆：确认拖拽即时、顺手，气泡会跟着呆呆位置走。
- 拖到新位置后退出再启动：确认上次有效位置能恢复。
- 右键呆呆：确认右键菜单能打开，中文菜单可读。
- 确认菜单里没有旧的 `我想他了`，也没有单独的 `麻麻辛苦啦`。
- 点 `开心一下`、`卖萌一下`、`打个招呼`、`睡一会儿`：确认动作和气泡正常。
- 点 `呆呆安静一下`：确认菜单下次变成 `不用保持安静啦`。
- 点 `不用保持安静啦`：确认恢复正常陪伴。
- 点 `回到屏幕角落`：确认呆呆能回到默认角落，且不会跑出屏幕。
- 确认菜单中没有 `打开配置文件`、`打开配置文件夹` 和 `编辑陪伴语料`。
- 点 `退出`：确认窗口关闭，并且任务管理器里没有残留 `DesktopCatGift.exe`。

## 中文 UI 检查

这些地方要用眼睛看实际窗口或文件，不要只看 PowerShell 输出，因为 PowerShell 可能会把 UTF-8 中文显示成乱码：

- 首次启动气泡。
- 普通互动气泡和状态气泡。
- 吃饭/睡觉提醒按钮，按钮文案应为 `谢谢呆呆的关心，不用再提醒啦`。
- 右键菜单。
- 自动生成的 `README.txt`。
- 礼物包里的 `README_先看我.txt`。
- `partner_custom.json` 里的 `text` 文案。

判断标准：实际窗口和用记事本打开的文件能正常读中文，就算通过；只有终端乱码不算 bug。

## 自动语料和特殊日子

- 普通自动语料会按时间段随机出现，气泡约 3 秒后消失。
- 固定吃饭、睡觉提醒气泡约 15 秒后消失。
- 特殊日子文案支持公历 `month_day` 和农历 `lunar_month_day`。
- 当前内置了纪念日、粑粑生日、麻麻生日，以及春节、元宵、劳动节、端午、七夕、中秋、国庆、圣诞等重要日子。
- 如果要手动验证特殊日子，优先用测试脚本或临时测试配置，不建议在她的真实电脑上改系统日期。

## 通过标准

- 首次启动不用开发环境。
- 呆呆可见、可拖拽、可通过 `回到屏幕角落` 救回。
- 右键互动、低打扰切换、回到角落和退出都能用。
- 中文 UI 在真实窗口和文件里可读。
- `退出` 后没有残留进程。
- 整体感觉仍然是安静陪伴的小礼物，不像一个需要维护的新 app。

## 如果某项失败

- 记录失败步骤，视觉问题尽量截图。
- 如果程序无法启动，在解压目录里测试：`DesktopCatGift.exe --smoke-ms 3000`。
- 如果中文在 UI 里乱码，先用 UTF-8 检查文件内容，再决定是否改代码。
- 如果呆呆跑到屏幕外，优先用右键 `回到屏幕角落`；如果右键不到，就删除 `config.json` 里的 `last_position`。
"""
    (ROOT / "docs" / "target-machine-acceptance-checklist.md").write_text(
        text, encoding="utf-8"
    )


if __name__ == "__main__":
    write_copywriting_catalog()
    write_acceptance_checklist()
