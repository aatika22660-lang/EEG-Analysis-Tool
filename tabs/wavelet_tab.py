from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from theme import CREAM, DUSTY_BLUE, PANEL_BG

class WaveletDenoisingTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left Sidebar for Parameters
        sidebar = QFrame()
        sidebar.setStyleSheet(f"background-color: {PANEL_BG}; border-radius: 6px;")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        
        title = QLabel("Wavelet Parameters")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {DUSTY_BLUE};")
        sidebar_layout.addWidget(title)
        
        # Placeholder for dropdowns/sliders
        sidebar_layout.addWidget(QLabel("(Dropdowns & Sliders to be added later)"))
        sidebar_layout.addStretch()
        
        layout.addWidget(sidebar)
        
        # Right Canvas Area
        canvas_area = QVBoxLayout()
        self.wavelet_figure, self.wavelet_ax = plt.subplots(facecolor=CREAM)
        self.wavelet_canvas = FigureCanvas(self.wavelet_figure)
        self.wavelet_canvas.setStyleSheet("background-color: transparent;")
        self.wavelet_ax.set_title("Wavelet Denoised Signal")
        self.wavelet_ax.set_facecolor(CREAM)
        canvas_area.addWidget(self.wavelet_canvas)
        
        # from matlab_bridge import get_engine
        # eng = get_engine()
        # result = eng.wavelet_denoise(signal)  # calls partner's .m file
        
        # TODO: partner plugs in wavelet plotting here
        
        layout.addLayout(canvas_area)
