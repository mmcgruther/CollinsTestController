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

#dmm4050 = 'TCPIP0::192.168.1.3::INSTR'
dmm4050 = 'TCPIP::192.168.1.3::3490::SOCKET'
rm = visa.ResourceManager('@py')
#scope = rm.open_resource(dpo3034addr, write_termination=None, read_termination='\n')
#scope.encoding = 'latin_1'
dmm = rm.open_resource(dmm4050)
#dmm.write("*CLS")
print(dmm.query("*IDN?"))


dmm.close()
rm.close()