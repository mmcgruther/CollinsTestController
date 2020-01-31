#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 00:12:55 2019

@author: pi
"""


import visa
import numpy as np
from struct import unpack
import pylab
import time

dpo3034addr = 'TCPIP0::192.168.1.2::INSTR'
rm = visa.ResourceManager('@py')
scope = rm.open_resource(dpo3034addr, write_termination=None, read_termination='\n')
scope.encoding = 'latin_1'
scope.write("*CLS")
print(scope.query("*IDN?"))

scope.timeout = 4000
#scope.write('*RST')
scope.write('Data INIT')
scope.write('DATA:SOU CH1')
scope.write('DATA:START 1')
scope.write('DATA:STOP 4000')
scope.write('DATA:WIDTH 1')
#scope.write('DATA:ENC RPB')
scope.write('DATA:ENC ASCII')
print(scope.query("DATA?"))
print(scope.query("BUSY?"))

#scope.write('CH1:SCALE 500E-3')
#scope.write('HOR:SCA 2E-7')
#time.sleep(1)
ymult = float(scope.query('WFMPRE:YMULT?'))
yzero = float(scope.query('WFMPRE:YZERO?'))
yoff = float(scope.query('WFMPRE:YOFF?'))
xincr = float(scope.query('WFMPRE:XINCR?'))

#scope.values_format.use_binary('d',True, np.array)

#scope.write('CURVE?')

#data = scope.read_raw()

#data = scope.query_ascii_values('CURVE?', container=np.array)
data = scope.query('CURVE?')
headerlen = 2 + int(data[1])
header = data[:headerlen]
#print(data.dtype)
#ADC_wave = data[headerlen:-1]
print(len(data))
data = data.split(',')
print(len(data))
ADC_wave = np.array(list(map(float, data)))
#ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))

Volts = (ADC_wave - yoff) * ymult + yzero
    
Time = np.arange(0, xincr * len(Volts), xincr)
"""
print("Data len:",len(data),"Data:",data)
print("Time len:",len(Time),"Time:",Time)
print("Volt len:", len(Volts),"Volt:", Volts)
"""    
pylab.plot(Time, Volts)
pylab.show()
print("Closing connection")
scope.close()
rm.close()
