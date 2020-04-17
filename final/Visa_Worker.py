
from PyQt5 import QtCore
import sys, time, threading
from final.Visa_Wrapper import Visa_Session

class Visa_Worker(QtCore.QObject):
    """
    Worker object for equipment communication.
    """
    def __init__(self, addr, backend, *args, **kwargs):
        super(Visa_Worker, self).__init__()
        self.session = Visa_Session(addr, backend)
        self.addr = addr
        self.args = args
        self.kwargs = kwargs
        self.connected = False
        self.running = False

    signal_connect = QtCore.pyqtSignal(str, str, str)
    signal_write = QtCore.pyqtSignal(str)
    signal_query = QtCore.pyqtSignal(str, int)
    signal_connected = QtCore.pyqtSignal(str, str)
    signal_not_connected = QtCore.pyqtSignal(str)
    signal_start = QtCore.pyqtSignal()
    signal_stop = QtCore.pyqtSignal()
    signal_write_success = QtCore.pyqtSignal(str)
    signal_query_success = QtCore.pyqtSignal(str, str, int)
    signal_error = QtCore.pyqtSignal(str, str)
    signal_disconnect = QtCore.pyqtSignal()

    @QtCore.pyqtSlot(str, str, str)
    def slot_connect(self, cmd, w_term, r_term):
        print(threading.get_ident(), "Connecting to", self.addr)
            
        if self.session.connect(w_term, r_term):
            print(threading.get_ident(), "Connection failure", self.addr)
            self.connected = False
            self.signal_not_connected.emit(self.addr)
        else:    
            response = self.session.query(cmd)
            if response is not None:
                self.connected = True
                self.signal_connected.emit(self.addr, response)
            else:
                print(threading.get_ident(), "No response", self.addr)
                self.connected = False
                self.signal_not_connected.emit(self.addr)
            
    @QtCore.pyqtSlot()
    def slot_disconnect(self):
        if self.connected:
            print(threading.get_ident(), "Disconnecting from", self.addr)
            self.connected = False
            self.session.close()

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
            self.signal_error.emit(self.addr, cmd)
        elif not self.connected:
            print(threading.get_ident(), "Write attempt while not connected", self.addr)
            self.signal_error.emit(self.addr, cmd)
        elif not self.running:
            print(threading.get_ident(), "Skipped write to", self.addr)
            self.signal_write_success.emit(self.addr)
        else:
            print(threading.get_ident(), "Write to", self.addr, cmd)
            if self.session.write(cmd):
                self.signal_error.emit(self.addr, cmd)
                print(threading.get_ident(), "Write failure", addr)
            else:
                self.signal_write_success.emit(self.addr)

    @QtCore.pyqtSlot(str, int)
    def slot_query(self, cmd, qID):
        if self.addr is None:
            self.signal_error.emit(self.addr, cmd)
        elif not self.connected:
            self.signal_error.emit(self.addr, cmd)
        elif not self.running:
            print(threading.get_ident(), "Skipped query to", self.addr)
            self.signal_query_success.emit(self.addr, None, qID)
        else:
            print(threading.get_ident(), "Query to", self.addr, cmd)
            response = self.session.query(cmd)
            if response is None:
                self.signal_error.emit(self.addr, cmd)
                print(threading.get_ident(), "Query failure", self.addr)
            else:
                self.signal_query_success.emit(self.addr, response, qID)

    def __del__(self):
        self.slot_disconnect()
            
