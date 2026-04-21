"""
views/pages/activity.py — Kendra Pro
"""
import tkinter as tk
from datetime import date, timedelta
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, StatCard, primary_btn, ghost_btn,
    form_label, styled_entry, styled_combobox,
    section_label, EmptyState, NoPetWidget, page_header
)

ACTIVITY_TYPES = ["Walk", "Run", "Play", "Training", "Swim",
                  "Fetch", "Agility", "Socialization", "Other"]

TYPE_COLORS = {
    "Walk":     COLORS["accent"],
    "Run":      COLORS["accent_red"],
    "Play":     COLORS["accent_green"],
    "Training": COLORS["accent_purple"],
    "Swim":     COLORS["accent"],
    "Fetch":    COLORS["accent_orange"],
}


def _fmt(minutes) -> str:
    minutes = int(minutes or 0)
    if minutes == 0: return "0 min"
    h, m = minutes // 60, minutes % 60
    return f"{h}h {m}m" if h and m else (f"{h}h" if h else f"{m} min")


class ActivityDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, on_save=None):
        super().__init__(parent)
        self.pet_id = pet_id
        self._on_save = on_save
        self.title("Log Activity")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        bg = COLORS["bg_surface"]
        tk.Label(self, text="Log Activity", bg=bg, fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 16))

        form_label(self, "Activity Type", bg=bg).pack(anchor="w", padx=24)
        self._type_var = tk.StringVar(value="Walk")

        chips = tk.Frame(self, bg=bg)
        chips.pack(fill="x", padx=24, pady=(4, 12))
        self._type_btns = {}
        for atype in ACTIVITY_TYPES:
            btn = tk.Button(chips, text=atype, bg=COLORS["bg_elevated"],
                            fg=COLORS["text_secondary"], font=font("xs"),
                            relief="flat", bd=0, padx=8, pady=4, cursor="hand2",
                            command=lambda t=atype: self._select(t))
            btn.pack(side="left", padx=(0, 4), pady=(0, 4))
            self._type_btns[atype] = btn
        self._select("Walk")

        row = tk.Frame(self, bg=bg)
        row.pack(fill="x", padx=24, pady=(0, 12))

        d_col = tk.Frame(row, bg=bg)
        d_col.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(d_col, "Duration (minutes)", bg=bg).pack(anchor="w")
        self._dur_f = styled_entry(d_col, width=8, bg=bg)
        self._dur_f.pack(fill="x", pady=(4, 0))
        self._dur_f.set("30")

        dt_col = tk.Frame(row, bg=bg)
        dt_col.pack(side="left", fill="x", expand=True)
        form_label(dt_col, "Date", bg=bg).pack(anchor="w")
        self._date_f = styled_entry(dt_col, width=14, bg=bg)
        self._date_f.pack(fill="x", pady=(4, 0))
        self._date_f.set(str(date.today()))

        form_label(self, "Notes", bg=bg).pack(anchor="w", padx=24)
        self._notes_f = styled_entry(self, placeholder="Off-leash at the park…", bg=bg)
        self._notes_f.pack(fill="x", padx=24, pady=(4, 16))

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 12))
        acts = tk.Frame(self, bg=bg)
        acts.pack(fill="x", padx=24, pady=(0, 20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8, 0))
        def submit():
            if self._on_save:
                self._on_save({
                    "pet_id": self.pet_id,
                    "activity_type": self._type_var.get(),
                    "duration_minutes": int(self._dur_f.get() or 30),
                    "date": self._date_f.get().strip() or None,
                    "notes": self._notes_f.get().strip() or None,
                })
            self.destroy()
        primary_btn(acts, "Log Activity", submit).pack(side="right")

    def _select(self, selected):
        self._type_var.set(selected)
        color = TYPE_COLORS.get(selected, COLORS["accent"])
        for atype, btn in self._type_btns.items():
            if atype == selected:
                btn.config(bg=COLORS["bg_hover"], fg=color)
            else:
                btn.config(bg=COLORS["bg_elevated"], fg=COLORS["text_secondary"])


class ActivityPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet = None
        self._logs = []
        self._stats = {}
        self._weekly = []
        self.cb_add_log = None
        self.cb_delete_log = None

        self._hdr = page_header(self, "Activity", action_text="＋  Log Activity",
                                action_cmd=self._open_log)
        self._hdr.pack(fill="x", padx=32, pady=(28, 0))
        self._subtitle = tk.Label(self, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_secondary"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x", padx=32, pady=(2, 16))

        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32, pady=(0, 24))

    def show_no_pet(self):
        self._clear()
        NoPetWidget(self._content, "activity").pack(fill="both", expand=True)

    def load(self, pet, logs, stats, weekly):
        self._pet = pet
        self._logs = logs
        self._stats = stats
        self._weekly = weekly
        self._subtitle.config(text=f"{pet.name}'s exercise log")
        self._refresh()

    def _refresh(self):
        self._clear()
        # Stat row
        sr = tk.Frame(self._content, bg=COLORS["bg_base"])
        sr.pack(fill="x", pady=(0, 20))
        StatCard(sr, _fmt(self._stats.get("total_minutes_week") or 0),
                 "This Week", color=COLORS["accent"]).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        StatCard(sr, str(self._stats.get("sessions_week") or 0),
                 "Sessions", color=COLORS["accent_green"]).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        StatCard(sr, _fmt(self._stats.get("avg_duration") or 0),
                 "Avg Duration", color=COLORS["accent_purple"]).pack(
            side="left", fill="x", expand=True)

        # Bar chart
        if self._weekly:
            section_label(self._content, "Weekly Activity").pack(anchor="w", pady=(0, 8))
            self._build_chart()

        if not self._logs:
            EmptyState(self._content, "🏃", "No activity logged yet",
                       "Track walks, play sessions, training, and more.",
                       bg=COLORS["bg_base"]).pack(fill="both", expand=True, pady=40)
            return

        section_label(self._content, "Recent Activity").pack(anchor="w", pady=(16, 8))
        sf = ScrollableFrame(self._content, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame

        for log in self._logs:
            color = TYPE_COLORS.get(log.activity_type, COLORS["accent_orange"])
            row = tk.Frame(f, bg=COLORS["bg_surface"])
            row.pack(fill="x", pady=(0, 1))
            tk.Frame(row, bg=color, width=3).pack(side="left", fill="y")
            inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)

            # Type initial
            init = tk.Label(inner, text=log.activity_type[0].upper(),
                            bg=COLORS["bg_elevated"], fg=color,
                            font=font("sm", "bold"), width=3)
            init.pack(side="left", padx=(0, 12))

            info = tk.Frame(inner, bg=COLORS["bg_surface"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=log.activity_type, bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"], font=font("sm", "bold"),
                     anchor="w").pack(fill="x")
            meta = log.date + (f"  ·  {log.notes}" if log.notes else "")
            tk.Label(info, text=meta, bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"], font=font("xs"), anchor="w").pack(fill="x")

            tk.Label(inner, text=_fmt(log.duration_minutes),
                     bg=COLORS["bg_surface"], fg=color,
                     font=font("md", "bold")).pack(side="right", padx=(0, 12))
            ghost_btn(inner, "✕",
                      command=lambda lid=log.id: self.cb_delete_log and self.cb_delete_log(lid),
                      fg=COLORS["accent_red"]).pack(side="right")

    def _build_chart(self):
        day_map = {e["date"]: e["total_minutes"] for e in self._weekly}
        days_data = []
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            days_data.append((d.strftime("%a"), day_map.get(str(d), 0)))

        max_val = max((m for _, m in days_data), default=1) or 1
        chart = tk.Frame(self._content, bg=COLORS["bg_surface"], pady=16)
        chart.pack(fill="x", pady=(0, 16))

        for day_label, minutes in days_data:
            col = tk.Frame(chart, bg=COLORS["bg_surface"])
            col.pack(side="left", fill="x", expand=True, padx=6)

            tk.Label(col, text=_fmt(minutes) if minutes else "",
                     bg=COLORS["bg_surface"], fg=COLORS["text_muted"],
                     font=font("xs")).pack()

            bar_frame = tk.Frame(col, bg=COLORS["bg_elevated"], height=80)
            bar_frame.pack(fill="x", pady=2)
            bar_frame.pack_propagate(False)

            if minutes:
                bar_h = max(int((minutes / max_val) * 80), 6)
                bar = tk.Frame(bar_frame, bg=COLORS["accent"], width=24, height=bar_h)
                bar.place(relx=0.5, rely=1.0, anchor="s")

            tk.Label(col, text=day_label, bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"], font=font("xs")).pack()

    def _open_log(self):
        if not self._pet: return
        ActivityDialog(self, self._pet.id,
                       on_save=lambda d: self.cb_add_log and self.cb_add_log(d))

    def _clear(self):
        for w in self._content.winfo_children(): w.destroy()