"""
views/pages/health.py
"""
import tkinter as tk
from assets.styles.theme import COLORS, font
from views.pages.base import (
    ScrollableFrame, StatCard, section_label, primary_btn,
    ghost_btn, form_label, styled_entry, styled_combobox,
    EmptyState, NoPetWidget
)


class WeightDialog(tk.Toplevel):
    def __init__(self, parent, pet_id, on_save=None):
        super().__init__(parent)
        self.pet_id  = pet_id
        self._on_save = on_save
        self.title("Log Weight")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        tk.Label(self, text="Log Weight", bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=font("lg","bold")).pack(
                 anchor="w", padx=20, pady=(20,8))
        row = tk.Frame(self, bg=COLORS["bg_card"])
        row.pack(fill="x", padx=20, pady=(0,8))
        w_col = tk.Frame(row, bg=COLORS["bg_card"])
        w_col.pack(side="left", fill="x", expand=True, padx=(0,10))
        form_label(w_col, "Weight").pack(anchor="w")
        self._weight_var = tk.StringVar(value="5.0")
        styled_entry(w_col, self._weight_var, width=10).pack(fill="x")
        u_col = tk.Frame(row, bg=COLORS["bg_card"])
        u_col.pack(side="left")
        form_label(u_col, "Unit").pack(anchor="w")
        self._unit_var = tk.StringVar(value="kg")
        styled_combobox(u_col, ["kg","lbs"], self._unit_var, width=6).pack(fill="x")
        form_label(self, "Date (YYYY-MM-DD)").pack(anchor="w", padx=20)
        from datetime import date
        self._date_var = tk.StringVar(value=str(date.today()))
        styled_entry(self, self._date_var).pack(fill="x", padx=20, pady=(0,8))
        form_label(self, "Notes").pack(anchor="w", padx=20)
        self._notes_var = tk.StringVar()
        styled_entry(self, self._notes_var, placeholder="Vet visit…").pack(fill="x", padx=20, pady=(0,12))
        acts = tk.Frame(self, bg=COLORS["bg_card"])
        acts.pack(fill="x", padx=20, pady=(0,20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8,0))
        def submit():
            if self._on_save:
                self._on_save({
                    "pet_id": self.pet_id,
                    "weight": float(self._weight_var.get() or 0),
                    "unit":   self._unit_var.get(),
                    "date":   self._date_var.get().strip() or None,
                    "notes":  self._notes_var.get().strip() or None,
                })
            self.destroy()
        primary_btn(acts, "Log Weight", submit).pack(side="right")


class HealthPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._pet   = None
        self._logs  = []
        self._stats = {}
        self.cb_log_weight    = None
        self.cb_delete_weight = None
        self._build_header()
        self._content = tk.Frame(self, bg=COLORS["bg_base"])
        self._content.pack(fill="both", expand=True, padx=32)

    def _build_header(self):
        hdr = tk.Frame(self, bg=COLORS["bg_base"])
        hdr.pack(fill="x", padx=32, pady=(32,16))
        left = tk.Frame(hdr, bg=COLORS["bg_base"])
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="Health & Weight", bg=COLORS["bg_base"],
                 fg=COLORS["text_primary"], font=font("hero","bold"), anchor="w").pack(fill="x")
        self._subtitle = tk.Label(left, text="", bg=COLORS["bg_base"],
                                  fg=COLORS["text_muted"], font=font("sm"), anchor="w")
        self._subtitle.pack(fill="x")
        primary_btn(hdr, "＋  Log Weight", self._open_log).pack(side="right", anchor="n")

    def show_no_pet(self):
        self._clear_content()
        NoPetWidget(self._content, "health").pack(fill="both", expand=True)

    def load(self, pet, logs, stats):
        self._pet   = pet
        self._logs  = logs
        self._stats = stats
        self._subtitle.config(text=f"{pet.name}'s weight history")
        self._refresh()

    def _refresh(self):
        self._clear_content()
        if self._stats.get("total_entries", 0) > 0:
            sr = tk.Frame(self._content, bg=COLORS["bg_base"])
            sr.pack(fill="x", pady=(0,16))
            unit = self._stats.get("unit","kg")
            latest = self._stats.get("latest_weight","—")
            change = None
            if len(self._logs) >= 2:
                change = round(self._logs[0].weight - self._logs[-1].weight, 1)
            for val, lbl in [
                (str(latest), f"Current ({unit})"),
                (str(self._stats.get("min_weight","—")), "Lowest"),
                (str(self._stats.get("max_weight","—")), "Highest"),
                ((f"+{change}" if change and change>0 else str(change)) if change is not None else "—", "Change"),
            ]:
                card = StatCard(sr, val, lbl)
                card.pack(side="left", fill="x", expand=True, padx=(0,8))
        if not self._logs:
            EmptyState(self._content, "⚖️", "No weight entries yet",
                       "Start logging to see trends.").pack(fill="both", expand=True, pady=40)
            return
        section_label(self._content, "Weight History").pack(anchor="w", pady=(8,8))
        sf = ScrollableFrame(self._content, bg=COLORS["bg_base"])
        sf.pack(fill="both", expand=True)
        f = sf.scrollable_frame
        for log in self._logs:
            row = tk.Frame(f, bg=COLORS["bg_card"], pady=12, padx=14)
            row.pack(fill="x", pady=(0,6))
            tk.Label(row, text=f"{log.weight}",
                     bg=COLORS["bg_card"], fg=COLORS["accent_gold"],
                     font=font("xl","bold")).pack(side="left", padx=(0,4))
            tk.Label(row, text=log.unit, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("sm")).pack(side="left", padx=(0,14))
            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=log.date, bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"], font=font("base","bold"), anchor="w").pack(fill="x")
            if log.notes:
                tk.Label(info, text=log.notes, bg=COLORS["bg_card"],
                         fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
            ghost_btn(row, "✕", command=lambda lid=log.id: self.cb_delete_weight and self.cb_delete_weight(lid)).pack(side="right")

    def _open_log(self):
        if not self._pet: return
        WeightDialog(self, self._pet.id,
                     on_save=lambda d: self.cb_log_weight and self.cb_log_weight(d))

    def _clear_content(self):
        for w in self._content.winfo_children(): w.destroy()