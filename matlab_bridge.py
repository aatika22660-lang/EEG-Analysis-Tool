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
