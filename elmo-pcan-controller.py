import can

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

### Setup can ###
bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=125000) #Open pcan bus at 125kHz baudrate. In active state by default

### Class to hold PCAN message data ###
class PCANData:

    name = "Default"
    reg = 0x00000000
    msg = can.Message()
    dataSuff = "units"

    def __init__(self, name, dataSuff):
        self.name = name
        self.dataSuff = dataSuff

    def setData(self, newmsg):
        self.msg = newmsg

### Dictionaries to hold each register entry. Keyed based on register value. ###
#ELMO
regsELMO = {
    0x09030010 : PCANData("Heartbeat", "units"),
    0x0103006 : PCANData("12V Supply Info", "mV, Ma, mW"),
    0x01030061 : PCANData("5V Supply Info", "mV, mA, mW"),
    0x01030080 : PCANData("Interlock Status", "2=Open"),
    0x010300A0 : PCANData("Mode-Lock AVG", "mV"),
    0x010300A1 : PCANData("Mode-Lock SIG", "mV"),
    0x010300A2 : PCANData("Mode-Lock HRM", "mV"),
    0x01030120 : PCANData("Diode Drive Current", "mA"),
    0x01030140 : PCANData("Diode Temperature", "mdegC"),
    0x01030180 : PCANData("Housing Temperature", "mdegC"),
    0x01030181 : PCANData("OScillator Temperature", "mdegC"),
    0x010301A0 : PCANData("Firmware Version", "Major+24+Minor"),
    0x010301A1 : PCANData("Serial Number", "#"),
    0x01030150 : PCANData("Photodiode Voltage", "m/V"),
    0x010301B1 : PCANData("Lifetime of Diodes", "Yes/No")
}

#ELMA
regsELMA = {
    0x09040010 : PCANData("Heartbeat", "units"),
    0x01040060 : PCANData("12V Supply Info", "mV, Ma, mW"),
    0x01040061 : PCANData("5V Supply Info", "mV, mA, mW"),
    0x010400A0 : PCANData("Incoming PD Voltage", "mV"),
    0x010400A1 : PCANData("Outgoing PD Voltage", "mV"),
    0x01040100 : PCANData("SET Input PD Thresh Voltage", "mV"),
    0x01040101 : PCANData("SET Output PD Thresh Voltage", "mV"),
    0x01040120 : PCANData("Diode Drive Current", "mA"),
    0x01040140 : PCANData("Diode 1 Temperature", "mdegC"),
    0x01040141 : PCANData("Diode 2 Temperature", "mdegC"),
    0x01040150 : PCANData("Photodetector 1 Voltage", "m/V"),
    0x01040151 : PCANData("Photodetector 2 Voltage", "m/V"),
    0x01040180 : PCANData("Heatsink Temperture", "mdegC"),
    0x01040181 : PCANData("Fiber Box Temperature", "mdegC"),
    0x010401A0 : PCANData("Firmware Version", "Major+24+Minor"),
    0x010401A1 : PCANData("Serial No", "#"),
    0x010401B1 : PCANData("Diode Lifetime", "units")
}




# Thread to recieve CAN communications
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        while (self.enableVar == True):
            msg = bus.recv()
            self.progress.emit(msg)
        self.finished.emit()

class Window(QMainWindow):
    # Snip...
    def readCAN(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.longRunningBtn.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.longRunningBtn.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.stepLabel.setText("Long-Running Step: 0")
        )
