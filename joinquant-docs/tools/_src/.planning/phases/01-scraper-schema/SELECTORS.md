# JoinQuant CSS Selectors Discovery

**Discovered:** 2026-03-22
**Method:** Headed Playwright discovery spike + HTML inspection via BeautifulSoup
**Confidence:** HIGH — confirmed by live page inspection with `page.query_selector_all()` and HTML dump

---

## 1. Login Page

**URL:** `https://www.joinquant.com/user/login/index`

### Confirmed Selectors

| Element | Selector | Notes |
|---------|----------|-------|
| Username input | `input[name="username"]` | type=text, placeholder="手机号". MUST be a Chinese mobile phone number. UUID credentials are rejected. |
| Password input | `input[name="pwd"]` | type=password, placeholder="请输入密码" |
| Agreement checkbox | `#agreementBox` | Must be `.check()`'d BEFORE clicking submit — button is `disabled` until checked |
| Login submit button | `.login-submit.btnPwdSubmit` | Has attribute `disabled="disabled"` until agreementBox is checked. Text: "登　　录" |
| Login form container | `.formPwdLogin` | Wraps username, password, and submit |
| Login tab (active) | `ul.tab-nav li.active` | "密码登录" tab is active by default (index 1). Index 0 is SMS code login. |
| Error message | `.phone-tip` | Shows validation errors; check `.is_visible()` before reading text |

### Login Flow (Required Order)

1. `page.goto("https://www.joinquant.com/user/login/index")`
2. `page.wait_for_selector('input[name="username"]', timeout=10000)`
3. `page.query_selector('#agreementBox').check()` — enables the submit button
4. `page.fill('input[name="username"]', phone_number)` — must be phone number format
5. `page.fill('input[name="pwd"]', password)`
6. `page.click('.login-submit.btnPwdSubmit')`
7. `page.wait_for_url(lambda url: "login" not in url, timeout=30000)`

### Session Check Selector

To verify if a session is still valid after loading auth.json:
- Navigate to `https://www.joinquant.com/algorithm/index/list`
- If redirected to login, session is expired. Check: `"login" in page.url`
- Alternative: check for `.pwd-phone` visible on the page (login form indicator)

### CRITICAL: Credential Format

**JoinQuant requires a Chinese mobile phone number (e.g., 138xxxxxxxx) as the username.**
UUID-format strings (e.g., `e8244388-e273-4aec-a9ff-856943866238`) are rejected with:
`"输入的手机号码无效，请输入正确的手机号码"` (Invalid phone number)

The `.env` credentials `JQ_USERNAME=e8244388-e273-4aec-a9ff-856943866238` are **JQData API credentials**, not web login credentials. Web scraping requires separate JoinQuant account credentials (phone + password).

---

## 2. API Documentation Pages

**Base URL:** `https://www.joinquant.com/help/api/help`
**Navigation:** Hash-based (`#Stock:获取股票数据`, etc.)
**Access:** Public (no login required)
**Key finding:** All 4 target sections are served in a single 635KB HTML file. Hash navigation scrolls to the correct section.

### Page Structure

```
<div class="jq-l-help-api">        <!-- Left sidebar navigation -->
  <a href="#获取股票数据">...</a>    <!-- Section links -->
  ...
</div>
<div>                               <!-- Main content (no class) -->
  <h2 id="获取股票数据">...</h2>    <!-- Section heading -->
  <h3 id="获取股票概况">...</h3>    <!-- Subsection heading -->
  <h4 id="获取单支股票数据">...</h4> <!-- Function group heading -->
  <p>description</p>
  <p>调用方法</p>
  <pre>function_name(params)</pre>  <!-- Call signature -->
  <p>参数</p>
  <ul>param list</ul>
  <p>返回值</p>
  <ul>return value list</ul>/<ol>
  <p>示例</p>
  <pre>example code</pre>
  <article>                         <!-- Complex function blocks -->
    <pre>function_name(params)</pre>
    <h5>参数</h5>
    <ul>...</ul>
    <h5>返回值</h5>
    <p>...</p>
    <h5>示例</h5>
    <pre>example code</pre>
  </article>
</div>
```

### Selectors for Content Extraction

| Element | Selector | Count | Notes |
|---------|----------|-------|-------|
| Left sidebar nav | `.jq-l-help-api` | 1 | Contains all section/function links |
| Section heading (h2) | `h2` | 12 | IDs match URL hash anchors |
| Subsection heading (h3) | `h3` | 42 | Category groupings |
| Function group heading (h4) | `h4` | 16 | Function-level headings (simple functions) |
| Complex function blocks | `article` | 4 | For complex functions with h5 sub-structure |
| Code examples | `pre` | 115 | Both call signatures and example code |
| Parameter tables | `table` | 72 | Used for return value tables in some sections |
| Description paragraphs | `p` | 447 | Contains "调用方法", "参数", "返回值", "示例" markers |

### Target Section IDs (hash anchors)

| Target Section | URL Hash | H2 id attribute |
|----------------|----------|-----------------|
| 获取股票数据 | `#Stock:获取股票数据` | `获取股票数据` |
| 获取单季度/年度财务数据 | `#Stock:获取单季度年度财务数据` | `获取单季度年度财务数据` |
| 上市公司概况 | `#Stock:上市公司概况` | `上市公司概况` |
| 获取融资融券标的列表 | `#Stock:获取融资融券标的列表` | `获取融资融券标的列表` |

### Function Block Extraction Pattern (Simple — h4 level)

```python
# For functions under h4 headings (most functions)
h4 = soup.find('h4', id='获取单支股票数据')
# siblings: p(desc), p("调用方法"), pre(sig), p("参数"), ul(params), p("返回值"), ul/ol(returns), p("示例"), pre(example)
el = h4
siblings = []
while True:
    el = el.find_next_sibling()
    if el is None or el.name in ['h2', 'h3', 'h4']:
        break
    siblings.append(el)

# Extract by label text
call_sig = next((s.get_text() for s in siblings if s.name == 'pre'), None)
# "参数" paragraph precedes the ul of params
# "示例" paragraph precedes the example pre
```

### Function Block Extraction Pattern (Complex — article level)

```python
# For article elements (get_fundamentals, get_fundamentals_continuously, etc.)
for article in soup.find_all('article'):
    # First pre = call signature
    sig = article.find('pre')

    # h5 elements mark sections: 参数, 返回值, 注意, 示例
    sections = {}
    current_h5 = None
    for child in article.children:
        if hasattr(child, 'name'):
            if child.name == 'h5':
                current_h5 = child.get_text(strip=True)
            elif current_h5:
                sections.setdefault(current_h5, []).append(child)

    params_ul = sections.get('参数', [None])[0]
    return_p = sections.get('返回值', [None])[0]
    example_pre = sections.get('示例', [None])[0]  # h5 text includes code
```

### Proof of Content Loading

After `page.goto(url)`, wait for content to appear:
```python
page.wait_for_selector('h2', timeout=20000)  # h2 appears once content loads
```
Alternative: `page.wait_for_selector('pre', timeout=20000)` — pre elements contain code snippets

---

## 3. Strategy Pages

**URL:** `https://www.joinquant.com/algorithm/study/index`
**Access:** Requires valid login session (redirects to login without auth)

### Access Status

Direct URL navigation to `/algorithm/study/index` returns **HTTP 404** without login.
URL `/algorithm/index/list` redirects to login: `https://www.joinquant.com/user/login/index?redirect=%2Falgorithm%2Findex%2Flist`

**Login required for strategy pages.** Since web login requires a phone number (which the current credentials don't satisfy), strategy page selectors could not be confirmed during this discovery spike.

### Inferred Selectors (from nav HTML on unauthenticated pages)

From the JoinQuant nav bar HTML, the strategy section is at:
- `/algorithm/index/list` (strategy list)
- `/algorithm/study/index` (classic strategy study)

```html
<a href="/algorithm/index/list" class="item">策略回测</a>
```

### Required for Future Discovery (Post-Login)

Once valid login credentials are available, navigate to:
1. `https://www.joinquant.com/algorithm/study/index` (after login)
2. Inspect `.sidebar`, `aside`, `.left-panel`, `[class*="nav"]` for category list
3. Find strategy name links and strategy code area selectors
4. Strategy URL pattern: likely `/algorithm/study/detail?id=<N>` or similar

---

## Summary: Extraction-Ready Selectors

### Auth Module (auth.py)

```python
_LOGIN_URL = "https://www.joinquant.com/user/login/index"
_SESSION_CHECK_URL = "https://www.joinquant.com/algorithm/index/list"
_USERNAME_SEL = 'input[name="username"]'   # Phone number, NOT UUID
_PASSWORD_SEL = 'input[name="pwd"]'
_AGREEMENT_SEL = "#agreementBox"            # Must check before submit
_SUBMIT_SEL = ".login-submit.btnPwdSubmit"
_LOGIN_INDICATOR_SEL = ".pwd-phone"         # Visible only on login page
```

### API Doc Scraper (scraper/api_docs.py)

```python
# Page load confirmation
CONTENT_READY_SEL = "h2"                    # Appears once SPA renders

# Section navigation
SECTION_H2_SEL = "h2"                       # id= attribute matches target
FUNCTION_H4_SEL = "h4"                      # Simple function group headings
FUNCTION_ARTICLE_SEL = "article"            # Complex function blocks

# Content within function blocks
CODE_SEL = "pre"                            # Both signatures and examples
PARAM_LIST_SEL = "ul"                       # Parameter lists (after "参数" p)
RETURN_LIST_SEL = "ul, ol"                  # Return value lists
SECTION_MARKERS = ["调用方法", "参数", "返回值", "示例"]  # p text labels
H5_MARKERS = ["参数", "返回值", "注意", "示例"]           # article-level markers
```

---

*Discovered: 2026-03-22*
*Method: Playwright headed browser + HTML analysis*
*Pages inspected: login form, 4 API doc sections (single HTML file), strategy page (unauthenticated)*
