# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Thu Oct 18 09:55:11 2018

@author: yansl
"""

import os
import cv2
import numpy as np
from skimage import morphology
import shutil

def file_operation(folder_name):
    #creating a folder to save the results
    pwd = os.getcwd()
    pwd = pwd.strip()
    path = pwd.rstrip('\\')
    save_path = path.replace('\\', '/') + '/' + folder_name
    
    #make sure the save path is existed
    #note that the existed folder will be deleted
    if not (os.path.exists(save_path)):
        os.makedirs(save_path)
    else:
        shutil.rmtree(save_path)
        os.makedirs(save_path)
    return (save_path + '/')

def result_saving(image_name, folder_name, postfix, file):
    cv2.imwrite(folder_name + image_name + postfix, file)
    return None

def files_iteration():
    #creating the folders
    saving_direct_mask = file_operation('direct_mask')
    
    #getting files
    current_path = os.getcwd()
    image_path = current_path.replace('\\', '/') + '/' + 'original_images'
    
    for images in os.listdir(image_path):
        full_path = os.path.join(image_path, images)
        if os.path.isdir(full_path):
            continue
        file = os.path.normcase(full_path)
        (image_name, output) = main(file)
                
        result_saving(image_name, saving_direct_mask, '_auto_threshold.png', output)
    return None

def boundingcircle(image):
    area = cv2.countNonZero(image)
    return area

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
    #copy
    temp = image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    temp = cv2.morphologyEx(temp, cv2.MORPH_OPEN, kernel)
    return temp

def closing(image, *, kernel_size=3):
    #copy
    temp = image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    temp = cv2.morphologyEx(temp, cv2.MORPH_CLOSE, kernel)
    return temp
    
def erosion(image, *, kernel_size=3):
    #copy
    temp = image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    temp = cv2.erode(temp, kernel)
    return temp

def area_remove(image, *, min_size=300, connectivity=2):
    #copy
    temp = image.copy().astype(np.bool)
    dst = morphology.remove_small_holes(temp, min_size, connectivity).astype(np.uint8)
    return dst
      
def main(file):
    #main
    #read input images with opencv
    image = cv2.imread(file, cv2.IMREAD_COLOR)
    """
    resize the image
    """
    #some down-scaling operations (optional)
    sp = image.shape[0: 2]
    if (sp[0] >= 2400) or (sp[1] >= 2400):
        resized_image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
    elif ((sp[0] >= 1200) and (sp[0] <= 2400)) or ((sp[1] >= 1200) and (sp[1] <= 2400)):
        resized_image = cv2.resize(image, (0, 0), fx=0.75, fy=0.75, interpolation=cv2.INTER_CUBIC)
    else:
        resized_image = image
    '''
    processing part
    '''
    """
    First of all, two basic masks will be generated
    """         
    #decomposing image channel
    (_, _, R) = channel_decomposion(resized_image)
    
    core_name = os.path.split(file)[1]
    name = os.path.splitext(core_name)[0]
    image_name = name.split('_image')[0]
    
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
    
    #opening operation
    img1 = opening(img, kernel_size=3)
    #closing operation
    img2 = closing(img1, kernel_size=3)
    #erosion
    img3 = erosion(img2, kernel_size=3)
    #remove error area
    img4 = area_remove(img3, min_size=26000, connectivity=2)
    #show image as white/black
    output = threshold(img4, threshold=0, value=255)
    
    return (image_name, output)

#entrance
if __name__ == '__main__':
    files_iteration()