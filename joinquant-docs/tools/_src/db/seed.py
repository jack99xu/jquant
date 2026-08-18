import sqlite3


def upsert_api_doc(conn: sqlite3.Connection, record: dict) -> None:
    """Insert or update an API doc record keyed on function_name."""
    conn.execute(
        """
        INSERT INTO api_docs (function_name, chinese_name, section, call_signature, description, return_type, example_code)
        VALUES (:function_name, :chinese_name, :section, :call_signature, :description, :return_type, :example_code)
        ON CONFLICT(function_name) DO UPDATE SET
            chinese_name = COALESCE(excluded.chinese_name, api_docs.chinese_name),
            section = excluded.section,
            call_signature = excluded.call_signature,
            description = excluded.description,
            return_type = excluded.return_type,
            example_code = excluded.example_code,
            scraped_at = datetime('now')
        """,
        record,
    )
    conn.commit()


def upsert_api_params(conn: sqlite3.Connection, function_name: str, params: list[dict]) -> None:
    """Replace all params for a function (delete + insert pattern for idempotency)."""
    conn.execute("DELETE FROM api_params WHERE function_name = ?", (function_name,))
    for p in params:
        conn.execute(
            """
            INSERT INTO api_params (function_name, param_name, param_type, description, is_required)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                function_name,
                p["param_name"],
                p.get("param_type"),
                p.get("description"),
                p.get("is_required", 1),
            ),
        )
    conn.commit()


def upsert_api_return_attrs(conn: sqlite3.Connection, function_name: str, attrs: list[dict]) -> None:
    """Replace all return attributes for a function (delete + insert pattern for idempotency)."""
    conn.execute("DELETE FROM api_return_attrs WHERE function_name = ?", (function_name,))
    for a in attrs:
        conn.execute(
            """
            INSERT INTO api_return_attrs (function_name, attr_name, attr_type, description)
            VALUES (?, ?, ?, ?)
            """,
            (
                function_name,
                a["attr_name"],
                a.get("attr_type"),
                a.get("description"),
            ),
        )
    conn.commit()


def upsert_table_columns(conn: sqlite3.Connection, table_name: str, columns: list[dict]) -> None:
    """Replace all column definitions for a table (delete + insert pattern for idempotency)."""
    conn.execute("DELETE FROM table_columns WHERE table_name = ?", (table_name,))
    seen = set()
    for col in columns:
        col_name = col["column_name"]
        if col_name in seen:
            continue
        seen.add(col_name)
        conn.execute(
            """
            INSERT INTO table_columns (table_name, column_name, column_type, meaning, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                table_name,
                col_name,
                col.get("column_type"),
                col.get("meaning"),
                col.get("description"),
            ),
        )
    conn.commit()


def upsert_strategy(conn: sqlite3.Connection, record: dict) -> None:
    """Insert or update a strategy record keyed on (name, category)."""
    conn.execute(
        """
        INSERT INTO strategies (name, category, description, code_content)
        VALUES (:name, :category, :description, :code_content)
        ON CONFLICT(name, category) DO UPDATE SET
            description = excluded.description,
            code_content = excluded.code_content,
            scraped_at = datetime('now')
        """,
        record,
    )
    conn.commit()
