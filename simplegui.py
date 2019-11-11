import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout

class GUI(QMainWindow):


	def __init__(self):
		QWidget.__init__(self)
		self.setGeometry(1000,200,2400,1600)
		self.setWindowTitle("M.A.D. Power RF Test Controller")
		self.dmm()

		self.label = QLabel("Modes",self)
		self.label.move(550,100)
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.label)
		self.setLayout(self.layout)


#Defines dmm as part of self structure
#Creates the 5 buttons for the 5 different relevant modes of the DMM
	def dmm(self):		
		button1 = QPushButton("Volts DC", self)
		button1.clicked.connect(self.vdc) #If the button is pressed, the vdc member activates
		button1.resize(300,100)
		button1.move(200,200)

		button2 = QPushButton("Volts AC", self)
		button2.clicked.connect(self.vac)
		button2.resize(300,100)
		button2.move(200,450)

		button3 = QPushButton("Amps DC", self)
		button3.clicked.connect(self.adc)
		button3.resize(300,100)
		button3.move(700,200)

		button4 = QPushButton("Amps AC", self)
		button4.clicked.connect(self.aac)
		button4.resize(300,100)
		button4.move(700,450)

		button5 = QPushButton("Resistance", self)
		button5.clicked.connect(self.ohms)
		button5.resize(300,100)
		button5.move(200,700)


				
	def vdc(self):
		print("Volts DC")
	def vac(self):
		print("Volts AC")
	def adc(self):
		print("Amps DC")
	def aac(self):
		print("Amps AC")
	def ohms(self):
		print("Resistance")




if __name__ == '__main__':
	app = QApplication([])
	gui = GUI()
	gui.show()
	sys.exit(app.exec_())
