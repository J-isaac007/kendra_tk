from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from models.database import get_db


@dataclass
class FeedingSchedule:
    id: int
    pet_id: int
    meal_name: str
    time: str
    days_of_week: str
    food_type: Optional[str]
    portion: Optional[str]
    active: int


@dataclass
class FeedingLog:
    id: int
    schedule_id: Optional[int]
    pet_id: int
    timestamp: str
    status: str


def _row_to_schedule(row) -> FeedingSchedule:
    return FeedingSchedule(
        id=row["id"], pet_id=row["pet_id"], meal_name=row["meal_name"],
        time=row["time"], days_of_week=row["days_of_week"],
        food_type=row["food_type"], portion=row["portion"], active=row["active"],
    )


class FeedingModel:

    @staticmethod
    def get_schedules(pet_id: int) -> list[FeedingSchedule]:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM feeding_schedules WHERE pet_id=? ORDER BY time", (pet_id,)
        ).fetchall()
        conn.close()
        return [_row_to_schedule(r) for r in rows]

    @staticmethod
    def get_today(pet_id: int) -> list[dict]:
        """Return today's schedules with a done_today flag."""
        conn = get_db()
        today = conn.execute("SELECT date('now')").fetchone()[0]
        schedules = conn.execute(
            "SELECT * FROM feeding_schedules WHERE pet_id=? AND active=1 ORDER BY time",
            (pet_id,)
        ).fetchall()
        result = []
        for s in schedules:
            done = conn.execute(
                """SELECT id FROM feeding_logs
                   WHERE schedule_id=? AND status='done' AND date(timestamp)=?""",
                (s["id"], today)
            ).fetchone()
            d = dict(s)
            d["done_today"] = done is not None
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def create_schedule(pet_id: int, meal_name: str, time: str,
                        days_of_week: str = "1,2,3,4,5,6,7",
                        food_type: str = None, portion: str = None) -> FeedingSchedule:
        conn = get_db()
        cur = conn.execute(
            """INSERT INTO feeding_schedules
               (pet_id, meal_name, time, days_of_week, food_type, portion)
               VALUES (?,?,?,?,?,?)""",
            (pet_id, meal_name, time, days_of_week, food_type, portion),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM feeding_schedules WHERE id=?", (cur.lastrowid,)
        ).fetchone()
        conn.close()
        return _row_to_schedule(row)

    @staticmethod
    def update_schedule(schedule_id: int, meal_name: str, time: str,
                        days_of_week: str, food_type: str = None,
                        portion: str = None, active: int = 1) -> None:
        conn = get_db()
        conn.execute(
            """UPDATE feeding_schedules
               SET meal_name=?, time=?, days_of_week=?, food_type=?, portion=?, active=?
               WHERE id=?""",
            (meal_name, time, days_of_week, food_type, portion, active, schedule_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete_schedule(schedule_id: int) -> None:
        conn = get_db()
        conn.execute("DELETE FROM feeding_schedules WHERE id=?", (schedule_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def log_feeding(pet_id: int, schedule_id: int = None,
                    status: str = "done") -> None:
        conn = get_db()
        conn.execute(
            "INSERT INTO feeding_logs (schedule_id, pet_id, status) VALUES (?,?,?)",
            (schedule_id, pet_id, status),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_due_reminders() -> list[dict]:
        """Return feeding schedules due within ±5 minutes of now."""
        from datetime import datetime, timedelta
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        window_start = (now - timedelta(minutes=5)).strftime("%H:%M")
        window_end   = (now + timedelta(minutes=5)).strftime("%H:%M")
        conn = get_db()
        rows = conn.execute(
            """SELECT fs.id, fs.meal_name, p.name as pet_name
               FROM feeding_schedules fs
               JOIN pets p ON p.id = fs.pet_id
               WHERE fs.active=1 AND fs.time BETWEEN ? AND ?""",
            (window_start, window_end),
        ).fetchall()
        reminders = []
        for r in rows:
            done = conn.execute(
                """SELECT id FROM feeding_logs
                   WHERE schedule_id=? AND status='done' AND date(timestamp)=?""",
                (r["id"], today),
            ).fetchone()
            if not done:
                reminders.append({
                    "pet_name": r["pet_name"],
                    "message": f"Time for {r['meal_name']}! 🍽️",
                })
        conn.close()
        return reminders