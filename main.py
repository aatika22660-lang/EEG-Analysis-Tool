import sys
import pandas as pd
import scipy.io as sio

from matlab_bridge import start_matlab
start_matlab()  # boots up MATLAB in background
# MNE is sometimes optional for basic python installs, handling gracefully if user hasn't installed
try:
    import mne
    MNE_AVALIABLE = True
except ImportError:
    MNE_AVALIABLE = False

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTabWidget, QToolBar, QAction, QFileDialog, 
                             QStatusBar, QMessageBox, QInputDialog, QStackedWidget)
from PyQt5.QtCore import Qt

from state import app_state
from theme import GLOBAL_STYLE
from landing_page import LandingPage

# Import Tabs
from tabs.visualization_tab import VisualizationTab
from tabs.wavelet_tab import WaveletDenoisingTab
from tabs.adaptive_tab import AdaptiveFilteringTab
from tabs.comparison_tab import ComparisonTab
from tabs.merging_tab import SignalMergingTab

class EEGApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive MATLAB-Based EEG Signal Analysis and Artifact Removal Tool")
        self.resize(1000, 700)
        self.setStyleSheet(GLOBAL_STYLE)
        
        self.init_ui()
        self.init_toolbar()
        
    def init_ui(self):
        # Main Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget: landing page (index 0) ↔ tabs (index 1)
        self.stack = QStackedWidget()
        
        # Landing Page
        self.landing = LandingPage()
        self.landing.on_load_clicked = self.load_signal
        self.stack.addWidget(self.landing)   # index 0
        
        # Tabs
        self.tabs = QTabWidget()
        self.vis_tab = VisualizationTab(app_state)
        self.wavelet_tab = WaveletDenoisingTab(app_state)
        self.adaptive_tab = AdaptiveFilteringTab(app_state)
        self.compare_tab = ComparisonTab(app_state)
        self.merge_tab = SignalMergingTab(app_state)
        
        self.tabs.addTab(self.vis_tab, "Visualization")
        self.tabs.addTab(self.wavelet_tab, "Wavelet Denoising")
        self.tabs.addTab(self.adaptive_tab, "Adaptive Filtering")
        self.tabs.addTab(self.compare_tab, "Comparison")
        self.tabs.addTab(self.merge_tab, "Signal Merging")
        
        self.stack.addWidget(self.tabs)      # index 1
        
        main_layout.addWidget(self.stack)
        
        # Status Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("No EEG file loaded.")
        
    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Load Button
        load_action = QAction("Load EEG File", self)
        load_action.triggered.connect(self.load_signal)
        toolbar.addAction(load_action)
        
        # Export Button
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
    def load_signal(self):
        """Signal Loading Module: Handle .edf, .mat, .csv"""
        file_filter = "EEG Data (*.edf *.mat *.csv)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Open EEG File", "", file_filter)
        
        if not file_path:
            return
            
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                app_state["raw_signal"] = df.values
                app_state["channel_names"] = list(df.columns)
                app_state["sampling_rate"] = 250  # Default assumption if CSV doesn't store FS
                
            elif file_path.endswith('.mat'):
                mat = sio.loadmat(file_path)
                
                # Attempt to find signal in common keys
                raw_signal = mat.get('val', mat.get('data', mat.get('signal', None)))
                
                # If not found, look for any 2D numeric array (ignoring metadata)
                if raw_signal is None:
                    for key, val in mat.items():
                        if not key.startswith('__') and hasattr(val, 'shape') and len(val.shape) == 2:
                            raw_signal = val
                            break
                            
                app_state["raw_signal"] = raw_signal
                
                # Handle sampling rate: check 'fs', 'sampling_rate', or default 250
                fs_val = mat.get('fs', mat.get('sampling_rate', [[250]]))
                if isinstance(fs_val, (int, float)):
                    app_state["sampling_rate"] = fs_val
                else:
                    try:
                        app_state["sampling_rate"] = float(np.array(fs_val).flatten()[0])
                    except:
                        app_state["sampling_rate"] = 250
                
                if app_state["raw_signal"] is not None:
                    # Determine channel count (smaller dimension typically)
                    # If 122880 x 16, then 16 is likely the channels
                    r, c = app_state["raw_signal"].shape
                    num_channels = min(r, c)
                    app_state["channel_names"] = [f"Ch{i+1}" for i in range(num_channels)]
                else:
                    raise Exception("No valid EEG signal array found in .mat file.")
                
            elif file_path.endswith('.edf'):
                if not MNE_AVALIABLE:
                    QMessageBox.warning(self, "Missing Library", "MNE library is required to read .edf files. Please pip install mne.")
                    return
                raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)
                app_state["raw_signal"] = raw.get_data()
                app_state["sampling_rate"] = raw.info['sfreq']
                app_state["channel_names"] = raw.ch_names
                
            # Update Status Bar
            filename = file_path.split("/")[-1]
            fs = app_state["sampling_rate"]
            self.statusBar.showMessage(f"Loaded: {filename} | Sampling Rate: {fs} Hz")
            
            # Switch from landing page to tabs view
            self.stack.setCurrentIndex(1)
            
            # TODO: partner - call update plots across all tabs here when data is loaded
            self.vis_tab.load_new_file()
            self.wavelet_tab.load_new_file()
            # other tabs still in prototype, but adding calls as they're implemented
            # self.adaptive_tab.load_new_file() 
            # self.compare_tab.load_new_file()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", f"Could not load {file_path}:\n{str(e)}")


    def export_data(self):
        """Export Module: Save Processed Signal or Current Plot"""
        options = ["Save Processed Signal (.csv)", "Save Current Plot (.png)"]
        choice, ok = QInputDialog.getItem(self, "Export", "Select Export Type:", options, 0, False)
        
        if not ok:
            return
            
        if "Plot" in choice:
            self.save_plot()
        elif "Signal" in choice:
            self.save_signal()
            
    def save_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "plot.png", "PNG Files (*.png)")
        if not file_path: return
            
        # Get active tab index to extract the plot dynamically
        idx = self.tabs.currentIndex()
        try:
            if idx == 0:
                self.vis_tab.time_figure.savefig(file_path)
            elif idx == 1:
                self.wavelet_tab.wavelet_figure.savefig(file_path)
            elif idx == 2:
                self.adaptive_tab.adaptive_figure.savefig(file_path)
            elif idx == 3:
                self.compare_tab.wavelet_compare_figure.savefig(file_path) # Just saving one for now
            elif idx == 4:
                self.merge_tab.merge_figure.savefig(file_path)
                
            QMessageBox.information(self, "Success", f"Plot saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save plot: {str(e)}")
            
    def save_signal(self):
        # Determine which signal to save if both exist
        sig_to_save = None
        
        if app_state["processed_wavelet"] is not None and app_state["processed_adaptive"] is not None:
            opts = ["Wavelet Processed", "Adaptive Processed"]
            choice, ok = QInputDialog.getItem(self, "Select Signal", "Both processing outputs exist. Which to save?", opts, 0, False)
            if not ok: return
            if "Wavelet" in choice:
                sig_to_save = app_state["processed_wavelet"]
            else:
                sig_to_save = app_state["processed_adaptive"]
                
        elif app_state["processed_wavelet"] is not None:
            sig_to_save = app_state["processed_wavelet"]
        elif app_state["processed_adaptive"] is not None:
            sig_to_save = app_state["processed_adaptive"]
        else:
            QMessageBox.warning(self, "No Data", "No processed signals found in state to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Signal", "processed_signal.csv", "CSV Files (*.csv)")
        if not file_path: return
        
        try:
            # Partner stores signal either transposed or not, basic saving fallback
            pd.DataFrame(sig_to_save).to_csv(file_path, index=False)
            QMessageBox.information(self, "Success", f"Signal saved to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save signal: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EEGApp()
    window.show()
    sys.exit(app.exec_())