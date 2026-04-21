"""
views/pages/health.py — Kendra Pro
"""
import tkinter as tk
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, StatCard, section_label, primary_btn, ghost_btn,
    form_label, styled_entry, styled_combobox, EmptyState, NoPetWidget, page_header
)


class WeightDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, on_save=None):
        super().__init__(parent)
        self.pet_id = pet_id
        self._on_save = on_save
        self.title("Log Weight")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        bg = COLORS["bg_surface"]
        tk.Label(self, text="Log Weight", bg=bg, fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 16))

        row = tk.Frame(self, bg=bg)
        row.pack(fill="x", padx=24, pady=(0, 12))

        w = tk.Frame(row, bg=bg)
        w.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(w, "Weight", bg=bg).pack(anchor="w")
        self._weight_f = styled_entry(w, width=10, bg=bg)
        self._weight_f.pack(fill="x", pady=(4, 0))
        self._weight_f.set("5.0")

        u = tk.Frame(row, bg=bg)
        u.pack(side="left")
        form_label(u, "Unit", bg=bg).pack(anchor="w")
        self._unit_var = tk.StringVar(value="kg")
        styled_combobox(u, ["kg", "lbs"], self._unit_var, width=6).pack(pady=(4, 0))

        form_label(self, "Date (YYYY-MM-DD)", bg=bg).pack(anchor="w", padx=24)
        from datetime import date
        self._date_f = styled_entry(self, bg=bg)
        self._date_f.pack(fill="x", padx=24, pady=(4, 12))
        self._date_f.set(str(date.today()))

        form_label(self, "Notes", bg=bg).pack(anchor="w", padx=24)
        self._notes_f = styled_entry(self, placeholder="Vet visit…", bg=bg)
        self._notes_f.pack(fill="x", padx=24, pady=(4, 16))

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 12))
        acts = tk.Frame(self, bg=bg)
        acts.pack(fill="x", padx=24, pady=(0, 20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8, 0))
        def submit():
            if self._on_save:
                self._on_save({
                    "pet_id": self.pet_id,
                    "weight": float(self._weight_f.get() or 0),
                    "unit": self._unit_var.get(),
                    "date": self._date_f.get().strip() or None,
                    "notes": self._notes_f.get().strip() or None,
                })
            self.destroy()
        primary_btn(acts, "Log Weight", submit).pack(side="right")


class HealthPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet = None
        self._logs = []
        self._stats = {}
        self.cb_log_weight = None
        self.cb_delete_weight = None

        self._hdr = page_header(self, "Health & Weight", action_text="＋  Log Weight",
                                action_cmd=self._open_log)
        self._hdr.pack(fill="x", padx=32, pady=(28, 0))
        self._subtitle = tk.Label(self, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_secondary"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x", padx=32, pady=(2, 16))

        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32, pady=(0, 24))

    def show_no_pet(self):
        self._clear()
        NoPetWidget(self._content, "health").pack(fill="both", expand=True)

    def load(self, pet, logs, stats):
        self._pet = pet
        self._logs = logs
        self._stats = stats
        self._subtitle.config(text=f"{pet.name}'s weight history")
        self._refresh()

    def _refresh(self):
        self._clear()
        # Stat row
        if self._stats.get("total_entries", 0) > 0:
            sr = tk.Frame(self._content, bg=COLORS["bg_base"])
            sr.pack(fill="x", pady=(0, 20))
            unit = self._stats.get("unit", "kg")
            latest = self._stats.get("latest_weight", "—")
            change = None
            if len(self._logs) >= 2:
                change = round(self._logs[0].weight - self._logs[-1].weight, 1)
            change_str = (f"+{change}" if change and change > 0 else str(change)) if change is not None else "—"
            change_color = COLORS["accent_red"] if change and change > 0 else COLORS["accent_green"]

            for val, lbl, col in [
                (str(latest), f"Current ({unit})", COLORS["accent"]),
                (str(self._stats.get("min_weight", "—")), "Lowest", COLORS["accent_green"]),
                (str(self._stats.get("max_weight", "—")), "Highest", COLORS["accent_amber"]),
                (change_str, "Change", change_color),
            ]:
                StatCard(sr, val, lbl, color=col).pack(
                    side="left", fill="x", expand=True, padx=(0, 8)
                )

        if not self._logs:
            EmptyState(self._content, "⚖️", "No weight entries yet",
                       "Start logging to track your pet's weight over time.",
                       bg=COLORS["bg_base"]).pack(fill="both", expand=True, pady=40)
            return

        section_label(self._content, "Weight History").pack(anchor="w", pady=(0, 8))
        sf = ScrollableFrame(self._content, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame

        for log in self._logs:
            row = tk.Frame(f, bg=COLORS["bg_surface"])
            row.pack(fill="x", pady=(0, 1))
            tk.Frame(row, bg=COLORS["accent"], width=3).pack(side="left", fill="y")
            inner = tk.Frame(row, bg=COLORS["bg_surface"], padx=14, pady=10)
            inner.pack(side="left", fill="both", expand=True)

            tk.Label(inner, text=f"{log.weight} {log.unit}",
                     bg=COLORS["bg_surface"], fg=COLORS["accent"],
                     font=font("lg", "bold")).pack(side="left", padx=(0, 14))

            info = tk.Frame(inner, bg=COLORS["bg_surface"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=log.date, bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"], font=font("sm", "bold"),
                     anchor="w").pack(fill="x")
            if log.notes:
                tk.Label(info, text=log.notes, bg=COLORS["bg_surface"],
                         fg=COLORS["text_muted"], font=font("xs"),
                         anchor="w").pack(fill="x")

            ghost_btn(inner, "✕",
                      command=lambda lid=log.id: self.cb_delete_weight and self.cb_delete_weight(lid),
                      fg=COLORS["accent_red"]).pack(side="right")

    def _open_log(self):
        if not self._pet: return
        WeightDialog(self, self._pet.id,
                     on_save=lambda d: self.cb_log_weight and self.cb_log_weight(d))

    def _clear(self):
        for w in self._content.winfo_children(): w.destroy()