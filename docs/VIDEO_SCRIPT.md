# 演示视频脚本（表单要求公开链接，90 秒以内）

评委只看提交材料，所以视频要一眼看懂：**工人全程没碰屏幕，经理在大屏上看到并处理**。

## 录之前的准备

- [ ] 手机通讯录里把 +1 (858) 348-9303 存成联系人 **Safe Line**，试一次「Hey Siri, call Safe Line on speaker」。
- [ ] 道具：手套，手里拿个工具 / 箱子；有反光背心或安全帽更好。手机放胸前口袋，**屏幕朝里**。
- [ ] 电脑：浏览器全屏开大屏 http://localhost:8000，**先点一下页面开启警报声**（右上角变成「Alarm sound on」）。Discord 窗口备用（填了 webhook 才有）。
- [ ] 录制：Windows 自带 **Clipchamp → 录制 → 屏幕和摄像头**。屏幕选大屏那个浏览器窗口，摄像头小窗拍你，麦克风收音（手机免提的声音会一起录进去）。
- [ ] 清空旧数据：停服务器 → 删除 `safeline.db` → 重启服务器，大屏从空白开始。
- [ ] 电脑连手机热点，隧道窗口开着。安静的房间。录 2–3 遍，挑最好的一条。

## 分镜（分段录，最后在 Clipchamp 里剪掉等待时间）

| # | 时长 | 画面 | 你说 / 发生什么 |
|---|---|---|---|
| 1 | 0:00–0:08 | 摄像头大画面：你戴着手套、手里拿着东西 | 「Construction workers have gloves on, hands full, and no time for an app. Safe Line has **no interface**.」 |
| 2 | 0:08–0:35 | 切到大屏（你在小窗） | 「Hey Siri, call Safe Line on speaker.」→ Safe Line：「Safe Line. What's the hazard, and where?」→ 你：「Loose plank on the level 3 scaffold, Zone B. Somebody could fall.」→ Safe Line 确认「the safety manager has been alerted」。左栏字幕滚动，右栏 **Zone B 变橙色**，提示音响。 |
| 3 | 0:35–0:45 | 大屏放大到隐患卡片（Clipchamp 里放大） | 字幕卡 / 旁白：「The manager sees it in seconds — the worker's own words, severity, zone.」 |
| 4 | 0:45–1:05 | 大屏 | 你再打：「Help! Someone fell off a ladder in Zone A!」→「Help is on the way…」→ **红色横幅 + 警报声**，Zone A 变红 EMERGENCY。 |
| 5 | 1:05–1:20 | 大屏，鼠标点 | 经理点「Mark resolved」→ 卡片划掉移到 Resolved，**Zone B 变回绿色 CLEAR**。旁白：「When it's fixed, the manager closes it. Nothing reported by voice gets lost.」 |
| 6 | 1:20–1:28 | 摄像头 | 「No screen, no app, any phone, any language. Safe Line.」 |

时间不够时：先缩短第 3 幕；**第 2 幕（手不碰手机报告）一定要完整**，它最能说明 no interface。
