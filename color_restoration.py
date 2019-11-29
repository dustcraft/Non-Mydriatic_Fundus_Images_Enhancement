# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Thu Oct 18 08:34:34 2018

@author: yansl

Target:  
    1. restore the image's colour
    2. back to original FOV
"""

import cv2
import numpy as np

import color_space_decomposition
import template_color_restoration
import unchange_factor

#%%
"""
secondary functions
"""
def channel_decomposion(image):
    temp_img = image.copy()
    #split image's channels
    (B, G, R) = cv2.split(temp_img)
    return (B, G, R)

def channel_merge(*, B, G, R):
    #merging the channels
    temp_img = cv2.merge([B, G, R])
    return temp_img

#%%
"""
primary functions
"""
def restoration(enhanced_image, reference_image):
#%%
    #Secction A: 
    #convert format & decomposition (besides including uint8 -> float32)
    enhanced = enhanced_image.copy().astype(np.float32) / 255.0
    reference = reference_image.copy().astype(np.float32) / 255.0    
    #1.YCrCb format decomposition, t_ means the target; r_ means the reference.
    (t_Y, t_Cr, t_Cb, r_Y, r_Cr, r_Cb) = color_space_decomposition.ycrcb_decomposition(enhanced, reference)    
    #2.HSV format decomposition
    (t_H, t_S, t_V, r_H, r_S, r_V) = color_space_decomposition.hsv_decomposition(enhanced, reference)
#%%    
    #Section B:
    #1.the preparation step:
    #make the template {note: the format - float32 (range 0 - 1), and the template is based on YCrCb space.}
    temp_ycrcb = template_color_restoration.standard_color_space_ycrcb(t_Y, r_Cr, r_Cb)   
    #calculate the enhancement factor by using V channel(float32) 
    factor_V = unchange_factor.gamma_enhanced_factor(t_V, r_V)   
    #2.the restoration step:
    #convert the template from RGB color space to HSV color space & decompose it
    (standard_H_ycrcb, second_S, standard_V_ycrcb) = unchange_factor.standard_hsv(temp_ycrcb)        
    #enhancement  
    final_S_V = unchange_factor.factor_enhancement(second_S, factor_V)      
    #3.merging & conversion back step:
    merging_ycrcb_sec_S_V = template_color_restoration.standard_color_space_hsv(standard_H_ycrcb, final_S_V, standard_V_ycrcb)
    return merging_ycrcb_sec_S_V

#%%
def FOV_recovery(restored_image, mask):
    image = restored_image
    """
    mask pre-processing part
    """
    #set value 1 to get FOV region
    mask[mask >= 1] = 1
    mask[mask < 1] = 0    
    """
    image processing part
    """
    #decompose RGB image channel
    (B, G, R) = channel_decomposion(image)
    #create temporary list
    temp = []
    #extract FOV region
    for i in (B, G, R):
        #multiply image with mask
        temp.append(i * mask)
    #merging all channels
    image_out = channel_merge(B = temp[0], G = temp[1], R = temp[2])
    
    return image_out