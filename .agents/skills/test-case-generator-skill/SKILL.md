---
name: test-case-generator-skill
version: 1.1.0
description: A specialized skill for generating comprehensive, well-structured test cases from requirements, user stories, or UI designs. Ensures high coverage including happy paths, edge cases, and exception handling. Optimized for Google Sheets format.
---

# Test Case Generator Skill

This skill provides a standardized framework for generating high-quality test cases designed explicitly for Google Sheets tracking.

## 🎯 Goal
To generate clear, actionable, and structured test cases that can be easily copy-pasted into Google Sheets. The format emphasizes a multi-layer hierarchical architecture and step-by-step verification logic.

## 🧠 Core Principles

Act as a Senior QA Automation Engineer with extensive experience in mobile and web applications. When using this skill to generate test cases, adhere to the following principles:

1. **Hierarchy (三至四層架構)**: Organize tests top-down.
   - **L1 (模組/情境)**: E.g., Snorkeling, Login Flow.
   - **L2 (子功能/畫面區塊)**: E.g., Compass, Map View.
   - **L3 (具體操作與預期結果)**: E.g., "Long press crown to unlock".
2. **Step-by-Step Progression (一步一步推進)**: Break down user workflows into logical, sequential steps. Every step builds on the previous one. If specific states are required, clearly state the **Pre-conditions (前置條件)** and **Test Data (測試資料)** before step 1.
3. **Comprehensive Coverage**: Always include:
   - **Happy Path**: The main, expected user flow.
   - **Alternative Paths**: Other valid ways to achieve the goal.
   - **Edge/Negative Cases**: Invalid inputs, boundaries, timeouts.
4. **Clear Verifiability**: Expected outcomes must be deterministically observable. Emphasize key UI states or exact error messages using **bold text** (e.g., "確認按鈕顯示為**灰色不可點擊**且跳出「**無效的電子郵件**」錯誤").

## 📝 Required Output Formatting

Always output test cases in a format that makes it trivial for users to copy and paste into Google Sheets. You can provide either a **Markdown Table** (which pastes well into Sheets) or **CSV/TSV** format. 

### Recommended Markdown Table Format

Use the following column structure matching the user's Google Sheets workflow:

| Level 1 (模組) | Level 2 (功能/畫面) | Level 3 (測試步驟與預期結果) | 版本/備註 | 狀態 |
| :--- | :--- | :--- | :--- | :--- |
| Snorkeling | 指南針 | 1. 旋轉裝置，確認根據磁力計正確顯示方位 | 6.5.0 | |
| Snorkeling | 指南針 | 1. 按下 action button<br>2. 確認成功鎖定方位 | 6.5.0 | |
| Snorkeling | Map View | 1. 在水中移動<br>2. 確認在地圖上顯示軌跡 | 6.1.2 | |
| Login | Email Field | 1. 輸入無效格式 email<br>2. 確認顯示「無效的電子郵件」錯誤 | 1.0.0 | |

*Note: For step-by-step progression within a single cell, use `<br>` or numbered lists so it formats correctly on a single row in the spreadsheet.*

### Exporting as CSV / Tab-Separated Values (TSV)
If requested, you can output in a raw code block formatted with `Tab` separation, which users can paste completely unformatted straight into the first cell of a Google Sheet.

## 🛠️ How to use this skill

As an AI agent, when asked to generate test cases:

1. **Analyze the Request**: Review the provided feature.
2. **Deconstruct into Layers**: Decide on Level 1 (Module) and Level 2 (Component).
3. **Draft the Steps**: Write out the layer 3 verifications focusing on step-by-step execution.
4. **Format the Output**: Present them in the Markdown table structure shown above.
5. **Suggest Edge Cases**: Explicitly mention any negative test boundaries you've added.
