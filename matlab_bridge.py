import matlab.engine
import numpy as np
import os

eng = None

def start_matlab():
    global eng
    eng = matlab.engine.start_matlab()

def get_engine():
    return eng

def run_visualize(signal, sampling_rate, channel_names):
    if eng is None:
        raise Exception("MATLAB Engine is not running. Please restart the application and wait for MATLAB to initialize or check your MATLAB installation.")
        
    sig_py = np.array(signal)
    if sig_py.ndim == 1:
        sig_py = sig_py.reshape(1, -1)
        
    func_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matlab_functions')
    eng.addpath(func_dir, nargout=0)
    
    sig_ml = matlab.double(sig_py.tolist())
    fs_ml = float(sampling_rate)
    
    time_data, freq_data, freq_axis, time_axis, c_names = eng.visualize(sig_ml, fs_ml, channel_names, nargout=5)
    
    t_dt = np.array(time_data)
    f_dt = np.array(freq_data)
    f_ax = np.array(freq_axis).flatten()
    t_ax = np.array(time_axis).flatten()
    
    
    return t_dt, f_dt, f_ax, t_ax, c_names

def run_wavelet_denoise(signal, wavelet_name, decomp_level, threshold_method):
    if eng is None:
        raise Exception("MATLAB Engine is not running. Please restart the application and wait for MATLAB to initialize or check your MATLAB installation.")
        
    sig_py = np.array(signal)
    if sig_py.ndim == 1:
        sig_py = sig_py.reshape(1, -1)
        
    func_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matlab_functions')
    eng.addpath(func_dir, nargout=0)
    
    # Convert inputs to MATLAB types
    sig_ml = matlab.double(sig_py.tolist())
    wn_ml = str(wavelet_name)
    dl_ml = float(decomp_level)
    tm_ml = str(threshold_method)
    
    # Call wavelet_denoise.m with nargout=6
    res = eng.wavelet_denoise(sig_ml, wn_ml, dl_ml, tm_ml, nargout=6)
    
    # Safe extraction from the result list
    denoised_sig = res[0]
    snr = res[1]
    mse = res[2]
    corr = res[3]
    raw_stats = res[4]
    denoised_stats = res[5]
    
    # Convert MATLAB results back to Python/NumPy types
    return (np.array(denoised_sig), 
            float(np.array(snr).flatten()[0]), 
            float(np.array(mse).flatten()[0]), 
            float(np.array(corr).flatten()[0]),
            dict(raw_stats),
            dict(denoised_stats))

def find_best_wavelet_params(signal, progress_callback=None):
    if eng is None:
        raise Exception("MATLAB Engine is not running.")
        
    wavelets = ['db1', 'db2', 'db4', 'db8', 'sym4', 'sym8', 'coif1', 'coif3']
    levels = [2, 3, 4, 5, 6]
    methods = ['soft', 'hard']
    
    results = []
    best_snr = -float('inf')
    best_params = (None, None, None, None)
    
    total = len(wavelets) * len(levels) * len(methods)
    count = 0
    
    for w in wavelets:
        for l in levels:
            for m in methods:
                count += 1
                if progress_callback:
                    progress_callback(f"Testing {w} / level {l} / {m} ({count}/{total})...")
                
                try:
                    # Reuse existing bridge call
                    _, snr, mse, corr, _, _ = run_wavelet_denoise(signal, w, l, m)
                    
                    res = {
                        "wavelet": w,
                        "level": l,
                        "method": m,
                        "snr": snr,
                        "mse": mse,
                        "corr": corr
                    }
                    results.append(res)
                    
                    if snr > best_snr:
                        best_snr = snr
                        best_params = (w, l, m, snr)
                except Exception:
                    # Skip failed combinations
                    continue
    
    # Sort by SNR descending
    results.sort(key=lambda x: x['snr'], reverse=True)
    
    return best_params[0], best_params[1], best_params[2], best_params[3], results
