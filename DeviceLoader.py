from SimpleStepperDriverV1.SimpleStepperDriverV1 import SimpleStepperDriverV1
from SimpleLoggerV1.SimpleLoggerV1 import SimpleLoggerV1
import threading
import pymodbus
import time
import serial.tools.list_ports


class DeviceLoader:

    def __init__(self) -> None:
        self.connectedDevices=self.find_all_serial_devices()
        self.board1=None
        self.board2=None
        self.board3=None
        self.board4=None
        self.board5=None
        self.tenzosBoard=None

        board1Id="0026002c5333501520353731"
        board2Id="002800265333501420353731"
        board3Id="002600275333501520353731"
        board4Id="002600345333501520353731"
        board5Id="002600185333501520353731"
        tenzosBoardId="002f00353530511130393832"

        for info in self.connectedDevices:
            if(info[2] == board1Id):
                self.board1=info[1]
            if(info[2] == board2Id):
                self.board2=info[1]
            if(info[2] == board3Id):
                self.board3=info[1]
            if(info[2] == board4Id):
                self.board4=info[1]
            if(info[2] == board5Id):
                self.board5=info[1]
            if(info[2] == tenzosBoardId):
                self.tenzosBoard=info[1]
    def find_all_serial_devices(self):
        foundPortDevices = []
        def check_port(port):
            try:
                dev = SimpleStepperDriverV1(serialPort=port,method='rtu')
                if(dev.getType()==39):
                    dev = SimpleLoggerV1(serialPort=port,method='rtu')
                foundPortDevices.append((port,dev,dev.getUid()))
            except pymodbus.exceptions.ModbusIOException:
                pass
            except pymodbus.exceptions.ConnectionException:
                pass
        [threading.Thread(target=check_port, args=(port.device,)).start() for port in serial.tools.list_ports.comports()]
        time.sleep(1.5)
        return foundPortDevices

    def getBoard1(self):
        return self.board1

    def getBoard2(self):
        return self.board2

    def getBoard3(self):
        return self.board3

    def getBoard4(self):
        return self.board4

    def getBoard5(self):
        return self.board5

    def getTenzosBoard(self):
        return self.tenzosBoard