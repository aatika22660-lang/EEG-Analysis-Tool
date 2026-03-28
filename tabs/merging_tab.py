from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from theme import CREAM, DUSTY_BLUE, PANEL_BG

class SignalMergingTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left Sidebar for Channel Selection
        sidebar = QFrame()
        sidebar.setStyleSheet(f"background-color: {PANEL_BG}; border-radius: 6px;")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        
        title = QLabel("Channel Selection")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {DUSTY_BLUE};")
        sidebar_layout.addWidget(title)
        
        # Empty channel selection area
        sidebar_layout.addWidget(QLabel("(Channel checkboxes to be added later)"))
        sidebar_layout.addStretch()
        
        layout.addWidget(sidebar)
        
        # Right Canvas Area
        canvas_area = QVBoxLayout()
        self.merge_figure, self.merge_ax = plt.subplots(facecolor=CREAM)
        self.merge_canvas = FigureCanvas(self.merge_figure)
        self.merge_canvas.setStyleSheet("background-color: transparent;")
        self.merge_ax.set_title("Merged Signals")
        self.merge_ax.set_facecolor(CREAM)
        canvas_area.addWidget(self.merge_canvas)
        
        # from matlab_bridge import get_engine
        # eng = get_engine()
        # result = eng.merge_channels(signal)  # calls partner's .m file
        
        # TODO: partner plugs in merged plotting here
        
        layout.addLayout(canvas_area)
