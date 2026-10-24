# 演示视频脚本（目标 90 秒，最长 2 分钟）

评委只看提交材料，所以视频要让人**一眼看懂：工人全程没碰屏幕**。

## 录之前的准备

- [ ] 手机：iPhone「设置 → 辅助功能 → 触控 → 通话音频路由 → 自动接听电话」打开（第 3 幕要用）。
- [ ] 手机通讯录里把 SafeLine 号码存成联系人 **SafeLine**，试一次「Hey Siri, call SafeLine on speaker」。
- [ ] 道具：手套，手里拿个工具 / 箱子；有反光背心或安全帽更好。手机放胸前口袋，**屏幕朝里**（或者用胶带贴住屏幕）。
- [ ] 电脑：浏览器开大屏 http://localhost:8000（先点一下页面，开启警报声）；另一个标签页开 Google Voice（Mike 的号码）；Discord 窗口备用。
- [ ] 录制：Windows 自带 **Clipchamp → 录制 → 屏幕和摄像头**。屏幕选大屏那个浏览器窗口，摄像头小窗拍你，麦克风收音（手机免提的声音会一起录进去）。
- [ ] 先用模拟脚本清一遍流程，再删掉 `safeline.db` 让大屏从空白开始。
- [ ] 安静的房间。录 2–3 遍，挑最好的一条。

## 分镜

| # | 时长 | 画面 | 你说 / 发生什么 |
|---|---|---|---|
| 1 | 0:00–0:10 | 摄像头大画面：你戴着手套、手里拿着东西 | 「Construction workers wear gloves, climb ladders, work in noise. They can't stop to use an app. So we built SafeLine — a safety network with **no interface**.」 |
| 2 | 0:10–0:40 | 切到大屏（你在小窗） | 「Hey Siri, call SafeLine on speaker.」→ SafeLine：「SafeLine. What's the hazard, and where?」→ 你：「There's a loose plank on the level 3 scaffold in Zone B. Somebody could fall.」→ SafeLine 确认「warning one coworker」。大屏上字幕滚动，Zone B 隐患出现。 |
| 3 | 0:40–0:55 | 大屏 + Google Voice 标签页 | Mike 那一路响铃，接起来听到：「Safety alert for Zone B…」，大屏上这条变成 **delivered**。旁白一句：「Mike, one floor up, gets warned in seconds.」 |
| 4 | 0:55–1:15 | 大屏，你在小窗**不动** | 用 Google Voice（Mike）打给 SafeLine 报告 **Zone A** 的隐患 →**你口袋里的手机自动接通**，警告从口袋里播出来。旁白：「And when someone else reports a hazard in my zone, my phone answers itself. I never touched it.」 |
| 5 | 1:15–1:30 | 大屏 | 你再打一次：「Help! Someone just fell off a ladder in Zone A!」→ SafeLine：「Help is on the way…」→ 大屏红色横幅 + 警报声，Discord `@here`。 |
| 6 | 1:30–1:40 | 摄像头 | 「Workers never touched a screen. Any phone, any language, nothing to install. That's SafeLine.」 |

## 注意

- 第 4 幕需要 Mike 在你的区：报告 Zone A 时，你（Presenter, Zone A）会被打电话。用 Google Voice 打给 SafeLine 时，Mike 的号码要在名单里（它在 Zone B，报告 Zone A 没问题）。
- 如果某一幕没录好，可以分段录再在 Clipchamp 里拼起来。
- 视频开头 10 秒最重要：评委可能只看前几秒就决定要不要看完。
