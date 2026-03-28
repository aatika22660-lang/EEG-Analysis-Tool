# EEG Signal Analysis GUI

A modern, high-performance desktop application for processing and analyzing EEG (Electroencephalogram) signals. Built with Python and PyQt5, this tool provides a comprehensive suite of modules for signal visualization, artifact removal, and data management.

## 🌟 Features

- **Multi-Format Support**: Load and process EEG data from `.edf`, `.mat`, and `.csv` files.
- **Adaptive Filtering**: Implementation of adaptive filtering techniques for real-time or offline artifact rejection.
- **Wavelet Denoising**: Advanced wavelet-based noise reduction for cleaner signal extraction.
- **Comparison View**: Side-by-side comparison of original and processed signals to validate filtering efficacy.
- **Signal Merging**: Combine and manage different signal datasets seamlessly.
- **Interactive Visualization**: High-fidelity plotting with interactive zooming and channel selection.

## 📂 Project Structure

```bash
EEG_Signal_Analysis_GUI/
├── main.py              # Application entry point & core logic
├── state.py             # Global application state management
├── theme.py             # UI styling and visual configuration
├── walkthrough.md       # Detailed development walkthrough
├── tabs/                # Functional modules (tabs)
│   ├── adaptive_tab.py
│   ├── comparison_tab.py
│   ├── merging_tab.py
│   ├── visualization_tab.py
│   └── wavelet_tab.py
└── venv/                # Local Python virtual environment
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Virtual Environment (`venv`)

### Installation & Setup
1. **Activate the Environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run the Application**:
   ```bash
   python3 main.py
   ```

## 🛠️ Maintenance Note
This README is managed and updated automatically (via Antigravity AI) as new features, tabs, or logic are added to the codebase. 

---
**Last Updated**: March 29, 2026
