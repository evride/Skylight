from serial import Serial
from serial.serialutil import SerialException
from threading import *
import time
import os
from utils import *

class TestSerial(Serial, EventDispatcher):
    def __init__(self, port, baud):
        Serial.__init__(self)
        EventDispatcher.__init__(self)
        self.port = port
        self.baudrate = baud
        self.listeners = {}
        self.connected = False
        self.closing = False
        try:
            self.open()
        except SerialException as se:
            if os.name == "nt":
                if str(se).find('FileNotFoundError') >= 0:
                    self.notFound = True
                    self.dispatch('connection-error')
                elif str(se).find('PermissionError') >= 0:
                    self.inUse = True
            self.connectionError = True
            self.dispatch('connection-error')
            return
        detectThread = Thread(target=self.detectSetup)
        detectThread.start()
    def detectSetup(self):
        time.sleep(2)
        
        while (self.closing == False):
            bytesWaiting = self.inWaiting()
            if (bytesWaiting):
                if (not self.connected):
                    self.connected = True
                    self.dispatch('connected')
                self.dispatch("data", self.read(self.inWaiting()))
            time.sleep(0.2)
    def close(self):
        self.closing = True
        super(TestSerial, self).close()
        self.dispatch('connection-close')
        
 