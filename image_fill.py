# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Wed Oct 17 09:28:35 2018

@author: yansl

Target: mirror & fill

Theory: Circle inversion

Details:
    1. mark and extract Non-FOV region
    2. use Circle inversion to fill Non-FOV region

Reference:
    1. D. E. Blair, Inversion Theory and Conformal Mapping. Student Mathematical Library, issue 9.
American Mathematical Society, Providence (2000)
    2. https://stackoverflow.com/questions/47006652/python-most-efficient-way-to-mirror-an-image-along-its-vertical-axis

"""

import cv2
import numpy as np

#%%
"""
secondary functions
"""
def channel_decomposion(image):
    temp_img = image.copy()
    #split image's all channels
    (B, G, R) = cv2.split(temp_img)
    return (B, G, R)

def channel_merge(*, B, G, R):
    #merge all channels
    temp_img = cv2.merge([B, G, R])
    return temp_img

def coordinate_translation(center, shape):
    #move origin to the center of circle
    #but will not change axis direction
    temp_x = np.array(range(shape[1]), dtype=np.float64) #column vector
    temp_y = np.array(range(shape[0]), dtype=np.float64)
    #expand dimension
    temp_x = np.tile(temp_x, (shape[0], 1))
    temp_y = np.tile(temp_y, (shape[1], 1))
    #transpose
    temp_y = np.transpose(temp_y)
    #translation
    output_x = temp_x - center[0]
    output_y = temp_y - center[1]
    return (output_x, output_y)

def image_coordinate(center_x, center_y, center):
    #back to image coordinate(top left is the origin)
    output_x = center_x + center[0]
    output_y = center_y + center[1]
    return (output_x, output_y)

def Circle_inversion(center, radius, shape):
    #Coordinate translation
    (x, y) = coordinate_translation(center, shape)
    #convert to polar coordinate
    (r, theta) = cv2.cartToPolar(x, y, angleInDegrees = True)
    # k is radius^2
    k = radius ** 2
    #Circle inversion coordinate calculation
    #inversion_r = k / r
    inversion_r = np.divide(k, r, out=np.zeros_like(r), where=r!=0)    
    #back to cartesian
    (inversion_x, inversion_y) = cv2.polarToCart(inversion_r, theta, angleInDegrees = True)
    #back to opencv image coordinate
    (image_x, image_y) = image_coordinate(inversion_x, inversion_y, center)
    return (image_x, image_y)

def nonfov_assignment(image, mask, inversion_coordinate, shape):
    temp = image.copy().astype(np.float64)
    temp[temp >= 0.0] = 0.0
    image = image.astype(np.float64)
    #float type index data
    inversion_x = inversion_coordinate[0]
    inversion_y = inversion_coordinate[1]    
    #go through all points in the Non-FOV region
    #shape[0] height(rows) y
    #shape[1] width(colums) x
    for y in range(shape[0]):
        for x in range(shape[1]):
            #copy value of relevant FOV point to inversion point
            #FOV retains existing values
            if mask[y, x]:
                #get 2-D grid, use bilinear interpolation method to get value.
                x0 = inversion_x[y, x]
                y0 = inversion_y[y, x]
                x1 = int(x0)
                y1 = int(y0)
                #eliminate boundary
                if ((x >= 0 and x < (shape[1] - 1)) and (y >= 0 and y < (shape[0] - 1))): 
                    #copy value of point in FOV to target point
                    #image boundary points do not implement interpolation
                    p = x0 - x1
                    q = y0 - y1
                    temp[y, x] = round((1 - p) * (1 - q) * image[y1, x1] + p * (1 - q) * image[y1, (x1 + 1)] + 
                                       q * (1 - p) * image[(y1 + 1), x1] + p * q * image[(y1 + 1), (x1 + 1)])
                else:
                    temp[y, x] = image[y1, x1]
    out = np.around(temp)
    output = np.clip(out, 0, 255).astype(np.uint8)
    return output

#%%
"""
primary functions
"""
def reflection_symmetry(mask_adding, image_adding, new_coordinate, border_length=20):
    #Note: for the robustness, the symmetry pixels were indented by 5 pixels
    (new_x , new_y, width, height) = new_coordinate
    """
    coordinate parameters
    """
    x_min = new_x
    y_min = new_y
    x_max = new_x + width
    y_max = new_y + height
    length = border_length
    """
    mask processing part
    """
    #reflection for left
    #need include column x_min & ensure robustness, so 5 pixel is added for that
    #thus, there are (x_min + 5 + length) columns to copy
    mask_adding[:, 0: (x_min + 5): 1] = mask_adding[:, ((x_min + length + 5) + 5): (x_min + 5): -1]
    #right
    #the axis of symmetry is x_max - 6 (5 pixels)
    mask_adding[:, (x_max - 5): (x_max + length): 1] = mask_adding[:, (x_max - 7): ((x_max - length - 5) - 7): -1]
    #up
    mask_adding[0: (y_min + 5): 1, :] = mask_adding[((y_min + length + 5) + 5): (y_min + 5): -1, :]
    #down
    mask_adding[(y_max - 5): (y_max + length): 1, :] = mask_adding[(y_max - 7): ((y_max - length - 5) - 7): -1, :]

    reflected_mask = mask_adding
    """
    image processing part
    """    
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(image_adding)
    #symmetry
    temporary = []
    for i in (B, G, R):
        #left
        i[:, 0: (x_min + 5): 1] = i[:, ((x_min + length + 5) + 5): (x_min + 5): -1]
        #right
        i[:, (x_max - 5): (x_max + length): 1] = i[:, (x_max - 7): ((x_max - length - 5) - 7): -1]
        #up
        i[0: (y_min + 5): 1, :] = i[((y_min + length + 5) + 5): (y_min + 5): -1, :]
        #down
        i[(y_max - 5): (y_max + length): 1, :] = i[(y_max - 7): ((y_max - length - 5) - 7): -1, :]
        temporary.append(i)
    #merge all channels
    reflected_image = channel_merge(B = temporary[0], G = temporary[1], R = temporary[2])

    return (reflected_mask, reflected_image)

def circle_cutting(ellipse_mask, reflected_mask, reflected_image):   
    """
    mask processing part
    """
    #multiplication
    #make new mask
    (_, ellipse_mask) = cv2.threshold(ellipse_mask, 0, 1, cv2.THRESH_BINARY)
    cut_mask = ellipse_mask * reflected_mask
    """
    image processing part
    """
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(reflected_image)
    #symmetry
    temporary = []
    for i in (B, G, R):
        temporary.append(i * ellipse_mask)    
    #merge all channels
    cut_image = channel_merge(B = temporary[0], G = temporary[1], R = temporary[2])

    return (cut_mask, cut_image)

def circle_fill(cut_mask, cut_image, ellipse):   
    '''
    the maximum inscribed circle
    '''
    '''
    mask processing part
    '''
    #grab ellipse's parameters
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
    temp_mask = np.zeros(sp, dtype=np.uint8)
    #draw a maximum inscribed circle first
    #few pixels (such as 2 or 3 pixels) have been shrunk in radius for solving bouding problem
    radius = round(b - 2)
    center = (round(x), round(y))
    cv2.circle(temp_mask, center, radius, color=1, thickness=-1)
    #Non-MAX zone
    (_, nonmax_mask) = cv2.threshold(temp_mask, 0, 255, cv2.THRESH_BINARY_INV)
    #extract MAX zone
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(cut_image)
    temporary = []
    for i in (B, G, R):
        temporary.append(i * temp_mask)    
    #merge all channels
    roi_minor = channel_merge(B = temporary[0], G = temporary[1], R = temporary[2])
    
    #compute relevant inversion coordinate
    coordinate = Circle_inversion(center, radius, sp)
    '''
    image processing part
    '''
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(roi_minor)
    #inversion
    max_B = nonfov_assignment(B, nonmax_mask, coordinate, sp)
    max_G = nonfov_assignment(G, nonmax_mask, coordinate, sp)
    max_R = nonfov_assignment(R, nonmax_mask, coordinate, sp)    
    #merge all channels
    max_ins_image = channel_merge(B = max_B, G = max_G, R = max_R)  
    '''
    the minimum circumscribed circle
    '''
    '''
    mask processing part
    '''    
    a = max((a2, b2)) / 2
    radius = round(a - 1)
    temp_mask[temp_mask >= 0] = 0
    cv2.circle(temp_mask, center, radius, color=1, thickness=-1)
    
    #boundary shrinking
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    shrunk_cut_mask = cv2.erode(cut_mask, kernel)
       
    (_, nonellipse_mask) = cv2.threshold(shrunk_cut_mask, 0, 1, cv2.THRESH_BINARY_INV)
    #grab expanded median region
    temp_region = temp_mask.copy()
    temp_region[temp_region >= 0] = 0
    temp_radius = round(a + 1)
    cv2.circle(temp_region, center, temp_radius, color=1, thickness=-1)    
    combination_region_mask = cv2.multiply(temp_region, nonellipse_mask)
       
    #Non-MIN
    (_, nonmin_mask) = cv2.threshold(temp_mask, 0, 255, cv2.THRESH_BINARY_INV)
    '''
    image processing part
    '''
    #grab the shrunk ellipse zone
    (_, shrunk_cut_mask) = cv2.threshold(shrunk_cut_mask, 0, 1, cv2.THRESH_BINARY)
    (B, G, R) = channel_decomposion(cut_image)
    temporary = []
    for i in (B, G, R):
        temporary.append(i * shrunk_cut_mask)    
    #merging all channels
    shrunk_ellipse = channel_merge(B = temporary[0], G = temporary[1], R = temporary[2]) 
       
    #grab MIN zone
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(max_ins_image)
    temporary = []
    for i in (B, G, R):
        temporary.append(i * combination_region_mask)    
    #merge all channels
    roi_median = channel_merge(B = temporary[0], G = temporary[1], R = temporary[2])
    #combine each part together thoroughly, and get the minimum circumscribed circle region image
    roi_major = cv2.bitwise_or(roi_median, shrunk_ellipse)
        
    #compute relevant inversion coordinate
    coordinate = Circle_inversion(center, radius, sp)
        
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(roi_major)
    #inversion
    min_B = nonfov_assignment(B, nonmin_mask, coordinate, sp)
    min_G = nonfov_assignment(G, nonmin_mask, coordinate, sp)
    min_R = nonfov_assignment(R, nonmin_mask, coordinate, sp)    
    #merge all channels    
    min_cir_image = channel_merge(B = min_B, G = min_G, R = min_R)  
    
    '''
    The whole image combination
    '''
    #for the robustness, the radius of minimum circumscribed circle should be shrunk   
    (_, new_nonmin_mask) = cv2.threshold(temp_region, 0, 1, cv2.THRESH_BINARY_INV)  
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(min_cir_image)
    temporary = []
    for i in (B, G, R):
        temporary.append(i * new_nonmin_mask)    
    #merging all channels
    roi_minor = channel_merge(B = temporary[0], G = temporary[1], R = temporary[2])
    #creating the whole image    
    whole_image = cv2.bitwise_or(roi_major, roi_minor)
        
    return whole_image