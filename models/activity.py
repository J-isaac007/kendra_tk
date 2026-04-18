from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from models.database import get_db


@dataclass
class ActivityLog:
    id: int
    pet_id: int
    activity_type: str
    duration_minutes: int
    date: str
    notes: Optional[str]


def _row_to_log(row) -> ActivityLog:
    return ActivityLog(
        id=row["id"], pet_id=row["pet_id"], activity_type=row["activity_type"],
        duration_minutes=row["duration_minutes"], date=row["date"], notes=row["notes"],
    )


class ActivityModel:

    @staticmethod
    def get_logs(pet_id: int, limit: int = 50) -> list[ActivityLog]:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM activity_logs WHERE pet_id=? ORDER BY date DESC, id DESC LIMIT ?",
            (pet_id, limit),
        ).fetchall()
        conn.close()
        return [_row_to_log(r) for r in rows]

    @staticmethod
    def create(pet_id: int, activity_type: str, duration_minutes: int,
               date: str = None, notes: str = None) -> ActivityLog:
        conn = get_db()
        cur = conn.execute(
            """INSERT INTO activity_logs (pet_id, activity_type, duration_minutes, date, notes)
               VALUES (?,?,?,?,?)""",
            (pet_id, activity_type, duration_minutes, date, notes),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM activity_logs WHERE id=?", (cur.lastrowid,)
        ).fetchone()
        conn.close()
        return _row_to_log(row)

    @staticmethod
    def delete(log_id: int) -> None:
        conn = get_db()
        conn.execute("DELETE FROM activity_logs WHERE id=?", (log_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_weekly_summary(pet_id: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT date,
                      SUM(duration_minutes) AS total_minutes,
                      COUNT(*)              AS sessions
               FROM activity_logs
               WHERE pet_id=? AND date >= date('now', '-6 days')
               GROUP BY date ORDER BY date""",
            (pet_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_stats(pet_id: int) -> dict:
        conn = get_db()
        row = conn.execute(
            """SELECT
                   SUM(duration_minutes)        AS total_minutes_week,
                   COUNT(*)                     AS sessions_week,
                   ROUND(AVG(duration_minutes), 1) AS avg_duration
               FROM activity_logs
               WHERE pet_id=? AND date >= date('now', '-6 days')""",
            (pet_id,),
        ).fetchone()
        conn.close()
        return dict(row) if row else {}