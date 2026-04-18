import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kendra.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_db()
    c = conn.cursor()

    # ── Pets ──────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            species     TEXT    NOT NULL,
            breed       TEXT,
            birthday    TEXT,
            photo_path  TEXT,
            notes       TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Add photo_path column if upgrading from old schema
    try:
        c.execute("ALTER TABLE pets ADD COLUMN photo_path TEXT")
    except Exception:
        pass

    # ── Feeding ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS feeding_schedules (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id       INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            meal_name    TEXT    NOT NULL,
            time         TEXT    NOT NULL,
            days_of_week TEXT    NOT NULL DEFAULT '1,2,3,4,5,6,7',
            food_type    TEXT,
            portion      TEXT,
            active       INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS feeding_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER REFERENCES feeding_schedules(id) ON DELETE SET NULL,
            pet_id      INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            timestamp   TEXT    DEFAULT (datetime('now')),
            status      TEXT    NOT NULL CHECK(status IN ('done','missed','skipped'))
        )
    """)

    # ── Medications ───────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id      INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            name        TEXT    NOT NULL,
            dosage      TEXT,
            frequency   TEXT    NOT NULL,
            time        TEXT,
            start_date  TEXT    NOT NULL,
            end_date    TEXT,
            notes       TEXT,
            active      INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS medication_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER REFERENCES medications(id) ON DELETE SET NULL,
            pet_id        INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            timestamp     TEXT    DEFAULT (datetime('now')),
            status        TEXT    NOT NULL CHECK(status IN ('given','skipped')),
            reason        TEXT
        )
    """)

    # ── Health / Weight ───────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id  INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            weight  REAL    NOT NULL,
            unit    TEXT    NOT NULL DEFAULT 'kg' CHECK(unit IN ('kg','lbs')),
            date    TEXT    NOT NULL DEFAULT (date('now')),
            notes   TEXT
        )
    """)

    # ── Grooming ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS grooming_tasks (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id        INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            task_name     TEXT    NOT NULL,
            interval_days INTEGER NOT NULL DEFAULT 7,
            last_done     TEXT,
            next_due      TEXT,
            notes         TEXT,
            active        INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS grooming_logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id   INTEGER REFERENCES grooming_tasks(id) ON DELETE SET NULL,
            pet_id    INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            timestamp TEXT    DEFAULT (datetime('now')),
            notes     TEXT
        )
    """)

    # ── Activity ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id           INTEGER NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
            activity_type    TEXT    NOT NULL,
            duration_minutes INTEGER NOT NULL,
            date             TEXT    NOT NULL DEFAULT (date('now')),
            notes            TEXT
        )
    """)

    # ── Notifications ─────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id    INTEGER REFERENCES pets(id) ON DELETE CASCADE,
            type      TEXT    NOT NULL,
            message   TEXT    NOT NULL,
            read      INTEGER DEFAULT 0,
            timestamp TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Reminders (custom scheduled) ──────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id      INTEGER REFERENCES pets(id) ON DELETE CASCADE,
            feature     TEXT    NOT NULL,
            label       TEXT    NOT NULL,
            remind_time TEXT    NOT NULL,
            lead_mins   INTEGER DEFAULT 0,
            active      INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
    print("[Kendra DB] Initialized successfully.")


def migrate_db() -> None:
    """
    Safe migrations for users upgrading from an older kendra.db.
    Each statement is wrapped in try/except so it never crashes on a fresh DB.
    """
    conn = get_db()
    migrations = [
        # Add photo_path to pets if missing
        "ALTER TABLE pets ADD COLUMN photo_path TEXT",
        # Create notifications table if missing
        """CREATE TABLE IF NOT EXISTS notifications (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id    INTEGER REFERENCES pets(id) ON DELETE CASCADE,
            type      TEXT    NOT NULL,
            message   TEXT    NOT NULL,
            read      INTEGER DEFAULT 0,
            timestamp TEXT    DEFAULT (datetime('now'))
        )""",
        # Create reminders table if missing
        """CREATE TABLE IF NOT EXISTS reminders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id      INTEGER REFERENCES pets(id) ON DELETE CASCADE,
            feature     TEXT    NOT NULL,
            label       TEXT    NOT NULL,
            remind_time TEXT    NOT NULL,
            lead_mins   INTEGER DEFAULT 0,
            active      INTEGER DEFAULT 1
        )""",
    ]
    for sql in migrations:
        try:
            conn.execute(sql)
        except Exception:
            pass  # column/table already exists — that's fine
    conn.commit()
    conn.close()