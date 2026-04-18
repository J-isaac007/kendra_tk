"""
views/pages/dashboard.py
Dashboard page — pet summary cards and quick access buttons.
"""
import os
import tkinter as tk
from datetime import datetime, date
from PIL import Image, ImageTk, ImageDraw

from assets.styles.theme import COLORS, font, font_size, PAD
from views.pages.base import (
    ScrollableFrame, primary_btn, ghost_btn,
    section_label, body_label, muted_label, badge, divider
)

SPECIES_EMOJI = {
    "dog": "🐶", "cat": "🐱", "bird": "🦜", "fish": "🐠",
    "rabbit": "🐰", "hamster": "🐹", "guinea pig": "🐹",
    "reptile": "🦎", "turtle": "🐢", "ferret": "🦡",
}

QUICK_NAV = [
    ("feeding",     "🍽  Feeding →",     COLORS["accent_gold"]),
    ("medications", "💊  Medications →", COLORS["accent_sage"]),
    ("grooming",    "✂  Grooming →",    COLORS["accent_lavender"]),
    ("activity",    "🏃  Activity →",    COLORS["accent_rust"]),
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
    """Individual pet summary card on the dashboard."""

    def __init__(self, parent, pet, summary: dict, on_navigate, **kwargs):
        super().__init__(
            parent,
            bg=COLORS["bg_card"],
            padx=16, pady=12,
            relief="flat",
            **kwargs
        )
        self._photo_ref = None
        self._build(pet, summary, on_navigate)

    def _build(self, pet, summary, on_navigate):
        # ── Header ───────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["bg_card"])
        header.pack(fill="x", pady=(0, 8))

        # Avatar
        avatar_frame = tk.Frame(
            header, bg=COLORS["bg_elevated"],
            width=44, height=44,
        )
        avatar_frame.pack(side="left", padx=(0, 12))
        avatar_frame.pack_propagate(False)

        photo_loaded = False
        if pet.photo_path and os.path.exists(pet.photo_path):
            try:
                self._photo_ref = _circular_photo(pet.photo_path, 44)
                tk.Label(
                    avatar_frame, image=self._photo_ref,
                    bg=COLORS["bg_elevated"]
                ).place(relx=0.5, rely=0.5, anchor="center")
                photo_loaded = True
            except Exception:
                pass

        if not photo_loaded:
            emoji = SPECIES_EMOJI.get((pet.species or "").lower(), "🐾")
            tk.Label(
                avatar_frame, text=emoji,
                bg=COLORS["bg_elevated"],
                font=(font()[0], 20),
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Name + meta
        info = tk.Frame(header, bg=COLORS["bg_card"])
        info.pack(side="left", fill="x", expand=True)

        tk.Label(
            info, text=pet.name,
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            font=font("md", "bold"), anchor="w",
        ).pack(fill="x")

        age_str = ""
        if pet.birthday:
            try:
                age = int(
                    (datetime.today() -
                     datetime.strptime(pet.birthday, "%Y-%m-%d")).days / 365.25
                )
                age_str = f" · {age}yr"
            except Exception:
                pass

        tk.Label(
            info,
            text=f"{(pet.breed or pet.species).capitalize()}{age_str}",
            bg=COLORS["bg_card"], fg=COLORS["accent_gold"],
            font=font("xs"), anchor="w",
        ).pack(fill="x")

        # ── Thin separator ────────────────────────────────────────
        tk.Frame(self, bg=COLORS["border"], height=1).pack(
            fill="x", pady=(0, 8)
        )

        # ── Stat pills ────────────────────────────────────────────
        pills = tk.Frame(self, bg=COLORS["bg_card"])
        pills.pack(fill="x", pady=(0, 4))

        fd = summary.get("feeding_done", 0)
        ft = summary.get("feeding_due", 0)
        md = summary.get("meds_done", 0)
        mt = summary.get("meds_due", 0)
        go = summary.get("grooming_overdue", 0)

        def pill(text, color, page):
            btn = tk.Button(
                pills, text=text,
                bg=COLORS["bg_elevated"],
                fg=color,
                font=(font()[0], font_size("xs"), "bold"),
                relief="flat", bd=0,
                cursor="hand2",
                padx=7, pady=3,
                command=lambda: on_navigate(page),
            )
            btn.pack(side="left", padx=(0, 5))

        f_done = fd >= ft > 0
        m_done = md >= mt > 0

        pill(f"🍽 {fd}/{ft}",
             COLORS["accent_sage"] if f_done else COLORS["accent_gold"],
             "feeding")
        pill(f"💊 {md}/{mt}",
             COLORS["accent_sage"] if m_done else COLORS["accent_gold"],
             "medications")
        pill(f"✂ {go} due" if go else "✂ OK",
             COLORS["danger"] if go else COLORS["accent_sage"],
             "grooming")

        # ── Notes (compact) ───────────────────────────────────────
        if pet.notes:
            tk.Label(
                self, text=pet.notes,
                bg=COLORS["bg_card"],
                fg=COLORS["text_muted"],
                font=font("xs"),
                wraplength=240,
                justify="left",
                anchor="w",
            ).pack(fill="x", pady=(4, 0))


class DashboardPage(tk.Frame):
    def __init__(self, parent, on_navigate, on_add_pet, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._on_navigate = on_navigate
        self._on_add_pet  = on_add_pet
        self._card_refs   = []

        # The entire dashboard is scrollable so nothing gets cut off
        self._sf = ScrollableFrame(self, bg=COLORS["bg_base"])
        self._sf.pack(fill="both", expand=True)
        self._inner = self._sf.scrollable_frame

        self._build_static()

    def _build_static(self):
        inner = self._inner

        # ── Hero header ───────────────────────────────────────────
        hero = tk.Frame(inner, bg=COLORS["bg_base"])
        hero.pack(fill="x", padx=32, pady=(28, 0))

        left = tk.Frame(hero, bg=COLORS["bg_base"])
        left.pack(side="left", fill="x", expand=True)

        hour = datetime.now().hour
        greeting = (
            "Good morning" if hour < 12
            else "Good afternoon" if hour < 18
            else "Good evening"
        )
        self._greeting_lbl = tk.Label(
            left, text=f"{greeting} 🌿",
            bg=COLORS["bg_base"], fg=COLORS["text_primary"],
            font=font("hero", "bold"), anchor="w",
        )
        self._greeting_lbl.pack(fill="x")

        today   = date.today()
        day_str = today.strftime("%A, %B ") + str(today.day)
        tk.Label(
            left,
            text=f"{day_str}  ·  Here's how your pets are doing",
            bg=COLORS["bg_base"], fg=COLORS["text_muted"],
            font=font("sm"), anchor="w",
        ).pack(fill="x", pady=(2, 0))

        primary_btn(inner if False else hero,
                    "＋  Add Pet", self._on_add_pet).pack(
            side="right", anchor="n"
        )

        # ── Cards area ────────────────────────────────────────────
        self._cards_frame = tk.Frame(inner, bg=COLORS["bg_base"])
        self._cards_frame.pack(fill="x", padx=32, pady=16)

        # ── Quick access ──────────────────────────────────────────
        qa_frame = tk.Frame(inner, bg=COLORS["bg_base"])
        qa_frame.pack(fill="x", padx=32, pady=(0, 24))

        section_label(qa_frame, "Quick Access").pack(
            anchor="w", pady=(0, 8)
        )

        btn_row = tk.Frame(qa_frame, bg=COLORS["bg_base"])
        btn_row.pack(fill="x")

        for page, label, color in QUICK_NAV:
            btn = tk.Button(
                btn_row, text=label,
                bg=COLORS["bg_card"], fg=color,
                font=font("base", "bold"),
                relief="flat", bd=0, cursor="hand2",
                padx=14, pady=10,
                activebackground=COLORS["bg_elevated"],
                activeforeground=color,
                command=lambda p=page: self._on_navigate(p),
            )
            btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

    def load(self, pets: list, summaries: dict):
        """Reload pet cards."""
        for w in self._cards_frame.winfo_children():
            w.destroy()
        self._card_refs.clear()

        if not pets:
            empty = tk.Frame(self._cards_frame, bg=COLORS["bg_base"])
            empty.pack(expand=True, fill="both", pady=40)
            tk.Label(
                empty, text="🐾",
                bg=COLORS["bg_base"],
                font=(font()[0], 44),
            ).pack()
            tk.Label(
                empty, text="Welcome to Kendra",
                bg=COLORS["bg_base"], fg=COLORS["text_primary"],
                font=font("xl", "bold"),
            ).pack(pady=(6, 4))
            tk.Label(
                empty,
                text="Add your first pet to get started.",
                bg=COLORS["bg_base"], fg=COLORS["text_muted"],
                font=font("base"),
            ).pack()
            primary_btn(
                empty, "＋  Add your first pet", self._on_add_pet
            ).pack(pady=(12, 0))
            return

        # Responsive grid — max 3 columns
        cols = min(3, max(1, len(pets)))
        for i, pet in enumerate(pets):
            card = PetCard(
                self._cards_frame,
                pet=pet,
                summary=summaries.get(pet.id, {}),
                on_navigate=self._on_navigate,
            )
            row, col = divmod(i, cols)
            card.grid(
                row=row, column=col,
                padx=(0, 10) if col < cols - 1 else 0,
                pady=(0, 10),
                sticky="nsew",
            )
            self._card_refs.append(card)

        for c in range(cols):
            self._cards_frame.columnconfigure(c, weight=1)