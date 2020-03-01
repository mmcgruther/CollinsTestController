from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QMainWindow, QDialogButtonBox, QRadioButton, QDoubleSpinBox

class Equipment_Window(QMainWindow):
    def __init__(self, equipment):
        super(Equipment_Window, self).__init__()
        uic.loadUi('final/SpecAn_Config_GUI.ui', self)

        self.dialog_buttons = self.findChild(QDialogButtonBox, 'buttonBox')
        self.dialog_buttons.accepted.connect(self.get_commands)
        self.dialog_buttons.rejected.connect(self.close)


    signal_set_gui_commands = QtCore.pyqtSignal(list)

    @QtCore.pyqtSlot()
    def get_commands(self):
        GUI_data = []
        state = self.findChild(QRadioButton, 'radioButton').isChecked()
        name = "Set Center Frequency"#Should match existing name in tests.json
        value = [self.findChild(QDoubleSpinBox, 'doubleSpinBox').text()]#list of parameters [1]
        phase = 'config'#Match phase from tests.json
        cmd = "set_center_freq"#Needs to match equipment.json command
        #list of tuples: (phase, cmdName, cmd, args)
        if state:
            GUI_data.append((phase, name, cmd, value))

        self.signal_set_gui_commands.emit(GUI_data)
        self.close()

