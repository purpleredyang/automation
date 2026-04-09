import pytest
import time
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

@pytest.fixture(scope="class")
def driver():
    """
    回復到最初最穩定的配置
    """
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.udid = "A1BE37E2-D482-4B1D-861B-4B2372E2BD57"
    options.bundle_id = "com.diverout.diverout.dev"
    options.set_capability("noReset", True)
    options.set_capability("autoAcceptAlerts", True)
    options.set_capability("usePrebuiltWDA", True)  # [PUA加速 🔥] 減少編譯損耗
    options.set_capability("wdaStartupRetries", 3)
    options.set_capability("wdaLaunchTimeout", 60000)
    options.set_capability("shouldTerminateApp", True)

    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    driver.implicitly_wait(10)

    # 只保留最簡單的啟動時排除
    time.sleep(2)
    _dismiss_update_alert(driver)

    yield driver
    driver.quit()

def _dismiss_update_alert(driver):
    """最基本的更新提示排除"""
    for label in ["稍後", "取消", "關閉", "Later", "Cancel", "Close", "Skip"]:
        try:
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, label).click()
            return
        except:
            pass
