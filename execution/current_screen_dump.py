import time
import os
from appium import webdriver
from appium.options.common import AppiumOptions

from env_utils import load_env_file


load_env_file()

def dump_screen():
    options = AppiumOptions()
    options.set_capability("platformName", "iOS")
    options.set_capability("appium:automationName", "XCUITest")
    options.set_capability(
        "appium:bundleId", os.getenv("BUNDLE_ID", "com.diverout.diverout.dev")
    )
    options.set_capability("appium:noReset", True)

    driver = webdriver.Remote(
        os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
        options=options,
    )
    time.sleep(2)
    
    source = driver.page_source
    with open(".tmp/current_dump.xml", "w", encoding="utf-8") as f:
        f.write(source)
    
    driver.save_screenshot(".tmp/current_dump.png")
    print(f"Dumped XML to .tmp/current_dump.xml")
    print(f"Dumped screenshot to .tmp/current_dump.png")
    driver.quit()

if __name__ == "__main__":
    dump_screen()
