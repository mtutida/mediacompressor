from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


class UIPalette:
    """Unified UI palette derived from Qt system palette with accent integration."""

    DARK = False

    CARD_BG = None
    CARD_BORDER = None
    TEXT_PRIMARY = None
    TEXT_SECONDARY = None

    FOOTER_BG = None
    FOOTER_BORDER = None

    BUTTON_BG = None
    BUTTON_BG_HOVER = None
    BUTTON_BG_ACTIVE = None

    ACCENT = None
    ACCENT_HOVER = None
    ACCENT_ACTIVE = None
    ACCENT_TEXT = None
    
    BUTTON_TEXT = None
    BUTTON_TEXT_DISABLED = None

    @classmethod
    def reload(cls):
        app = QApplication.instance()
        if not app:
            return

        palette: QPalette = app.palette()

        window = palette.color(QPalette.Window)
        text = palette.color(QPalette.WindowText)
        base = palette.color(QPalette.Base)
        highlight = palette.color(QPalette.Highlight)

        cls.DARK = window.lightness() < 128

        cls.CARD_BG = base
        cls.CARD_BORDER = palette.color(QPalette.Mid)

        cls.TEXT_PRIMARY = text
        cls.TEXT_SECONDARY = palette.color(QPalette.Disabled, QPalette.WindowText)

        cls.FOOTER_BG = window
        cls.FOOTER_BORDER = palette.color(QPalette.Dark)

        cls.BUTTON_BG = palette.color(QPalette.Button)
        cls.BUTTON_BG_HOVER = highlight.lighter(140)
        cls.BUTTON_BG_ACTIVE = highlight

        cls.BUTTON_TEXT = palette.color(QPalette.ButtonText)
        cls.BUTTON_TEXT_DISABLED = palette.color(QPalette.Disabled, QPalette.ButtonText)

        # Accent integration
        cls.ACCENT = highlight
        cls.ACCENT_HOVER = highlight.lighter(120)
        cls.ACCENT_ACTIVE = highlight.darker(120)
        cls.ACCENT_TEXT = palette.color(QPalette.HighlightedText)


# initialize palette once
UIPalette.reload()