#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:42:36 2019

@author: pi
"""

import time, warnings
import visa

class DM3068():
    
    def __init__(self, addr = 'TCPIP0::192.168.1.3'):
        self.addr = addr
        self.rm = visa.ResourceManager('@py')
    
    def connect(self):
        self.dmm = self.rm.open_resource(self.addr)
    
    def query(self):
        return self.dmm.query("*IDN?")
    
    def disconnect(self):
        self.dmm.close()
        self.rm.close()
        
    def configDC(self):
        self.dmm.write('CONF:VOLT:DC')
        
    def configRES(self):
        self.dmm.write('CONF:RES')
        
    def measureVDC(self):
        return self.dmm.query('MEAS:VOLT:DC?')
    
    def measureVAC(self):
        return self.dmm.query('MEAS:VOLT:AC?')
    
    def measureIDC(self):
        return self.dmm.query('MEAS:CURR:DC?')
    
    def measureIAC(self):
        return self.dmm.query('MEAS:CURR:AC?')    
        
    def measureRES(self):
        return self.dmm.query('MEAS:RES?')
    
    def readtest(self):
        self.dmm.write('CONF:RES 200')
        self.dmm.write('TRIG:COUN 100')
        self.dmm.write('TRIG:DEL 1')
        self.dmm.write('TRIG:SOUR IMM')
        return self.dmm.query('READ?')