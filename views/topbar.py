"""
views/topbar.py
Top navigation bar — nav buttons, bell icon with badge, pet avatar.
"""
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

from assets.styles.theme import COLORS, font, font_size

NAV_ITEMS = [
    ("dashboard",   "Dashboard"),
    ("feeding",     "Feeding"),
    ("medications", "Medications"),
    ("health",      "Health"),
    ("grooming",    "Grooming"),
    ("activity",    "Activity"),
    ("calendar",    "Calendar"),
    ("settings",    "Settings"),
]

SPECIES_EMOJI = {
    "dog": "🐶", "cat": "🐱", "bird": "🦜", "fish": "🐠",
    "rabbit": "🐰", "hamster": "🐹", "guinea pig": "🐹",
    "reptile": "🦎", "turtle": "🐢", "ferret": "🦡",
}


def _circular_photo(path: str, size: int) -> ImageTk.PhotoImage:
    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return ImageTk.PhotoImage(result)


class TopBar(tk.Frame):
    def __init__(self, parent, on_navigate, on_pet_click,
                 on_bell_click, **kwargs):
        super().__init__(
            parent,
            bg=COLORS["topbar_bg"],
            height=58,
            **kwargs
        )
        self.pack_propagate(False)

        self._on_navigate   = on_navigate
        self._on_pet_click  = on_pet_click
        self._on_bell_click = on_bell_click
        self._nav_btns: dict[str, tk.Button] = {}
        self._active_page   = "dashboard"
        self._avatar_photo  = None
        self._unread_count  = 0

        self._build()

    def _build(self):
        # ── Brand ────────────────────────────────────────────────
        brand_frame = tk.Frame(self, bg=COLORS["topbar_bg"])
        brand_frame.pack(side="left", padx=(20, 16))

        # Logo (if exists)
        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "assets", "icons", "logo.png"
        )
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path).resize((28, 28), Image.LANCZOS)
                self._logo_photo = ImageTk.PhotoImage(logo_img)
                tk.Label(
                    brand_frame, image=self._logo_photo,
                    bg=COLORS["topbar_bg"]
                ).pack(side="left", padx=(0, 8))
            except Exception:
                pass

        tk.Label(
            brand_frame, text="Kendra",
            bg=COLORS["topbar_bg"], fg=COLORS["accent_gold"],
            font=font("lg", "bold"),
        ).pack(side="left")

        # ── Nav buttons ──────────────────────────────────────────
        nav_frame = tk.Frame(self, bg=COLORS["topbar_bg"])
        nav_frame.pack(side="left", padx=8)

        for page_id, label in NAV_ITEMS:
            btn = tk.Button(
                nav_frame, text=label,
                bg=COLORS["topbar_bg"],
                fg=COLORS["text_muted"],
                font=font("base"),
                relief="flat", bd=0,
                cursor="hand2",
                padx=12, pady=18,
                activebackground=COLORS["bg_elevated"],
                activeforeground=COLORS["accent_gold"],
                command=lambda pid=page_id: self._on_nav(pid),
            )
            btn.pack(side="left")
            self._nav_btns[page_id] = btn

        # ── Right side ───────────────────────────────────────────
        right_frame = tk.Frame(self, bg=COLORS["topbar_bg"])
        right_frame.pack(side="right", padx=20)

        # Pet switcher
        self._pet_frame = tk.Frame(
            right_frame, bg=COLORS["bg_elevated"],
            padx=10, pady=4, cursor="hand2",
        )
        self._pet_frame.pack(side="right", padx=(12, 0))
        self._pet_frame.bind("<Button-1>", lambda e: self._on_pet_click())

        self._avatar_lbl = tk.Label(
            self._pet_frame, text="🐾",
            bg=COLORS["bg_elevated"],
            font=(font()[0], 18),
        )
        self._avatar_lbl.pack(side="left", padx=(0, 8))
        self._avatar_lbl.bind("<Button-1>", lambda e: self._on_pet_click())

        info_col = tk.Frame(self._pet_frame, bg=COLORS["bg_elevated"])
        info_col.pack(side="left")
        info_col.bind("<Button-1>", lambda e: self._on_pet_click())

        self._pet_name_lbl = tk.Label(
            info_col, text="Select pet",
            bg=COLORS["bg_elevated"], fg=COLORS["text_primary"],
            font=font("base", "bold"),
        )
        self._pet_name_lbl.pack(anchor="w")
        self._pet_name_lbl.bind("<Button-1>", lambda e: self._on_pet_click())

        self._pet_species_lbl = tk.Label(
            info_col, text="",
            bg=COLORS["bg_elevated"], fg=COLORS["accent_gold"],
            font=font("xs"),
        )
        self._pet_species_lbl.pack(anchor="w")
        self._pet_species_lbl.bind("<Button-1>", lambda e: self._on_pet_click())

        tk.Label(
            self._pet_frame, text="▾",
            bg=COLORS["bg_elevated"], fg=COLORS["text_muted"],
            font=font("sm"),
        ).pack(side="left", padx=(6, 0))

        # Divider
        tk.Frame(right_frame, bg=COLORS["border"], width=1).pack(
            side="right", fill="y", pady=12, padx=12
        )

        # Bell + badge
        bell_container = tk.Frame(right_frame, bg=COLORS["topbar_bg"])
        bell_container.pack(side="right")

        self._bell_btn = tk.Button(
            bell_container, text="🔔",
            bg=COLORS["bg_elevated"],
            fg=COLORS["text_primary"],
            font=(font()[0], 16),
            relief="flat", bd=0,
            cursor="hand2",
            padx=8, pady=6,
            activebackground=COLORS["bg_hover"],
            command=self._on_bell_click,
        )
        self._bell_btn.pack()

        self._badge_lbl = tk.Label(
            bell_container, text="0",
            bg=COLORS["danger"], fg="white",
            font=(font()[0], 8, "bold"),
            padx=3, pady=1,
        )
        # Position badge over bell
        self._badge_lbl.place(x=26, y=2)
        self._badge_lbl.place_forget()  # hide initially

        self._set_active("dashboard")

    # ── Nav active state ──────────────────────────────────────────

    def _on_nav(self, page_id: str):
        self._set_active(page_id)
        self._on_navigate(page_id)

    def _set_active(self, page_id: str):
        for pid, btn in self._nav_btns.items():
            if pid == page_id:
                btn.config(
                    fg=COLORS["accent_gold"],
                    bg=COLORS["bg_elevated"],
                    font=font("base", "bold"),
                )
            else:
                btn.config(
                    fg=COLORS["text_muted"],
                    bg=COLORS["topbar_bg"],
                    font=font("base"),
                )
        self._active_page = page_id

    def set_active_page(self, page_id: str):
        self._set_active(page_id)

    # ── Pet display ───────────────────────────────────────────────

    def update_pet(self, pet):
        if not pet:
            self._pet_name_lbl.config(text="Select pet")
            self._pet_species_lbl.config(text="")
            self._avatar_lbl.config(text="🐾", image="")
            self._avatar_photo = None
            return

        self._pet_name_lbl.config(text=pet.name)
        self._pet_species_lbl.config(
            text=(pet.breed or pet.species or "").capitalize()
        )

        # Try photo first
        if pet.photo_path and os.path.exists(pet.photo_path):
            try:
                self._avatar_photo = _circular_photo(pet.photo_path, 32)
                self._avatar_lbl.config(
                    image=self._avatar_photo, text=""
                )
                return
            except Exception:
                pass

        # Fallback emoji
        self._avatar_photo = None
        self._avatar_lbl.config(
            image="",
            text=SPECIES_EMOJI.get((pet.species or "").lower(), "🐾"),
        )

    # ── Notification badge ────────────────────────────────────────

    def update_unread_count(self, count: int):
        self._unread_count = count
        if count > 0:
            self._badge_lbl.config(text=str(min(count, 99)))
            self._badge_lbl.place(x=26, y=2)
        else:
            self._badge_lbl.place_forget()