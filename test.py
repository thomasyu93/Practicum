#!/usr/bin/env
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
import listenerworker,jamworker
import threading
import readline
import rlcompleter
readline.parse_and_bind("tab: complete")
from rflib import *



#Globals
#Default Values
#frequency = 314350000
baudRate = 4800
FSK2 = "MOD_2FSK"
bandwidth = 24000


class Display(QWidget):

    def __init__(self):
        super(Display, self).__init__()
        self.allowListening = True
        self.initUI()
    def initUI(self):
        self.setFixedSize(1000, 500)
        self.setWindowTitle('RF Spoofer')
        #label = QLabel('RF Spoofer')
        layout = QGridLayout()
        #layout.addWidget(label)
        self.testButton = QPushButton('Initialize', self)
        self.listenButton = QPushButton('Listen', self)
        self.sendButton = QPushButton('Send', self)
        self.jamButton = QPushButton('Jam', self)
        self.stopButton = QPushButton('Stop', self)
        self.exitButton = QPushButton('Exit', self)

        self.testButton.setStyleSheet("background-color:green")
        self.jamButton.setStyleSheet("background-color:orange")
        self.exitButton.setStyleSheet("background-color: red")


        #self.stopButton.setEnabled(False)
        self.listenButton.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.jamButton.setEnabled(False)

        self.testButton.clicked.connect(self.handleButtonTest)
        self.exitButton.clicked.connect(self.closeEvent)
        self.listenButton.clicked.connect(self.handleButtonListen)
        self.stopButton.clicked.connect(self.handleButtonStop)
        self.jamButton.clicked.connect(self.handleButtonJam)


        self.modLabel = QLabel('Modulation:')
        layout.addWidget(self.modLabel,2,5)
        self.b1 = QRadioButton("2FSK")
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda:self.radioButtonState(self.b1))
        layout.addWidget(self.b1,3,5)

        self.b2 = QRadioButton("ASK")
        self.b2.toggled.connect(lambda:self.radioButtonState(self.b2))
        layout.addWidget(self.b2,3,6)

        self.frequencyLabel = QLabel('Frequency (Hz):')
        self.frequencyLine = QLineEdit('314350000')
        self.frequencyLabel.setFixedWidth(100)
        self.frequencyLine.setFixedWidth(100)

        self.baudLabel = QLabel('Baud Rate (bps):')
        self.BaudLine = QLineEdit('4800')
        self.baudLabel.setFixedWidth(100)
        self.BaudLine.setFixedWidth(100)


        #self.dlg.setFilter("*.txt")
        #self.filenames = QStringList()

        self.fileLineEdit = QLineEdit("Please Select File")
        #self.fileLineEdit.setFixedWidth(100)
        self.fileButton = QPushButton("Select File")
        self.fileLineEdit.setReadOnly(True)
        self.fileLabel = QLabel("File Save Location: ")
        self.fileButton.clicked.connect(self.handleButtonFile)

        layout.addWidget(self.fileLabel,18,0)
        layout.addWidget(self.fileLineEdit,18,1,1,3)
        layout.addWidget(self.fileButton,18,4)
        layout.addWidget(self.frequencyLabel,0,5)
        layout.addWidget(self.frequencyLine,0,6)
        layout.addWidget(self.baudLabel,1,5)
        layout.addWidget(self.BaudLine,1,6)

        #layout.addRow(self.frequencyLabel,self.frequencyLine)


        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text,0,0,18,5)


        layout.addWidget(self.testButton,19,0)
        layout.addWidget(self.listenButton,19,1)
        layout.addWidget(self.sendButton,19,2)
        layout.addWidget(self.jamButton,19,3)
        layout.addWidget(self.stopButton,19,4)
        layout.addWidget(self.exitButton,19,6)

        #layout.setColumnStretch(0, 1)
        #layout.setColumnStretch(1, 3)
        #layout.setRowStretch(0, 3)
        #layout.setRowStretch(1, 1)
        #layout.setAlignment(Qt.AlignRight)
        self.setLayout(layout)

    def handleButtonFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if self.fileName:
           self.fileLineEdit.setText(self.fileName)
        self.fileName = os.path.basename(self.fileName)
        print(self.fileName)
    def handleButtonTest(self):
        self.text.append("Initializing...")

        #Force update GUI
        app.processEvents()

        try:
            frequency = int(self.frequencyLine.text())
            self.dongle= RfCat()
            self.dongle.setFreq(frequency)
            self.dongle.setMdmModulation(MOD_2FSK)
            self.dongle.setMdmDRate(baudRate)
            self.dongle.setMaxPower()
            self.dongle.lowball()
            self.dongle.makePktFLEN(255)
            self.dongle.setChannel(0)

        except (ChipconUsbTimeoutException):
            self.text.append('Timd out... try again later')
            return
        except Exception as e:
            self.text.append(str(e))
            self.text.append('Dongle is busy, please try again later')
            return
        self.text.append("Initializing succesful:")


        self.text.append(self.dongle.reprHardwareConfig())
        self.text.append(self.dongle.reprSoftwareConfig())
        self.text.append(self.dongle.reprMdmModulation())
        self.text.append(self.dongle.reprFreqConfig())
        self.text.append(self.dongle.reprModemConfig() + "\n")

        self.listenButton.setEnabled(True)
        self.sendButton.setEnabled(True)
        self.jamButton.setEnabled(True)
        self.stopButton.setEnabled(True)

    #Thread handle
    def handleButtonListen(self):
        #t1 = threading.Thread(target=self.listenThreadWorker)
        #t1.start()


        self.obj = listenerworker.ListenerWorker(self.dongle)
        self.thread = QThread()

        self.obj.messageReady.connect(self.onMessageReady)

        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)

        self.thread.started.connect(self.obj.procListen)
        self.thread.start()

    def handleButtonJam(self):

        self.objJam = jamworker.JamWorker(self.dongle)
        self.jamThread = QThread()

        self.objJam.jamMessageReady.connect(self.onMessageReady)

        self.objJam.moveToThread(self.jamThread)
        self.objJam.finished.connect(self.jamThread.quit)

        self.jamThread.started.connect(self.objJam.procJam)
        self.jamThread.start()


    def onMessageReady(self, msg):
        self.text.append(msg)
        self.saveToFile(self.fileName,msg)

    def handleButtonStop(self):

        self.text.append("Stopping...")
        try:
            QtCore.QMetaObject.invokeMethod(self.obj, 'stopListen', Qt.DirectConnection, Q_ARG(str, 'test'))
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass
        try:
            QtCore.QMetaObject.invokeMethod(self.objJam, 'stopJam', Qt.DirectConnection)
        #Thread didn't start, therefore object does not exist
        except(AttributeError):
            pass
        #self.allowListening = False

    def radioButtonState(self,b):
        msg = b.text() + " is selected"
        #self.text.append(msg)
        if b.text() == "2FSK":
            if b.isChecked() == True:
                self.text.append(b.text()+" modulation is selected")
            else:
                pass
                #self.text.append(b.text()+" is deselected")
        if b.text() == "ASK":
            if b.isChecked() == True:
                self.text.append(b.text()+" modulation is selected")
            else:
                pass
                #self.text.append(b.text()+" is deselected")


    def closeEvent(self, event):
        try:
            self.dongle.setModeIDLE()
        #If no dongle binded
        except:
            print(event)
            pass
        self.close()

    def saveToFile(self,fileName,data):
        file = open(fileName, 'a')
        file.write(data)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ui = Display()
    ui.show()
    sys.exit(app.exec_())
