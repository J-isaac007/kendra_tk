"""
views/pages/grooming.py
"""
import tkinter as tk
from datetime import date, datetime
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, primary_btn, ghost_btn, danger_btn,
    form_label, styled_entry, section_label,
    EmptyState, NoPetWidget, badge
)

PRESETS = ["Bath","Nail trim","Brush/comb","Ear cleaning",
           "Teeth brushing","Haircut","Flea check"]


class TaskDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, task=None, on_save=None):
        super().__init__(parent)
        self.pet_id  = pet_id
        self.task    = task
        self._on_save = on_save
        self.title("Edit Task" if task else "Add Grooming Task")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        tk.Label(self, text="Edit Task" if self.task else "Add Grooming Task",
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                 font=font("lg","bold")).pack(anchor="w", padx=20, pady=(20,8))
        form_label(self, "Task Name").pack(anchor="w", padx=20)
        self._name_var = tk.StringVar(value=self.task.task_name if self.task else "")
        styled_entry(self, self._name_var, placeholder="Bath, Nail trim…").pack(fill="x", padx=20, pady=(0,8))
        chips = tk.Frame(self, bg=COLORS["bg_card"])
        chips.pack(fill="x", padx=20, pady=(0,12))
        for p in PRESETS:
            tk.Button(chips, text=p, bg=COLORS["bg_elevated"], fg=COLORS["text_muted"],
                      font=font("xs"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                      command=lambda pr=p: self._name_var.set(pr)).pack(side="left", padx=(0,4))
        form_label(self, "Repeat Every (days)").pack(anchor="w", padx=20)
        row = tk.Frame(self, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=20, pady=(0,8))
        self._interval_var = tk.StringVar(value=str(self.task.interval_days if self.task else 7))
        styled_entry(row, self._interval_var, width=6).pack(side="left", padx=(0,10))
        for label, days in [("Weekly",7),("2 Weeks",14),("Monthly",30)]:
            tk.Button(row, text=label, bg=COLORS["bg_elevated"], fg=COLORS["text_muted"],
                      font=font("xs"), relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                      command=lambda d=days: self._interval_var.set(str(d))).pack(side="left", padx=(0,4))
        form_label(self, "Notes").pack(anchor="w", padx=20)
        self._notes_var = tk.StringVar(value=self.task.notes or "" if self.task else "")
        styled_entry(self, self._notes_var, placeholder="Specific instructions…").pack(fill="x", padx=20, pady=(0,12))
        acts = tk.Frame(self, bg=COLORS["bg_card"])
        acts.pack(fill="x", padx=20, pady=(0,20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8,0))
        def submit():
            name = self._name_var.get().strip()
            if not name: return
            if self._on_save:
                self._on_save({
                    "pet_id":        self.pet_id,
                    "task_name":     name,
                    "interval_days": int(self._interval_var.get() or 7),
                    "notes":         self._notes_var.get().strip() or None,
                    "task_id":       self.task.id if self.task else None,
                })
            self.destroy()
        primary_btn(acts, "Save" if self.task else "Add Task", submit).pack(side="right")


class GroomingPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet   = None
        self._tasks = []
        self.cb_add_task      = None
        self.cb_edit_task     = None
        self.cb_delete_task   = None
        self.cb_complete_task = None
        self._build_header()
        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32)

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_base"])
        hdr.pack(fill="x", padx=32, pady=(32,16))
        left = tk.Frame(hdr, bg=COLORS["bg_base"])
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="Grooming", bg=COLORS["bg_base"],
                 fg=COLORS["text_primary"], font=font("hero","bold"), anchor="w").pack(fill="x")
        self._subtitle = tk.Label(left, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_muted"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x")
        primary_btn(hdr, "＋  Add Task", self._open_add).pack(side="right", anchor="n")

    def show_no_pet(self):
        self._clear_content()
        NoPetWidget(self._content, "grooming").pack(fill="both", expand=True)

    def load(self, pet, tasks):
        self._pet   = pet
        self._tasks = tasks
        self._subtitle.config(text=f"{pet.name}'s grooming schedule")
        self._refresh()

    def _refresh(self):
        self._clear_content()
        overdue  = [t for t in self._tasks if t.overdue]
        upcoming = [t for t in self._tasks if not t.overdue]
        if overdue:
            banner = tk.Frame(self._content, bg="#2e1a10", pady=10, padx=14)
            banner.pack(fill="x", pady=(0,12))
            tk.Label(banner, text=f"⚠  {len(overdue)} task{'s' if len(overdue)>1 else ''} overdue",
                     bg="#2e1a10", fg=COLORS["danger"], font=font("base","bold")).pack(anchor="w")
        if not self._tasks:
            EmptyState(self._content, "✂️", "No grooming tasks yet",
                       "Add recurring tasks like baths and nail trims.").pack(fill="both", expand=True, pady=40)
            return
        sf = ScrollableFrame(self._content, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame
        if overdue:
            section_label(f, "Overdue").pack(anchor="w", pady=(8,6))
            for t in overdue: self._make_row(f, t)
        if upcoming:
            section_label(f, "Upcoming").pack(anchor="w", pady=(16,6))
            for t in upcoming: self._make_row(f, t)

    def _make_row(self, parent, task):
        row = tk.Frame(parent, bg=COLORS["bg_card"], pady=12, padx=14)
        row.pack(fill="x", pady=(0,6))
        done_btn = tk.Button(row, text="✓ Done",
                             bg=COLORS["bg_elevated"], fg=COLORS["accent_sage"],
                             font=font("sm"), relief="flat", bd=0, padx=10, pady=4,
                             cursor="hand2",
                             command=lambda tid=task.id: self.cb_complete_task and self.cb_complete_task(tid))
        done_btn.pack(side="left", padx=(0,12))
        info = tk.Frame(row, bg=COLORS["bg_card"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=task.task_name, bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=font("base","bold"), anchor="w").pack(fill="x")
        meta = f"Every {task.interval_days} days"
        if task.last_done: meta += f" · Last: {task.last_done}"
        tk.Label(info, text=meta, bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
        if task.notes:
            tk.Label(info, text=task.notes, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
        acts = tk.Frame(row, bg=COLORS["bg_card"])
        acts.pack(side="right")
        due_str = "—"
        if task.next_due:
            delta = (datetime.strptime(task.next_due,"%Y-%m-%d").date() - date.today()).days
            if delta < 0:    due_str = "Overdue"
            elif delta == 0: due_str = "Today"
            elif delta == 1: due_str = "Tomorrow"
            else:            due_str = f"In {delta}d"
        style = "overdue" if task.overdue else "pending"
        tk.Label(acts, text=due_str,
                 bg=COLORS[f"badge_{'over' if task.overdue else 'warn'}_bg"],
                 fg=COLORS[f"badge_{'over' if task.overdue else 'warn'}_fg"],
                 font=font("xs","bold"), padx=8, pady=3).pack(side="left", padx=(0,8))
        ghost_btn(acts, "Edit", command=lambda t=task: self._open_edit(t)).pack(side="left", padx=(0,4))
        ghost_btn(acts, "✕", command=lambda tid=task.id: self.cb_delete_task and self.cb_delete_task(tid)).pack(side="left")

    def _open_add(self):
        if not self._pet: return
        TaskDialog(self, self._pet.id,
                   on_save=lambda d: self.cb_add_task and self.cb_add_task(d))

    def _open_edit(self, task):
        TaskDialog(self, self._pet.id, task=task,
                   on_save=lambda d: self.cb_edit_task and self.cb_edit_task(d))

    def _clear_content(self):
        for w in self._content.winfo_children(): w.destroy()