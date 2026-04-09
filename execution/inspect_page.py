import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
import accessibility_ids

def test_inspect_pure_post_page(driver):
    """
    這個腳本只做一件事：進到發布頁，填個字，關鍵盤，然後抓 Page Source。
    """
    print("\n[DEBUG] 進入發布頁面探測...")
    
    # 導航
    try:
        add_tab = driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_ids.TabBarController.addTab)
        add_tab.click()
        time.sleep(1)
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_ids.AddViewController.purePostView).click()
        time.sleep(2)
    except:
        pass # 可能已在頁面

    # 填字
    title = driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_ids.ModifyPurePostPrimaryView.titleView)
    title.click()
    driver.find_element(AppiumBy.CLASS_NAME, "XCUIElementTypeTextField").send_keys("PAGE-SOURCE-CHECK")
    
    # 座標點擊收起鍵盤
    win = driver.get_window_size()
    driver.tap([(win['width'] - 40, win['height'] // 2 + 10)])
    time.sleep(2)

    # 截圖確認鍵盤收起來了
    driver.save_screenshot("/tmp/debug_keyboard_dismissed.png")
    
    # 抓取 XML
    source = driver.page_source
    with open("/tmp/pure_post_source.xml", "w", encoding="utf-8") as f:
        f.write(source)
    
    print("[DEBUG] XML 已存入 /tmp/pure_post_source.xml")
    print("[DEBUG] 截圖已存入 /tmp/debug_keyboard_dismissed.png")
