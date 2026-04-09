# GitHub 基礎操作流程 (QA 專屬 SOP)

本指令集定義了 QA 如何管理自動化測試腳本。

## 角色與目標
- **角色**：Junior QA
- **目標**：確保自動化腳本 (`execution/*.py`) 在本地開發後，能正確、安全地同步至 GitHub。

## 操作步驟

### 1. 建立存檔 (Commit)
每當你完成一個測試案例，務必執行：
```bash
git add execution/<你的腳本>.py
git commit -m "feat: [描述你寫了什麼測試]"
```

### 2. 同步遠端 (Push)
每天下班前，或是需要給同事看腳本時：
```bash
git push
```

### 3. 常見問題處理
- **如果衝突了？**：別慌，先執行 `git pull --rebase`。
- **忘記指令？**：執行 `git help status`。
