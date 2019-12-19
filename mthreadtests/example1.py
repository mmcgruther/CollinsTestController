from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout
import sys
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.task = None

    def initUI(self):
        self.cmd_button = QPushButton("Push/Cancel", self)
        self.cmd_button2 = QPushButton("Push", self)
        self.cmd_button.clicked.connect(self.send_cancellable_evt)
        self.cmd_button2.clicked.connect(self.send_evt)
        self.statusBar()
        self.layout = QGridLayout()
        self.layout.addWidget(self.cmd_button, 0, 0)
        self.layout.addWidget(self.cmd_button2, 0, 1)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.show()

    def send_evt(self, arg):
        self.t1 = RunThread(self.worker, self.on_send_finished, "test")
        self.t2 = RunThread(self.worker, self.on_send_finished, 55)
        print("kicked off async tasks, waiting for it to be done")

    def worker(self, inval):
        print("in worker, received " + str(inval))
        time.sleep(2)
        return inval

    def send_cancellable_evt(self, arg):
        if not self.task:
            self.task = RunCancellableThread(None, self.on_csend_finished, "test")
            print("kicked off async task, waiting for it to be done")
        else:
            self.task.cancel()
            print("Cancelled async task.")

    def on_csend_finished(self, result):
        self.task = None  # Allow the worker to be restarted.
        print("got" + result)

    def on_send_finished(self, result):
        print("got "+ str(result) + ". Type is " + str(type(result)))


class RunThread(QtCore.QThread):
    """ Runs a function in a thread, and alerts the parent when done. 

    Uses a pyqtSignal to alert the main thread of completion.

    """
    finished = QtCore.pyqtSignal(["QString"], [int])

    def __init__(self, func, on_finish, *args, **kwargs):
        super(RunThread, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.func = func
        self.finished.connect(on_finish)
        self.finished[int].connect(on_finish)
        self.start()

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            print("e is" + str(e))
            result = e
        finally:
            if isinstance(result, int):
                self.finished[int].emit(result)
            else:
                self.finished.emit(str(result)) # Force it to be a string by default.

class RunCancellableThread(RunThread):
    def __init__(self, *args, **kwargs):
        self.cancelled = False
        super(RunCancellableThread, self).__init__(*args, **kwargs)

    def cancel(self):
        self.cancelled = True  # Use this if you just want to signal your run() function.
        # Use this to ungracefully stop the thread. This isn't recommended,
        # especially if you're doing any kind of work in the thread that could
        # leave things in an inconsistent or corrupted state if suddenly
        # terminated
        #self.terminate() 

    def run(self):
        try:
            start = cur_time = time.time()
            while cur_time - start < 10:
                if self.cancelled:
                    print("cancelled")
                    result = "cancelled"
                    break
                print("doing work in worker...")
                time.sleep(1)
                cur_time = time.time()
        except Exception as e:
            print("e is " + e)
            result = e
        finally:
            if isinstance(result, int):
                self.finished[int].emit(result)
            else:
                self.finished.emit(str(result)) # Force it to be a string by default.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    sys.exit(app.exec_())