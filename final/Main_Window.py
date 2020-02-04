from PyQt5 import QtCore, uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QTableView, QTreeView, QComboBox, QGraphicsView, QGraphicsScene
from final import Controller_Model
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys, time, json

class Main_Window(QMainWindow):
    def __init__(self, equipment_file = "equipment.json", tests_file = "tests.json", backend = "@py"):
        super(Main_Window, self).__init__()
        self.controller_model = Controller_Model.Controller_Model(self, equipment_file, tests_file, backend)

        self.controller_model.signal_set_refresh_button.connect(self.slot_set_refresh_button)
        self.controller_model.signal_set_execute_button.connect(self.slot_set_execute_button)
        self.controller_model.signal_set_abort_button.connect(self.slot_set_abort_button)
        self.controller_model.signal_set_test_combobox.connect(self.slot_set_test_combobox)
        self.controller_model.signal_set_equipment_combobox.connect(self.slot_set_equipment_combobox)

        self.controller_model.signal_set_equipment_list.connect(self.slot_set_equipment_list)

        self.initUI()

    def initUI(self):
        """Lay out main window"""
        uic.loadUi('final/Main_Window.ui', self)

        self.refresh_button = self.findChild(QPushButton, 'refresh_button')
        self.refresh_button.clicked.connect(self.controller_model.list_resources)

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
        for test in self.controller_model.get_tests():
            self.test_combobox.addItem(test)
        self.test_combobox.currentIndexChanged.connect(self.controller_model.slot_change_selected_test)

        self.equipment_combobox = self.findChild(QComboBox, 'equipment_combobox')
        self.test_combobox.currentIndexChanged.emit(0)
        self.equipment_combobox.currentIndexChanged.connect(self.controller_model.slot_selected_equipment_changed)

        self.graphics_view = self.findChild(QGraphicsView, 'graphics_view')
        figure = Figure()
        axes = figure.gca()
        axes.set_title("title")
        canvas = FigureCanvas(figure)
        scene = QGraphicsScene(self.graphics_view)
        scene.addWidget(canvas)
        self.graphics_view.setScene(scene)
        self.show()

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

    @QtCore.pyqtSlot(list)
    def slot_set_equipment_list(self, equipment_list):
        self.equipment_combobox.clear()
        for equipment in equipment_list:
            self.equipment_combobox.addItem(equipment)