import unittest

class SimpleQAAutomation(unittest.TestCase):
    def test_example_logic(self):
        """這是一個基礎的 QA 自動化測試範例"""
        expected_status = "Success"
        actual_status = "Success"
        print(f"執行測試... 預期結果: {expected_status}, 實際結果: {actual_status}")
        self.assertEqual(expected_status, actual_status)

if __name__ == "__main__":
    unittest.main()
