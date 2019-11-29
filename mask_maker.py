# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Fri Jun 29 20:57:25 2018

@author: yansl

Usage:
    make image mask.
"""

import cv2
import sys
import numpy as np
from skimage import morphology

#%%
"""
secondary functions
"""
def channel_decomposion(image):
    temp_img = image.copy()
    #splitting all image's channels
    (B, G, R) = cv2.split(temp_img)
    return (B, G, R)

def channel_merge(*, B, G, R):
    #merging all channels
    temp_img = cv2.merge([B, G, R])
    return temp_img

def threshold(image, threshold, value):
    #copy
    temp = image.copy()
    #use threshold to set binary value
    #output: ret->input threshold, dst->output image
    (ret, dst) = cv2.threshold(temp, threshold, value, cv2.THRESH_BINARY)
    return dst

def opening(image, *, kernel_size=3):
    #a kind of morphological operation
    temp = image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    temp = cv2.morphologyEx(temp, cv2.MORPH_OPEN, kernel)
    return temp

def closing(image, *, kernel_size=3):
    temp = image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    temp = cv2.morphologyEx(temp, cv2.MORPH_CLOSE, kernel)
    return temp
    
def erosion(image, *, kernel_size=3):
    temp = image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    temp = cv2.erode(temp, kernel)
    return temp

def area_remove(image, *, min_size=300, connectivity=2):
    temp = image.copy().astype(np.bool)
    dst = morphology.remove_small_holes(temp, min_size, connectivity).astype(np.uint8)
    return dst

def border_addition(image, border_width, value):
    temp = image.copy()
    #adding border
    temp = cv2.copyMakeBorder(temp, border_width, border_width, border_width, border_width, cv2.BORDER_CONSTANT, value)
    return temp

def boundingcircle(image):
    temp = image.copy()
    #find profile
    (tmp, contours, hierarchy) = cv2.findContours(temp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #fitting
    ellipse = cv2.fitEllipseDirect(contours[0])
    return ellipse

def boundingbox(image):
    temp = image.copy()
    #find profile
    (_, contours, _) = cv2.findContours(temp, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)   
    #find bounding box coordinates
    #to get rectangular area which encloses the profile area, but it may be not the minimum.
    index = 0
    max_size = 0
    for i in range(len(contours)):
        size = contours[i].shape[0]
        if (size >= max_size):
            max_size = size
            index = i
        else:
            pass    
    cnt = contours[index]
    #(x, y)minimal up-right bounding rectangle
    (x, y, width, height) = cv2.boundingRect(np.array(cnt))
    return (x, y, width, height)

def rough(image):
    '''
    mathematical morphology preprocessing
    --for noise suppression
    '''
    """
    morphological filtering
    """
    #opening operation
    img = opening(image, kernel_size=3)
    #closing operation
    img = closing(img, kernel_size=3)
    #erosion
    img3 = erosion(img, kernel_size=3)
    #remove error area (empirical threshold)
    img4 = area_remove(img3, min_size=26000, connectivity=2)
    #inversion
    (_, img5) = cv2.threshold(img4, 0, 255, cv2.THRESH_BINARY_INV)
    #remove error area
    img6 = area_remove(img5, min_size=2000, connectivity=2)
    (_, output) = cv2.threshold(img6, 0, 255, cv2.THRESH_BINARY_INV)
    
    #if the empirical thresholds above failed, some smaller ones should be used
    #parameters adjustment base on prior
    #shape (y, x)
    sp_temp = image.shape[0: 2]
    #grab top-left, top-right, bottom-left, bottom-right corners
    top_left = output[0, 0]
    bottom_left = output[(sp_temp[0] - 1), 0]
    top_right = output[0, (sp_temp[1] - 1)]
    bottom_right = output[(sp_temp[0] - 1), (sp_temp[1] - 1)]
    
    #for robustness, the value of four corners did not set to 0    
    if ((top_left >= 10) or (bottom_left >= 10) or (top_right >= 10) or (bottom_right >=10)):
        #change to a smaller threshold
        img4 = area_remove(img3, min_size=1000, connectivity=2)
        (_, img5) = cv2.threshold(img4, 0, 255, cv2.THRESH_BINARY_INV)
        img6 = area_remove(img5, min_size=1000, connectivity=2)
        (_, output) = cv2.threshold(img6, 0, 255, cv2.THRESH_BINARY_INV)
        if output.min() != 0:
            #change to another threshold
            img4 = area_remove(img3, min_size=2000, connectivity=2)
            (_, img5) = cv2.threshold(img4, 0, 255, cv2.THRESH_BINARY_INV)
            img6 = area_remove(img5, min_size=2000, connectivity=2)
            (_, output) = cv2.threshold(img6, 0, 255, cv2.THRESH_BINARY_INV)
    
    return output

#%%
"""
primary functions
"""    
def mask(rgb_img):
    """
    resize the image
    """
    #some down-scaling operations (optional)
    sp = rgb_img.shape[0: 2]
    if (sp[0] >= 2400) or (sp[1] >= 2400):
        resized_image = cv2.resize(rgb_img, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    elif ((sp[0] >= 1200) and (sp[0] <= 2400)) or ((sp[1] >= 1200) and (sp[1] <= 2400)):
        resized_image = cv2.resize(rgb_img, (0, 0), fx=0.75, fy=0.75, interpolation=cv2.INTER_CUBIC)
    else:
        resized_image = rgb_img
    '''
    processing part
    '''
    """
    First of all, a basic mask will be generated
    """         
    #decomposing image channels
    (_, _, R) = channel_decomposion(resized_image)
    #In order to generalize our algorithm, the automatic thresholds are produced by histogram prior.
    hist = np.bincount(R.ravel(), minlength=256)
    clip = hist[5:21]   
    fragment = hist[1:21]   
    condition = hist[31:256]
    condition_max_number = int(np.argpartition(condition, -1)[-1] + 31)
    value = hist[condition_max_number]    
    if (hist[30] > value):
        local_min_number = int(np.argpartition(fragment, 1)[0] + 1)
    else:
        local_min_number = int(np.argpartition(clip, 1)[0] + 5)    
    threshold_value = local_min_number
    #binary image
    img = threshold(R, threshold=threshold_value, value=1)    
    #preprocessing
    mask_output = rough(img)
    
    mask_output[mask_output > 0] = 255
    
    direct_out = mask_output
    """
    The second correction
    """    
    #inverse smoothing
    (_, inverse) = cv2.threshold(mask_output.copy(), 0, 255, cv2.THRESH_BINARY_INV)
    #edge smoothing
    blurredmask = cv2.pyrUp(inverse) #should be uint8(CV_8U)
    for i in range(19):
        blurredmask = cv2.medianBlur(blurredmask, 19)
    blurredmask = cv2.pyrDown(blurredmask)
    
    (_, blurredmask) = cv2.threshold(blurredmask, 200, 255, cv2.THRESH_BINARY)
    (_, temp1) = cv2.threshold(blurredmask, 0, 255, cv2.THRESH_BINARY_INV)
    
    temp = temp1.copy()
    #find the maximum polygonal profile of FOV
    (_, contours, _) = cv2.findContours(temp, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    index = 0
    max_size = 0
    for i in range(len(contours)):
        size = contours[i].shape[0]
        if (size >= max_size):
            max_size = size
            index = i
        else:
            pass    
    cnt = contours[index]
    #make a convex mask
    hull = cv2.convexHull(cnt)    
    temp[temp > 0] = 0
    temp = cv2.fillConvexPoly(temp, hull[:, 0, :], color=255)
    """
    repair border
    """
    #statistics
    rest_area = cv2.bitwise_xor(mask_output, temp)
    rest_number = cv2.countNonZero(rest_area)
    origin_number = cv2.countNonZero(mask_output)
       
    #comparison
    if (rest_number >= 0):
        if (rest_number <= 0.02 * origin_number):
            while 1:
                temp = erosion(temp, kernel_size=3)
                count = cv2.countNonZero(temp)
                if (count <= 0.97 * origin_number):
                    break
            mask_output = temp
        else:
            while 1:
                temp = erosion(temp, kernel_size=3)
                count = cv2.countNonZero(temp)
                if (count <= 0.98 * origin_number):
                    break
            mask_output = temp
    else:
        sys.exit(0)
        
    if mask_output.min() != 0:
        #change to a smaller threshold
        mask_output = area_remove(mask_output, min_size=2000, connectivity=2)
        
    mask_output[mask_output > 0] = 255
    
    return (resized_image, mask_output, direct_out)

def border_cropping(image, mask, direct_mask):
    """
    mask coordinate processing & processing part
    """
    #get bounding box
    (x, y, width, height) = boundingbox(mask)
    (x1, y1, width1, height1) = boundingbox(direct_mask)
    """
    mask & image cropping part
    """
    #image coordinate (y, x)
    #numpy array range: [a, b), note: include a, but not include b!
    #numpy array order: [row, column]    
    #cropping
    cropped_mask = mask[y : (y + height), x : (x + width)]   
    cropped_direct_mask = direct_mask[y1 : (y1 + height1), x1 : (x1 + width1)]
    #decompose into RGB image channels
    (B, G, R) = channel_decomposion(image)
    #cropping
    temp = []
    output = []
    for i in (B, G, R):
        temp.append(i[y : (y + height), x : (x + width)])
    original_appearance = channel_merge(B = temp[0], G = temp[1], R = temp[2])
    #set value 1 to get FOV region           
    (_, temp_mask) = cv2.threshold(cropped_mask, 0, 1, cv2.THRESH_BINARY)
    for i in temp:
        #multiplication image with mask
        output.append(i * temp_mask)
    cropped_image = channel_merge(B = output[0], G = output[1], R = output[2])
    
    return (cropped_mask, cropped_image, cropped_direct_mask, original_appearance)

def border_adding(mask, image, original_appearance, border_length=20):
    """
    mask processing part
    """
    #adding a border
    #default: border_addition(img, 20, 0)
    mask_adding = border_addition(mask, border_length, 0)
    """
    coordinate processing part
    """
    #getting coordinate parameters (x, y, width, height)
    coordinate = boundingbox(mask_adding)
    """
    image processing part
    """
    '''
    1. corrected images
    '''
    #decomposing all RGB image channels
    (B, G, R) = channel_decomposion(image)
    #addition
    temp = []
    #adding a border
    for i in (B, G, R):
        temp.append(border_addition(i, border_length, 0))
    #merging all channels
    image_adding = channel_merge(B = temp[0], G = temp[1], R = temp[2])
    '''
    2. retained the images of origin appearance
    '''
    #decomposing all RGB image channels
    (B, G, R) = channel_decomposion(original_appearance)
    #addition
    temp = []
    #adding a border
    for i in (B, G, R):
        temp.append(border_addition(i, border_length, 0))
    #merging all channels
    original_appearance_adding = channel_merge(B = temp[0], G = temp[1], R = temp[2])
    return (mask_adding, image_adding, original_appearance_adding, coordinate)

def border_corresponding(cropped_mask, cropped_direct_mask, original_appearance_adding, border_length):
    """
    mask processing part
    """
    #scatch around for image's dimensions
    #note: shape[0] denotes row (y), shape[1] denotes column (x)
    cropped_size = cropped_mask.shape[0: 2]
    direct_cropped_size = cropped_direct_mask.shape[0: 2]
    
    if ((cropped_size[0] != direct_cropped_size[0]) or (cropped_size[1] != direct_cropped_size[1])):        
        diff_y = (cropped_size[0] - direct_cropped_size[0]) / 2
        diff_x = (cropped_size[1] - direct_cropped_size[1]) / 2
        
        if (diff_y < 0):
            constant_y = -1
        else:
            constant_y = 1
            
        if (diff_x < 0):
            constant_x = -1
        else:
            constant_x = 1
        
        if (np.fabs(diff_x) > int(np.fabs(diff_x))):
            left_x = border_length + int(diff_x)
            right_x = border_length + int(diff_x) + constant_x
        else:
            left_x = border_length + int(diff_x)
            right_x = border_length + int(diff_x)
        
        if (np.fabs(diff_y) > int(np.fabs(diff_y))):
            up_y = border_length + int(diff_y)
            down_y = border_length + int(diff_y) + constant_y
        else:
            up_y = border_length + int(diff_y)
            down_y = border_length + int(diff_y)
            
        direct_mask_adding = cv2.copyMakeBorder(cropped_direct_mask, up_y, down_y, left_x, right_x, cv2.BORDER_CONSTANT, 0)
    else:
        direct_mask_adding = cv2.copyMakeBorder(cropped_direct_mask, border_length, border_length, border_length, border_length, cv2.BORDER_CONSTANT, 0)
    """
    image processing part
    """
    #decomposing all RGB image channels
    (B, G, R) = channel_decomposion(original_appearance_adding)
    #masking
    output = []
    #getting the corresponding masks
    (_, temp_mask) = cv2.threshold(direct_mask_adding, 0, 1, cv2.THRESH_BINARY)
    for i in (B, G, R):
        #multiplication image with mask
        output.append(i * temp_mask)
    #merging all channels
    original_appearance_masking = channel_merge(B = output[0], G = output[1], R = output[2])
    return (direct_mask_adding, original_appearance_masking)

def FOV_adjustment(border_added_mask):
    #create template
    ellipse_mask = np.zeros(border_added_mask.shape, dtype=np.uint8)    
    #edge smoothing
    blurredmask = cv2.pyrUp(border_added_mask) #should be uint8(CV_8U)
    for i in range(15):
        blurredmask = cv2.medianBlur(blurredmask, 19)
    blurredmask = cv2.pyrDown(blurredmask)
    
    (_, blurredmask) = cv2.threshold(blurredmask, 200, 255, cv2.THRESH_BINARY)    
    #Canny operator extract elliptical profile
    temp = cv2.Canny(blurredmask, 25, 150)    
    #the algorithm will get the maximum inscribed circle & the minimum circumscribed circle(fitting ellipse)
    #parameters: center(x, y), axis(major, minor), angle(degree)
    ellipse = boundingcircle(temp)
    #draw an ellipse on the template
    #important parameters of ellipse: axis(major axis(2a), minor axis(2b)) & center(x, y)
    #note: semi-axis(semi-major axis(a), semi-minor axis(b))

    cv2.ellipse(ellipse_mask, ellipse, color=255, thickness=-1)
    
    return (ellipse_mask, ellipse)

def recovering(adding_mask, ellipse_mask, original_appearance_masking, direct_mask_adding):
    """
    mask processing part
    """
    #making the post-processing mask
    #First, exploiting bitwise or operartion
    or_result = cv2.bitwise_or(direct_mask_adding, adding_mask)
    #Second, exploiting bitwise and operation
    recovering_mask = cv2.bitwise_and(or_result, ellipse_mask)
    """
    image processing part
    """
    #decomposing all RGB image channels
    (B, G, R) = channel_decomposion(original_appearance_masking)
    #masking
    output = []
    #getting the corresponding masks
    (_, temp_mask) = cv2.threshold(recovering_mask, 0, 1, cv2.THRESH_BINARY)
    for i in (B, G, R):
        #multiplication image with mask
        output.append(i * temp_mask)
    #merging all channels
    recorrected_image = channel_merge(B = output[0], G = output[1], R = output[2])
    return (recovering_mask, recorrected_image)