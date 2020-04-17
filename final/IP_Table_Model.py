from PyQt5 import QtCore, QtGui

class IP_Table_Model(QtCore.QAbstractTableModel):
    """
    Model used by QTableView for equipment connection info
    """

    def __init__(self, parent, data, header = ['Address', 'Equipment ID'], *args):
        super(IP_Table_Model, self).__init__()
        self.data = data
        self.header = header

    def setData(self, data):
        self.data = data
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def rowCount(self, parent):
        return len(self.data[0])

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return None
        if index.column() == 0:
            value = self.data[0][index.row()]
        elif index.column() == 1:
            if self.data[2][index.row()] == 1:
                value = self.data[1][index.row()]
            else:
                value = None
        if role == QtCore.Qt.DisplayRole:
            return value
        elif role == QtCore.Qt.ForegroundRole:
            if self.data[2][index.row()] == 1:
                return QtGui.QBrush(QtGui.QColor('green'))
            elif self.data[2][index.row()] == 2:
                return QtGui.QBrush(QtGui.QColor('gray'))
            else:
                return QtGui.QBrush(QtGui.QColor('red'))
        else:
            return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[section]
        return None