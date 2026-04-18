from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
from models.database import get_db


@dataclass
class GroomingTask:
    id: int
    pet_id: int
    task_name: str
    interval_days: int
    last_done: Optional[str]
    next_due: Optional[str]
    notes: Optional[str]
    active: int
    overdue: bool = False


def _compute_next_due(last_done: Optional[str], interval_days: int) -> str:
    base = datetime.strptime(last_done, "%Y-%m-%d") if last_done else datetime.today()
    return (base + timedelta(days=interval_days)).strftime("%Y-%m-%d")


def _row_to_task(row, today: str = None) -> GroomingTask:
    t = GroomingTask(
        id=row["id"], pet_id=row["pet_id"], task_name=row["task_name"],
        interval_days=row["interval_days"], last_done=row["last_done"],
        next_due=row["next_due"], notes=row["notes"], active=row["active"],
    )
    if today and t.next_due:
        t.overdue = t.next_due <= today
    return t


class GroomingModel:

    @staticmethod
    def get_tasks(pet_id: int) -> list[GroomingTask]:
        conn = get_db()
        today = conn.execute("SELECT date('now')").fetchone()[0]
        rows = conn.execute(
            "SELECT * FROM grooming_tasks WHERE pet_id=? AND active=1 ORDER BY next_due",
            (pet_id,),
        ).fetchall()
        conn.close()
        return [_row_to_task(r, today) for r in rows]

    @staticmethod
    def create(pet_id: int, task_name: str, interval_days: int,
               notes: str = None) -> GroomingTask:
        next_due = _compute_next_due(None, interval_days)
        conn = get_db()
        cur = conn.execute(
            """INSERT INTO grooming_tasks (pet_id, task_name, interval_days, next_due, notes)
               VALUES (?,?,?,?,?)""",
            (pet_id, task_name, interval_days, next_due, notes),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM grooming_tasks WHERE id=?", (cur.lastrowid,)
        ).fetchone()
        conn.close()
        return _row_to_task(row)

    @staticmethod
    def update(task_id: int, task_name: str, interval_days: int,
               notes: str = None) -> None:
        conn = get_db()
        old = conn.execute(
            "SELECT last_done FROM grooming_tasks WHERE id=?", (task_id,)
        ).fetchone()
        next_due = _compute_next_due(old["last_done"] if old else None, interval_days)
        conn.execute(
            """UPDATE grooming_tasks
               SET task_name=?, interval_days=?, next_due=?, notes=?
               WHERE id=?""",
            (task_name, interval_days, next_due, notes, task_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(task_id: int) -> None:
        conn = get_db()
        conn.execute("DELETE FROM grooming_tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def complete(task_id: int, notes: str = None) -> GroomingTask:
        conn = get_db()
        task = conn.execute(
            "SELECT * FROM grooming_tasks WHERE id=?", (task_id,)
        ).fetchone()
        today = conn.execute("SELECT date('now')").fetchone()[0]
        next_due = _compute_next_due(today, task["interval_days"])
        conn.execute(
            "UPDATE grooming_tasks SET last_done=?, next_due=? WHERE id=?",
            (today, next_due, task_id),
        )
        conn.execute(
            "INSERT INTO grooming_logs (task_id, pet_id, notes) VALUES (?,?,?)",
            (task_id, task["pet_id"], notes),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM grooming_tasks WHERE id=?", (task_id,)
        ).fetchone()
        conn.close()
        return _row_to_task(row, today)

    @staticmethod
    def get_logs(pet_id: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT gl.*, gt.task_name
               FROM grooming_logs gl
               LEFT JOIN grooming_tasks gt ON gl.task_id = gt.id
               WHERE gl.pet_id=? ORDER BY gl.timestamp DESC LIMIT 50""",
            (pet_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]