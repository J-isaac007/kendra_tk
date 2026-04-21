"""
views/pages/grooming.py — Kendra Pro
"""
import tkinter as tk
from datetime import date, datetime
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, primary_btn, ghost_btn, danger_btn,
    form_label, styled_entry, section_label,
    EmptyState, NoPetWidget, page_header
)

PRESETS = ["Bath", "Nail trim", "Brush/comb", "Ear cleaning",
           "Teeth brushing", "Haircut", "Flea check"]


class TaskDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, task=None, on_save=None):
        super().__init__(parent)
        self.pet_id = pet_id
        self.task = task
        self._on_save = on_save
        self.title("Edit Task" if task else "Add Grooming Task")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        bg = COLORS["bg_surface"]
        tk.Label(self, text="Edit Task" if self.task else "Add Grooming Task",
                 bg=bg, fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 16))

        form_label(self, "Task Name", bg=bg).pack(anchor="w", padx=24)
        self._name_f = styled_entry(self, placeholder="Bath, Nail trim…", bg=bg)
        self._name_f.pack(fill="x", padx=24, pady=(4, 8))
        if self.task and self.task.task_name: self._name_f.set(self.task.task_name)

        # Preset chips
        chips = tk.Frame(self, bg=bg)
        chips.pack(fill="x", padx=24, pady=(0, 12))
        for p in PRESETS:
            btn = tk.Button(chips, text=p, bg=COLORS["bg_elevated"],
                            fg=COLORS["text_secondary"], font=font("xs"),
                            relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                            command=lambda pr=p: self._name_var.set(pr))
            btn.pack(side="left", padx=(0, 4))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["bg_hover"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS["bg_elevated"]))

        form_label(self, "Repeat Every (days)", bg=bg).pack(anchor="w", padx=24)
        row = tk.Frame(self, bg=bg)
        row.pack(fill="x", padx=24, pady=(4, 12))
        self._interval_f = styled_entry(row, width=6, bg=bg)
        self._interval_f.pack(side="left", padx=(0, 12))
        self._interval_f.set(str(self.task.interval_days if self.task else 7))
        for label, days in [("Weekly", 7), ("2 Weeks", 14), ("Monthly", 30)]:
            btn = tk.Button(row, text=label, bg=COLORS["bg_elevated"],
                            fg=COLORS["text_secondary"], font=font("xs"),
                            relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                            command=lambda d=days: self._interval_var.set(str(d)))
            btn.pack(side="left", padx=(0, 4))

        form_label(self, "Notes", bg=bg).pack(anchor="w", padx=24)
        self._notes_f = styled_entry(self, placeholder="Specific instructions…", bg=bg)
        self._notes_f.pack(fill="x", padx=24, pady=(4, 16))
        if self.task and self.task.notes: self._notes_f.set(self.task.notes)

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 12))
        acts = tk.Frame(self, bg=bg)
        acts.pack(fill="x", padx=24, pady=(0, 20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8, 0))
        def submit():
            name = self._name_f.get().strip()
            if not name: return
            if self._on_save:
                self._on_save({
                    "pet_id": self.pet_id,
                    "task_name": name,
                    "interval_days": int(self._interval_f.get() or 7),
                    "notes": self._notes_f.get().strip() or None,
                    "task_id": self.task.id if self.task else None,
                })
            self.destroy()
        primary_btn(acts, "Save" if self.task else "Add Task", submit).pack(side="right")


class GroomingPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet = None
        self._tasks = []
        self.cb_add_task = None
        self.cb_edit_task = None
        self.cb_delete_task = None
        self.cb_complete_task = None

        self._hdr = page_header(self, "Grooming", action_text="＋  Add Task",
                                action_cmd=self._open_add)
        self._hdr.pack(fill="x", padx=32, pady=(28, 0))
        self._subtitle = tk.Label(self, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_secondary"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x", padx=32, pady=(2, 16))

        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32, pady=(0, 24))

    def show_no_pet(self):
        self._clear()
        NoPetWidget(self._content, "grooming").pack(fill="both", expand=True)

    def load(self, pet, tasks):
        self._pet = pet
        self._tasks = tasks
        self._subtitle.config(text=f"{pet.name}'s grooming schedule")
        self._refresh()

    def _refresh(self):
        self._clear()
        overdue  = [t for t in self._tasks if t.overdue]
        upcoming = [t for t in self._tasks if not t.overdue]

        if overdue:
            banner = tk.Frame(self._content, bg=COLORS["bg_elevated"], padx=14, pady=10)
            banner.pack(fill="x", pady=(0, 14))
            tk.Frame(banner, bg=COLORS["accent_red"], width=3).pack(side="left", fill="y")
            tk.Label(banner, text=f"  ⚠  {len(overdue)} task{'s' if len(overdue) > 1 else ''} overdue",
                     bg=COLORS["bg_elevated"], fg=COLORS["accent_red"],
                     font=font("sm", "bold")).pack(side="left")

        if not self._tasks:
            EmptyState(self._content, "✂", "No grooming tasks yet",
                       "Add recurring tasks like baths and nail trims.",
                       bg=COLORS["bg_base"]).pack(fill="both", expand=True, pady=40)
            return

        sf = ScrollableFrame(self._content, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame

        if overdue:
            section_label(f, f"Overdue ({len(overdue)})").pack(anchor="w", pady=(0, 6))
            for t in overdue: self._make_row(f, t)

        if upcoming:
            section_label(f, f"Upcoming ({len(upcoming)})").pack(
                anchor="w", pady=(16 if overdue else 0, 6))
            for t in upcoming: self._make_row(f, t)

    def _make_row(self, parent, task):
        row = tk.Frame(parent, bg=COLORS["bg_surface"])
        row.pack(fill="x", pady=(0, 1))
        accent = COLORS["accent_red"] if task.overdue else COLORS["accent_purple"]
        tk.Frame(row, bg=accent, width=3).pack(side="left", fill="y")
        inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
        inner.pack(side="left", fill="both", expand=True)

        # Done button
        done_btn = tk.Button(inner, text="✓ Done",
                             bg=COLORS["bg_elevated"], fg=COLORS["accent_green"],
                             font=font("xs", "bold"), relief="flat", bd=0,
                             padx=10, pady=4, cursor="hand2",
                             command=lambda tid=task.id: self.cb_complete_task and self.cb_complete_task(tid))
        done_btn.pack(side="left", padx=(0, 12))
        done_btn.bind("<Enter>", lambda e: done_btn.config(bg=COLORS["bg_hover"]))
        done_btn.bind("<Leave>", lambda e: done_btn.config(bg=COLORS["bg_elevated"]))

        info = tk.Frame(inner, bg=COLORS["bg_surface"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=task.task_name, bg=COLORS["bg_surface"],
                 fg=COLORS["text_primary"], font=font("sm", "bold"),
                 anchor="w").pack(fill="x")
        meta = f"Every {task.interval_days} days"
        if task.last_done: meta += f"  ·  Last: {task.last_done}"
        tk.Label(info, text=meta, bg=COLORS["bg_surface"],
                 fg=COLORS["text_muted"], font=font("xs"), anchor="w").pack(fill="x")

        # Due badge
        due_str, due_color = "—", COLORS["text_muted"]
        if task.next_due:
            delta = (datetime.strptime(task.next_due, "%Y-%m-%d").date() - date.today()).days
            if delta < 0:     due_str, due_color = "Overdue", COLORS["accent_red"]
            elif delta == 0:  due_str, due_color = "Today",   COLORS["accent_amber"]
            elif delta == 1:  due_str, due_color = "Tomorrow",COLORS["accent_amber"]
            else:             due_str, due_color = f"In {delta}d", COLORS["text_secondary"]

        acts = tk.Frame(inner, bg=COLORS["bg_surface"])
        acts.pack(side="right")
        tk.Label(acts, text=due_str, bg=COLORS["bg_surface"],
                 fg=due_color, font=font("xs", "bold")).pack(side="left", padx=(0, 12))
        ghost_btn(acts, "Edit",
                  command=lambda t=task: self._open_edit(t)).pack(side="left", padx=(0, 4))
        ghost_btn(acts, "✕",
                  command=lambda tid=task.id: self.cb_delete_task and self.cb_delete_task(tid),
                  fg=COLORS["accent_red"]).pack(side="left")

    def _open_add(self):
        if not self._pet: return
        TaskDialog(self, self._pet.id,
                   on_save=lambda d: self.cb_add_task and self.cb_add_task(d))

    def _open_edit(self, task):
        TaskDialog(self, self._pet.id, task=task,
                   on_save=lambda d: self.cb_edit_task and self.cb_edit_task(d))

    def _clear(self):
        for w in self._content.winfo_children(): w.destroy()