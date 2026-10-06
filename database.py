import sqlite3
from datetime import datetime
import os


# =========================================================
# DATABASE
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "labellens.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


# =========================================================
# DATABASE INITIALIZATION / MIGRATION
# =========================================================

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # PROFILE
    c.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            skin_tone TEXT,
            concern TEXT,
            food_goal TEXT,
            kids_mode INTEGER DEFAULT 0
        )
    """)

    # SCANS
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            product_name TEXT,
            category TEXT,
            ingredients TEXT,
            verdict TEXT
        )
    """)

    conn.commit()

    # Check existing scan columns
    c.execute("PRAGMA table_info(scans)")
    columns = [row[1] for row in c.fetchall()]

    # Add missing columns one by one
    if "created_at" not in columns:
        c.execute(
            "ALTER TABLE scans ADD COLUMN created_at TEXT"
        )

    if "product_name" not in columns:
        c.execute(
            "ALTER TABLE scans ADD COLUMN product_name TEXT"
        )

    if "category" not in columns:
        c.execute(
            "ALTER TABLE scans ADD COLUMN category TEXT"
        )

    if "ingredients" not in columns:
        c.execute(
            "ALTER TABLE scans ADD COLUMN ingredients TEXT"
        )

    if "verdict" not in columns:
        c.execute(
            "ALTER TABLE scans ADD COLUMN verdict TEXT"
        )

    if "flagged" not in columns:
        c.execute(
            "ALTER TABLE scans ADD COLUMN flagged TEXT"
        )

    conn.commit()
    conn.close()


# =========================================================
# PROFILE
# =========================================================

def save_profile(
    skin_tone="",
    concern="",
    food_goal="",
    kids_mode=False
):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM profile")

    c.execute("""
        INSERT INTO profile (
            id,
            skin_tone,
            concern,
            food_goal,
            kids_mode
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        1,
        str(skin_tone),
        str(concern),
        str(food_goal),
        int(bool(kids_mode))
    ))

    conn.commit()
    conn.close()


def load_profile():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            skin_tone,
            concern,
            food_goal,
            kids_mode
        FROM profile
        WHERE id = 1
    """)

    row = c.fetchone()

    conn.close()

    if not row:
        return {}

    return {
        "skin_tone": row[0] or "",
        "concern": row[1] or "",
        "food_goal": row[2] or "",
        "kids_mode": bool(row[3])
    }


# =========================================================
# SAFE TEXT CONVERSION
# =========================================================

def _safe_text(value):

    if value is None:
        return ""

    if isinstance(value, dict):
        return ", ".join(
            f"{k}: {v}"
            for k, v in value.items()
        )

    if isinstance(value, (list, tuple, set)):
        return ", ".join(
            str(x)
            for x in value
        )

    return str(value)


# =========================================================
# SAVE SCAN
# =========================================================

def save_scan(
    product_name,
    category,
    ingredients,
    verdict,
    flagged
):

    # Make absolutely sure database is migrated
    init_db()

    product_name = _safe_text(product_name)
    category = _safe_text(category)
    ingredients = _safe_text(ingredients)
    verdict = _safe_text(verdict)
    flagged = _safe_text(flagged)

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO scans (
            created_at,
            product_name,
            category,
            ingredients,
            verdict,
            flagged
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        product_name,
        category,
        ingredients[:2000],
        verdict,
        flagged[:2000]
    ))

    conn.commit()
    conn.close()


# =========================================================
# GET HISTORY
# =========================================================

def get_scans(limit=50):

    # IMPORTANT:
    # This runs migration BEFORE SELECT.
    init_db()

    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT
            id,
            created_at,
            product_name,
            category,
            ingredients,
            verdict,
            flagged
        FROM scans
        ORDER BY id DESC
        LIMIT ?
    """, (
        int(limit),
    ))

    rows = c.fetchall()

    conn.close()

    return rows


def recent_scans(limit=50):
    return get_scans(limit)


# =========================================================
# CLEAR HISTORY
# =========================================================

def clear_scans():

    init_db()

    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM scans")

    conn.commit()
    conn.close()


def clear_history():
    clear_scans()


# =========================================================
# AUTO INITIALIZE
# =========================================================

init_db()