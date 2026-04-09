import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import accessibility_ids

def test_debug_page_source(driver):
    """
    抓取目前「我的」分頁的頁面結構。
    """
    print("\n[DEBUG] 正在抓取「我的」分頁頁面結構...")
    time.sleep(5) # 等 App 啟動穩定
    
    # 印出 Page Source 以便確認 ID 到底在不在
    source = driver.page_source
    # 我們把 source 寫進一個文件，方便我看清楚
    with open("/tmp/page_source_mine.xml", "w", encoding="utf-8") as f:
        f.write(source)
    print("[DEBUG] 頁面結構已存入 /tmp/page_source_mine.xml")
    
    # 嘗試找尋 Tab Bar 的 addTab 按鈕
    try:
        add_tab = driver.find_element(AppiumBy.ACCESSIBILITY_ID, accessibility_ids.TabBarController.addTab)
        print(f"[DEBUG] addTab 找到！位置: {add_tab.location}, 可見性: {add_tab.is_displayed()}")
    except:
        print("[DEBUG] 找不到 addTab ID")
