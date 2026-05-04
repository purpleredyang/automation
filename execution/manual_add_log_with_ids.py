import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import accessibility_ids as ids


ROOT_DIR = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT_DIR / ".tmp" / "manual-add-log-evidence"
SIMULATOR_UDID = "E5016B3C-530F-4AA5-88D5-8D64F6C8B4E5"
APP_BUNDLE_ID = "com.diverout.diverout.dev"


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
        fallback="Tap bottom-center tab bar area by coordinates.",
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
        fallback="Tap visible text '水肺潛水' or tap segment by relative offset.",
        note="Container has an AX id, but the individual segment option may not.",
    ),
    StepSpec(
        name="Enter title",
        expected_id=ids.ModifyLogTitleView.titleTextField,
        fallback="Tap first text field under title view and input text by keyboard.",
        note="Title field should be directly addressable.",
    ),
    StepSpec(
        name="Open photos field",
        expected_id=ids.ModifyLogSection1View.photosView,
        fallback="Tap the row labeled '照片'.",
        note="Opens photo management page.",
    ),
    StepSpec(
        name="Tap photo add plus",
        expected_id=ids.ModifyLogPhotoAddCollectionViewCell.dashedAddView,
        fallback="Use ModifyLogPhotosViewController.addButton or tap visible plus button.",
        note="Primary add-photo entry point.",
    ),
    StepSpec(
        name="Choose spot source",
        expected_id=None,
        fallback="Tap visible action-sheet text '潛點'.",
        note="Current codebase only exposes a text constant via AddPhotoActionSheetTag.spotSelection.",
    ),
    StepSpec(
        name="Choose arbitrary spot",
        expected_id=ids.ModifyLogSection2View.spotView,
        fallback="Tap first enabled cell/text in spot picker list.",
        note="Entry row has AX id, but downstream arbitrary list item id is unknown.",
    ),
    StepSpec(
        name="Select camera roll photos",
        expected_id=None,
        fallback="Tap first few selectable thumbnails by visible element frames.",
        note="System photo picker items are not represented in execution/accessibility_ids.py.",
    ),
    StepSpec(
        name="Tap picker done",
        expected_id=ids.ModifyPhotosViewController.doneButton,
        fallback="Tap top-right '完成' by text lookup.",
        note="Applies selected photos inside picker flow.",
    ),
    StepSpec(
        name="Tap photos page done",
        expected_id=ids.ModifyPhotosViewController.doneButton,
        fallback="Tap top-right '完成' again by text lookup.",
        note="Returns to modify log page.",
    ),
    StepSpec(
        name="Submit new log",
        expected_id=ids.ModifyLogViewController.addButton,
        fallback="Tap visible top-right '新增'.",
        note="Completes manual log creation.",
    ),
    StepSpec(
        name="Open mine tab",
        expected_id=ids.TabBarController.mineTab,
        fallback="Tap fourth tab-bar slot by coordinates.",
        note="Navigates to My page for verification.",
    ),
    StepSpec(
        name="Verify new record",
        expected_id=ids.ManageLogsTableViewCell.titleLabel,
        fallback="Find the generated title text in the visible logs list.",
        note="Verification likely depends on visible text instead of a unique row id.",
    ),
]


class ManualAddLogAutomation:
    def __init__(self, udid: str = SIMULATOR_UDID):
        self.udid = udid
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.test_title = f"QA-MANUAL-LOG-{self.timestamp}"
        self.output_dir = ARTIFACT_ROOT / self.timestamp
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.step_results: list[dict] = []

    def _run(self, cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)

    def _idb(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        return self._run(["idb", *args, "--udid", self.udid], check=check)

    def _simctl(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        return self._run(["xcrun", "simctl", *args], check=check)

    def _tree(self) -> list[dict]:
        result = self._idb("ui", "describe-all", "--json", "--nested")
        return json.loads(result.stdout)

    def _flatten(self, node: dict) -> list[dict]:
        items = [node]
        for child in node.get("children", []):
            items.extend(self._flatten(child))
        return items

    def _elements(self) -> list[dict]:
        tree = self._tree()
        root = tree[0] if isinstance(tree, list) else tree
        return self._flatten(root)

    def _find_by_id(self, identifier: str) -> dict | None:
        for element in self._elements():
            if element.get("AXUniqueId") == identifier:
                return element
        return None

    def _find_by_label(self, label: str) -> dict | None:
        for element in self._elements():
            if element.get("AXLabel") == label or element.get("AXValue") == label:
                return element
        return None

    def _tap_point(self, x: int, y: int) -> None:
        self._idb("ui", "tap", str(x), str(y))

    def _tap_element(self, element: dict) -> None:
        frame = element.get("frame", {})
        x = int(frame["x"] + frame["width"] / 2)
        y = int(frame["y"] + frame["height"] / 2)
        self._tap_point(x, y)

    def _enter_text(self, text: str) -> None:
        self._idb("ui", "text", text)

    def _capture(self, slug: str) -> tuple[str, str]:
        screenshot = self.output_dir / f"{slug}.png"
        tree_file = self.output_dir / f"{slug}.json"
        self._simctl("io", self.udid, "screenshot", str(screenshot), check=False)
        tree = self._tree()
        tree_file.write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
        return (str(screenshot), str(tree_file))

    def _record(
        self,
        spec: StepSpec,
        status: str,
        implementation: str,
        detail: str,
    ) -> None:
        slug = f"{len(self.step_results)+1:02d}-{spec.name.lower().replace(' ', '-')[:40]}"
        screenshot, tree_file = self._capture(slug)
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
                "tree": tree_file,
            }
        )

    def launch_app(self) -> None:
        self._simctl("launch", self.udid, APP_BUNDLE_ID, check=False)
        time.sleep(2)

    def tap_by_id_or_label(
        self,
        spec: StepSpec,
        label: str | None = None,
    ) -> bool:
        if spec.expected_id:
            element = self._find_by_id(spec.expected_id)
            if element:
                self._tap_element(element)
                self._record(spec, "ok", f"Accessibility ID: {spec.expected_id}", "Tapped by AX id.")
                time.sleep(1)
                return True
        if label:
            element = self._find_by_label(label)
            if element:
                self._tap_element(element)
                self._record(spec, "fallback", f"Visible text: {label}", "Primary AX id unavailable.")
                time.sleep(1)
                return True
        self._record(spec, "missing", "Not executed", "Could not resolve AX id or fallback text.")
        return False

    def enter_title(self, spec: StepSpec) -> bool:
        element = self._find_by_id(spec.expected_id) if spec.expected_id else None
        if not element:
            self._record(spec, "missing", "Not executed", "Title text field AX id not found.")
            return False
        self._tap_element(element)
        time.sleep(0.5)
        self._enter_text(self.test_title)
        self._record(spec, "ok", f"Accessibility ID: {spec.expected_id}", f"Entered title {self.test_title}.")
        time.sleep(1)
        return True

    def export_report(self) -> Path:
        report = self.output_dir / "report.md"
        recorded = {item["step"]: item for item in self.step_results}
        lines = [
            "# Manual Add Log Automation Evidence",
            "",
            f"- Generated: {datetime.now().isoformat()}",
            f"- Simulator UDID: `{self.udid}`",
            f"- Test title: `{self.test_title}`",
            "",
            "## Step Coverage",
            "",
        ]
        for spec in STEP_SPECS:
            item = recorded.get(
                spec.name,
                {
                    "step": spec.name,
                    "expected_id": spec.expected_id,
                    "fallback": spec.fallback,
                    "note": spec.note,
                    "status": "planned",
                    "implementation": "Not probed yet",
                    "detail": "Static coverage entry based on accessibility_ids.py and repo docs.",
                    "screenshot": "n/a",
                    "tree": "n/a",
                },
            )
            lines.append(f"### {item['step']}")
            lines.append(f"- Status: `{item['status']}`")
            lines.append(f"- Expected Accessibility ID: `{item['expected_id']}`")
            lines.append(f"- Implementation: {item['implementation']}")
            lines.append(f"- Fallback: {item['fallback']}")
            lines.append(f"- Note: {item['note']}")
            lines.append(f"- Detail: {item['detail']}")
            lines.append(f"- Screenshot: `{item['screenshot']}`")
            lines.append(f"- Accessibility Tree: `{item['tree']}`")
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
        self.launch_app()
        self.tap_by_id_or_label(STEP_SPECS[0], label=None)
        self.tap_by_id_or_label(STEP_SPECS[1], label="手動添加潛水紀錄")
        self.tap_by_id_or_label(STEP_SPECS[2], label="水肺潛水")
        self.enter_title(STEP_SPECS[3])
        return self.export_report()


if __name__ == "__main__":
    report_path = ManualAddLogAutomation().run_partial_probe()
    print(f"Evidence report: {report_path}")
