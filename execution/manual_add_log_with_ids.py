import json
import os
from dataclasses import dataclass
from datetime import datetime
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
ARTIFACT_ROOT = ROOT_DIR / ".tmp" / "manual-add-log-evidence"


@dataclass
class StepSpec:
    name: str
    expected_id: str | None
    fallback: str
    note: str


STEP_SPECS = [
    StepSpec(
        name="Tap add tab",
        expected_id=ids.TabBarController.addTab,
        fallback="Tap the center tab-bar slot by coordinates.",
        note="Primary navigation entry into Add flow.",
    ),
    StepSpec(
        name="Tap manual add log",
        expected_id=ids.AddViewController.manualAddLogView,
        fallback="Match visible text for the row if AX id is missing.",
        note="Routes to ModifyLog screen.",
    ),
    StepSpec(
        name="Choose scuba segment",
        expected_id=ids.ModifyLogSection1View.segmentedControl,
        fallback="Tap visible text '水肺潛水' if the segment option is not individually exposed.",
        note="Container has an AX id, but the selected option text is sometimes easier to target.",
    ),
    StepSpec(
        name="Enter title",
        expected_id=ids.ModifyLogTitleView.titleTextField,
        fallback="Tap the first visible text field under the title section.",
        note="Title field should be directly addressable.",
    ),
    StepSpec(
        name="Open photos field",
        expected_id=ids.ModifyLogPhotoTitleView.titleLabel,
        fallback="Tap visible text '照片' if the title label is not exposed.",
        note="Tapping the photos entry should dismiss the keyboard and open photo management.",
    ),
    StepSpec(
        name="Tap photo add plus",
        expected_id=ids.ModifyLogPhotoAddCollectionViewCell.dashedAddView,
        fallback="Use ModifyLogPhotosViewController.addButton if the dashed add card is not exposed.",
        note="Primary entry for adding photos to the dive log.",
    ),
    StepSpec(
        name="Choose spot source",
        expected_id=None,
        fallback="Tap visible text '潛點'.",
        note="Current codebase exposes this action-sheet option as visible text.",
    ),
    StepSpec(
        name="Select two photos",
        expected_id=None,
        fallback="Tap the first two cells in the system photo picker grid.",
        note="Uses the visible Recents collection view because system items do not expose project accessibility IDs.",
    ),
    StepSpec(
        name="Tap picker done",
        expected_id=None,
        fallback="Tap the visible system picker '完成' button.",
        note="Closes the system photo picker and returns to the app photo page.",
    ),
    StepSpec(
        name="Tap photos page done",
        expected_id=ids.ModifyPhotosViewController.doneButton,
        fallback="Tap visible text '完成' on the app photo page.",
        note="Returns from the photo page to the modify log page.",
    ),
    StepSpec(
        name="Submit new log",
        expected_id=ids.ModifyLogViewController.addButton,
        fallback="Tap visible text '新增' on the modify log page.",
        note="Completes the manual add-log flow.",
    ),
]


class ManualAddLogAutomation:
    def __init__(self):
        load_env_file()
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.test_title = f"QA-MANUAL-LOG-{self.timestamp}"
        self.output_dir = ARTIFACT_ROOT / self.timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.step_results: list[dict] = []
        self.driver = self._connect_driver()

    def _connect_driver(self):
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
        driver.implicitly_wait(0)
        self._wait_for_any_id(
            driver,
            [
                ids.TabBarController.addTab,
                ids.TabBarController.mineTab,
                ids.AddViewController.manualAddLogView,
                ids.ModifyLogViewController.scrollView,
            ],
            timeout=12,
        )
        return driver

    def _wait_for_id(self, locator: str, timeout: int = 8):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, locator))
            )
        except TimeoutException:
            return None

    def _wait_for_any_id(self, driver, locators: list[str], timeout: int = 8):
        end = WebDriverWait(driver, timeout)
        for locator in locators:
            try:
                return end.until(
                    EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, locator))
                )
            except TimeoutException:
                continue
        return None

    def _wait_for_static_text(self, text: str, timeout: int = 8):
        xpath = f"//XCUIElementTypeStaticText[@name='{text}']"
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, xpath))
            )
        except TimeoutException:
            return None

    def _wait_for_button_name(self, text: str, timeout: int = 8):
        xpath = f"//XCUIElementTypeButton[@name='{text}']"
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, xpath))
            )
        except TimeoutException:
            return None

    def _find_static_text(self, text: str):
        xpath = f"//XCUIElementTypeStaticText[@name='{text}']"
        matches = self.driver.find_elements(AppiumBy.XPATH, xpath)
        return matches[0] if matches else None

    def _find_button_by_name(self, text: str):
        xpath = f"//XCUIElementTypeButton[@name='{text}']"
        matches = self.driver.find_elements(AppiumBy.XPATH, xpath)
        return matches[0] if matches else None

    def _tap_tab_bar_slot(self, slot_index: int, total_slots: int = 5) -> tuple[int, int]:
        size = self.driver.get_window_size()
        x = int(size["width"] * ((slot_index + 0.5) / total_slots))
        y = int(size["height"] - 42)
        self.driver.tap([(x, y)])
        return x, y

    def _capture(self, slug: str) -> tuple[str, str]:
        screenshot = self.output_dir / f"{slug}.png"
        source_file = self.output_dir / f"{slug}.xml"
        self.driver.save_screenshot(str(screenshot))
        source_file.write_text(self.driver.page_source, encoding="utf-8")
        return (str(screenshot), str(source_file))

    def _record(
        self,
        spec: StepSpec,
        status: str,
        implementation: str,
        detail: str,
        capture: bool = False,
    ) -> None:
        screenshot = "n/a"
        source_file = "n/a"
        if capture:
            slug = f"{len(self.step_results)+1:02d}-{spec.name.lower().replace(' ', '-')[:40]}"
            screenshot, source_file = self._capture(slug)
        self.step_results.append(
            {
                "step": spec.name,
                "expected_id": spec.expected_id,
                "fallback": spec.fallback,
                "note": spec.note,
                "status": status,
                "implementation": implementation,
                "detail": detail,
                "screenshot": screenshot,
                "source": source_file,
            }
        )

    def _capture_final_state(self) -> tuple[str, str]:
        return self._capture("final-state")

    def _wait_after_step(self, spec: StepSpec) -> None:
        if spec.name == "Tap add tab":
            self._wait_for_any_id(self.driver, [ids.AddViewController.manualAddLogView], timeout=8)
        elif spec.name == "Tap manual add log":
            self._wait_for_any_id(self.driver, [ids.ModifyLogViewController.scrollView, ids.ModifyLogSection1View.segmentedControl], timeout=10)
        elif spec.name == "Enter title":
            self._wait_for_any_id(self.driver, [ids.ModifyLogPhotoTitleView.titleLabel], timeout=6)
        elif spec.name == "Open photos field":
            self._wait_for_any_id(self.driver, [ids.ModifyLogPhotoAddCollectionViewCell.dashedAddView, ids.ModifyLogPhotosViewController.addButton], timeout=8)
        elif spec.name == "Tap photo add plus":
            self._wait_for_static_text(ids.AddPhotoActionSheetTag.spotSelection, timeout=8)
        elif spec.name == "Choose spot source":
            self._wait_for_button_name("完成", timeout=10)
        elif spec.name == "Tap picker done":
            self._wait_for_any_id(self.driver, [ids.ModifyPhotosViewController.doneButton], timeout=10)
        elif spec.name == "Tap photos page done":
            self._wait_for_any_id(self.driver, [ids.ModifyLogViewController.addButton], timeout=10)

    def _tap_id_or_text(self, spec: StepSpec, text_candidates: list[str] | None = None) -> bool:
        if spec.expected_id:
            element = self._wait_for_id(spec.expected_id)
            if element:
                element.click()
                self._record(spec, "ok", f"Accessibility ID: {spec.expected_id}", "Tapped by AX id.")
                self._wait_after_step(spec)
                return True

        for candidate in text_candidates or []:
            element = self._find_static_text(candidate)
            if element:
                element.click()
                self._record(spec, "fallback", f"Visible text: {candidate}", "Primary AX id unavailable.")
                self._wait_after_step(spec)
                return True

        if spec.expected_id == ids.TabBarController.addTab:
            tap_x, tap_y = self._tap_tab_bar_slot(slot_index=2)
            self._record(
                spec,
                "fallback",
                f"Tab bar coordinate: ({tap_x}, {tap_y})",
                "Primary AX id unavailable; tapped the center tab-bar slot.",
            )
            self._wait_after_step(spec)
            return True

        self._record(spec, "missing", "Not executed", "Could not resolve AX id or fallback text.", capture=True)
        return False

    def _choose_scuba_segment(self, spec: StepSpec) -> bool:
        segment = self._wait_for_id(spec.expected_id) if spec.expected_id else None
        if segment:
            self._record(
                spec,
                "ok",
                f"Accessibility ID: {spec.expected_id}",
                "Segmented control was present; left the existing selection unchanged.",
            )
            return True

        self._record(spec, "missing", "Not executed", "Could not resolve segmented control.", capture=True)
        return False

    def _enter_title(self, spec: StepSpec) -> bool:
        text_field = self._wait_for_id(spec.expected_id) if spec.expected_id else None
        if not text_field:
            text_fields = self.driver.find_elements(AppiumBy.XPATH, "//XCUIElementTypeTextField")
            text_field = text_fields[0] if text_fields else None
            if not text_field:
                self._record(spec, "missing", "Not executed", "Title text field AX id not found.", capture=True)
                return False
            implementation = "First visible text field"
            status = "fallback"
        else:
            implementation = f"Accessibility ID: {spec.expected_id}"
            status = "ok"

        text_field.click()
        text_field.clear()
        text_field.send_keys(self.test_title)
        self._record(spec, status, implementation, f"Entered title {self.test_title}.")
        self._wait_after_step(spec)
        return True

    def _tap_photo_add_entry(self, spec: StepSpec) -> bool:
        primary = self._wait_for_id(spec.expected_id) if spec.expected_id else None
        if primary:
            primary.click()
            self._record(spec, "ok", f"Accessibility ID: {spec.expected_id}", "Tapped by AX id.")
            self._wait_after_step(spec)
            return True

        fallback = self._wait_for_id(ids.ModifyLogPhotosViewController.addButton, timeout=3)
        if fallback:
            fallback.click()
            self._record(
                spec,
                "fallback",
                f"Accessibility ID: {ids.ModifyLogPhotosViewController.addButton}",
                "Primary dashed add card was unavailable.",
            )
            self._wait_after_step(spec)
            return True

        self._record(spec, "missing", "Not executed", "Could not resolve photo add entry.", capture=True)
        return False

    def _choose_spot_source(self, spec: StepSpec) -> bool:
        element = self._find_static_text(ids.AddPhotoActionSheetTag.spotSelection)
        if element:
            element.click()
            self._record(spec, "fallback", f"Visible text: {ids.AddPhotoActionSheetTag.spotSelection}", "Opened the spot-based system photo picker.")
            self._wait_after_step(spec)
            return True

        self._record(spec, "missing", "Not executed", "Could not resolve AX id or fallback text.", capture=True)
        return False

    def _select_two_photos(self, spec: StepSpec) -> bool:
        cells = self.driver.find_elements(
            AppiumBy.XPATH,
            "//XCUIElementTypeCollectionView/XCUIElementTypeCell",
        )
        if len(cells) < 3:
            self._record(spec, "missing", "Not executed", f"Expected at least 3 picker cells, found {len(cells)}.", capture=True)
            return False

        chosen_indices: list[int] = []
        for index in [1, 2]:
            cells[index].click()
            chosen_indices.append(index)

        self._record(spec, "fallback", f"Picker cells: {chosen_indices}", "Selected two visible media items from Recents.")
        return True

    def _tap_system_done(self, spec: StepSpec) -> bool:
        button = self._find_button_by_name("完成")
        if button:
            button.click()
            self._record(spec, "fallback", "Visible button: 完成", "Closed the system photo picker.")
            self._wait_after_step(spec)
            return True

        self._record(spec, "missing", "Not executed", "System picker done button was not found.", capture=True)
        return False

    def export_report(self) -> Path:
        report = self.output_dir / "report.md"
        lines = [
            "# Manual Add Log Automation Evidence",
            "",
            f"- Generated: {datetime.now().isoformat()}",
            f"- Test title: `{self.test_title}`",
            "",
            "## Step Coverage",
            "",
        ]

        for item in self.step_results:
            lines.append(f"### {item['step']}")
            lines.append(f"- Status: `{item['status']}`")
            lines.append(f"- Expected Accessibility ID: `{item['expected_id']}`")
            lines.append(f"- Implementation: {item['implementation']}")
            lines.append(f"- Fallback: {item['fallback']}")
            lines.append(f"- Note: {item['note']}")
            lines.append(f"- Detail: {item['detail']}")
            lines.append(f"- Screenshot: `{item['screenshot']}`")
            lines.append(f"- Source: `{item['source']}`")
            lines.append("")

        report.write_text("\n".join(lines), encoding="utf-8")
        metadata = self.output_dir / "results.json"
        metadata.write_text(
            json.dumps(
                {
                    "generated_at": datetime.now().isoformat(),
                    "test_title": self.test_title,
                    "steps": self.step_results,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return report

    def run_partial_probe(self) -> Path:
        try:
            self._tap_id_or_text(STEP_SPECS[0])
            self._tap_id_or_text(STEP_SPECS[1], ["手動添加潛水記錄", "手動添加潛水紀錄"])
            self._choose_scuba_segment(STEP_SPECS[2])
            self._enter_title(STEP_SPECS[3])
            self._tap_id_or_text(STEP_SPECS[4], ["照片"])
            self._tap_photo_add_entry(STEP_SPECS[5])
            self._choose_spot_source(STEP_SPECS[6])
            self._select_two_photos(STEP_SPECS[7])
            self._tap_system_done(STEP_SPECS[8])
            self._tap_id_or_text(STEP_SPECS[9], ["完成"])
            self._tap_id_or_text(STEP_SPECS[10], ["新增"])
            screenshot, source = self._capture_final_state()
            if self.step_results:
                self.step_results[-1]["screenshot"] = screenshot
                self.step_results[-1]["source"] = source
            return self.export_report()
        except Exception:
            if self.step_results:
                screenshot, source = self._capture("exception-state")
                self.step_results[-1]["screenshot"] = screenshot
                self.step_results[-1]["source"] = source
            raise
        finally:
            self.driver.quit()


if __name__ == "__main__":
    report_path = ManualAddLogAutomation().run_partial_probe()
    print(f"Evidence report: {report_path}")
