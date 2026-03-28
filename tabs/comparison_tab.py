from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from theme import CREAM, DUSTY_BLUE

class ComparisonTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Top half: Side by side plots
        plots_layout = QHBoxLayout()
        
        self.wavelet_compare_figure, self.wavelet_compare_ax = plt.subplots(facecolor=CREAM)
        self.wavelet_compare_canvas = FigureCanvas(self.wavelet_compare_figure)
        self.wavelet_compare_canvas.setStyleSheet("background-color: transparent;")
        self.wavelet_compare_ax.set_title("Wavelet Output")
        self.wavelet_compare_ax.set_facecolor(CREAM)
        plots_layout.addWidget(self.wavelet_compare_canvas)
        # TODO: partner plugs in wavelet comparison plotting here
        
        self.adaptive_compare_figure, self.adaptive_compare_ax = plt.subplots(facecolor=CREAM)
        self.adaptive_compare_canvas = FigureCanvas(self.adaptive_compare_figure)
        self.adaptive_compare_canvas.setStyleSheet("background-color: transparent;")
        self.adaptive_compare_ax.set_title("Adaptive Output")
        self.adaptive_compare_ax.set_facecolor(CREAM)
        plots_layout.addWidget(self.adaptive_compare_canvas)
        # TODO: partner plugs in adaptive comparison plotting here
        
        layout.addLayout(plots_layout)
        
        # Bottom half: Metrics table
        title = QLabel("Performance Metrics")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {DUSTY_BLUE};")
        layout.addWidget(title)
        
        self.metrics_table = QTableWidget(0, 3)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Wavelet", "Adaptive"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.metrics_table)
        
        # from matlab_bridge import get_engine
        # eng = get_engine()
        # result = eng.compare_methods(signal)  # calls partner's .m file
        
        # TODO: partner populates metrics table here
