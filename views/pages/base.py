"""
views/pages/base.py
Kendra Pro shared widgets.
- BorderCard: 1px border trick, zero PIL
- ScrollableFrame: per-canvas mousewheel (no bind_all)
- Flat buttons, thin progress bar, clean form helpers
"""
import tkinter as tk
from tkinter import ttk
from assets.styles.theme import COLORS, PAD, font, font_size


# ── Border card (replaces PIL RoundedCard) ────────────────────────────────────

class BorderCard(tk.Frame):
    """
    A card with a 1px border using the 2-frame trick.
    Outer frame = border color, inner frame = card color.
    Zero PIL, instant render.
    """
    def __init__(self, parent,
                 bg: str = COLORS["bg_surface"],
                 border: str = COLORS["border"],
                 padx: int = 16, pady: int = 14,
                 **kwargs):
        # Outer frame acts as the border
        super().__init__(parent, bg=border, **kwargs)

        # Inner frame is the actual card
        self.inner = tk.Frame(self, bg=bg, padx=padx, pady=pady)
        self.inner.pack(fill="both", expand=True, padx=1, pady=1)

        # Expose inner bg for child widgets
        self.bg = bg


# ── Scrollable frame (per-canvas wheel binding) ───────────────────────────────

class ScrollableFrame(tk.Frame):
    """
    Vertically scrollable frame.
    Mousewheel bound only to this canvas — no bind_all pollution.
    """
    def __init__(self, parent, bg: str = COLORS["bg_base"], **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        self._canvas = tk.Canvas(
            self, bg=bg, highlightthickness=0, bd=0
        )
        self._scrollbar = ttk.Scrollbar(
            self, orient="vertical",
            command=self._canvas.yview,
            style="Kendra.Vertical.TScrollbar",
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

        self._canvas.bind("<Configure>", self._on_canvas_resize)

        # Per-canvas mouse wheel — no bind_all
        self._canvas.bind("<Enter>", self._bind_wheel)
        self._canvas.bind("<Leave>", self._unbind_wheel)

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._window_id, width=event.width)

    def _bind_wheel(self, event):
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_wheel(self, event):
        self._canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ── Buttons ───────────────────────────────────────────────────────────────────

def primary_btn(parent, text: str, command=None, width: int = None) -> tk.Button:
    kw = {"width": width} if width else {}
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["accent"], fg=COLORS["text_inverse"],
        font=font("sm", "bold"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["accent_hover"],
        activeforeground=COLORS["text_inverse"],
        padx=16, pady=7, **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["accent_hover"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["accent"]))
    return btn


def secondary_btn(parent, text: str, command=None) -> tk.Button:
    """Outline-style button."""
    # Use a border frame trick for outline effect
    outer = tk.Frame(parent, bg=COLORS["border"])
    btn = tk.Button(
        outer, text=text, command=command,
        bg=COLORS["bg_elevated"], fg=COLORS["text_primary"],
        font=font("sm"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["bg_hover"],
        activeforeground=COLORS["text_primary"],
        padx=14, pady=6,
    )
    btn.pack(padx=1, pady=1)
    btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["bg_hover"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["bg_elevated"]))
    outer._btn = btn  # expose for callers who need to configure
    return outer


def ghost_btn(parent, text: str, command=None,
              fg: str = None) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["bg_surface"],
        fg=fg or COLORS["text_secondary"],
        font=font("sm"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["bg_elevated"],
        activeforeground=COLORS["text_primary"],
        padx=10, pady=5,
    )
    btn.bind("<Enter>", lambda e: btn.config(
        bg=COLORS["bg_elevated"], fg=COLORS["text_primary"]
    ))
    btn.bind("<Leave>", lambda e: btn.config(
        bg=COLORS["bg_surface"], fg=fg or COLORS["text_secondary"]
    ))
    return btn


def danger_btn(parent, text: str, command=None) -> tk.Button:
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLORS["bg_surface"], fg=COLORS["accent_red"],
        font=font("sm"),
        relief="flat", bd=0, cursor="hand2",
        activebackground=COLORS["bg_elevated"],
        activeforeground=COLORS["accent_red"],
        padx=14, pady=6,
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["bg_elevated"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["bg_surface"]))
    return btn


# ── Labels ────────────────────────────────────────────────────────────────────

def page_title(parent, text: str, bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=bg or COLORS["bg_base"],
        fg=COLORS["text_primary"],
        font=font("hero", "bold"),
        anchor="w",
    )


def page_subtitle(parent, text: str, bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=bg or COLORS["bg_base"],
        fg=COLORS["text_secondary"],
        font=font("sm"),
        anchor="w",
    )


def section_label(parent, text: str, bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text.upper(),
        bg=bg or COLORS["bg_base"],
        fg=COLORS["text_muted"],
        font=(font()[0], font_size("xs"), "bold"),
        anchor="w",
    )


def body_label(parent, text: str, color: str = None,
               size: str = "base", bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=bg or COLORS["bg_base"],
        fg=color or COLORS["text_primary"],
        font=font(size),
        justify="left", anchor="w",
    )


def muted_label(parent, text: str, bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=bg or COLORS["bg_base"],
        fg=COLORS["text_secondary"],
        font=font("sm"),
        anchor="w",
    )


def status_dot(parent, color: str, bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text="●",
        bg=bg or COLORS["bg_surface"],
        fg=color,
        font=(font()[0], 8),
    )


# ── Form helpers ──────────────────────────────────────────────────────────────

def form_label(parent, text: str, bg: str = None) -> tk.Label:
    return tk.Label(
        parent, text=text,
        bg=bg or COLORS["bg_surface"],
        fg=COLORS["text_secondary"],
        font=(font()[0], font_size("xs"), "bold"),
        anchor="w",
    )


def styled_entry(parent, textvariable=None, width: int = 28,
                 placeholder: str = "",
                 bg: str = None) -> tk.Frame:
    """
    Returns a bordered frame containing a styled Entry.

    The frame exposes two helpers:
      .get()      → always returns real user text (never the placeholder)
      .set(value) → sets the entry value, restoring placeholder if value is empty
      .entry      → the raw tk.Entry widget if needed

    If a textvariable is supplied AND there is no placeholder, the StringVar
    is used normally.  When a placeholder is present we manage state ourselves
    so the placeholder text never leaks into .get() / the StringVar.
    """
    outer = tk.Frame(parent, bg=COLORS["border"])
    inner_frame = tk.Frame(outer, bg=COLORS["bg_input"])
    inner_frame.pack(padx=1, pady=1)

    # Only bind textvariable when there is no placeholder — otherwise
    # the StringVar and the inserted placeholder text fight each other.
    use_var = textvariable if (textvariable is not None and not placeholder) else None

    entry = tk.Entry(
        inner_frame,
        textvariable=use_var,
        bg=COLORS["bg_input"],
        fg=COLORS["text_primary"],
        insertbackground=COLORS["accent"],
        font=font("base"),
        relief="flat", bd=6,
        width=width,
    )
    entry.pack(fill="x")

    # ── Placeholder logic ─────────────────────────────────────────
    _placeholder = placeholder  # captured in closures below

    def _is_placeholder():
        return bool(_placeholder) and entry.get() == _placeholder

    def _show_placeholder():
        entry.delete(0, "end")
        entry.insert(0, _placeholder)
        entry.config(fg=COLORS["text_muted"])

    def _clear_placeholder():
        entry.delete(0, "end")
        entry.config(fg=COLORS["text_primary"])

    def _on_focus_in(e):
        outer.config(bg=COLORS["accent"])
        if _is_placeholder():
            _clear_placeholder()

    def _on_focus_out(e):
        outer.config(bg=COLORS["border"])
        if not entry.get():
            _show_placeholder()
        # Sync StringVar if one was provided (only reached when no placeholder)

    entry.bind("<FocusIn>",  _on_focus_in)
    entry.bind("<FocusOut>", _on_focus_out)

    if _placeholder:
        _show_placeholder()

    # ── Public helpers on the outer frame ─────────────────────────

    def _get() -> str:
        """Return user-typed text, or '' if only placeholder is showing."""
        val = entry.get()
        if _placeholder and val == _placeholder:
            return ""
        return val

    def _set(value: str):
        """Set a value; if empty, restore placeholder."""
        entry.config(fg=COLORS["text_primary"])
        entry.delete(0, "end")
        if value:
            entry.insert(0, value)
        elif _placeholder:
            _show_placeholder()

    outer.entry = entry
    outer.get   = _get
    outer.set   = _set
    return outer


def styled_combobox(parent, values: list,
                    textvariable=None, width: int = 20) -> ttk.Combobox:
    return ttk.Combobox(
        parent, values=values,
        textvariable=textvariable,
        style="Kendra.TCombobox",
        width=width, state="readonly",
    )


# ── Progress bar (thin, 4px) ──────────────────────────────────────────────────

class ProgressBar(tk.Frame):
    def __init__(self, parent, label: str = "",
                 bg: str = None, **kwargs):
        _bg = bg or COLORS["bg_base"]
        super().__init__(parent, bg=_bg, **kwargs)

        header = tk.Frame(self, bg=_bg)
        header.pack(fill="x", pady=(0, 6))

        self._lbl = tk.Label(
            header, text=label,
            bg=_bg, fg=COLORS["text_secondary"],
            font=font("sm"), anchor="w",
        )
        self._lbl.pack(side="left")

        self._count = tk.Label(
            header, text="0 / 0",
            bg=_bg, fg=COLORS["accent"],
            font=font("sm", "bold"),
        )
        self._count.pack(side="right")

        # 4px track
        track = tk.Frame(self, bg=COLORS["bg_elevated"], height=4)
        track.pack(fill="x")
        track.pack_propagate(False)

        self._fill = tk.Frame(track, bg=COLORS["accent"], height=4)
        self._fill.place(x=0, y=0, relheight=1, relwidth=0)

    def update_progress(self, done: int, total: int):
        self._count.config(text=f"{done} / {total}")
        pct = done / max(total, 1)
        self._fill.place(relwidth=pct)
        if pct >= 1.0:
            self._fill.config(bg=COLORS["accent_green"])
        elif pct >= 0.5:
            self._fill.config(bg=COLORS["accent"])
        else:
            self._fill.config(bg=COLORS["accent_amber"])


# ── Tab bar ───────────────────────────────────────────────────────────────────

class TabBar(tk.Frame):
    def __init__(self, parent, tabs: list[str],
                 on_change=None, bg: str = None, **kwargs):
        _bg = bg or COLORS["bg_base"]
        super().__init__(parent, bg=_bg, **kwargs)
        self._on_change = on_change
        self._buttons: list[tk.Button] = []
        self._active = 0
        self._bg = _bg

        for i, label in enumerate(tabs):
            btn = tk.Button(
                self, text=label,
                bg=_bg, fg=COLORS["text_muted"],
                font=font("sm"),
                relief="flat", bd=0, cursor="hand2",
                padx=16, pady=8,
                command=lambda idx=i: self._switch(idx),
            )
            btn.pack(side="left")
            self._buttons.append(btn)

        tk.Frame(self, bg=COLORS["border"], height=1).pack(
            fill="x", side="bottom"
        )
        self._switch(0)

    def _switch(self, idx: int):
        self._active = idx
        for i, btn in enumerate(self._buttons):
            if i == idx:
                btn.config(fg=COLORS["accent"], font=font("sm", "bold"))
            else:
                btn.config(fg=COLORS["text_muted"], font=font("sm"))
        if self._on_change:
            self._on_change(idx)


# ── Stat card ─────────────────────────────────────────────────────────────────

class StatCard(tk.Frame):
    def __init__(self, parent, value: str, label: str,
                 color: str = None, **kwargs):
        super().__init__(
            parent, bg=COLORS["bg_surface"],
            padx=20, pady=16, **kwargs
        )
        # Left accent bar
        tk.Frame(self, bg=color or COLORS["accent"], width=3).pack(
            side="left", fill="y", padx=(0, 14)
        )
        text_col = tk.Frame(self, bg=COLORS["bg_surface"])
        text_col.pack(side="left")

        self._val_lbl = tk.Label(
            text_col, text=value,
            bg=COLORS["bg_surface"],
            fg=color or COLORS["text_primary"],
            font=font("xl", "bold"),
        )
        self._val_lbl.pack(anchor="w")

        tk.Label(
            text_col, text=label.upper(),
            bg=COLORS["bg_surface"],
            fg=COLORS["text_muted"],
            font=(font()[0], font_size("xs"), "bold"),
        ).pack(anchor="w")

    def set_value(self, value: str):
        self._val_lbl.config(text=value)

    def set_color(self, color: str):
        self._val_lbl.config(fg=color)


# ── List row ──────────────────────────────────────────────────────────────────

class ListRow(tk.Frame):
    """
    A clean list row with a left colored accent bar and hover effect.
    """
    def __init__(self, parent, accent: str = None, **kwargs):
        super().__init__(parent, bg=COLORS["bg_surface"], **kwargs)

        if accent:
            tk.Frame(self, bg=accent, width=3).pack(
                side="left", fill="y"
            )

        self.inner = tk.Frame(self, bg=COLORS["bg_surface"],
                              padx=14, pady=10)
        self.inner.pack(side="left", fill="both", expand=True)

        # Border bottom
        tk.Frame(self, bg=COLORS["border_subtle"], height=1).pack(
            side="bottom", fill="x"
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.config(bg=COLORS["bg_elevated"])
        self.inner.config(bg=COLORS["bg_elevated"])

    def _on_leave(self, e):
        self.config(bg=COLORS["bg_surface"])
        self.inner.config(bg=COLORS["bg_surface"])


# ── Empty state ───────────────────────────────────────────────────────────────

class EmptyState(tk.Frame):
    def __init__(self, parent, icon: str, title: str,
                 subtitle: str = "", bg: str = None, **kwargs):
        _bg = bg or COLORS["bg_base"]
        super().__init__(parent, bg=_bg, **kwargs)

        inner = tk.Frame(self, bg=_bg)
        inner.place(relx=0.5, rely=0.42, anchor="center")

        tk.Label(inner, text=icon, bg=_bg,
                 font=(font()[0], 36)).pack()
        tk.Label(inner, text=title,
                 bg=_bg, fg=COLORS["text_primary"],
                 font=font("md", "bold")).pack(pady=(10, 4))
        if subtitle:
            tk.Label(inner, text=subtitle,
                     bg=_bg, fg=COLORS["text_secondary"],
                     font=font("sm"), wraplength=320).pack()


# ── No pet placeholder ────────────────────────────────────────────────────────

class NoPetWidget(tk.Frame):
    def __init__(self, parent, feature: str = "feature",
                 bg: str = None, **kwargs):
        _bg = bg or COLORS["bg_base"]
        super().__init__(parent, bg=_bg, **kwargs)

        inner = tk.Frame(self, bg=_bg)
        inner.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(inner, text="🐾", bg=_bg,
                 font=(font()[0], 44)).pack()
        tk.Label(inner, text="No pet selected",
                 bg=_bg, fg=COLORS["text_primary"],
                 font=font("lg", "bold")).pack(pady=(10, 4))
        tk.Label(inner,
                 text=f"Select a pet from the top bar to view their {feature} data.",
                 bg=_bg, fg=COLORS["text_secondary"],
                 font=font("sm"), wraplength=320).pack()


# ── Divider ───────────────────────────────────────────────────────────────────

def divider(parent, bg: str = None) -> tk.Frame:
    return tk.Frame(parent, bg=bg or COLORS["border"], height=1)


# ── Check button ──────────────────────────────────────────────────────────────

def check_btn(parent, done: bool, command=None,
              bg: str = None) -> tk.Button:
    _bg = bg or COLORS["bg_surface"]
    if done:
        btn = tk.Button(
            parent, text="✓",
            bg=COLORS["accent_green"], fg="#0f1117",
            font=font("sm", "bold"),
            relief="flat", bd=0, width=3,
            cursor="arrow", pady=4,
        )
    else:
        btn = tk.Button(
            parent, text="",
            bg=COLORS["bg_elevated"], fg=COLORS["text_muted"],
            font=font("sm"),
            relief="flat", bd=0, width=3,
            cursor="hand2", pady=4,
            command=command,
        )
        btn.bind("<Enter>", lambda e: btn.config(
            bg=COLORS["accent_green"], fg="#0f1117", text="✓"
        ))
        btn.bind("<Leave>", lambda e: btn.config(
            bg=COLORS["bg_elevated"], fg=COLORS["text_muted"], text=""
        ))
    return btn


# ── Page header builder ───────────────────────────────────────────────────────

def page_header(parent, title: str, subtitle: str = "",
                action_text: str = None, action_cmd=None,
                bg: str = None) -> tk.Frame:
    """Builds a standard page header with title, subtitle, and optional action button."""
    _bg = bg or COLORS["bg_base"]
    frame = tk.Frame(parent, bg=_bg)

    left = tk.Frame(frame, bg=_bg)
    left.pack(side="left", fill="x", expand=True)

    tk.Label(left, text=title, bg=_bg,
             fg=COLORS["text_primary"],
             font=font("hero", "bold"), anchor="w").pack(fill="x")

    if subtitle:
        tk.Label(left, text=subtitle, bg=_bg,
                 fg=COLORS["text_secondary"],
                 font=font("sm"), anchor="w").pack(fill="x", pady=(2, 0))

    if action_text and action_cmd:
        primary_btn(frame, action_text, action_cmd).pack(
            side="right", anchor="center"
        )

    return frame