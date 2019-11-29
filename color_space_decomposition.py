# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Sun Feb 10 08:35:37 2019

@author: yansl

Target:  
    1. decompose different color spaces
    2. convert format from uint8 to float64
"""

import cv2
import numpy as np

#%%
"""
secondary functions
"""
def channel_decomposion(image):
    temp_img = image.copy().astype(np.float32)
    #split image's channels
    (B, G, R) = cv2.split(temp_img)
    return (B, G, R)

def space_decomposition(image):
    #decomposion    
    (channel1, channel2, channel3) = channel_decomposion(image)     
    return (channel1, channel2, channel3)

#%%
"""
primary functions
"""
'''
convert format & decomposition
    target image: after ACE
    reference image: only first filtering (No USM)
'''  
def ycrcb_decomposition(target_image, reference_image):
    #1. YCrCb
    #the target
    target_YCrCb = cv2.cvtColor(target_image, cv2.COLOR_BGR2YCrCb)
    (t_Y, t_Cr, t_Cb) = space_decomposition(target_YCrCb)
    #the reference    
    reference_YCrCb = cv2.cvtColor(reference_image, cv2.COLOR_BGR2YCrCb)        
    (r_Y, r_Cr, r_Cb) = space_decomposition(reference_YCrCb)
    return (t_Y, t_Cr, t_Cb, r_Y, r_Cr, r_Cb)

def hsv_decomposition(target_image, reference_image):
    #2. HSV
    #the target    
    target_HSV = cv2.cvtColor(target_image, cv2.COLOR_BGR2HSV)
    (t_H, t_S, t_V) = space_decomposition(target_HSV)
    #the reference
    reference_HSV = cv2.cvtColor(reference_image, cv2.COLOR_BGR2HSV)
    (r_H, r_S, r_V) = space_decomposition(reference_HSV)
    return (t_H, t_S, t_V, r_H, r_S, r_V)