import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PyQt5 import QtCore, QtGui
from csv import writer 
from csv import reader
from PyQt5.QtWidgets import QLineEdit


class Output_Manager(QtCore.QObject):
    def __init__(self, parent):
        super(Output_Manager, self).__init__()
        self.parent = parent
        self.df = pd.DataFrame({})

    signal_update_canvas = QtCore.pyqtSignal(object)

    #This function initializes the parameters needed
    #for drawing tables and plotting graphs. 
    def init_output(self, params,pin_file, ploss_file):
        #params is a dictionary of text from GUI line edits. Ie: params["xlabel"]
        self.params = params
        self.pin_file = pin_file#Input file name 
        self.ploss_file = ploss_file #Power loss file name
        self.plot_data = []
        self.figure = plt.gcf()
        self.subplot1 = self.figure.add_subplot(311)
        self.subplot2 = self.figure.add_subplot(312)
        self.subplot3 = self.figure.add_subplot(313)
        self.a = 0
        self.arr1 = []
        self.arr2 = []
        self.df = pd.DataFrame({})
        self.subplot3.cla()
        
        
    #This function parses the Power in values from the input
    #value files, converts the string values to integers
    #and returns an array of the Power In integers
    def parse_pin(self):
        arr = []
        with open(self.pin_file, newline='') as csv_file:
            pin_vals = reader(csv_file, delimiter='\n')
            for vals in pin_vals:
                strings = [str(lilval) for lilval in vals]
                a_string = "".join(strings)
                a_string = a_string.split(',')
                #print(a_string[0])
                an_integer = int(a_string[1])
                arr.append(an_integer)
        return arr 

    #This function parses the Frequency values from the input
    #value files, converts the string values to integers
    #and returns an array('arr') of the Frequency integers
    def parse_freq(self):
        arr = []
        with open(self.pin_file, newline='') as csv_file:
            pin_vals = reader(csv_file, delimiter='\n')
            for vals in pin_vals:
                strings = [str(lilval) for lilval in vals]
                a_string = "".join(strings)
                a_string = a_string.split(',')
                an_integer = int(a_string[0])
                arr.append(an_integer)
        return arr       

    #This function parses the Power loss values from the power loss
    #values file, converts the string values to integers
    #and returns an array of the Power Loss integers
    def parse_ploss(self):
        arr = []
        with open(self.ploss_file, newline='') as csv_file:
            ploss_vals = reader(csv_file, delimiter='\n')
            for vals in ploss_vals:
                strings = [str(lilval) for lilval in vals]
                a_string = "".join(strings)
                an_integer = int(a_string)
                arr.append(an_integer)
        return arr       
        
    #this function saves the data from the created table to 
    #a .csv file
    def save_data(self,file_name, final):
        with open(file_name, 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(final)

    #this is the main output configuration function.When qID = 0 
    #the function receives all the data points that the equipment 
    #sends and plots it on the GUI output section.
    #When qID = 1, The function fills a table with the peak output
    # values and their corresponding frequencies that the test equipment sends.
    #These peak output values are saved to the output .csv file. 
    def update_output(self, str_data, addr, qID):
        if qID == 0:
            self.subplot1.cla()
            data_split = str_data.split(',')
            data_array = np.array(list(map(float, data_split[1:])))
            #using the input parameters from the GUI to configure the 
            #axis of the plot
            start = (int(self.params['cent_freq'])-0.5*int(self.params['freq_span'])) * 10**6#start frequency in MHz
            stop =  (int(self.params['cent_freq'])+0.5*int(self.params['freq_span'])) * 10**6#stop  frequency in MHz
            step = (stop-start)/len(data_array)
            x = np.arange(start, stop, step)
            self.subplot1.plot(x,data_array)
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
            #adding the power loss values to the Pout
            p_loss = self.parse_ploss()
            p_in = self.parse_pin()
            freq = self.parse_freq()
            p_meas = data_array[1] #measured power out
            p_out = p_meas + p_loss[self.a]#peak amplitude
            p_in_out = p_in[self.a]-p_out
            data_array[0] = data_array[0]/1000000
            #creating the output table with necessary columns
            table = pd.DataFrame({"Peak Frequency(MHz)": [freq[self.a]], "Power In(dB)": [p_in[self.a]],"Power Measured(dB)": [p_meas], "Power Loss": [p_loss[self.a]],  "Peak Amplitude(dB)": [p_out], "Pin-Pout": [p_in_out]})
            self.save_data('power_out.csv', table.values)
            self.df = self.df.append(table, ignore_index=True)
            cell_text = []
            for row in range(len(self.df)):
                cell_text.append(self.df.iloc[row])
            self.subplot2.table(cellText=cell_text, colLabels=self.df.columns, loc='center')
            self.subplot2.axis('off')

            #creating Pin vs Pout plot with a legend and axes labels for different frequencies 
            last_color = None

            if(freq[self.a] != freq[self.a-1]):
                self.arr1.clear()
                self.arr2.clear()
            elif self.a != 0:
                last_color = self.lastline.get_color()
                self.subplot3.lines.remove(self.lastline)

            self.arr1.append(p_in[self.a])
            self.arr2.append(p_out)
            
            self.lastline, = self.subplot3.plot(self.arr1, self.arr2)
            if last_color is not None:
                self.lastline.set_color(last_color)
            self.lastline.set_label(str(freq[self.a])+" MHz")
            self.subplot3.legend()

            self.subplot3.set_xlabel('Power In(dB)')
            self.subplot3.set_ylabel('Power Out(dB)')
            self.subplot3.set_title('Plot of Power In vs Power Out values')
            self.a = self.a + 1

        self.signal_update_canvas.emit(self.figure)
    
