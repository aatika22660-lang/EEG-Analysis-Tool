import os
import math
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QDialog, QGridLayout, QSpacerItem,
                             QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPixmap, QFont, QCursor, QPainter, QPainterPath, QPen, QColor, QBrush, QRadialGradient

from theme import CREAM, PANEL_BG, DUSTY_BLUE, BOLD_BLUE, LIGHT_BLUE, FAINT_LINE, TEXT_DARK


class LandingPage(QWidget):
    """Full-screen landing page shown before any EEG file is loaded."""

    # Signal-like callback — set by main window
    on_load_clicked = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {CREAM};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Centre everything vertically
        outer.addStretch(3)

        # ── 1. Logo ──
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = "/Users/aatikashaikh/EEG_Signal_Analysis_GUI/logo.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        logo_label.setStyleSheet("background: transparent;")
        outer.addWidget(logo_label, alignment=Qt.AlignCenter)

        outer.addSpacing(12)

        # ── 2. Title ──
        title = QLabel("Interactive EEG Signal Analysis\nand Artifact Removal Tool")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-family: Georgia;
            font-size: 28px;
            font-weight: bold;
            color: {DUSTY_BLUE};
            background: transparent;
        """)
        outer.addWidget(title, alignment=Qt.AlignCenter)

        # ── 3. Spacing ──
        outer.addSpacing(32)

        # ── 4. Load Button (outlined) ──
        self.load_btn = QPushButton("Load EEG File")
        self.load_btn.setFixedSize(200, 44)
        self.load_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.load_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {DUSTY_BLUE};
                font-family: Georgia;
                font-size: 15px;
                font-weight: bold;
                border: 2px solid {DUSTY_BLUE};
                border-radius: 6px;
                padding: 8px 16px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {DUSTY_BLUE};
                color: {CREAM};
            }}
        """)
        self.load_btn.clicked.connect(self._on_load)
        outer.addWidget(self.load_btn, alignment=Qt.AlignCenter)

        # ── 5. Spacing ──
        outer.addSpacing(36)

        # ── 6. How to Use ──
        how_label = QLabel("How to Use")
        how_label.setAlignment(Qt.AlignCenter)
        how_label.setStyleSheet(f"""
            font-family: Georgia;
            font-size: 14px;
            font-weight: bold;
            color: {LIGHT_BLUE};
            background: transparent;
        """)
        outer.addWidget(how_label, alignment=Qt.AlignCenter)

        outer.addSpacing(8)

        steps = [
            "1.  Load your EEG file (.edf, .mat, or .csv)",
            "2.  Visualize the raw signal in the Visualization tab",
            "3.  Apply and compare denoising methods",
            "4.  Export your results",
        ]
        for step_text in steps:
            s = QLabel(step_text)
            s.setAlignment(Qt.AlignCenter)
            s.setStyleSheet(f"""
                font-family: Georgia;
                font-size: 12px;
                color: {LIGHT_BLUE};
                background: transparent;
                padding: 1px 0px;
            """)
            outer.addWidget(s, alignment=Qt.AlignCenter)

        outer.addStretch(3)

        # ── 8. Credits ──
        credits = QLabel("By Mohammad Azlaan & Aatika Asim")
        credits.setAlignment(Qt.AlignCenter)
        credits.setStyleSheet(f"""
            font-family: Georgia;
            font-size: 10px;
            color: {DUSTY_BLUE};
            background: transparent;
        """)
        outer.addWidget(credits, alignment=Qt.AlignCenter)

        outer.addSpacing(14)

    # ── Helpers ──

    def _on_load(self):
        if self.on_load_clicked:
            self.on_load_clicked()