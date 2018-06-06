"""---------------------------------------------------------------------------------------
--      SOURCE FILE:        jamworker.py - jam worker
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
--      This file is responsible for jamming transmissions. This class is
--      started as a thread from rfspoofer.py
---------------------------------------------------------------------------------------"""
    # worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import time
from rflib import *


class JamWorker(QObject, RfCat):
    def __init__(self, Rfcat):
        super(JamWorker, self).__init__()
        self.dongle = Rfcat
    finished = pyqtSignal()
    jamMessageReady = pyqtSignal(str)

    @pyqtSlot()
    def procJam(self): # A slot takes no params

        self.Jamming = True
        self.jamMessageReady.emit("Starting Jamming...")

        self.dongle.setModeTX()


    @pyqtSlot()
    def finishJam(self):
        if self.Jamming == True:
            self.Jamming=False
            print("finished jamming...")
            #self.dongle.setRfMode(RFST_SRX)
            self.dongle.setModeRX()
            #self.dongle.setRfMode(RFST_SRX)
            self.finished.emit()
