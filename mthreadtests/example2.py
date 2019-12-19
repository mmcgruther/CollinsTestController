from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QLineEdit
import sys, time, threading, json

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.task = None

    def initUI(self):
        self.statusBar = self.statusBar()
        self.layout_equipment("equipment1.json")
        self.start_button = QPushButton("Start", self)
        self.abort_button = QPushButton("Abort", self)
        self.layout.addWidget(self.start_button, self.next_y, self.next_x)
        self.layout.addWidget(self.abort_button, self.next_y, self.next_x+1)
        self.next_y += 1
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.show()

        self.workerthread = QtCore.QThread()
        self.workerthread.start()

        self.workerObj = WorkerObj(self.worker, "this is an arg")
        print("main ", threading.get_ident())
        self.workerObj.call_stop_f.connect(self.workerObj.stop_f)
        self.workerObj.call_start_f.connect(self.workerObj.start_f)
        self.workerObj.call_stop_f.emit()

        self.workerObj.moveToThread(self.workerthread)

        self.workerObj.call_stop_f.emit()
        self.start_button.clicked.connect(self.push_start)
        self.abort_button.clicked.connect(self.push_stop)
        self.workerObj.abort_complete_f.connect(self.abort_complete)

    def worker(self, inval):
        print(threading.get_ident(), "in worker, received " + str(inval))
        time.sleep(2)
        return inval


    @QtCore.pyqtSlot()
    def push_start(self):
        self.workerObj.stopped.clear()
        self.workerObj.call_start_f.emit()

    @QtCore.pyqtSlot()
    def push_stop(self):
        self.workerObj.stopped.set()
        self.workerObj.call_stop_f.emit()
        self.statusBar.showMessage("Aborting...")
        self.start_button.setEnabled(False)
        self.abort_button.setEnabled(False)

    @QtCore.pyqtSlot()
    def abort_complete(self):
        self.start_button.setEnabled(True)
        self.abort_button.setEnabled(True)
        self.statusBar.showMessage("Abort Complete", 1000)
        

    def on_csend_finished(self, result):
        self.task = None  # Allow the worker to be restarted.
        print("got" + result)

    def on_send_finished(self, result):
        print("got "+ str(result) + ". Type is " + str(type(result)))

    def layout_equipment(self, equipment_file):
        infile = open(equipment_file, 'r')
        json_obj = json.load(infile)
        print(json_obj)
        self.setWindowTitle(json_obj['name'])
        self.address = json_obj['address']
        self.layout = QGridLayout()
        self.buttons = []
        self.next_x = 0
        self.next_y = 0
        self.commands = []

        for objects in json_obj:
            value = json_obj[objects]
            if type(value) is dict:
                method_name = value['method']
                method = getattr(self, method_name, lambda *args: print(objects, ": Bad method name"))
                method(value['name'], value['command'])
    
    def set_lineedit(self, name, command_str, *args):
        print("set lineedit: ", str(args))
        label = QLabel(name, self)
        lineedit = QLineEdit("0", self)
        self.layout.addWidget(label, self.next_y, self.next_x)
        self.layout.addWidget(lineedit, self.next_y, self.next_x + 1)
        self.next_y += 1


class WorkerObj(QtCore.QObject):
    def __init__(self, func, *args, **kwargs):
        super(WorkerObj, self).__init__()

        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.stopped = threading.Event()

    call_stop_f = QtCore.pyqtSignal()
    call_start_f = QtCore.pyqtSignal()
    abort_complete_f = QtCore.pyqtSignal()

    @QtCore.pyqtSlot()
    def stop_f(self):
        #self.func(*self.args, **self.kwargs)
        print("stop_f ", threading.get_ident(), " stop reached")
        self.abort_complete_f.emit()

    @QtCore.pyqtSlot()
    def start_f(self):
        if not self.stopped.is_set():
            self.func(*self.args, **self.kwargs)
            print("start_f ", threading.get_ident(), " sleeping")
            time.sleep(1)
            print("woke")
        else:
            print("start_f aborted ", threading.get_ident())
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    sys.exit(app.exec_())