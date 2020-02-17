from PyQt5 import QtCore
import sys, time, threading

"""Creates and returns worker threads. Manages identifying connected configured equipment

Functions:

Signals:

Slots:

Variables:

"""
class Connection_Manager(QtCore.QObject):
    def __init__(self, addr_list):
        super(Connection_Manager, self).__init__()
        self.addr_list = addr_list

    @QtCore.pyqtSlot()
    def list_resources(self):
        """On first call, starts workers for each address.
        Begin queries for each worker to identify connected equipment.
        Disables refresh button until queries completed"""
        self.signal_set_refresh_button.emit(False)
        self.signal_set_execute_button.emit(False)
        self.workersResponded = 0
        print("Main thread", threading.get_ident())

        for addr in self.get_addr_list():
            self.equipment_model.reset_index(addr)
            self.set_connected(addr, 2)
            
            if not self.workersInit:           
                self.set_worker(self.create_worker(addr), addr)

            self.next_connection(addr)
 
        self.workersInit = True
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())