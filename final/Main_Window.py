from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QTableView, QTreeView, QComboBox
import IP_Table_Model, Controller_Model, Test_Model
import sys, time, threading, json, Visa_Worker

class Main_Window(QMainWindow):
    def __init__(self):
        super(Main_Window, self).__init__()
        self.equipment_model = Controller_Model.Controller_Model("equipment1.json")
        self.workersInit = False
        self.initUI()

    def initUI(self):
        """Lay out main window"""
        uic.loadUi('final/Main_Window.ui', self)

        self.refresh_button = self.findChild(QPushButton, 'refresh_button')
        self.refresh_button.clicked.connect(self.list_resources)

        self.execute_button = self.findChild(QPushButton, 'execute_button')
        self.execute_button.clicked.connect(self.execute_test)

        self.abort_button = self.findChild(QPushButton, 'abort_button')
        self.abort_button.clicked.connect(self.abort_test)  
        self.abort_button.setEnabled(False)      

        self.ip_table_model = IP_Table_Model.IP_Table_Model(self, self.equipment_model.get_IP_table_data())
        self.ip_table_view = self.findChild(QTableView, 'ip_table_view')
        self.ip_table_view.setModel(self.ip_table_model)

        self.test_model = Test_Model.Test_Model(self)
        self.test_tableview = self.findChild(QTableView, 'test_tableview')
        self.test_tableview.setModel(self.test_model)

        self.test_combobox = self.findChild(QComboBox, 'test_combobox')
        for test in self.test_model.get_tests():
            self.test_combobox.addItem(test)
        self.test_combobox.currentIndexChanged.connect(self.change_selected_test)
        self.selected_test_changed.connect(self.test_model.slot_selected_test_changed)

        self.equipment_combobox = self.findChild(QComboBox, 'equipment_combobox')
        self.set_equipment_combobox()
        self.equipment_combobox.currentIndexChanged.connect(self.test_model.slot_selected_equipment_changed)

        self.show()

    selected_test_changed = QtCore.pyqtSignal(int)

    def set_equipment_combobox(self):
        self.equipment_combobox.clear()
        for equipment in self.test_model.get_test_equipment():
            self.equipment_combobox.addItem(equipment)

    @QtCore.pyqtSlot(int)
    def change_selected_test(self, index):
        self.selected_test_changed.emit(index)
        self.set_equipment_combobox()

    @QtCore.pyqtSlot()
    def execute_test(self):
        """Starts sending test commands to workers"""
        self.test_equipment_addr = {}
        for equipment in self.test_model.get_test_equipment():
            addr = self.equipment_model.get_equipment_address(equipment)
            self.test_equipment_addr[equipment] = addr
            if addr is None:
                #Error: equipment not connected
                print(equipment,"not connected")
                return
        
        self.refresh_button.setEnabled(False)
        self.execute_button.setEnabled(False)
        self.abort_button.setEnabled(False)
        self.test_combobox.setEnabled(False)
        self.equipment_combobox.setEnabled(False)
        self.workersResponded = 0
        print("Main thread starting test", threading.get_ident())

        for equipment in self.test_model.get_test_equipment():
            self.test_model.reset_index(equipment)
            self.equipment_model.get_worker(self.test_equipment_addr[equipment]).signal_start.emit()
            self.next_command(equipment)

    @QtCore.pyqtSlot()
    def abort_test(self):
        pass    

    @QtCore.pyqtSlot()
    def list_resources(self):
        """On first call, starts workers for each address.
        Begin queries for each worker to identify connected equipment.
        Disables refresh button until queries completed"""
        self.refresh_button.setEnabled(False)
        self.execute_button.setEnabled(False)
        self.workersResponded = 0
        print("Main thread", threading.get_ident())

        for addr in self.equipment_model.get_addr_list():
            self.equipment_model.reset_index(addr)
            self.equipment_model.set_connected(addr, 2)
            
            if not self.workersInit:           
                self.equipment_model.set_worker(self.create_worker(addr), addr)

            self.next_connection(addr)
 
        self.workersInit = True
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())
        
    @QtCore.pyqtSlot(str, str)
    def slot_connected(self, addr, name):
        if name == self.equipment_model.get_equipment_idn(addr):
            print(addr, ": Connected to ", name)
            self.equipment_model.set_connected(addr, 1)
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
        self.equipment_model.set_connected(addr, 2)
        if not self.equipment_model.increment_equipment(addr):
            self.equipment_model.get_worker(addr).signal_connect.emit(addr)
            return False
        else:
            print(addr, ": No connection found")
            self.equipment_model.set_connected(addr, 0)
            return True

    def next_command(self, equipment):
        cmd = self.test_model.get_next_config_command(equipment)
        if cmd is None:
            #Current phase complete, wait for other equipment
            self.test_response()
        else:
            addr = self.test_equipment_addr[equipment]
            self.equipment_model.get_worker(addr).signal_write.emit(cmd)

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
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())
        self.workersResponded += 1
        if self.workersResponded == len(self.equipment_model.get_addr_list()):
            self.refresh_button.setEnabled(True)
            self.execute_button.setEnabled(True)

    def test_response(self):
        """Tracks when worker threads have completed test phase"""
        self.workersResponded += 1
        if self.workersResponded == len(self.test_equipment_addr):
            print("End of test execution")
            self.refresh_button.setEnabled(True)
            self.execute_button.setEnabled(True)
            self.abort_button.setEnabled(True)
            self.test_combobox.setEnabled(True)
            self.equipment_combobox.setEnabled(True)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = Main_Window()
    sys.exit(app.exec_())
