# Architecture Research

**Domain:** Web scraping pipeline + document storage + MCP server exposure
**Researched:** 2026-03-22
**Confidence:** HIGH (MCP architecture from official docs; scraping pipeline from verified community sources)

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER (run once)                    │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────────┐   │
│  │   Browser   │   │   Page      │   │   Content            │   │
│  │  Launcher   │──▶│  Navigator  │──▶│   Extractor          │   │
│  │ (Playwright)│   │ (login,nav) │   │  (HTML→structured)   │   │
│  └─────────────┘   └─────────────┘   └──────────┬───────────┘   │
│                                                  │               │
│                                                  ▼               │
│                                       ┌──────────────────────┐   │
│                                       │   Transformer        │   │
│                                       │  (clean, validate,   │   │
│                                       │   normalize fields)  │   │
│                                       └──────────┬───────────┘   │
├──────────────────────────────────────────────────┼───────────────┤
│                    STORAGE LAYER                  │               │
├──────────────────────────────────────────────────┼───────────────┤
│                                                  ▼               │
│                              ┌───────────────────────────────┐   │
│                              │          SQLite DB            │   │
│                              │  ┌─────────────────────────┐  │   │
│                              │  │   api_docs table        │  │   │
│                              │  │   strategies table      │  │   │
│                              │  └─────────────────────────┘  │   │
│                              └───────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────┤
│                    EXPOSURE LAYER (always-on)                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    MCP Server                             │   │
│  │   tools/list ──▶ [search_api_docs, list_functions, ...]   │   │
│  │   tools/call ──▶ query SQLite → return structured text    │   │
│  └───────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│                    AI Host (Claude, Cursor, etc.)                 │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Browser Launcher | Opens a headless browser, manages session lifecycle | Playwright `chromium.launch()` |
| Page Navigator | Handles login flow, navigates to target pages, waits for dynamic content | Playwright `page.goto()`, `page.fill()`, `page.waitForSelector()` |
| Content Extractor | Pulls raw HTML/text from DOM elements; handles pagination and sidebar menu traversal | Playwright `page.$$eval()`, `page.textContent()` |
| Transformer | Cleans raw text, validates field presence, normalizes structure into typed records | Plain functions; no framework needed |
| SQLite DB | Persistent document store; single-file, zero-server, portable | `better-sqlite3` (Node sync API) or `sqlite3` (Python) |
| MCP Server | Exposes search tools to AI hosts via JSON-RPC over stdio; converts SQL results to text | `@modelcontextprotocol/sdk` (TypeScript) |

## Recommended Project Structure

```
src/
├── scraper/
│   ├── browser.ts        # Browser lifecycle (launch, close, reuse session)
│   ├── auth.ts           # Login flow for JoinQuant credentials
│   ├── nav.ts            # Page navigation helpers (sidebar, pagination)
│   ├── extract/
│   │   ├── api-docs.ts   # Extract from /help/api/help pages
│   │   └── strategies.ts # Extract from 经典策略学习 sidebar entries
│   └── transform/
│       ├── api-docs.ts   # Parse raw HTML into ApiDoc records
│       └── strategies.ts # Parse into Strategy records
├── db/
│   ├── schema.ts         # CREATE TABLE statements, migrations
│   ├── seed.ts           # Orchestrates scrape → insert run
│   └── queries.ts        # Typed query functions (search, lookup)
├── mcp/
│   ├── server.ts         # MCP server entry point (stdio transport)
│   └── tools/
│       ├── search-api-docs.ts    # Tool: search by keyword/function name
│       └── list-functions.ts     # Tool: list all indexed function names
└── run-scrape.ts         # CLI entry point: runs full ingestion pipeline
```

### Structure Rationale

- **scraper/**: Isolates browser automation from everything else. If Playwright API changes, only this folder needs updates.
- **db/**: All SQL knowledge lives here. MCP tools import query functions, never write raw SQL themselves.
- **mcp/**: Thin layer. Tools call `db/queries.ts` and format results as text. No business logic here.
- **run-scrape.ts**: A single script a human can run once. Not part of the MCP server process.

## Architectural Patterns

### Pattern 1: Separation of Ingestion from Exposure

**What:** The scraper pipeline (ingestion) and the MCP server (exposure) are separate processes. Ingestion runs once (or on demand) to populate SQLite. The MCP server reads from the populated DB at query time.

**When to use:** Always, for this type of system. Mixing scraping logic into the MCP server would mean the server hangs during scrapes and risks corrupting the DB mid-read.

**Trade-offs:** Two entry points to maintain (`run-scrape.ts` and `mcp/server.ts`), but the separation makes each independently testable and avoids shared-state bugs.

**Example:**
```typescript
// run-scrape.ts — run once
import { scrapeApiDocs } from './scraper/extract/api-docs'
import { insertApiDocs } from './db/seed'

const docs = await scrapeApiDocs()
insertApiDocs(docs)
console.log(`Inserted ${docs.length} API doc entries`)
```

### Pattern 2: Typed Query Functions as the DB Boundary

**What:** The `db/queries.ts` module exports strongly-typed functions. MCP tools and tests call these functions — never raw SQL outside `db/`.

**When to use:** Any time SQLite is the backing store. Prevents SQL string duplication and makes schema changes findable via TypeScript compiler.

**Trade-offs:** Slightly more boilerplate than inline SQL, but pays off immediately when you change a column name.

**Example:**
```typescript
// db/queries.ts
export function searchApiDocs(keyword: string): ApiDocRecord[] {
  return db.prepare(
    `SELECT * FROM api_docs WHERE function_name LIKE ? OR description LIKE ?`
  ).all(`%${keyword}%`, `%${keyword}%`) as ApiDocRecord[]
}
```

### Pattern 3: MCP Tools as Thin Formatters

**What:** Each MCP tool does exactly two things: call a query function, then format the result as a human-readable text string for the AI host.

**When to use:** Always for knowledge base MCP servers. The AI model needs readable text, not JSON blobs or raw SQL rows.

**Trade-offs:** Formatting logic is duplicated per-tool, but keeping it inline makes each tool self-contained and easy to read.

**Example:**
```typescript
// mcp/tools/search-api-docs.ts
server.tool('search_api_docs', { keyword: z.string() }, async ({ keyword }) => {
  const results = searchApiDocs(keyword)
  if (results.length === 0) return { content: [{ type: 'text', text: 'No results found.' }] }
  const text = results.map(r =>
    `## ${r.function_name}\n**Parameters:** ${r.parameters}\n**Returns:** ${r.return_type}\n${r.description}`
  ).join('\n\n---\n\n')
  return { content: [{ type: 'text', text }] }
})
```

## Data Flow

### Ingestion Flow (run once)

```
JoinQuant Website
    |
    | HTTP/browser session
    v
Page Navigator (login → navigate to target page)
    |
    | raw HTML / DOM content
    v
Content Extractor (page.$$eval, textContent)
    |
    | raw string arrays
    v
Transformer (parse, clean, validate → typed records)
    |
    | ApiDocRecord[] / StrategyRecord[]
    v
SQLite (INSERT OR REPLACE)
    |
    | confirmation count
    v
Console log / exit
```

### Query Flow (at AI query time)

```
AI Host (Claude Desktop, Cursor, etc.)
    |
    | MCP initialize (stdio)
    v
MCP Server (tools/list → advertise available tools)
    |
    | tools/call { name: "search_api_docs", arguments: { keyword: "get_price" } }
    v
Tool Handler
    |
    | searchApiDocs("get_price")
    v
SQLite (SELECT with LIKE)
    |
    | ApiDocRecord[]
    v
Formatter (records → markdown text)
    |
    | { content: [{ type: "text", text: "..." }] }
    v
AI Host (injects text into LLM context)
```

### Key Data Flows

1. **Credential flow:** Login credentials are read from environment variable or config at scrape time only. The MCP server never needs them — it only reads the already-populated DB.
2. **Schema dependency:** The MCP server's query functions depend on the DB schema being populated first. `run-scrape.ts` must run before the MCP server is useful.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1 developer, local | Single SQLite file, stdio transport MCP server. Exactly this design. No changes needed. |
| Team sharing the KB | Commit the `.db` file to git (it's read-only after scrape), or run scrape CI and publish artifact. |
| Frequent re-scraping | Add a scheduled job (cron / GitHub Actions) that re-runs `run-scrape.ts` and overwrites the DB. Still no need to change architecture. |
| Many concurrent AI queries | SQLite handles concurrent reads fine. Write contention only occurs during scrape, which is offline. No bottleneck. |

### Scaling Priorities

1. **First bottleneck:** Playwright login failures due to site changes. Mitigation: session cookie caching so login only runs when session expires.
2. **Second bottleneck:** Full-text search quality. SQLite's `LIKE` search is enough for v1 but degrades for large corpora. SQLite FTS5 (full-text search extension) is the upgrade path — no schema rewrite required, just add a virtual FTS table.

## Anti-Patterns

### Anti-Pattern 1: Running Scraper Inside the MCP Server

**What people do:** Trigger a fresh scrape on every MCP tool call, or start the scraper in the MCP server process.

**Why it's wrong:** Scraping takes minutes, blocks all responses, and risks DB corruption if the MCP server is killed mid-write. The AI host will timeout waiting.

**Do this instead:** Keep scraping as a separate offline script. MCP server is always-on and only reads.

### Anti-Pattern 2: Returning Raw SQL Rows to the AI

**What people do:** JSON-serialize the SQLite row and return it directly from the MCP tool.

**Why it's wrong:** AI models work better with structured prose than raw column dumps. Column names like `param_json` and `return_type_raw` don't help the model understand context.

**Do this instead:** Format tool results as markdown with clear section headers (function name, parameters, return type, description, example). The AI host injects this as readable context.

### Anti-Pattern 3: One Monolithic Tool

**What people do:** Build a single `query_database` tool that accepts arbitrary SQL.

**Why it's wrong:** AI models will write incorrect SQL, table names will change, and the tool surface is opaque to the LLM. The model doesn't know what to query.

**Do this instead:** Named, documented tools with clear `description` fields and constrained inputs (`keyword: string`, `function_name: string`). The MCP `tools/list` response is what the AI reads to decide which tool to call.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| JoinQuant login page | Playwright form fill + session cookie reuse | Credentials from env var; session can be saved to file to avoid re-login on re-runs |
| JoinQuant API docs (`/help/api/help`) | Playwright headless GET + DOM extraction | Publicly accessible, no login required |
| JoinQuant strategy listing (`经典策略学习`) | Playwright with authenticated session + sidebar menu traversal | Login required; content loads dynamically |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| scraper/ → db/ | Function call (TypeScript import) | Transformer output is typed records; `db/seed.ts` accepts them |
| db/ → mcp/ | Function call (TypeScript import) | `db/queries.ts` is the only API the MCP tools use |
| mcp/server.ts → AI Host | JSON-RPC 2.0 over stdio | MCP SDK handles framing; tools register handlers at startup |
| run-scrape.ts → Everything | Script orchestration | Calls scraper, then calls db/seed. One-shot process, exits on completion. |

## Build Order Implications

The component dependency graph determines which phases must come first:

```
1. db/schema.ts           (no dependencies — define tables first)
    |
2. db/queries.ts          (depends on schema being defined)
    |
3. scraper/browser.ts     (no dependencies — standalone)
3. scraper/auth.ts        (depends on browser.ts)
3. scraper/extract/       (depends on auth.ts)
3. scraper/transform/     (depends on extract shape — can be built in parallel)
    |
4. db/seed.ts             (depends on queries + transform output types)
    |
5. run-scrape.ts          (depends on all of the above — integration test: does scrape → DB work?)
    |
6. mcp/tools/             (depends on db/queries.ts being stable and populated)
    |
7. mcp/server.ts          (depends on tools being registered)
```

**Conclusion for roadmap:** Build DB schema → scraper → verify data in DB → then MCP server. Do not build MCP server before the DB is populated and queryable; there is nothing to test against.

## Sources

- [MCP Architecture Overview (official)](https://modelcontextprotocol.io/docs/learn/architecture) — HIGH confidence
- [MCP Example Servers (official)](https://modelcontextprotocol.io/examples) — HIGH confidence
- [SQLite MCP Server (Anthropic reference)](https://www.pulsemcp.com/servers/modelcontextprotocol-sqlite) — HIGH confidence
- [Web Scraping with Playwright Python Part 3 — SQLite storage](https://scrapingant.com/blog/web-scraping-playwright-python-part-3) — MEDIUM confidence
- [ETL Pipeline for Web Scraping (DEV Community)](https://dev.to/techwithqasim/building-an-etl-pipeline-for-web-scraping-using-python-2381) — MEDIUM confidence
- [MCP Servers GitHub (modelcontextprotocol/servers)](https://github.com/modelcontextprotocol/servers) — HIGH confidence

---
*Architecture research for: JoinQuant API & Strategy Knowledge Base (web scraping + SQLite + MCP server)*
*Researched: 2026-03-22*
