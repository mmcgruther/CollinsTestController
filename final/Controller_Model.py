from PyQt5 import QtCore, QtGui
from final import Equipment_Model, Test_Model, Visa_Worker, IP_Table_Model
from final.connection_manager import Connection_Manager
from final.worker_pool import Worker_Pool
from final.test_manager import Test_Manager
from final.output_manager import Output_Manager
import json, threading, os

class Controller_Model(QtCore.QObject):
   
    def __init__(self, parent, equipment_file, tests_file, backend):
        super(Controller_Model, self).__init__()
        self.equipment_model = Equipment_Model.Equipment_Model(equipment_file)
        self.test_model = Test_Model.Test_Model(self, tests_file)
        self.worker_pool = Worker_Pool(self, backend)
        self.connection_manager = Connection_Manager(self, self.equipment_model, self.worker_pool)
        self.output_manager = Output_Manager(self)
        self.test_manager = None
        self.selectedTest = None
        self.selectedEquipment = None
        self.selectedPhase = None
        self.pin_filename = None
        self.ploss_filename = None
        self.default_test_selection()
        self.ip_table_model = IP_Table_Model.IP_Table_Model(self, self.equipment_model.get_IP_table_data())
        self.phase_list = ['config','run','reset']
        self.parent=parent

    signal_status_message = QtCore.pyqtSignal(str, int)

    signal_set_refresh_button = QtCore.pyqtSignal(bool)
    signal_set_execute_button = QtCore.pyqtSignal(bool)
    signal_set_abort_button = QtCore.pyqtSignal(bool)
    signal_set_test_combobox = QtCore.pyqtSignal(bool)
    signal_set_equipment_combobox = QtCore.pyqtSignal(bool)
    signal_set_phase_combobox = QtCore.pyqtSignal(bool)

    signal_set_test_list = QtCore.pyqtSignal(list)
    signal_set_equipment_list = QtCore.pyqtSignal(list)
    signal_set_phase_list = QtCore.pyqtSignal(list)

    signal_set_test_index = QtCore.pyqtSignal(int)
    signal_set_equipment_index = QtCore.pyqtSignal(int)

    signal_set_pin_button_label = QtCore.pyqtSignal(str)
    signal_set_ploss_button_label = QtCore.pyqtSignal(str)

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
        """
        Triggers start of establishing equipment connections
        """
        self.signal_set_refresh_button.emit(False)
        self.signal_set_execute_button.emit(False)
        print("Main thread", threading.get_ident())
        self.connection_manager.list_resources()
        self.ip_table_model.setData(self.equipment_model.get_IP_table_data())
        

    @QtCore.pyqtSlot()
    def slot_execute_test(self):
        """
        Triggers start of test execution
        """
        self.test_manager = Test_Manager(self, self.test_model, self.equipment_model, self.worker_pool, self.selectedTest)
        try:
            if self.pin_filename is None:
                raise RuntimeError("No 'Input' file selected")
            if self.ploss_filename is None:
                raise RuntimeError("No 'Power Loss' file selected")
            test_output_params = self.get_test_lineedits()
            self.test_manager.execute_test()
        except Exception as e:
            print(e)
            self.signal_status_message.emit(e.__str__(), 5000)
        else:
            self.output_manager.init_output(test_output_params, self.pin_filename, self.ploss_filename)
            self.signal_set_refresh_button.emit(False)
            self.signal_set_execute_button.emit(False)
            self.signal_set_abort_button.emit(True)
            self.signal_set_test_combobox.emit(False)
            self.signal_set_equipment_combobox.emit(False)

    def get_test_lineedits(self):
        line_dict = {}
        line_dict["xlabel"] = self.parent.xlabel_lineedit.text()
        line_dict["ylabel"] = self.parent.ylabel_lineedit.text()
        line_dict["plot_title"] = self.parent.plot_title_in_lineedit.text()
        line_dict["cent_freq"] = self.parent.cent_freq_in_lineedit.text()
        line_dict["freq_span"] = self.parent.freq_span_in_lineedit.text()
        try:
            int(line_dict["cent_freq"])
        except:
            raise RuntimeError("Invalid center frequency")
        try:
            int(line_dict["freq_span"])
        except:
            raise RuntimeError("Invalid frequency span")
        return line_dict

    @QtCore.pyqtSlot()
    def abort_test(self):
        self.signal_set_abort_button.emit(False)
        self.test_manager.abort_test()

    @QtCore.pyqtSlot(str)
    def slot_write_success(self, addr):
        self.test_manager.next_command_by_addr(addr)

    @QtCore.pyqtSlot(str, str, int)
    def slot_query_success(self, addr, data, qID):
        print("Data received from", addr, "type:", type(data), "cmd ID:", qID)
        if len(data) != 0:
            self.output_manager.update_output(data, addr, qID)
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
        self.pin_filename = filename[0]
        self.signal_set_pin_button_label.emit("Selected Input File: " + os.path.basename(self.pin_filename))

    def set_ploss_filename(self, filename):
        self.ploss_filename = filename[0]
        self.signal_set_ploss_button_label.emit("Selected Power Loss: " + os.path.basename(self.ploss_filename))

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
