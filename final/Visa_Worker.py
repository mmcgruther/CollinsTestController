#import pyvisa
from PyQt5 import QtCore
import sys, time, threading
#from Visa_Wrapper import Visa_Manager

class Visa_Worker(QtCore.QObject):
    def __init__(self, addr = None, *args, **kwargs):
        super(Visa_Worker, self).__init__()
        #self.rm = Visa_Manager(addr)
        self.addr = addr
        self.args = args
        self.kwargs = kwargs
        self.connected = False
        self.running = False

    signal_connect = QtCore.pyqtSignal(str)
    signal_write = QtCore.pyqtSignal(str)
    signal_connected = QtCore.pyqtSignal(str, str)
    signal_not_connected = QtCore.pyqtSignal(str)
    signal_start = QtCore.pyqtSignal()
    signal_write_success = QtCore.pyqtSignal(str)
    signal_query_success = QtCore.pyqtSignal()
    signal_error = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(str)
    def slot_connect(self, cmd):
        print(threading.get_ident(), "Connecting to", self.addr)

        if self.addr == "TCPIP0::192.168.1.3":
            time.sleep(1)
            self.connected = False
            self.signal_not_connected.emit(self.addr)
        else:
            time.sleep(0.5)
            self.connected = True
            self.signal_connected.emit(self.addr, "dummy")
    @QtCore.pyqtSlot()
    def slot_start(self):
        self.running = True
        print(threading.get_ident(), "Start sending to", self.addr)

    @QtCore.pyqtSlot()
    def slot_stop(self):
        self.running = False
        print(threading.get_ident(), "Abort sending to", self.addr)

    @QtCore.pyqtSlot(str)
    def slot_write(self, cmd):
        if self.addr is None:
            self.signal_error.emit()
        elif not self.connected:
            self.signal_error.emit()
        elif not self.running:
            print(threading.get_ident(), "Skipped write to", self.addr)
        else:
            print(threading.get_ident(), "Write to", self.addr, cmd)
            time.sleep(1)
            self.signal_write_success.emit(self.addr)
    @QtCore.pyqtSlot()
    def slot_query(self):
        if self.addr is None:
            self.signal_error.emit()
        elif not self.connected:
            self.signal_error.emit()
        elif not self.running:
            print(threading.get_ident(), "Skipped query to", self.addr)
        else:
            print(threading.get_ident(), "Query to", self.addr)
            self.signal_write_success.emit()
            
