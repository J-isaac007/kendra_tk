"""
views/pages/dashboard.py — Kendra Pro
Clean 2-column pet cards, professional stat pills, quick access rows.
No ScrollableFrame wrapping the whole page — only list areas scroll.
"""
import os
import tkinter as tk
from datetime import datetime, date
from PIL import Image, ImageTk, ImageDraw

from assets.styles.theme import COLORS, font, font_size
from views.pages.base import (
    primary_btn, ghost_btn, section_label,
    body_label, muted_label, BorderCard, divider, page_header
)

SPECIES_EMOJI = {
    "dog": "🐶", "cat": "🐱", "bird": "🦜", "fish": "🐠",
    "rabbit": "🐰", "hamster": "🐹", "guinea pig": "🐹",
    "reptile": "🦎", "turtle": "🐢", "ferret": "🦡",
}

QUICK_NAV = [
    ("feeding",     "🍽",  "Feeding",     COLORS["accent_amber"]),
    ("medications", "💊",  "Medications", COLORS["accent_green"]),
    ("grooming",    "✂",   "Grooming",    COLORS["accent_purple"]),
    ("activity",    "🏃",  "Activity",    COLORS["accent_orange"]),
]


def _circular_photo(path: str, size: int) -> ImageTk.PhotoImage:
    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return ImageTk.PhotoImage(result)


class PetCard(tk.Frame):
    """Clean professional pet card."""

    def __init__(self, parent, pet, summary: dict,
                 on_navigate, **kwargs):
        super().__init__(
            parent, bg=COLORS["bg_border"],
            **kwargs
        )
        self._photo_ref = None
        # Inner card
        self._inner = tk.Frame(self, bg=COLORS["bg_surface"], padx=18, pady=16)
        self._inner.pack(fill="both", expand=True, padx=1, pady=1)
        self._build(pet, summary, on_navigate)

    def _build(self, pet, summary, on_navigate):
        bg = COLORS["bg_surface"]

        # ── Header ───────────────────────────────────────────────
        header = tk.Frame(self._inner, bg=bg)
        header.pack(fill="x", pady=(0, 12))

        # Avatar circle
        avatar = tk.Frame(header, bg=COLORS["bg_elevated"],
                          width=40, height=40)
        avatar.pack(side="left", padx=(0, 12))
        avatar.pack_propagate(False)

        photo_loaded = False
        if pet.photo_path and os.path.exists(pet.photo_path):
            try:
                self._photo_ref = _circular_photo(pet.photo_path, 40)
                tk.Label(avatar, image=self._photo_ref,
                         bg=COLORS["bg_elevated"]).place(
                    relx=0.5, rely=0.5, anchor="center"
                )
                photo_loaded = True
            except Exception:
                pass

        if not photo_loaded:
            emoji = SPECIES_EMOJI.get((pet.species or "").lower(), "🐾")
            tk.Label(avatar, text=emoji, bg=COLORS["bg_elevated"],
                     font=(font()[0], 18)).place(
                relx=0.5, rely=0.5, anchor="center"
            )

        # Name + breed
        name_col = tk.Frame(header, bg=bg)
        name_col.pack(side="left", fill="x", expand=True)

        tk.Label(name_col, text=pet.name, bg=bg,
                 fg=COLORS["text_primary"],
                 font=font("md", "bold"), anchor="w").pack(fill="x")

        age_str = ""
        if pet.birthday:
            try:
                age = int((datetime.today() -
                           datetime.strptime(pet.birthday, "%Y-%m-%d")).days / 365.25)
                age_str = f" · {age}yr"
            except Exception:
                pass

        tk.Label(name_col,
                 text=f"{(pet.breed or pet.species).capitalize()}{age_str}",
                 bg=bg, fg=COLORS["text_muted"],
                 font=font("xs"), anchor="w").pack(fill="x")

        # ── Divider ───────────────────────────────────────────────
        tk.Frame(self._inner, bg=COLORS["border_subtle"],
                 height=1).pack(fill="x", pady=(0, 12))

        # ── Stats row ─────────────────────────────────────────────
        stats = tk.Frame(self._inner, bg=bg)
        stats.pack(fill="x")

        fd = summary.get("feeding_done", 0)
        ft = summary.get("feeding_due", 0)
        md = summary.get("meds_done", 0)
        mt = summary.get("meds_due", 0)
        go = summary.get("grooming_overdue", 0)

        def stat_pill(icon, text, color, page):
            f = tk.Frame(stats, bg=COLORS["bg_elevated"],
                         padx=8, pady=4)
            f.pack(side="left", padx=(0, 6))
            tk.Label(f, text=f"{icon} {text}", bg=COLORS["bg_elevated"],
                     fg=color, font=font("xs", "bold")).pack()
            f.bind("<Button-1>", lambda e: on_navigate(page))
            f.bind("<Enter>", lambda e: f.config(bg=COLORS["bg_hover"]))
            f.bind("<Leave>", lambda e: f.config(bg=COLORS["bg_elevated"]))

        stat_pill("🍽", f"{fd}/{ft}",
                  COLORS["accent_green"] if fd >= ft > 0 else COLORS["accent_amber"],
                  "feeding")
        stat_pill("💊", f"{md}/{mt}",
                  COLORS["accent_green"] if md >= mt > 0 else COLORS["accent_amber"],
                  "medications")
        stat_pill("✂", f"{go} overdue" if go else "OK",
                  COLORS["accent_red"] if go else COLORS["accent_green"],
                  "grooming")

        # ── Notes ─────────────────────────────────────────────────
        if pet.notes:
            tk.Label(self._inner, text=pet.notes, bg=bg,
                     fg=COLORS["text_muted"], font=font("xs"),
                     wraplength=240, justify="left",
                     anchor="w").pack(fill="x", pady=(10, 0))


class DashboardPage(tk.Frame):
    def __init__(self, parent, on_navigate, on_add_pet, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._on_navigate = on_navigate
        self._on_add_pet  = on_add_pet
        self._card_refs   = []
        self._built       = False
        self._build_static()

    def _build_static(self):
        # ── Hero ──────────────────────────────────────────────────
        hero = tk.Frame(self, bg=COLORS["bg_base"])
        hero.pack(fill="x", padx=32, pady=(28, 20))

        left = tk.Frame(hero, bg=COLORS["bg_base"])
        left.pack(side="left", fill="x", expand=True)

        hour = datetime.now().hour
        greeting = ("Good morning" if hour < 12
                    else "Good afternoon" if hour < 18
                    else "Good evening")

        tk.Label(left, text=f"{greeting} 👋",
                 bg=COLORS["bg_base"], fg=COLORS["text_primary"],
                 font=font("hero", "bold"), anchor="w").pack(fill="x")

        today = date.today()
        day_str = today.strftime("%A, %B ") + str(today.day)
        tk.Label(left, text=f"{day_str}",
                 bg=COLORS["bg_base"], fg=COLORS["text_secondary"],
                 font=font("sm"), anchor="w").pack(fill="x", pady=(3, 0))

        primary_btn(hero, "＋  Add Pet", self._on_add_pet).pack(
            side="right", anchor="center"
        )

        # ── Pet cards container ───────────────────────────────────
        self._cards_frame = tk.Frame(self, bg=COLORS["bg_base"])
        self._cards_frame.pack(fill="x", padx=32, pady=(0, 24))

        # ── Quick access ──────────────────────────────────────────
        qa = tk.Frame(self, bg=COLORS["bg_base"])
        qa.pack(fill="x", padx=32, pady=(0, 24))

        section_label(qa, "Quick Access").pack(anchor="w", pady=(0, 10))

        # 2x2 grid of quick nav cards
        grid = tk.Frame(qa, bg=COLORS["bg_base"])
        grid.pack(fill="x")

        for i, (page, icon, label, color) in enumerate(QUICK_NAV):
            card = tk.Frame(grid, bg=COLORS["bg_border"])
            row, col = divmod(i, 2)
            card.grid(row=row, column=col, padx=(0, 8) if col == 0 else 0,
                      pady=(0, 8) if row == 0 else 0, sticky="nsew")

            inner = tk.Frame(card, bg=COLORS["bg_surface"],
                             padx=16, pady=12)
            inner.pack(fill="both", expand=True, padx=1, pady=1)

            top_row = tk.Frame(inner, bg=COLORS["bg_surface"])
            top_row.pack(fill="x")

            tk.Label(top_row, text=icon, bg=COLORS["bg_surface"],
                     fg=color, font=(font()[0], 20)).pack(side="left")
            tk.Label(top_row, text="→", bg=COLORS["bg_surface"],
                     fg=COLORS["text_muted"],
                     font=font("base")).pack(side="right")

            tk.Label(inner, text=label, bg=COLORS["bg_surface"],
                     fg=COLORS["text_primary"],
                     font=font("sm", "bold"), anchor="w").pack(
                fill="x", pady=(6, 0)
            )

            # Clickable
            for w in [card, inner, top_row]:
                w.bind("<Button-1>", lambda e, p=page: self._on_navigate(p))
                w.bind("<Enter>", lambda e, c=inner: c.config(bg=COLORS["bg_elevated"]))
                w.bind("<Leave>", lambda e, c=inner: c.config(bg=COLORS["bg_surface"]))

        for c in range(2):
            grid.columnconfigure(c, weight=1)

    def load(self, pets: list, summaries: dict):
        for w in self._cards_frame.winfo_children():
            w.destroy()
        self._card_refs.clear()

        if not pets:
            empty = tk.Frame(self._cards_frame, bg=COLORS["bg_base"])
            empty.pack(expand=True, fill="both", pady=32)
            tk.Label(empty, text="🐾", bg=COLORS["bg_base"],
                     font=(font()[0], 40)).pack()
            tk.Label(empty, text="Welcome to Kendra",
                     bg=COLORS["bg_base"], fg=COLORS["text_primary"],
                     font=font("xl", "bold")).pack(pady=(8, 4))
            tk.Label(empty,
                     text="Add your first pet to get started.",
                     bg=COLORS["bg_base"], fg=COLORS["text_secondary"],
                     font=font("base")).pack()
            primary_btn(empty, "＋  Add your first pet",
                        self._on_add_pet).pack(pady=(16, 0))
            return

        cols = min(2, len(pets))
        for i, pet in enumerate(pets):
            card = PetCard(
                self._cards_frame, pet=pet,
                summary=summaries.get(pet.id, {}),
                on_navigate=self._on_navigate,
            )
            r, c = divmod(i, cols)
            card.grid(row=r, column=c,
                      padx=(0, 10) if c == 0 else 0,
                      pady=(0, 10), sticky="nsew")
            self._card_refs.append(card)

        for c in range(cols):
            self._cards_frame.columnconfigure(c, weight=1)