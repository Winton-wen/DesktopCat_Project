# DesktopCat 全部语料与触发条件修改稿

这份文档列出当前礼物版 DesktopCat 会用到的全部语料、菜单文字、README 文案和触发条件。你可以逐条修改“修改后文案”和“修改后触发条件/时间”，再交给我同步到工程。

当前礼物 EXE 的入口是 `gift_launcher.py` -> `RigDesktopCatApp`。旧版备用语料已经不再列入，也不会再作为后续修改对象。

## 0. 怎么填写

- **工程模板**：实际存入工程的文字。
- **默认显示**：使用默认称呼时，她实际看到的文字。
- **当前触发条件/时间**：现在什么情况下出现。
- **修改后文案**：直接写你想要的新文字；不改可以留空。
- **修改后触发条件/时间**：想改触发时间、日期、冷却或动作时填写；不改可以留空。

可用占位符：

- `{pet_name}`：默认显示为“呆呆”。
- `{mama_nickname}`：默认显示为“麻麻”。
- `{papa_nickname}`：默认显示为“粑粑”。
- `{anniversary_year_cn}`：周年纪念日自动计算出的中文周年数。

新增普通自动语料时，建议使用 `category`、`text`、`cooldown_hours`、`action`。新增特殊日子语料时，公历用 `month_day: "MM-DD"`，农历用 `lunar_month_day: "MM-DD"`。
可用动作：`wave` 招手，`cute` 卖萌，`happy` 开心跳跃，`blink` 眨眼，`sleep` 睡眠。

## A. 默认称呼

### A-01 `pet_name`

- 当前默认值：`呆呆`
- 用途：小猫名字，替换所有 `{pet_name}`。
- 修改后默认值：

### A-02 `mama_nickname`

- 当前默认值：`麻麻`
- 用途：呆呆对她的称呼，替换所有 `{mama_nickname}`。
- 修改后默认值：

### A-03 `papa_nickname`

- 当前默认值：`粑粑`
- 用途：呆呆对你的称呼，替换所有 `{papa_nickname}`。
- 修改后默认值：

### A-04 `partner_nickname`

- 当前默认值：`麻麻`
- 用途：旧配置兼容字段，新文案不建议继续使用。
- 修改后默认值：

## B. 基础互动气泡

### B-01 `pet`

- 工程 key：`pet`
- 工程模板：
  - `喜欢{mama_nickname}摸我的头៷>ᴗ<៷`
  - `哎呀呀好痒呀好痒呀！`
  - `喵喵喵꜀(^. .^꜀  )꜆੭`
- 默认显示：
  - `喜欢麻麻摸我的头៷>ᴗ<៷`
  - `哎呀呀好痒呀好痒呀！`
  - `喵喵喵꜀(^. .^꜀  )꜆੭`
- 当前触发条件/时间：左键点击呆呆；如果正在睡觉则优先触发唤醒。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`clicked`
- 修改后文案：
- 修改后触发条件/时间：

### B-02 `happy`

- 工程 key：`happy`
- 工程模板：
  - `{mama_nickname}看，{pet_name}跳一下！`
  - `(*^ω^*)开心`
  - `cchh，嘟嘟哒哒⌯ᵔᗜᵔ⌯`
- 默认显示：
  - `麻麻看，呆呆跳一下！`
  - `(*^ω^*)开心`
  - `cchh，嘟嘟哒哒⌯ᵔᗜᵔ⌯`
- 当前触发条件/时间：右键点“开心一下”；随机待机也可能触发开心动作并随机显示其中一条气泡。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`happy`
- 修改后文案：
- 修改后触发条件/时间：

### B-03 `cute`

- 工程 key：`cute`
- 工程模板：
  - `{mama_nickname}看{pet_name}可爱嘛`
  - `{pet_name}最最最喜欢{mama_nickname}啦˶>ᗜ<˶`
  - `真的不和{pet_name}玩一下嘛ₒ⦁⩊⦁ₒ`
- 默认显示：
  - `麻麻看呆呆可爱嘛`
  - `呆呆最最最喜欢麻麻啦˶>ᗜ<˶`
  - `真的不和呆呆玩一下嘛ₒ⦁⩊⦁ₒ`
- 当前触发条件/时间：右键点“卖萌一下”；随机待机可能播放卖萌动作，但只有主动菜单会显示这组气泡。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`cute`
- 修改后文案：
- 修改后触发条件/时间：

### B-04 `wave`

- 工程 key：`wave`
- 工程模板：
  - `{mama_nickname}，看这里呀。`
  - `你好呀，我是呆呆~`
- 默认显示：
  - `麻麻，看这里呀。`
  - `你好呀，我是呆呆~`
- 当前触发条件/时间：右键点“打个招呼”，或双击呆呆。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`wave`
- 修改后文案：
- 修改后触发条件/时间：

### B-05 `sleep`

- 工程 key：`sleep`
- 工程模板：
  - `ᶻz ₍^_ ̫ _^₎`
- 默认显示：
  - `ᶻz ₍^_ ̫ _^₎`
- 当前触发条件/时间：右键点“睡一会儿”。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`sleep_in -> sleep`
- 修改后文案：
- 修改后触发条件/时间：

### B-06 `wake`

- 工程 key：`wake`
- 工程模板：
  - `呆呆醒啦՞･∞･՞`
- 默认显示：
  - `呆呆醒啦՞･∞･՞`
- 当前触发条件/时间：呆呆处于睡眠动作时左键点击。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`wake`
- 修改后文案：
- 修改后触发条件/时间：

### B-07 `walk_left`

- 工程 key：`walk_left`
- 工程模板：
  - `天才在左。`
- 默认显示：
  - `天才在左。`
- 当前触发条件/时间：右键点“向左走两步”。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`walk_left`
- 修改后文案：
- 修改后触发条件/时间：

### B-08 `walk_right`

- 工程 key：`walk_right`
- 工程模板：
  - `疯子在右。`
- 默认显示：
  - `疯子在右。`
- 当前触发条件/时间：右键点“向右走两步”。 同一 key 下多条文案会随机选择一条；气泡显示约 3 秒。
- 动作：`walk`
- 修改后文案：
- 修改后触发条件/时间：

## C. 首次启动与状态气泡

### C-01 `first_launch`

- 工程模板：`呆呆来啦！我以后就是麻麻的桌面小猫啦`
- 默认显示：`呆呆来啦！我以后就是麻麻的桌面小猫啦`
- 当前触发条件/时间：第一次运行时，启动约 1.2 秒后显示；正常只显示一次；气泡显示约 10 秒。
- 动作：`wave`
- 修改后文案：
- 修改后触发条件/时间：

### C-02 `low_distraction_on`

- 工程模板：`{pet_name}会乖乖安静地陪着{mama_nickname}\n꜀(^. .^꜀  )꜆੭`
- 默认显示：`呆呆会乖乖安静地陪着麻麻\n꜀(^. .^꜀  )꜆੭`
- 当前触发条件/时间：右键点“呆呆安静一下”；气泡显示约 3 秒。
- 动作：`idle`
- 修改后文案：
- 修改后触发条件/时间：

### C-03 `low_distraction_off`

- 工程模板：`呆呆要和麻麻玩！`
- 默认显示：`呆呆要和麻麻玩！`
- 当前触发条件/时间：右键点“不用保持安静啦”；气泡显示约 3 秒。
- 动作：`idle`
- 修改后文案：
- 修改后触发条件/时间：

### C-04 `return_corner_done`

- 工程模板：`{pet_name}跳回屏幕角落啦。`
- 默认显示：`呆呆跳回屏幕角落啦。`
- 当前触发条件/时间：右键点“回到屏幕角落”，返回动画完成后显示；气泡显示约 3 秒。
- 动作：`idle`
- 修改后文案：
- 修改后触发条件/时间：

## D. 右键菜单文字

### D-01

- 当前文字：`开心一下`
- 用途：播放开心动作并显示 B-02。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-02

- 当前文字：`卖萌一下`
- 用途：播放卖萌动作并显示 B-03。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-03

- 当前文字：`打个招呼`
- 用途：播放招手动作并显示 B-04。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-04

- 当前文字：`向左走两步`
- 用途：向左移动并显示 B-07。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-05

- 当前文字：`向右走两步`
- 用途：向右移动并显示 B-08。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-06

- 当前文字：`睡一会儿`
- 用途：进入睡眠并显示 B-05。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-07

- 当前文字：`呆呆安静一下`
- 用途：当前为正常模式时显示，点击后进入更安静的陪伴模式。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-08

- 当前文字：`不用保持安静啦`
- 用途：当前为低打扰模式时显示，点击后恢复正常陪伴。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-09

- 当前文字：`回到屏幕角落`
- 用途：让呆呆返回默认角落。
- 修改后菜单文字：
- 修改后触发条件/时间：

### D-10

- 当前文字：`退出`
- 用途：关闭呆呆和气泡窗口。
- 修改后菜单文字：
- 修改后触发条件/时间：

说明：右键菜单中已删除单独的安慰入口；原先三条安慰文案已并入 F 组普通自动语料。

## E. 固定时间提醒

### E-01 `lunch`

- 工程模板：`{mama_nickname}要记得按时吃午饭呀，不然呆呆和粑粑都会担心的喔՞･∞･՞`
- 默认显示：`麻麻要记得按时吃午饭呀，不然呆呆和粑粑都会担心的喔՞･∞･՞`
- 当前触发条件/时间：每天 11:45-12:15 附近；当天只提醒一次；气泡显示约 15 秒。
- 按钮文字：`谢谢呆呆的关心，不用再提醒啦`
- 修改后文案：
- 修改后触发条件/时间：

### E-02 `dinner`

- 工程模板：`{mama_nickname}该吃晚饭啦，想吃什么可以和粑粑说呀₍⑅ᐢ..ᐢ₎`
- 默认显示：`麻麻该吃晚饭啦，想吃什么可以和粑粑说呀₍⑅ᐢ..ᐢ₎`
- 当前触发条件/时间：每天 18:00-19:00 附近；当天只提醒一次；气泡显示约 15 秒。
- 按钮文字：`谢谢呆呆的关心，不用再提醒啦`
- 修改后文案：
- 修改后触发条件/时间：

### E-03 `bedtime`

- 工程模板：`已经很晚啦，{mama_nickname}早点休息呀\n꜀(^. .^꜀  )꜆੭`
- 默认显示：`已经很晚啦，麻麻早点休息呀\n꜀(^. .^꜀  )꜆੭`
- 当前触发条件/时间：每天 23:00-23:45 附近；当天只提醒一次；气泡显示约 15 秒。
- 按钮文字：`谢谢呆呆的关心，不用再提醒啦`
- 修改后文案：
- 修改后触发条件/时间：

### E-04 `late_night`

- 工程模板：`{mama_nickname}还在忙嘛...{pet_name}会一直陪伴{mama_nickname}呀，但是{mama_nickname}也要早点睡觉呀，熬夜记得补充水分呀。`
- 默认显示：`麻麻还在忙嘛...呆呆会一直陪伴麻麻呀，但是麻麻也要早点睡觉呀，熬夜记得补充水分呀。`
- 当前触发条件/时间：每天 00:30-02:00 附近；当天只提醒一次；气泡显示约 15 秒。
- 按钮文字：`谢谢呆呆的关心，不用再提醒啦`
- 修改后文案：
- 修改后触发条件/时间：

## F. 自动陪伴语料

时间段分类：

- `morning`: 07:00-11:30
- `lunch`: 11:30-13:30
- `afternoon`: 13:30-18:00
- `evening`: 18:00-22:30
- `late_night`: 01:30-05:00
- `bedtime`: 其余时间

特殊日子优先于全部普通语料。非低打扰状态下，程序会把当前时间段语料与`miss_you`、`busy_support`、`comfort`、`encouragement` 通用语料合并，再从冷却结束的候选中随机选择一条；气泡显示约 3 秒。低打扰状态不播放自动陪伴语料。`cooldown_hours` 表示同一条语料再次出现前至少等待多少小时。

### F-01 `morning_01`

- category：`morning`
- 工程模板：`早上好呀{mama_nickname}！{pet_name}来陪你开启新的一天啦꜀(^. .^꜀  )꜆੭`
- 默认显示：`早上好呀麻麻！呆呆来陪你开启新的一天啦꜀(^. .^꜀  )꜆੭`
- cooldown_hours：`24`
- action：`wave`
- 当前触发条件/时间：当前时间属于 `morning` 时参与随机选择。 同 ID 距上次显示至少 24 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-02 `morning_02`

- category：`morning`
- 工程模板：`{mama_nickname}先伸个懒腰吧，{pet_name}也要醒醒啦₍ᵔ･•･ᵔ₎`
- 默认显示：`麻麻先伸个懒腰吧，呆呆也要醒醒啦₍ᵔ･•･ᵔ₎`
- cooldown_hours：`24`
- action：`cute`
- 当前触发条件/时间：当前时间属于 `morning` 时参与随机选择。 同 ID 距上次显示至少 24 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-03 `lunch_01`

- category：`lunch`
- 工程模板：`{mama_nickname}要好好吃午饭呀，{pet_name}会帮粑粑认真监督你的喔`
- 默认显示：`麻麻要好好吃午饭呀，呆呆会帮粑粑认真监督你的喔`
- cooldown_hours：`12`
- action：`wave`
- 当前触发条件/时间：当前时间属于 `lunch` 时参与随机选择。 同 ID 距上次显示至少 12 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-04 `afternoon_01`

- category：`afternoon`
- 工程模板：`{mama_nickname}下午也辛苦啦，累了的话就和{pet_name}一起发一会儿呆吧₍ᵔ･•･ᵔ₎`
- 默认显示：`麻麻下午也辛苦啦，累了的话就和呆呆一起发一会儿呆吧₍ᵔ･•･ᵔ₎`
- cooldown_hours：`18`
- action：`cute`
- 当前触发条件/时间：当前时间属于 `afternoon` 时参与随机选择。 同 ID 距上次显示至少 18 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-05 `evening_01`

- category：`evening`
- 工程模板：`{mama_nickname}辛苦一天啦，{pet_name}来贴贴你\n꜀(^. .^꜀  )꜆੭`
- 默认显示：`麻麻辛苦一天啦，呆呆来贴贴你\n꜀(^. .^꜀  )꜆੭`
- cooldown_hours：`18`
- action：`happy`
- 当前触发条件/时间：当前时间属于 `evening` 时参与随机选择。 同 ID 距上次显示至少 18 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-06 `bedtime_01`

- category：`bedtime`
- 工程模板：`很晚啦，{pet_name}想和{mama_nickname}一起早点睡觉呀ᶻz ₍^_ ̫ _^₎`
- 默认显示：`很晚啦，呆呆想和麻麻一起早点睡觉呀ᶻz ₍^_ ̫ _^₎`
- cooldown_hours：`12`
- action：`sleep`
- 当前触发条件/时间：当前时间属于 `bedtime` 时参与随机选择。 同 ID 距上次显示至少 12 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-07 `late_night_01`

- category：`late_night`
- 工程模板：`{mama_nickname}还没睡嘛，{pet_name}好心疼{mama_nickname}\n(｡í _ ì｡)，{mama_nickname}忙完就早点休息吧。`
- 默认显示：`麻麻还没睡嘛，呆呆好心疼麻麻\n(｡í _ ì｡)，麻麻忙完就早点休息吧。`
- cooldown_hours：`12`
- action：`sleep`
- 当前触发条件/时间：当前时间属于 `late_night` 时参与随机选择。 同 ID 距上次显示至少 12 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-08 `miss_you_01`

- category：`miss_you`
- 工程模板：`{pet_name}也想{papa_nickname}啦。等以后住在一起，我们就能天天在一个家里啦。`
- 默认显示：`呆呆也想粑粑啦。等以后住在一起，我们就能天天在一个家里啦。`
- cooldown_hours：`36`
- action：`wave`
- 当前触发条件/时间：任意时间段均可作为通用语料参与随机选择。 同 ID 距上次显示至少 36 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-09 `busy_support_01`

- category：`busy_support`
- 工程模板：`{mama_nickname}先忙啵，{pet_name}会安安静静待在这里。`
- 默认显示：`麻麻先忙啵，呆呆会安安静静待在这里。`
- cooldown_hours：`24`
- action：`blink`
- 当前触发条件/时间：任意时间段均可作为通用语料参与随机选择。 同 ID 距上次显示至少 24 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-10 `comfort_01`

- category：`comfort`
- 工程模板：`事情不顺利也没关系，{pet_name}会一直陪伴{mama_nickname}呀，有什么不开心的事情可以和粑粑说呀。`
- 默认显示：`事情不顺利也没关系，呆呆会一直陪伴麻麻呀，有什么不开心的事情可以和粑粑说呀。`
- cooldown_hours：`36`
- action：`cute`
- 当前触发条件/时间：任意时间段均可作为通用语料参与随机选择。 同 ID 距上次显示至少 36 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-11 `comfort_02`

- category：`comfort`
- 工程模板：`{mama_nickname}今天辛苦啦，先摸摸{pet_name}好好放松一下吧₍⑅ᐢ..ᐢ₎`
- 默认显示：`麻麻今天辛苦啦，先摸摸呆呆好好放松一下吧₍⑅ᐢ..ᐢ₎`
- cooldown_hours：`36`
- action：`cute`
- 当前触发条件/时间：任意时间段均可作为通用语料参与随机选择。 同 ID 距上次显示至少 36 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-12 `comfort_03`

- category：`comfort`
- 工程模板：`忙完这一阵就休息一会儿吧，{pet_name}在这里陪{mama_nickname}哟՞･∞･՞`
- 默认显示：`忙完这一阵就休息一会儿吧，呆呆在这里陪麻麻哟՞･∞･՞`
- cooldown_hours：`36`
- action：`cute`
- 当前触发条件/时间：任意时间段均可作为通用语料参与随机选择。 同 ID 距上次显示至少 36 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-13 `encouragement_01`

- category：`encouragement`
- 工程模板：`今天已经做得很好啦，{mama_nickname}的努力{pet_name}都看见了喔ₒ⦁⩊⦁ₒ`
- 默认显示：`今天已经做得很好啦，麻麻的努力呆呆都看见了喔ₒ⦁⩊⦁ₒ`
- cooldown_hours：`36`
- action：`happy`
- 当前触发条件/时间：任意时间段均可作为通用语料参与随机选择。 同 ID 距上次显示至少 36 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-14 `encouragement_02`

- category：`encouragement`
- 工程模板：`{mama_nickname}已经很努力啦。喝点水，今晚也要对自己温柔一点呀⌯ᵔᗜᵔ⌯`
- 默认显示：`麻麻已经很努力啦。喝点水，今晚也要对自己温柔一点呀⌯ᵔᗜᵔ⌯`
- cooldown_hours：`36`
- action：`happy`
- 当前触发条件/时间：任意时间段均可作为通用语料参与随机选择。 同 ID 距上次显示至少 36 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-15 `special_anniversary_0324`

- category：`special_day`
- month_day：`03-24`
- 工程模板：`今天是{mama_nickname}和{papa_nickname}在一起的{anniversary_year_cn}周年纪念日，希望{mama_nickname}{papa_nickname}和{pet_name}可以永远在一起呀˶>ᗜ<˶`
- 默认显示：`今天是麻麻和粑粑在一起的二周年纪念日，希望麻麻粑粑和呆呆可以永远在一起呀˶>ᗜ<˶`
- cooldown_hours：`72`
- action：`happy`
- 当前触发条件/时间：每年公历 03-24，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-16 `special_valentine_0214`

- category：`special_day`
- month_day：`02-14`
- 工程模板：`{mama_nickname}情人节快乐呀！{pet_name}想看{mama_nickname}和{papa_nickname}亲亲¯꒳¯`
- 默认显示：`麻麻情人节快乐呀！呆呆想看麻麻和粑粑亲亲¯꒳¯`
- cooldown_hours：`72`
- action：`happy`
- 当前触发条件/时间：每年公历 02-14，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-17 `special_love_day_0520`

- category：`special_day`
- month_day：`05-20`
- 工程模板：`{mama_nickname}520快乐呀！{pet_name}和{papa_nickname}都爱{mama_nickname}呀៷>ᴗ<៷`
- 默认显示：`麻麻520快乐呀！呆呆和粑粑都爱麻麻呀៷>ᴗ<៷`
- cooldown_hours：`72`
- action：`cute`
- 当前触发条件/时间：每年公历 05-20，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-18 `special_labor_day_0501`

- category：`special_day`
- month_day：`05-01`
- 工程模板：`{mama_nickname}劳动节快乐呀，{pet_name}眼中的{mama_nickname}是全世界最勤劳滴(๓´˘`๓)`
- 默认显示：`麻麻劳动节快乐呀，呆呆眼中的麻麻是全世界最勤劳滴(๓´˘`๓)`
- cooldown_hours：`72`
- action：`wave`
- 当前触发条件/时间：每年公历 05-01，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-19 `special_papa_birthday_0912`

- category：`special_day`
- month_day：`09-12`
- 工程模板：`今天是{papa_nickname}的生日耶！{pet_name}想和{mama_nickname}一起给{papa_nickname}买蛋糕៷>ᴗ<៷`
- 默认显示：`今天是粑粑的生日耶！呆呆想和麻麻一起给粑粑买蛋糕៷>ᴗ<៷`
- cooldown_hours：`72`
- action：`happy`
- 当前触发条件/时间：每年公历 09-12，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-20 `special_mama_birthday_1022`

- category：`special_day`
- month_day：`10-22`
- 工程模板：`{mama_nickname}生日快乐呀！希望{mama_nickname}以后也要天天开心呀˶>ᗜ<˶`
- 默认显示：`麻麻生日快乐呀！希望麻麻以后也要天天开心呀˶>ᗜ<˶`
- cooldown_hours：`72`
- action：`happy`
- 当前触发条件/时间：每年公历 10-22，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-21 `special_national_day_1001`

- category：`special_day`
- month_day：`10-01`
- 工程模板：`{mama_nickname}国庆快乐呀，终于可以休息一段时间啦꜀(^. .^꜀  )꜆੭`
- 默认显示：`麻麻国庆快乐呀，终于可以休息一段时间啦꜀(^. .^꜀  )꜆੭`
- cooldown_hours：`72`
- action：`wave`
- 当前触发条件/时间：每年公历 10-01，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-22 `special_christmas_1225`

- category：`special_day`
- month_day：`12-25`
- 工程模板：`{mama_nickname}圣诞快乐呀，{pet_name}想把小铃铛摇给{mama_nickname}听₍ᵔ･•･ᵔ₎`
- 默认显示：`麻麻圣诞快乐呀，呆呆想把小铃铛摇给麻麻听₍ᵔ･•･ᵔ₎`
- cooldown_hours：`72`
- action：`cute`
- 当前触发条件/时间：每年公历 12-25，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-23 `special_year_end_1231`

- category：`special_day`
- month_day：`12-31`
- 工程模板：`{pet_name}已经忍不住期待和{mama_nickname}{papa_nickname}一起走进新的一年啦˶>ᗜ<˶`
- 默认显示：`呆呆已经忍不住期待和麻麻粑粑一起走进新的一年啦˶>ᗜ<˶`
- cooldown_hours：`72`
- action：`wave`
- 当前触发条件/时间：每年公历 12-31，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-24 `special_new_year_0101`

- category：`special_day`
- month_day：`01-01`
- 工程模板：`{mama_nickname}新年快乐呀，{pet_name}今年也要一直陪着{mama_nickname}和{papa_nickname}(๓´˘`๓)`
- 默认显示：`麻麻新年快乐呀，呆呆今年也要一直陪着麻麻和粑粑(๓´˘`๓)`
- cooldown_hours：`72`
- action：`wave`
- 当前触发条件/时间：每年公历 01-01，当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-25 `special_spring_festival`

- category：`special_day`
- lunar_month_day：`01-01`
- 工程模板：`{mama_nickname}春节快乐呀，{pet_name}要陪{mama_nickname}和{papa_nickname}一起过年˶>ᗜ<˶`
- 默认显示：`麻麻春节快乐呀，呆呆要陪麻麻和粑粑一起过年˶>ᗜ<˶`
- cooldown_hours：`72`
- action：`happy`
- 当前触发条件/时间：每年农历 01-01，换算到对应公历日期后当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-26 `special_lantern_festival`

- category：`special_day`
- lunar_month_day：`01-15`
- 工程模板：`{mama_nickname}元宵节快乐呀，{pet_name}想和{mama_nickname}一起吃甜甜的汤圆(*^ω^*)`
- 默认显示：`麻麻元宵节快乐呀，呆呆想和麻麻一起吃甜甜的汤圆(*^ω^*)`
- cooldown_hours：`72`
- action：`cute`
- 当前触发条件/时间：每年农历 01-15，换算到对应公历日期后当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-27 `special_dragon_boat`

- category：`special_day`
- lunar_month_day：`05-05`
- 工程模板：`{mama_nickname}端午安康呀，{pet_name}今天也要乖乖陪{mama_nickname}꜀(^. .^꜀  )꜆੭`
- 默认显示：`麻麻端午安康呀，呆呆今天也要乖乖陪麻麻꜀(^. .^꜀  )꜆੭`
- cooldown_hours：`72`
- action：`wave`
- 当前触发条件/时间：每年农历 05-05，换算到对应公历日期后当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-28 `special_qixi`

- category：`special_day`
- lunar_month_day：`07-07`
- 工程模板：`{mama_nickname}七夕快乐呀，{pet_name}要用乐高积木帮{mama_nickname}和{papa_nickname}搭鹊桥¯꒳¯`
- 默认显示：`麻麻七夕快乐呀，呆呆要用乐高积木帮麻麻和粑粑搭鹊桥¯꒳¯`
- cooldown_hours：`72`
- action：`cute`
- 当前触发条件/时间：每年农历 07-07，换算到对应公历日期后当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-29 `special_mid_autumn`

- category：`special_day`
- lunar_month_day：`08-15`
- 工程模板：`{mama_nickname}中秋快乐呀，{pet_name}想陪{mama_nickname}和{papa_nickname}一起看月亮՞･∞･՞`
- 默认显示：`麻麻中秋快乐呀，呆呆想陪麻麻和粑粑一起看月亮՞･∞･՞`
- cooldown_hours：`72`
- action：`happy`
- 当前触发条件/时间：每年农历 08-15，换算到对应公历日期后当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

### F-30 `special_double_ninth`

- category：`special_day`
- lunar_month_day：`09-09`
- 工程模板：`重阳节到啦，{pet_name}提醒{mama_nickname}今天也要照顾好自己呀(๓´˘`๓)`
- 默认显示：`重阳节到啦，呆呆提醒麻麻今天也要照顾好自己呀(๓´˘`๓)`
- cooldown_hours：`72`
- action：`wave`
- 当前触发条件/时间：每年农历 09-09，换算到对应公历日期后当天优先于全部普通语料。 同 ID 距上次显示至少 72 小时。
- 修改后文案：
- 修改后触发条件/时间：

## G. 自动生成的配置 README

来源：`src/desktop_cat/config.py` 的 `README_TEXT`。首次创建用户配置目录时写入 `README.txt`，已经存在的 README 不会被自动覆盖。

当前全文：

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

companion_messages/partner_custom.json 是高级自定义陪伴语料文件。
text 支持 {pet_name}、{mama_nickname}、{papa_nickname}。
周年纪念日还可以使用 {anniversary_year_cn} 自动显示中文周年数。
也可以调整 category、cooldown_hours 和 action。
公历特殊日子使用 category=special_day 和 MM-DD 格式的 month_day，例如 07-18。
农历特殊日子使用 category=special_day 和 MM-DD 格式的 lunar_month_day，例如 08-15。

如果自定义语料改坏了，删除 partner_custom.json，程序会继续使用内置默认语料。
```

修改后全文：

```text

```

修改后触发条件/写入方式：

## H. 礼物包 README

来源：`assets/gift/README_先看我.txt`。她解压礼物包后可以直接看到。

当前全文：

```text
这是麻麻和粑粑一起养的电子小猫“呆呆”。

现在我们还不能一起养一只真正的小猫，所以先让呆呆住在你的桌面上，陪你学习、工作、吃饭和休息。

第一次使用：
1. 先解压整个 DesktopCatGift 文件夹。
2. 双击 DesktopCatGift.exe，呆呆会出现在桌面角落。
3. 可以左键摸摸呆呆，也可以拖着它换位置。
4. 右键呆呆可以互动、让它安静陪伴、回到角落或退出。

默认称呼：
- 小猫：呆呆
- 你：麻麻
- 我：粑粑

如果呆呆跑到奇怪的位置，右键点“回到屏幕角落”。
如果想关闭，右键点“退出”。

希望电子呆呆能先陪我们慢慢等到真正一起生活、一起养猫的那一天。
```

修改后全文：

```text

```

修改后触发条件/放置方式：

## I. 新增自动语料格式

### I-01 普通时间段语料

```json
{
  "id": "evening_02",
  "category": "evening",
  "text": "{pet_name}来陪{mama_nickname}休息一下，{papa_nickname}也希望你别太累。",
  "cooldown_hours": 24,
  "action": "cute"
}
```

### I-02 公历特殊日子语料

```json
{
  "id": "special_visit_0718",
  "category": "special_day",
  "month_day": "07-18",
  "text": "今天是特别的日子，{pet_name}要陪{mama_nickname}和{papa_nickname}一起记住。",
  "cooldown_hours": 72,
  "action": "happy"
}
```

### I-03 农历特殊日子语料

```json
{
  "id": "special_mid_autumn",
  "category": "special_day",
  "lunar_month_day": "08-15",
  "text": "中秋快乐呀，{pet_name}想陪{mama_nickname}和{papa_nickname}一起看月亮。",
  "cooldown_hours": 72,
  "action": "happy"
}
```

填写规则：同一天最好只放一条特殊日语料；当前程序会按 `id` 排序并只选第一条可用语料。
农历特殊日当前内置 2026-2030 年换算表。

### I-04 可以直接复制的空白模板

```text
新增语料名称：
希望出现的日期或时间段：
文案：
希望动作：
同一条多久最多出现一次：
是否只在特殊日期出现：
```
