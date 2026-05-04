from manual_add_log_with_ids import ManualAddLogAutomation


if __name__ == "__main__":
    report_path = ManualAddLogAutomation().run_partial_probe()
    print(f"Evidence report: {report_path}")
