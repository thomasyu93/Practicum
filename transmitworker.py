    # worker.py
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtCore
import os
import time
import bitstring
from rflib import *


class TransmitWorker(QObject, RfCat):
    def __init__(self, Rfcat,transmissions):
        super(TransmitWorker, self).__init__()
        self.dongle = Rfcat
        self.rawCapture = transmissions
    finished = pyqtSignal()
    messageReady = pyqtSignal(str)
    @pyqtSlot()
    def procTransmit(self): # A slot takes no params
        #self.dongle.setRfMode(RFST_SRX)
        self.isRunning = True
        try:
            for index, transmit in enumerate(self.rawCapture):
                if self.isRunning:
                    transmission=bitstring.BitArray(hex=transmit).tobytes()
                    self.dongle.makePktFLEN(len(transmission))
                    self.dongle.RFxmit(transmission)
                    msg = "Sent: " + str(transmit) + " " + str(index +1)  + "Of" + str(len(self.rawCapture))
                    self.messageReady.emit(msg)
                else:
                    break
        except (KeyboardInterrupt):
            print("finished sending")
            self.dongle.setModeIDLE()
        print("finished sending")
        #self.dongle.setModeIDLE()
        #self.dongle.setRfMode(RFST_SRX)
        #self.dongle.setRfMode(RFST_SRX)
        self.finished.emit()


    @pyqtSlot()
    def forceExit(self):
        print("force exiting...")
        self.isRunning=False
