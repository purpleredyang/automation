from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30)

    def safe_click(self, locator, by=AppiumBy.ACCESSIBILITY_ID, timeout=15):
        """ Robust click using explicit wait """
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, locator)))
            element.click()
            return True
        except Exception as e:
            print(f"⚠️ Failed to click {locator} via {by}: {str(e)[:50]}")
            return False

    def wait_for_element(self, locator, by=AppiumBy.ACCESSIBILITY_ID, timeout=15):
        """ Explicitly wait for element's presence """
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, locator)))
        except:
            return None

    def wait_for_invisibility(self, locator, by=AppiumBy.ACCESSIBILITY_ID, timeout=15):
        """ Optimized for removing time.sleep(2) """
        try:
            return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located((by, locator)))
        except:
            return False
