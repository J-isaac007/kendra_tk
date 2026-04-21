"""
views/pet_dialog.py — Kendra Pro
PetDialog, PetSelectorDialog, NotificationCenter

All styled_entry fields use frame.get() — never StringVar.get() —
so placeholder text never leaks into submitted data.
"""
import os, shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

from assets.styles.theme import COLORS, font
from views.pages.base import (
    primary_btn, ghost_btn,
    form_label, styled_entry, styled_combobox, ScrollableFrame
)

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "assets", "images", "pets")
SPECIES_OPTIONS = ["dog", "cat", "bird", "fish", "rabbit", "hamster",
                   "guinea pig", "reptile", "turtle", "ferret", "other"]
SPECIES_EMOJI = {
    "dog": "🐶", "cat": "🐱", "bird": "🦜", "fish": "🐠",
    "rabbit": "🐰", "hamster": "🐹", "guinea pig": "🐹",
    "reptile": "🦎", "turtle": "🐢", "ferret": "🦡",
}


def _circular(path: str, size: int) -> ImageTk.PhotoImage:
    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return ImageTk.PhotoImage(result)


# ── Pet Dialog ────────────────────────────────────────────────────────────────

class PetDialog(tk.Toplevel):
    def __init__(self, parent, pet=None, on_save=None):
        super().__init__(parent)
        self.pet = pet
        self._on_save = on_save
        self._selected_photo = None
        self._preview_photo  = None
        self.title("Edit Pet" if pet else "Add a Pet")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()
        self.update_idletasks()
        self.geometry("")

    def _build(self):
        bg = COLORS["bg_surface"]

        tk.Label(self, text="Edit Pet" if self.pet else "Add a Pet",
                 bg=bg, fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(anchor="w", padx=24, pady=(20, 4))
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 16))

        # ── Photo ─────────────────────────────────────────────────
        photo_row = tk.Frame(self, bg=bg)
        photo_row.pack(fill="x", padx=24, pady=(0, 16))

        self._avatar_lbl = tk.Label(
            photo_row, text="📷",
            bg=COLORS["bg_elevated"],
            font=(font()[0], 24), width=5, height=2,
        )
        self._avatar_lbl.pack(side="left", padx=(0, 16))
        self._refresh_preview()

        btn_col = tk.Frame(photo_row, bg=bg)
        btn_col.pack(side="left", fill="y")
        tk.Button(btn_col, text="📁  Choose Photo",
                  bg=COLORS["bg_elevated"], fg=COLORS["accent"],
                  font=font("sm", "bold"), relief="flat", bd=0,
                  cursor="hand2", padx=12, pady=6,
                  command=self._pick_photo).pack(anchor="w")
        tk.Label(btn_col, text="JPG or PNG — shown as pet avatar",
                 bg=bg, fg=COLORS["text_muted"],
                 font=font("xs")).pack(anchor="w", pady=(4, 0))
        if self.pet and self.pet.photo_path:
            tk.Button(btn_col, text="Remove photo",
                      bg=bg, fg=COLORS["accent_red"],
                      font=font("xs"), relief="flat", bd=0,
                      cursor="hand2",
                      command=self._remove_photo).pack(anchor="w", pady=(4, 0))

        # ── Name + Species ────────────────────────────────────────
        row1 = tk.Frame(self, bg=bg)
        row1.pack(fill="x", padx=24, pady=(0, 12))

        n_col = tk.Frame(row1, bg=bg)
        n_col.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(n_col, "Name", bg=bg).pack(anchor="w")
        self._name_f = styled_entry(
            n_col, placeholder="Mochi",
            width=22, bg=bg)
        self._name_f.pack(fill="x", pady=(4, 0))
        # Pre-fill for edit mode
        if self.pet and self.pet.name:
            self._name_f.set(self.pet.name)

        s_col = tk.Frame(row1, bg=bg)
        s_col.pack(side="left", fill="x", expand=True)
        form_label(s_col, "Species", bg=bg).pack(anchor="w")
        self._species_var = tk.StringVar(
            value=(self.pet.species.capitalize() if self.pet else "Dog")
        )
        styled_combobox(s_col, [x.capitalize() for x in SPECIES_OPTIONS],
                        self._species_var, width=16).pack(fill="x", pady=(4, 0))

        # ── Breed + Birthday ──────────────────────────────────────
        row2 = tk.Frame(self, bg=bg)
        row2.pack(fill="x", padx=24, pady=(0, 12))

        b_col = tk.Frame(row2, bg=bg)
        b_col.pack(side="left", fill="x", expand=True, padx=(0, 12))
        form_label(b_col, "Breed", bg=bg).pack(anchor="w")
        self._breed_f = styled_entry(
            b_col, placeholder="Golden Retriever",
            width=22, bg=bg)
        self._breed_f.pack(fill="x", pady=(4, 0))
        if self.pet and self.pet.breed:
            self._breed_f.set(self.pet.breed)

        bd_col = tk.Frame(row2, bg=bg)
        bd_col.pack(side="left", fill="x", expand=True)
        form_label(bd_col, "Birthday (YYYY-MM-DD)", bg=bg).pack(anchor="w")
        self._birthday_f = styled_entry(
            bd_col, placeholder="2020-01-15",
            width=16, bg=bg)
        self._birthday_f.pack(fill="x", pady=(4, 0))
        if self.pet and self.pet.birthday:
            self._birthday_f.set(self.pet.birthday)

        # ── Notes ─────────────────────────────────────────────────
        form_label(self, "Notes", bg=bg).pack(anchor="w", padx=24)
        self._notes_f = styled_entry(
            self, placeholder="Allergies, favourite treats…",
            width=46, bg=bg)
        self._notes_f.pack(fill="x", padx=24, pady=(4, 8))
        if self.pet and self.pet.notes:
            self._notes_f.set(self.pet.notes)

        self._err = tk.Label(self, text="", bg=bg,
                             fg=COLORS["accent_red"], font=font("sm"))
        self._err.pack(anchor="w", padx=24)

        # ── Actions ───────────────────────────────────────────────
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(8, 12))
        acts = tk.Frame(self, bg=bg)
        acts.pack(fill="x", padx=24, pady=(0, 20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8, 0))
        primary_btn(acts, "Save Changes" if self.pet else "Add Pet",
                    self._submit).pack(side="right")

    def _refresh_preview(self):
        path = self._selected_photo or (self.pet.photo_path if self.pet else None)
        if path and path != "__REMOVE__" and os.path.exists(path):
            try:
                self._preview_photo = _circular(path, 72)
                self._avatar_lbl.config(image=self._preview_photo, text="")
                return
            except Exception:
                pass
        self._avatar_lbl.config(image="", text="📷")

    def _pick_photo(self):
        path = filedialog.askopenfilename(
            title="Choose Pet Photo",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if path:
            self._selected_photo = path
            self._refresh_preview()

    def _remove_photo(self):
        self._selected_photo = "__REMOVE__"
        self._avatar_lbl.config(image="", text="📷")

    def _save_photo(self, pet_id: int) -> str | None:
        if self._selected_photo == "__REMOVE__": return None
        if not self._selected_photo:
            return self.pet.photo_path if self.pet else None
        os.makedirs(PHOTOS_DIR, exist_ok=True)
        ext  = os.path.splitext(self._selected_photo)[1].lower() or ".jpg"
        dest = os.path.join(PHOTOS_DIR, f"pet_{pet_id}{ext}")
        shutil.copy2(self._selected_photo, dest)
        return dest

    def _submit(self):
        # Use frame.get() — guaranteed to return "" instead of placeholder
        name = self._name_f.get().strip()
        if not name:
            self._err.config(text="Name is required.")
            return
        if self._on_save:
            self._on_save({
                "pet_id":        self.pet.id if self.pet else None,
                "name":          name,
                "species":       self._species_var.get().lower(),
                "breed":         self._breed_f.get().strip() or None,
                "birthday":      self._birthday_f.get().strip() or None,
                "notes":         self._notes_f.get().strip() or None,
                "_photo_picker": self,
            })
        self.destroy()


# ── Pet Selector ──────────────────────────────────────────────────────────────

class PetSelectorDialog(tk.Toplevel):
    def __init__(self, parent, pets, active_pet_id=None,
                 on_select=None, on_add=None, on_edit=None, on_delete=None):
        super().__init__(parent)
        self.title("Your Pets")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build(pets, active_pet_id, on_select, on_add, on_edit, on_delete)
        self.update_idletasks()
        self.geometry("")

    def _build(self, pets, active_id, on_select, on_add, on_edit, on_delete):
        bg = COLORS["bg_surface"]
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        tk.Label(hdr, text="Your Pets", bg=bg,
                 fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(side="left")
        primary_btn(hdr, "＋ Add Pet",
                    command=lambda: (on_add() if on_add else None, self.destroy())
                    ).pack(side="right")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(4, 8))

        if not pets:
            tk.Label(self, text="No pets yet. Add your first pet!",
                     bg=bg, fg=COLORS["text_secondary"],
                     font=font("sm")).pack(padx=24, pady=30)
            return

        for pet in pets:
            row = tk.Frame(self, bg=bg, pady=8, padx=24)
            row.pack(fill="x")
            emoji = SPECIES_EMOJI.get((pet.species or "").lower(), "🐾")
            tk.Label(row, text=emoji, bg=COLORS["bg_elevated"],
                     font=(font()[0], 16), padx=8, pady=4).pack(side="left", padx=(0, 12))
            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=pet.name, bg=bg,
                     fg=COLORS["text_primary"],
                     font=font("sm", "bold"), anchor="w").pack(fill="x")
            tk.Label(info, text=pet.species.capitalize(), bg=bg,
                     fg=COLORS["text_muted"], font=font("xs"),
                     anchor="w").pack(fill="x")
            acts = tk.Frame(row, bg=bg)
            acts.pack(side="right")
            sel_text = "✓ Active" if active_id == pet.id else "Select"
            primary_btn(acts, sel_text,
                        command=lambda pid=pet.id: (
                            on_select(pid) if on_select else None, self.destroy()
                        )).pack(side="left", padx=(0, 4))
            ghost_btn(acts, "✏",
                      command=lambda pid=pet.id: (
                          on_edit(pid) if on_edit else None, self.destroy()
                      )).pack(side="left", padx=(0, 4))
            ghost_btn(acts, "✕",
                      command=lambda pid=pet.id: (
                          on_delete(pid) if on_delete else None, self.destroy()
                      ), fg=COLORS["accent_red"]).pack(side="left")
            tk.Frame(self, bg=COLORS["border_subtle"], height=1).pack(fill="x", padx=24)

        tk.Frame(self, bg=bg, height=12).pack()


# ── Notification Center ───────────────────────────────────────────────────────

class NotificationCenter(tk.Toplevel):
    def __init__(self, parent, on_badge_update=None):
        super().__init__(parent)
        self.title("Notifications")
        self.configure(bg=COLORS["bg_surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._on_badge_update = on_badge_update
        self._build()
        self._load()

    def _build(self):
        bg = COLORS["bg_surface"]
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(hdr, text="Notifications", bg=bg,
                 fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(side="left")
        ghost_btn(hdr, "Mark all read", self._mark_all).pack(side="right", padx=(8, 0))
        ghost_btn(hdr, "Clear all", self._clear_all).pack(side="right")
        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=16)
        self._sf = ScrollableFrame(self, bg=bg)
        self._sf.pack(fill="both", expand=True)
        self._sf.config(width=420, height=460)
        self._empty = tk.Label(self, text="✨ All caught up!",
                               bg=bg, fg=COLORS["text_muted"], font=font("base"))

    def _load(self):
        from models.notification import NotificationModel, TYPE_ICONS
        f = self._sf.scrollable_frame
        for w in f.winfo_children(): w.destroy()
        self._empty.pack_forget()
        notifs = NotificationModel.get_all(limit=50)
        if not notifs:
            self._empty.pack(pady=40)
            return
        for n in notifs:
            bg = COLORS["bg_elevated"] if not n.read else COLORS["bg_surface"]
            row = tk.Frame(f, bg=bg)
            row.pack(fill="x", pady=(0, 1))
            accent = COLORS["accent"] if not n.read else COLORS["text_muted"]
            tk.Frame(row, bg=accent, width=3).pack(side="left", fill="y")
            inner = tk.Frame(row, bg=bg, padx=12, pady=10)
            inner.pack(side="left", fill="x", expand=True)
            tk.Label(inner, text=TYPE_ICONS.get(n.type, "🔔"),
                     bg=bg, font=(font()[0], 13)).pack(side="left", padx=(0, 10))
            info = tk.Frame(inner, bg=bg)
            info.pack(side="left", fill="x", expand=True)
            if n.pet_name:
                tk.Label(info, text=n.pet_name, bg=bg,
                         fg=COLORS["accent"],
                         font=font("xs", "bold")).pack(anchor="w")
            tk.Label(info, text=n.message, bg=bg,
                     fg=COLORS["text_primary"] if not n.read else COLORS["text_secondary"],
                     font=font("sm", "bold" if not n.read else "normal"),
                     wraplength=280, justify="left", anchor="w").pack(anchor="w")
            tk.Label(info, text=n.timestamp[:16], bg=bg,
                     fg=COLORS["text_muted"], font=font("xs")).pack(anchor="w")
            ghost_btn(inner, "✕",
                      command=lambda nid=n.id: self._delete(nid),
                      fg=COLORS["accent_red"]).pack(side="right")
        self._update_badge()

    def _mark_all(self):
        from models.notification import NotificationModel
        NotificationModel.mark_all_read(); self._load()

    def _clear_all(self):
        from models.notification import NotificationModel
        NotificationModel.clear_all(); self._load()

    def _delete(self, nid):
        from models.notification import NotificationModel
        NotificationModel.delete(nid); self._load()

    def _update_badge(self):
        from models.notification import NotificationModel
        if self._on_badge_update:
            self._on_badge_update(NotificationModel.get_unread_count())