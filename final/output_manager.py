import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PyQt5 import QtCore, QtGui
from csv import writer 
from PyQt5.QtWidgets import QLineEdit
class Output_Manager(QtCore.QObject):
    def __init__(self, parent):
        super(Output_Manager, self).__init__()
        self.parent = parent
        self.df = pd.DataFrame({})

    signal_update_canvas = QtCore.pyqtSignal(object)

    def init_output(self, params,pin_file, ploss_file):
        #params is a dictionary of text from GUI line edits. Ie: params["xlabel"]
        self.params = params
        self.pin_file = pin_file
        self.ploss_file = ploss_file 
        self.plot_data = []
        self.df = pd.DataFrame(columns=["Peak Frequency", "Peak Amplitude"])
        self.figure = plt.gcf()
        self.subplot1 = self.figure.add_subplot(211)
        self.subplot2 = self.figure.add_subplot(212)
        print(self.params)
    """def draw_table(self, colnames, colval):
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
        plt.show()"""
    
    def save_data(self,file_name, final): #pass the dic final to this function after last call
        #final.to_csv(r'C:\Users\Demilade\Documents\4806\test1.csv')
        with open(file_name, 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(final)

    def update_output(self, str_data, addr, qID):
        if qID == 0:
            self.subplot1.cla()
            data_split = str_data.split(',')
            data_array = np.array(list(map(float, data_split[1:])))
            self.subplot1.plot(data_array)
            start = int(self.params['cent_freq'])-0.5*int(self.params['freq_span'])
            stop =  int(self.params['cent_freq'])+0.5*int(self.params['freq_span'])
            self.subplot1.set_xlim(start, stop)
            for i in self.params:
                if(i=='xlabel'):
                    self.subplot1.set_xlabel(self.params[i])
                if(i=='ylabel'):
                    self.subplot1.set_ylabel(self.params[i])
                if(i=='plot_title'):
                    self.subplot1.set_title(self.params[i])
            self.plot_data.append(data_array)

        if qID == 1:
            self.subplot2.cla()
            data_split = str_data.split(',')
            data_array = np.array(list(map(float, data_split)))
            table = pd.DataFrame({"Peak Frequency": [data_array[0]], "Peak Amplitude": [data_array[1]]})
            self.df = self.df.append(table, ignore_index=True)

            #print(self.df)
            cell_text = []
            for row in range(len(self.df)):
                cell_text.append(self.df.iloc[row])
            self.subplot2.table(cellText=cell_text, colLabels=self.df.columns, loc='center')
            self.subplot2.axis('off')

        self.signal_update_canvas.emit(self.figure)
    
