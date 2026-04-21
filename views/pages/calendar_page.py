"""
views/pages/calendar_page.py — Kendra Pro
"""
import tkinter as tk
from tkcalendar import Calendar
from assets.styles.theme import COLORS, font
from views.pages.base import ScrollableFrame, section_label, ghost_btn, page_header
from models.database import get_db

TYPE_COLORS = {
    "feeding":    COLORS["accent_amber"],
    "medication": COLORS["accent_green"],
    "grooming":   COLORS["accent_purple"],
    "birthday":   COLORS["accent_orange"],
}
TYPE_ICONS = {
    "feeding": "🍽", "medication": "💊",
    "grooming": "✂", "birthday": "🎂",
}


def _get_events(date_str):
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
        hdr = page_header(self, "Calendar",
                          subtitle="All schedules and events at a glance")
        hdr.pack(fill="x", padx=32, pady=(28, 20))

        body = tk.Frame(self, bg=COLORS["bg_base"])
        body.pack(fill="both", expand=True, padx=32, pady=(0, 32))

        # Left: calendar
        left = tk.Frame(body, bg=COLORS["bg_base"])
        left.pack(side="left", fill="y", padx=(0, 24))

        self._cal = Calendar(
            left,
            selectmode="day",
            background=COLORS["bg_surface"],
            foreground=COLORS["text_primary"],
            headersbackground=COLORS["bg_elevated"],
            headersforeground=COLORS["accent"],
            selectbackground=COLORS["accent"],
            selectforeground=COLORS["text_inverse"],
            weekendbackground=COLORS["bg_surface"],
            weekendforeground=COLORS["text_secondary"],
            othermonthbackground=COLORS["bg_base"],
            othermonthforeground=COLORS["text_muted"],
            font=font("sm"),
            bordercolor=COLORS["border"],
            normalbackground=COLORS["bg_surface"],
            normalforeground=COLORS["text_primary"],
        )
        self._cal.pack()
        self._cal.bind("<<CalendarSelected>>", self._on_date_change)

        # Right: events
        right = tk.Frame(body, bg=COLORS["bg_base"])
        right.pack(side="left", fill="both", expand=True)

        self._event_title = tk.Label(
            right, text="Today's Events",
            bg=COLORS["bg_base"], fg=COLORS["text_primary"],
            font=font("lg", "bold"), anchor="w",
        )
        self._event_title.pack(fill="x", pady=(0, 12))

        self._sf = ScrollableFrame(right, bg=COLORS["bg_base"])
        self._sf.pack(fill="both", expand=True)

        self._on_date_change()

    def _on_date_change(self, event=None):
        date_str = self._cal.get_date()
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%m/%d/%y")
            date_str = dt.strftime("%Y-%m-%d")
            self._event_title.config(text=f"Events — {dt.strftime('%B %d, %Y')}")
        except Exception:
            self._event_title.config(text="Events")

        f = self._sf.scrollable_frame
        for w in f.winfo_children(): w.destroy()

        events = _get_events(date_str)
        if not events:
            tk.Label(f, text="No events for this day.",
                     bg=COLORS["bg_base"], fg=COLORS["text_secondary"],
                     font=font("sm")).pack(pady=30)
            return

        for ev in events:
            color = TYPE_COLORS.get(ev["type"], COLORS["accent"])
            icon  = TYPE_ICONS.get(ev["type"], "🔔")

            row = tk.Frame(f, bg=COLORS["bg_surface"])
            row.pack(fill="x", pady=(0, 1))
            tk.Frame(row, bg=color, width=3).pack(side="left", fill="y")
            inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)

            tk.Label(inner, text=icon, bg=COLORS["bg_surface"],
                     fg=color, font=font("base")).pack(side="left", padx=(0, 10))

            info = tk.Frame(inner, bg=COLORS["bg_surface"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=ev.get("meal_name", ""), bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"], font=font("sm", "bold"),
                     anchor="w").pack(fill="x")
            tk.Label(info, text=ev.get("pet_name", ""), bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"], font=font("xs"),
                     anchor="w").pack(fill="x")

            if ev.get("time"):
                tk.Label(inner, text=ev["time"], bg=COLORS["bg_surface"],
                         fg=COLORS["text_muted"], font=font("xs")).pack(side="right")

    def load(self):
        self._on_date_change()