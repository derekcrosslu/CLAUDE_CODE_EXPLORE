#!/usr/bin/env python3
"""
Test Monte Carlo notebook in local LEAN environment using Playwright
"""

from playwright.sync_api import sync_playwright
import time
import sys

def test_lean_notebook():
    """Test QuantConnect imports in LEAN Jupyter Lab"""

    print("="*60)
    print("TESTING MONTE CARLO NOTEBOOK IN LOCAL LEAN")
    print("="*60)

    with sync_playwright() as p:
        # Launch browser
        print("\n1. Launching Chromium browser...")
        browser = p.chromium.launch(headless=False)  # Set to False to see what's happening
        context = browser.new_context()
        page = context.new_page()

        # Navigate to Jupyter Lab
        print("2. Navigating to Jupyter Lab (http://127.0.0.1:8888/lab)...")
        page.goto("http://127.0.0.1:8888/lab")

        # Wait for Jupyter Lab to load
        print("3. Waiting for Jupyter Lab interface to load...")
        time.sleep(5)

        # Look for the research.ipynb file in the file browser
        print("4. Looking for research.ipynb in file browser...")
        try:
            # DOUBLE-CLICK to open (single click just selects)
            # Use more specific selector to target file browser, not running sessions
            print("   Attempting double-click to open notebook...")
            page.locator('.jp-DirListing-content').locator('text=research.ipynb').dblclick(timeout=10000)
            print("   ✅ Double-clicked research.ipynb")
            time.sleep(5)

            # Verify notebook actually opened by checking for cells
            page.screenshot(path="after_open.png")
            if page.locator('.jp-Cell').count() > 0:
                print("   ✅ Notebook opened successfully - cells visible")
            else:
                print("   ⚠️  No cells found - may still be loading")
                time.sleep(3)

        except Exception as e:
            print(f"   ❌ Could not open research.ipynb: {e}")
            page.screenshot(path="open_failed.png")
            browser.close()
            return False

        # Execute the first cell (imports)
        print("5. Executing Cell 1 (QuantConnect imports)...")
        try:
            # Click on first cell to select it
            print("   Clicking first cell...")
            first_cell = page.locator('.jp-Cell').first
            first_cell.click()
            time.sleep(1)

            # Execute using Shift+Enter
            print("   Pressing Shift+Enter to execute...")
            page.keyboard.press('Shift+Enter')
            print("   ✅ Cell 1 execution started")

            # Wait for execution to complete
            print("7. Waiting for cell execution to complete...")
            time.sleep(5)

            # Check for output
            print("8. Checking cell output...")

            # Look for success indicators
            page_content = page.content()

            if "QuantConnect Research environment initialized" in page_content:
                print("\n" + "="*60)
                print("✅ SUCCESS: QuantConnect imports worked!")
                print("="*60)
                print("   Cell output found: 'QuantConnect Research environment initialized'")
                success = True
            elif "ModuleNotFoundError" in page_content or "ImportError" in page_content:
                print("\n" + "="*60)
                print("❌ FAILED: Import error detected")
                print("="*60)
                success = False
            else:
                print("\n" + "="*60)
                print("⚠️  UNCLEAR: Could not determine success/failure")
                print("="*60)
                print("   Taking screenshot for manual review...")
                page.screenshot(path="jupyter_test_screenshot.png")
                print("   Screenshot saved: jupyter_test_screenshot.png")
                success = None

            # Take a screenshot regardless
            print("\n9. Taking final screenshot...")
            page.screenshot(path="jupyter_final_state.png")
            print("   Screenshot saved: jupyter_final_state.png")

        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            page.screenshot(path="jupyter_error_screenshot.png")
            print("   Error screenshot saved: jupyter_error_screenshot.png")
            success = False

        # Keep browser open for 5 seconds to see result
        print("\n10. Keeping browser open for 5 seconds...")
        time.sleep(5)

        # Close browser
        print("11. Closing browser...")
        browser.close()

        return success

if __name__ == "__main__":
    print("\nStarting LEAN notebook test with Playwright...")
    print("Browser will open automatically (set headless=True to hide)")
    print()

    result = test_lean_notebook()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

    if result is True:
        print("✅ Result: SUCCESS - QuantConnect imports work in local LEAN")
        sys.exit(0)
    elif result is False:
        print("❌ Result: FAILED - QuantConnect imports failed")
        sys.exit(1)
    else:
        print("⚠️  Result: UNCLEAR - Check screenshots manually")
        sys.exit(2)
