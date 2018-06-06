"""---------------------------------------------------------------------------------------
--      SOURCE FILE:        bruteworker.py - bruteforce worker
--
--      PROGRAM:            RFSpoofer
--
--
--      DATE:               May 14, 2018
--
--      DESIGNERS:          Thomas Yu
--
--      PROGRAMMERS:        Thomas Yu
--
--      NOTES:
--      This file is responsible for brute force transmitting transmissions. note
--      that this class is started as a thread from rfspoofer.py
---------------------------------------------------------------------------------------"""
# worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import os
import time
import bitstring
from rflib import *


class BruteWorker(QObject, RfCat):
    def __init__(self, Rfcat):
        super(BruteWorker, self).__init__()
        self.dongle = Rfcat
    finished = pyqtSignal()
    messageReady = pyqtSignal(str)
    @pyqtSlot()
    def procTransmit(self): # A slot takes no params
        self.isRunning = True
        counter = 0
        while self.isRunning:
            hexdata= hex(counter)
            counter +=1
            self.dongle.makePktFLEN(len(hexdata))
            self.dongle.RFxmit(hexdata)
            msg = "sent: " + hexdata
            self.messageReady.emit(msg)
            time.sleep(0.01)

    @pyqtSlot()
    def forceExit(self):
        print("force exiting...")
        self.isRunning=False
        self.dongle.setModeRX()
        self.finished.emit()
