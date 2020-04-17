from PyQt5 import QtCore
import sys, time, threading
from final.worker_pool import Worker_Pool
from final.Equipment_Model import Equipment_Model

"""

Functions:

Signals:

Slots:

Variables:

"""
class Connection_Manager(QtCore.QObject):
    def __init__(self, parent, equipment_model, worker_pool):
        super(Connection_Manager, self).__init__()
        self.parent = parent
        self.equipment_model = equipment_model
        self.worker_pool = worker_pool

    def list_resources(self):
        """
        Initiates establishing connections to configured equipment.

        On first call, starts workers for each address.
        Begin queries for each worker to identify connected equipment.
        Disables refresh button until queries completed
        """
        self.workersResponded = 0
        print("Main thread", threading.get_ident())

        for addr in self.equipment_model.get_addr_list():
            self.equipment_model.reset_index(addr)
            self.equipment_model.set_connected(addr, 2)

            if not self.worker_pool.is_init():
                w = self.worker_pool.create_worker(addr)
                #Signals from worker
                w.signal_connected.connect(self.slot_connected)
                w.signal_not_connected.connect(self.slot_not_connected)
                w.signal_write_success.connect(self.parent.slot_write_success)
                w.signal_query_success.connect(self.parent.slot_query_success)
                w.signal_error.connect(self.parent.slot_error)

            self.next_connection(addr)
 
        self.worker_pool.set_init(True)

    def next_connection(self, addr):
        """
        Triggers connection attempt to next equipment configured for an IP address.

        Subsequent calls iterate to next possible equipment.
        If no more equipment, returns True
        """
        self.equipment_model.set_connected(addr, 2)
        if not self.equipment_model.increment_equipment(addr):
            self.equipment_model.get_equipment_idn_cmd(addr)
            w_term = self.equipment_model.get_equipment_write_termination(addr)
            r_term = self.equipment_model.get_equipment_read_termination(addr)
            self.worker_pool.get_worker(addr).signal_connect.emit(self.equipment_model.get_equipment_idn_cmd(addr), w_term, r_term)
            return False
        else:
            print(addr, ": No connection found")
            self.equipment_model.set_connected(addr, 0)
            return True
    
    def connection_responded(self):
        """
        Keeps track of how many workers have completed, indicating when connection is complete
        """
        complete = False
        self.workersResponded += 1
        if self.workersResponded == len(self.equipment_model.get_addr_list()):
            complete = True
        self.parent.connection_responded(complete)

    @QtCore.pyqtSlot(str, str)
    def slot_connected(self, addr, name):
        """
        Called by worker's query response, determines if connection was successful.
        """
        if name == self.equipment_model.get_equipment_idn(addr):
            print(addr, ": Connected to ", name)
            self.equipment_model.set_connected(addr, 1)
            self.connection_responded()
        else:
            print(addr, ": Incorrect IDN", name, ", expected",self.equipment_model.get_equipment_idn(addr))
            if self.next_connection(addr):
                self.connection_responded()
            else:
                print(addr, ": Reconnecting...")      
        
    @QtCore.pyqtSlot(str)
    def slot_not_connected(self, addr):
        """
        Called by worker's query response when nothing was received
        """
        if self.next_connection(addr):
            self.connection_responded()
        else:
            print(addr, ": Reconnecting...")
