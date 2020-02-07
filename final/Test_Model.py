from PyQt5 import QtCore, QtGui
import json

class Test_Model(QtCore.QAbstractTableModel):
    """
    data:
    {
        'test_name': Test_Object
    }
    """
    def __init__(self, parent, file, header = ['Categories', 'Commands','Parameter 1','Parameter 2','Parameter 3'], *args):
        super(Test_Model, self).__init__()
        self.data = {}
        self.load_json(file)
        self.header = header
        self.selectedTest = list(self.data)[0]
        self.selectedEquipment = None
        self.default_equipment_select()
        self.update_row_offsets()

    def default_equipment_select(self):
        if len(self.data[self.selectedTest]) == 0:
            self.selectedEquipment = None
        else:
            self.selectedEquipment = list(self.data[self.selectedTest])[0]

    def slot_selected_test_changed(self, index):
        self.selectedTest = list(self.data)[index]
        self.default_equipment_select()
        self.update_row_offsets()
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def slot_selected_equipment_changed(self, index):
        if index < 0:
            self.selectedEquipment = None
        else:
            self.selectedEquipment = list(self.data[self.selectedTest])[index]
        self.update_row_offsets()
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def update_row_offsets(self):
        self.row_offsets = []
        current_offset = 1
        self.row_offsets.append(current_offset)
        if self.selectedEquipment is not None:
            current_offset += len(self.get_selected_equipment()['config']) + 1
            self.row_offsets.append(current_offset)
            current_offset += len(self.get_selected_equipment()['run']) + 1
            self.row_offsets.append(current_offset)
            current_offset += len(self.get_selected_equipment()['reset'])
            self.row_offsets.append(current_offset)

    def load_json(self, file):
        with open(file, 'r') as infile:
            self.data = {}
            raw_data = json.load(infile)
            for item in raw_data:
                self.data[item] = Test_Object(raw_data[item]) 

    def reset_index(self, equipment):
        self.data[self.selectedTest][equipment]['index'] = -1

    def get_tests(self):
        return list(self.data)

    def get_test_equipment(self):
        return list(self.data[self.selectedTest])

    def get_num_config_commands(self, equipment):
        return len(self.data[self.selectedTest][equipment]['config'])

    def get_num_run_commands(self, equipment):
        return len(self.data[self.selectedTest][equipment]['run'])

    def get_num_reset_commands(self, equipment):
        return len(self.data[self.selectedTest][equipment]['reset'])

    def get_next_config_command(self, equipment):
        cmd = None
        cmd_type = None
        self.data[self.selectedTest][equipment]['index'] += 1
        valid_index = self.data[self.selectedTest][equipment]['index'] < self.get_num_config_commands(equipment)
        if valid_index:
            cmd_obj = self.data[self.selectedTest][equipment]['config'][self.data[self.selectedTest][equipment]['index']]
            cmd = self.get_cmd_string(cmd_obj)
            cmd_type = self.get_cmd_type(cmd_obj)
        else:
            self.reset_index(equipment)
        return cmd, cmd_type

    def get_next_run_command(self, equipment):
        cmd = None
        cmd_type = None
        self.data[self.selectedTest][equipment]['index'] += 1
        valid_index = self.data[self.selectedTest][equipment]['index'] < self.get_num_run_commands(equipment)
        if valid_index:
            cmd_obj = self.data[self.selectedTest][equipment]['run'][self.data[self.selectedTest][equipment]['index']]
            cmd = self.get_cmd_string(cmd_obj)
            cmd_type = self.get_cmd_type(cmd_obj)
        else:
            self.reset_index(equipment)
        return cmd, cmd_type

    def get_next_reset_command(self, equipment):
        cmd = None
        cmd_type = None
        self.data[self.selectedTest][equipment]['index'] += 1
        valid_index = self.data[self.selectedTest][equipment]['index'] < self.get_num_reset_commands(equipment)
        if valid_index:
            cmd_obj = self.data[self.selectedTest][equipment]['reset'][self.data[self.selectedTest][equipment]['index']]
            cmd = self.get_cmd_string(cmd_obj)
            cmd_type = self.get_cmd_type(cmd_obj)
        else:
            self.reset_index(equipment)
        return cmd, cmd_type

    def get_indexed_command(self, equipment):
        pass

    def get_cmd_string(self, cmd_obj):
        return cmd_obj['cmd'].format(*cmd_obj['args'])

    def get_cmd_type(self, cmd_obj):
        return cmd_obj['type']

    def set_equipment_param(self, equipment, p_ind, param):
        pass

    def get_selected_equipment(self):
        return self.data[self.selectedTest][self.selectedEquipment]

    def setData(self, data):
        self.data = data
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def rowCount(self, parent):
        return self.row_offsets[-1]

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        value = None
        if not index.isValid():
            return None
        if self.selectedEquipment is None:
            value = None
        elif index.column() == 0:
            if index.row() == self.row_offsets[0] - 1:
                value = list(self.get_selected_equipment())[0]
            elif index.row() == self.row_offsets[1] - 1:
                value = list(self.get_selected_equipment())[1]
            elif index.row() == self.row_offsets[2] - 1:
                value = list(self.get_selected_equipment())[2]
        elif index.column() == 1:
            if index.row() == self.row_offsets[0] - 1:
                value = None
            elif index.row() == self.row_offsets[1] - 1:
                value = None
            elif index.row() == self.row_offsets[2] - 1:
                value = None
            elif index.row() < self.row_offsets[1]:
                cmd_obj = self.get_selected_equipment()[list(self.get_selected_equipment())[0]][index.row() - self.row_offsets[0]]
                value = self.get_cmd_string(cmd_obj)
            elif index.row() < self.row_offsets[2]:
                value = self.get_selected_equipment()[list(self.get_selected_equipment())[1]][index.row() - self.row_offsets[1]]['cmd']
            else:
                value = self.get_selected_equipment()[list(self.get_selected_equipment())[2]][index.row() - self.row_offsets[2]]['cmd']
        if role == QtCore.Qt.DisplayRole:
            return value
        else:
            return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[section]
        return None

class Test_Object:
    pass
    """
    test:
        {
            equipment:
            {
                config: [...],
                run: [...],
                reset: [...]
                index: -1
            }
        }
    """
    def __init__(self, data):
        self.data = data
        for equipment in self.data:
            self.data[equipment]['index'] = -1

    def __getitem__(self, key):
        return self.data[key]
    
    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for elem in self.data:
            yield elem