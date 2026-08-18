"""
auth.py — JoinQuant session management.

Provides:
  - ensure_authenticated(context): Load existing session or perform fresh login.
  - AUTH_FILE: Path to the Playwright storage state file (auth.json).

Usage:
    from auth import ensure_authenticated, AUTH_FILE
    ...
    context = browser.new_context(storage_state=str(AUTH_FILE) if AUTH_FILE.exists() else None)
    ensure_authenticated(context)

Credentials must be set in .env:
    JQ_USERNAME=<JoinQuant phone number>
    JQ_PASSWORD=<JoinQuant password>

Note: JoinQuant login requires a Chinese mobile phone number as the username.
      UUID-format usernames are not accepted.
"""
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import BrowserContext

load_dotenv()

AUTH_FILE = Path("auth.json")

# --- Confirmed selectors from headed discovery spike (2026-03-22) ---
_LOGIN_URL = "https://www.joinquant.com/user/login/index"
_SESSION_CHECK_URL = "https://www.joinquant.com/algorithm/index/list"

# Login form selectors (confirmed from HTML inspection)
_USERNAME_SEL = 'input[name="username"]'          # Phone number input (type=text)
_PASSWORD_SEL = 'input[name="pwd"]'               # Password input (type=password)
_AGREEMENT_SEL = "#agreementBox"                   # Agreement checkbox (must be checked first)
_SUBMIT_SEL = ".login-submit.btnPwdSubmit"         # Login button (disabled until checkbox checked)

# Session validity indicator: this element only appears on the login page
# If we navigate to an authenticated URL and get redirected back to login,
# this selector will be visible — confirming the session is expired/absent.
_LOGIN_INDICATOR_SEL = ".pwd-phone"               # Username input on login page


def ensure_authenticated(context: BrowserContext) -> None:
    """Load existing session or perform fresh login. Saves auth.json on success.

    On the first call (no auth.json): opens login page, fills credentials, saves state.
    On subsequent calls (auth.json exists and session valid): returns immediately.
    On subsequent calls (auth.json exists but session expired): re-authenticates.
    """
    page = context.new_page()
    try:
        # Navigate to an authenticated endpoint to test session validity
        page.goto(_SESSION_CHECK_URL, timeout=15000, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")

        # If redirected to login page, session is invalid (expired or absent)
        if "login" in page.url or page.query_selector(_LOGIN_INDICATOR_SEL) is not None:
            _do_login(page)
            context.storage_state(path=str(AUTH_FILE))
        # else: session valid — auth.json already loaded, no login needed
    finally:
        page.close()


def _do_login(page) -> None:
    """Fill and submit JoinQuant login form. Fails fast on error.

    IMPORTANT: JoinQuant requires a Chinese mobile phone number as the username.
    UUID-format usernames (e.g., e8244388-e273-4aec-a9ff-856943866238) will be
    rejected with "输入的手机号码无效" (invalid phone number).

    Raises:
        RuntimeError: If JQ_USERNAME or JQ_PASSWORD is not set in .env.
        RuntimeError: If login fails (wrong credentials, CAPTCHA, etc.).
    """
    username = os.environ.get("JQ_USERNAME")
    password = os.environ.get("JQ_PASSWORD")
    if not username or not password:
        raise RuntimeError("JQ_USERNAME and JQ_PASSWORD must be set in .env")

    page.goto(_LOGIN_URL, timeout=15000, wait_until="domcontentloaded")
    page.wait_for_selector(_USERNAME_SEL, timeout=10000)

    # The submit button is disabled until the agreement checkbox is checked
    agreement = page.query_selector(_AGREEMENT_SEL)
    if agreement and not agreement.is_checked():
        agreement.check()
        time.sleep(0.3)

    page.fill(_USERNAME_SEL, username)
    time.sleep(0.2)
    page.fill(_PASSWORD_SEL, password)
    time.sleep(0.3)

    page.click(_SUBMIT_SEL)

    # Wait for navigation away from login page (indicates success)
    try:
        page.wait_for_url(lambda url: "login" not in url, timeout=30000)
    except Exception:
        # Check for visible error message
        error_el = page.query_selector(".phone-tip")
        if error_el and error_el.is_visible():
            error_text = error_el.inner_text()
            raise RuntimeError(f"JoinQuant login failed: {error_text}")
        raise RuntimeError(
            f"JoinQuant login failed: still on {page.url} after 30s. "
            "Check credentials and whether a CAPTCHA appeared."
        )
