# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Thu Sep  6 08:42:01 2018

@author: yansl

Target: Highpass filter (lapalce) & Unsharp mask enhancement
"""

import cv2
import numpy as np
from scipy import signal

import output_convert

#%%
"""
secondary functions
"""
def channel_decomposion(image):
    temp_img = image.copy()
    #split all channels
    (B, G, R) = cv2.split(temp_img)
    return (B, G, R)

def channel_merge(*, B, G, R):
    #merge all channels
    temp_img = cv2.merge([B, G, R])
    return temp_img 

def gaussian_filter(image, ksize=(131,131), sigmaX=95):
    temp = image.copy()
    #Gaussian Blur
    output = cv2.GaussianBlur(temp, ksize, sigmaX)
    return output

def laplacian(image):
    #copy & the precision should be float32
    temp = image.copy().astype(np.float32)
    #create convolutional template
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]], dtype=np.float32)
    #Laplacian convolutional processing
    output = signal.convolve2d(temp, kernel, boundary='symm', mode='same')
    return output

def image_subtraction(image):
    #copy
    temp = image.copy()   
    #strong Guided Filtering
    size = 30
    #format: float32
    guide_filtered = cv2.ximgproc.guidedFilter(temp, temp, size, 0.01)   
    #format: float32
    highpass = image - guide_filtered   
    return highpass

def normalization(data):
    output = cv2.normalize(src = data, dst = None, alpha = 0.0, beta = 1.0, norm_type = cv2.NORM_MINMAX, dtype = -1)
    return output

def unsharpening_mask(image, HFE):
    #copy
    temp = image.copy()    
    #USM, range: 0 ~ 1 
    #enhancement factor: default 1.5
    usm = USM(temp, HFE, 1.5)    
    #normalization (float32)
    usm = normalization(usm)
    return usm

def USM(origin: 'float32', highpass: 'float32', enhancement_factor):
    usm = origin + enhancement_factor * highpass
    return usm

#%%
"""
primary functions
"""
def filter_enhancement(filled_image): 
    #set the range to 0 - 1
    filled_image = filled_image.astype(np.float32) / 255.0
    
    #slight guided filter smoothing
    guide_filtered = cv2.ximgproc.guidedFilter(filled_image, filled_image, 1, 0.01)  
    #slight gaussian filter smoothing
    ksize = (5, 5)
    sigmaX = 2
    gaussian_filtered = gaussian_filter(guide_filtered, ksize, sigmaX)
    #decompose into RGB image channels
    (B0, G0, R0) = channel_decomposion(gaussian_filtered)
        
    #laplacian algorithm
    B1 = laplacian(B0)
    G1 = laplacian(G0)
    R1 = laplacian(R0)
    #merge all channels
    laplaced = channel_merge(B = B1, G = G1, R = R1)
    
    #enhancement part
    highpass = laplaced + guide_filtered
    #normalize the output directly
    #range 0 - 1, float32
    filtered_image = normalization(highpass)
    #back to uint8
    output = output_convert.conversion(filled_image)  
    return (filtered_image, output)

def usm_enhancement(filtered_image):   
    #unsharpening mask
    #high frequency emphasis (HFE)
    #filtered_image's format should be float32, range 0 - 1
    highpass = image_subtraction(filtered_image)   
    #subtraction method
    usm_image = unsharpening_mask(filtered_image, highpass)    
    #back to uint8
    output = output_convert.conversion(usm_image)    
    return output