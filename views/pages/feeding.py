"""
views/pages/feeding.py
"""
import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import datetime

from assets.styles.theme import COLORS, font, PAD
from views.pages.base import (
    ScrollableFrame, ProgressBar, TabBar, ItemRow,
    primary_btn, ghost_btn, danger_btn, section_label,
    body_label, muted_label, badge, divider, NoPetWidget,
    EmptyState, styled_entry, form_label, styled_combobox
)

DAYS = [("1","Mon"),("2","Tue"),("3","Wed"),("4","Thu"),
        ("5","Fri"),("6","Sat"),("7","Sun")]


class ScheduleDialog(tk.Toplevel):
    def __init__(self, parent, pet_id: int, schedule: dict = None,
                 on_save=None):
        super().__init__(parent)
        self.pet_id   = pet_id
        self.schedule = schedule
        self._on_save = on_save
        self.title("Edit Meal" if schedule else "Add Meal Schedule")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_card"])
        self.grab_set()
        self._build()
        self.transient(parent)

    def _build(self):
        pad = dict(padx=20, pady=8)

        tk.Label(
            self,
            text="Edit Meal" if self.schedule else "Add Meal Schedule",
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            font=font("lg", "bold"),
        ).pack(anchor="w", padx=20, pady=(20, 4))

        # Meal name
        form_label(self, "Meal Name").pack(anchor="w", **pad)
        self._name_var = tk.StringVar(
            value=self.schedule["meal_name"] if self.schedule else ""
        )
        f = styled_entry(self, self._name_var, placeholder="Breakfast, Dinner…")
        f.pack(fill="x", padx=20, pady=(0, 8))

        # Time
        form_label(self, "Time (HH:MM)").pack(anchor="w", **pad)
        self._time_var = tk.StringVar(
            value=self.schedule["time"] if self.schedule else "08:00"
        )
        f2 = styled_entry(self, self._time_var, placeholder="08:00", width=10)
        f2.pack(anchor="w", padx=20, pady=(0, 8))

        # Food + portion row
        row = tk.Frame(self, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=20, pady=(0, 8))

        food_col = tk.Frame(row, bg=COLORS["bg_card"])
        food_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        form_label(food_col, "Food Type").pack(anchor="w")
        self._food_var = tk.StringVar(
            value=self.schedule.get("food_type") or "" if self.schedule else ""
        )
        styled_entry(food_col, self._food_var,
                     placeholder="Dry kibble…").pack(fill="x")

        portion_col = tk.Frame(row, bg=COLORS["bg_card"])
        portion_col.pack(side="left", fill="x", expand=True)
        form_label(portion_col, "Portion").pack(anchor="w")
        self._portion_var = tk.StringVar(
            value=self.schedule.get("portion") or "" if self.schedule else ""
        )
        styled_entry(portion_col, self._portion_var,
                     placeholder="1 cup…").pack(fill="x")

        # Days of week
        form_label(self, "Days of Week").pack(anchor="w", **pad)
        days_frame = tk.Frame(self, bg=COLORS["bg_card"])
        days_frame.pack(anchor="w", padx=20, pady=(0, 12))

        selected = (
            self.schedule["days_of_week"] if self.schedule else "1,2,3,4,5,6,7"
        ).split(",")
        self._day_vars: dict[str, tk.BooleanVar] = {}
        for val, label in DAYS:
            var = tk.BooleanVar(value=val in selected)
            self._day_vars[val] = var
            bg = COLORS["bg_elevated"] if val in selected else COLORS["bg_input"]
            cb = tk.Checkbutton(
                days_frame, text=label, variable=var,
                bg=COLORS["bg_card"],
                fg=COLORS["accent_gold"],
                selectcolor=COLORS["bg_elevated"],
                activebackground=COLORS["bg_card"],
                font=font("sm"),
            )
            cb.pack(side="left", padx=3)

        # Actions
        actions = tk.Frame(self, bg=COLORS["bg_card"])
        actions.pack(fill="x", padx=20, pady=(8, 20))

        ghost_btn(actions, "Cancel", self.destroy).pack(side="right", padx=(8, 0))
        primary_btn(
            actions,
            "Save" if self.schedule else "Add Meal",
            self._on_submit,
        ).pack(side="right")

    def _on_submit(self):
        name = self._name_var.get().strip()
        if not name:
            return
        days = ",".join(k for k, v in self._day_vars.items() if v.get()) or "1"
        data = {
            "pet_id":       self.pet_id,
            "meal_name":    name,
            "time":         self._time_var.get().strip() or "08:00",
            "food_type":    self._food_var.get().strip() or None,
            "portion":      self._portion_var.get().strip() or None,
            "days_of_week": days,
            "schedule_id":  self.schedule["id"] if self.schedule else None,
        }
        if self._on_save:
            self._on_save(data)
        self.destroy()


class FeedingPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet       = None
        self._today     = []
        self._schedules = []

        # Callbacks set by controller
        self.cb_mark_done        = None
        self.cb_add_schedule     = None
        self.cb_edit_schedule    = None
        self.cb_delete_schedule  = None

        self._build_header()
        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True,
                           padx=32, pady=(0, 32))

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_base"])
        hdr.pack(fill="x", padx=32, pady=(32, 16))

        left = tk.Frame(hdr, bg=COLORS["bg_base"])
        left.pack(side="left", fill="x", expand=True)

        tk.Label(
            left, text="Feeding",
            bg=COLORS["bg_base"], fg=COLORS["text_primary"],
            font=font("hero", "bold"), anchor="w",
        ).pack(fill="x")

        self._subtitle = tk.Label(
            left, text="",
            bg=COLORS["bg_base"], fg=COLORS["text_muted"],
            font=font("sm"), anchor="w",
        )
        self._subtitle.pack(fill="x")

        self._add_btn = primary_btn(hdr, "＋  Add Meal",
                                    self._open_add_dialog)
        self._add_btn.pack(side="right", anchor="n")

    def show_no_pet(self):
        self._clear_content()
        NoPetWidget(self._content, "feeding").pack(
            fill="both", expand=True
        )

    def load(self, pet, today: list, schedules: list):
        self._pet       = pet
        self._today     = today
        self._schedules = schedules
        self._subtitle.config(text=f"{pet.name}'s meal schedule")
        self._refresh()

    def _refresh(self):
        self._clear_content()

        # Progress
        done  = sum(1 for s in self._today if s.get("done_today"))
        total = len(self._today)
        pb = ProgressBar(self._content, label="Today's meals")
        pb.pack(fill="x", pady=(0, 16))
        pb.update_progress(done, total)

        # Tabs
        self._stack_today = tk.Frame(self._content, bg=COLORS["bg_base"])
        self._stack_sched = tk.Frame(self._content, bg=COLORS["bg_base"])

        def on_tab(idx):
            if idx == 0:
                self._stack_today.pack(fill="both", expand=True)
                self._stack_sched.pack_forget()
            else:
                self._stack_sched.pack(fill="both", expand=True)
                self._stack_today.pack_forget()

        TabBar(
            self._content,
            ["Today", "All Schedules"],
            on_change=on_tab,
        ).pack(fill="x", pady=(0, 12))

        self._build_today_list()
        self._build_schedule_list()
        self._stack_today.pack(fill="both", expand=True)

    def _build_today_list(self):
        for w in self._stack_today.winfo_children():
            w.destroy()

        sf = ScrollableFrame(self._stack_today, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame

        if not self._today:
            EmptyState(f, "🍽️", "No meals today",
                       "Add a meal schedule to get started.").pack(
                fill="both", expand=True, pady=40
            )
            return

        for s in self._today:
            row = tk.Frame(f, bg=COLORS["bg_card"],
                           pady=12, padx=14)
            row.pack(fill="x", pady=(0, 6))

            # Checkbox button
            done = s.get("done_today", False)
            cb_text = "✓" if done else "○"
            cb_color = COLORS["accent_sage"] if done else COLORS["text_muted"]

            cb = tk.Button(
                row, text=cb_text,
                bg=COLORS["accent_sage"] if done else COLORS["bg_elevated"],
                fg="white" if done else COLORS["text_muted"],
                font=font("base", "bold"),
                relief="flat", bd=0, width=3,
                cursor="hand2" if not done else "arrow",
            )
            cb.pack(side="left", padx=(0, 12))
            if not done:
                cb.config(command=lambda sc=s: self._mark_done(sc))

            # Info
            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)

            tk.Label(
                info, text=s["meal_name"],
                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                font=font("base", "bold"), anchor="w",
            ).pack(fill="x")

            meta_parts = []
            if s.get("food_type"): meta_parts.append(s["food_type"])
            if s.get("portion"):   meta_parts.append(s["portion"])
            meta_parts.append(s["time"])
            tk.Label(
                info, text=" · ".join(meta_parts),
                bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                font=font("sm"), anchor="w",
            ).pack(fill="x")

            # Badge
            if done:
                tk.Label(
                    row, text="Done",
                    bg=COLORS["badge_done_bg"],
                    fg=COLORS["badge_done_fg"],
                    font=font("xs", "bold"),
                    padx=8, pady=3,
                ).pack(side="right")

    def _build_schedule_list(self):
        for w in self._stack_sched.winfo_children():
            w.destroy()

        sf = ScrollableFrame(self._stack_sched, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame

        if not self._schedules:
            EmptyState(f, "📅", "No schedules yet",
                       "Create meal schedules and they'll appear here.").pack(
                fill="both", expand=True, pady=40
            )
            return

        for s in self._schedules:
            row = tk.Frame(f, bg=COLORS["bg_card"],
                           pady=12, padx=14)
            row.pack(fill="x", pady=(0, 6))

            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)

            tk.Label(
                info, text=s.meal_name,
                bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                font=font("base", "bold"), anchor="w",
            ).pack(fill="x")

            parts = []
            if s.food_type: parts.append(s.food_type)
            if s.portion:   parts.append(s.portion)
            parts.append(s.time)
            tk.Label(
                info, text=" · ".join(parts),
                bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                font=font("sm"), anchor="w",
            ).pack(fill="x")

            acts = tk.Frame(row, bg=COLORS["bg_card"])
            acts.pack(side="right")

            ghost_btn(
                acts, "Edit",
                command=lambda sc=s: self._open_edit_dialog(sc)
            ).pack(side="left", padx=(0, 4))

            ghost_btn(
                acts, "✕",
                command=lambda sc=s: self._delete(sc.id)
            ).pack(side="left")

    def _mark_done(self, schedule):
        if self.cb_mark_done:
            self.cb_mark_done(schedule)

    def _delete(self, schedule_id):
        if self.cb_delete_schedule:
            self.cb_delete_schedule(schedule_id)

    def _open_add_dialog(self):
        if not self._pet:
            return
        ScheduleDialog(
            self, self._pet.id,
            on_save=lambda d: self.cb_add_schedule and self.cb_add_schedule(d)
        )

    def _open_edit_dialog(self, schedule):
        ScheduleDialog(
            self, self._pet.id,
            schedule=dict(
                id=schedule.id, meal_name=schedule.meal_name,
                time=schedule.time, days_of_week=schedule.days_of_week,
                food_type=schedule.food_type, portion=schedule.portion,
            ),
            on_save=lambda d: self.cb_edit_schedule and self.cb_edit_schedule(d)
        )

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()