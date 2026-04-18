"""
views/pet_dialog.py  +  views/pet_selector.py  +  views/notification_center.py
Combined for brevity — split into separate files as needed.
"""
import os, shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

from assets.styles.theme import COLORS, font
from views.pages.base import primary_btn, ghost_btn, danger_btn, form_label, styled_entry, styled_combobox

PHOTOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "assets", "images", "pets")
SPECIES_OPTIONS = ["dog","cat","bird","fish","rabbit","hamster",
                   "guinea pig","reptile","turtle","ferret","other"]
SPECIES_EMOJI = {
    "dog":"🐶","cat":"🐱","bird":"🦜","fish":"🐠","rabbit":"🐰",
    "hamster":"🐹","guinea pig":"🐹","reptile":"🦎","turtle":"🐢","ferret":"🦡",
}


def _circular_preview(path: str, size: int) -> ImageTk.PhotoImage:
    img = Image.open(path).convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size-1, size-1], fill=255)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return ImageTk.PhotoImage(result)


# ── Pet Dialog ────────────────────────────────────────────────────────────────

class PetDialog(tk.Toplevel):
    def __init__(self, parent, pet=None, on_save=None):
        super().__init__(parent)
        self.pet      = pet
        self._on_save = on_save
        self._selected_photo = None
        self._preview_photo  = None
        self.title("Edit Pet" if pet else "Add a Pet")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build()

    def _build(self):
        tk.Label(self, text="Edit Pet" if self.pet else "Add a Pet",
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                 font=font("lg","bold")).pack(anchor="w", padx=20, pady=(20,12))

        # ── Photo upload ─────────────────────────────────────────
        photo_row = tk.Frame(self, bg=COLORS["bg_card"])
        photo_row.pack(fill="x", padx=20, pady=(0,12))

        self._avatar_lbl = tk.Label(
            photo_row, text="📷",
            bg=COLORS["bg_elevated"],
            font=(font()[0], 28),
            width=5, height=2,
        )
        self._avatar_lbl.pack(side="left", padx=(0,16))
        self._refresh_preview()

        btn_col = tk.Frame(photo_row, bg=COLORS["bg_card"])
        btn_col.pack(side="left", fill="y")

        tk.Button(btn_col, text="📁  Choose Photo",
                  bg=COLORS["bg_elevated"], fg=COLORS["accent_gold"],
                  font=font("sm","bold"), relief="flat", bd=0,
                  cursor="hand2", padx=12, pady=6,
                  command=self._pick_photo).pack(anchor="w")
        tk.Label(btn_col, text="JPG, PNG — shows as your pet's avatar",
                 bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                 font=font("xs")).pack(anchor="w", pady=(4,0))

        if self.pet and self.pet.photo_path:
            tk.Button(btn_col, text="Remove photo",
                      bg=COLORS["bg_card"], fg=COLORS["danger"],
                      font=font("xs"), relief="flat", bd=0,
                      cursor="hand2",
                      command=self._remove_photo).pack(anchor="w", pady=(4,0))

        # ── Name + species ───────────────────────────────────────
        row1 = tk.Frame(self, bg=COLORS["bg_card"])
        row1.pack(fill="x", padx=20, pady=(0,8))
        n_col = tk.Frame(row1, bg=COLORS["bg_card"])
        n_col.pack(side="left", fill="x", expand=True, padx=(0,10))
        form_label(n_col, "Name").pack(anchor="w")
        self._name_var = tk.StringVar(value=self.pet.name if self.pet else "")
        styled_entry(n_col, self._name_var, placeholder="e.g. Mochi").pack(fill="x")
        s_col = tk.Frame(row1, bg=COLORS["bg_card"])
        s_col.pack(side="left", fill="x", expand=True)
        form_label(s_col, "Species").pack(anchor="w")
        self._species_var = tk.StringVar(value=self.pet.species if self.pet else "dog")
        styled_combobox(s_col, [s.capitalize() for s in SPECIES_OPTIONS],
                        self._species_var, width=14).pack(fill="x")

        row2 = tk.Frame(self, bg=COLORS["bg_card"])
        row2.pack(fill="x", padx=20, pady=(0,8))
        b_col = tk.Frame(row2, bg=COLORS["bg_card"])
        b_col.pack(side="left", fill="x", expand=True, padx=(0,10))
        form_label(b_col, "Breed").pack(anchor="w")
        self._breed_var = tk.StringVar(value=self.pet.breed or "" if self.pet else "")
        styled_entry(b_col, self._breed_var, placeholder="Golden Retriever").pack(fill="x")
        bd_col = tk.Frame(row2, bg=COLORS["bg_card"])
        bd_col.pack(side="left", fill="x", expand=True)
        form_label(bd_col, "Birthday (YYYY-MM-DD)").pack(anchor="w")
        self._birthday_var = tk.StringVar(value=self.pet.birthday or "" if self.pet else "")
        styled_entry(bd_col, self._birthday_var, placeholder="2020-01-15").pack(fill="x")

        form_label(self, "Notes").pack(anchor="w", padx=20)
        self._notes_var = tk.StringVar(value=self.pet.notes or "" if self.pet else "")
        notes_frame = styled_entry(self, self._notes_var,
                                   placeholder="Any additional info…", width=40)
        notes_frame.pack(fill="x", padx=20, pady=(0,8))

        self._error_lbl = tk.Label(self, text="", bg=COLORS["bg_card"],
                                   fg=COLORS["danger"], font=font("sm"))
        self._error_lbl.pack(anchor="w", padx=20)

        acts = tk.Frame(self, bg=COLORS["bg_card"])
        acts.pack(fill="x", padx=20, pady=(8,20))
        ghost_btn(acts, "Cancel", self.destroy).pack(side="right", padx=(8,0))
        primary_btn(acts, "Save Changes" if self.pet else "Add Pet",
                    self._on_submit).pack(side="right")

    def _refresh_preview(self):
        path = self._selected_photo or (self.pet.photo_path if self.pet else None)
        if path and path != "__REMOVE__" and os.path.exists(path):
            try:
                self._preview_photo = _circular_preview(path, 72)
                self._avatar_lbl.config(image=self._preview_photo, text="")
                return
            except Exception:
                pass
        self._avatar_lbl.config(image="", text="📷")
        self._preview_photo = None

    def _pick_photo(self):
        path = filedialog.askopenfilename(
            title="Choose Pet Photo",
            filetypes=[("Images","*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if path:
            self._selected_photo = path
            self._refresh_preview()

    def _remove_photo(self):
        self._selected_photo = "__REMOVE__"
        self._avatar_lbl.config(image="", text="📷")
        self._preview_photo = None

    def _save_photo(self, pet_id: int) -> str | None:
        if self._selected_photo == "__REMOVE__":
            return None
        if not self._selected_photo:
            return self.pet.photo_path if self.pet else None
        os.makedirs(PHOTOS_DIR, exist_ok=True)
        ext  = os.path.splitext(self._selected_photo)[1].lower() or ".jpg"
        dest = os.path.join(PHOTOS_DIR, f"pet_{pet_id}{ext}")
        shutil.copy2(self._selected_photo, dest)
        return dest

    def _on_submit(self):
        name = self._name_var.get().strip()
        if not name:
            self._error_lbl.config(text="Name is required.")
            return
        if self._on_save:
            self._on_save({
                "pet_id":        self.pet.id if self.pet else None,
                "name":          name,
                "species":       self._species_var.get().lower(),
                "breed":         self._breed_var.get().strip() or None,
                "birthday":      self._birthday_var.get().strip() or None,
                "notes":         self._notes_var.get().strip() or None,
                "_photo_picker": self,
            })
        self.destroy()


# ── Pet Selector ──────────────────────────────────────────────────────────────

class PetSelectorDialog(tk.Toplevel):
    def __init__(self, parent, pets, active_pet_id=None,
                 on_select=None, on_add=None,
                 on_edit=None, on_delete=None):
        super().__init__(parent)
        self.title("Your Pets")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._build(pets, active_pet_id, on_select, on_add, on_edit, on_delete)

    def _build(self, pets, active_id, on_select, on_add, on_edit, on_delete):
        hdr = tk.Frame(self, bg=COLORS["bg_card"])
        hdr.pack(fill="x", padx=20, pady=(20,12))
        tk.Label(hdr, text="Your Pets", bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=font("lg","bold")).pack(side="left")
        primary_btn(hdr, "＋ Add Pet",
                    command=lambda: (on_add() if on_add else None, self.destroy())
                    ).pack(side="right")

        if not pets:
            tk.Label(self, text="No pets yet. Add your first pet!",
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                     font=font("base")).pack(padx=20, pady=30)
            return

        for pet in pets:
            row = tk.Frame(self, bg=COLORS["bg_card"], pady=8, padx=20)
            row.pack(fill="x")
            emoji = SPECIES_EMOJI.get((pet.species or "").lower(), "🐾")
            tk.Label(row, text=emoji, bg=COLORS["bg_elevated"],
                     font=(font()[0], 18), padx=8, pady=4).pack(side="left", padx=(0,12))
            info = tk.Frame(row, bg=COLORS["bg_card"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=pet.name, bg=COLORS["bg_card"],
                     fg=COLORS["text_primary"], font=font("base","bold"), anchor="w").pack(fill="x")
            tk.Label(info, text=pet.species.capitalize(), bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=font("sm"), anchor="w").pack(fill="x")
            acts = tk.Frame(row, bg=COLORS["bg_card"])
            acts.pack(side="right")
            sel_text = "✓ Active" if active_id == pet.id else "Select"
            sel_btn = primary_btn(acts, sel_text,
                command=lambda pid=pet.id: (on_select(pid) if on_select else None, self.destroy()))
            sel_btn.pack(side="left", padx=(0,4))
            ghost_btn(acts, "✏",
                command=lambda pid=pet.id: (on_edit(pid) if on_edit else None, self.destroy())
                ).pack(side="left", padx=(0,4))
            ghost_btn(acts, "✕",
                command=lambda pid=pet.id: (on_delete(pid) if on_delete else None, self.destroy())
                ).pack(side="left")
            tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=20)

        tk.Frame(self, bg=COLORS["bg_card"], height=12).pack()


# ── Notification Center ───────────────────────────────────────────────────────

class NotificationCenter(tk.Toplevel):
    def __init__(self, parent, on_badge_update=None):
        super().__init__(parent)
        self.title("Notifications")
        self.configure(bg=COLORS["bg_card"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._on_badge_update = on_badge_update
        self._build()
        self._load()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["bg_card"])
        hdr.pack(fill="x", padx=16, pady=(16,8))
        tk.Label(hdr, text="Notifications", bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=font("lg","bold")).pack(side="left")
        ghost_btn(hdr, "Mark all read", self._mark_all).pack(side="right", padx=(8,0))
        ghost_btn(hdr, "Clear all", self._clear_all).pack(side="right")

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x", padx=16)

        # Scroll area
        from views.pages.base import ScrollableFrame
        self._sf = ScrollableFrame(self, bg=COLORS["bg_card"])
        self._sf.pack(fill="both", expand=True, padx=0)
        self._sf.config(width=380, height=420)

        self._empty_lbl = tk.Label(
            self, text="✨ You're all caught up!",
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
            font=font("base")
        )

    def _load(self):
        from models.notification import NotificationModel, TYPE_ICONS
        f = self._sf.scrollable_frame
        for w in f.winfo_children(): w.destroy()
        self._empty_lbl.pack_forget()

        notifs = NotificationModel.get_all(limit=50)
        if not notifs:
            self._empty_lbl.pack(pady=40)
            return

        for n in notifs:
            row = tk.Frame(f, bg=COLORS["bg_card"] if n.read else COLORS["bg_elevated"],
                           pady=10, padx=12)
            row.pack(fill="x", pady=(0,4))

            tk.Label(row, text=TYPE_ICONS.get(n.type,"🔔"),
                     bg=row.cget("bg"), font=(font()[0],14),
                     padx=6, pady=4).pack(side="left", padx=(0,8))

            info = tk.Frame(row, bg=row.cget("bg"))
            info.pack(side="left", fill="x", expand=True)
            if n.pet_name:
                tk.Label(info, text=n.pet_name, bg=row.cget("bg"),
                         fg=COLORS["accent_gold"], font=font("xs","bold")).pack(anchor="w")
            tk.Label(info, text=n.message, bg=row.cget("bg"),
                     fg=COLORS["text_primary"] if not n.read else COLORS["text_secondary"],
                     font=font("sm","bold" if not n.read else "normal"),
                     wraplength=260, justify="left", anchor="w").pack(anchor="w")
            tk.Label(info, text=n.timestamp[:16], bg=row.cget("bg"),
                     fg=COLORS["text_muted"], font=font("xs")).pack(anchor="w")

            acts = tk.Frame(row, bg=row.cget("bg"))
            acts.pack(side="right")
            if not n.read:
                tk.Label(acts, text="●", bg=row.cget("bg"),
                         fg=COLORS["accent_gold"], font=font("xs")).pack()
            ghost_btn(acts, "✕",
                command=lambda nid=n.id: self._delete(nid)).pack()

        self._update_badge()

    def _mark_all(self):
        from models.notification import NotificationModel
        NotificationModel.mark_all_read()
        self._load()

    def _clear_all(self):
        from models.notification import NotificationModel
        NotificationModel.clear_all()
        self._load()

    def _delete(self, notif_id):
        from models.notification import NotificationModel
        NotificationModel.delete(notif_id)
        self._load()

    def _update_badge(self):
        from models.notification import NotificationModel
        count = NotificationModel.get_unread_count()
        if self._on_badge_update:
            self._on_badge_update(count)