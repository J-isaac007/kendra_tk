"""
controllers/app_controller.py  (Tkinter version)
"""
from tkinter import messagebox
from models.database import init_db, migrate_db
from models.pet import Pet
from models.feeding import FeedingModel
from models.medication import MedicationModel
from models.grooming import GroomingModel
from models.health import HealthModel
from models.activity import ActivityModel
from models.notification import NotificationModel

from views.app import KendraApp
from views.topbar import TopBar
from views.pet_dialog import PetDialog, PetSelectorDialog, NotificationCenter
from views.pages.dashboard import DashboardPage
from views.pages.feeding import FeedingPage
from views.pages.medications import MedicationsPage
from views.pages.health import HealthPage
from views.pages.grooming import GroomingPage
from views.pages.activity import ActivityPage
from views.pages.calendar_page import CalendarPage
from views.pages.settings_page import SettingsPage

import csv, os
from datetime import datetime


class AppController:
    def __init__(self):
        # ── DB ───────────────────────────────────────────────────
        init_db()
        migrate_db()

        # ── Root window ──────────────────────────────────────────
        self.app = KendraApp()

        # ── Active pet ───────────────────────────────────────────
        self.active_pet = None
        pets = Pet.get_all()
        if pets:
            self.active_pet = pets[0]

        # ── Build pages ──────────────────────────────────────────
        self._build_pages()

        # ── Top bar ──────────────────────────────────────────────
        self.topbar = TopBar(
            self.app.topbar_frame,
            on_navigate=self._on_navigate,
            on_pet_click=self._open_pet_selector,
            on_bell_click=self._open_notification_center,
        )
        self.topbar.pack(fill="both", expand=True)
        self.topbar.update_pet(self.active_pet)

        # ── Wire page callbacks ───────────────────────────────────
        self._wire_callbacks()

        # ── Initial load ─────────────────────────────────────────
        self.refresh_all()
        self._on_navigate("dashboard")

        # ── Reminder polling (every 60s) ─────────────────────────
        self._check_reminders()
        self._check_birthdays()

    def run(self):
        self.app.mainloop()

    # ── Page building ─────────────────────────────────────────────────────────

    def _build_pages(self):
        page_area = self.app.page_area

        self.dashboard_page   = DashboardPage(
            page_area,
            on_navigate=self._on_navigate,
            on_add_pet=self._open_add_pet,
        )
        self.feeding_page     = FeedingPage(page_area)
        self.medications_page = MedicationsPage(page_area)
        self.health_page      = HealthPage(page_area)
        self.grooming_page    = GroomingPage(page_area)
        self.activity_page    = ActivityPage(page_area)
        self.calendar_page    = CalendarPage(page_area)
        self.settings_page    = SettingsPage(page_area)

        self._pages = {
            "dashboard":   self.dashboard_page,
            "feeding":     self.feeding_page,
            "medications": self.medications_page,
            "health":      self.health_page,
            "grooming":    self.grooming_page,
            "activity":    self.activity_page,
            "calendar":    self.calendar_page,
            "settings":    self.settings_page,
        }
        for page_id, page in self._pages.items():
            self.app.register_page(page_id, page)

    def _wire_callbacks(self):
        # Feeding
        fp = self.feeding_page
        fp.cb_mark_done       = self._feeding_mark_done
        fp.cb_add_schedule    = self._feeding_add
        fp.cb_edit_schedule   = self._feeding_edit
        fp.cb_delete_schedule = self._feeding_delete

        # Medications
        mp = self.medications_page
        mp.cb_mark_given = self._med_mark_given
        mp.cb_skip_dose  = self._med_skip
        mp.cb_add_med    = self._med_add
        mp.cb_edit_med   = self._med_edit
        mp.cb_delete_med = self._med_delete

        # Health
        hp = self.health_page
        hp.cb_log_weight    = self._health_log
        hp.cb_delete_weight = self._health_delete

        # Grooming
        gp = self.grooming_page
        gp.cb_add_task      = self._groom_add
        gp.cb_edit_task     = self._groom_edit
        gp.cb_delete_task   = self._groom_delete
        gp.cb_complete_task = self._groom_complete

        # Activity
        ap = self.activity_page
        ap.cb_add_log    = self._activity_add
        ap.cb_delete_log = self._activity_delete

        # Settings
        self.settings_page.cb_export = self._export_csv

    # ── Navigation ────────────────────────────────────────────────────────────

    def _on_navigate(self, page_id: str):
        self.app.show_page(page_id)
        self.topbar.set_active_page(page_id)
        loaders = {
            "dashboard":   self.refresh_dashboard,
            "feeding":     self._load_feeding,
            "medications": self._load_medications,
            "health":      self._load_health,
            "grooming":    self._load_grooming,
            "activity":    self._load_activity,
            "calendar":    self.calendar_page.load,
            "settings":    lambda: None,
        }
        if page_id in loaders:
            loaders[page_id]()

    # ── Refresh helpers ───────────────────────────────────────────────────────

    def refresh_all(self):
        pets = Pet.get_all()
        self.topbar.update_pet(self.active_pet)
        if not self.active_pet and pets:
            self.active_pet = pets[0]
            self.topbar.update_pet(self.active_pet)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        pets = Pet.get_all()
        summaries = {p.id: Pet.get_today_summary(p.id) for p in pets}
        self.dashboard_page.load(pets, summaries)

    # ── Page loaders ──────────────────────────────────────────────────────────

    def _load_feeding(self):
        if not self.active_pet:
            self.feeding_page.show_no_pet(); return
        today     = FeedingModel.get_today(self.active_pet.id)
        schedules = FeedingModel.get_schedules(self.active_pet.id)
        self.feeding_page.load(self.active_pet, today, schedules)

    def _load_medications(self):
        if not self.active_pet:
            self.medications_page.show_no_pet(); return
        today    = MedicationModel.get_today(self.active_pet.id)
        all_meds = MedicationModel.get_all(self.active_pet.id)
        self.medications_page.load(self.active_pet, today, all_meds)

    def _load_health(self):
        if not self.active_pet:
            self.health_page.show_no_pet(); return
        logs  = HealthModel.get_weights(self.active_pet.id)
        stats = HealthModel.get_stats(self.active_pet.id)
        self.health_page.load(self.active_pet, logs, stats)

    def _load_grooming(self):
        if not self.active_pet:
            self.grooming_page.show_no_pet(); return
        tasks = GroomingModel.get_tasks(self.active_pet.id)
        self.grooming_page.load(self.active_pet, tasks)

    def _load_activity(self):
        if not self.active_pet:
            self.activity_page.show_no_pet(); return
        logs   = ActivityModel.get_logs(self.active_pet.id)
        stats  = ActivityModel.get_stats(self.active_pet.id)
        weekly = ActivityModel.get_weekly_summary(self.active_pet.id)
        self.activity_page.load(self.active_pet, logs, stats, weekly)

    # ── Pet management ────────────────────────────────────────────────────────

    def _open_pet_selector(self):
        pets = Pet.get_all()
        PetSelectorDialog(
            self.app, pets,
            active_pet_id=self.active_pet.id if self.active_pet else None,
            on_select=self._select_pet,
            on_add=self._open_add_pet,
            on_edit=self._open_edit_pet,
            on_delete=self._delete_pet,
        )

    def _open_add_pet(self):
        PetDialog(self.app, on_save=self._on_add_pet)

    def _open_edit_pet(self, pet_id: int):
        pet = Pet.get_by_id(pet_id)
        if pet:
            PetDialog(self.app, pet=pet, on_save=self._on_edit_pet)

    def _select_pet(self, pet_id: int):
        pet = Pet.get_by_id(pet_id)
        if pet:
            self.active_pet = pet
            self.refresh_all()

    def _on_add_pet(self, data: dict):
        picker = data.pop("_photo_picker", None)
        pet = Pet.create(
            name=data["name"], species=data["species"],
            breed=data.get("breed"), birthday=data.get("birthday"),
            notes=data.get("notes"),
        )
        if picker:
            photo = picker._save_photo(pet.id)
            if photo:
                Pet.update(pet.id, pet.name, pet.species, pet.breed,
                           pet.birthday, photo, pet.notes)
                pet = Pet.get_by_id(pet.id)
        self.active_pet = pet
        self.refresh_all()
        self._push(f"{pet.name} added! 🐾", "system", pet.id)

    def _on_edit_pet(self, data: dict):
        picker = data.pop("_photo_picker", None)
        photo  = picker._save_photo(data["pet_id"]) if picker else None
        pet = Pet.update(
            pet_id=data["pet_id"], name=data["name"],
            species=data["species"], breed=data.get("breed"),
            birthday=data.get("birthday"), photo_path=photo,
            notes=data.get("notes"),
        )
        if pet and self.active_pet and self.active_pet.id == pet.id:
            self.active_pet = pet
        self.refresh_all()

    def _delete_pet(self, pet_id: int):
        pet = Pet.get_by_id(pet_id)
        if not pet: return
        if not messagebox.askyesno("Delete Pet",
                f"Delete {pet.name}? All their data will be removed permanently."):
            return
        Pet.delete(pet_id)
        if self.active_pet and self.active_pet.id == pet_id:
            self.active_pet = None
        self.refresh_all()

    # ── Feeding callbacks ─────────────────────────────────────────────────────

    def _feeding_mark_done(self, schedule: dict):
        if not self.active_pet: return
        FeedingModel.log_feeding(self.active_pet.id, schedule["id"], "done")
        self.app.show_toast(f"{schedule['meal_name']} marked done ✓", "🍽")
        self._load_feeding(); self.refresh_dashboard()

    def _feeding_add(self, data: dict):
        FeedingModel.create_schedule(**{k:v for k,v in data.items() if k!="schedule_id"})
        self.app.show_toast("Meal schedule added!", "🍽")
        self._load_feeding(); self.refresh_dashboard()

    def _feeding_edit(self, data: dict):
        FeedingModel.update_schedule(data["schedule_id"], data["meal_name"],
            data["time"], data.get("days_of_week","1,2,3,4,5,6,7"),
            data.get("food_type"), data.get("portion"))
        self.app.show_toast("Schedule updated.", "✏")
        self._load_feeding()

    def _feeding_delete(self, schedule_id: int):
        if messagebox.askyesno("Delete", "Delete this meal schedule?"):
            FeedingModel.delete_schedule(schedule_id)
            self._load_feeding(); self.refresh_dashboard()

    # ── Medication callbacks ──────────────────────────────────────────────────

    def _med_mark_given(self, med_id: int):
        if not self.active_pet: return
        MedicationModel.log_dose(self.active_pet.id, med_id, "given")
        self.app.show_toast("Dose logged ✓", "💊")
        self._load_medications(); self.refresh_dashboard()

    def _med_skip(self, med_id: int, reason: str):
        if not self.active_pet: return
        MedicationModel.log_dose(self.active_pet.id, med_id, "skipped", reason)
        self.app.show_toast("Dose skipped.", "⏭")
        self._load_medications()

    def _med_add(self, data: dict):
        MedicationModel.create(pet_id=data["pet_id"], name=data["name"],
            frequency=data["frequency"], start_date=data["start_date"],
            dosage=data.get("dosage"), time=data.get("time"),
            end_date=data.get("end_date"), notes=data.get("notes"))
        self.app.show_toast("Medication added! 💊", "💊")
        self._load_medications(); self.refresh_dashboard()

    def _med_edit(self, data: dict):
        MedicationModel.update(med_id=data["med_id"], name=data["name"],
            frequency=data["frequency"], start_date=data["start_date"],
            dosage=data.get("dosage"), time=data.get("time"),
            end_date=data.get("end_date"), notes=data.get("notes"))
        self.app.show_toast("Medication updated.", "✏")
        self._load_medications()

    def _med_delete(self, med_id: int):
        if messagebox.askyesno("Delete", "Remove this medication?"):
            MedicationModel.delete(med_id)
            self._load_medications(); self.refresh_dashboard()

    # ── Health callbacks ──────────────────────────────────────────────────────

    def _health_log(self, data: dict):
        HealthModel.log_weight(**{k:v for k,v in data.items()})
        self.app.show_toast("Weight logged ⚖", "⚖")
        self._load_health()

    def _health_delete(self, log_id: int):
        if messagebox.askyesno("Delete", "Remove this weight entry?"):
            HealthModel.delete_weight(log_id)
            self._load_health()

    # ── Grooming callbacks ────────────────────────────────────────────────────

    def _groom_add(self, data: dict):
        GroomingModel.create(pet_id=data["pet_id"], task_name=data["task_name"],
            interval_days=data["interval_days"], notes=data.get("notes"))
        self.app.show_toast("Grooming task added ✂", "✂")
        self._load_grooming(); self.refresh_dashboard()

    def _groom_edit(self, data: dict):
        GroomingModel.update(task_id=data["task_id"], task_name=data["task_name"],
            interval_days=data["interval_days"], notes=data.get("notes"))
        self.app.show_toast("Task updated.", "✏")
        self._load_grooming()

    def _groom_delete(self, task_id: int):
        if messagebox.askyesno("Delete", "Delete this grooming task?"):
            GroomingModel.delete(task_id)
            self._load_grooming(); self.refresh_dashboard()

    def _groom_complete(self, task_id: int):
        task = GroomingModel.complete(task_id)
        self.app.show_toast(f"{task.task_name} done! Next: {task.next_due}", "✓")
        self._load_grooming(); self.refresh_dashboard()

    # ── Activity callbacks ────────────────────────────────────────────────────

    def _activity_add(self, data: dict):
        ActivityModel.create(**{k:v for k,v in data.items()})
        self.app.show_toast("Activity logged 🏃", "🏃")
        self._load_activity()

    def _activity_delete(self, log_id: int):
        if messagebox.askyesno("Delete", "Remove this activity entry?"):
            ActivityModel.delete(log_id)
            self._load_activity()

    # ── Notifications ─────────────────────────────────────────────────────────

    def _push(self, message: str, notif_type: str = "system", pet_id: int = None):
        NotificationModel.create(message, notif_type, pet_id)
        self.app.show_toast(message)
        self._refresh_badge()

    def _refresh_badge(self):
        count = NotificationModel.get_unread_count()
        self.topbar.update_unread_count(count)

    def _open_notification_center(self):
        NotificationCenter(self.app,
                           on_badge_update=self.topbar.update_unread_count)

    def _check_reminders(self):
        for r in FeedingModel.get_due_reminders():
            self._push(r["message"], "feeding")
        for r in MedicationModel.get_due_reminders():
            self._push(r["message"], "medication")
        # Poll again in 60 seconds
        self.app.after(60_000, self._check_reminders)

    def _check_birthdays(self):
        upcoming = NotificationModel.check_birthdays()
        for b in upcoming:
            msg = (f"🎂 Happy Birthday {b['name']}! They turn {b['age']} today!"
                   if b["days"] == 0
                   else f"🎂 {b['name']}'s birthday in {b['days']} day{'s' if b['days']>1 else ''}!")
            from models.database import get_db
            conn = get_db()
            today = conn.execute("SELECT date('now')").fetchone()[0]
            already = conn.execute(
                "SELECT id FROM notifications WHERE pet_id=? AND type='birthday' AND date(timestamp)=?",
                (b["pet_id"], today)
            ).fetchone()
            conn.close()
            if not already:
                NotificationModel.create(msg, "birthday", b["pet_id"])
                self.app.show_toast(msg, "🎂")
        self._refresh_badge()
        # Check again in 24 hours
        self.app.after(86_400_000, self._check_birthdays)

    # ── Export ────────────────────────────────────────────────────────────────

    def _export_csv(self, fmt: str, folder: str):
        from models.database import get_db
        from tkinter import messagebox
        conn = get_db()
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        written = []
        exports = {
            "feeding_logs": "SELECT fl.timestamp,p.name as pet,fs.meal_name,fl.status FROM feeding_logs fl LEFT JOIN pets p ON p.id=fl.pet_id LEFT JOIN feeding_schedules fs ON fs.id=fl.schedule_id ORDER BY fl.timestamp DESC",
            "medication_logs": "SELECT ml.timestamp,p.name as pet,m.name as medication,ml.status,ml.reason FROM medication_logs ml LEFT JOIN pets p ON p.id=ml.pet_id LEFT JOIN medications m ON m.id=ml.medication_id ORDER BY ml.timestamp DESC",
            "weight_logs": "SELECT wl.date,p.name as pet,wl.weight,wl.unit,wl.notes FROM weight_logs wl LEFT JOIN pets p ON p.id=wl.pet_id ORDER BY wl.date DESC",
            "activity_logs": "SELECT al.date,p.name as pet,al.activity_type,al.duration_minutes,al.notes FROM activity_logs al LEFT JOIN pets p ON p.id=al.pet_id ORDER BY al.date DESC",
        }
        try:
            for name, query in exports.items():
                rows = conn.execute(query).fetchall()
                if not rows: continue
                fp = os.path.join(folder, f"kendra_{name}_{ts}.csv")
                with open(fp, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(rows[0].keys())
                    for row in rows: w.writerow(list(row))
                written.append(os.path.basename(fp))
            conn.close()
            if written:
                messagebox.showinfo("Export Complete",
                    f"Exported {len(written)} file(s) to:\n{folder}\n\n" + "\n".join(f"• {f}" for f in written))
            else:
                messagebox.showinfo("Nothing to Export", "No data found to export.")
        except Exception as e:
            conn.close()
            messagebox.showerror("Export Failed", str(e))