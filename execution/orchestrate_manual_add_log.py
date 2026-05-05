import subprocess
import sys
import argparse
from pathlib import Path
import json

PASS_ICON = "🟢"
FAIL_ICON = "🔴"
INFO_ICON = "🔵"

def run_command(cmd, description):
    print(f"{INFO_ICON} ==> {description}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{FAIL_ICON} ERROR: {description} failed.")
        print(result.stdout)
        print(result.stderr)
        return False, result.stdout
    print(result.stdout)
    print(f"{PASS_ICON} SUCCESS: {description} completed.")
    return True, result.stdout

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Manual Add Dive Log Creation and Verification.")
    parser.add_argument("--skip-creation", action="store_true", help="Skip the creation step.")
    args = parser.parse_args()

    execution_dir = Path(__file__).parent
    
    title = None

    if not args.skip_creation:
        # 1. Run Creation
        # Note: We need to ensure manual_add_log_with_ids.py returns the title it generated.
        # Currently it prints the report path. We might need to parse the report or the results.json.
        success, output = run_command(
            [sys.executable, str(execution_dir / "create_manual_add_log.py")],
            "Creating Manual Dive Log"
        )
        if not success:
            sys.exit(1)
        
        # Try to find the title from the output or the latest results.json
        # The script creates a directory in .tmp/manual-add-log-evidence/<timestamp>/results.json
        evidence_root = execution_dir.parent / ".tmp" / "manual-add-log-evidence"
        if evidence_root.exists():
            dirs = sorted([d for d in evidence_root.iterdir() if d.is_dir()], key=lambda d: d.name, reverse=True)
            if dirs:
                latest_json = dirs[0] / "results.json"
                if latest_json.exists():
                    try:
                        data = json.loads(latest_json.read_text())
                        title = data.get("test_title")
                        print(f"{INFO_ICON} Extracted generated title: {title}")
                    except Exception as e:
                        print(f"{FAIL_ICON} Warning: Could not parse results.json: {e}")

    if not title:
        # Fallback if no creation was run or title extraction failed
        # In a real scenario, we might want to pass this as an argument if skipping creation
        print(f"{FAIL_ICON} Error: No test title found to verify.")
        sys.exit(1)

    # 2. Run Verification
    success, output = run_command(
        [sys.executable, str(execution_dir / "verify_manual_add_log_result.py"), "--title", title],
        f"Verifying Dive Log: {title}"
    )
    
    if success:
        print("\n" + "="*40)
        print(f"{PASS_ICON} ORCHESTRATION SUCCESSFUL")
        print(f"Title: {title}")
        print("="*40)
    else:
        print("\n" + "="*40)
        print(f"{FAIL_ICON} ORCHESTRATION FAILED")
        print("="*40)
        sys.exit(1)

if __name__ == "__main__":
    main()
