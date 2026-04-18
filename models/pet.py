from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from models.database import get_db


@dataclass
class Pet:
    id: int
    name: str
    species: str
    breed: Optional[str]
    birthday: Optional[str]
    photo_path: Optional[str]
    notes: Optional[str]
    created_at: str

    @staticmethod
    def _row_to_pet(row) -> "Pet":
        keys = row.keys()
        return Pet(
            id=row["id"], name=row["name"], species=row["species"],
            breed=row["breed"], birthday=row["birthday"],
            photo_path=row["photo_path"] if "photo_path" in keys else None,
            notes=row["notes"], created_at=row["created_at"],
        )

    @staticmethod
    def get_all() -> list["Pet"]:
        conn = get_db()
        rows = conn.execute("SELECT * FROM pets ORDER BY name").fetchall()
        conn.close()
        return [Pet._row_to_pet(r) for r in rows]

    @staticmethod
    def get_by_id(pet_id: int) -> Optional["Pet"]:
        conn = get_db()
        row = conn.execute("SELECT * FROM pets WHERE id=?", (pet_id,)).fetchone()
        conn.close()
        return Pet._row_to_pet(row) if row else None

    @staticmethod
    def create(name: str, species: str, breed: str = None,
               birthday: str = None, photo_path: str = None,
               notes: str = None) -> "Pet":
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO pets (name,species,breed,birthday,photo_path,notes) VALUES (?,?,?,?,?,?)",
            (name, species, breed, birthday, photo_path, notes),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM pets WHERE id=?", (cur.lastrowid,)).fetchone()
        conn.close()
        return Pet._row_to_pet(row)

    @staticmethod
    def update(pet_id: int, name: str, species: str, breed: str = None,
               birthday: str = None, photo_path: str = None,
               notes: str = None) -> Optional["Pet"]:
        conn = get_db()
        existing = conn.execute(
            "SELECT photo_path FROM pets WHERE id=?", (pet_id,)
        ).fetchone()
        final_photo = photo_path if photo_path is not None else (
            existing["photo_path"] if existing else None
        )
        conn.execute(
            "UPDATE pets SET name=?,species=?,breed=?,birthday=?,photo_path=?,notes=? WHERE id=?",
            (name, species, breed, birthday, final_photo, notes, pet_id),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM pets WHERE id=?", (pet_id,)).fetchone()
        conn.close()
        return Pet._row_to_pet(row) if row else None

    @staticmethod
    def delete(pet_id: int) -> None:
        conn = get_db()
        conn.execute("DELETE FROM pets WHERE id=?", (pet_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_today_summary(pet_id: int) -> dict:
        conn = get_db()
        today = conn.execute("SELECT date('now')").fetchone()[0]
        fd = conn.execute("SELECT COUNT(*) FROM feeding_schedules WHERE pet_id=? AND active=1",(pet_id,)).fetchone()[0]
        fd_done = conn.execute("SELECT COUNT(*) FROM feeding_logs WHERE pet_id=? AND status='done' AND date(timestamp)=?",(pet_id,today)).fetchone()[0]
        md = conn.execute("SELECT COUNT(*) FROM medications WHERE pet_id=? AND active=1 AND start_date<=? AND (end_date IS NULL OR end_date>=?)",(pet_id,today,today)).fetchone()[0]
        md_done = conn.execute("SELECT COUNT(*) FROM medication_logs WHERE pet_id=? AND status='given' AND date(timestamp)=?",(pet_id,today)).fetchone()[0]
        go = conn.execute("SELECT COUNT(*) FROM grooming_tasks WHERE pet_id=? AND active=1 AND next_due<=?",(pet_id,today)).fetchone()[0]
        conn.close()
        return {"feeding_due":fd,"feeding_done":fd_done,"meds_due":md,"meds_done":md_done,"grooming_overdue":go}