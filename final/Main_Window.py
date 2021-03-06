from PyQt5 import QtCore, uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QTableView, QTreeView, QComboBox, QGraphicsView, QGraphicsScene, QFileDialog, QAction, QInputDialog, QDialog, QVBoxLayout, QLineEdit, QStatusBar
from final import Controller_Model, Equipment_Window
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sys, time, json
import pandas as pd

class Main_Window(QMainWindow):
    """
    Top level object. Uses controller_model object to handle software logic. Makes Qt signal/slot connections between UI elements and their 
    functionality in controller_model
    """
    def __init__(self, equipment_file = "equipment.json", tests_file = "tests.json", backend = "@py"):
        super(Main_Window, self).__init__()
        self.controller_model = Controller_Model.Controller_Model(self, equipment_file, tests_file, backend)

        self.controller_model.signal_set_refresh_button.connect(self.slot_set_refresh_button)
        self.controller_model.signal_set_execute_button.connect(self.slot_set_execute_button)
        self.controller_model.signal_set_abort_button.connect(self.slot_set_abort_button)
        self.controller_model.signal_set_test_combobox.connect(self.slot_set_test_combobox)
        self.controller_model.signal_set_equipment_combobox.connect(self.slot_set_equipment_combobox)
        self.controller_model.signal_set_phase_combobox.connect(self.slot_set_phase_combobox)

        self.controller_model.signal_set_test_list.connect(self.slot_set_test_list)
        self.controller_model.signal_set_equipment_list.connect(self.slot_set_equipment_list)
        self.controller_model.signal_set_phase_list.connect(self.slot_set_phase_list)

        self.controller_model.signal_set_pin_button_label.connect(self.slot_set_pin_button_label)
        self.controller_model.signal_set_ploss_button_label.connect(self.slot_set_ploss_button_label)

        self.initUI()
        self.controller_model.initialize_view()

    def initUI(self):
        """Defines and connects GUI elements from .ui file"""
        uic.loadUi('final/Main_Window.ui', self)

        self.statusbar = self.findChild(QStatusBar, 'statusbar')
        self.controller_model.signal_status_message.connect(self.statusbar.showMessage)

        self.refresh_button = self.findChild(QPushButton, 'refresh_button')
        self.refresh_button.clicked.connect(self.controller_model.list_resources)

        self.gui_button = self.findChild(QPushButton, 'gui_button')
        self.gui_button.clicked.connect(self.slot_open_equipment_gui)

        self.execute_button = self.findChild(QPushButton, 'execute_button')
        self.execute_button.clicked.connect(self.controller_model.slot_execute_test)

        self.abort_button = self.findChild(QPushButton, 'abort_button')
        self.abort_button.clicked.connect(self.controller_model.abort_test)  
        self.abort_button.setEnabled(False)      

        self.ip_table_view = self.findChild(QTableView, 'ip_table_view')
        self.ip_table_view.setModel(self.controller_model.get_IP_table_model())

        self.test_tableview = self.findChild(QTableView, 'test_tableview')
        self.test_tableview.setModel(self.controller_model.get_test_model())

        self.test_combobox = self.findChild(QComboBox, 'test_combobox')
        self.test_combobox.currentIndexChanged.connect(self.controller_model.slot_change_selected_test)
        self.controller_model.signal_set_test_index.connect(self.test_combobox.setCurrentIndex)

        self.equipment_combobox = self.findChild(QComboBox, 'equipment_combobox')
        self.equipment_combobox.currentIndexChanged.connect(self.controller_model.slot_change_selected_equipment)
        self.controller_model.signal_set_equipment_index.connect(self.equipment_combobox.setCurrentIndex)

        self.phase_combobox = self.findChild(QComboBox, 'phase_combobox')
        self.phase_combobox.currentIndexChanged.connect(self.controller_model.slot_change_selected_phase)

        self.vboxlayout = self.findChild(QVBoxLayout, 'verticalLayout_3')
    
        self.figure = plt.figure(facecolor='black')        
        self.figure.set_facecolor("none")
        self.canvas = FigureCanvas(self.figure)
        self.vboxlayout.addWidget(self.canvas)

        self.canvas.draw()
        
        self.controller_model.output_manager.signal_update_canvas.connect(self.slot_update_canvas)

        self.pin_button = self.findChild(QPushButton, 'pin_button')
        self.pin_button.clicked.connect(self.slot_open_pin_dialog)

        self.ploss_button = self.findChild(QPushButton, 'ploss_button')
        self.ploss_button.clicked.connect(self.slot_open_ploss_dialog)

        self.action_new_test = self.findChild(QAction, 'action_new_test')
        self.action_new_test.triggered.connect(self.slot_add_new_test)

        self.action_new_equipment = self.findChild(QAction, 'action_new_equipment')
        self.action_new_equipment.triggered.connect(self.slot_add_new_equipment)

        self.action_new_command = self.findChild(QAction, 'action_new_command')
        self.action_new_command.triggered.connect(self.slot_add_new_command)

        self.action_exit = self.findChild(QAction, 'action_exit')
        self.action_exit.triggered.connect(self.close)

        self.xlabel_lineedit = self.findChild(QLineEdit, 'xlabel')
        self.ylabel_lineedit = self.findChild(QLineEdit, 'ylabel')
        self.plot_title_in_lineedit = self.findChild(QLineEdit, 'plot_title_in')
        self.cent_freq_in_lineedit = self.findChild(QLineEdit, 'cent_freq_in')
        self.freq_span_in_lineedit = self.findChild(QLineEdit, 'freq_span_in')

        self.showMaximized()

    @QtCore.pyqtSlot()
    def slot_add_new_command(self):
        #Dialog for new command
        command_list = self.controller_model.get_configured_equipment_command_list()
        item, ok = QInputDialog.getItem(self, "New Command", "Select Command:", command_list, 0, False)
        #Check user confirmed
        if ok:
            name, ok = QInputDialog.getText(self, "New Command", "Select command name:")
            if ok:
                self.controller_model.add_new_command(item, name)

    @QtCore.pyqtSlot()
    def slot_add_new_equipment(self):
        #Dialog for new equipment
        equipment_list = self.controller_model.get_configured_equipment_list()
        item, ok = QInputDialog.getItem(self, "New Equipment", "Select equipment:", equipment_list, 0, False)
        #Check user confirmed
        if ok:
            #Add new equipment/check valid selection
            self.controller_model.add_new_equipment(item)
                
                

    @QtCore.pyqtSlot()
    def slot_add_new_test(self):
        #Dialog for new test name
        name, ok = QInputDialog.getText(self, "New Test", "Test name:")
        #Check user confirmed
        if ok:
            #Add test/check valid name
            self.controller_model.add_new_test(name)

    def slot_update_canvas(self, fig):
        self.canvas.draw()

    @QtCore.pyqtSlot(bool)
    def slot_set_refresh_button(self, state):
        self.refresh_button.setEnabled(state)

    @QtCore.pyqtSlot(bool)
    def slot_set_execute_button(self, state):
        self.execute_button.setEnabled(state)

    @QtCore.pyqtSlot(bool)
    def slot_set_abort_button(self, state):
        self.abort_button.setEnabled(state)

    @QtCore.pyqtSlot(bool)
    def slot_set_test_combobox(self, state):
        self.test_combobox.setEnabled(state)

    @QtCore.pyqtSlot(bool)
    def slot_set_equipment_combobox(self, state):
        self.equipment_combobox.setEnabled(state)

    @QtCore.pyqtSlot(bool)
    def slot_set_phase_combobox(self, state):
        self.phase_combobox.setEnabled(state)

    @QtCore.pyqtSlot(list)
    def slot_set_test_list(self, test_list):
        self.test_combobox.clear()
        for test in test_list:
            self.test_combobox.addItem(test)


    @QtCore.pyqtSlot(list)
    def slot_set_equipment_list(self, equipment_list):
        self.equipment_combobox.clear()
        for equipment in equipment_list:
            self.equipment_combobox.addItem(equipment)

    @QtCore.pyqtSlot(list)
    def slot_set_phase_list(self, phase_list):
        self.phase_combobox.clear()
        for phase in phase_list:
            self.phase_combobox.addItem(phase)

    @QtCore.pyqtSlot()
    def slot_open_pin_dialog(self):
        self.controller_model.set_pin_filename(QFileDialog.getOpenFileName(self,"Open Power In file","~","CSV File (*.csv)"))

    @QtCore.pyqtSlot()
    def slot_open_ploss_dialog(self):
        self.controller_model.set_ploss_filename(QFileDialog.getOpenFileName(self,"Open Power Loss file","~","CSV File (*.csv)"))

    @QtCore.pyqtSlot()
    def slot_open_equipment_gui(self):
        self.dialog = Equipment_Window.Equipment_Window("string")
        self.dialog.signal_set_gui_commands.connect(self.controller_model.slot_set_test_commands)
        self.dialog.show()
        
    @QtCore.pyqtSlot(str)
    def slot_set_pin_button_label(self, label):
        self.pin_button.setText(label)

    @QtCore.pyqtSlot(str)
    def slot_set_ploss_button_label(self, label):
        self.ploss_button.setText(label)
