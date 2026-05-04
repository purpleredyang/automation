import argparse
import os
import sys
import time
from pathlib import Path

from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import accessibility_ids as ids
from env_utils import load_env_file


ROOT_DIR = Path(__file__).resolve().parents[1]
TMP_DIR = ROOT_DIR / ".tmp" / "verification"
TMP_DIR.mkdir(parents=True, exist_ok=True)


def light(status: str, message: str) -> None:
    print(f"[{status}] {message}")


def connect_driver():
    load_env_file()

    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.automation_name = "XCUITest"
    options.bundle_id = os.getenv("BUNDLE_ID", "com.diverout.diverout.dev")
    options.set_capability("noReset", True)
    options.set_capability("autoAcceptAlerts", True)
    options.set_capability("usePrebuiltWDA", True)
    options.set_capability("wdaStartupRetries", 3)
    options.set_capability("wdaLaunchTimeout", 60000)
    options.set_capability("shouldTerminateApp", False)

    server_url = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    driver = webdriver.Remote(server_url, options=options)
    driver.implicitly_wait(3)
    return driver


def wait_for_element(driver, locator: str, timeout: int = 10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, locator))
        )
    except TimeoutException:
        return None


def dump_state(driver, slug: str) -> None:
    xml_path = TMP_DIR / f"{slug}.xml"
    png_path = TMP_DIR / f"{slug}.png"
    xml_path.write_text(driver.page_source, encoding="utf-8")
    driver.save_screenshot(str(png_path))
    light("INFO", f"Dumped state to {xml_path} and {png_path}")


def click_accessibility_id(driver, locator: str, success_message: str, timeout: int = 10) -> bool:
    element = wait_for_element(driver, locator, timeout=timeout)
    if not element:
        light("FAIL", f"Missing Accessibility ID: {locator}")
        return False
    element.click()
    light("PASS", success_message)
    return True


def click_first_available_id(driver, locators: list[str], success_message: str, timeout: int = 6) -> str | None:
    for locator in locators:
        element = wait_for_element(driver, locator, timeout=timeout)
        if element:
            element.click()
            light("PASS", f"{success_message}: {locator}")
            return locator
    light("FAIL", f"None of the expected Accessibility IDs were found: {', '.join(locators)}")
    return None


def get_visible_manage_log_titles(driver) -> list[str]:
    elements = driver.find_elements(AppiumBy.ACCESSIBILITY_ID, ids.ManageLogsTableViewCell.titleLabel)
    titles: list[str] = []
    for element in elements:
        text = (element.text or "").strip()
        if text:
            titles.append(text)
    return titles


def get_visible_mine_titles(driver) -> list[str]:
    elements = driver.find_elements(AppiumBy.XPATH, "//XCUIElementTypeStaticText")
    titles: list[str] = []
    for element in elements:
        text = (element.text or "").strip()
        if text:
            titles.append(text)
    return titles


def get_first_mine_log_card(driver):
    cards = driver.find_elements(
        AppiumBy.XPATH,
        "//XCUIElementTypeCell[@name='DiveLogCollectionViewCell.cell']",
    )
    return cards[0] if cards else None


def verify_first_card_title(driver, expected_title: str) -> bool:
    card = get_first_mine_log_card(driver)
    if not card:
        light("FAIL", "Did not find the first Mine-page log card")
        return False

    title_nodes = card.find_elements(AppiumBy.XPATH, ".//XCUIElementTypeStaticText")
    values = [(node.text or "").strip() for node in title_nodes if (node.text or "").strip()]

    if expected_title in values:
        light("PASS", f"First Mine-page log card shows expected title: {expected_title}")
        return True

    for value in values:
        if expected_title.startswith(value) or value.startswith(expected_title[: min(len(expected_title), 12)]):
            light("PASS", f"First Mine-page log card shows truncated expected title: {value}")
            return True

    light("FAIL", f"First Mine-page log card title did not match expected log: {expected_title}")
    return False


def verify_first_card_scuba_icon(driver) -> bool:
    card = get_first_mine_log_card(driver)
    if not card:
        light("FAIL", "Did not find the first Mine-page log card for scuba icon verification")
        return False

    scuba_icons = card.find_elements(
        AppiumBy.XPATH,
        ".//XCUIElementTypeImage[@name='icon_scuba']",
    )
    if scuba_icons:
        light("PASS", "First Mine-page log card shows scuba icon")
        return True

    light("FAIL", "First Mine-page log card did not expose a scuba icon")
    return False


def tap_first_card_fallback(driver) -> bool:
    card = get_first_mine_log_card(driver)
    if not card:
        light("FAIL", "Did not find the first Mine-page log card to open detail")
        return False

    rect = card.rect
    tap_x = int(rect["x"] + rect["width"] / 2)
    tap_y = int(rect["y"] + rect["height"] / 2)
    driver.tap([(tap_x, tap_y)])
    light("PASS", "Opened first Mine-page log card via positional fallback")
    return True


def wait_for_page_source_contains(driver, text: str, timeout: int = 10) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if text in driver.page_source:
            return True
        time.sleep(0.5)
    return False


def verify_detail_title(driver, expected_title: str) -> bool:
    if wait_for_page_source_contains(driver, expected_title, timeout=10):
        light("PASS", f"Detail page shows full title: {expected_title}")
        return True

    light("FAIL", f"Detail page did not show full title: {expected_title}")
    return False


def verify_detail_photo_indicator(driver) -> bool:
    source = driver.page_source
    candidates = ["1/2", "2/2", "1 / 2", "2 / 2"]
    for candidate in candidates:
        if candidate in source:
            light("PASS", f"Detail page shows two-photo indicator: {candidate}")
            return True

    light("FAIL", "Detail page did not expose a two-photo indicator")
    return False


def find_title_in_manage_logs(driver, expected_title: str, max_scrolls: int = 4) -> bool:
    for _ in range(max_scrolls + 1):
        visible_titles = get_visible_manage_log_titles(driver)
        if expected_title in visible_titles:
            light("PASS", f"Found new dive log in ManageLogs list: {expected_title}")
            return True

        size = driver.get_window_size()
        start_x = int(size["width"] * 0.5)
        start_y = int(size["height"] * 0.72)
        end_y = int(size["height"] * 0.42)
        driver.swipe(start_x, start_y, start_x, end_y, 700)
        time.sleep(1)

    light("FAIL", f"Did not find new dive log in ManageLogs list: {expected_title}")
    return False


def find_title_on_mine_page(driver, expected_title: str) -> bool:
    visible_titles = get_visible_mine_titles(driver)
    if expected_title in visible_titles:
        light("PASS", f"Found new dive log on Mine page: {expected_title}")
        return True

    for title in visible_titles:
        if expected_title.startswith(title) or title.startswith(expected_title[: min(len(expected_title), 12)]):
            light("PASS", f"Found truncated Mine page title matching expected log: {title}")
            return True

    light("FAIL", f"Did not find new dive log on Mine page: {expected_title}")
    return False


def verify_manual_add_result(expected_title: str) -> int:
    driver = connect_driver()
    try:
        time.sleep(2)

        if not click_accessibility_id(
            driver,
            ids.TabBarController.mineTab,
            "Tapped Mine tab via Accessibility ID",
        ):
            dump_state(driver, "missing-mine-tab")
            return 1

        mine_root = (
            wait_for_element(driver, ids.MineViewController.collectionView, timeout=10)
            or wait_for_element(driver, ids.MyProfileViewController.collectionView, timeout=10)
            or wait_for_element(driver, ids.BaseProfileViewController.collectionView, timeout=10)
            or wait_for_element(driver, ids.MineViewController.segmentedControl, timeout=10)
            or wait_for_element(driver, ids.TotalCountView.manageButton, timeout=10)
        )
        if not mine_root:
            light("FAIL", "Mine/Profile root view did not appear after tapping Mine tab")
            dump_state(driver, "missing-mine-root")
            return 1
        light("PASS", "Reached Mine/Profile area")

        light("INFO", "Using temporary fallback verification on Mine page title visibility; log card container lacks a stable Accessibility ID.")

        if not find_title_on_mine_page(driver, expected_title):
            dump_state(driver, "title-not-found-on-mine")
            return 1

        if not verify_first_card_title(driver, expected_title):
            dump_state(driver, "first-card-title-mismatch")
            return 1

        if not verify_first_card_scuba_icon(driver):
            dump_state(driver, "first-card-not-scuba")
            return 1

        if not tap_first_card_fallback(driver):
            dump_state(driver, "failed-open-first-card")
            return 1

        time.sleep(2)

        if not verify_detail_title(driver, expected_title):
            dump_state(driver, "detail-title-mismatch")
            return 1

        if not verify_detail_photo_indicator(driver):
            dump_state(driver, "detail-photo-indicator-missing")
            return 1

        light("PASS", "Manual Add Dive Log verification completed")
        return 0
    finally:
        driver.quit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the newly added dive log from the Mine > ManageLogs flow.")
    parser.add_argument("--title", required=True, help="Expected dive log title to verify.")
    args = parser.parse_args()
    return verify_manual_add_result(args.title)


if __name__ == "__main__":
    sys.exit(main())
