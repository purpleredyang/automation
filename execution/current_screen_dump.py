import time
from appium import webdriver
from appium.options.common import AppiumOptions

def dump_screen():
    options = AppiumOptions()
    options.set_capability("platformName", "iOS")
    options.set_capability("appium:deviceName", "iPhone 17 Pro")
    options.set_capability("appium:automationName", "XCUITest")
    options.set_capability("appium:bundleId", "com.diverout.diverout.dev")
    options.set_capability("appium:noReset", True)
    
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
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
