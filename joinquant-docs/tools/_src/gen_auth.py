"""
gen_auth.py — Interactive login helper to generate auth.json.

Run this script to open a browser window where you can solve the CAPTCHA
manually. Once logged in, the session will be saved to auth.json.

Usage:
    uv run python gen_auth.py

After the browser closes (or you press Enter), auth.json will contain
the authenticated session cookies.
"""
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
import time

load_dotenv()
username = os.environ.get("JQ_USERNAME")
password = os.environ.get("JQ_PASSWORD")

print("=" * 60)
print("JoinQuant Interactive Login Helper")
print("=" * 60)
print(f"Username: {username}")
print()
print("This will open a browser window. You will need to:")
print("  1. Solve the jigsaw CAPTCHA (slide the puzzle piece)")
print("  2. Wait for login to complete")
print()
print("The session will be saved to auth.json automatically.")
print("=" * 60)
print()

with sync_playwright() as p:
    # Launch in HEADED mode so user can see and interact
    browser = p.chromium.launch(
        headless=False,
        slow_mo=100,
        args=["--window-size=1000,700"]
    )

    context = browser.new_context(
        viewport={"width": 1000, "height": 700},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )

    page = context.new_page()
    print("Opening browser...")
    page.goto("https://www.joinquant.com/user/login/index", timeout=30000, wait_until="domcontentloaded")
    time.sleep(1)

    # Pre-fill the form to help the user
    agreement = page.query_selector("#agreementBox")
    if agreement and not agreement.is_checked():
        agreement.check()
        time.sleep(0.3)

    page.fill('input[name="username"]', username)
    time.sleep(0.2)
    page.fill('input[name="pwd"]', password)
    time.sleep(0.2)

    print("Form pre-filled with your credentials.")
    print("Please solve the CAPTCHA in the browser window, then click Login.")
    print()
    print("Waiting for login to complete (up to 2 minutes)...")

    try:
        # Wait for navigation away from login page (up to 2 minutes)
        page.wait_for_url(lambda url: "login" not in url, timeout=120000)
        print(f"\nLOGIN SUCCESSFUL! Now on: {page.url}")

        # Save the session
        context.storage_state(path="auth.json")
        print("Session saved to auth.json")
        print()
        print("You can now run: uv run python run_scrape.py")

    except Exception as e:
        print(f"\nLogin timed out or failed: {e}")
        print("Please try again.")
    finally:
        print("Closing browser...")
        browser.close()
