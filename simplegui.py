import sys
from PyQt5.QtCore import QTimer
from PyQt5 import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QLineEdit
from DM3068 import DM3068

class GUI(QMainWindow):


    def __init__(self):
        QMainWindow.__init__(self)
        self.setGeometry(0,0,800,600)
        self.setWindowTitle("M.A.D. Power RF Test Controller")
        self.dmm()
        
        self.label = QLabel("Modes",self)
        self.label.move(100,50)
        
        self.mode = QLabel("No Mode Selected",self)
        self.mode.resize(250,30)
        self.mode.move(500,270)
        
        self.reading = QLineEdit("0",self)
        self.reading.setAlignment(Qt.Qt.AlignHCenter)
        self.reading.resize(250,50)
        self.reading.move(500, 300)
        self.rigol = DM3068()
        self.rigol.connect()
        
        self.timer = QTimer(self)
        self.timer.start(250)
        self.timer.timeout.connect(self.timercallback)
        
        self.func = None
        self.readunits = None
        
        print(self.rigol.query())


#Defines dmm as part of self structure
#Creates the 5 buttons for the 5 different relevant modes of the DMM
    def dmm(self):        
        button1 = QPushButton("Volts DC", self)
        button1.clicked.connect(self.vdc) #If the button is pressed, the vdc member activates
        button1.resize(150,100)
        button1.move(100,100)

        button2 = QPushButton("Volts AC", self)
        button2.clicked.connect(self.vac)
        button2.resize(150,100)
        button2.move(100,250)

        button3 = QPushButton("Amps DC", self)
        button3.clicked.connect(self.adc)
        button3.resize(150,100)
        button3.move(300,100)

        button4 = QPushButton("Amps AC", self)
        button4.clicked.connect(self.aac)
        button4.resize(150,100)
        button4.move(300,250)

        button5 = QPushButton("Resistance", self)
        button5.clicked.connect(self.ohms)
        button5.resize(150,100)
        button5.move(100,400)
        
    def timercallback(self):
        if self.func != None:
            print(self.func.__name__)
            value = self.func()
            self.reading.setText("{:.4f}".format(float(value))+ " " + self.readunits)
            
                
    def vdc(self):
        self.mode.setText("Voltage DC:")
        self.func = self.rigol.measureVDC
        self.readunits = "V"
        self.timercallback()
        
    def vac(self):
        print("Volts AC")
    def adc(self):
        self.mode.setText("Current DC:")
        self.func = self.rigol.measureIDC
        self.readunits = "A"
        self.timercallback()
    def aac(self):
        print("Amps AC")
    def ohms(self):
        self.mode.setText("Resistance:")
        self.func = self.rigol.measureRES
        self.readunits = "\u03A9"
        self.timercallback()




if __name__ == '__main__':
    app = QApplication([])
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
