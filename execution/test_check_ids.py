import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
import accessibility_ids as ids

def test_check_accessibility_ids(driver):
    """
    Checking existence of Accessibility IDs for the first two steps.
    """
    print("\n🔍 Accessibility ID Inspection starting...")
    
    # Check Tab Bar "+"
    try:
        add_tab = driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.TabBarController.addTab)
        print(f"✅ Found Tab Bar '+' with ID: {ids.TabBarController.addTab}")
        add_tab.click()
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed to find Tab Bar '+' with ID: {ids.TabBarController.addTab}. Error: {str(e)[:50]}")
        pytest.fail("Cannot continue without Tab Bar '+'")

    # Check "發布文章"
    try:
        pure_post = driver.find_element(AppiumBy.ACCESSIBILITY_ID, ids.AddViewController.purePostView)
        print(f"✅ Found '發布文章' with ID: {ids.AddViewController.purePostView}")
        pure_post.click()
        time.sleep(2)
    except Exception as e:
        print(f"❌ Failed to find '發布文章' with ID: {ids.AddViewController.purePostView}. Error: {str(e)[:50]}")
        pytest.fail("Cannot continue without Pure Post view")

    # Now on the Pure Post page. Let's dump the hierarchy to answer user's question 1 & 2.
    source = driver.page_source
    with open("/tmp/pure_post_page.xml", "w", encoding="utf-8") as f:
        f.write(source)
    print(f"📊 Dumped UI tree to /tmp/pure_post_page.xml")
    
    # Check common elements on this page
    elements_to_check = [
        ("Title Box", ids.ModifyPurePostPrimaryView.titleView),
        ("Photo Add Button", ids.ModifyLogPhotoAddCollectionViewCell.dashedAddView),
        ("Dive Point Button", ids.ModifyLogSection2View.spotView),
        ("Partner Button", ids.ModifyLogSection2View.partnerView),
        ("Submit Button", ids.ModifyPurePostViewController.postButton)
    ]
    
    for name, aid in elements_to_check:
        try:
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, aid)
            print(f"✅ Found {name} with ID: {aid}")
        except:
            print(f"⚠️ Missing {name} with ID: {aid}")
