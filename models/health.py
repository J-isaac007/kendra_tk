from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from models.database import get_db


@dataclass
class WeightLog:
    id: int
    pet_id: int
    weight: float
    unit: str
    date: str
    notes: Optional[str]


def _row_to_log(row) -> WeightLog:
    return WeightLog(
        id=row["id"], pet_id=row["pet_id"], weight=row["weight"],
        unit=row["unit"], date=row["date"], notes=row["notes"],
    )


class HealthModel:

    @staticmethod
    def get_weights(pet_id: int, limit: int = 30) -> list[WeightLog]:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM weight_logs WHERE pet_id=? ORDER BY date DESC LIMIT ?",
            (pet_id, limit),
        ).fetchall()
        conn.close()
        return [_row_to_log(r) for r in rows]

    @staticmethod
    def log_weight(pet_id: int, weight: float, unit: str = "kg",
                   date: str = None, notes: str = None) -> WeightLog:
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO weight_logs (pet_id, weight, unit, date, notes) VALUES (?,?,?,?,?)",
            (pet_id, weight, unit, date, notes),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM weight_logs WHERE id=?", (cur.lastrowid,)).fetchone()
        conn.close()
        return _row_to_log(row)

    @staticmethod
    def delete_weight(log_id: int) -> None:
        conn = get_db()
        conn.execute("DELETE FROM weight_logs WHERE id=?", (log_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_stats(pet_id: int) -> dict:
        conn = get_db()
        row = conn.execute(
            """SELECT
                   COUNT(*)        AS total_entries,
                   MIN(weight)     AS min_weight,
                   MAX(weight)     AS max_weight,
                   ROUND(AVG(weight), 2) AS avg_weight,
                   (SELECT weight FROM weight_logs WHERE pet_id=?
                    ORDER BY date DESC LIMIT 1) AS latest_weight,
                   (SELECT unit FROM weight_logs WHERE pet_id=?
                    ORDER BY date DESC LIMIT 1) AS unit
               FROM weight_logs WHERE pet_id=?""",
            (pet_id, pet_id, pet_id),
        ).fetchone()
        conn.close()
        return dict(row) if row else {}