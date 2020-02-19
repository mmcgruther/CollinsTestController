from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QMainWindow

class Equipment_Window(QMainWindow):
    def __init__(self, equipment):
        super(Equipment_Window, self).__init__()
        uic.loadUi('final/SpecAn_Config_GUI.ui', self)
        
