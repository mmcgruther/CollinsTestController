from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
import sys, time, threading
from final.worker_pool import Worker_Pool
from final.Equipment_Model import Equipment_Model
from final.Test_Model import Test_Model

"""

Functions:

Signals:

Slots:

Variables:

"""
class Test_Manager(QtCore.QObject):
    def __init__(self, parent, test_model, equipment_model, worker_pool, selectedTest):
        super(Test_Manager, self).__init__()
        self.parent = parent
        self.test_model = test_model
        self.equipment_model = equipment_model
        self.worker_pool = worker_pool
        self.selectedTest = selectedTest
        self.timer = QTimer(self)
        self.runRepetitions = 10
        self.configdelay = 500
        self.runPeriod = 2000
        self.runCounter = 0
        self.timer.timeout.connect(self.timer_callback)

    def execute_test(self):
        self.test_equipment_addr = {}
        test_equipment_list = self.test_model.get_test_equipment_list(self.selectedTest)
        for equipment in test_equipment_list:
            addr = self.equipment_model.get_equipment_address(equipment)
            self.test_equipment_addr[equipment] = addr
            if addr is None:
                #Error: equipment not connected
                raise Exception(equipment + " not connected")
        self.workersResponded = 0
        print("Main thread starting test", threading.get_ident())
        for equipment in self.test_model.get_test_equipment_list(self.selectedTest):
            self.worker_pool.get_worker(self.test_equipment_addr[equipment]).signal_start.emit()
        self.start_test_phase('config')

    def start_test_phase(self, phase):
        self.executionPhase = phase
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

    def next_command_by_addr(self, addr):
        equipment = list(self.test_equipment_addr.keys())[list(self.test_equipment_addr.values()).index(addr)]
        self.next_command(equipment)

    def next_command(self, equipment):
        self.test_index_by_equipment[equipment] += 1
        if self.test_index_by_equipment[equipment] >= len(self.cmd_tuple_lists_by_equipment[equipment]):
            #Current phase complete, wait for other equipment
            self.test_responded()
        else:
            addr = self.test_equipment_addr[equipment]
            cmd, cmd_type =self.cmd_tuple_lists_by_equipment[equipment][self.test_index_by_equipment[equipment]]
            qID = self.test_index_by_equipment[equipment]
            if cmd_type == 'w':
                self.worker_pool.get_worker(addr).signal_write.emit(cmd)
            elif cmd_type == 'q':
                self.worker_pool.get_worker(addr).signal_query.emit(cmd, qID)

    def test_responded(self):
        """Tracks when worker threads have completed test phase"""
        self.workersResponded += 1
        if self.workersResponded == len(self.test_equipment_addr):
            if self.executionPhase == 'config':
                
                self.workersResponded = 0
                print("Config complete")
                self.timer.setInterval(self.configdelay)
                self.timer.start()
                self.runCounter = 0

            elif self.executionPhase == 'run':
                self.runCounter += 1
                print("Run iteration", self.runCounter, "complete")
                if self.runRepetitions > self.runCounter:
                    self.workersResponded = 0
                    
                else:
                    self.timer.stop()
                    print("End of", self.executionPhase, "phase")
                    self.executionPhase = 'reset'
                    self.workersResponded = 0
                    print("Starting reset phase")
                    self.start_test_phase(self.executionPhase)

            elif self.executionPhase == 'reset':
                print("End of test")
                self.parent.end_test()

    def abort_test(self):
        print("Main thread aborting test", threading.get_ident())
        for equipment in self.test_model.get_test_equipment_list(self.selectedTest):
            self.worker_pool.get_worker(self.test_equipment_addr[equipment]).signal_stop.emit()

    def timer_callback(self):
        if self.executionPhase == 'config':
            self.executionPhase = 'run'
            self.timer.setInterval(self.runPeriod)
            print("Begin run phase")
        
        self.start_test_phase(self.executionPhase)
