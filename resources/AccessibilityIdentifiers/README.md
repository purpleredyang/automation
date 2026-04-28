# Accessibility Identifiers 使用指南

## 概述

本專案採用 Page Object Pattern 集中管理所有 UI 元件的 accessibility identifiers，方便 QA 進行 UI 自動化測試。

## 檔案結構

```
AccessibilityIdentifiers/
├── LoginAccessibilityID.swift       - Login 模組
├── TabAccessibilityID.swift         - Tab 和 Add 模組
├── AddAccessibilityID.swift         - 新增相關（ModifyLog, Apnea, ImportLogs, ColorEnhance）
├── MineAccessibilityID.swift        - 個人頁面模組
├── ExploreAccessibilityID.swift     - 探索模組
├── NewsAccessibilityID.swift        - 動態模組
├── SettingsAccessibilityID.swift    - 設定模組
├── OthersAccessibilityID.swift      - 其他（Posts, Report, ImageUpload）
└── UIComponentsAccessibilityID.swift - UIComponents 共用元件
```

## 命名規範

所有 accessibility identifier 遵循統一格式：

```
"{ClassName}.{componentName}"
```

### 範例

```swift
// ViewController
"LoginViewController.appleSignButton"
"SettingsViewController.unitView"

// View
"PostCellTitleRowView.titleLabel"
"AddRowView.imageView"

// Cell
"PostTableViewCell.likeButton"
```

## 使用方式

### 1. 查找對應的 ID 定義

根據你的 ViewController 或 View 所在模組，打開對應的 AccessibilityID 檔案。

例如：
- Login 相關 → `LoginAccessibilityID.swift`
- Settings 相關 → `SettingsAccessibilityID.swift`
- Modify Log 相關 → `AddAccessibilityID.swift`

### 2. 在元件中使用

```swift
// 在 ViewController 中
private lazy var appleSignButton: UIButton = {
    let button = UIButton()
    button.accessibilityIdentifier = LoginAccessibilityID.LoginViewController.appleSignButton
    // ... 其他配置
    return button
}()
```

### 3. 如果需要新增 ID

1. 在對應的 AccessibilityID 檔案中添加新的 static let：

```swift
struct SettingsAccessibilityID {
    struct NewViewController {
        static let newButton = "NewViewController.newButton"
        static let newLabel = "NewViewController.newLabel"
    }
}
```

2. 在 ViewController/View 中使用：

```swift
button.accessibilityIdentifier = SettingsAccessibilityID.NewViewController.newButton
```

## 已完成的模組

### ✅ 完全實作
- **Login 模組**
  - LoginViewController
  - LoginPreviewSubView
  - LoginLegalView

- **Tab 模組**
  - TabBarController
  - TabBarAddItem
  - TabBarDefaultItem

- **News 模組**
  - NewsViewController
  - NotificationsViewController
  - NotificationsNaviItem
  - NotificationBaseTableViewCell / NotificationGeneralTableViewCell
  - PostTableViewCell
  - PostCellTitleRowView / PostCellProfileView / PostCellCollectionView
  - PostCellPlacesView / PostCellLikeView / PostCellTimeView
  - NewsFollowingTableViewCell / FollowingUserCollectionViewCell
  - UserSuggestionsTableViewCell
  - ProfilesSheetViewController

- **Explore 模組**
  - ExploreViewController / ExploreList / PlaceDetail
  - CreatePlaceViewController
  - PlaceAllCommentsViewController / PlacePhotoListViewController
  - NewExplore（BookingExplore / BookingAllDestination / ExploreCountry / ExploreDiversMedia）

- **Mine 模組**
  - MineViewController
  - MyProfile / EditMyProfile / ExportLogs
  - Followers / ManageLogs / Statistics / Calendar / Map
  - PublicUser / RangePosts / RelateLogs

- **Settings 模組**
  - SettingsViewController
  - Subscription / InviteFriend / Permissions / Privacy
  - UnitSetting / InitDivingCount / MapType
  - WatchIntro / PartnerList / DebugInfos
  
- **Add 模組**
  - ModifyLog（Section 1/2/3、Detail、Photos）
  - ModifyPurePost
  - ImportLogs（ATMOS、Shearwater、Subsurface、UDDF、Divelogs、DiverLogPlus、Crest、Unified）
  - ApneaTraining / ApneaTest / PreApneaTest / ApneaResult
  - ColorEnhance（Photo/Video 參數與輸出設定）

- **Others 模組**
  - BasePostDetail / PostDetail（Main Context / Floating / Actions）
  - Freediving / Apnea 圖表
  - SharePost / Report / ImageUpload / PostImageEditRequest

- **UIComponents**
  - Control / Reusable Cells & Views
  - JTAppleCalendar / Photo & Lightbox / Misc Views

### 🔄 進行中
- 目前無

### 🔄 待完成
- 目前無

所有的 AccessibilityID 定義已經準備好，只需要在對應的元件中添加一行：

```swift
component.accessibilityIdentifier = ModuleAccessibilityID.ClassName.componentName
```

## QA 測試使用

### XCUITest 範例

```swift
// 定位元件
let loginButton = app.buttons["LoginViewController.appleSignButton"]
loginButton.tap()

// 驗證元件存在
XCTAssertTrue(app.buttons["SettingsViewController.unitView"].exists)

// 檢查 Label 內容
let titleLabel = app.staticTexts["PostCellTitleRowView.titleLabel"]
XCTAssertEqual(titleLabel.label, "Expected Title")
```

### Appium 範例

```python
# 定位元件
apple_sign_button = driver.find_element_by_accessibility_id("LoginViewController.appleSignButton")
apple_sign_button.click()
```

## 注意事項

1. **型別安全**：使用靜態常數可以在編譯時檢查拼寫錯誤
2. **避免硬編碼**：永遠不要直接寫字串，使用定義好的常數
3. **命名一致性**：嚴格遵循 `{ClassName}.{componentName}` 格式
4. **更新同步**：修改元件名稱時，記得同時更新 AccessibilityID 定義

## 統計資訊

- **AccessibilityID 檔案**：9 個（含 UIComponents）

## 後續工作

繼續為剩餘的 ViewController 和 View 添加 accessibility identifiers，參考已完成的檔案進行相同的處理。
