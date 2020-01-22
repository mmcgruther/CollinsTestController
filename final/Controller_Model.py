from PyQt5 import QtCore, QtGui
import json, threading, Equipment_Model, Test_Model, Visa_Worker, IP_Table_Model

class Controller_Model(QtCore.QObject):
   
    def __init__(self, parent, equipment_file=None, test_file=None):
        super(Controller_Model, self).__init__()
        self.equipment_model = Equipment_Model.Equipment_Model("equipment1.json")
        self.test_model = Test_Model.Test_Model(self)
        self.ip_table_model = IP_Table_Model.IP_Table_Model(self, self.get_IP_table_data())
        self.workersInit = False

    signal_set_refresh_button = QtCore.pyqtSignal(bool)
    signal_set_execute_button = QtCore.pyqtSignal(bool)
    signal_set_abort_button = QtCore.pyqtSignal(bool)
    signal_set_test_combobox = QtCore.pyqtSignal(bool)
    signal_set_equipment_combobox = QtCore.pyqtSignal(bool)

    signal_set_equipment_list = QtCore.pyqtSignal(list)

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
            self.reset_equipment_index(addr)
            self.set_connected(addr, 2)
            
            if not self.workersInit:           
                self.set_worker(self.create_worker(addr), addr)

            self.next_connection(addr)
 
        self.workersInit = True
        self.ip_table_model.setData(self.get_IP_table_data())

    @QtCore.pyqtSlot(int)
    def slot_change_selected_test(self, index):
        self.test_model.slot_selected_test_changed(index)
        self.signal_set_equipment_list.emit(self.get_test_equipment())

    @QtCore.pyqtSlot()
    def slot_execute_test(self):
        """Starts sending test commands to workers"""
        self.test_equipment_addr = {}
        for equipment in self.get_test_equipment():
            addr = self.get_equipment_address(equipment)
            self.test_equipment_addr[equipment] = addr
            if addr is None:
                #Error: equipment not connected
                print(equipment,"not connected")
                return
        self.signal_set_refresh_button.emit(False)
        self.signal_set_execute_button.emit(False)
        self.signal_set_abort_button.emit(False)
        self.signal_set_test_combobox.emit(False)
        self.signal_set_equipment_combobox.emit(False)

        self.workersResponded = 0
        print("Main thread starting test", threading.get_ident())

        for equipment in self.get_test_equipment():
            self.reset_test_index(equipment)
            self.get_worker(self.test_equipment_addr[equipment]).signal_start.emit()
            self.next_command(equipment)

    @QtCore.pyqtSlot()
    def abort_test(self):
        pass    
       
    @QtCore.pyqtSlot(str, str)
    def slot_connected(self, addr, name):
        if name == self.get_equipment_idn(addr):
            print(addr, ": Connected to ", name)
            self.set_connected(addr, 1)
            self.connection_response()
        elif self.next_connection(addr):
            self.connection_response()
        else:
            print(addr, ": Incorrect ID", name, ", Reconnecting...")
        
    @QtCore.pyqtSlot(str)
    def slot_not_connected(self, addr):
        if self.next_connection(addr):
            self.connection_response()
        else:
            print(addr, ": No connection response. Reconnecting...")

    @QtCore.pyqtSlot(str)
    def slot_write_success(self, addr):
        equipment = list(self.test_equipment_addr.keys())[list(self.test_equipment_addr.values()).index(addr)]
        self.next_command(equipment)

    def next_connection(self, addr):
        self.set_connected(addr, 2)
        if not self.increment_equipment(addr):
            self.get_worker(addr).signal_connect.emit(addr)
            return False
        else:
            print(addr, ": No connection found")
            self.set_connected(addr, 0)
            return True

    def next_command(self, equipment):
        cmd = self.get_next_config_command(equipment)
        if cmd is None:
            #Current phase complete, wait for other equipment
            self.test_response()
        else:
            addr = self.test_equipment_addr[equipment]
            self.get_worker(addr).signal_write.emit(cmd)

    def create_worker(self, addr):
        w = Visa_Worker.Visa_Worker(addr)
        w.w_thread = QtCore.QThread()
        w.w_thread.start()

        w.signal_connect.connect(w.slot_connect)
        w.signal_write.connect(w.slot_write)
        w.signal_write_success.connect(self.slot_write_success)
        w.signal_connected.connect(self.slot_connected)
        w.signal_not_connected.connect(self.slot_not_connected)
        w.signal_start.connect(w.slot_start)

        w.moveToThread(w.w_thread)
        return w

    def connection_response(self):
        self.ip_table_model.setData(self.get_IP_table_data())
        self.workersResponded += 1
        if self.workersResponded == len(self.get_addr_list()):
            self.signal_set_refresh_button.emit(True)
            self.signal_set_execute_button.emit(True)

    def test_response(self):
        """Tracks when worker threads have completed test phase"""
        self.workersResponded += 1
        if self.workersResponded == len(self.test_equipment_addr):
            print("End of test execution")

            self.signal_set_refresh_button.emit(True)
            self.signal_set_execute_button.emit(True)
            self.signal_set_abort_button.emit(False)
            self.signal_set_test_combobox.emit(True)
            self.signal_set_equipment_combobox.emit(True)



    def get_IP_table_data(self):
        return self.equipment_model.get_IP_table_data()

    def get_test_model(self):
        return self.test_model

    def get_tests(self):
        return self.test_model.get_tests()

    @QtCore.pyqtSlot(int)
    def slot_selected_test_changed(self, index):
        self.test_model.slot_selected_test_changed(index)

    @QtCore.pyqtSlot(int)
    def slot_selected_equipment_changed(self, index):
        self.test_model.slot_selected_equipment_changed(index)

    def get_test_equipment(self):
        return self.test_model.get_test_equipment()

    def get_equipment_address(self, equipment_name):
        return self.equipment_model.get_equipment_address(equipment_name)

    def reset_test_index(self, equipment):
        self.test_model.reset_index(equipment)

    def get_worker(self, addr):
        return self.equipment_model.get_worker(addr)

    def get_addr_list(self):
        return self.equipment_model.get_addr_list()
    
    def reset_equipment_index(self, addr):
        self.equipment_model.reset_index(addr)

    def set_connected(self, addr, value):
        self.equipment_model.set_connected(addr, value)

    def set_worker(self, worker, addr):
        self.equipment_model.set_worker(worker, addr)

    def get_equipment_idn(self, addr):
        return self.equipment_model.get_equipment_idn(addr)

    def increment_equipment(self, addr):
        return self.equipment_model.increment_equipment(addr)

    def get_next_config_command(self, equipment):
        return self.test_model.get_next_config_command(equipment)