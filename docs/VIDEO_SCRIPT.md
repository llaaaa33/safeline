# 演示视频脚本（表单要求公开链接，90 秒以内）

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

90 秒很紧，**每一幕都要分段录，最后在 Clipchamp 里剪掉等待和响铃的时间**（比如 Mike 那边响铃 10 秒，只留 1–2 秒）。

| # | 时长 | 画面 | 你说 / 发生什么 |
|---|---|---|---|
| 1 | 0:00–0:08 | 摄像头大画面：你戴着手套、手里拿着东西 | 「Construction workers have gloves on, hands full, and no time for an app. SafeLine has **no interface**.」 |
| 2 | 0:08–0:35 | 切到大屏（你在小窗） | 「Hey Siri, call SafeLine on speaker.」→ SafeLine：「SafeLine. What's the hazard, and where?」→ 你：「Loose plank on the level 3 scaffold, Zone B. Somebody could fall.」→ SafeLine 确认「warning one coworker」。大屏上字幕滚动，Zone B 隐患出现。 |
| 3 | 0:35–0:47 | 大屏 + Google Voice 标签页 | Mike 那一路响铃 → 接起来听到「Safety alert for Zone B…」→ 大屏上这条变成 **delivered**。字幕卡：「Every worker in Zone B is called in seconds.」 |
| 4 | 0:47–1:07 | 大屏，你在小窗**不动** | Mike 报告 **Zone A** 的隐患 →**你口袋里的手机自动接通**，警告从口袋里播出来。你说：「My phone answered itself. I never touched it.」 |
| 5 | 1:07–1:20 | 大屏 | 你打进来：「Help! Someone fell off a ladder in Zone A!」→「Help is on the way…」→ 大屏红色横幅 + 警报声，Discord `@here`。 |
| 6 | 1:20–1:28 | 摄像头 | 「No screen, no app, any phone, any language. SafeLine.」 |

时间不够时的取舍：先剪第 5 幕（紧急情况），**第 4 幕（自动接听）一定要留**，它最能说明「no interface」。

## 注意

- 第 4 幕需要 Mike 在你的区：报告 Zone A 时，你（Presenter, Zone A）会被打电话。用 Google Voice 打给 SafeLine 时，Mike 的号码要在名单里（它在 Zone B，报告 Zone A 没问题）。
- 如果某一幕没录好，可以分段录再在 Clipchamp 里拼起来。
- 视频开头 10 秒最重要：评委可能只看前几秒就决定要不要看完。
