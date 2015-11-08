from threading import *
import xml.etree.ElementTree as ET
import re
import time
from utils import *
from copy import deepcopy
'''
from tkinter import messagebox
from PrintWindow import *
from Configuration import *
from PrinterSerial import *
from utils import *
from copy import deepcopy
'''

class LogType:
    SEND = "send"
    RESPONSE = "response"
    ACTION = "action"

class Logger(EventDispatcher):
    def __init__(self):
        EventDispatcher.__init__(self)
        self.log = {LogType.SEND: [], LogType.RESPONSE:[], LogType.ACTION:[]}
    def log(self, type, message):
        self.log[type].append({'message':message})
 