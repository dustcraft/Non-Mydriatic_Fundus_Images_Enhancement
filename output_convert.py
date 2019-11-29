# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Wed Mar  6 08:52:57 2019

@author: yansl

Target:  
    1. convert output format
"""

import numpy as np

#%%
def conversion(input_data):
    #input: float32
    #output: uint8
    temp1 = np.around(np.fabs(input_data * 255.0))
    temp = np.clip(temp1, 0, 255)
    output = temp.astype(np.uint8)
    return output