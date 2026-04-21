"""
views/topbar.py
Kendra Pro top navigation bar.
Slim 52px, clean underline nav, no heavy styling.
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
            height=52,
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
        brand = tk.Frame(self, bg=COLORS["topbar_bg"])
        brand.pack(side="left", padx=(20, 0))

        # Logo if exists
        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "assets", "icons", "logo.png"
        )
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path).resize((24, 24), Image.LANCZOS)
                self._logo_photo = ImageTk.PhotoImage(logo_img)
                tk.Label(brand, image=self._logo_photo,
                         bg=COLORS["topbar_bg"]).pack(side="left", padx=(0, 8))
            except Exception:
                pass

        tk.Label(
            brand, text="Kendra",
            bg=COLORS["topbar_bg"], fg=COLORS["text_primary"],
            font=font("base", "bold"),
        ).pack(side="left")

        # Subtle divider after brand
        tk.Frame(self, bg=COLORS["topbar_border"], width=1).pack(
            side="left", fill="y", pady=12, padx=16
        )

        # ── Nav buttons ──────────────────────────────────────────
        nav = tk.Frame(self, bg=COLORS["topbar_bg"])
        nav.pack(side="left")

        for page_id, label in NAV_ITEMS:
            btn = tk.Button(
                nav, text=label,
                bg=COLORS["topbar_bg"],
                fg=COLORS["text_muted"],
                font=font("sm"),
                relief="flat", bd=0, cursor="hand2",
                padx=12, pady=16,
                activebackground=COLORS["topbar_bg"],
                activeforeground=COLORS["text_primary"],
                command=lambda pid=page_id: self._on_nav(pid),
            )
            btn.pack(side="left")
            self._nav_btns[page_id] = btn

        # ── Right controls ───────────────────────────────────────
        right = tk.Frame(self, bg=COLORS["topbar_bg"])
        right.pack(side="right", padx=20)

        # Pet switcher
        self._pet_btn = tk.Frame(
            right, bg=COLORS["bg_elevated"],
            cursor="hand2", padx=10, pady=6,
        )
        self._pet_btn.pack(side="right", padx=(10, 0))
        self._pet_btn.bind("<Button-1>", lambda e: self._on_pet_click())
        self._pet_btn.bind("<Enter>", lambda e: self._pet_btn.config(bg=COLORS["bg_hover"]))
        self._pet_btn.bind("<Leave>", lambda e: self._pet_btn.config(bg=COLORS["bg_elevated"]))

        self._avatar_lbl = tk.Label(
            self._pet_btn, text="🐾",
            bg=COLORS["bg_elevated"],
            font=(font()[0], 15),
        )
        self._avatar_lbl.pack(side="left", padx=(0, 8))
        self._avatar_lbl.bind("<Button-1>", lambda e: self._on_pet_click())

        pet_text_col = tk.Frame(self._pet_btn, bg=COLORS["bg_elevated"])
        pet_text_col.pack(side="left")
        pet_text_col.bind("<Button-1>", lambda e: self._on_pet_click())

        self._pet_name_lbl = tk.Label(
            pet_text_col, text="Select pet",
            bg=COLORS["bg_elevated"], fg=COLORS["text_primary"],
            font=font("sm", "bold"),
        )
        self._pet_name_lbl.pack(anchor="w")
        self._pet_name_lbl.bind("<Button-1>", lambda e: self._on_pet_click())

        self._pet_sub_lbl = tk.Label(
            pet_text_col, text="",
            bg=COLORS["bg_elevated"], fg=COLORS["text_muted"],
            font=font("xs"),
        )
        self._pet_sub_lbl.pack(anchor="w")
        self._pet_sub_lbl.bind("<Button-1>", lambda e: self._on_pet_click())

        tk.Label(self._pet_btn, text="⌄",
                 bg=COLORS["bg_elevated"], fg=COLORS["text_muted"],
                 font=font("sm")).pack(side="left", padx=(6, 0))

        # Divider
        tk.Frame(right, bg=COLORS["topbar_border"], width=1).pack(
            side="right", fill="y", pady=12, padx=10
        )

        # Bell button
        bell_wrap = tk.Frame(right, bg=COLORS["topbar_bg"])
        bell_wrap.pack(side="right")

        self._bell_btn = tk.Button(
            bell_wrap, text="🔔",
            bg=COLORS["topbar_bg"],
            fg=COLORS["text_secondary"],
            font=(font()[0], 14),
            relief="flat", bd=0, cursor="hand2",
            padx=8, pady=8,
            activebackground=COLORS["bg_elevated"],
            command=self._on_bell_click,
        )
        self._bell_btn.pack()
        self._bell_btn.bind("<Enter>", lambda e: self._bell_btn.config(bg=COLORS["bg_elevated"]))
        self._bell_btn.bind("<Leave>", lambda e: self._bell_btn.config(bg=COLORS["topbar_bg"]))

        self._badge_lbl = tk.Label(
            bell_wrap, text="",
            bg=COLORS["accent_red"], fg="white",
            font=(font()[0], 7, "bold"),
            padx=3,
        )
        self._badge_lbl.place(x=22, y=4)
        self._badge_lbl.place_forget()

        self._set_active("dashboard")

    def _on_nav(self, page_id: str):
        self._set_active(page_id)
        self._on_navigate(page_id)

    def _set_active(self, page_id: str):
        for pid, btn in self._nav_btns.items():
            if pid == page_id:
                btn.config(
                    fg=COLORS["accent"],
                    font=font("sm", "bold"),
                )
            else:
                btn.config(
                    fg=COLORS["text_muted"],
                    font=font("sm"),
                )
        self._active_page = page_id

    def set_active_page(self, page_id: str):
        self._set_active(page_id)

    def update_pet(self, pet):
        if not pet:
            self._pet_name_lbl.config(text="Select pet")
            self._pet_sub_lbl.config(text="")
            self._avatar_lbl.config(text="🐾", image="")
            self._avatar_photo = None
            return

        self._pet_name_lbl.config(text=pet.name)
        self._pet_sub_lbl.config(
            text=(pet.breed or pet.species or "").capitalize()
        )

        if pet.photo_path and os.path.exists(pet.photo_path):
            try:
                self._avatar_photo = _circular_photo(pet.photo_path, 28)
                self._avatar_lbl.config(image=self._avatar_photo, text="")
                return
            except Exception:
                pass

        self._avatar_photo = None
        self._avatar_lbl.config(
            image="",
            text=SPECIES_EMOJI.get((pet.species or "").lower(), "🐾"),
        )

    def update_unread_count(self, count: int):
        if count > 0:
            self._badge_lbl.config(text=str(min(count, 99)))
            self._badge_lbl.place(x=22, y=4)
        else:
            self._badge_lbl.place_forget()