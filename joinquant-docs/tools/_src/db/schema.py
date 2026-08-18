import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS api_docs (
    function_name   TEXT PRIMARY KEY,
    chinese_name    TEXT,
    section         TEXT NOT NULL,
    call_signature  TEXT,
    description     TEXT,
    return_type     TEXT,
    example_code    TEXT,
    scraped_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS api_params (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name   TEXT NOT NULL REFERENCES api_docs(function_name) ON DELETE CASCADE,
    param_name      TEXT NOT NULL,
    param_type      TEXT,
    description     TEXT,
    is_required     INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS api_return_attrs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name   TEXT NOT NULL REFERENCES api_docs(function_name) ON DELETE CASCADE,
    attr_name       TEXT NOT NULL,
    attr_type       TEXT,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS strategies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,
    description     TEXT,
    code_content    TEXT NOT NULL,
    scraped_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(name, category)
);

CREATE TABLE IF NOT EXISTS table_columns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name      TEXT NOT NULL,
    column_name     TEXT NOT NULL,
    column_type     TEXT,
    meaning         TEXT,
    description     TEXT,
    UNIQUE(table_name, column_name)
);

CREATE INDEX IF NOT EXISTS idx_api_docs_section ON api_docs(section);
CREATE INDEX IF NOT EXISTS idx_strategies_category ON strategies(category);
CREATE INDEX IF NOT EXISTS idx_api_params_function ON api_params(function_name);
CREATE INDEX IF NOT EXISTS idx_api_return_function ON api_return_attrs(function_name);
CREATE INDEX IF NOT EXISTS idx_table_columns_table ON table_columns(table_name);
"""


def init_db(db_path_or_conn):
    """Initialize database. Accepts a Path (creates file DB) or an existing connection (for testing)."""
    if isinstance(db_path_or_conn, (str, Path)):
        conn = sqlite3.connect(str(db_path_or_conn))
    else:
        conn = db_path_or_conn
    conn.executescript(SCHEMA_SQL)
    return conn
