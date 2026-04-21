"""
assets/styles/theme.py
Kendra Pro — Professional dark theme.
Cool blue-tinted dark, clean typography, precise accents.
"""
import os

# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_base":      "#0f1117",
    "bg_surface":   "#161b22",
    "bg_elevated":  "#1c2128",
    "bg_hover":     "#21262d",
    "bg_input":     "#0d1117",
    "bg_border":    "#30363d",

    # Accents
    "accent":       "#4f8ef7",   # electric blue — primary actions
    "accent_hover": "#6ba3f9",
    "accent_green": "#3fb950",   # success, done
    "accent_amber": "#d29922",   # warning, pending
    "accent_red":   "#f85149",   # danger, overdue
    "accent_purple":"#a371f7",   # grooming
    "accent_orange":"#f0883e",   # activity

    # Text
    "text_primary":  "#e6edf3",
    "text_secondary":"#8b949e",
    "text_muted":    "#484f58",
    "text_inverse":  "#0f1117",

    # Borders
    "border":       "#30363d",
    "border_subtle":"#21262d",

    # Status badges (text only, no bg)
    "done_fg":    "#3fb950",
    "pending_fg": "#d29922",
    "overdue_fg": "#f85149",

    # Topbar
    "topbar_bg":  "#0d1117",
    "topbar_border": "#21262d",
}

# ── Font sizes ─────────────────────────────────────────────────────────────────
FONT_SIZES = {
    "xs":    9,
    "sm":   11,
    "base": 13,
    "md":   15,
    "lg":   18,
    "xl":   26,
    "hero": 30,
}

# ── Spacing ────────────────────────────────────────────────────────────────────
PAD = {
    "xs":  4,
    "sm":  8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# ── Font family — no loading needed, system fonts only ───────────────────────
import sys
if sys.platform == "win32":
    FONT_FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    FONT_FAMILY = "SF Pro Display"
else:
    FONT_FAMILY = "Ubuntu"

MONO_FAMILY = "Consolas" if sys.platform == "win32" else "Menlo"


def font(size_key: str = "base", weight: str = "normal") -> tuple:
    """Return a tkinter font tuple: (family, size, weight)"""
    size = FONT_SIZES.get(size_key, 13)
    return (FONT_FAMILY, size, weight)


def mono(size_key: str = "sm") -> tuple:
    size = FONT_SIZES.get(size_key, 11)
    return (MONO_FAMILY, size, "normal")


def font_size(size_key: str = "base") -> int:
    return FONT_SIZES.get(size_key, 13)