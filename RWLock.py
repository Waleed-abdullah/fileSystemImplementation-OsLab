from threading import *

class RWLock:
    def __init__(self):
        self.readers = 0
        self.lock = Semaphore(1)
        self.writelock = Semaphore(1)
    
    def acquire_readlock(self):
        self.lock.acquire()
        self.readers += 1
        if self.readers == 1:
            self.writelock.acquire()
        self.lock.release()

    def release_readlock(self):
        self.lock.acquire()
        self.readers -= 1
        if self.readers == 0:
            self.writelock.release()
        self.lock.release()
    
    def acquire_writelock(self):
        self.writelock.acquire()
    
    def release_writelock(self):
        self.writelock.release()