---
phase: 01-scraper-schema
plan: 02
subsystem: auth
tags: [playwright, python, selenium-selector-discovery, auth-session, python-dotenv]

# Dependency graph
requires:
  - phase: 01-scraper-schema
    plan: 01
    provides: "uv project scaffolding, SQLite schema, seed functions — provides project foundation"
provides:
  - "auth.py: ensure_authenticated() + _do_login() with real confirmed CSS selectors"
  - "SELECTORS.md: documented CSS selectors for login (5 selectors), API docs (8 selectors), strategy pages"
  - "auth.json: Playwright storage state file from browser session"
  - "Discovery finding: JoinQuant requires phone number for web login; UUID credentials are JQData API keys"
affects:
  - 01-scraper-schema/03  # scraper/api_docs.py uses selectors from SELECTORS.md
  - 01-scraper-schema/04  # scraper/strategies.py uses auth module and strategy selectors
  - 02-mcp-server

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Playwright headed discovery: run headless=False to inspect live DOM before writing extraction code"
    - "Login gate: check agreementBox before submit — JoinQuant disables submit until checkbox checked"
    - "Session check: navigate to authenticated URL, check if redirected to login"
    - "auth.json save: context.storage_state(path=str(AUTH_FILE)) after successful login"

key-files:
  created:
    - "auth.py — ensure_authenticated(), _do_login() with confirmed selectors and session persistence"
    - ".planning/phases/01-scraper-schema/SELECTORS.md — full selector documentation for all page types"
  modified: []

key-decisions:
  - "JoinQuant web login requires Chinese mobile phone number, not UUID API credentials — two different auth systems"
  - "Agreement checkbox (#agreementBox) must be checked before submit button is enabled — required login flow step"
  - "API doc pages are public (no login required) — all 4 target sections served in single 635KB HTML file"
  - "Hash-based navigation: all API sections in one HTML file; h2 id attributes match URL hash anchors"
  - "Function block structure: h4-level for simple functions (p/pre/ul sibling pattern); article-level for complex functions (h5 sub-structure)"
  - "Strategy pages require valid session — selectors to be confirmed once valid credentials provided"

patterns-established:
  - "Login flow: goto login URL, wait for username field, check agreementBox, fill credentials, click submit, wait_for_url"
  - "API extraction: wait for h2 selector (SPA content ready), then parse h4 siblings or article children"
  - "Session validation: navigate to authenticated URL, check 'login' in page.url"

requirements-completed: []  # SCRP-01, SCRP-02 partially addressed in design; full validation blocked by credential format

# Metrics
duration: 12min
completed: 2026-03-22
---

# Phase 1 Plan 02: Discovery Spike and Auth Module Summary

**Playwright headed discovery confirming JoinQuant login form selectors, API doc page structure (single 635KB HTML, h2/h4/article hierarchy), and auth.py with session persistence — with documented finding that web login requires phone number, not UUID API credentials**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-03-22T11:35:00Z
- **Completed:** 2026-03-22T11:47:00Z
- **Tasks:** 1 complete (Task 2 is a human-verify checkpoint)
- **Files modified:** 2

## Accomplishments
- Ran 6 iterations of headed Playwright discovery against live JoinQuant pages to confirm real CSS selectors
- Discovered critical credential format issue: JoinQuant web login requires Chinese phone number, not UUID credentials
- Confirmed agreement checkbox (#agreementBox) must be checked before submit button is enabled
- Confirmed all 4 API doc target sections are public (no login required) and served in a single 635KB HTML file
- Mapped complete API doc page structure: h2/h3/h4 hierarchy for simple functions, `article` blocks for complex ones
- Built auth.py with all confirmed selectors (zero placeholders), session save/load, and fast-fail error messages
- Created SELECTORS.md documenting complete selector reference for login, API docs, and strategy pages

## Task Commits

1. **Task 1: Discovery spike and auth module** - `7e1451e` (feat)

## Files Created/Modified
- `auth.py` — Session management with `ensure_authenticated()`, `_do_login()`, confirmed selectors, #agreementBox handling
- `.planning/phases/01-scraper-schema/SELECTORS.md` — Complete selector documentation for login, API docs, strategy pages

## Decisions Made
- JoinQuant web login requires a Chinese mobile phone number as username. The `.env` credentials (`e8244388-...`) are JQData API keys for local data access, not web platform login credentials. The two auth systems are separate.
- Agreement checkbox (`#agreementBox`) must be `.check()`'d BEFORE clicking the submit button — JoinQuant's JS disables the button until checked. Previous plan assumptions did not account for this.
- API doc pages are public — this simplifies the scraper: 4 API sections can be scraped without login.
- The entire API doc page is one HTML file (635KB) with hash navigation — the scraper loads it once and extracts all 4 target sections from a single HTML document.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Login button disabled — agreement checkbox required**
- **Found during:** Task 1 (headed discovery spike — login attempt)
- **Issue:** The plan's login flow template did not include the agreement checkbox step. JoinQuant's `btnPwdSubmit` has `disabled="disabled"` until `#agreementBox` is checked.
- **Fix:** Added `page.query_selector('#agreementBox').check()` to `_do_login()` before filling credentials and clicking submit.
- **Files modified:** auth.py
- **Verification:** Checkbox selection confirmed via DOM inspection; submit button transitions from disabled to enabled.
- **Committed in:** 7e1451e

**2. [Rule 1 - Bug] Username input selector ambiguity**
- **Found during:** Task 1 (discovery spike iteration 1)
- **Issue:** `input[type="text"]` matched a hidden timestamp field (`class="timeStamp"`) before the visible username input, causing wait_for_selector timeout. The correct selector is `input[name="username"]`.
- **Fix:** Used `input[name="username"]` (confirmed from HTML dump) instead of the less specific `input[type="text"]`.
- **Files modified:** auth.py
- **Verification:** DOM inspection showed `input[name="username"]` uniquely selects the visible phone input with class `pwd-phone`.
- **Committed in:** 7e1451e

---

**Total deviations:** 2 auto-fixed (2 bugs in login flow)
**Impact on plan:** Both fixes necessary for correctness. No scope creep.

## Issues Encountered

**Credential format mismatch (not a code bug — a discovery finding):**
- JoinQuant requires a Chinese mobile phone number for web login
- The `.env` credentials (`JQ_USERNAME=e8244388-e273-4aec-a9ff-856943866238`) are JQData local data API keys
- Login validation returned: "输入的手机号码无效，请输入正确的手机号码" (Invalid mobile phone number)
- **Impact:** Login could not be completed; auth.json was saved with unauthenticated session cookies
- **Impact on plan:** API doc scraping unaffected (pages are public). Strategy page scraping blocked until valid phone-based credentials are provided.
- **Resolution path:** Human must provide JoinQuant web account credentials (phone + password) in `.env`

## User Setup Required

**Valid JoinQuant web login credentials are needed for strategy page scraping.**

Update `.env` with web platform credentials (phone number format):
```
JQ_USERNAME=13800000000   # Chinese mobile phone number registered on joinquant.com
JQ_PASSWORD=YourWebPassword
```

Note: The existing UUID credentials (`e8244388-e273-4aec-a9ff-856943866238`) are JQData API keys for local data access, not for web login. These are different auth systems.

**Verification:** After updating credentials, run:
```bash
uv run python -c "
from playwright.sync_api import sync_playwright
from auth import ensure_authenticated, AUTH_FILE
import os; os.remove('auth.json') if os.path.exists('auth.json') else None
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    ensure_authenticated(context)
    print('Login successful - auth.json saved')
    browser.close()
"
```

## Next Phase Readiness
- auth.py is complete with all confirmed selectors — ready for use by scraper modules once valid credentials provided
- API doc pages confirmed public — scraper/api_docs.py can be built immediately (Plan 03)
- Strategy scraping blocked on credentials — Plan 04 depends on this being resolved
- SELECTORS.md provides full selector reference for Plan 03 and Plan 04 implementation

---
*Phase: 01-scraper-schema*
*Completed: 2026-03-22*
