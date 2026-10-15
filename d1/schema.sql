-- D1 schema for MAX-LEGACY runtime
-- Run under Cloudflare D1 (SQLite-compatible).

CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    metadata JSON,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    name TEXT NOT NULL,
    metadata JSON,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS capabilities (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    metadata JSON,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS contracts (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    details JSON,
    start_at INTEGER,
    end_at INTEGER,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS revenue_events (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    contract_id TEXT,
    amount REAL NOT NULL DEFAULT 0,
    currency TEXT DEFAULT 'USD',
    metadata JSON,
    recorded_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE TABLE IF NOT EXISTS knowledge_metadata (
    id TEXT PRIMARY KEY,
    source TEXT,
    pointer TEXT,
    schema JSON,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_projects_customer ON projects(customer_id);
CREATE INDEX IF NOT EXISTS idx_capabilities_project ON capabilities(project_id);
CREATE INDEX IF NOT EXISTS idx_revenue_project ON revenue_events(project_id);
