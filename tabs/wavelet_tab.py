from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QFrame, 
                             QComboBox, QSlider, QPushButton, QSizePolicy, QSpacerItem, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import traceback

from theme import CREAM, DUSTY_BLUE, PANEL_BG, LIGHT_BLUE, TEXT_DARK, FAINT_LINE, SIGNAL_COLORS
from matlab_bridge import run_wavelet_denoise, find_best_wavelet_params

class ParamSearchThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(tuple)
    
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        
    def run(self):
        try:
            start_time = time.time()
            # The bridge function accepts a callback for real-time progress
            best_w, best_l, best_m, best_snr, all_results = find_best_wavelet_params(
                self.signal, 
                progress_callback=self.progress.emit
            )
            duration = time.time() - start_time
            self.finished.emit((best_w, best_l, best_m, best_snr, all_results, duration))
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit((None, None, None, None, None, 0))

class WaveletDenoisingTab(QWidget):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.denoised_data = None
        self.metrics = None # (snr, mse, corr)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left Sidebar (fixed width with ScrollArea)
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setFixedWidth(220)
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFrameShape(QFrame.NoFrame)
        sidebar_scroll.setStyleSheet(f"background-color: {PANEL_BG}; border-right: 1px solid {FAINT_LINE};")
        
        sidebar_content = QFrame()
        sidebar_content.setStyleSheet(f"""
            QFrame {{ 
                background-color: {PANEL_BG}; 
                border: none;
            }}
            QLabel {{ 
                color: {TEXT_DARK}; 
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
                font-size: 12px; 
            }}
            QComboBox {{
                background-color: {CREAM};
                color: {TEXT_DARK};
                border: 1px solid {FAINT_LINE};
                border-radius: 4px;
                padding: 3px;
                font-size: 12px;
                margin-bottom: 5px;
            }}
            QPushButton {{
                background-color: transparent;
                color: {DUSTY_BLUE};
                border: 1px solid {DUSTY_BLUE};
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
                height: 30px;
            }}
            QPushButton:hover {{
                background-color: {DUSTY_BLUE};
                color: white;
            }}
        """)
        
        sidebar_layout = QVBoxLayout(sidebar_content)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(6)
        
        # 1. Parameters Section
        sidebar_layout.addLayout(self._create_section_heading("Parameters"))
        
        # Wavelet Family
        sidebar_layout.addWidget(QLabel("Wavelet Family:"))
        self.wavelet_combo = QComboBox()
        self.wavelet_combo.addItems(["db1", "db2", "db4", "db8", "sym4", "sym8", "coif1", "coif3"])
        self.wavelet_combo.setCurrentText("db4")
        sidebar_layout.addWidget(self.wavelet_combo)
        
        # Decomposition Level
        sidebar_layout.addWidget(QLabel("Decomposition Level:"))
        level_top_layout = QHBoxLayout()
        self.level_slider = QSlider(Qt.Horizontal)
        self.level_slider.setRange(1, 8)
        self.level_slider.setValue(4)
        self.level_label = QLabel("4")
        self.level_slider.valueChanged.connect(lambda v: self.level_label.setText(str(v)))
        level_top_layout.addWidget(self.level_slider)
        level_top_layout.addWidget(self.level_label)
        sidebar_layout.addLayout(level_top_layout)
        
        # Threshold Method
        sidebar_layout.addWidget(QLabel("Threshold Method:"))
        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems(["soft", "hard"])
        sidebar_layout.addWidget(self.threshold_combo)
        
        # Run Button
        self.run_btn = QPushButton("Run Denoising")
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.clicked.connect(self.run_denoising)
        sidebar_layout.addWidget(self.run_btn)
        
        # Metrics Display Area
        self.metrics_container = QFrame()
        self.metrics_container.setContentsMargins(0, 4, 0, 0)
        metrics_layout = QVBoxLayout(self.metrics_container)
        metrics_layout.setSpacing(4)
        
        self.snr_label = QLabel("SNR: -- dB")
        self.mse_label = QLabel("MSE: --")
        self.corr_label = QLabel("Correlation: --")
        
        for lbl in [self.snr_label, self.mse_label, self.corr_label]:
            metrics_layout.addWidget(lbl)
        
        self.metrics_container.setVisible(False)
        sidebar_layout.addWidget(self.metrics_container)
        
        # 2. Statistics Section
        sidebar_layout.addWidget(self._create_divider())
        sidebar_layout.addLayout(self._create_section_heading("Signal Statistics"))
        
        self.stats_container = QWidget()
        stats_main_layout = QVBoxLayout(self.stats_container)
        stats_main_layout.setContentsMargins(0, 4, 0, 0)
        stats_main_layout.setSpacing(4)
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(4)
        stats_grid.setContentsMargins(0, 0, 0, 0)
        
        # Headers
        h_raw = QLabel("Raw")
        h_den = QLabel("Denoised")
        for h in [h_raw, h_den]:
            h.setStyleSheet("font-weight: bold; text-decoration: underline;")
            h.setAlignment(Qt.AlignCenter)
        
        stats_grid.addWidget(h_raw, 0, 1)
        stats_grid.addWidget(h_den, 0, 2)
        
        self.stat_labels = {}
        metrics_names = ["Min", "Max", "Mean", "Std", "RMS"]
        
        for i, name in enumerate(metrics_names):
            label = QLabel(f"{name}:")
            stats_grid.addWidget(label, i + 1, 0)
            
            self.stat_labels[f"raw_{name.lower()}"] = QLabel("--")
            self.stat_labels[f"den_{name.lower()}"] = QLabel("--")
            
            self.stat_labels[f"raw_{name.lower()}"].setAlignment(Qt.AlignCenter)
            self.stat_labels[f"den_{name.lower()}"].setAlignment(Qt.AlignCenter)
            
            stats_grid.addWidget(self.stat_labels[f"raw_{name.lower()}"], i + 1, 1)
            stats_grid.addWidget(self.stat_labels[f"den_{name.lower()}"], i + 1, 2)
            
        stats_main_layout.addLayout(stats_grid)
        self.stats_container.setVisible(False)
        sidebar_layout.addWidget(self.stats_container)
        
        # 3. Best Parameters Section
        sidebar_layout.addWidget(self._create_divider())
        sidebar_layout.addLayout(self._create_section_heading("Best Parameters"))
        
        self.find_best_btn = QPushButton("Find Best Parameters")
        self.find_best_btn.setCursor(Qt.PointingHandCursor)
        self.find_best_btn.clicked.connect(self.start_param_search)
        sidebar_layout.addWidget(self.find_best_btn)
        
        self.search_progress = QLabel("")
        self.search_progress.setStyleSheet(f"color: {LIGHT_BLUE}; font-size: 11px; font-style: italic;")
        self.search_progress.setWordWrap(True)
        sidebar_layout.addWidget(self.search_progress)
        
        self.best_results_container = QWidget()
        best_layout = QVBoxLayout(self.best_results_container)
        best_layout.setContentsMargins(0, 4, 0, 0)
        best_layout.setSpacing(4)
        
        self.best_grid = QGridLayout()
        self.best_grid.setSpacing(4)
        
        self.best_labels = {}
        for i, name in enumerate(["Wavelet", "Level", "Method", "SNR"]):
            self.best_grid.addWidget(QLabel(f"{name}:"), i, 0)
            self.best_labels[name.lower()] = QLabel("--")
            self.best_grid.addWidget(self.best_labels[name.lower()], i, 1)
            
        best_layout.addLayout(self.best_grid)
        
        self.apply_best_btn = QPushButton("Apply Optimal Settings")
        self.apply_best_btn.setCursor(Qt.PointingHandCursor)
        self.apply_best_btn.clicked.connect(self.apply_best_params)
        best_layout.addWidget(self.apply_best_btn)
        
        self.best_results_container.setVisible(False)
        sidebar_layout.addWidget(self.best_results_container)
        
        sidebar_layout.addStretch()
        
        sidebar_scroll.setWidget(sidebar_content)
        main_layout.addWidget(sidebar_scroll)
        
        # Right Main Area - 2x2 Grid
        content_layout = QVBoxLayout()
        
        # Top Controller: Channel Selector
        top_ctrl_layout = QHBoxLayout()
        top_ctrl_layout.addWidget(QLabel("Channel Selection:"))
        self.channel_selector = QComboBox()
        self.channel_selector.addItem("All Channels")
        self.channel_selector.setFixedWidth(200)
        self.channel_selector.currentIndexChanged.connect(self.update_plots)
        top_ctrl_layout.addWidget(self.channel_selector)
        
        # View Toggle Button (Heatmap vs Signals)
        self.view_toggle_btn = QPushButton("Show Heatmap")
        self.view_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {DUSTY_BLUE};
                font-size: 13px;
                font-weight: bold;
                text-decoration: none;
                padding: 0px;
            }}
            QPushButton:hover {{
                color: {LIGHT_BLUE};
            }}
        """)
        self.view_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.view_toggle_btn.setVisible(False)
        self.view_toggle_btn.clicked.connect(self.toggle_view)
        top_ctrl_layout.addWidget(self.view_toggle_btn)
        
        top_ctrl_layout.addStretch()
        content_layout.addLayout(top_ctrl_layout)
        
        # 1. Signal View (2x2 Grid)
        self.signal_view_widget = QWidget()
        grid_layout = QGridLayout(self.signal_view_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(10)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(0, 1)
        grid_layout.setRowStretch(1, 1)
        
        # 1. Raw Time (Top Left)
        self.raw_fig, self.raw_ax = plt.subplots(figsize=(5, 4), facecolor=CREAM)
        self.raw_canvas = FigureCanvas(self.raw_fig)
        self.raw_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(self.raw_canvas, 0, 0)
        
        # 2. Raw Spectrogram (Top Right)
        self.raw_spec_fig, self.raw_spec_ax = plt.subplots(figsize=(5, 4), facecolor=CREAM)
        self.raw_spec_canvas = FigureCanvas(self.raw_spec_fig)
        self.raw_spec_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(self.raw_spec_canvas, 0, 1)
        
        # 3. Denoised Time (Bottom Left)
        self.denoised_fig, self.denoised_ax = plt.subplots(figsize=(5, 4), facecolor=CREAM)
        self.denoised_canvas = FigureCanvas(self.denoised_fig)
        self.denoised_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(self.denoised_canvas, 1, 0)
        
        # 4. Denoised Spectrogram (Bottom Right)
        self.denoised_spec_fig, self.denoised_spec_ax = plt.subplots(figsize=(5, 4), facecolor=CREAM)
        self.denoised_spec_canvas = FigureCanvas(self.denoised_spec_fig)
        self.denoised_spec_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid_layout.addWidget(self.denoised_spec_canvas, 1, 1)

        # Initialize colorbars once with placeholder space
        for fig, ax, attr in [(self.raw_spec_fig, self.raw_spec_ax, 'raw_cbar'), 
                              (self.denoised_spec_fig, self.denoised_spec_ax, 'denoised_cbar')]:
            fig.subplots_adjust(right=0.85, left=0.15, bottom=0.2, top=0.85)
            # Create a dummy mappable to initialize colorbar
            sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=-100, vmax=0))
            cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04, shrink=0.8)
            cbar.set_label('Power (dB)', color='black')
            cbar.ax.yaxis.set_tick_params(color='black', labelcolor='black')
            setattr(self, attr, cbar)
        
        content_layout.addWidget(self.signal_view_widget)
        
        # 2. Heatmap View (Initially Hidden)
        self.heatmap_fig, self.heatmap_axs = plt.subplots(1, 2, figsize=(10, 5), facecolor=CREAM)
        self.heatmap_canvas = FigureCanvas(self.heatmap_fig)
        self.heatmap_canvas.setVisible(False)
        content_layout.addWidget(self.heatmap_canvas)
        
        content_layout.setStretch(1, 1) # Give the views all the remaining space in QVBoxLayout
        
        main_layout.addLayout(content_layout)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #D9534F; font-size: 11px;")
        self.error_label.setWordWrap(True)
        sidebar_layout.addWidget(self.error_label)

        # Initial plot update
        self.update_plots()

    def load_new_file(self):
        """Called by main.py when a new file is loaded"""
        self.denoised_data = None
        self.metrics = None
        self.best_results_container.setVisible(False)
        self.view_toggle_btn.setVisible(False)
        self.view_toggle_btn.setText("Show Heatmap")
        self.signal_view_widget.setVisible(True)
        self.heatmap_canvas.setVisible(False)
        self.search_progress.setText("")
        self.error_label.setText("")
        
        # Reset stat labels
        for label in self.stat_labels.values():
            label.setText("--")
        
        # Update channel selector
        self.channel_selector.blockSignals(True)
        self.channel_selector.clear()
        self.channel_selector.addItem("All Channels")
        if self.app_state["channel_names"]:
            for ch in self.app_state["channel_names"]:
                self.channel_selector.addItem(str(ch))
        self.channel_selector.blockSignals(False)
        
        self.update_plots()

    def run_denoising(self):
        if self.app_state["raw_signal"] is None:
            return
            
        try:
            self.run_btn.setEnabled(False)
            self.run_btn.setText("Processing...")
            self.error_label.setText("")
            
            wavelet = self.wavelet_combo.currentText()
            level = self.level_slider.value()
            method = self.threshold_combo.currentText()
            
            # Call bridge
            signal = np.asanyarray(self.app_state["raw_signal"])
            if signal.ndim == 2 and signal.shape[0] > signal.shape[1]:
                signal = signal.T  # transpose to channels × samples

            denoised, snr, mse, corr, raw_stats, den_stats = run_wavelet_denoise(
                signal,
                wavelet,
                level,
                method
            )
            
            self.denoised_data = denoised
            self.metrics = (snr, mse, corr)
            
            # Update metrics display
            self.snr_label.setText(f"SNR: {snr:.2f} dB")
            self.mse_label.setText(f"MSE: {mse:.4f}")
            self.corr_label.setText(f"Correlation: {corr:.4f}")
            self.metrics_container.setVisible(True)
            
            # Update statistics display
            for key in ["min", "max", "mean", "std", "rms"]:
                self.stat_labels[f"raw_{key}"].setText(f"{raw_stats[key]:.4f}")
                self.stat_labels[f"den_{key}"].setText(f"{den_stats[key]:.4f}")
            self.stats_container.setVisible(True)
            
            # Save to app_state for other tabs (e.g. Comparison Tab)
            # TODO: comparison tab reads from app_state["processed_wavelet"]
            self.app_state["processed_wavelet"] = denoised
            
            self.update_plots()
            
        except Exception as e:
            self.error_label.setText(f"MATLAB Error: {str(e)}")
            print(traceback.format_exc())
        finally:
            self.run_btn.setEnabled(True)
            self.run_btn.setText("Run Denoising")

    def start_param_search(self):
        if self.app_state["raw_signal"] is None:
            return
            
        if hasattr(self, 'search_thread') and self.search_thread.isRunning():
            return
            
        self.find_best_btn.setEnabled(False)
        self.run_btn.setEnabled(False)
        self.search_progress.setText("Searching... this may take a minute")
        self.best_results_container.setVisible(False)
        
        # Prepare signal
        signal = np.asanyarray(self.app_state["raw_signal"])
        if signal.ndim == 2 and signal.shape[0] > signal.shape[1]:
            signal = signal.T
            
        self.search_thread = ParamSearchThread(signal)
        self.search_thread.progress.connect(self.on_search_progress)
        self.search_thread.finished.connect(self.on_search_finished)
        self.search_thread.start()
        
    def on_search_progress(self, msg):
        self.search_progress.setText(msg)
        
    def on_search_finished(self, result):
        self.find_best_btn.setEnabled(True)
        self.run_btn.setEnabled(True)
        
        best_w, best_l, best_m, best_snr, all_results, duration = result
        
        if best_w:
            self.search_progress.setText(f"Completed in {duration:.1f}s")
            self.best_labels["wavelet"].setText(best_w)
            self.best_labels["level"].setText(str(best_l))
            self.best_labels["method"].setText(best_m)
            self.best_labels["snr"].setText(f"{best_snr:.2f} dB")
            self.best_results_container.setVisible(True)
            self.view_toggle_btn.setVisible(True) # Show the heatmap toggle
            
            # Save for apply and plotting
            self.best_params_found = (best_w, best_l, best_m)
            self.search_results = all_results
            
            # Auto-plot heatmap (ready in background)
            self._plot_snr_heatmap()
        else:
            self.search_progress.setText("Search failed. Check logs.")

    def toggle_view(self):
        if self.signal_view_widget.isVisible():
            self.signal_view_widget.setVisible(False)
            self.heatmap_canvas.setVisible(True)
            self.view_toggle_btn.setText("Show Signals")
        else:
            self.signal_view_widget.setVisible(True)
            self.heatmap_canvas.setVisible(False)
            self.view_toggle_btn.setText("Show Heatmap")

    def _plot_snr_heatmap(self):
        if not hasattr(self, 'search_results'):
            return
            
        wavelets = ['db1', 'db2', 'db4', 'db8', 'sym4', 'sym8', 'coif1', 'coif3']
        levels = [2, 3, 4, 5, 6]
        methods = ['soft', 'hard']
        
        # Prepare matrices
        snr_mats = {m: np.zeros((len(levels), len(wavelets))) for m in methods}
        
        # Best overall result for the star
        max_snr = -float('inf')
        max_pos = (None, None, None) # (method, level_idx, wavelet_idx)
        
        for res in self.search_results:
            m = res['method']
            l_idx = levels.index(res['level'])
            w_idx = wavelets.index(res['wavelet'])
            snr = res['snr']
            snr_mats[m][l_idx, w_idx] = snr
            
            if snr > max_snr:
                max_snr = snr
                max_pos = (m, l_idx, w_idx)
        
        self.heatmap_fig.clear()
        self.heatmap_fig.set_facecolor(CREAM)
        self.heatmap_fig.suptitle("SNR Performance Heatmap — Wavelet Parameter Search", 
                                 fontsize=15, fontweight='bold', color=DUSTY_BLUE)
        
        global_min = min(r['snr'] for r in self.search_results)
        global_max = max_snr
        midpoint = (global_min + global_max) / 2
        
        for i, m in enumerate(methods):
            ax = self.heatmap_fig.add_subplot(1, 2, i + 1)
            im = ax.imshow(snr_mats[m], cmap='YlOrRd', aspect='auto', 
                          vmin=global_min, vmax=global_max)
            
            ax.set_title(f"{m.capitalize()} Thresholding", color=TEXT_DARK, pad=10)
            ax.set_xticks(np.arange(len(wavelets)))
            ax.set_xticklabels(wavelets, color=TEXT_DARK, fontsize=10)
            ax.set_yticks(np.arange(len(levels)))
            ax.set_yticklabels([f"Lv {l}" for l in levels], color=TEXT_DARK, fontsize=10)
            
            # Cell text annotations
            for l in range(len(levels)):
                for w in range(len(wavelets)):
                    val = snr_mats[m][l, w]
                    # Dynamic text color (white for darker backgrounds)
                    txt_color = "white" if val > midpoint else TEXT_DARK
                    
                    text_str = f"{val:.1f}"
                    # Add star if it is the best overall
                    if max_pos == (m, l, w):
                        text_str += " ★"
                        
                    ax.text(w, l, text_str, ha="center", va="center", 
                            color=txt_color, fontweight='bold', fontsize=9)
            
            # Visual polish
            ax.set_facecolor(CREAM)
            for spine in ax.spines.values():
                spine.set_color(FAINT_LINE)
        
        # Add colorbar on the right
        self.heatmap_fig.subplots_adjust(bottom=0.2, right=0.85, top=0.85, wspace=0.3)
        cax = self.heatmap_fig.add_axes([0.88, 0.2, 0.02, 0.65])
        cbar = self.heatmap_fig.colorbar(im, cax=cax)
        cbar.set_label("SNR (dB)", color=TEXT_DARK, fontsize=11)
        cbar.ax.yaxis.set_tick_params(colors=TEXT_DARK)
        
        self.heatmap_canvas.draw()

    def _create_section_heading(self, text):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 4)
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {DUSTY_BLUE};")
        layout.addWidget(lbl)
        return layout

    def _create_divider(self):
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Plain)
        divider.setStyleSheet(f"background-color: {FAINT_LINE}; margin: 6px 0;")
        divider.setFixedHeight(1)
        return divider

    def apply_best_params(self):
        if not hasattr(self, 'best_params_found'):
            return
            
        w, l, m = self.best_params_found
        
        # Update UI components
        self.wavelet_combo.setCurrentText(w)
        self.level_slider.setValue(l)
        self.level_label.setText(str(l))
        self.threshold_combo.setCurrentText(m)
        
        # Run denoising
        self.run_denoising()

    def update_plots(self):
        self._clear_axes()
        
        # 1. Check if data is loaded
        if self.app_state["raw_signal"] is None:
            self._show_msg(self.raw_ax, "Load an EEG file to begin")
            self._show_msg(self.denoised_ax, "Load an EEG file to begin")
        else:
            # File is loaded
            start_t, end_t = self._get_time_window()
            t_axis = self.app_state["time_axis"]
            
            # Slicing
            mask = (t_axis >= start_t) & (t_axis <= end_t)
            t_slice = t_axis[mask]

            # In PyQt, set x-axis limits like visualization tab
            self.raw_ax.set_xlim([start_t, end_t])
            self.denoised_ax.set_xlim([start_t, end_t])
            
            selected_ch = self.channel_selector.currentIndex() # 0 is "All", 1+ are channels
            
            # Plot Raw
            self._plot_signal(self.raw_ax, self.app_state["raw_signal"], t_slice, mask, selected_ch, "Raw Signal")
            
            # Spectrogram logic: If All Channels, use first channel (index 0)
            spec_ch = 0 if selected_ch == 0 else selected_ch - 1
            fs = self.app_state["sampling_rate"]
            self._plot_spectrogram(self.raw_spec_ax, self.raw_spec_fig, self.app_state["raw_signal"], spec_ch, mask, fs, "Raw Spectrogram")
            
            # Plot Denoised or Empty
            if self.denoised_data is None:
                self._show_msg(self.denoised_ax, "Run denoising to see results")
                self._show_msg(self.denoised_spec_ax, "Run denoising to see results")
            else:
                self._plot_signal(self.denoised_ax, self.denoised_data, t_slice, mask, selected_ch, "Denoised Signal")
                self._plot_spectrogram(self.denoised_spec_ax, self.denoised_spec_fig, self.denoised_data, spec_ch, mask, fs, "Denoised Spectrogram")

        self.raw_canvas.draw()
        self.raw_spec_canvas.draw()
        self.denoised_canvas.draw()
        self.denoised_spec_canvas.draw()

    def _get_time_window(self):
        """Uses slider position from VisualizationTab in window structure if available"""
        try:
            # Direct access to visualization tab slider via the parent EEGApp window
            main_window = self.window()
            if hasattr(main_window, 'vis_tab'):
                start_t = main_window.vis_tab.time_slider.value()
                return start_t, start_t + 10
        except:
            pass
        return 0, 10

    def _plot_signal(self, ax, data, t_axis, mask, selected_idx, title):
        data = np.asanyarray(data)
        if data.ndim == 2 and data.shape[0] > data.shape[1]:
            data = data.T  # transpose to channels × samples

        ax.set_title(title, color='black', pad=10)
        ax.set_facecolor(CREAM)
        
        ch_names = self.app_state["channel_names"]
        
        if selected_idx == 0: # All channels
            for i in range(data.shape[0]):
                color = SIGNAL_COLORS[i % len(SIGNAL_COLORS)]
                ax.plot(t_axis, data[i, mask], color=color, linewidth=0.8, alpha=0.8, label=ch_names[i])
            if data.shape[0] < 10: # Only show legend if not too many
                ax.legend(loc='upper right', frameon=False, fontsize=8)
        else:
            idx = selected_idx - 1
            color = SIGNAL_COLORS[idx % len(SIGNAL_COLORS)]
            ax.plot(t_axis, data[idx, mask], color=color, linewidth=1.0, label=ch_names[idx])
            ax.legend(loc='upper right', frameon=False, fontsize=8)

        ax.set_xlabel("Time (s)", color='black')
        ax.set_ylabel("Amplitude (µV)", color='black')
        ax.grid(True, linestyle='--', color=FAINT_LINE, alpha=0.5)
        ax.tick_params(colors='black')
        for spine in ax.spines.values():
            spine.set_color(FAINT_LINE)

    def _plot_spectrogram(self, ax, fig, data, ch_idx, mask, fs, title):
        data = np.asanyarray(data)
        if data.ndim == 2 and data.shape[0] > data.shape[1]:
            data = data.T
            
        signal = data[ch_idx, mask]
        
        # Clear colorbars before redraw if they exist
        try:
            if hasattr(ax, 'cb') and ax.cb is not None:
                ax.cb.remove()
                ax.cb = None
        except Exception:
            pass
        
        # Spectrum logic
        spectrum, freqs, t_bins, im = ax.specgram(signal, Fs=fs, cmap='viridis', NFFT=256, noverlap=128)
        
        ax.set_title(title, color='black', pad=10)
        ax.set_ylim([0, 50])
        ax.set_xlabel("Time (s)", color='black')
        ax.set_ylabel("Frequency (Hz)", color='black')
        ax.tick_params(colors='black')
        
        for spine in ax.spines.values():
            spine.set_color(FAINT_LINE)
            
        # Update existing colorbar data instead of recreating
        cbar = self.raw_cbar if ax == self.raw_spec_ax else self.denoised_cbar
        cbar.update_normal(im)

    def _show_msg(self, ax, msg):
        ax.text(0.5, 0.5, msg, ha='center', va='center', fontsize=12, color=LIGHT_BLUE, 
                transform=ax.transAxes, alpha=0.7)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    def _clear_axes(self):
        for ax in [self.raw_ax, self.raw_spec_ax, self.denoised_ax, self.denoised_spec_ax]:
            ax.clear()
            ax.set_facecolor(CREAM)
            for spine in ax.spines.values():
                spine.set_visible(True)
