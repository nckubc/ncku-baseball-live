# 成大棒球 線上觀賽

觀眾打開網址就能看 YouTube 直播，同時看到即時比分、陣容、聊天彈幕，還可以替球員刷火箭。

## 每場比賽前要做的事（約 1 分鐘）

1. 在 YouTube 排好這場直播，複製直播網址，例如 `https://www.youtube.com/live/xxxxxxxxxxx`。
2. 用手機或電腦打開 **直播管理頁**：<https://nckubc.github.io/ncku-baseball-live/admin.html>
3. 按「用 Google 登入」，選 **nckubc@gmail.com**（只有這個帳號能改）。
4. 把網址貼進「直播網址」，下面會出現預覽；確認沒錯按 **儲存直播網址**。
5. 幾秒內，所有已經開著網頁的觀眾也會自動換上新的直播。

不用再改 `config.json`。設定存在 Firebase 的 `/config`；只有在 Firebase 讀不到時，網頁才會退回用 `config.json` 的 `yt`。

分享給觀眾的連結永遠是同一個：<https://nckubc.github.io/ncku-baseball-live/>

比分、陣容、系統播報會自動讀「比賽紀錄系統」上傳到雲端的資料；紀錄系統要開啟「雲端即時備份」。

## DEMO

- 開啟方式：在比分上 1.5 秒內連點 5 下，或網址加 `?demo=1`。
- 在直播管理頁的「DEMO 影片」設定要播的影片、**起點**（秒，或 `分:秒`）和**每球秒數**（預設 25）。
  DEMO 開始時從起點播放，每按一次「下一球」跳到 `起點 + 第幾球 × 每球秒數`；「▶ 自動」也會用每球秒數換下一球。按「離開 DEMO」回到正式直播。

## 其他

- 臨時想分享某一部影片：在網址後面加 `?v=影片ID`，會優先播放那一部。
- 播放優先順序：`?v=` ＞ 觀眾自己在設定裡填的測試網址 ＞ 直播管理頁（Firebase `/config`）＞ `config.json`。
- `index.src.html` 是原始碼；`index.html` 由 `build_live.py` 產生（會把示範資料內嵌進去）。
- 權限：Firebase Realtime Database 規則只允許已驗證的 nckubc@gmail.com 寫入 `/config`；任何人都能讀。
