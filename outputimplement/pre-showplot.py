from PyQt5 import QtCore, uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit,QPushButton, QWidget, QTableView, QTreeView, QComboBox, QGraphicsView, QGraphicsScene, QFileDialog, QAction, QInputDialog, QDialog, QVBoxLayout
import sys
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from csv import writer 

#convert string input array into integers for display
#create the plot in the GUI canvas space and not plot.show

class output(QtGui.QWidget):

    def __init__(self):
        data = {}
        self.df = pd.DataFrame(data)
        uic.loadUi('final/Main_Window.ui', self)
        self.xlabel=QtGui.QLineEdit('xlabel', self)

    def draw_table(self, colnames, colval):
        data_1 = {}
        n=0
        for c in colnames:
            data_1[c] = colval[n]
            n=n+1

        df1 = pd.DataFrame(data_1)
        self.df = self.df.append(df1, ignore_index = True)

        return self.df

    def draw_plot(self, colnames, xval,data_val):
        plt.plot(xval,data_val)
        plt.xlabel(colnames[0])
        plt.ylabel(colnames[1])
        plt.show()
    
    def save_data(self,file_name, final): #pass the dic final to this function after last call
        #final.to_csv(r'C:\Users\Demilade\Documents\4806\test1.csv')
        with open(file_name, 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(final)


#sample main
d = output()
colnames = ["xval","yval"]
colvalue = [[1,2,3],[20,30,40]]
plot_sampx = [1,2,3,4,5,6,7,8,9,10]
plot_sampy = [100,200,300,400,500,600,700,800,900,1000]

for r in range(2):
    d_1=d.draw_table(colnames, colvalue)

print(d_1)
d.draw_plot(colnames, plot_sampx,plot_sampy)
for r in range(3):
    d.save_data('test1.csv',plot_sampy)


