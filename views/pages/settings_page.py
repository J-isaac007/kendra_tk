"""
views/pages/settings_page.py — Kendra Pro
"""
import os
import tkinter as tk
from tkinter import filedialog
from assets.styles.theme import COLORS, font
from views.pages.base import primary_btn, section_label, page_header


class SettingsPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self.cb_export = None
        self._build()

    def _build(self):
        bg = COLORS["bg_base"]

        hdr = page_header(self, "Settings",
                          subtitle="Export data and manage preferences")
        hdr.pack(fill="x", padx=32, pady=(28, 24))

        # Export section
        section_label(self, "Data Export").pack(anchor="w", padx=32, pady=(0, 8))

        card = tk.Frame(self, bg=COLORS["bg_border"])
        card.pack(fill="x", padx=32, pady=(0, 24))
        inner = tk.Frame(card, bg=COLORS["bg_surface"], padx=20, pady=16)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(inner,
                 text="Export your pet data as CSV files. One file per category:\n"
                      "feeding logs, medication logs, weight history, activity logs.",
                 bg=COLORS["bg_surface"], fg=COLORS["text_secondary"],
                 font=font("sm"), justify="left", anchor="w",
                 wraplength=520).pack(anchor="w", pady=(0, 14))

        primary_btn(inner, "📄  Export as CSV", self._on_export).pack(anchor="w")

        # Preferences
        section_label(self, "Reminder Preferences").pack(anchor="w", padx=32, pady=(0, 8))

        pref_card = tk.Frame(self, bg=COLORS["bg_border"])
        pref_card.pack(fill="x", padx=32)
        pref_inner = tk.Frame(pref_card, bg=COLORS["bg_surface"], padx=20, pady=16)
        pref_inner.pack(fill="both", expand=True, padx=1, pady=1)

        row = tk.Frame(pref_inner, bg=COLORS["bg_surface"])
        row.pack(anchor="w")

        tk.Label(row, text="Remind me",
                 bg=COLORS["bg_surface"], fg=COLORS["text_primary"],
                 font=font("sm")).pack(side="left")

        self._lead_var = tk.StringVar(value="5")
        entry = tk.Entry(row, textvariable=self._lead_var,
                         bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                         insertbackground=COLORS["accent"],
                         font=font("sm"), relief="flat", bd=6, width=4)
        entry.pack(side="left", padx=10)

        tk.Label(row, text="minutes before scheduled time",
                 bg=COLORS["bg_surface"], fg=COLORS["text_secondary"],
                 font=font("sm")).pack(side="left")

    def _on_export(self):
        folder = filedialog.askdirectory(title="Choose Export Folder")
        if folder and self.cb_export:
            self.cb_export("csv", folder)