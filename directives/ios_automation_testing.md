# iOS Automation Test SOP

## 概述
這份文件定義了在為此專案進行 iOS 自動化測試時的標準作業流程。
我們使用 RD 提供的 `AccessibilityIdentifiers` 作為 UI 互動的核心依據，確保 UI 更動時測試腳本的穩定性。

## 目標
透過確保 Python 測試腳本能穩定呼叫頁面上各個 UI 元件（藉著 Mapping 好的 Accessibility IDs），完成自動化測試任務。

## 執行規範

1. **Accessibility ID 的引用**
   - 不要直接在腳本中 Hardcode 字串（例如：`"LoginViewController.appleSignButton"`）。
   - 請一律引用 `execution/accessibility_ids.py` 內的類別和常數。
   - 範例：`import accessibility_ids` 然後使用 `accessibility_ids.LoginAccessibilityID.LoginViewController.appleSignButton`。

2. **撰寫測試腳本（`execution/` 內）**
   - 腳本需具備高度容錯與重試機制（例如等待元件載入）。
   - 請根據當前實作的框架（如 Appium 或者自建的 ios-simulator-skill）編寫測試。

3. **測試報告與成品**
   - 所有暫存截圖或執行日誌都應存放於 `.tmp/`。
   - 失敗的步驟需有明確記錄並停止後續非必要的流程。

## 增加新 Test Case
當使用者提出新 Test Case 時，請：
1. 分析 Test Case 需要操作哪些頁面與 UI 元件。
2. 檢查 `accessibility_ids.py` 中是否有對應的 ID。
3. 如果該元件缺失，應提示缺少的 Accessibility ID，或使用替代定位方式，同時把情況記錄下來。
4. 撰寫或更新對應的 `execution/*.py` 腳本。
