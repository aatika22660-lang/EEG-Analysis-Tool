# 🧠 EEG Signal Analysis GUI — Setup Guide

Welcome! Follow these steps to get the project running on your computer. Don't worry if you're not super technical — just go through each section in order.

---

## 1. Prerequisites

Before you start, make sure you have the following installed:

| Tool | Details |
|------|---------|
| **Python** | Version 3.8 or higher — [Download here](https://www.python.org/downloads/) |
| **MATLAB** | Already installed on university computers |
| **Git** | [Download here](https://git-scm.com/downloads) |

> 💡 **Tip:** To check if Python is installed, open a terminal and type `python --version` or `python3 --version`.

---

## 2. Clone the Repository

Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/aatika22660-lang/EEG-Analysis-Tool.git
cd EEG-Analysis-Tool
```

This will download the project to your computer and move you into the project folder.

---

## 3. Set Up Virtual Environment

A virtual environment keeps the project's dependencies separate from your system. Choose the instructions for **your operating system**:

### 🪟 Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 🍎 Mac / 🐧 Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

> ✅ You'll know it worked if you see `(venv)` at the beginning of your terminal line.

---

## 4. Install Dependencies

With your virtual environment activated, run:

```bash
pip install -r requirements.txt
```

This installs all the Python packages the project needs.

---

## 5. Install MATLAB Engine for Python

This step connects Python to MATLAB so the app can call MATLAB functions.

### Steps:

1. **Find your MATLAB installation folder.** Open MATLAB and type the following in the MATLAB **Command Window**:

   ```matlab
   matlabroot
   ```

   It will print something like:
   - **Windows:** `C:\Program Files\MATLAB\R2023b`
   - **Mac:** `/Applications/MATLAB_R2023b.app`

2. **Navigate to the MATLAB engine folder** in your terminal:

   **Windows:**
   ```bash
   cd "C:\Program Files\MATLAB\R2023b\extern\engines\python"
   ```

   **Mac/Linux:**
   ```bash
   cd /Applications/MATLAB_R2023b.app/extern/engines/python
   ```

   > ⚠️ Replace the path above with whatever `matlabroot` gave you.

3. **Install the engine:**

   ```bash
   python setup.py install
   ```

---

## 6. Run the App

Make sure you're back in the project folder and your virtual environment is activated, then run:

```bash
python main.py
```

The GUI window should open and you're good to go! 🎉

---

## 7. For My Partner (Important!)

Hey! 👋 Here's what you need to know about the project structure:

- ✅ All MATLAB processing functions go inside the **`matlab_functions/`** folder
- ✅ Each `.m` file already exists as a placeholder — just **add your code inside them**
- 🚫 **Do NOT touch any files outside of `matlab_functions/`**
- 📣 Once a function is ready, **tell me (Aatika)** so I can wire it up to the GUI

### MATLAB files you'll be working with:

| File | Purpose |
|------|---------|
| `matlab_functions/wavelet_denoise.m` | Wavelet denoising function |
| `matlab_functions/adaptive_filter.m` | Adaptive filtering function |
| `matlab_functions/compare_methods.m` | Method comparison function |
| `matlab_functions/merge_channels.m` | Channel merging function |

---

## 8. Common Issues & Troubleshooting

### ❌ `matlab.engine` import fails
**Cause:** MATLAB Engine for Python is not installed.
**Fix:** Go back to **Section 5** and follow the steps again.

### ❌ The GUI doesn't open
**Cause:** Virtual environment is not activated.
**Fix:** Make sure you see `(venv)` in your terminal. If not, re-run the activation command from **Section 3**.

### ❌ `mne` gives an error
**Cause:** The `mne` package didn't install correctly.
**Fix:** Run this manually:

```bash
pip install mne
```

---

## Need Help?

If something isn't working, reach out to **Aatika** before making changes to any files outside of `matlab_functions/`.

Happy coding! 🚀
