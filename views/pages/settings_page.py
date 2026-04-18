"""
views/pages/settings_page.py
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from assets.styles.theme import COLORS, font
from views.pages.base import primary_btn, section_label, body_label


class SettingsPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self.cb_export = None
        self._build()

    def _build(self):
        tk.Label(self, text="Settings", bg=COLORS["bg_base"],
                 fg=COLORS["text_primary"], font=font("hero","bold")).pack(
                 anchor="w", padx=36, pady=(32,4))
        tk.Label(self, text="Export data and manage preferences",
                 bg=COLORS["bg_base"], fg=COLORS["text_muted"],
                 font=font("sm")).pack(anchor="w", padx=36, pady=(0,24))

        # Export card
        section_label(self, "Export Data").pack(anchor="w", padx=36, pady=(0,8))
        card = tk.Frame(self, bg=COLORS["bg_card"], padx=20, pady=16)
        card.pack(fill="x", padx=36, pady=(0,24))
        tk.Label(card,
                 text="Export your pet data as CSV files.\n"
                      "One file per category: feeding, medications, weight, activity, grooming.",
                 bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                 font=font("sm"), justify="left", anchor="w",
                 wraplength=500).pack(anchor="w", pady=(0,12))
        primary_btn(card, "📄  Export as CSV", self._on_export).pack(anchor="w")

        # Reminder prefs card
        section_label(self, "Reminder Preferences").pack(anchor="w", padx=36, pady=(0,8))
        pref = tk.Frame(self, bg=COLORS["bg_card"], padx=20, pady=16)
        pref.pack(fill="x", padx=36)
        row = tk.Frame(pref, bg=COLORS["bg_card"])
        row.pack(anchor="w")
        tk.Label(row, text="Remind me", bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=font("base")).pack(side="left")
        self._lead_var = tk.StringVar(value="5")
        lead_entry = tk.Entry(row, textvariable=self._lead_var,
                              bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                              font=font("base"), relief="flat", bd=4, width=5)
        lead_entry.pack(side="left", padx=8)
        tk.Label(row, text="minutes before scheduled time",
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                 font=font("base")).pack(side="left")

    def _on_export(self):
        folder = filedialog.askdirectory(title="Choose Export Folder")
        if folder and self.cb_export:
            self.cb_export("csv", folder)