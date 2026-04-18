from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from models.database import get_db


@dataclass
class Notification:
    id: int
    pet_id: Optional[int]
    type: str
    message: str
    read: bool
    timestamp: str
    pet_name: Optional[str] = None  # joined from pets table


TYPE_ICONS = {
    "feeding":    "🍽",
    "medication": "💊",
    "grooming":   "✂",
    "activity":   "🏃",
    "birthday":   "🎂",
    "system":     "🔔",
}


def _row_to_notif(row) -> Notification:
    return Notification(
        id=row["id"],
        pet_id=row["pet_id"],
        type=row["type"],
        message=row["message"],
        read=bool(row["read"]),
        timestamp=row["timestamp"],
        pet_name=row["pet_name"] if "pet_name" in row.keys() else None,
    )


class NotificationModel:

    @staticmethod
    def create(message: str, notif_type: str = "system",
               pet_id: int = None) -> Notification:
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO notifications (pet_id, type, message) VALUES (?,?,?)",
            (pet_id, notif_type, message),
        )
        conn.commit()
        row = conn.execute(
            "SELECT n.*, p.name as pet_name FROM notifications n "
            "LEFT JOIN pets p ON p.id = n.pet_id WHERE n.id=?",
            (cur.lastrowid,),
        ).fetchone()
        conn.close()
        return _row_to_notif(row)

    @staticmethod
    def get_all(limit: int = 50) -> list[Notification]:
        conn = get_db()
        rows = conn.execute(
            """SELECT n.*, p.name as pet_name
               FROM notifications n
               LEFT JOIN pets p ON p.id = n.pet_id
               ORDER BY n.timestamp DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        conn.close()
        return [_row_to_notif(r) for r in rows]

    @staticmethod
    def get_unread_count() -> int:
        conn = get_db()
        count = conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE read=0"
        ).fetchone()[0]
        conn.close()
        return count

    @staticmethod
    def mark_read(notif_id: int) -> None:
        conn = get_db()
        conn.execute("UPDATE notifications SET read=1 WHERE id=?", (notif_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def mark_all_read() -> None:
        conn = get_db()
        conn.execute("UPDATE notifications SET read=1")
        conn.commit()
        conn.close()

    @staticmethod
    def delete(notif_id: int) -> None:
        conn = get_db()
        conn.execute("DELETE FROM notifications WHERE id=?", (notif_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def clear_all() -> None:
        conn = get_db()
        conn.execute("DELETE FROM notifications")
        conn.commit()
        conn.close()

    @staticmethod
    def check_birthdays() -> list[dict]:
        """Return pets whose birthday is today or within 3 days."""
        conn = get_db()
        today = conn.execute("SELECT date('now')").fetchone()[0]
        pets = conn.execute(
            "SELECT id, name, birthday FROM pets WHERE birthday IS NOT NULL"
        ).fetchall()
        conn.close()

        upcoming = []
        from datetime import date, datetime
        today_dt = date.today()
        for pet in pets:
            try:
                bday = datetime.strptime(pet["birthday"], "%Y-%m-%d").date()
                # Compare month-day only (birthday this year)
                this_year = bday.replace(year=today_dt.year)
                delta = (this_year - today_dt).days
                if delta < 0:
                    # Try next year
                    this_year = bday.replace(year=today_dt.year + 1)
                    delta = (this_year - today_dt).days
                if 0 <= delta <= 3:
                    upcoming.append({
                        "pet_id":  pet["id"],
                        "name":    pet["name"],
                        "days":    delta,
                        "age":     today_dt.year - bday.year + (1 if delta == 0 else 0),
                    })
            except Exception:
                continue
        return upcoming