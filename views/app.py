"""
views/app.py
Root Tk window, background rendering, and page manager.
"""
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

from assets.styles.theme import COLORS, load_fonts, font

BG_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "assets", "images", "background.jpg"
))


class KendraApp(tk.Tk):
    """
    Root application window.
    Manages the background canvas, topbar, notification bar, and page stack.
    """

    def __init__(self):
        super().__init__()
        self.title("Kendra")
        self.geometry("1280x800")
        self.minsize(1024, 680)
        self.configure(bg=COLORS["bg_base"])

        # Load fonts before building UI
        load_fonts(self)

        # ── Background canvas ────────────────────────────────────
        self._bg_canvas = tk.Canvas(
            self, highlightthickness=0, bd=0,
            bg=COLORS["bg_base"]
        )
        self._bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._bg_photo = None
        self._load_background()
        self.bind("<Configure>", self._on_resize)

        # ── Main layout ──────────────────────────────────────────
        # Topbar placeholder (set by controller)
        self.topbar_frame = tk.Frame(
            self, bg=COLORS["topbar_bg"], height=58
        )
        self.topbar_frame.place(x=0, y=0, relwidth=1)
        self.topbar_frame.pack_propagate(False)

        # Notification bar placeholder
        self.notif_frame = tk.Frame(
            self, bg=COLORS["bg_base"], height=0
        )
        self.notif_frame.place(x=0, y=58, relwidth=1)

        # Page area
        self.page_area = tk.Frame(
            self, bg=COLORS["bg_base"]
        )
        self.page_area.place(x=0, y=58, relwidth=1, relheight=1)

        # Page registry
        self._pages: dict[str, tk.Frame] = {}
        self._current_page: str = ""

    # ── Background ───────────────────────────────────────────────

    def _load_background(self):
        if os.path.exists(BG_PATH):
            try:
                self._bg_original = Image.open(BG_PATH)
                self._render_background()
                print("[Kendra] Background loaded.")
                return
            except Exception as e:
                print(f"[Kendra] Background load failed: {e}")
        print(f"[Kendra] No background at {BG_PATH} — using gradient.")
        self._bg_original = None
        self._render_gradient()

    def _render_background(self):
        w = self.winfo_width()  or 1280
        h = self.winfo_height() or 800
        if not self._bg_original:
            return

        # Scale to cover
        img = self._bg_original.copy()
        img_ratio = img.width / img.height
        win_ratio = w / h
        if img_ratio > win_ratio:
            new_h = h
            new_w = int(h * img_ratio)
        else:
            new_w = w
            new_h = int(w / img_ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)

        # Center crop
        x = (new_w - w) // 2
        y = (new_h - h) // 2
        img = img.crop((x, y, x + w, y + h))

        # Dark overlay
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        # Gradient from top-dark to mid-lighter
        for row in range(h):
            alpha = int(180 - (row / h) * 60)
            draw.line([(0, row), (w, row)], fill=(0, 0, 0, alpha))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")

        self._bg_photo = ImageTk.PhotoImage(img)
        self._bg_canvas.delete("all")
        self._bg_canvas.create_image(0, 0, anchor="nw", image=self._bg_photo)

    def _render_gradient(self):
        w = self.winfo_width()  or 1280
        h = self.winfo_height() or 800
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        for row in range(h):
            t = row / h
            r = int(0x16 * (1-t) + 0x0d * t)
            g = int(0x15 * (1-t) + 0x0c * t)
            b = int(0x0f * (1-t) + 0x08 * t)
            draw.line([(0, row), (w, row)], fill=(r, g, b))
        self._bg_photo = ImageTk.PhotoImage(img)
        self._bg_canvas.delete("all")
        self._bg_canvas.create_image(0, 0, anchor="nw", image=self._bg_photo)

    def _on_resize(self, event):
        if hasattr(self, "_bg_original"):
            if self._bg_original:
                self._render_background()
            else:
                self._render_gradient()

    # ── Page management ──────────────────────────────────────────

    def register_page(self, page_id: str, page_frame: tk.Frame):
        self._pages[page_id] = page_frame
        page_frame.place(in_=self.page_area,
                         x=0, y=0, relwidth=1, relheight=1)

    def show_page(self, page_id: str):
        page = self._pages.get(page_id)
        if page:
            page.tkraise()
            self._current_page = page_id

    def show_toast(self, text: str, icon: str = "🔔", duration_ms: int = 5000):
        """Show a brief notification bar at the top."""
        # Clear existing toast
        for w in self.notif_frame.winfo_children():
            w.destroy()

        self.notif_frame.config(height=46)
        self.page_area.place(y=104)  # push page down

        bar = tk.Frame(self.notif_frame, bg="#2a2810",
                       pady=0)
        bar.pack(fill="x", padx=12, pady=4)

        inner = tk.Frame(bar, bg="#2a2810")
        inner.pack(fill="x", padx=12, pady=8)

        tk.Label(inner, text=icon, bg="#2a2810",
                 fg=COLORS["accent_gold"],
                 font=font("base")).pack(side="left", padx=(0, 8))

        tk.Label(inner, text=text, bg="#2a2810",
                 fg=COLORS["accent_gold"],
                 font=font("base", "bold")).pack(side="left")

        close = tk.Button(
            inner, text="✕",
            bg="#2a2810", fg=COLORS["text_muted"],
            relief="flat", bd=0, cursor="hand2",
            font=font("base"),
            command=self._hide_toast,
        )
        close.pack(side="right")

        # Border
        tk.Frame(bar, bg=COLORS["accent_gold_dim"], height=1).pack(
            fill="x", side="bottom"
        )

        # Auto-dismiss
        self.after(duration_ms, self._hide_toast)

    def _hide_toast(self):
        for w in self.notif_frame.winfo_children():
            w.destroy()
        self.notif_frame.config(height=0)
        self.page_area.place(y=58)