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

        '''
        while self.Jamming:
            try:
                self.dongle.setModeTX()

            except (KeyboardInterrupt):
                break
            except (ChipconUsbTimeoutException):
                pass
        self.jamMessageReady.emit("stopped Jamming")
        self.dongle.setModeIDLE()
        '''
        '''
    @pyqtSlot()
    def stopJam(self):
        print("stopped called")
        self.Jamming = False
        self.dongle.setModeIDLE()
        self.dongle.setRfMode(RFST_SRX)
        print("stop jamming.......")
    '''

    @pyqtSlot()
    def finishJam(self):
        if self.Jamming == True:
            self.Jamming=False
            print("finished jamming...")
            #self.dongle.setRfMode(RFST_SRX)
            self.dongle.setModeRX()
            #self.dongle.setRfMode(RFST_SRX)
            self.finished.emit()
