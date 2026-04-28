# Diver App 付費事件追蹤指南

> **目標受眾**：行銷團隊、數據分析團隊  
> **最後更新**：2026-03-25  
> **狀態**：✅ 已上線

## 概述

Diver App 已整合付費事件追蹤，現在會依產品類型分開送資料：

| 平台 | 用途 | 查看連結 |
|-----|------|---------|
| **Firebase Analytics** | 用戶行為分析 | [Firebase Console](https://console.firebase.google.com) |
| **Singular** | 歸因追蹤 | [Singular Dashboard](https://app.singular.net) |

---

## 事件對照

### Firebase
Firebase 維持單一事件名稱 `IAP_Purchase`，差異透過 `event_type` 與附加欄位區分。

| 參數名稱 | 說明 | 範例值 |
|---------|------|--------|
| `product_id` | Apple 產品識別碼 | `"scubaDiving.weekly"` |
| `transaction_id` | Apple 交易 ID | `"2000000123456789"` |
| `original_transaction_id` | 原始訂閱交易 ID | `"2000000123000000"` |
| `event_type` | 事件分類 | `"subscription_trial_started"` / `"subscription_started"` / `"subscription_renewed"` / `"non_subscription_purchase"` |
| `subscription_type` | 訂閱類型 | `"weekly"` / `"monthly"` / `"halfyear"` / `"annual"` |
| `trial_duration` | 試用期長度（僅試用時） | `"7_days"` / `"14_days"` 等 |
| `product_category` | 產品類別 | `"watch_scuba"`, `"watch_freediving"`, `"watch_snorkeling"`, `"mobile_plus"`, `"watch_lifetime"` |
| `billing_period` | 方案週期 | `"weekly"` / `"monthly"` / `"halfyear"` / `"annual"` |
| `revenue_amount` | 金額字串 | `"9.99"` |
| `currency` | ISO 4217 貨幣代碼 | `"USD"` |
| `userID` | 用戶 ID | 自動帶入 |
| `file` | 程式檔案路徑 | 自動帶入 |
| `line` | 程式行數 | 自動帶入 |

### Singular
Singular 不再把所有付費事件都送成同一個事件名稱，而是依官方建議拆成訂閱標準事件與 StoreKit 2 收入事件：

| 產品類型 | 觸發時機 | Singular 事件名稱 | 方法 |
|---------|----------|------------------|------|
| 訂閱 | 首購 | `sng_subscribe` | `customRevenue()` |
| 訂閱 | 試用開始 | `sng_start_trial` | `event()` |
| 訂閱 | 自動續訂 | `subscription_renewed` | `customRevenue()` |
| 非訂閱 | 一次性購買 | `IAP_Purchase` | StoreKit 2 `customRevenue(transactionJsonRepresentation:productJsonRepresentation:)` |

### event_type 對照說明
| event_type | 觸發時機 |
|-----------|----------|
| `subscription_trial_started` | StoreKit 判斷為 free trial |
| `subscription_started` | 新訂閱首購 |
| `subscription_renewed` | 同一組訂閱的續訂交易 |
| `non_subscription_purchase` | 非訂閱商品的一次性購買 |

> 重要：恢復購買不會再送新的營收事件。Restore 只會同步權限與狀態，不會新增訂閱營收。

---

## 產品類別說明 (product_category)

| 類別代碼 | 產品名稱 | 說明 |
|---------|---------|------|
| `mobile_plus` | Mobile Plus | App 進階功能（照片/影片增強等） |
| `watch_snorkeling` | Watch+ 浮潛 | Apple Watch 浮潛記錄功能 |
| `watch_freediving` | Watch+ 自由潛水 | Apple Watch 自由潛水功能 |
| `watch_scuba` | Watch+ 水肺潛水 | Apple Watch 水肺潛水功能 |
| `watch_lifetime` | Watch+ 終身版 | 一次性解鎖 Watch 付費功能 |

---

## 如何查看這些事件

### 在 Singular 查看
1. 前往 [Singular Dashboard](https://app.singular.net)
2. 進入事件或 attribution 相關報表
3. 針對訂閱查看 `sng_subscribe`、`sng_start_trial`、`subscription_renewed`
4. 針對非訂閱查看 `IAP_Purchase`
5. 檢查 `product_id`、`transaction_id`、`original_transaction_id`、`billing_period`、`product_category`

### 在 Firebase 查看
1. 前往 [Firebase Console](https://console.firebase.google.com)
2. 進入 Analytics 的 Events 或 DebugView
3. 以事件名稱 `IAP_Purchase` 篩選
4. 檢查對應參數與事件量

### 事件名稱
| 事件名稱 | 說明 |
|---------|------|
| `IAP_Purchase` | Firebase 的統一付費事件名稱 |
| `sng_subscribe` | Singular 的新訂閱事件 |
| `sng_start_trial` | Singular 的試用開始事件 |
| `subscription_renewed` | Singular 的續訂事件 |

---

## 應用場景範例

### 場景 1：追蹤試用轉換率
**目標**：了解有多少試用用戶轉為付費用戶

1. 在 Singular 或 Firebase 中以 `event_type = subscription_trial_started` 篩選 `IAP_Purchase`
2. 對比 `event_type = subscription_started` 與 `subscription_renewed`
3. 計算轉換率 = (付費事件數 / 試用事件數) × 100%

### 場景 2：優化廣告投放
**目標**：針對開始試用但未付費的用戶投放再行銷廣告

1. 匯出或串接 `event_type = subscription_trial_started` 的用戶集合
2. 排除 `event_type = subscription_started` 與 `subscription_renewed` 的用戶
3. 對這個受眾投放「試用期即將結束」的再行銷活動

### 場景 3：分析產品偏好
**目標**：了解哪個產品類別最受歡迎

在 Singular 或 Firebase 匯出資料中：
1. 在 Firebase 選擇 `IAP_Purchase`，或在 Singular 分別查看各事件
2. 依 `product_category` 參數分組
3. 比較 `mobile_plus`、`watch_scuba`、`watch_freediving`、`watch_lifetime` 的購買量
---

## 重要注意事項

- 不同平台的顯示延遲不同，通常會有幾分鐘到數小時的同步時間
- 如果剛完成測試，請耐心等待資料同步

- 建議使用 **Sandbox 環境**測試訂閱流程
- Sandbox 續訂速度很快，所以同一位測試者在短時間內看到多筆 `subscription_renewed` 是正常現象

- 所有事件都經過 Apple StoreKit 驗證
- 訂閱與非訂閱已分流到對應的 Singular SDK 方法
- 同一筆 `transaction_id` 在 app 內只會處理一次，避免 purchase flow 與 `Transaction.updates` 雙重送單
- Restore 不會送新的營收事件
- 自動續訂仍然會產生新的續訂事件，這是正常的營收事件

---

## 技術團隊參考資訊

<details>
<summary>點擊展開技術實作細節</summary>

### 實作位置
事件追蹤入口在 `IAPRepository.swift` 的 `listenForTransactions()`，核心規劃與送單邏輯在 `IAPRepository+EventLogging.swift` 與 `IAPAnalyticsTracking.swift`。

### 事件流程
1. 用戶完成購買 → StoreKit 交易完成
2. `purchase()` 與 `Transaction.updates` 會共用同一個 transaction-level 處理任務
3. 先做 backend 驗證
4. 依產品類型產生 Singular / Firebase 事件計畫
5. Singular 依事件類型選用 `event()`、`customRevenue()` 或 StoreKit 2 `customRevenue(...)`
6. Firebase 統一記錄 `IAP_Purchase`
7. 交易 `finish()` 後更新訂閱狀態

### 覆蓋範圍
✅ App 內直接購買  
✅ 自動續訂  
✅ 非訂閱商品  
✅ 恢復購買權限同步  
✅ 跨設備同步

### Restore 行為
- `AppStore.sync()` 後仍會將 entitlement 同步回 backend
- Restore 期間不會送新的收入事件到 Singular 或 Firebase

</details>

---

## 📋 完整產品 ID 對照表

### Mobile Plus 產品
| 產品名稱 | Product ID | 對應 product_category |
|---------|-----------|---------------------|
| Mobile Plus 月訂閱 | `mobile.plus.month` | `mobile_plus` |
| Mobile Plus 年訂閱 | `mobile.plus.year` | `mobile_plus` |

### Watch+ 浮潛 (Snorkeling)
| 產品名稱 | Product ID | 對應 product_category |
|---------|-----------|---------------------|
| 浮潛月訂閱 | `snorkeling.month` | `watch_snorkeling` |
| 浮潛年訂閱 | `snorkeling.year` | `watch_snorkeling` |

### Watch+ 自由潛水 (Free Diving)
| 產品名稱 | Product ID | 對應 product_category |
|---------|-----------|---------------------|
| 自由潛水 7天試用 | `freediving.weekly` | `watch_freediving` |
| 自由潛水月訂閱 | `freediving.monthly` | `watch_freediving` |
| 自由潛水半年訂閱 | `freediving.halfyear` | `watch_freediving` |
| 自由潛水年訂閱 | `freediving.yearly` | `watch_freediving` |

### Watch+ 水肺潛水 (Scuba Diving)
| 產品名稱 | Product ID | 對應 product_category |
|---------|-----------|---------------------|
| 水肺潛水 7天試用 | `scubaDiving.weekly` | `watch_scuba` |
| 水肺潛水月訂閱 | `scubaDiving.monthly` | `watch_scuba` |
| 水肺潛水半年訂閱 | `scubaDiving.halfyear` | `watch_scuba` |
| 水肺潛水年訂閱 | `scubaDiving.yearly` | `watch_scuba` |

### Watch+ 終身購買 (Lifetime)
| 產品名稱 | Product ID | 對應 product_category |
|---------|-----------|---------------------|
| Apple Watch Plus 終身 | `apple.watch.plus` | `watch_lifetime` |

> 注意：終身購買會解鎖所有 Watch+ 功能（浮潛、自由潛水、水肺潛水），追蹤類別為 `watch_lifetime`

---

## 📞 聯絡資訊

如有任何問題或需要額外的事件追蹤，請聯繫：
- **技術團隊**：[新增聯絡方式]
- **數據分析團隊**：[新增聯絡方式]
