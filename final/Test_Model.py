from PyQt5 import QtCore, QtGui
import json

class Test_Model(QtCore.QAbstractTableModel):
    """
    Object handles loading test json configuration file, get/set test equipment/commands/parameters

    DICT STRUCTURE
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
        self.parent = parent
        self.load_json(file)
        self.header = header
        self.selectedTest = None
        self.selectedEquipment = None
        self.selectedPhase = None
        self.rowNumber = 0

    def set_view_selections(self, test, equipment, phase):           
        self.selectedTest = test
        self.selectedEquipment = equipment
        self.selectedPhase = phase
        
        if self.selectedTest is None:
            newRows = 0
        elif self.selectedEquipment is None:
            newRows = 0
        elif self.selectedPhase is None:
            newRows = 0
        else:
            newRows = len(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase])
        
        row_diff = newRows - self.rowNumber
        if row_diff > 0:
            self.insertRows(self.parent, 0, row_diff)
        if row_diff < 0:
            self.removeRows(self.parent, 0, -row_diff)
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def load_json(self, file):
        with open(file, 'r') as infile:
            self.data = json.load(infile)

    def get_test_list(self):
        return list(self.data)

    def get_test_equipment_list(self, test):
        ret_list = []
        if self.data[test] is not None:
            ret_list = list(self.data[test])
        return ret_list

    def get_cmd_objs(self, test, equipment, phase):
        return self.data[test][equipment][phase]

    def get_num_config_commands(self, test, equipment):
        return len(self.data[test][equipment]['config'])

    def get_num_run_commands(self, test, equipment):
        return len(self.data[test][equipment]['run'])

    def get_num_reset_commands(self, test, equipment):
        return len(self.data[test][equipment]['reset'])
        
    def get_num_args(self, test, equipment, phase, command):
        num = None
        if test and equipment and phase and command:
            num = len(self.data[test][equipment][phase][command]['args'])
        return num
   
    def set_equipment_args(self, test, equipment, phase, cmd, args):
        self.data[test][equipment][phase][cmd]['args'] = args

    def get_selected_row_args(self, row):
        key_list = list(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase].keys())
        command_name = key_list[row]
        return list(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase][command_name]['args'])

    def is_test(self, testName):
        if testName in self.data.keys():
            return True
        else:
            return False

    def is_equipment(self, test, equipment):
        if equipment in self.data[test].keys():
            return True
        else:
            return False

    def append_new_test(self, testName):
        self.data[testName] = {}

    def append_new_equipment(self, test, equipment):
        self.data[test][equipment] = {"config": {}, "run": {}, "reset": {}}

    def append_new_command(self, test, equipment, phase, cmdName, command, args = []):
        newCommand = {"name": command, "args": args}
        if cmdName not in self.data[test][equipment][phase].keys():
            self.data[test][equipment][phase][cmdName] = newCommand
            self.insertRows(self.parent, 0, 1)
            self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def set_command(self, test, equipment, phase, cmdName, command, args):
        if cmdName in self.data[test][equipment][phase].keys():
            self.data[test][equipment][phase][cmdName]['args'] = args
        else:
            self.append_new_command(test, equipment, phase, cmdName, command, args)


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

    def insertRows(self, parent, row, count):
        first = row
        last = row + count - 1
        self.beginInsertRows(QtCore.QModelIndex(), first, last)
        self.endInsertRows()
        self.rowNumber += count

    def removeRows(self, parent, row, count):
        first = row
        last = row + count - 1
        self.beginRemoveRows(QtCore.QModelIndex(), first, last)
        self.endRemoveRows()
        self.rowNumber -= count

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

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return False
            else:
                command = list(self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase])[index.row()]
                numArgs = self.get_num_args(self.selectedTest,self.selectedEquipment,self.selectedPhase,command)
                if numArgs > (index.column() - 1):
                    self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase][command]['args'][index.column() - 1] = value
                    return True
                else:
                    self.data[self.selectedTest][self.selectedEquipment][self.selectedPhase][command]['args'].append(value)
                    return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEditable
        if index.column() == 0:
            return QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[section]
        return None