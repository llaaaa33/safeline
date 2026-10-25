# SafeLine 录制台词（目标 ≤ 90 秒）

台词全部是英文（视频给评委看）。**旁白** = 后期配音；**通话** = 你真实打电话时说的话。
AI 那一方的台词是系统真实会说的话，实际措辞可能会有一点点不同，正常。

---

## 录之前（5 分钟）

1. **清空数据，让大屏从空白开始**：在「SafeLine 服务器」终端按 Ctrl-C，然后运行：
   ```
   del safeline.db
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
   ```
2. 电脑连着手机热点，隧道窗口开着。
3. 浏览器打开 http://localhost:8000 ，按 **F11 全屏**，**先点一下页面**（右上角变成「Alarm sound on」）。
4. 录屏：Windows 自带 **Clipchamp → 录制 → 屏幕**（或 Win+G 录屏）。
5. 打电话用**免提**，这样电脑麦克风能把 AI 的声音也录进去。
   （或者正常打，录完告诉我，我从 Vapi 下载两边都很清楚的通话录音给你。）

---

## 1. 故事开场（0:00–0:07）

画面：工地 / 对讲机画面，或卡片 `story.png`

**旁白：**
> My family has a background in construction. Most crews we know still talk over walkie-talkies.

## 2. 对讲机的问题（0:07–0:20）

画面：卡片 `pain.png`

**旁白：**
> But a radio is still an interface. You need a free hand to push to talk. Everyone shares one noisy channel — if you weren't listening, you missed it. Nothing is recorded. And crews speak different languages.

## 3. 产品（0:20–0:29）

画面：设备概念图（标 **Concept**）→ 卡片 `product.png`

**旁白：**
> SafeLine is a voice safety device. It works like the radio you already carry — press once and talk — but you're talking to an AI that listens.

## 4. 原型说明（0:29–0:33）

画面：字卡 **"Today's prototype is the software. A phone call stands in for the device."**

**旁白：**
> Today's prototype is the software. A phone call stands in for the device.

---

## 5. 通话 1：报告隐患（0:33–0:50）

画面：先录**通话前**的大屏（Zone B = CLEAR），打电话，挂断后大屏更新。

拨打 **+1 (858) 348-9303**

> **SafeLine:** Safe Line. Report a hazard, or ask me about a zone.
> **你:** There's a loose plank on the level 3 scaffold in Zone B. Somebody could fall.
> **SafeLine:** Got it. The safety manager has been alerted. *(… Stay safe. Goodbye.)*
> *（AI 自己挂断）*

如果 AI 追问 *"Which zone is that in?"*，就回答 **"Zone B."**

大屏这时会：左边出现对话字幕，中间出现 **loose scaffold plank · HIGH**，右边 **Zone B 变成 1 OPEN**（橙色），并响一声提示音。

**旁白（挂断后，配大屏）：**
> The safety manager sees it in seconds, in the worker's own words.

## 6. 通话 2：语音提问（0:50–1:06）

再拨一次 **+1 (858) 348-9303**

> **SafeLine:** Safe Line. Report a hazard, or ask me about a zone.
> **你:** Is Zone B safe right now?
> **SafeLine:** Zone B has one open hazard: a loose scaffold plank. Avoid that area.
> **SafeLine:** Anything else?
> **你:** No, thanks.
> **SafeLine:** Stay safe. Goodbye.

**字幕条（可选）：** Workers ask by voice. Answers come from live site data.

## 7. 经理打勾解决（1:06–1:15）

画面：鼠标点隐患卡片右边的 **Mark resolved** → 卡片划掉、移到 Resolved → **Zone B 变回绿色 CLEAR**

**旁白：**
> When it's fixed, the manager checks it off. Nothing reported by voice gets lost.

（时间够的话可以再打一次 **"Is Zone B safe now?"** → SafeLine：**"Zone B is clear."**）

## 8. 结尾（1:15–1:24）

画面：卡片 `close.png`

**旁白：**
> Workers talk. Managers see. Nothing gets lost. SafeLine.

---

## 小提示

- 通话里的停顿、等待在剪辑时剪掉，通话部分保持紧凑。
- 旁白语速放慢一点，平静、自信，不用夸张。名字读作 **"Safe Line"**（两个词）。
- 总时长超了就先缩短第 2 段（对讲机的问题）或去掉第 7 段的再次提问。
- 卡片图在 `video/build/` 里；大屏截图 `dash_*.png` 可以当备用画面。
