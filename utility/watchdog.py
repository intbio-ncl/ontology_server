from threading import Timer

class Watchdog(Exception):
    def __init__(self, timeout=5, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)

    def start(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()
    
    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self