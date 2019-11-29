# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Tue Jan  8 20:03:12 2019

@author: yansl

Target:
    1. due to discreteness of image, the boundaries of two circles need to repair.
    2. The core resolution is that the median filtering technique will be executed.
"""

import cv2
import numpy as np

#%%
"""
secondary functions
"""
def image_inpaint(mask, image, radius):
    temp = image.copy()
    #use mask to get all ill-condition points
    #use Fast Marching Method to get rid of ill-condition point, which might be caused by computational precision and computer graphics.
    output = cv2.inpaint(temp, mask, radius, cv2.INPAINT_TELEA)     
    return output

#%%
"""
primary functions
"""
def border_repair(cut_mask, image, ellipse, inpaintradius):
    #make the mask template
    #1. input two circles
    '''
    the maximum inscribed circle
    '''
    '''
    mask processing part
    '''
    #*.grab ellipse's parameters
    #important parameters (in opencv): axis(major axis(2a), minor axis(2b)) & center(x, y)
    #note: semi-axis(semi-major axis(a), semi-minor axis(b))
    (x, y) = ellipse[0]
    (a2, b2) = ellipse[1]
    #find the semi-minor axis in mathematics (float)
    b = min((a2, b2)) / 2
    #create temporary template
    #sp[0] height(rows) y
    #sp[1] width(colums) x
    sp = cut_mask.shape[0: 2]
    min_mask = np.zeros(sp, dtype=np.uint8)
    #draw a maximum inscribed circle first
    #few pixels (such as one pixel) have been shrunk in radius for solving bouding problem
    radius = round(b + 1)
    center = (round(x), round(y))    
    #*.border expansion
    cv2.circle(min_mask, center, (radius - 3), color=255, thickness=7)     
    '''
    the minimum circumscribed circle
    '''
    '''
    mask processing part
    '''    
    a = max((a2, b2)) / 2
    radius = round(a + 8)
    max_mask = min_mask.copy()
    max_mask[max_mask >= 0] = 0
    #*.border expansion
    cv2.circle(max_mask, center, (radius - 4), color=255, thickness=9)      
    #2.inpaint   
    '''
    image processing part
    '''
    '''
    the minimum circumscribed circle
    '''
    repaired_max = image_inpaint(max_mask, image, inpaintradius)
    '''
    the maximum inscribed circle
    '''
    repaired_min = image_inpaint(min_mask, repaired_max, inpaintradius)
    '''
    The whole image combination
    '''
    repaired_image = repaired_min
    
    return repaired_image