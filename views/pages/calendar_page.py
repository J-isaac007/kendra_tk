"""
views/pages/calendar_page.py
"""
import tkinter as tk
from tkcalendar import Calendar
from assets.styles.theme import COLORS, font
from views.pages.base import ScrollableFrame, section_label, ghost_btn
from models.database import get_db

TYPE_COLORS = {
    "feeding":    COLORS["accent_gold"],
    "medication": COLORS["accent_sage"],
    "grooming":   COLORS["accent_lavender"],
    "birthday":   COLORS["accent_rust"],
}
TYPE_ICONS = {
    "feeding": "🍽", "medication": "💊",
    "grooming": "✂", "birthday": "🎂",
}


def _get_events(date_str: str) -> list[dict]:
    conn = get_db()
    events = []
    rows = conn.execute(
        "SELECT fs.meal_name,fs.time,p.name as pet_name,'feeding' as type "
        "FROM feeding_schedules fs JOIN pets p ON p.id=fs.pet_id WHERE fs.active=1"
    ).fetchall()
    for r in rows: events.append(dict(r))
    rows = conn.execute(
        "SELECT m.name as meal_name,m.time,p.name as pet_name,'medication' as type "
        "FROM medications m JOIN pets p ON p.id=m.pet_id "
        "WHERE m.active=1 AND m.start_date<=? AND (m.end_date IS NULL OR m.end_date>=?)",
        (date_str, date_str)
    ).fetchall()
    for r in rows: events.append(dict(r))
    rows = conn.execute(
        "SELECT gt.task_name as meal_name,null as time,p.name as pet_name,'grooming' as type "
        "FROM grooming_tasks gt JOIN pets p ON p.id=gt.pet_id "
        "WHERE gt.active=1 AND gt.next_due=?", (date_str,)
    ).fetchall()
    for r in rows: events.append(dict(r))
    rows = conn.execute("SELECT name,birthday FROM pets WHERE birthday IS NOT NULL").fetchall()
    for r in rows:
        try:
            from datetime import datetime
            bday = datetime.strptime(r["birthday"], "%Y-%m-%d")
            ds   = datetime.strptime(date_str, "%Y-%m-%d")
            if bday.month == ds.month and bday.day == ds.day:
                events.append({"meal_name": f"{r['name']}'s Birthday! 🎂",
                                "time": None, "pet_name": r["name"], "type": "birthday"})
        except Exception: pass
    conn.close()
    return events


class CalendarPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS["bg_base"])
        hdr.pack(fill="x", padx=36, pady=(32, 16))
        tk.Label(hdr, text="Calendar", bg=COLORS["bg_base"],
                 fg=COLORS["text_primary"], font=font("hero","bold")).pack(anchor="w")
        tk.Label(hdr, text="All schedules and events at a glance",
                 bg=COLORS["bg_base"], fg=COLORS["text_muted"], font=font("sm")).pack(anchor="w")

        body = tk.Frame(self, bg=COLORS["bg_base"])
        body.pack(fill="both", expand=True, padx=36, pady=(0,32))

        # Calendar widget
        left = tk.Frame(body, bg=COLORS["bg_base"])
        left.pack(side="left", fill="y", padx=(0, 24))

        self._cal = Calendar(
            left,
            selectmode="day",
            background=COLORS["bg_card"],
            foreground=COLORS["text_primary"],
            headersbackground=COLORS["bg_elevated"],
            headersforeground=COLORS["accent_gold"],
            selectbackground=COLORS["accent_gold"],
            selectforeground=COLORS["text_inverse"],
            weekendbackground=COLORS["bg_card"],
            weekendforeground=COLORS["text_secondary"],
            othermonthbackground=COLORS["bg_surface"],
            othermonthforeground=COLORS["text_muted"],
            font=font("base"),
            bordercolor=COLORS["border"],
            normalbackground=COLORS["bg_card"],
            normalforeground=COLORS["text_primary"],
        )
        self._cal.pack()
        self._cal.bind("<<CalendarSelected>>", self._on_date_change)

        # Events panel
        right = tk.Frame(body, bg=COLORS["bg_base"])
        right.pack(side="left", fill="both", expand=True)

        self._event_title = tk.Label(
            right, text="Today's Events",
            bg=COLORS["bg_base"], fg=COLORS["text_primary"],
            font=font("lg","bold"), anchor="w",
        )
        self._event_title.pack(fill="x", pady=(0,12))

        self._events_frame = ScrollableFrame(right, bg=COLORS["bg_base"])
        self._events_frame.pack(fill="both", expand=True)

        self._on_date_change()

    def _on_date_change(self, event=None):
        date_str = self._cal.get_date()
        # tkcalendar returns MM/DD/YY — convert to YYYY-MM-DD
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%m/%d/%y")
            date_str = dt.strftime("%Y-%m-%d")
            self._event_title.config(text=f"Events — {dt.strftime('%B %d, %Y')}")
        except Exception:
            self._event_title.config(text="Events")

        f = self._events_frame.scrollable_frame
        for w in f.winfo_children(): w.destroy()

        events = _get_events(date_str)
        if not events:
            tk.Label(f, text="No events for this day.",
                     bg=COLORS["bg_base"], fg=COLORS["text_muted"],
                     font=font("base")).pack(pady=30)
            return

        for ev in events:
            row = tk.Frame(f, bg=COLORS["bg_card"], pady=10, padx=12)
            row.pack(fill="x", pady=(0,8))
            color = TYPE_COLORS.get(ev["type"], COLORS["accent_gold"])
            icon  = TYPE_ICONS.get(ev["type"], "🔔")
            tk.Label(row, text=icon, bg=COLORS["bg_elevated"],
                     font=font("md"), padx=6, pady=4).pack(side="left", padx=(0,10))
            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=ev.get("meal_name",""), bg=COLORS["bg_card"],
                     fg=color, font=font("base","bold"), anchor="w").pack(fill="x")
            tk.Label(info, text=ev.get("pet_name",""), bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
            if ev.get("time"):
                tk.Label(row, text=ev["time"], bg=COLORS["bg_card"],
                         fg=COLORS["text_muted"], font=font("sm")).pack(side="right")

    def load(self):
        self._on_date_change()