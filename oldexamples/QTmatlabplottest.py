#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 06:07:28 2019

@author: pi
"""

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random

def btn_clicked():
    print ("Button Pressed")
    
    

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = "Test title here"
        self.width = 640
        self.height = 400
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        m = PlotCanvas(self, width = 5, height = 4)
        m.move(0,0)
        
        button = QPushButton('Test Button', self)
        button.setToolTip('Tool tip here')
        button.move(500,0)
        button.resize(140,100)
        button.clicked.connect( btn_clicked )
        self.show()
        
class PlotCanvas(FigureCanvas):
    data = [random.random() for i in range(25)]
    def __init__(self, parent, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width,height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()
        
    def plot(self):
        ax = self.figure.add_subplot(111)
        ax.plot(self.data, 'r-')
        ax.set_title('ax title')
        self.draw()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())