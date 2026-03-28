# EEG Signal Analysis GUI Walkthrough

## How to Run the Application
To run the EEG Signal Analysis GUI on your machine, launch the terminal in the project directory and run:
```bash
# 1. Activate the virtual environment
source venv/bin/activate

# 2. Run the main application script
python3 main.py
```
> [!NOTE]
> If you are outside the virtual environment, you can quickly run the app using `venv/bin/python3 main.py` directly from the project root.

## What was Accomplished
- **Environment Setup**: Validated and prepared the localized Python virtual environment (`venv`).
- **Dependencies Installed**: Outfitted the environment with required signal processing and UI libraries (`PyQt5`, `pandas`, `scipy`, `mne`, `matplotlib`).
- **Application Launched**: Executed `venv/bin/python3 main.py`, successfully instantiating the graphical user interface.

## Functionality Overview
The application is an interactive tool for artifact removal and signal processing. Based on the successful load of `main.py`, the following components are initialized and ready to use:

1. **Visualization**: Module for viewing loaded `.mat`, `.csv`, or `.edf` EEG signals.
2. **Wavelet Denoising**: Interface for Wavelet-based noise reduction techniques.
3. **Adaptive Filtering**: Interface for adaptive removal of physiological or hardware artifacts.
4. **Comparison**: Dedicated view to contrast original vs. denoised/filtered signals.
5. **Signal Merging**: Controls for combining dataset channels.

## Validation Results
- **Status**: **PASS** - Background process actively running.
- **Dependency Checking**: Verified no `ModuleNotFoundError` regressions; GUI loads cleanly.
- **Stability**: Tested smooth execution loop for the `QApplication`.

> [!TIP]
> You can now use the `Load EEG File` action in the Main Toolbar to process your EDF/MAT/CSV files directly within the running window.
