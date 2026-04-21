"""
views/app.py
Root Tk window. Gradient background drawn once with Canvas line drawing.
No PIL, no image loading, no resize redraws.
"""
import tkinter as tk
from tkinter import ttk
from assets.styles.theme import COLORS, font

# ── ttk style setup ───────────────────────────────────────────────────────────

def _setup_ttk_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    # Scrollbar — thin and subtle
    style.configure("Kendra.Vertical.TScrollbar",
        background=COLORS["bg_elevated"],
        troughcolor=COLORS["bg_surface"],
        bordercolor=COLORS["bg_surface"],
        arrowcolor=COLORS["text_muted"],
        relief="flat", borderwidth=0,
        width=6,
    )
    style.map("Kendra.Vertical.TScrollbar",
        background=[("active", COLORS["border"])],
    )

    # Combobox
    style.configure("Kendra.TCombobox",
        fieldbackground=COLORS["bg_input"],
        background=COLORS["bg_elevated"],
        foreground=COLORS["text_primary"],
        arrowcolor=COLORS["text_secondary"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["bg_input"],
        darkcolor=COLORS["bg_input"],
        selectbackground=COLORS["accent"],
        selectforeground=COLORS["text_inverse"],
        padding=(8, 6),
    )
    style.map("Kendra.TCombobox",
        fieldbackground=[("readonly", COLORS["bg_input"])],
        foreground=[("readonly", COLORS["text_primary"])],
    )


# ── Gradient canvas ───────────────────────────────────────────────────────────

def _draw_gradient(canvas, width: int, height: int):
    """Draw a vertical gradient from bg_base to bg_surface. Fast, no PIL."""
    # Parse hex colors
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    top = hex_to_rgb(COLORS["bg_base"])
    bot = hex_to_rgb(COLORS["bg_surface"])

    canvas.delete("gradient")
    steps = min(height, 400)  # cap steps for performance
    for i in range(steps):
        t = i / steps
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        color = f"#{r:02x}{g:02x}{b:02x}"
        y0 = int(i * height / steps)
        y1 = int((i + 1) * height / steps)
        canvas.create_rectangle(
            0, y0, width, y1,
            fill=color, outline=color, tags="gradient"
        )


class KendraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kendra")
        self.geometry("1280x800")
        self.minsize(1024, 680)
        self.configure(bg=COLORS["bg_base"])

        _setup_ttk_styles(self)

        # ── Gradient background ──────────────────────────────────
        self._bg_canvas = tk.Canvas(
            self, highlightthickness=0, bd=0,
            bg=COLORS["bg_base"]
        )
        self._bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Draw gradient once after window is ready
        self.after(50, self._draw_once)

        # ── Top bar frame ─────────────────────────────────────────
        self.topbar_frame = tk.Frame(
            self, bg=COLORS["topbar_bg"], height=52
        )
        self.topbar_frame.place(x=0, y=0, relwidth=1)
        self.topbar_frame.pack_propagate(False)

        # Top bar bottom border
        self._topbar_border = tk.Frame(
            self, bg=COLORS["topbar_border"], height=1
        )
        self._topbar_border.place(x=0, y=52, relwidth=1)

        # ── Toast notification bar ────────────────────────────────
        self.notif_frame = tk.Frame(self, bg=COLORS["bg_base"], height=0)
        self.notif_frame.place(x=0, y=53, relwidth=1)

        # ── Page area ─────────────────────────────────────────────
        self.page_area = tk.Frame(self, bg=COLORS["bg_base"])
        self.page_area.place(x=0, y=53, relwidth=1, relheight=1)

        # Page registry
        self._pages: dict[str, tk.Frame] = {}
        self._current_page: str = ""

    def _draw_once(self):
        w = self.winfo_width()
        h = self.winfo_height()
        _draw_gradient(self._bg_canvas, w, h)

    # ── Page management ───────────────────────────────────────────

    def register_page(self, page_id: str, page_frame: tk.Frame):
        self._pages[page_id] = page_frame
        page_frame.place(in_=self.page_area,
                         x=0, y=0, relwidth=1, relheight=1)

    def show_page(self, page_id: str):
        page = self._pages.get(page_id)
        if page:
            page.tkraise()
            self._current_page = page_id

    # ── Toast notifications ───────────────────────────────────────

    def show_toast(self, text: str, icon: str = "●", duration_ms: int = 4000):
        for w in self.notif_frame.winfo_children():
            w.destroy()

        self.notif_frame.config(height=40)
        self.page_area.place(y=93)

        bar = tk.Frame(self.notif_frame, bg=COLORS["bg_elevated"])
        bar.pack(fill="x", padx=16, pady=4)

        # Left accent bar
        tk.Frame(bar, bg=COLORS["accent"], width=3).pack(
            side="left", fill="y"
        )

        inner = tk.Frame(bar, bg=COLORS["bg_elevated"])
        inner.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        tk.Label(inner, text=f"{icon}  {text}",
                 bg=COLORS["bg_elevated"],
                 fg=COLORS["text_primary"],
                 font=font("sm", "bold"),
                 anchor="w").pack(side="left")

        tk.Button(inner, text="✕",
                  bg=COLORS["bg_elevated"],
                  fg=COLORS["text_muted"],
                  relief="flat", bd=0,
                  font=font("xs"),
                  cursor="hand2",
                  command=self._hide_toast).pack(side="right")

        self.after(duration_ms, self._hide_toast)

    def _hide_toast(self):
        for w in self.notif_frame.winfo_children():
            w.destroy()
        self.notif_frame.config(height=0)
        self.page_area.place(y=53)