# GitHub 基礎操作流程 (QA 專屬 SOP)

本指令集定義了 QA 如何管理自動化測試腳本。

## 角色與目標
- **角色**：Junior QA
- **目標**：確保自動化腳本 (`execution/*.py`) 在本地開發後，能正確、安全地同步至 GitHub。

## AI 協作 Commit 流程
本專案預設採用「**AI 幫忙準備，人類做最後確認與提交**」的方式，而不是自動 commit。

### AI 可以負責
- 修改檔案
- 執行基本驗證
- 整理變更摘要
- 草擬 commit message
- 草擬 commit description / 工作日誌
- 在使用者確認後協助 stage 或 commit

### 使用者負責最後決定
- 這次是否真的要 commit
- 這次改動是否需要拆成多個 commit
- 功能是否已經驗證到足夠放心
- commit message 與 description 是否符合這次改動意圖

### 推薦流程
1. AI 先完成修改
2. AI 執行必要驗證
3. AI 整理這次改了什麼、怎麼驗證、結果如何
4. 使用者確認功能與描述
5. 再由使用者自行 commit，或明確授權 AI commit

### Commit 顆粒度原則
- 一次 commit 盡量只做一件完整且可理解的事
- 無關修改不要混在同一個 commit
- 可以獨立回滾的修改，盡量拆成獨立 commit
- 如果同時有設定調整、功能修復、UI 變更，優先考慮拆開

## 操作步驟

### 1. Commit 前先整理變更說明
在建立 commit 前，先留下這次改動的摘要，至少要包含：
- **改了什麼**：這次修改的目標與檔案
- **怎麼驗證**：實際執行了哪些功能、指令或測試
- **結果如何**：成功、失敗、或待補驗證
- **視覺化佐證**：若有 UI、流程或畫面差異，請保留截圖、錄影、dump、報告或前後對照

建議把這些資料先存放在 `.tmp/commit-notes/<日期>-<主題>/`，例如：
```text
.tmp/commit-notes/2026-04-28-auth-env/
- summary.md
- before.png
- after.png
- api-auth.txt
```

### 2. 建立存檔 (Commit)
每當你完成一個測試案例，務必在確認上面的說明與驗證資料齊全後，再執行：
```bash
git add execution/<你的腳本>.py
git commit -m "feat: [描述你寫了什麼測試]"
```

如果要請 AI 協助 commit，請先確認：
- 你已看過這次的功能結果
- 你已看過 summary / 驗證紀錄
- 你同意這次 commit 的範圍與 message

### 3. 同步遠端 (Push)
每天下班前，或是需要給同事看腳本時：
```bash
git push
```

### 4. 常見問題處理
- **如果衝突了？**：別慌，先執行 `git pull --rebase`。
- **忘記指令？**：執行 `git help status`。

## 補充原則
- 如果這次改動跟 UI、截圖、流程結果有關，優先保留可肉眼比對的資料，方便回頭找穩定版本。
- 如果功能壞掉了，先看當次 commit 前留下的 summary 與視覺化資料，再對照 git 歷史，通常會比直接讀 code 更快定位問題。
- 如果這次只做設定或小修，也至少要留下簡短 description，避免未來不知道這次 commit 的意圖。
