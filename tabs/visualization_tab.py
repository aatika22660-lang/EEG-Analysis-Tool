from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QSlider, QCheckBox, QSizePolicy, QPushButton, QStackedWidget,
                             QSplitter, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import io
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import traceback
import numpy as np
import mne
import re

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
        
        # Topoplot state
        self.show_topoplot = False
        self.topo_display_mode = "Mean Amplitude"
        self.matching_indices = []
        self.matched_pos = []
        self.matched_names = []
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title & Controls
        top_layout = QHBoxLayout()
        title = QLabel("Time and Frequency Domain Analysis")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {DUSTY_BLUE};")
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        # Unavailable Label (hidden by default)
        self.topo_unavailable_label = QLabel("Topoplot unavailable — no standard electrode names detected")
        self.topo_unavailable_label.setStyleSheet(f"color: {LIGHT_BLUE}; font-family: Georgia; font-style: italic; font-size: 13px;")
        self.topo_unavailable_label.setVisible(False)
        top_layout.addWidget(self.topo_unavailable_label)

        # Toggle Button
        self.topo_toggle_btn = QPushButton("Show Topoplot")
        self.topo_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PANEL_BG};
                color: {DUSTY_BLUE};
                border: 1px solid {FAINT_LINE};
                border-radius: 4px;
                padding: 4px 12px;
                font-family: Georgia;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BLUE};
                color: white;
            }}
        """)
        self.topo_toggle_btn.clicked.connect(self.toggle_view)
        self.topo_toggle_btn.setVisible(False)
        top_layout.addWidget(self.topo_toggle_btn)
        
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
        
        # Bottom Stacked Widget (PSD vs Topoplot)
        self.bottom_stack = QStackedWidget()
        
        # Freq Canvas (Index 0)
        self.freq_figure, self.freq_ax = plt.subplots(facecolor=CREAM)
        self.freq_figure.subplots_adjust(bottom=0.2, right=0.95, top=0.9, left=0.1)
        self.freq_domain_canvas = FigureCanvas(self.freq_figure)
        self.freq_domain_canvas.setStyleSheet("background-color: transparent;")
        self.freq_domain_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.bottom_stack.addWidget(self.freq_domain_canvas)
        
        # Topo Page (Index 1) - Redesigned with Pixmap
        topo_page = QWidget()
        topo_page_layout = QHBoxLayout(topo_page)
        topo_page_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Left Panel: Controls & Info (Fixed 220px) ---
        left_panel = QFrame()
        left_panel.setFixedWidth(220)
        left_panel.setStyleSheet(f"background-color: {PANEL_BG}; border-radius: 6px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # Heading 1
        topo_ctrl_lbl = QLabel("Topoplot Controls")
        topo_ctrl_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {DUSTY_BLUE};")
        left_layout.addWidget(topo_ctrl_lbl)
        
        # Divider utility
        def get_divider():
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet(f"color: {FAINT_LINE};")
            return line
            
        left_layout.addWidget(get_divider())
        
        # Time Window
        left_layout.addWidget(QLabel("Time Window:"))
        self.topo_time_slider = QSlider(Qt.Horizontal)
        self.topo_time_slider.valueChanged.connect(self.plot_topo)
        left_layout.addWidget(self.topo_time_slider)
        
        self.topo_time_label = QLabel("0s — 10s")
        self.topo_time_label.setStyleSheet(f"color: {TEXT_DARK}; font-family: Georgia; font-size: 13px;")
        self.topo_time_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.topo_time_label)
        
        # Preset row
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(5)
        btn_style = f"""
            QPushButton {{
                background-color: {CREAM};
                color: {TEXT_DARK};
                border: 1px solid {FAINT_LINE};
                border-radius: 4px;
                padding: 4px 5px;
                font-family: Georgia;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {LIGHT_BLUE};
                color: white;
            }}
        """
        for name in ["Start", "Middle", "End"]:
            btn = QPushButton(name)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda checked, n=name: self.jump_to_fixed_time(n))
            presets_layout.addWidget(btn)
        left_layout.addLayout(presets_layout)
        
        left_layout.addWidget(get_divider())
        
        # Signal Info
        sig_info_lbl = QLabel("Signal Info")
        sig_info_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {DUSTY_BLUE};")
        left_layout.addWidget(sig_info_lbl)
        
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)
        
        self.stat_gfp = QLabel("GFP: --")
        self.stat_most = QLabel("Most Active: --")
        self.stat_least = QLabel("Least Active: --")
        self.stat_window = QLabel("Window: --")
        
        for lbl in [self.stat_gfp, self.stat_most, self.stat_least, self.stat_window]:
            lbl.setStyleSheet(f"color: {TEXT_DARK}; font-family: Georgia; font-size: 13px;")
            stats_layout.addWidget(lbl)
            
        left_layout.addLayout(stats_layout)
        left_layout.addStretch()
        
        # --- Right Panel: Triple Topomap Grid ---
        right_panel = QWidget()
        right_layout = QHBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 10, 0)
        right_layout.setSpacing(20)
        
        # Mode Definitions for the grid
        self.topo_modes = ["Mean Amplitude", "Peak Amplitude", "Std Deviation"]
        
        # Store image labels in a dict for easy access or sequential updating
        self.topo_image_labels = {}
        
        for title_text in self.topo_modes:
            v_col = QVBoxLayout()
            v_col.setContentsMargins(0, 5, 0, 5)
            v_col.setSpacing(10)
            
            # Sub-heading style: 15px bold DUSTY_BLUE
            t_lbl = QLabel(title_text)
            t_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {DUSTY_BLUE};")
            t_lbl.setAlignment(Qt.AlignCenter)
            v_col.addWidget(t_lbl)
            
            img_lbl = QLabel()
            img_lbl.setAlignment(Qt.AlignCenter)
            img_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            img_lbl.setStyleSheet(f"color: {LIGHT_BLUE}; font-family: Georgia; font-size: 13px;")
            img_lbl.setText("Rendering...")
            
            v_col.addWidget(img_lbl)
            self.topo_image_labels[title_text] = img_lbl
            right_layout.addLayout(v_col)
        
        topo_page_layout.addWidget(left_panel)
        topo_page_layout.addWidget(right_panel)
        
        self.bottom_stack.addWidget(topo_page)
        
        layout.addWidget(self.bottom_stack)
        
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
        
        # Clear topo labels
        if hasattr(self, 'topo_image_labels'):
            for lbl in self.topo_image_labels.values():
                lbl.setText("Topoplot will appear here")
                lbl.setPixmap(QPixmap())
        
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
            
            # Setup sliders
            max_t = int(self.time_axis[-1]) if len(self.time_axis) > 0 else 0
            if max_t > 10:
                self.time_slider.setMaximum(max_t - 10)
                self.time_slider.setEnabled(True)
                self.topo_time_slider.setMaximum(max_t - 10)
                self.topo_time_slider.setEnabled(True)
            else:
                self.time_slider.setMaximum(0)
                self.time_slider.setEnabled(False)
                self.topo_time_slider.setMaximum(0)
                self.topo_time_slider.setEnabled(False)
                
            self.time_slider.blockSignals(True)
            self.time_slider.setValue(0)
            self.time_slider.blockSignals(False)
            self.topo_time_slider.blockSignals(True)
            self.topo_time_slider.setValue(0)
            self.topo_time_label.setText("0s — 10s")
            self.topo_time_slider.blockSignals(False)
            
            self.plot_data()
            
            # --- Topoplot Prep ---
            try:
                montage = mne.channels.make_standard_montage('standard_1020')
                montage_ch_names = [ch.upper() for ch in montage.ch_names]
                
                self.matching_indices = []
                self.matched_pos = []
                self.matched_names = []
                
                for i, ch_name in enumerate(self.channel_names):
                    # Clean: strip trailing dots, spaces, or special characters at the end
                    clean_name = re.sub(r'[^a-zA-Z0-9]+$', '', str(ch_name)).strip().upper()
                    
                    match_found = False
                    for m_name in montage.ch_names:
                        if m_name.upper() == clean_name:
                            self.matching_indices.append(i)
                            self.matched_pos.append(montage.get_positions()['ch_pos'][m_name])
                            # Use montage's capitalization for better topoplot labels
                            self.matched_names.append(m_name)
                            match_found = True
                            break
                
                # Convert positions to 2D
                self.matched_pos = np.array([p[:2] for p in self.matched_pos])
                
                if len(self.matching_indices) >= 3:
                    self.topo_toggle_btn.setVisible(True)
                    self.topo_unavailable_label.setVisible(False)
                    if self.show_topoplot:
                        self.plot_topo()
                else:
                    self.topo_toggle_btn.setVisible(False)
                    self.topo_unavailable_label.setVisible(True)
                    # Reset view to PSD if Topo is now unavailable
                    self.show_topoplot = False
                    self.bottom_stack.setCurrentIndex(0)
                    self.topo_toggle_btn.setText("Show Topoplot")
                    
            except Exception as e:
                print(f"Topoplot setup error: {e}")
                self.topo_toggle_btn.setVisible(False)
                self.topo_unavailable_label.setVisible(True)
            
        except Exception as e:
            self.is_loaded = False
            self.error_msg = f"MATLAB Error:\n{str(e)}\n{traceback.format_exc()}"
            self.channel_selector.setEnabled(False)
            self.time_slider.setEnabled(False)
            self.topo_toggle_btn.setVisible(False)
            self.topo_unavailable_label.setVisible(False)
            self.plot_empty_state()

    def on_combo_changed(self):
        self.plot_data()

    def jump_to_fixed_time(self, position):
        if not self.is_loaded:
            return
        
        max_val = self.topo_time_slider.maximum()
        if position == "Start":
            self.topo_time_slider.setValue(0)
        elif position == "Middle":
            self.topo_time_slider.setValue(max_val // 2)
        elif position == "End":
            self.topo_time_slider.setValue(max_val)

    def toggle_view(self):
        self.show_topoplot = not self.show_topoplot
        if self.show_topoplot:
            self.topo_toggle_btn.setText("Show PSD")
            self.bottom_stack.setCurrentIndex(1)
            # All controls are internal to the redesigned topo_page splitter
            self.plot_topo()
        else:
            self.topo_toggle_btn.setText("Show Topoplot")
            self.bottom_stack.setCurrentIndex(0)
            self.plot_data()

    def plot_topo(self):
        if not self.is_loaded or len(self.matching_indices) < 3:
            if self.is_loaded:
                for lbl in self.topo_image_labels.values():
                    lbl.setText("Topoplot unavailable — insufficient electrodes")
                    lbl.setPixmap(QPixmap()) # Clear any old pixmap
            return
            
        # Calculate time slice
        start_t = self.topo_time_slider.value()
        end_t = start_t + 10
        self.topo_time_label.setText(f"{start_t}s — {end_t}s")
        
        mask = (self.time_axis >= start_t) & (self.time_axis <= end_t)
        slice_data = self.time_data[self.matching_indices][:, mask]
        
        # Render all 3 modes sequentially
        for mode in self.topo_modes:
            if mode == "Peak Amplitude":
                data = np.max(np.abs(slice_data), axis=1)
            elif mode == "Std Deviation":
                data = np.std(slice_data, axis=1)
            else: # Mean Amplitude
                data = np.mean(slice_data, axis=1)
                # Update Signal Info Based on Mean Mode
                gfp_val = np.std(data)
                self.stat_gfp.setText(f"GFP: {gfp_val:.2f} µV")
                most_idx = np.argmax(data)
                least_idx = np.argmin(data)
                self.stat_most.setText(f"Most Active: {self.matched_names[most_idx]}")
                self.stat_least.setText(f"Least Active: {self.matched_names[least_idx]}")
                self.stat_window.setText(f"Window: {start_t}s to {end_t}s")
                
            try:
                # Fresh figure for each mode (3.5x3.5 as requested)
                fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor=CREAM)
                
                im, cm = mne.viz.plot_topomap(
                    data, 
                    self.matched_pos, 
                    axes=ax, 
                    show=False,
                    cmap='RdBu_r', 
                    sensors=True, 
                    names=None, # Remove internal labels to maximize plot size
                    vlim=(None, None)
                )
                
                # Colorbar
                cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.04)
                cb.ax.tick_params(labelsize=8, colors=TEXT_DARK)
                
                # Save to buffer
                buf = io.BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor=CREAM)
                buf.seek(0)
                
                # Load Pixmap
                pixmap = QPixmap()
                pixmap.loadFromData(buf.read())
                scaled_pixmap = pixmap.scaled(380, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.topo_image_labels[mode].setPixmap(scaled_pixmap)
                
                plt.close(fig)
                buf.close()
            except Exception as e:
                print(f"Render error ({mode}): {e}")
                self.topo_image_labels[mode].setText("Render Error")

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
