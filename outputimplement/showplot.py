#import pylab 
import PyQt5
import sys
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

#dummy values
colnames=["time", "voltage"] 
colval=[[1,2,3,4,5,6] , [200,20,300,45,37,56]]
app_end = [[7,8,9], [20, 30, 40]]
#function to create table and save to .csv file

#putting these values in the data dictionary
data = {}
data_1 ={}
data[colnames[0]] = colval[0]
data[colnames[1]] = colval[1]

data_1[colnames[0]]= app_end[0]
data_1[colnames[1]] = app_end[1]

#using pandas and dictionary of lists to display data
df = pd.DataFrame(data)
df1 = pd.DataFrame(data_1)
df2 = df.append(df1, ignore_index = True)

print(df2)
#df.to_csv(r'C:\Users\Demilade\Documents\4806\test1.csv')

#function to display plot

#colval will be an array with all the points on a curve
plt.plot(colval[0], colval[1])
plt.ylabel('Voltage, (V)')
plt.xlabel('Time, (s)')
#plt.show()

#plotting sine wave
x=np.arange(0,3*np.pi,0.1)
y = np.sin(x)
plt.plot(x,y)
plt.show()

