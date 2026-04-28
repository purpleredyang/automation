# 離線優先同步流程 - iOS 開發指南

本文檔為 iOS 開發者提供完整的離線優先同步實作指南。讓使用者能夠無縫地離線操作潛水記錄，並在恢復網路連線時自動同步資料。

## 📋 實作步驟總覽

### 第一步：設定資料模型
1. 建立與 API 對應的 Swift 資料模型
2. 定義所有必要的 enum 類型
3. 實作本地同步狀態追蹤

### 第二步：實作 API 服務層
1. 建立 APIService 處理網路請求
2. 實作認證和錯誤處理
3. 支援同步相關的 API 端點

### 第三步：建立同步引擎
1. 實作兩階段同步流程（Push → Pull）
2. 處理衝突檢測與解決
3. 管理同步狀態和時間戳

### 第四步：實作離線優先邏輯
1. 建立本地資料庫接口
2. 實作網路狀態監控
3. 設定自動同步觸發機制

## 🔄 同步流程說明

### 核心概念
- **兩階段同步**: 先推送本地變更，再拉取遠端變更
- **軟刪除**: 使用 `deletedAt` 時間戳標記刪除，不實際刪除資料
- **衝突檢測**: 使用 `updatedAt` 時間戳防止資料衝突
- **游標分頁**: 使用游標分批獲取大量資料

### API 端點
- **建立記錄**: `POST /v1/sync/posts`
- **更新/刪除記錄**: `PATCH /v1/sync/posts/:id`
- **獲取變更**: `GET /v1/sync/posts?updatedAfter=&cursor=&limit=`

### 同步流程
1. **推送階段**: 將本地的新建、修改、刪除記錄推送到伺服器
2. **拉取階段**: 從伺服器獲取其他裝置的變更
3. **衝突處理**: 處理同一記錄的並行修改
4. **狀態更新**: 更新本地同步時間戳和記錄狀態

## 🛠 離線優先最佳實踐

### 資料管理
- 維護本地同步狀態 (`updatedAt`, `deletedAt`)
- 實作本地資料庫的 CRUD 操作
- 支援離線時的資料修改

### 網路處理
- 監控網路狀態變化
- 在恢復連線時自動同步
- 實作重試機制和錯誤處理

### 使用者體驗
- 提供同步進度指示
- 顯示離線狀態提示
- 處理衝突時的使用者選擇

---

# 📝 Swift 實作範例

以下提供完整的 Swift 程式碼範例，展示如何實作離線優先的同步功能。

## 1. 資料模型定義

```swift
import Foundation

// MARK: - 主要的潛水記錄模型
// 與 API 的 PostDto 對應，包含所有潛水記錄的必要資訊
struct DivingPost: Codable, Identifiable {
    let id: String
    
    let startAt: Date
    let endAt: Date
    let createdAt: Date
    var updatedAt: Date
    var deletedAt: Date?
    
    let postType: DiveType
    let maxDepth: Double
    let maxDepthUnit: DepthUnit
    
    var title: String?
    var note: String?
    var rating: Double?
    var waterTemperature: Double?
    var waterTemperatureUnit: TemperatureUnit?
    var maxRisingSpeedPerMin: Double?
    var maxRisingSpeedPerMinUnit: DepthUnit?
    var safetyStop: SafetyStopState?
    var noDecompressionStop: SafetyStopState?
    
    var cylinders: [DivingCylinder]
    var photos: [PostPhoto]
    var merchantPhotos: [PostPhoto]
    
    var divingShop: PostShop?
    var divingSpot: PostDivingSpot?
    var journey: DivingJourney?
    var provider: PostProvider?
    var partners: DivingPartner?
    
    var maxApneaDurationBySec: Double?
    var underwaterDurationBySec: Double?
    var diveCount: Double?
    var expense: Double?
    
    var apneaTest: ApneaTest?
    var apneaTraining: ApneaTraining?
    
    let isDefaultSample: Bool
    var hideFromRecommend: Bool?
    var weights: [Double]
    var weightsUnit: WeightUnit?
    
    var createdLocation: Location?
}

// MARK: - 巢狀結構
struct DivingCylinder: Codable {
    let oxygenPercentage: Double
    let pressureUnit: PressureUnit
    let fromPressure: Double
    let toPressure: Double
}

struct PostPhoto: Codable {
    let url: String
    let provider: String?
}

struct Location: Codable {
    let latitude: Double
    let longitude: Double
}

struct PostShop: Codable {
    let shopId: String
    var comment: String?
    var rating: Double?
    var shopName: String?
    var location: Location?
    var photos: [PostPhoto]
}

struct PostDivingSpot: Codable {
    let spotId: String
    var comment: String?
    var rating: Double?
    var spotName: String?
    var location: Location?
}

struct DivingJourney: Codable {
    let depthUnit: DepthUnit
    let temperatureUnit: TemperatureUnit?
    let points: [DivingJourneyPoint]
}

struct DivingJourneyPoint: Codable {
    let depth: Double
    let diveTime: Double
    let temperature: Double?
    let heartRate: Double?
}

struct PostProvider: Codable {
    let logId: String?
    let source: String?
    let sourceId: String?
    let sourceName: String?
    let version: String?
}

struct DivingPartner: Codable {
    let onlineUsers: [String]
}

struct ApneaTest: Codable {
    let breathingDuration: Double
    let holdDuration: Double
}

struct ApneaTraining: Codable {
    let templateId: String
    let templateName: String
    let completedDuration: Double
    let steps: [ApneaTrainingStep]
}

struct ApneaTrainingStep: Codable {
    let breathingDuration: Double
    let holdDuration: Double
}

// MARK: - Prisma Enums
enum DiveType: String, Codable, CaseIterable {
    case scubaDiving = "scubaDiving"
    case freeDiving = "freeDiving"
    case snorkeling = "snorkeling"
    case apneaTest = "apneaTest"
    case apneaTraining = "apneaTraining"
    case purePost = "purePost"
}

enum DepthUnit: String, Codable, CaseIterable {
    case meter = "meter"
    case feet = "feet"
}

enum TemperatureUnit: String, Codable, CaseIterable {
    case celsius = "celsius"
    case fahrenheit = "fahrenheit"
}

enum WeightUnit: String, Codable, CaseIterable {
    case kilogram = "kilogram"
    case pound = "pound"
}

enum PressureUnit: String, Codable, CaseIterable {
    case bar = "bar"
    case psi = "psi"
}

enum SafetyStopState: String, Codable, CaseIterable {
    case done = "done"
    case missed = "missed"
    case notRequired = "notRequired"
}

enum AuthProvider: String, Codable, CaseIterable {
    case anonymous = "anonymous"
    case google = "google"
    case weixin = "weixin"
    case apple = "apple"
}

enum PlaceType: String, Codable, CaseIterable {
    case divingShop = "divingShop"
    case divingSpot = "divingSpot"
}

enum MediaType: String, Codable, CaseIterable {
    case divingLog = "divingLog"
    case privatePartnerAvatar = "privatePartnerAvatar"
    case myAvatar = "myAvatar"
    case myBackground = "myBackground"
    case aiAvatar = "aiAvatar"
    case place = "place"
}

// MARK: - API 負載結構

// 用於 PATCH 請求。除了 `updatedAt` 以外，所有屬性都是可選的。
struct PatchPayload: Codable {
    var title: String?
    var note: String?
    var rating: Double?
    var deletedAt: Date?
    var waterTemperature: Double?
    var waterTemperatureUnit: TemperatureUnit?
    // ... 包含所有其他可變更欄位作為可選項 ...
    
    // updatedAt 是衝突檢查所需的
    let updatedAt: Date
}

// PATCH 回應結構，包含衝突處理
struct PatchPostResponse: Codable {
    let post: DivingPost
    let success: Bool
    let conflictMessage: String?
}
```

## 2. API 服務層

```swift
import Foundation

// 負責處理所有網路請求的服務類別
actor APIService {
    private let baseURL = URL(string: "https://api.yourdomain.com/v1")!
    private let session = URLSession.shared
    private let decoder = JSONDecoder()
    private let encoder = JSONEncoder()
    private var authToken: String?
    
    init() {
        // 設定日期格式，與伺服器保持一致
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZ"
        formatter.timeZone = TimeZone(abbreviation: "UTC")
        
        decoder.dateDecodingStrategy = .formatted(formatter)
        encoder.dateEncodingStrategy = .formatted(formatter)
    }
    
    func setAuthToken(_ token: String) {
        self.authToken = token
    }
    
    private func makeAuthenticatedRequest(url: URL, method: String = "GET", body: Data? = nil) -> URLRequest {
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let body = body {
            request.httpBody = body
        }
        
        return request
    }

    // PUSH: 建立新記錄
    func createPost(payload: DivingPost) async throws -> DivingPost {
        let url = baseURL.appendingPathComponent("sync/posts")
        let body = try encoder.encode(payload)
        let request = makeAuthenticatedRequest(url: url, method: "POST", body: body)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw SyncError.networkError(URLError(.badServerResponse))
        }
        
        if httpResponse.statusCode >= 400 {
            throw SyncError.httpError(httpResponse.statusCode)
        }
        
        return try decoder.decode(DivingPost.self, from: data)
    }

    // PUSH: 更新 / 軟刪除 (自動處理衝突)
    func patchPost(id: String, payload: PatchPayload) async throws -> PatchPostResponse {
        let url = baseURL.appendingPathComponent("sync/posts/\(id)")
        let body = try encoder.encode(payload)
        let request = makeAuthenticatedRequest(url: url, method: "PATCH", body: body)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw SyncError.networkError(URLError(.badServerResponse))
        }
        
        if httpResponse.statusCode >= 400 {
            throw SyncError.httpError(httpResponse.statusCode)
        }
        
        return try decoder.decode(PatchPostResponse.self, from: data)
    }

    // PULL: 從伺服器獲取變更
    func fetchPosts(updatedAfter: Date?, cursor: String?, limit: Int = 100) async throws -> SyncGetResponse {
        var urlComponents = URLComponents(url: baseURL.appendingPathComponent("sync/posts"), resolvingAgainstBaseURL: false)!
        
        var queryItems: [URLQueryItem] = []
        
        if let updatedAfter = updatedAfter {
            let formatter = ISO8601DateFormatter()
            formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            queryItems.append(URLQueryItem(name: "updatedAfter", value: formatter.string(from: updatedAfter)))
        }
        
        if let cursor = cursor {
            queryItems.append(URLQueryItem(name: "cursor", value: cursor))
        }
        
        queryItems.append(URLQueryItem(name: "limit", value: String(limit)))
        urlComponents.queryItems = queryItems
        
        guard let url = urlComponents.url else {
            throw SyncError.invalidURL
        }
        
        let request = makeAuthenticatedRequest(url: url)
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw SyncError.networkError(URLError(.badServerResponse))
        }
        
        if httpResponse.statusCode >= 400 {
            throw SyncError.httpError(httpResponse.statusCode)
        }
        
        return try decoder.decode(SyncGetResponse.self, from: data)
    }
}

struct SyncGetResponse: Codable {
    let posts: [DivingPost]
    let nextCursor: String?
}

enum SyncError: Error {
    case networkError(Error)
    case httpError(Int)
    case invalidURL
    case unauthorized
}
```

## 3. 同步引擎

```swift
// 核心同步邏輯，負責協調本地與遠端資料
actor SyncEngine {
    private let apiService = APIService()
    private let localDatabase: LocalDatabase // 您的本地儲存包裝器
    private let userDefaults = UserDefaults.standard
    
    private let lastSyncKey = "lastSyncTimestamp"
    
    init(database: LocalDatabase) {
        self.localDatabase = database
    }
    
    // 主要同步方法
    func sync() async throws {
        do {
            try await push()
            try await pull()
            updateLastSyncTimestamp()
        } catch {
            print("同步失敗: \(error)")
            throw error
        }
    }
    
    // 階段 1: 推送本地變更
    private func push() async throws {
        // 獲取需要建立的記錄
        let postsToCreate = await localDatabase.getPostsWithSyncStatus(.needsCreation)
        for post in postsToCreate {
            do {
                let createdPost = try await apiService.createPost(payload: post)
                await localDatabase.updatePost(createdPost, syncStatus: .synced)
            } catch SyncError.httpError(let code) where code >= 400 {
                // 處理建立錯誤
                print("建立記錄失敗: \(code)")
                continue
            }
        }
        
        // 獲取需要更新的記錄
        let postsToUpdate = await localDatabase.getPostsWithSyncStatus(.needsUpdate)
        for post in postsToUpdate {
            do {
                let patchPayload = createPatchPayload(from: post)
                let response = try await apiService.patchPost(id: post.id, payload: patchPayload)
                
                if response.success {
                    // 更新成功，使用返回的資料
                    await localDatabase.updatePost(response.post, syncStatus: .synced)
                } else {
                    // 發生衝突，伺服器已返回最新版本
                    print("衝突檢測到記錄 ID: \(post.id) - \(response.conflictMessage ?? "")")
                    await localDatabase.updatePost(response.post, syncStatus: .synced)
                }
            } catch SyncError.httpError(let code) where code >= 400 {
                print("更新記錄失敗: \(code)")
                continue
            }
        }
    }
    
    // 階段 2: 拉取遠端變更
    private func pull() async throws {
        let lastSync = getLastSyncTimestamp()
        var cursor: String? = nil
        var hasMore = true
        
        while hasMore {
            let response = try await apiService.fetchPosts(
                updatedAfter: lastSync,
                cursor: cursor,
                limit: 100
            )
            
            // 處理接收到的記錄
            for post in response.posts {
                if post.deletedAt != nil {
                    // 軟刪除的記錄 - 從本地刪除
                    await localDatabase.deletePost(id: post.id)
                } else {
                    // upsert 記錄到本地資料庫
                    await localDatabase.upsertPost(post, syncStatus: .synced)
                }
            }
            
            cursor = response.nextCursor
            hasMore = cursor != nil
        }
    }
    
    // 建立 PATCH 負載
    private func createPatchPayload(from post: DivingPost) -> PatchPayload {
        return PatchPayload(
            title: post.title,
            note: post.note,
            rating: post.rating,
            deletedAt: post.deletedAt,
            waterTemperature: post.waterTemperature,
            waterTemperatureUnit: post.waterTemperatureUnit,
            updatedAt: post.updatedAt
        )
    }
    
    // 時間戳管理
    private func getLastSyncTimestamp() -> Date? {
        guard let timestamp = userDefaults.object(forKey: lastSyncKey) as? Date else {
            return nil
        }
        return timestamp
    }
    
    private func updateLastSyncTimestamp() {
        userDefaults.set(Date(), forKey: lastSyncKey)
    }
}

// 本地資料庫介面
protocol LocalDatabase {
    func getPostsWithSyncStatus(_ status: SyncStatus) async -> [DivingPost]
    func updatePost(_ post: DivingPost, syncStatus: SyncStatus) async
    func upsertPost(_ post: DivingPost, syncStatus: SyncStatus) async
    func deletePost(id: String) async
}
```

## 4. 應用程式整合範例

```swift
// 主要的資料管理類別，整合所有同步功能
class DivingDataManager: ObservableObject {
    private let syncEngine: SyncEngine
    private let apiService: APIService
    
    init() {
        let database = CoreDataLocalDatabase() // 您的 Core Data 實作
        self.syncEngine = SyncEngine(database: database)
        self.apiService = APIService()
    }
    
    // 定期同步
    func performPeriodicSync() async {
        do {
            try await syncEngine.sync()
            print("同步完成")
        } catch {
            print("同步錯誤: \(error)")
        }
    }
    
    // 離線建立新記錄
    func createOfflinePost(_ post: DivingPost) async {
        var newPost = post
        newPost.updatedAt = Date()
        
        // 儲存到本地資料庫
        await localDatabase.savePost(newPost)
        
        // 如果有網路連線，立即嘗試同步
        if NetworkMonitor.shared.isConnected {
            await performPeriodicSync()
        }
    }
    
    // 離線更新記錄
    func updateOfflinePost(_ post: DivingPost) async {
        var updatedPost = post
        updatedPost.updatedAt = Date()
        
        await localDatabase.updatePost(updatedPost)
        
        if NetworkMonitor.shared.isConnected {
            await performPeriodicSync()
        }
    }
    
    // 軟刪除記錄
    func deletePost(_ post: DivingPost) async {
        var deletedPost = post
        deletedPost.deletedAt = Date()
        deletedPost.updatedAt = Date()
        
        await localDatabase.updatePost(deletedPost)
        
        if NetworkMonitor.shared.isConnected {
            await performPeriodicSync()
        }
    }
}
```

## 5. 工具類別與最佳實踐

### 網路狀態監控

```swift
import Network

// 監控網路連線狀態，自動觸發同步
class NetworkMonitor: ObservableObject {
    static let shared = NetworkMonitor()
    
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")
    
    @Published var isConnected = false
    
    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
            }
        }
        monitor.start(queue: queue)
    }
}
```

### Enum 使用範例與工具函數

```swift
// 範例：建立新的潛水記錄
func createNewDiveLog() -> DivingPost {
    let newPost = DivingPost(
        id: UUID().uuidString,
        startAt: Date(),
        endAt: Date().addingTimeInterval(2700), // 45 分鐘後
        createdAt: Date(),
        updatedAt: Date(),
        deletedAt: nil,
        postType: .scubaDiving, // 使用 enum 值
        maxDepth: 18.5,
        maxDepthUnit: .meter, // 使用 enum 值
        title: "美麗的珊瑚礁潛水",
        note: "能見度很好，看到許多熱帶魚",
        rating: 4.5,
        waterTemperature: 26.0,
        waterTemperatureUnit: .celsius, // 使用 enum 值
        maxRisingSpeedPerMin: nil,
        maxRisingSpeedPerMinUnit: nil,
        safetyStop: .done, // 使用 enum 值
        noDecompressionStop: .notRequired, // 使用 enum 值
        cylinders: [
            DivingCylinder(
                oxygenPercentage: 21.0,
                pressureUnit: .bar, // 使用 enum 值
                fromPressure: 200.0,
                toPressure: 50.0
            )
        ],
        photos: [],
        merchantPhotos: [],
        divingShop: nil,
        divingSpot: nil,
        journey: nil,
        provider: nil,
        partners: nil,
        maxApneaDurationBySec: nil,
        underwaterDurationBySec: 2700,
        diveCount: 1,
        expense: 1500.0,
        apneaTest: nil,
        apneaTraining: nil,
        isDefaultSample: false,
        hideFromRecommend: false,
        weights: [2.5, 1.0],
        weightsUnit: .kilogram, // 使用 enum 值
        createdLocation: nil
    )
    
    return newPost
}

// 範例：根據使用者設定顯示單位
extension DepthUnit {
    var displaySymbol: String {
        switch self {
        case .meter: return "m"
        case .feet: return "ft"
        }
    }
    
    var localizedName: String {
        switch self {
        case .meter: return NSLocalizedString("公尺", comment: "")
        case .feet: return NSLocalizedString("英尺", comment: "")
        }
    }
}

extension TemperatureUnit {
    var displaySymbol: String {
        switch self {
        case .celsius: return "°C"
        case .fahrenheit: return "°F"
        }
    }
}

// 範例：轉換單位
extension Double {
    func convertDepth(from source: DepthUnit, to target: DepthUnit) -> Double {
        if source == target { return self }
        
        switch (source, target) {
        case (.meter, .feet):
            return self * 3.28084
        case (.feet, .meter):
            return self / 3.28084
        default:
            return self
        }
    }
    
    func convertTemperature(from source: TemperatureUnit, to target: TemperatureUnit) -> Double {
        if source == target { return self }
        
        switch (source, target) {
        case (.celsius, .fahrenheit):
            return (self * 9/5) + 32
        case (.fahrenheit, .celsius):
            return (self - 32) * 5/9
        default:
            return self
        }
    }
}
```

---

## 📚 重要提醒

### 實作要點
1. **類型安全**: 使用 enum 而非字串，避免拼寫錯誤
2. **錯誤處理**: 實作完善的錯誤處理和重試機制
3. **使用者體驗**: 提供清晰的同步狀態指示
4. **資料一致性**: 定期驗證本地與遠端資料的一致性

### 效能優化
- 批次處理多個同步操作
- 使用適當的分頁大小
- 實作指數退避重試策略
- 監控網路狀態，智慧觸發同步

### 衝突解決策略
- **自動解決**: 伺服器在檢測到衝突時直接返回最新版本，客戶端無需額外處理
- **時間戳比較**: 使用 `updatedAt` 決定是否有衝突
- **優雅處理**: 衝突不再是錯誤，而是正常的回應狀態

### 範例：處理 PATCH 回應
```swift
// 處理 PATCH 操作的回應
func handlePatchResponse(_ response: PatchPostResponse, for postId: String) async {
    if response.success {
        print("✅ 記錄 \(postId) 更新成功")
        // 使用更新後的資料
        await localDatabase.updatePost(response.post, syncStatus: .synced)
    } else {
        print("⚠️ 檢測到衝突: \(response.conflictMessage ?? "")")
        print("📥 使用伺服器最新版本覆蓋本地資料")
        // 直接使用伺服器返回的最新版本
        await localDatabase.updatePost(response.post, syncStatus: .synced)
        
        // 可選：通知使用者
        DispatchQueue.main.async {
            NotificationCenter.default.post(
                name: .dataConflictResolved,
                object: nil,
                userInfo: ["postId": postId, "message": response.conflictMessage]
            )
        }
    }
}
```

此實作提供完整的離線優先同步功能，確保使用者在任何網路環境下都能順暢使用應用程式。新的衝突處理機制讓整體體驗更加流暢和使用者友善。