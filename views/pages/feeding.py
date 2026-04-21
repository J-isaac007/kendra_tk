"""
views/pages/feeding.py — Kendra Pro
Clean list rows, accent bar style, scroll only in list area.
"""
import tkinter as tk
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, ProgressBar, TabBar,
    primary_btn, ghost_btn, danger_btn,
    section_label, form_label, styled_entry,
    styled_combobox, EmptyState, NoPetWidget,
    check_btn, page_header, BorderCard, divider
)

DAYS = [("1","Mon"),("2","Tue"),("3","Wed"),("4","Thu"),
        ("5","Fri"),("6","Sat"),("7","Sun")]


class ScheduleDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, schedule=None, on_save=None):
        super().__init__(parent)
        self.pet_id = pet_id
        self.schedule = schedule
        self._on_save = on_save
        self.title("Edit Meal" if schedule else "Add Meal")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        bg = COLORS["bg_surface"]
        tk.Label(self, text="Edit Meal" if self.schedule else "Add Meal Schedule",
                 bg=bg, fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 16))

        # Name
        form_label(self, "Meal Name", bg=bg).pack(anchor="w", padx=24)
        self._name_f = styled_entry(self, placeholder="Meal name", bg=bg)
        self._name_f.pack(fill="x", padx=24, pady=(4, 12))
        if self.schedule:
            self._name_f.set(self.schedule["meal_name"])

        # Time
        row1 = tk.Frame(self, bg=bg)
        row1.pack(fill="x", padx=24, pady=(0, 12))
        t_col = tk.Frame(row1, bg=bg)
        t_col.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(t_col, "Time (HH:MM)", bg=bg).pack(anchor="w")
        self._time_f = styled_entry(t_col, placeholder="08:00", width=10, bg=bg)
        self._time_f.pack(fill="x", pady=(4, 0))
        if self.schedule:
            self._time_f.set(self.schedule["time"])

        # Food + portion
        f_col = tk.Frame(row1, bg=bg)
        f_col.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(f_col, "Food Type", bg=bg).pack(anchor="w")
        self._food_f = styled_entry(f_col, placeholder="Dry kibble, wet food…", bg=bg)
        self._food_f.pack(fill="x", pady=(4, 0))
        if self.schedule and self.schedule.get("food_type"):
            self._food_f.set(self.schedule["food_type"])

        p_col = tk.Frame(row1, bg=bg)
        p_col.pack(side="left", fill="x", expand=True)
        form_label(p_col, "Portion", bg=bg).pack(anchor="w")
        self._portion_f = styled_entry(p_col, placeholder="1 cup, 200g…", bg=bg)
        self._portion_f.pack(fill="x", pady=(4, 0))
        if self.schedule and self.schedule.get("portion"):
            self._portion_f.set(self.schedule["portion"])

        # Days
        form_label(self, "Days of Week", bg=bg).pack(anchor="w", padx=24)
        days_row = tk.Frame(self, bg=bg)
        days_row.pack(anchor="w", padx=24, pady=(4, 16))

        selected = (
            self.schedule["days_of_week"] if self.schedule else "1,2,3,4,5,6,7"
        ).split(",")
        self._day_vars: dict[str, tk.BooleanVar] = {}
        for val, label in DAYS:
            var = tk.BooleanVar(value=val in selected)
            self._day_vars[val] = var
            cb = tk.Checkbutton(
                days_row, text=label, variable=var,
                bg=bg, fg=COLORS["text_secondary"],
                selectcolor=COLORS["bg_elevated"],
                activebackground=bg,
                font=font("sm"),
            )
            cb.pack(side="left", padx=2)

        # Actions
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 12))
        acts = tk.Frame(self, bg=bg)
        acts.pack(fill="x", padx=24, pady=(0, 20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8, 0))
        primary_btn(acts, "Save" if self.schedule else "Add Meal",
                    self._submit).pack(side="right")

    def _submit(self):
        name = self._name_f.get().strip()
        if not name: return
        days = ",".join(k for k, v in self._day_vars.items() if v.get()) or "1"
        if self._on_save:
            self._on_save({
                "pet_id": self.pet_id,
                "meal_name": name,
                "time": self._time_f.get().strip() or "08:00",
                "food_type": self._food_f.get().strip() or None,
                "portion": self._portion_f.get().strip() or None,
                "days_of_week": days,
                "schedule_id": self.schedule["id"] if self.schedule else None,
            })
        self.destroy()


class FeedingPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet = None
        self._today = []
        self._schedules = []
        self.cb_mark_done = None
        self.cb_add_schedule = None
        self.cb_edit_schedule = None
        self.cb_delete_schedule = None

        # Header (static)
        self._hdr = page_header(self, "Feeding", action_text="＋  Add Meal",
                                action_cmd=self._open_add)
        self._hdr.pack(fill="x", padx=32, pady=(28, 0))
        self._subtitle = tk.Label(self, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_secondary"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x", padx=32, pady=(2, 16))

        # Content area (rebuilt on load)
        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32, pady=(0, 24))

    def show_no_pet(self):
        self._clear()
        NoPetWidget(self._content, "feeding").pack(fill="both", expand=True)

    def load(self, pet, today, schedules):
        self._pet = pet
        self._today = today
        self._schedules = schedules
        self._subtitle.config(text=f"{pet.name}'s meal schedule")
        self._refresh()

    def _refresh(self):
        self._clear()
        done  = sum(1 for s in self._today if s.get("done_today"))
        total = len(self._today)

        pb = ProgressBar(self._content, "Today's meals", bg=COLORS["bg_base"])
        pb.pack(fill="x", pady=(0, 16))
        pb.update_progress(done, total)

        self._tab_today = tk.Frame(self._content, bg=COLORS["bg_base"])
        self._tab_sched = tk.Frame(self._content, bg=COLORS["bg_base"])

        def switch(idx):
            if idx == 0:
                self._tab_today.pack(fill="both", expand=True)
                self._tab_sched.pack_forget()
            else:
                self._tab_sched.pack(fill="both", expand=True)
                self._tab_today.pack_forget()

        TabBar(self._content, ["Today", "All Schedules"],
               on_change=switch).pack(fill="x", pady=(0, 12))

        self._build_today()
        self._build_schedules()
        self._tab_today.pack(fill="both", expand=True)

    def _build_today(self):
        sf = ScrollableFrame(self._tab_today, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame

        if not self._today:
            EmptyState(f, "🍽", "No meals scheduled today",
                       "Add a meal schedule to track feeding.",
                       bg=COLORS["bg_base"]).pack(fill="both", expand=True, pady=40)
            return

        for s in self._today:
            done = s.get("done_today", False)
            row = tk.Frame(f, bg=COLORS["bg_surface"])
            row.pack(fill="x", pady=(0, 1))

            # Accent bar: green if done, amber if pending
            accent = COLORS["accent_green"] if done else COLORS["accent_amber"]
            tk.Frame(row, bg=accent, width=3).pack(side="left", fill="y")

            inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)

            # Check button
            cb = check_btn(inner, done,
                           command=lambda sc=s: self.cb_mark_done and self.cb_mark_done(sc),
                           bg=COLORS["bg_surface"])
            cb.pack(side="left", padx=(0, 12))

            # Info
            info = tk.Frame(inner, bg=COLORS["bg_surface"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=s["meal_name"], bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"], font=font("base", "bold"),
                     anchor="w").pack(fill="x")

            parts = [p for p in [s.get("food_type"), s.get("portion"), s["time"]] if p]
            tk.Label(info, text="  ·  ".join(parts), bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"], font=font("xs"), anchor="w").pack(fill="x")

            # Status
            if done:
                tk.Label(inner, text="Done", bg=COLORS["bg_surface"],
                         fg=COLORS["accent_green"],
                         font=font("xs", "bold")).pack(side="right")

    def _build_schedules(self):
        sf = ScrollableFrame(self._tab_sched, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame

        if not self._schedules:
            EmptyState(f, "📅", "No schedules yet",
                       "Add recurring meal times for your pet.",
                       bg=COLORS["bg_base"]).pack(fill="both", expand=True, pady=40)
            return

        for s in self._schedules:
            row = tk.Frame(f, bg=COLORS["bg_surface"])
            row.pack(fill="x", pady=(0, 1))
            tk.Frame(row, bg=COLORS["accent"], width=3).pack(side="left", fill="y")
            inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)

            info = tk.Frame(inner, bg=COLORS["bg_surface"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=s.meal_name, bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"], font=font("sm", "bold"),
                     anchor="w").pack(fill="x")
            parts = [p for p in [s.food_type, s.portion, s.time] if p]
            tk.Label(info, text="  ·  ".join(parts), bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"], font=font("xs"), anchor="w").pack(fill="x")

            acts = tk.Frame(inner, bg=COLORS["bg_surface"])
            acts.pack(side="right")
            ghost_btn(acts, "Edit",
                      command=lambda sc=s: self._open_edit(sc)).pack(side="left", padx=(0, 4))
            ghost_btn(acts, "✕",
                      command=lambda sc=s: self.cb_delete_schedule and self.cb_delete_schedule(sc.id),
                      fg=COLORS["accent_red"]).pack(side="left")

    def _open_add(self):
        if not self._pet: return
        ScheduleDialog(self, self._pet.id,
                       on_save=lambda d: self.cb_add_schedule and self.cb_add_schedule(d))

    def _open_edit(self, s):
        ScheduleDialog(self, self._pet.id,
                       schedule=dict(id=s.id, meal_name=s.meal_name, time=s.time,
                                     days_of_week=s.days_of_week,
                                     food_type=s.food_type, portion=s.portion),
                       on_save=lambda d: self.cb_edit_schedule and self.cb_edit_schedule(d))

    def _clear(self):
        for w in self._content.winfo_children(): w.destroy()