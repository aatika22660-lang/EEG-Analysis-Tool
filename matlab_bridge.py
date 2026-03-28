import matlab.engine

eng = None

def start_matlab():
    global eng
    eng = matlab.engine.start_matlab()

def get_engine():
    return eng
