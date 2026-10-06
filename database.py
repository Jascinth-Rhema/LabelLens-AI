"""Tiny SQLite store: scan history and the saved profile."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent / "labellens_v2.db"   # new file name, avoids the old broken table

SCAN_COLS = {"id", "ts", "category", "ingredients", "verdict", "flagged"}


def _conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    with _conn() as c:
        cols = {row[1] for row in c.execute("PRAGMA table_info(scans)")}
        if cols and not SCAN_COLS <= cols:  # incompatible old table: keep it as a backup
            c.execute("DROP TABLE IF EXISTS scans_old")
            c.execute("ALTER TABLE scans RENAME TO scans_old")
        c.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, ts TEXT, category TEXT, ingredients TEXT, verdict TEXT, flagged TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS profile (k TEXT PRIMARY KEY, v TEXT)")


def save_scan(category: str, ingredients: str, verdict: str, flagged: list):
    with _conn() as c:
        c.execute("INSERT INTO scans (ts, category, ingredients, verdict, flagged) VALUES (?,?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), category, ingredients[:2000], verdict, ", ".join(flagged)))


def recent_scans(limit: int = 20):
    with _conn() as c:
        return c.execute("SELECT ts, category, verdict, flagged, ingredients FROM scans ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def clear_history():
    with _conn() as c:
        c.execute("DELETE FROM scans")


def save_profile(d: dict):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO profile (k, v) VALUES ('profile', ?)", (json.dumps(d),))


def load_profile() -> dict:
    with _conn() as c:
        row = c.execute("SELECT v FROM profile WHERE k='profile'").fetchone()
    return json.loads(row[0]) if row else {}