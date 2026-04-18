"""
assets/styles/theme.py
Central theme definition for Kendra (Tkinter version).
All colors, font sizes, and spacing live here.
Import COLORS, FONTS, RADIUS anywhere in views/.
"""
import os
import tkinter.font as tkfont

# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_base":       "#16150f",
    "bg_surface":    "#1e1d15",
    "bg_card":       "#252318",
    "bg_elevated":   "#2a2820",
    "bg_hover":      "#323028",
    "bg_input":      "#1a1814",

    # Accent colors
    "accent_gold":   "#d4a843",
    "accent_gold_dim":"#a07830",
    "accent_sage":   "#7fa669",
    "accent_rust":   "#c46a3a",
    "accent_lavender":"#9b7fc4",
    "danger":        "#e07848",

    # Text
    "text_primary":  "#f0ead8",
    "text_secondary":"#a89f85",
    "text_muted":    "#6b6450",
    "text_inverse":  "#16150f",

    # Borders
    "border":        "#2e2c1e",
    "border_strong": "#3a3828",
    "border_gold":   "#d4a843",

    # Badges
    "badge_done_bg": "#1a2e18",
    "badge_done_fg": "#7fa669",
    "badge_warn_bg": "#2a2010",
    "badge_warn_fg": "#d4a843",
    "badge_over_bg": "#2e1a10",
    "badge_over_fg": "#e07848",

    # Topbar
    "topbar_bg":     "#0e0d08",
}

# ── Font sizes ─────────────────────────────────────────────────────────────────
FONT_SIZES = {
    "xs":    9,
    "sm":   11,
    "base": 13,
    "md":   15,
    "lg":   18,
    "xl":   24,
    "hero": 32,
}

# ── Spacing ────────────────────────────────────────────────────────────────────
PAD = {
    "xs":  4,
    "sm":  8,
    "md": 16,
    "lg": 24,
    "xl": 32,
}

# ── Card corner radius (for PIL rounded rects) ────────────────────────────────
RADIUS = {
    "sm":  6,
    "md": 12,
    "lg": 18,
    "xl": 24,
}

# ── Font family ────────────────────────────────────────────────────────────────
_FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
FONT_FAMILY = "Segoe UI"   # fallback


def load_fonts(root) -> str:
    """
    Try to load Nunito from assets/fonts/.
    Returns the font family name that was successfully loaded.
    Falls back to Segoe UI on Windows, TkDefaultFont elsewhere.
    """
    global FONT_FAMILY
    try:
        from PIL import ImageFont
        nunito_path = os.path.join(_FONTS_DIR, "Nunito-Regular.ttf")
        if os.path.exists(nunito_path):
            # Register with tkinter via a hidden label trick
            import tkinter as tk
            root.tk.call("font", "create", "Nunito",
                         "-family", "Nunito", "-size", 13)
            # Load via PIL to verify it works
            ImageFont.truetype(nunito_path, 13)
            FONT_FAMILY = "Nunito"
            print(f"[Theme] Nunito font loaded.")
        else:
            print(f"[Theme] Nunito not found, using {FONT_FAMILY}")
    except Exception as e:
        print(f"[Theme] Font load failed ({e}), using {FONT_FAMILY}")
    return FONT_FAMILY


def font(size_key: str = "base", weight: str = "normal") -> tuple:
    """Return a tkinter font tuple: (family, size, weight)"""
    size = FONT_SIZES.get(size_key, 13)
    return (FONT_FAMILY, size, weight)


def font_size(size_key: str = "base") -> int:
    return FONT_SIZES.get(size_key, 13)