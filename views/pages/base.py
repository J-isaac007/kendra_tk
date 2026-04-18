"""
views/pages/base.py
Shared widgets and helpers used across all Kendra pages.
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from assets.styles.theme import COLORS, RADIUS, PAD, font, font_size


# ── PIL rounded rectangle helpers ─────────────────────────────────────────────

def _make_rounded_image(width: int, height: int, radius: int,
                        fill: str, outline: str = None,
                        outline_width: int = 1) -> Image.Image:
    """Create a PIL RGBA image with a rounded rectangle."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Fill
    r, g, b = int(fill[1:3],16), int(fill[3:5],16), int(fill[5:7],16)
    draw.rounded_rectangle([0, 0, width-1, height-1],
                           radius=radius, fill=(r, g, b, 255))
    # Outline
    if outline:
        ro, go, bo = int(outline[1:3],16), int(outline[3:5],16), int(outline[5:7],16)
        draw.rounded_rectangle([0, 0, width-1, height-1],
                               radius=radius, outline=(ro, go, bo, 180),
                               width=outline_width)
    return img


# ── RoundedCard ───────────────────────────────────────────────────────────────

class RoundedCard(tk.Canvas):
    """
    A Canvas that draws a rounded-rectangle background via PIL.
    Use it like a Frame — add child widgets with .inner frame.
    """

    def __init__(self, parent, width: int = 400, height: int = 120,
                 radius: int = RADIUS["lg"],
                 bg_color: str = COLORS["bg_card"],
                 border_color: str = COLORS["border"],
                 **kwargs):
        super().__init__(
            parent,
            width=width, height=height,
            bg=COLORS["bg_base"],
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self._w = width
        self._h = height
        self._radius = radius
        self._bg_color = bg_color
        self._border_color = border_color
        self._img_ref = None  # keep PIL ref alive
        self._draw_bg()

        # Inner frame for child widgets
        self.inner = tk.Frame(self, bg=bg_color)
        self.create_window(
            PAD["md"], PAD["md"],
            anchor="nw",
            window=self.inner,
            width=width - PAD["md"] * 2,
            height=height - PAD["md"] * 2,
        )

    def _draw_bg(self):
        img = _make_rounded_image(
            self._w, self._h, self._radius,
            self._bg_color, self._border_color
        )
        self._img_ref = ImageTk.PhotoImage(img)
        self.create_image(0, 0, anchor="nw", image=self._img_ref)

    def resize(self, width: int, height: int):
        self._w, self._h = width, height
        self.config(width=width, height=height)
        self._draw_bg()
        self.itemconfig(2, width=width - PAD["md"]*2,
                        height=height - PAD["md"]*2)


# ── ScrollableFrame ───────────────────────────────────────────────────────────

class ScrollableFrame(tk.Frame):
    """
    A vertically scrollable frame using Canvas + Scrollbar.
    Add child widgets to .scrollable_frame, not to this widget directly.
    """

    def __init__(self, parent, bg: str = COLORS["bg_base"], **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        self._canvas = tk.Canvas(
            self, bg=bg, highlightthickness=0, bd=0
        )
        self._scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self._canvas.yview
        )
        self.scrollable_frame = tk.Frame(self._canvas, bg=bg)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            )
        )

        self._window_id = self._canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        # Stretch inner frame to canvas width
        self._canvas.bind("<Configure>", self._on_canvas_resize)

        # Mouse wheel scrolling
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._window_id, width=event.width)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ── Styled button helpers ─────────────────────────────────────────────────────

def primary_btn(parent, text: str, command=None, width: int = None) -> tk.Button:
    kw = dict(width=width) if width else {}
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["accent_gold"], fg=COLORS["text_inverse"],
        font=font("base", "bold"),
        relief="flat", bd=0, cursor="hand2",
        activebackground="#e8bc55",
        activeforeground=COLORS["text_inverse"],
        padx=18, pady=8, **kw
    )
    _add_hover(btn, COLORS["accent_gold"], "#e8bc55")
    return btn


def secondary_btn(parent, text: str, command=None) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["bg_elevated"], fg=COLORS["text_primary"],
        font=font("base"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["bg_hover"],
        activeforeground=COLORS["text_primary"],
        padx=14, pady=7,
    )
    _add_hover(btn, COLORS["bg_elevated"], COLORS["bg_hover"])
    return btn


def ghost_btn(parent, text: str, command=None) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
        font=font("sm"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["bg_elevated"],
        activeforeground=COLORS["text_primary"],
        padx=10, pady=5,
    )
    _add_hover(btn, COLORS["bg_card"], COLORS["bg_elevated"])
    return btn


def danger_btn(parent, text: str, command=None) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["bg_card"], fg=COLORS["danger"],
        font=font("base"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["bg_elevated"],
        activeforeground=COLORS["danger"],
        padx=14, pady=7,
    )
    _add_hover(btn, COLORS["bg_card"], COLORS["bg_elevated"])
    return btn


def nav_btn(parent, text: str, command=None, active: bool = False) -> tk.Button:
    fg = COLORS["accent_gold"] if active else COLORS["text_muted"]
    bg = COLORS["bg_elevated"] if active else COLORS["topbar_bg"]
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg,
        font=font("base", "bold" if active else "normal"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["bg_elevated"],
        activeforeground=COLORS["accent_gold"],
        padx=14, pady=10,
    )
    return btn


def _add_hover(btn: tk.Button, normal_bg: str, hover_bg: str):
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))


# ── Label helpers ─────────────────────────────────────────────────────────────

def page_title(parent, text: str) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=COLORS["bg_base"], fg=COLORS["text_primary"],
        font=font("hero", "bold"),
    )


def page_subtitle(parent, text: str) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=COLORS["bg_base"], fg=COLORS["text_muted"],
        font=font("sm"),
    )


def section_label(parent, text: str) -> tk.Label:
    return tk.Label(
        parent, text=text.upper(),
        bg=COLORS["bg_base"], fg=COLORS["text_muted"],
        font=(font()[0], font_size("xs"), "bold"),
    )


def body_label(parent, text: str, color: str = None,
               size: str = "base", bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=bg or COLORS["bg_base"],
        fg=color or COLORS["text_primary"],
        font=font(size),
        justify="left",
    )


def muted_label(parent, text: str, bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=bg or COLORS["bg_base"],
        fg=COLORS["text_muted"],
        font=font("sm"),
    )


def badge(parent, text: str, style: str = "pending",
          bg_override: str = None) -> tk.Label:
    styles = {
        "done":    (COLORS["badge_done_bg"], COLORS["badge_done_fg"]),
        "pending": (COLORS["badge_warn_bg"], COLORS["badge_warn_fg"]),
        "overdue": (COLORS["badge_over_bg"], COLORS["badge_over_fg"]),
    }
    bg_c, fg_c = styles.get(style, styles["pending"])
    return tk.Label(
        parent, text=text,
        bg=bg_override or bg_c, fg=fg_c,
        font=font("xs", "bold"),
        padx=8, pady=3,
        relief="flat",
    )


# ── Form helpers ──────────────────────────────────────────────────────────────

def form_label(parent, text: str) -> tk.Label:
    return tk.Label(
        parent, text=text.upper(),
        bg=COLORS["bg_card"],
        fg=COLORS["accent_gold"],
        font=(font()[0], font_size("xs"), "bold"),
    )


def text_entry(parent, textvariable=None, placeholder: str = "",
               width: int = 28) -> tk.Entry:
    entry = tk.Entry(
        parent,
        textvariable=textvariable,
        bg=COLORS["bg_input"], fg=COLORS["text_primary"],
        insertbackground=COLORS["accent_gold"],
        font=font("base"),
        relief="flat", bd=0,
        width=width,
    )
    # Wrap in a bordered frame
    return entry


def styled_entry(parent, textvariable=None, width: int = 28,
                 placeholder: str = "") -> tk.Frame:
    """Returns a Frame containing a styled Entry with border."""
    frame = tk.Frame(
        parent,
        bg=COLORS["border_strong"],
        padx=1, pady=1,
    )
    entry = tk.Entry(
        frame,
        textvariable=textvariable,
        bg=COLORS["bg_input"], fg=COLORS["text_primary"],
        insertbackground=COLORS["accent_gold"],
        font=font("base"),
        relief="flat", bd=6,
        width=width,
    )
    entry.pack(fill="x")

    if placeholder:
        _add_placeholder(entry, placeholder)

    # Focus border highlight
    entry.bind("<FocusIn>",  lambda e: frame.config(bg=COLORS["accent_gold"]))
    entry.bind("<FocusOut>", lambda e: frame.config(bg=COLORS["border_strong"]))

    frame.entry = entry  # expose entry directly
    return frame


def _add_placeholder(entry: tk.Entry, text: str):
    entry.insert(0, text)
    entry.config(fg=COLORS["text_muted"])

    def on_focus_in(e):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.config(fg=COLORS["text_primary"])

    def on_focus_out(e):
        if not entry.get():
            entry.insert(0, text)
            entry.config(fg=COLORS["text_muted"])

    entry.bind("<FocusIn>",  on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def styled_combobox(parent, values: list, textvariable=None,
                    width: int = 20) -> ttk.Combobox:
    style = ttk.Style()
    style.configure(
        "Kendra.TCombobox",
        fieldbackground=COLORS["bg_input"],
        background=COLORS["bg_elevated"],
        foreground=COLORS["text_primary"],
        arrowcolor=COLORS["accent_gold"],
        bordercolor=COLORS["border_strong"],
        lightcolor=COLORS["bg_input"],
        darkcolor=COLORS["bg_input"],
    )
    cb = ttk.Combobox(
        parent, values=values,
        textvariable=textvariable,
        style="Kendra.TCombobox",
        width=width, state="readonly",
    )
    return cb


# ── Progress bar ──────────────────────────────────────────────────────────────

class ProgressBar(tk.Frame):
    def __init__(self, parent, label: str = "", **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], **kwargs)
        self._label_text = label

        header = tk.Frame(self, bg=COLORS["bg_card"])
        header.pack(fill="x", padx=16, pady=(12, 6))

        self._lbl = tk.Label(
            header, text=label,
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
            font=font("sm"),
        )
        self._lbl.pack(side="left")

        self._count_lbl = tk.Label(
            header, text="0 / 0",
            bg=COLORS["bg_card"], fg=COLORS["accent_gold"],
            font=font("sm", "bold"),
        )
        self._count_lbl.pack(side="right")

        # Track background
        bar_frame = tk.Frame(self, bg=COLORS["bg_card"], padx=16, pady=(0, 12))
        bar_frame.pack(fill="x")

        self._track = tk.Frame(bar_frame, bg=COLORS["bg_elevated"], height=8)
        self._track.pack(fill="x")
        self._track.pack_propagate(False)

        self._fill = tk.Frame(self._track, bg=COLORS["accent_gold"], height=8)
        self._fill.place(x=0, y=0, relheight=1, relwidth=0)

    def update_progress(self, done: int, total: int):
        self._count_lbl.config(text=f"{done} / {total}")
        pct = done / max(total, 1)
        self._fill.place(x=0, y=0, relheight=1, relwidth=pct)
        # Color gradient effect
        if pct >= 1.0:
            self._fill.config(bg=COLORS["accent_sage"])
        elif pct >= 0.5:
            self._fill.config(bg=COLORS["accent_gold"])
        else:
            self._fill.config(bg=COLORS["accent_rust"])


# ── Item row ──────────────────────────────────────────────────────────────────

class ItemRow(tk.Frame):
    """
    Styled list item row with gold border bottom.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=COLORS["bg_card"],
            pady=1,
            **kwargs
        )
        # Bottom border line
        self._content = tk.Frame(self, bg=COLORS["bg_card"])
        self._content.pack(fill="x", padx=0, pady=0)

        self._border = tk.Frame(self, bg=COLORS["border"], height=1)
        self._border.pack(fill="x")

    @property
    def content(self):
        return self._content


# ── Tab bar ───────────────────────────────────────────────────────────────────

class TabBar(tk.Frame):
    def __init__(self, parent, tabs: list[str],
                 on_change=None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self._on_change = on_change
        self._buttons: list[tk.Button] = []
        self._active = 0

        for i, label in enumerate(tabs):
            btn = tk.Button(
                self, text=label,
                bg=COLORS["bg_base"],
                fg=COLORS["text_muted"],
                font=font("base"),
                relief="flat", bd=0,
                cursor="hand2",
                padx=18, pady=8,
                command=lambda idx=i: self._switch(idx),
            )
            btn.pack(side="left")
            self._buttons.append(btn)

        # Bottom border
        tk.Frame(self, bg=COLORS["border"], height=1).pack(
            fill="x", side="bottom"
        )

        self._switch(0)

    def _switch(self, idx: int):
        self._active = idx
        for i, btn in enumerate(self._buttons):
            if i == idx:
                btn.config(
                    fg=COLORS["accent_gold"],
                    font=font("base", "bold"),
                )
            else:
                btn.config(
                    fg=COLORS["text_muted"],
                    font=font("base"),
                )
        if self._on_change:
            self._on_change(idx)


# ── Divider ───────────────────────────────────────────────────────────────────

def divider(parent, color: str = None) -> tk.Frame:
    return tk.Frame(
        parent,
        bg=color or COLORS["border"],
        height=1,
    )


# ── No pet selected placeholder ───────────────────────────────────────────────

class NoPetWidget(tk.Frame):
    def __init__(self, parent, feature: str = "feature", **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)
        self.pack_propagate(False)

        inner = tk.Frame(self, bg=COLORS["bg_base"])
        inner.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(inner, text="🐾", bg=COLORS["bg_base"],
                 font=(font()[0], 52)).pack()
        tk.Label(inner, text="No pet selected",
                 bg=COLORS["bg_base"], fg=COLORS["text_secondary"],
                 font=font("lg", "bold")).pack(pady=(8, 4))
        tk.Label(inner,
                 text=f"Select a pet to view their {feature} data.",
                 bg=COLORS["bg_base"], fg=COLORS["text_muted"],
                 font=font("base")).pack()


# ── Stat card ─────────────────────────────────────────────────────────────────

class StatCard(tk.Frame):
    def __init__(self, parent, value: str, label: str, **kwargs):
        super().__init__(
            parent,
            bg=COLORS["bg_card"],
            padx=16, pady=14,
            **kwargs
        )
        self._val_lbl = tk.Label(
            self, text=value,
            bg=COLORS["bg_card"], fg=COLORS["text_primary"],
            font=font("xl", "bold"),
        )
        self._val_lbl.pack()

        tk.Label(
            self, text=label.upper(),
            bg=COLORS["bg_card"], fg=COLORS["text_muted"],
            font=(font()[0], font_size("xs"), "bold"),
        ).pack()

    def set_value(self, value: str):
        self._val_lbl.config(text=value)

    def set_color(self, color: str):
        self._val_lbl.config(fg=color)


# ── Scrolled text (for logs) ──────────────────────────────────────────────────

class EmptyState(tk.Frame):
    def __init__(self, parent, icon: str, title: str,
                 subtitle: str = "", **kwargs):
        super().__init__(parent, bg=COLORS["bg_base"], **kwargs)

        inner = tk.Frame(self, bg=COLORS["bg_base"])
        inner.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(inner, text=icon, bg=COLORS["bg_base"],
                 font=(font()[0], 40)).pack()
        tk.Label(inner, text=title,
                 bg=COLORS["bg_base"], fg=COLORS["text_secondary"],
                 font=font("md", "bold")).pack(pady=(8, 4))
        if subtitle:
            tk.Label(inner, text=subtitle,
                     bg=COLORS["bg_base"], fg=COLORS["text_muted"],
                     font=font("base"), wraplength=300).pack()