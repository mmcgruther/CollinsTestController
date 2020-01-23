#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:53:00 2019

@author: pi
"""

from DM3068 import DM3068

dmm = DM3068()

dmm.connect()

print(dmm.query())

print("Resistance: " +dmm.measureRES()+" Ohms")
print("Voltage: " +dmm.measureVDC()+" Volts")
print("Current: " +dmm.measureIDC()+" Amps")
#print(dmm.readtest())
dmm.disconnect()