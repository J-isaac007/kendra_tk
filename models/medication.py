from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from models.database import get_db


@dataclass
class Medication:
    id: int
    pet_id: int
    name: str
    dosage: Optional[str]
    frequency: str
    time: Optional[str]
    start_date: str
    end_date: Optional[str]
    notes: Optional[str]
    active: int


def _row_to_med(row) -> Medication:
    return Medication(
        id=row["id"], pet_id=row["pet_id"], name=row["name"],
        dosage=row["dosage"], frequency=row["frequency"], time=row["time"],
        start_date=row["start_date"], end_date=row["end_date"],
        notes=row["notes"], active=row["active"],
    )


class MedicationModel:

    @staticmethod
    def get_all(pet_id: int) -> list[Medication]:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM medications WHERE pet_id=? ORDER BY name", (pet_id,)
        ).fetchall()
        conn.close()
        return [_row_to_med(r) for r in rows]

    @staticmethod
    def get_today(pet_id: int) -> list[dict]:
        conn = get_db()
        today = conn.execute("SELECT date('now')").fetchone()[0]
        meds = conn.execute(
            """SELECT * FROM medications
               WHERE pet_id=? AND active=1 AND start_date<=?
               AND (end_date IS NULL OR end_date>=?)""",
            (pet_id, today, today),
        ).fetchall()
        result = []
        for m in meds:
            given = conn.execute(
                """SELECT id FROM medication_logs
                   WHERE medication_id=? AND status='given' AND date(timestamp)=?""",
                (m["id"], today),
            ).fetchone()
            d = dict(m)
            d["given_today"] = given is not None
            result.append(d)
        conn.close()
        return result

    @staticmethod
    def create(pet_id: int, name: str, frequency: str, start_date: str,
               dosage: str = None, time: str = None,
               end_date: str = None, notes: str = None) -> Medication:
        conn = get_db()
        cur = conn.execute(
            """INSERT INTO medications
               (pet_id, name, dosage, frequency, time, start_date, end_date, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (pet_id, name, dosage, frequency, time, start_date, end_date, notes),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM medications WHERE id=?", (cur.lastrowid,)).fetchone()
        conn.close()
        return _row_to_med(row)

    @staticmethod
    def update(med_id: int, name: str, frequency: str, start_date: str,
               dosage: str = None, time: str = None, end_date: str = None,
               notes: str = None, active: int = 1) -> None:
        conn = get_db()
        conn.execute(
            """UPDATE medications
               SET name=?, dosage=?, frequency=?, time=?,
                   start_date=?, end_date=?, notes=?, active=?
               WHERE id=?""",
            (name, dosage, frequency, time, start_date, end_date, notes, active, med_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(med_id: int) -> None:
        conn = get_db()
        conn.execute("DELETE FROM medications WHERE id=?", (med_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def log_dose(pet_id: int, medication_id: int,
                 status: str = "given", reason: str = None) -> None:
        conn = get_db()
        conn.execute(
            """INSERT INTO medication_logs (medication_id, pet_id, status, reason)
               VALUES (?,?,?,?)""",
            (medication_id, pet_id, status, reason),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_logs(pet_id: int, limit: int = 50) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT ml.*, m.name as medication_name
               FROM medication_logs ml
               LEFT JOIN medications m ON ml.medication_id = m.id
               WHERE ml.pet_id=? ORDER BY ml.timestamp DESC LIMIT ?""",
            (pet_id, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_due_reminders() -> list[dict]:
        from datetime import datetime, timedelta
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        window_start = (now - timedelta(minutes=5)).strftime("%H:%M")
        window_end   = (now + timedelta(minutes=5)).strftime("%H:%M")
        conn = get_db()
        rows = conn.execute(
            """SELECT m.id, m.name, p.name as pet_name
               FROM medications m
               JOIN pets p ON p.id = m.pet_id
               WHERE m.active=1 AND m.time BETWEEN ? AND ?
                 AND m.start_date<=? AND (m.end_date IS NULL OR m.end_date>=?)""",
            (window_start, window_end, today, today),
        ).fetchall()
        reminders = []
        for r in rows:
            given = conn.execute(
                """SELECT id FROM medication_logs
                   WHERE medication_id=? AND status='given' AND date(timestamp)=?""",
                (r["id"], today),
            ).fetchone()
            if not given:
                reminders.append({
                    "pet_name": r["pet_name"],
                    "message": f"Time for {r['name']} medication! 💊",
                })
        conn.close()
        return reminders