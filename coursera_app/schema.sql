CREATE TABLE IF NOT EXISTS jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slug        TEXT NOT NULL,
    title       TEXT,
    types_json  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'queued',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    started_at  TEXT,
    finished_at TEXT,
    error_code  TEXT,
    error_msg   TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id      INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    url_hash    TEXT NOT NULL,
    rel_path    TEXT NOT NULL,
    kind        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'queued',
    bytes_done  INTEGER NOT NULL DEFAULT 0,
    bytes_total INTEGER,
    attempts    INTEGER NOT NULL DEFAULT 0,
    error_code  TEXT,
    UNIQUE (job_id, url_hash)
);

CREATE TABLE IF NOT EXISTS events (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      TEXT NOT NULL DEFAULT (datetime('now')),
    level   TEXT NOT NULL,
    job_id  INTEGER,
    message TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_items_job ON items(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
