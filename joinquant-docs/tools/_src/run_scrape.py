#!/usr/bin/env python3
"""JoinQuant Knowledge Base Scraper — Full ingestion pipeline.

Orchestrates the complete data ingestion pipeline:
  1. Initialize SQLite database (creates jq_knowledge.db if not exists)
  2. Launch Playwright browser (headless), load auth.json session if available
  3. Ensure authenticated session (login if needed, re-use saved session if valid)
  4. Scrape API documentation from 4 target pages (public, no login required)
  5. Upsert all API doc records, params, and return attributes
  6. Scrape classic strategies from 经典策略学习 sidebar (requires login)
  7. Upsert all strategy records
  8. Print row count summary for all 4 tables
  9. Warn if any table has 0 rows (sanity check)

Usage:
    uv run python run_scrape.py

Requirements:
    - .env file with JQ_USERNAME and JQ_PASSWORD (phone number format for web login)
    - Playwright Chromium browser installed: uv run playwright install chromium

Note on strategy scraping:
    JoinQuant web login requires a Chinese mobile phone number (e.g., 138xxxxxxxx).
    UUID-format credentials (JQData API keys) will fail web login.
    API documentation scraping is public and does not require login.
"""

import sqlite3
from pathlib import Path
from playwright.sync_api import sync_playwright
from rich import print as rprint
from rich.console import Console

from auth import ensure_authenticated, AUTH_FILE
from scraper.api_docs import scrape_all_api_sections
from scraper.strategies import scrape_all_strategies
from db.schema import init_db
from db.seed import upsert_api_doc, upsert_api_params, upsert_api_return_attrs, upsert_table_columns, upsert_strategy

DB_FILE = Path("jq_knowledge.db")
console = Console()


def count_rows(conn: sqlite3.Connection, table: str) -> int:
    """Return the number of rows in the given table."""
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def main():
    rprint("[bold blue]JoinQuant Knowledge Base Scraper[/bold blue]")
    rprint(f"Database: {DB_FILE}")

    # Step 1: Initialize database (creates file + schema if not exists)
    conn = init_db(DB_FILE)
    rprint("[green]Database initialized[/green]")

    with sync_playwright() as p:
        # Step 2: Launch browser (headless), load saved session if available
        storage = str(AUTH_FILE) if AUTH_FILE.exists() else None
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage)

        # Step 3: Ensure authenticated session (login if needed)
        # If auth fails due to CAPTCHA or invalid credentials, API doc scraping
        # continues (public pages) but strategy scraping is skipped.
        rprint("Checking authentication...")
        auth_ok = False
        try:
            ensure_authenticated(context)
            auth_ok = True
            rprint("[green]Authenticated[/green]")
        except RuntimeError as e:
            rprint(
                f"[bold yellow]WARNING: Authentication failed: {e}[/bold yellow]\n"
                "[yellow]Strategy scraping will be skipped. API doc scraping will continue.\n"
                "To enable strategy scraping, run: uv run python gen_auth.py[/yellow]"
            )

        # Step 4: Scrape API documentation (all sections, public pages)
        rprint("\n[bold]Scraping API documentation...[/bold]")
        api_records, table_column_records = scrape_all_api_sections(context)
        rprint(f"Extracted {len(api_records)} API functions")
        rprint(f"Extracted {len(table_column_records)} table column definitions")

        # Step 5: Upsert API docs + params + return attrs
        for record in api_records:
            upsert_api_doc(conn, {
                "function_name": record["function_name"],
                "chinese_name": record.get("chinese_name"),
                "section": record["section"],
                "call_signature": record.get("call_signature"),
                "description": record.get("description"),
                "return_type": record.get("return_type"),
                "example_code": record.get("example_code"),
            })
            if record.get("params"):
                upsert_api_params(conn, record["function_name"], record["params"])
            if record.get("return_attrs"):
                upsert_api_return_attrs(conn, record["function_name"], record["return_attrs"])

        # Step 5b: Upsert table column definitions
        for tc in table_column_records:
            upsert_table_columns(conn, tc["table_name"], tc["columns"])

        # Step 6: Scrape classic strategies (requires authenticated session)
        strategy_records = []
        if auth_ok:
            rprint("\n[bold]Scraping classic strategies...[/bold]")
            strategy_records = scrape_all_strategies(context)
            rprint(f"Extracted {len(strategy_records)} strategies")
        else:
            rprint(
                "\n[yellow]Skipping strategy scraping (no authenticated session).[/yellow]"
            )

        # Step 7: Upsert strategy records
        for record in strategy_records:
            upsert_strategy(conn, record)

        browser.close()

    # Step 8: Print summary
    rprint("\n[bold green]Scraping complete![/bold green]")
    rprint(f"  api_docs:         {count_rows(conn, 'api_docs')} rows")
    rprint(f"  api_params:       {count_rows(conn, 'api_params')} rows")
    rprint(f"  api_return_attrs: {count_rows(conn, 'api_return_attrs')} rows")
    rprint(f"  table_columns:    {count_rows(conn, 'table_columns')} rows")
    rprint(f"  strategies:       {count_rows(conn, 'strategies')} rows")

    # Step 9: Sanity checks — warn if any core table is empty
    for table in ["api_docs", "strategies"]:
        if count_rows(conn, table) == 0:
            rprint(
                f"[bold red]WARNING: {table} has 0 rows -- something went wrong![/bold red]"
            )

    conn.close()


if __name__ == "__main__":
    main()
