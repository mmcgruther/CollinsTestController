from PyQt5 import QtCore, QtGui
import json

class Test_Model(QtCore.QAbstractTableModel):
    """
    data:
    {
        "test":
        {
            "equipment":
            {
                "config": 
                {
                    "data_init":
                    {
                        "args": [
                            "INIT"
                        ]
                    }
                },
                run: {...},
                reset: {...},
            }
        }
    }
    """
    def __init__(self, parent, file, header = ['Commands','Parameter 1','Parameter 2','Parameter 3'], *args):
        super(Test_Model, self).__init__()
        self.data = {}
        self.load_json(file)
        self.header = header
        self.selectedTest = None
        self.selectedEquipment = None
        self.selectedPhase = None

    def set_view_selections(self, test, equipment, phase):
        self.selectedTest = test
        self.selectedEquipment = equipment
        self.selectedPhase = phase
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def load_json(self, file):
        with open(file, 'r') as infile:
            self.data = json.load(infile)

    def get_test_list(self):
        return list(self.data)

    def get_test_equipment_list(self, test):
        return list(self.data[test])

    def get_cmd_objs(self, test, equipment, phase):
        return self.data[test][equipment][phase]

    def get_num_config_commands(self, test, equipment):
        return len(self.data[test][equipment]['config'])

    def get_num_run_commands(self, test, equipment):
        return len(self.data[test][equipment]['run'])

    def get_num_reset_commands(self, test, equipment):
        return len(self.data[test][equipment]['reset'])
   
    def set_equipment_args(self, test, equipment, phase, cmd, args):
        self.data[test][equipment][phase][cmd]['args'] = args

    def get_selected_row_args(self, row):
        key_list = list(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase].keys())
        command_name = key_list[row]
        return list(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase][command_name]['args'])

    def setData(self, data):
        self.data = data
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def rowCount(self, parent):
        if self.selectedTest is None:
            return 0
        elif self.selectedEquipment is None:
            return 0
        elif self.selectedPhase is None:
            return 0
        else:
            return len(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase])

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        value = None
        if not index.isValid():
            return None
        if self.selectedEquipment is None:
            value = None
        elif index.column() == 0:
            value = list(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase])[index.row()]
        else:
            arg_list = self.get_selected_row_args(index.row())
            if index.column() > len(arg_list):
                value = None
            else:
                value = arg_list[index.column() - 1]

        if role == QtCore.Qt.DisplayRole:
            return value
        else:
            return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[section]
        return None