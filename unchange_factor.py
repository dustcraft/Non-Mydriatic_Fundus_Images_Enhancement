# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Sun Feb 10 16:26:38 2019

@author: yansl

Target:  
    1. calculate the enhancement factor
"""

import cv2
import numpy as np

#%%
"""
secondary functions
"""
def channel_decomposion(image):
    temp_img = image.copy().astype(np.float32)
    #split the image's channels
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
def gamma_enhanced_factor(t_channel, r_channel):
    #Gamma corrected enhancement
    gamma = -1 * (np.log(np.e/2)/np.log(1/2))
    new_t_channel = np.float_power(t_channel, gamma)   
    #calculate the factor
    #float64
    factor = np.divide(new_t_channel, r_channel, out=np.zeros_like(t_channel), where=r_channel!=0)
    final_factor = 1.5 * factor #- 0.5
    factor1 = final_factor.copy()
    factor1[factor1 <= 1] = 1.0
    #Saturation function
    final_factor = np.fmin(factor1, (5*np.tanh(factor1/2)))   
    #factor1[factor1 >= 5] = 5.0    
    return final_factor

def standard_hsv(standard_template):
    standard_space2hsv = cv2.cvtColor(standard_template, cv2.COLOR_BGR2HSV)
    (standard_H, standard_S, standard_V) = space_decomposition(standard_space2hsv)
    return (standard_H, standard_S, standard_V)

def factor_enhancement(benchmark, factor):    
    #factor enhancement
    #float32
    enhanced_channel = benchmark * factor
    #implement saturation operation
    new_value_channel = enhanced_channel.copy()
    new_value_channel[new_value_channel >= 1] = 1.0
    return new_value_channel