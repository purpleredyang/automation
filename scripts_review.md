# 自動化腳本總覽與提取

您目前在工作空間中編寫了以下 9 個主要的 Python 腳本，主要用於 iOS App 的自動化測試與開發。

---

## 腳本詳細內容

### 1. api_client.py
**路徑**: `execution/api_client.py`
**用途**: API 測試客戶端，支援登入與生成模擬潛水紀錄。

```python
import requests
import uuid
import datetime
from datetime import timedelta

class DiverOutAPIClient:
    def __init__(self, base_url="https://api-dev.diverout.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def login_with_cookie(self, session_id_cookie, cdn_cookie):
        self.session.cookies.set('sessionId', session_id_cookie)
        self.session.cookies.set('Cloud-CDN-Cookie', cdn_cookie)
        self.session.headers.update({
            "User-Agent": "DiverOut-Automated-QA-Client",
            "Content-Type": "application/json"
        })
        print("Cookies 設置完成，API Client 初始化完畢！")

    def test_authentication(self, endpoint_path="/v4/auth/me"):
        url = f"{self.base_url}{endpoint_path}"
        try:
            response = self.session.get(url)
            print(f"Auth Test -> GET {url}")
            print(f"Status Code: {response.status_code}")
            return response.status_code
        except Exception as e:
            print(f"請求失敗: {e}")
            return None

    def create_mock_dive_logs(self, count=50, post_type="scuba"):
        url = f"{self.base_url}/v1/sync/posts"
        success_count = 0
        now = datetime.datetime.utcnow()
        for i in range(count):
            start_time = now - timedelta(days=i, hours=2)
            end_time = start_time + timedelta(minutes=45)
            iso_start = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            iso_end = end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            iso_created = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            payload = {
                "id": str(uuid.uuid4()).upper(),
                "startAt": iso_start,
                "endAt": iso_end,
                "createdAt": iso_created,
                "postType": post_type,
                "maxDepth": 25.5,
                "maxDepthUnit": "m",
                "waterTemperature": 26.5,
                "waterTemperatureUnit": "C",
                "cylinders": [],
                "mediaUrls": [],
                "isDefaultSample": False,
                "weights": [2.0],
                "weightsUnit": "kg",
                "note": f"QA Automation Test Log {i+1}"
            }
            resp = self.session.post(url, json=payload)
            if resp.status_code in [200, 201]:
                success_count += 1
        print(f"已成功發布了 {success_count} / {count} 筆假潛水紀錄！")

if __name__ == "__main__":
    client = DiverOutAPIClient()
    SESSION_ID = os.getenv("SESSION_ID")
    CDN_COOKIE = os.getenv("CDN_COOKIE")
    client.login_with_cookie(SESSION_ID, CDN_COOKIE)
    client.test_authentication()
```

---

### 2. test_pure_post_pua.py
**路徑**: `execution/test_pure_post_pua.py`
**用途**: 優化過的「發布文章」自動化測試（使用 P8 戰術協議）。

```python
import pytest
import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import accessibility_ids as ids

class TestPurePostPUA:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30)

    def _take_screenshot(self, step_name):
        os.makedirs(".tmp/pua_test", exist_ok=True)
        path = os.path.join(".tmp/pua_test", f"{step_name}.png")
        self.driver.save_screenshot(path)

    def _safe_click(self, locator, by=AppiumBy.ACCESSIBILITY_ID, timeout=15):
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, locator)))
            element.click()
            return True
        except: return False

    def test_pure_post_mission_completed(self):
        # Step 1: 入口
        self._safe_click(ids.TabBarController.addTab)
        self._safe_click(ids.AddViewController.purePostView)

        # Step 2: 照片選取入口
        self._safe_click(ids.ModifyLogPhotoAddCollectionViewCell.dashedAddView)
        for lbl in ["潛點", "Dive Point", "潛"]:
            if self._safe_click(lbl, timeout=5): break
        
        # Step 3: PHPicker 選圖
        time.sleep(2)
        photo = self.wait.until(EC.element_to_be_clickable((AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeCell[1]")))
        photo.click()
        for lbl in ["完成", "Done", "Add"]:
            if self._safe_click(lbl, timeout=2): break

        # Step 4: 地點與評分
        self._safe_click(ids.ModifyLogSection2View.spotView)
        self.wait.until(EC.element_to_be_clickable((AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeTable/XCUIElementTypeCell[1]"))).click()
        self._safe_click(ids.ExploreSelectButtonView.selectButton)
        self._safe_click(ids.RatingSelectView.rating5Button)
        self._safe_click(ids.ExploreRatingCommentView.confirmButton)

        # Step 5: 潛伴
        self._safe_click(ids.ModifyLogSection2View.partnerView)
        self._safe_click("線上") 
        self._safe_click("DIVEROUT")
        self._safe_click(ids.PartnerListViewController.doneButton)

        # Step 6: 發布
        self._safe_click(ids.ModifyPurePostViewController.postButton)
```

---

### 3. test_post_user_story.py
**路徑**: `execution/test_post_user_story.py`
**用途**: 完整的「發布文章」全流程測試（Version 12 穩定版）。

```python
import pytest
import time
import os
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import accessibility_ids as ids

class TestPostUserStory:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 45)

    def test_pure_post_full_flow(self):
        # 1. 入口
        self.wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, ids.TabBarController.addTab))).click()
        self.wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, ids.AddViewController.purePostView))).click()
        
        # 2. 標題
        title_box = self.wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, ids.ModifyPurePostPrimaryView.titleView)))
        title_box.click()
        self.wait.until(EC.presence_of_element_located((AppiumBy.CLASS_NAME, "XCUIElementTypeTextField"))).send_keys("Tactical B: V12 Optimized")

        # 3. 潛點 (V12)
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.ModifyLogSection2View.spotView).click()
        cells = self.driver.find_elements(AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeCell")
        if len(cells) >= 2: cells[1].click()
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.ExploreSelectButtonView.selectButton).click()

        # 4. 潛伴
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.ModifyLogSection2View.partnerView).click()
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "線上").click()
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "DIVEROUT").click()
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, "完成").click()

        # 5. 照片
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.ModifyLogPhotoAddCollectionViewCell.dashedAddView).click()

        # 6. 正式發布
        self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.ModifyPurePostViewController.postButton).click()
```

---

### 4. test_check_ids.py
**路徑**: `execution/test_check_ids.py`
**用途**: 驗證關鍵 Accessibility ID 是否存在的檢測腳本。

```python
import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
import accessibility_ids as ids

def test_check_accessibility_ids(driver):
    add_tab = driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.TabBarController.addTab)
    add_tab.click()
    pure_post = driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.AddViewController.purePostView)
    pure_post.click()
    # Check common elements
    elements_to_check = [
        ("Title Box", ids.ModifyPurePostPrimaryView.titleView),
        ("Photo Add Button", ids.ModifyLogPhotoAddCollectionViewCell.dashedAddView)
    ]
    for name, aid in elements_to_check:
        try:
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, aid)
            print(f"✅ Found {name}")
        except: print(f"⚠️ Missing {name}")
```

---

### 5. inspect_page.py
**路徑**: `execution/inspect_page.py`
**用途**: 探查特定頁面結構並抓取 XML。

```python
import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
import accessibility_ids

def test_inspect_pure_post_page(driver):
    # 導航至發布頁面
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_ids.TabBarController.addTab).click()
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_ids.AddViewController.purePostView).click()
    # 抓截圖與 XML
    source = driver.page_source
    with open("/tmp/pure_post_source.xml", "w", encoding="utf-8") as f:
        f.write(source)
```

---

### 6. debug_page.py
**路徑**: `execution/debug_page.py`
**用途**: 調試「我的」分頁結構。

```python
import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
import accessibility_ids

def test_debug_page_source(driver):
    time.sleep(5)
    source = driver.page_source
    with open("/tmp/page_source_mine.xml", "w", encoding="utf-8") as f:
        f.write(source)
```

---

### 7. current_screen_dump.py
**路徑**: `execution/current_screen_dump.py`
**用途**: 快速抓取當前模擬器頁面的 XML 與截圖。

```python
import time
from appium import webdriver
from appium.options.common import AppiumOptions

def dump_screen():
    options = AppiumOptions()
    options.set_capability("platformName", "iOS")
    # ... 設置細節 ...
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    source = driver.page_source
    with open(".tmp/current_dump.xml", "w", encoding="utf-8") as f:
        f.write(source)
    driver.save_screenshot(".tmp/current_dump.png")
    driver.quit()
```

---

### 8. conftest.py
**路徑**: `execution/conftest.py`
**用途**: Pytest 共享配置（Appium 啟動）。

```python
import pytest
from appium import webdriver
from appium.options.ios import XCUITestOptions

@pytest.fixture(scope="class")
def driver():
    options = XCUITestOptions()
    options.bundle_id = "com.diverout.diverout.dev"
    # ... 配置細節 ...
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield driver
    driver.quit()
```

---

### 9. accessibility_ids.py
**路徑**: `execution/accessibility_ids.py`
**用途**: 自動生成的 ID 對照表（超過 3000 行，此處略過）。
