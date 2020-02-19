from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer
from final import Equipment_Model, Test_Model, Visa_Worker, IP_Table_Model
import json, threading
import numpy as np

"""
TODO:
    -Fix repetitions bug
    -Create Output Manager?
    -Get csv file data for output manager
    -Create tabbed window for Test config

    -Documentation
    -Refactor Connection Manager and Test Manager out of Controller Model
    -Rename Controller Model?
"""

class Controller_Model(QtCore.QObject):
   
    def __init__(self, parent, equipment_file, tests_file, backend):
        super(Controller_Model, self).__init__()
        self.equipment_model = Equipment_Model.Equipment_Model(equipment_file)
        self.test_model = Test_Model.Test_Model(self, tests_file)
        self.selectedTest = None
        self.selectedEquipment = None
        self.selectedPhase = None
        self.default_test_selection()
        self.ip_table_model = IP_Table_Model.IP_Table_Model(self, self.equipment_model.get_IP_table_data())
        self.backend = backend
        self.workersInit = False
        self.phase_list = ['config','run','reset']
        self.runRepetitions = 10
        self.runPeriod = 1000
        self.runCounter = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_callback)

    signal_set_refresh_button = QtCore.pyqtSignal(bool)
    signal_set_execute_button = QtCore.pyqtSignal(bool)
    signal_set_abort_button = QtCore.pyqtSignal(bool)
    signal_set_test_combobox = QtCore.pyqtSignal(bool)
    signal_set_equipment_combobox = QtCore.pyqtSignal(bool)
    signal_set_phase_combobox = QtCore.pyqtSignal(bool)
    signal_update_canvas = QtCore.pyqtSignal(object)

    signal_set_test_list = QtCore.pyqtSignal(list)
    signal_set_equipment_list = QtCore.pyqtSignal(list)
    signal_set_phase_list = QtCore.pyqtSignal(list)

    signal_set_test_index = QtCore.pyqtSignal(int)
    signal_set_equipment_index = QtCore.pyqtSignal(int)

    def initialize_view(self):
        self.signal_set_test_list.emit(self.test_model.get_test_list())
        self.slot_change_selected_test(0)

    def add_new_command(self, command, commandName):
        self.test_model.append_new_command(command, commandName, self.selectedTest, self.selectedEquipment, self.selectedPhase)


    def get_configured_equipment_command_list(self):
        return self.equipment_model.get_equipment_command_list(self.selectedEquipment)

    def add_new_equipment(self, equipment):
        if not self.test_model.is_equipment(self.selectedTest, equipment):
            self.test_model.append_new_equipment(self.selectedTest, equipment)
            equipment_list = self.test_model.get_test_equipment_list(self.selectedTest)
            self.signal_set_equipment_list.emit(equipment_list)
            self.signal_set_equipment_index.emit(len(equipment_list) - 1)

    def get_configured_equipment_list(self):
        return self.equipment_model.get_configured_equipment_list()

    def add_new_test(self, testName):
        if not self.test_model.is_test(testName):
            self.test_model.append_new_test(testName)
            #Select new test
            test_list = self.test_model.get_test_list()
            self.signal_set_test_list.emit(test_list)
            self.signal_set_test_index.emit(len(test_list) - 1)
            
        

    def timer_callback(self):
        print("Timer Elapsed")
        self.start_test_phase(self.executionPhase)

    def default_test_selection(self):
        test_list = self.test_model.get_test_list()
        if len(test_list) == 0:
            self.selectedTest = None
        else:
            self.selectedTest = test_list[0]
        self.default_equipment_selection(self.selectedTest)

    def default_equipment_selection(self, test):
        equipment_list = self.test_model.get_test_equipment_list(test)
        if len(equipment_list) == 0:
            self.selectedEquipment = None
        else:
            self.selectedEquipment = equipment_list[0]
        self.default_phase_selection(test, self.selectedEquipment)

    def default_phase_selection(self, test, equipment):
        self.selectedPhase = 'config'

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
                self.equipment_model.set_worker(self.create_worker(addr), addr)         

            self.next_connection(addr)
 
        self.workersInit = True
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())

    @QtCore.pyqtSlot()
    def slot_execute_test(self):
        """Starts sending test commands to workers"""
        self.test_equipment_addr = {}
        test_equipment_list = self.test_model.get_test_equipment_list(self.selectedTest)
        for equipment in test_equipment_list:
            addr = self.get_equipment_address(equipment)
            self.test_equipment_addr[equipment] = addr
            if addr is None:
                #Error: equipment not connected
                print(equipment,"not connected")
                return
        self.signal_set_refresh_button.emit(False)
        self.signal_set_execute_button.emit(False)
        self.signal_set_abort_button.emit(True)
        self.signal_set_test_combobox.emit(False)
        self.signal_set_equipment_combobox.emit(False)
        self.workersResponded = 0
        print("Main thread starting test", threading.get_ident())
        for equipment in self.test_model.get_test_equipment_list(self.selectedTest):
            self.get_worker(self.test_equipment_addr[equipment]).signal_start.emit()
        self.init_output()
        self.start_test_phase('config')

    @QtCore.pyqtSlot()
    def abort_test(self):
        self.signal_set_abort_button.emit(False)
        print("Main thread aborting test", threading.get_ident())
        for equipment in self.test_model.get_test_equipment_list(self.selectedTest):
            self.get_worker(self.test_equipment_addr[equipment]).signal_stop.emit()
       
    @QtCore.pyqtSlot(str, str)
    def slot_connected(self, addr, name):
        if name == self.get_equipment_idn(addr):
            print(addr, ": Connected to ", name)
            self.set_connected(addr, 1)
            self.connection_responded()
        else:
            print(addr, ": Incorrect IDN", name, ", expected",self.get_equipment_idn(addr))
            if self.next_connection(addr):
                self.connection_responded()
            else:
                print(addr, ": Reconnecting...")      
        
    @QtCore.pyqtSlot(str)
    def slot_not_connected(self, addr):
        if self.next_connection(addr):
            self.connection_responded()
        else:
            print(addr, ": Reconnecting...")

    @QtCore.pyqtSlot(str)
    def slot_write_success(self, addr):
        equipment = list(self.test_equipment_addr.keys())[list(self.test_equipment_addr.values()).index(addr)]
        self.next_command(equipment)

    def init_output(self):
        self.plot_data = []

    def update_output(self, str_data):
        #data = float(str_data)
        data_split = str_data.split(',')
        data_array = np.array(list(map(float, data_split[1:])))
        #print(data)
        #self.plot_data.append(data)
        if len(data_array) > 5:
            self.plot_data = data_array
            self.signal_update_canvas.emit(self.plot_data)

    @QtCore.pyqtSlot(str, str)
    def slot_query_success(self, addr, data):
        print("Data received from", addr, "type:", type(data), "data:", data)
        equipment = list(self.test_equipment_addr.keys())[list(self.test_equipment_addr.values()).index(addr)]
        self.update_output(data)
        self.next_command(equipment)

    @QtCore.pyqtSlot(str, str)
    def slot_error(self, addr, cmd):
        print("Error from:", addr, "with command:", cmd)
        equipment = list(self.test_equipment_addr.keys())[list(self.test_equipment_addr.values()).index(addr)]
        self.abort_test()
        self.next_command(equipment)

    def next_connection(self, addr):
        self.set_connected(addr, 2)
        if not self.increment_equipment(addr):
            self.equipment_model.get_equipment_idn_cmd(addr)
            self.get_worker(addr).signal_connect.emit(self.equipment_model.get_equipment_idn_cmd(addr))
            return False
        else:
            print(addr, ": No connection found")
            self.set_connected(addr, 0)
            return True

    def reset_test_index(self):
        test_equipment_list = self.test_model.get_test_equipment_list(self.selectedTest)
        self.test_index_by_equipment = {}
        for equipment in test_equipment_list:
            self.test_index_by_equipment[equipment] = -1

    def start_test_phase(self, phase):
        self.executionPhase = phase
        #self.reset_test_index()
        self.test_index_by_equipment = {}
        self.cmd_tuple_lists_by_equipment  = {}
        for equipment in self.test_model.get_test_equipment_list(self.selectedTest):
            
            self.test_index_by_equipment[equipment] = -1
            self.cmd_tuple_lists_by_equipment[equipment] = self.get_cmd_tuple_list(self.selectedTest, equipment, phase)
            self.next_command(equipment)

    def get_cmd_tuple_list(self, test, equipment, phase):
        temp_list = []
        addr = self.test_equipment_addr[equipment]
        cmd_objs = self.test_model.get_cmd_objs(test,equipment,phase)
        for key in list(cmd_objs.keys()):
            cmd_name = cmd_objs[key]['name']
            cmd_args = cmd_objs[key]['args']
            cmd_tuple = self.equipment_model.get_formatted_cmd_tuple(addr, cmd_name, cmd_args)
            temp_list.append(cmd_tuple)
        return temp_list

    def next_command(self, equipment):
        self.test_index_by_equipment[equipment] += 1
        if self.test_index_by_equipment[equipment] >= len(self.cmd_tuple_lists_by_equipment[equipment]):
            #Current phase complete, wait for other equipment
            self.test_responded()
        else:
            addr = self.test_equipment_addr[equipment]
            cmd, cmd_type =self.cmd_tuple_lists_by_equipment[equipment][self.test_index_by_equipment[equipment]]
            if cmd_type == 'w':
                self.get_worker(addr).signal_write.emit(cmd)
            elif cmd_type == 'q':
                self.get_worker(addr).signal_query.emit(cmd)

    def create_worker(self, addr):
        w = Visa_Worker.Visa_Worker(addr, self.backend)
        w.w_thread = QtCore.QThread()
        w.w_thread.start()

        w.signal_connect.connect(w.slot_connect)
        w.signal_write.connect(w.slot_write)
        w.signal_write_success.connect(self.slot_write_success)
        w.signal_connected.connect(self.slot_connected)
        w.signal_not_connected.connect(self.slot_not_connected)
        w.signal_start.connect(w.slot_start)
        w.signal_query.connect(w.slot_query)
        w.signal_query_success.connect(self.slot_query_success)
        w.signal_stop.connect(w.slot_stop)
        w.signal_error.connect(self.slot_error)

        w.moveToThread(w.w_thread)
        return w

    def connection_responded(self):
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())
        self.workersResponded += 1
        if self.workersResponded == len(self.get_addr_list()):
            self.signal_set_refresh_button.emit(True)
            self.signal_set_execute_button.emit(True)

    def test_responded(self):
        """Tracks when worker threads have completed test phase"""
        self.workersResponded += 1
        if self.workersResponded == len(self.test_equipment_addr):
            print("End of", self.executionPhase, "phase")
            #self.reset_test_index()

            if self.executionPhase == 'config':
                self.executionPhase = 'run'
                self.workersResponded = 0
                print("Starting run phase")
                self.timer.setInterval(self.runPeriod)
                if self.runRepetitions > 0:
                    self.timer.start()
                self.start_test_phase(self.executionPhase)

            elif self.executionPhase == 'run':
                self.runCounter += 1
                if self.runRepetitions > self.runCounter:
                    print("Run iteration", self.runCounter, "complete")
                    self.workersResponded = 0
                    
                else:
                    self.timer.stop()
                    self.executionPhase = 'reset'
                    self.workersResponded = 0
                    print("Starting reset phase")
                    self.start_test_phase(self.executionPhase)

            elif self.executionPhase == 'reset':
                print("End of test")
                self.end_test()

    def end_test(self):
        self.signal_set_refresh_button.emit(True)
        self.signal_set_execute_button.emit(True)
        self.signal_set_abort_button.emit(False)
        self.signal_set_test_combobox.emit(True)
        self.signal_set_equipment_combobox.emit(True)
    
    def set_pin_filename(self, filename):
        self.pin_filename = filename

    def get_IP_table_model(self):
        return self.ip_table_model

    def get_test_model(self):
        return self.test_model

    def get_test_list(self):
        return self.test_model.get_test_list()

    @QtCore.pyqtSlot(int)
    def slot_change_selected_test(self, index):
        self.selectedTest = self.test_model.get_test_list()[index]
        self.default_equipment_selection(self.selectedTest)
        #self.default_phase_selection(self.selectedTest, self.selectedEquipment)
        self.test_model.set_view_selections(self.selectedTest, self.selectedEquipment, self.selectedPhase)
        self.signal_set_equipment_list.emit(self.test_model.get_test_equipment_list(self.selectedTest))
        self.signal_set_phase_list.emit(self.phase_list)

    @QtCore.pyqtSlot(int)
    def slot_change_selected_equipment(self, index):
        equipment_list = self.test_model.get_test_equipment_list(self.selectedTest)
        self.default_equipment_selection(self.selectedTest)
        if len(equipment_list) > index and index >= 0:
            self.selectedEquipment = equipment_list[index]
        self.test_model.set_view_selections(self.selectedTest,self.selectedEquipment, self.selectedPhase)
        self.signal_set_phase_list.emit(self.phase_list)

    @QtCore.pyqtSlot(int)
    def slot_change_selected_phase(self, index):
        self.default_phase_selection(self.selectedTest, self.selectedEquipment)
        if len(self.phase_list) > index and index >= 0:
            self.selectedPhase = self.phase_list[index]
        self.test_model.set_view_selections(self.selectedTest,self.selectedEquipment, self.selectedPhase)

    def get_equipment_address(self, equipment_name):
        return self.equipment_model.get_equipment_address(equipment_name)

    def get_worker(self, addr):
        return self.equipment_model.get_worker(addr)

    def get_addr_list(self):
        return self.equipment_model.get_addr_list()

    def set_connected(self, addr, value):
        self.equipment_model.set_connected(addr, value)

    def get_equipment_idn(self, addr):
        return self.equipment_model.get_equipment_idn(addr)

    def increment_equipment(self, addr):
        return self.equipment_model.increment_equipment(addr)

    def get_next_command(self, equipment):
        if self.executionPhase is None:
            pass
        elif self.executionPhase == 'config':
            return self.test_model.get_next_config_command(equipment)
        elif self.executionPhase == 'run':
            return self.test_model.get_next_run_command(equipment)
        elif self.executionPhase == 'reset':
            return self.test_model.get_next_reset_command(equipment)
        else:
            pass
    def __del__(self):
        if self.workersInit:  
            for addr in self.get_addr_list():
                self.get_worker(addr).w_thread.terminate()
