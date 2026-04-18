"""
views/pages/activity.py
"""
import tkinter as tk
from datetime import date, timedelta
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, StatCard, primary_btn, ghost_btn,
    form_label, styled_entry, styled_combobox,
    section_label, EmptyState, NoPetWidget
)

ACTIVITY_TYPES = ["Walk","Run","Play","Training","Swim",
                  "Fetch","Agility","Socialization","Other"]

TYPE_COLORS = {
    "Walk": COLORS["accent_gold"], "Run": COLORS["accent_rust"],
    "Play": COLORS["accent_sage"], "Training": COLORS["accent_lavender"],
}


class ActivityDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, on_save=None):
        super().__init__(parent)
        self.pet_id  = pet_id
        self._on_save = on_save
        self.title("Log Activity")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        tk.Label(self, text="Log Activity", bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=font("lg","bold")).pack(
                 anchor="w", padx=20, pady=(20,8))
        form_label(self, "Activity Type").pack(anchor="w", padx=20)
        self._type_var = tk.StringVar(value="Walk")
        chips = tk.Frame(self, bg=COLORS["bg_card"])
        chips.pack(fill="x", padx=20, pady=(0,12))
        self._type_btns = {}
        for atype in ACTIVITY_TYPES:
            btn = tk.Button(chips, text=atype,
                            bg=COLORS["bg_elevated"], fg=COLORS["text_muted"],
                            font=font("xs"), relief="flat", bd=0,
                            padx=8, pady=4, cursor="hand2",
                            command=lambda t=atype: self._select_type(t))
            btn.pack(side="left", padx=(0,4), pady=(0,4))
            self._type_btns[atype] = btn
        self._select_type("Walk")
        row = tk.Frame(self, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=20, pady=(0,8))
        d_col = tk.Frame(row, bg=COLORS["bg_card"])
        d_col.pack(side="left", fill="x", expand=True, padx=(0,10))
        form_label(d_col, "Duration (minutes)").pack(anchor="w")
        self._dur_var = tk.StringVar(value="30")
        styled_entry(d_col, self._dur_var, width=8).pack(fill="x")
        dt_col = tk.Frame(row, bg=COLORS["bg_card"])
        dt_col.pack(side="left", fill="x", expand=True)
        form_label(dt_col, "Date").pack(anchor="w")
        self._date_var = tk.StringVar(value=str(date.today()))
        styled_entry(dt_col, self._date_var, width=14).pack(fill="x")
        form_label(self, "Notes").pack(anchor="w", padx=20)
        self._notes_var = tk.StringVar()
        styled_entry(self, self._notes_var, placeholder="Off-leash at the park…").pack(
            fill="x", padx=20, pady=(0,12))
        acts = tk.Frame(self, bg=COLORS["bg_card"])
        acts.pack(fill="x", padx=20, pady=(0,20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8,0))
        def submit():
            if self._on_save:
                self._on_save({
                    "pet_id":           self.pet_id,
                    "activity_type":    self._type_var.get(),
                    "duration_minutes": int(self._dur_var.get() or 30),
                    "date":             self._date_var.get().strip() or None,
                    "notes":            self._notes_var.get().strip() or None,
                })
            self.destroy()
        primary_btn(acts, "Log Activity", submit).pack(side="right")

    def _select_type(self, selected):
        self._type_var.set(selected)
        for atype, btn in self._type_btns.items():
            if atype == selected:
                btn.config(bg=COLORS["bg_hover"], fg=COLORS["accent_gold"])
            else:
                btn.config(bg=COLORS["bg_elevated"], fg=COLORS["text_muted"])


def _fmt(minutes) -> str:
    minutes = int(minutes or 0)
    if minutes == 0: return "0 min"
    h, m = minutes // 60, minutes % 60
    return f"{h}h {m}m" if h and m else (f"{h}h" if h else f"{m} min")


class ActivityPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet    = None
        self._logs   = []
        self._stats  = {}
        self._weekly = []
        self.cb_add_log    = None
        self.cb_delete_log = None
        self._build_header()
        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32)

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_base"])
        hdr.pack(fill="x", padx=32, pady=(32,16))
        left = tk.Frame(hdr, bg=COLORS["bg_base"])
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="Activity", bg=COLORS["bg_base"],
                 fg=COLORS["text_primary"], font=font("hero","bold"), anchor="w").pack(fill="x")
        self._subtitle = tk.Label(left, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_muted"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x")
        primary_btn(hdr, "＋  Log Activity", self._open_log).pack(side="right", anchor="n")

    def show_no_pet(self):
        self._clear_content()
        NoPetWidget(self._content, "activity").pack(fill="both", expand=True)

    def load(self, pet, logs, stats, weekly):
        self._pet    = pet
        self._logs   = logs
        self._stats  = stats
        self._weekly = weekly
        self._subtitle.config(text=f"{pet.name}'s exercise log")
        self._refresh()

    def _refresh(self):
        self._clear_content()
        # Stats
        sr = tk.Frame(self._content, bg=COLORS["bg_base"])
        sr.pack(fill="x", pady=(0,16))
        StatCard(sr, _fmt(self._stats.get("total_minutes_week") or 0),
                 "This Week").pack(side="left", fill="x", expand=True, padx=(0,8))
        StatCard(sr, str(self._stats.get("sessions_week") or 0),
                 "Sessions").pack(side="left", fill="x", expand=True, padx=(0,8))
        StatCard(sr, _fmt(self._stats.get("avg_duration") or 0),
                 "Avg Duration").pack(side="left", fill="x", expand=True)

        # Simple bar chart
        if self._weekly:
            section_label(self._content, "Weekly Activity").pack(anchor="w", pady=(8,8))
            self._build_chart()

        if not self._logs:
            EmptyState(self._content, "🏃", "No activity logged yet",
                       "Track walks, play sessions, training, and more.").pack(
                fill="both", expand=True, pady=40)
            return

        section_label(self._content, "Recent Activity").pack(anchor="w", pady=(16,8))
        sf = ScrollableFrame(self._content, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame
        for log in self._logs:
            row = tk.Frame(f, bg=COLORS["bg_card"], pady=12, padx=14)
            row.pack(fill="x", pady=(0,6))
            # Initial badge
            color = TYPE_COLORS.get(log.activity_type, COLORS["accent_rust"])
            badge_lbl = tk.Label(row, text=log.activity_type[0].upper(),
                                 bg=COLORS["bg_elevated"], fg=color,
                                 font=font("md","bold"), width=3, height=1)
            badge_lbl.pack(side="left", padx=(0,12))
            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=log.activity_type, bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"], font=font("base","bold"), anchor="w").pack(fill="x")
            meta = log.date
            if log.notes: meta += f" · {log.notes}"
            tk.Label(info, text=meta, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
            tk.Label(row, text=_fmt(log.duration_minutes),
                     bg=COLORS["bg_card"], fg=color,
                     font=font("md")).pack(side="right", padx=(0,12))
            ghost_btn(row, "✕", command=lambda lid=log.id: self.cb_delete_log and self.cb_delete_log(lid)).pack(side="right")

    def _build_chart(self):
        # Build 7-day map
        day_map = {e["date"]: e["total_minutes"] for e in self._weekly}
        days_data = []
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            days_data.append((d.strftime("%a"), day_map.get(str(d), 0)))

        max_val = max((m for _, m in days_data), default=1) or 1
        chart = tk.Frame(self._content, bg=COLORS["bg_card"], pady=12)
        chart.pack(fill="x", pady=(0,12))

        for day_label, minutes in days_data:
            col = tk.Frame(chart, bg=COLORS["bg_card"])
            col.pack(side="left", fill="x", expand=True, padx=4)
            # Value label
            tk.Label(col, text=_fmt(minutes) if minutes else "",
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                     font=font("xs")).pack()
            # Bar
            bar_h = max(int((minutes / max_val) * 80), 4) if minutes else 4
            bar_color = COLORS["accent_rust"] if minutes else COLORS["bg_elevated"]
            bar_frame = tk.Frame(col, bg=COLORS["bg_card"], height=80)
            bar_frame.pack(fill="x")
            bar_frame.pack_propagate(False)
            bar = tk.Frame(bar_frame, bg=bar_color, width=28, height=bar_h)
            bar.place(relx=0.5, rely=1.0, anchor="s")
            # Day label
            tk.Label(col, text=day_label, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("xs")).pack()

    def _open_log(self):
        if not self._pet: return
        ActivityDialog(self, self._pet.id,
                       on_save=lambda d: self.cb_add_log and self.cb_add_log(d))

    def _clear_content(self):
        for w in self._content.winfo_children(): w.destroy()