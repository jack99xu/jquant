"""
scraper/strategies.py — JoinQuant 策略与应用 scraper.

Extracts strategy articles from the 量化课堂 (study) page under the
"策略与应用" section. Each article is a community post containing strategy
description text and Python code blocks.

Exports:
    scrape_all_strategies(context) -> list[dict]

The study page at /study uses `_href` attributes (not standard `href`) for
article links. Strategy articles have `m=algorithm` in their URL params.
Articles redirect from /post/{id} to /view/community/detail/{id}.

Per user decisions (01-CONTEXT.md):
- 2-3 second polite delay between page navigations
- Store partial data on failure (never skip a strategy)
- Warn (not crash) on single strategy extraction failure
"""
import time
import random

from playwright.sync_api import BrowserContext
from rich import print as rprint

# ---------------------------------------------------------------------------
# URLs
# ---------------------------------------------------------------------------

_STUDY_URL = "https://www.joinquant.com/study"
_BASE_URL = "https://www.joinquant.com"


def scrape_all_strategies(context: BrowserContext) -> list[dict]:
    """Scrape all strategy articles from the 策略与应用 section.

    Returns a list of strategy record dicts with keys:
        name, category, code_content, description
    """
    page = context.new_page()
    records = []
    try:
        rprint("[bold]Navigating to study page...[/bold]")
        page.goto(_STUDY_URL, timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)

        if "login" in page.url:
            rprint(
                "[bold red]WARNING: Redirected to login page — session not authenticated. "
                "Strategy scraping requires valid session. Run: uv run python gen_auth.py[/bold red]"
            )
            return []

        # Collect strategy article links from the study page.
        # JoinQuant uses _href attributes (not standard href) for post links.
        # Strategy articles have m=algorithm in their URL params.
        strategy_links = _collect_strategy_links(page)
        rprint(f"Found {len(strategy_links)} strategy articles")

        if not strategy_links:
            rprint(
                "[bold yellow]WARNING: 0 strategy links found on study page. "
                "Page structure may have changed.[/bold yellow]"
            )
            return []

        for link_info in strategy_links:
            time.sleep(random.uniform(2.0, 3.0))
            record = _extract_strategy(page, link_info)
            if record:
                records.append(record)
                rprint(f"  Extracted: {record['name'][:50]} ({record['category']})")

    except Exception as e:
        rprint(f"[bold red]ERROR: Strategy scraping failed: {e}[/bold red]")
    finally:
        page.close()

    return records


def _collect_strategy_links(page) -> list[dict]:
    """Collect all strategy article links from the study page.

    Strategy links use _href attribute with m=algorithm parameter.
    They appear in the '策略与应用' session section and also in carousels.
    We deduplicate by post ID.
    """
    links = page.query_selector_all('[_href*="m=algorithm"]')
    seen_ids = set()
    results = []

    for link in links:
        href = link.get_attribute("_href") or ""
        text = link.inner_text().strip()
        if not href or not text:
            continue

        # Extract post ID from href like /post/{id}?f=stydy&m=algorithm
        post_id = href.split("/post/")[-1].split("?")[0] if "/post/" in href else href
        if post_id in seen_ids:
            continue
        seen_ids.add(post_id)

        # Determine category from parent session container
        category = link.evaluate(
            'el => { '
            'let s = el.closest(".session"); '
            'if (s) { let t = s.querySelector(".s-title"); return t ? t.innerText.trim() : "策略与应用"; } '
            'return "策略与应用"; '
            '}'
        )

        results.append({
            "name": text,
            "href": href,
            "category": category,
        })

    return results


def _extract_strategy(page, link_info: dict) -> dict | None:
    """Navigate to a strategy article and extract its content.

    Articles are at /post/{id} which redirects to /view/community/detail/{id}.
    Content includes description text and Python code in <pre> blocks.
    """
    name = link_info.get("name", "unknown")
    href = link_info.get("href", "")
    category = link_info.get("category", "策略与应用")

    try:
        full_url = href if href.startswith("http") else f"{_BASE_URL}{href}"
        page.goto(full_url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(2)

        # Extract the article title (may differ from link text)
        title_el = page.query_selector("h1")
        if title_el:
            title_text = title_el.inner_text().strip()
            if title_text:
                name = title_text

        # Extract code content from all <pre> blocks
        code_content = _extract_code(page)

        # Extract description from the article body
        description = _extract_description(page)

        return {
            "name": name,
            "category": category,
            "code_content": code_content,
            "description": description,
        }

    except Exception as e:
        rprint(f"  [yellow]WARNING: Failed to extract strategy '{name}': {e}[/yellow]")
        return {
            "name": name,
            "category": category,
            "code_content": "",
            "description": None,
        }


def _extract_code(page) -> str:
    """Extract all Python code blocks from the article page.

    Concatenates all <pre> blocks that contain Python-like code,
    skipping metadata/copyright blocks.
    """
    pre_elements = page.query_selector_all("pre")
    code_blocks = []

    for pre in pre_elements:
        try:
            text = pre.inner_text().strip()
            if not text:
                continue
            # Skip short metadata/copyright blocks
            if len(text) < 20:
                continue
            # Skip blocks that are clearly not code (copyright notices, author info)
            if text.startswith("本文由") and "版权" in text:
                continue
            code_blocks.append(text)
        except Exception:
            continue

    return "\n\n".join(code_blocks) if code_blocks else ""


def _extract_description(page) -> str | None:
    """Extract the article description/body text.

    Gets the full article text content, excluding code blocks and navigation.
    Uses the main content container on the community detail page.
    """
    # Try common article body selectors
    for sel in [".jq-m-community__content", ".detail-body", ".article-content", ".post-content"]:
        el = page.query_selector(sel)
        if el:
            text = el.inner_text().strip()
            if text and len(text) > 20:
                # Truncate very long descriptions to first ~2000 chars
                return text[:2000] if len(text) > 2000 else text

    # Fallback: get text between h1 and first pre block
    try:
        body_text = page.evaluate('''() => {
            const h1 = document.querySelector('h1');
            if (!h1) return null;
            let text = '';
            let node = h1.parentElement;
            if (!node) return null;
            const children = node.children;
            let collecting = false;
            for (const child of children) {
                if (child === h1) { collecting = true; continue; }
                if (collecting && child.tagName === 'PRE') break;
                if (collecting) text += child.innerText + '\\n';
            }
            return text.trim() || null;
        }''')
        if body_text and len(body_text) > 20:
            return body_text[:2000]
    except Exception:
        pass

    return None
