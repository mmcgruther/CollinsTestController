from PyQt5 import QtCore, QtGui
from final import Equipment_Model, Test_Model, Visa_Worker, IP_Table_Model
from final.connection_manager import Connection_Manager
from final.worker_pool import Worker_Pool
from final.test_manager import Test_Manager
import json, threading
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

"""
TODO:
    -Create Output Manager to format data output per test
    -Get csv file data for output manager
    -Create tabbed window for Test config

    -Documentation
    -Refactor Connections out of Equipment_Model
    -Rename Controller Model?
"""

class Controller_Model(QtCore.QObject):
   
    def __init__(self, parent, equipment_file, tests_file, backend):
        super(Controller_Model, self).__init__()
        self.equipment_model = Equipment_Model.Equipment_Model(equipment_file)
        self.test_model = Test_Model.Test_Model(self, tests_file)
        self.worker_pool = Worker_Pool(self, backend)
        self.connection_manager = Connection_Manager(self, self.equipment_model, self.worker_pool)
        self.test_manager = None
        self.selectedTest = None
        self.selectedEquipment = None
        self.selectedPhase = None
        self.default_test_selection()
        self.ip_table_model = IP_Table_Model.IP_Table_Model(self, self.equipment_model.get_IP_table_data())
        self.phase_list = ['config','run','reset']


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
        self.test_model.append_new_command(self.selectedTest, self.selectedEquipment, self.selectedPhase, commandName, command)


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
        self.signal_set_refresh_button.emit(False)
        self.signal_set_execute_button.emit(False)
        print("Main thread", threading.get_ident())
        self.connection_manager.list_resources()
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())
        

    @QtCore.pyqtSlot()
    def slot_execute_test(self):
        """Starts sending test commands to workers"""
        self.test_manager = Test_Manager(self, self.test_model, self.equipment_model, self.worker_pool, self.selectedTest)
        try:
            self.test_manager.execute_test()
        except Exception as  e:
            print(e)
        else:
            self.init_output()
            self.signal_set_refresh_button.emit(False)
            self.signal_set_execute_button.emit(False)
            self.signal_set_abort_button.emit(True)
            self.signal_set_test_combobox.emit(False)
            self.signal_set_equipment_combobox.emit(False)

    @QtCore.pyqtSlot()
    def abort_test(self):
        self.signal_set_abort_button.emit(False)
        print("Main thread aborting test", threading.get_ident())
        for equipment in self.test_model.get_test_equipment_list(self.selectedTest):
            self.worker_pool.get_worker(self.test_equipment_addr[equipment]).signal_stop.emit()

    def init_output(self):
        self.plot_data = []
        self.df = pd.DataFrame(columns=["Peak Frequency", "Peak Amplitude"])
        self.figure = plt.gcf()
        self.subplot1 = self.figure.add_subplot(211)
        self.subplot2 = self.figure.add_subplot(212)

    def update_output(self, str_data, addr, qID):
        """
        TODO: 
        -Create Output Manager to format data output per test
        """

        if qID == 0:
            self.subplot1.cla()
            data_split = str_data.split(',')
            data_array = np.array(list(map(float, data_split[1:])))
            self.subplot1.plot(data_array)
            self.plot_data.append(data_array)

        if qID == 1:
            self.subplot2.cla()
            data_split = str_data.split(',')
            data_array = np.array(list(map(float, data_split)))
            table = pd.DataFrame({"Peak Frequency": [data_array[0]], "Peak Amplitude": [data_array[1]]})
            self.df = self.df.append(table, ignore_index=True)

            #print(self.df)
            cell_text = []
            for row in range(len(self.df)):
                cell_text.append(self.df.iloc[row])
            self.subplot2.table(cellText=cell_text, colLabels=self.df.columns, loc='center')
            self.subplot2.axis('off')

        self.signal_update_canvas.emit(self.figure)

    @QtCore.pyqtSlot(str)
    def slot_write_success(self, addr):
        self.test_manager.next_command_by_addr(addr)

    @QtCore.pyqtSlot(str, str, int)
    def slot_query_success(self, addr, data, qID):
        print("Data received from", addr, "type:", type(data), "cmd ID:", qID)
        if len(data) != 0:
            self.update_output(data, addr, qID)
        self.test_manager.next_command_by_addr(addr)

    @QtCore.pyqtSlot(str, str)
    def slot_error(self, addr, cmd):
        print("Error from:", addr, "with command:", cmd)
        self.abort_test()
        self.test_manager.next_command_by_addr(addr)

    def connection_responded(self, complete = False):
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())
        if complete:
            self.signal_set_refresh_button.emit(True)
            self.signal_set_execute_button.emit(True)

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

    def get_addr_list(self):
        return self.equipment_model.get_addr_list()

    @QtCore.pyqtSlot(list)
    def slot_set_test_commands(self, cmdTupleList):
        #list of tuples: (phase, cmdName, cmd, args)
        for phase, cmdName, cmd, args in cmdTupleList:
            self.test_model.set_command(self.selectedTest, self.selectedEquipment, self.selectedPhase, cmdName, cmd, args)
