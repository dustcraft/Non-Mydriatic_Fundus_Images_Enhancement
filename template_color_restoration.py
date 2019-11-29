# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Sun Feb 10 09:32:48 2019

@author: yansl

Target:  
    1. apply YCrCB & HSV color space to create standard color space
"""

import cv2
import numpy as np

#%%
"""
secondary functions
"""
def channel_merge(*, B, G, R):
    #merging the channels
    B = B.copy().astype(np.float32)
    G = G.copy().astype(np.float32)
    R = R.copy().astype(np.float32)
    temp_img = cv2.merge([B, G, R])
    return temp_img

#%%
"""
primary functions
"""
def standard_color_space_ycrcb(t_Y, r_Cr, r_Cb):
    #format: float32
    #YCrCb
    temp_ycrcb = channel_merge(B = t_Y, G = r_Cr, R = r_Cb)
    rgb_based_ycrcb = cv2.cvtColor(temp_ycrcb, cv2.COLOR_YCrCb2BGR)
    return rgb_based_ycrcb

def standard_color_space_hsv(r_H, r_S, t_V):
    #format: float32
    #HSV
    temp_hsv = channel_merge(B = r_H, G = r_S, R = t_V)
    rgb_based_hsv = cv2.cvtColor(temp_hsv, cv2.COLOR_HSV2BGR)   
    return rgb_based_hsv