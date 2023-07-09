import threading

class Thread:
    def __init__(self, func = None, arg =None):
        self.t = threading.Thread(target=func, args=arg)
        self.t.start()