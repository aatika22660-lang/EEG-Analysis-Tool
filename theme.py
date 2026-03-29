# the cream + dusty blue minimalist aesthetic

CREAM      = "#F4EFE8"
PANEL_BG   = "#EDE8E2"
DUSTY_BLUE = "#7E8FB2"
BOLD_BLUE  = "#6B7DA6"
LIGHT_BLUE = "#A3B0C8"
FAINT_LINE = "#C8CCD4"
TEXT_DARK  = "#5A6A8C"

GLOBAL_STYLE = f"""
    QMainWindow {{
        background-color: {CREAM};
    }}
    QTabWidget::pane {{
        border: 1px solid {FAINT_LINE};
        background-color: {CREAM};
        border-radius: 6px;
    }}
    QTabBar::tab {{
        background-color: {PANEL_BG};
        color: {LIGHT_BLUE};
        font-family: Georgia;
        font-size: 14px;
        padding: 8px 24px;
        min-width: 120px;
        border: 1px solid {FAINT_LINE};
        border-bottom-color: {FAINT_LINE};
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{
        background-color: {CREAM};
        color: {DUSTY_BLUE};
        font-weight: bold;
        border-bottom-color: {CREAM};
    }}
    QLabel {{
        font-family: Georgia;
        color: {TEXT_DARK};
    }}
    QPushButton {{
        background-color: {DUSTY_BLUE};
        color: {CREAM};
        font-family: Georgia;
        font-size: 14px;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        letter-spacing: 1px;
        padding: 8px 16px;
    }}
    QPushButton:hover {{
        background-color: {BOLD_BLUE};
    }}
    QTableWidget {{
        background-color: {PANEL_BG};
        color: {TEXT_DARK};
        font-family: Georgia;
        gridline-color: {FAINT_LINE};
        border: 1px solid {FAINT_LINE};
        border-radius: 6px;
    }}
    QHeaderView::section {{
        background-color: {DUSTY_BLUE};
        color: {CREAM};
        font-family: Georgia;
        font-weight: bold;
        padding: 4px;
        border: 1px solid {FAINT_LINE};
    }}
"""
