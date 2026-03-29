from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QCheckBox, QSizePolicy
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import traceback
import numpy as np

from theme import CREAM, DUSTY_BLUE, PANEL_BG, LIGHT_BLUE, TEXT_DARK, FAINT_LINE, SIGNAL_COLORS
from matlab_bridge import run_visualize

class VisualizationTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.channel_names = []
        self.time_data = None
        self.freq_data = None
        self.freq_axis = None
        self.time_axis = None
        self.is_loaded = False
        self.error_msg = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title & Controls
        top_layout = QHBoxLayout()
        title = QLabel("Time and Frequency Domain Analysis")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {DUSTY_BLUE};")
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        self.channel_selector = QComboBox()
        self.channel_selector.addItem("All Channels")
        self.channel_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {PANEL_BG};
                color: {TEXT_DARK};
                border: 1px solid {FAINT_LINE};
                border-radius: 4px;
                padding: 4px 10px;
                font-family: Georgia;
                font-size: 14px;
            }}
        """)
        self.channel_selector.currentIndexChanged.connect(self.on_combo_changed)
        self.channel_selector.setEnabled(False)
        top_layout.addWidget(self.channel_selector)
        
        layout.addLayout(top_layout)
        
        # Time Canvas
        self.time_figure, self.time_ax = plt.subplots(facecolor=CREAM)
        self.time_figure.subplots_adjust(bottom=0.2, right=0.95, top=0.9, left=0.1)
        self.time_domain_canvas = FigureCanvas(self.time_figure)
        self.time_domain_canvas.setStyleSheet("background-color: transparent;")
        self.time_domain_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.time_domain_canvas)
        
        # Time Slider
        slider_layout = QHBoxLayout()
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setEnabled(False)
        self.time_slider.valueChanged.connect(self.plot_data)
        self.time_slider_label = QLabel("0s - 10s")
        self.time_slider_label.setStyleSheet(f"color: {TEXT_DARK}; font-family: Georgia; font-size: 14px;")
        slider_layout.addWidget(self.time_slider)
        slider_layout.addWidget(self.time_slider_label)
        layout.addLayout(slider_layout)
        
        # Freq Canvas
        self.freq_figure, self.freq_ax = plt.subplots(facecolor=CREAM)
        self.freq_figure.subplots_adjust(bottom=0.2, right=0.95, top=0.9, left=0.1)
        self.freq_domain_canvas = FigureCanvas(self.freq_figure)
        self.freq_domain_canvas.setStyleSheet("background-color: transparent;")
        self.freq_domain_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.freq_domain_canvas)
        
        # Initial empty state
        self.plot_empty_state()
        
    def plot_empty_state(self, custom_msg=None):
        self._clear_axes()
        msg = custom_msg if custom_msg else (self.error_msg if self.error_msg else "Load an EEG file to begin")
        
        # TODO: partner plugs in here
        for ax in [self.time_ax, self.freq_ax]:
            ax.text(0.5, 0.5, msg, 
                    ha='center', va='center', fontsize=14, color=LIGHT_BLUE, alpha=0.8,
                    transform=ax.transAxes, family='Georgia')
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
                
        self.time_ax.set_title("Time Domain", color='black', pad=10)
        self.freq_ax.set_title("Frequency Domain (PSD)", color='black', pad=10)
        
        self.time_domain_canvas.draw()
        self.freq_domain_canvas.draw()
        
    def _clear_axes(self):
        self.time_ax.clear()
        self.freq_ax.clear()
        self.time_ax.set_facecolor(CREAM)
        self.freq_ax.set_facecolor(CREAM)
        
    def load_new_file(self):
        # Called when a new file is loaded
        if self.app_state["raw_signal"] is None:
            return
            
        try:
            raw = self.app_state["raw_signal"]
            fs = self.app_state["sampling_rate"]
            channels = self.app_state["channel_names"]
            
            t_dt, f_dt, f_ax, t_ax, c_names = run_visualize(raw, fs, channels)
            
            self.time_data = t_dt
            self.freq_data = f_dt
            self.freq_axis = f_ax
            self.time_axis = t_ax
            self.app_state["time_axis"] = t_ax
            self.channel_names = c_names
            self.is_loaded = True
            self.error_msg = None
            
            # Update combobox
            self.channel_selector.blockSignals(True)
            self.channel_selector.clear()
            self.channel_selector.addItem("All Channels")
            for c in self.channel_names:
                self.channel_selector.addItem(str(c))
            self.channel_selector.blockSignals(False)
            self.channel_selector.setEnabled(True)
            
            # Setup slider
            max_t = int(self.time_axis[-1]) if len(self.time_axis) > 0 else 0
            if max_t > 10:
                self.time_slider.setMaximum(max_t - 10)
                self.time_slider.setEnabled(True)
            else:
                self.time_slider.setMaximum(0)
                self.time_slider.setEnabled(False)
                
            self.time_slider.blockSignals(True)
            self.time_slider.setValue(0)
            self.time_slider.blockSignals(False)
            
            self.plot_data()
            
        except Exception as e:
            self.is_loaded = False
            self.error_msg = f"MATLAB Error:\n{str(e)}\n{traceback.format_exc()}"
            self.channel_selector.setEnabled(False)
            self.time_slider.setEnabled(False)
            self.plot_empty_state()

    def on_combo_changed(self):
        self.plot_data()

    def plot_data(self, *args, **kwargs):
        if not self.is_loaded:
            return
            
        self._clear_axes()
        
        selected = self.channel_selector.currentText()
        if selected == "All Channels":
            indices = list(range(len(self.channel_names)))
        else:
            try:
                idx = list(self.channel_names).index(selected)
                indices = [idx]
            except ValueError:
                indices = [0]
        
        # Calculate time slice
        start_t = self.time_slider.value()
        end_t = start_t + 10
        self.time_slider_label.setText(f"{start_t}s - {end_t}s")
        
        mask = (self.time_axis >= start_t) & (self.time_axis <= end_t)
        t_ax_slice = self.time_axis[mask]
        
        # Time Domain Plot (SLICED)
        for ch_idx in indices:
            c = SIGNAL_COLORS[ch_idx % len(SIGNAL_COLORS)]
            self.time_ax.plot(t_ax_slice, self.time_data[ch_idx][mask], color=c, label=str(self.channel_names[ch_idx]), linewidth=1)
            
        self.time_ax.set_title("Time Domain", color='black', pad=10)
        self.time_ax.set_xlabel("Time (s)", color='black')
        self.time_ax.set_ylabel("Amplitude (µV)", color='black')
        self.time_ax.set_xlim([start_t, end_t])
        self.time_ax.grid(True, linestyle='--', color=FAINT_LINE, alpha=0.5)
        self.time_ax.tick_params(colors='black')
        for spine in self.time_ax.spines.values():
            spine.set_color(FAINT_LINE)
            spine.set_visible(True)
        if len(indices) > 1:
            self.time_ax.legend(loc='upper right', frameon=False, prop={'size': 9})
            
        # Frequency Domain Plot (FULL)
        for ch_idx in indices:
            c = SIGNAL_COLORS[ch_idx % len(SIGNAL_COLORS)]
            self.freq_ax.plot(self.freq_axis, self.freq_data[ch_idx], color=c, label=str(self.channel_names[ch_idx]), linewidth=1)
            
        self.freq_ax.set_title("Frequency Domain (PSD)", color='black', pad=10)
        self.freq_ax.set_xlabel("Frequency (Hz)", color='black')
        self.freq_ax.set_ylabel("Power (dB)", color='black')
        self.freq_ax.grid(True, linestyle='--', color=FAINT_LINE, alpha=0.5)
        self.freq_ax.tick_params(colors='black')
        for spine in self.freq_ax.spines.values():
            spine.set_color(FAINT_LINE)
            spine.set_visible(True)
        if len(indices) > 1:
            self.freq_ax.legend(loc='upper right', frameon=False, prop={'size': 9})
            
        self.time_domain_canvas.draw()
        self.freq_domain_canvas.draw()
