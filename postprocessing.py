# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Thu Oct 18 09:55:11 2018

@author: yansl
"""

import os
import cv2
import shutil

import color_restoration
import output_convert

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

def files(folder_name, image_name, postfix_name):
    #creating a folder to save the results
    pwd = os.getcwd()
    pwd = pwd.strip()
    path = pwd.rstrip('\\')
    result = path.replace('\\', '/') + '/' + folder_name + '/' + image_name + postfix_name
    
    return result

def result_saving(image_name, folder_name, postfix, file):
    cv2.imwrite(folder_name + image_name + postfix, file)
    return None

def files_iteration():
    #creating the folders
    saving_recovery = file_operation('recovery')
    saving_restoration = file_operation('restoration')
    
    #getting files
    current_path = os.getcwd()
    image_path = current_path.replace('\\', '/') + '/' + 'ace'
    
    for images in os.listdir(image_path):
        full_path = os.path.join(image_path, images)
        if os.path.isdir(full_path):
            continue
        file = os.path.normcase(full_path)
        temp = os.path.splitext(images)[0]
        image_name = temp.split('_ace')[0]
        
        reference_image = files('first_filtered', image_name, '_first_filter_image.png') 
        mask_image = files('recovering_mask', image_name, '_recovering_mask.png')                 
        
        (image_name, result, output) = main(file, reference_image, mask_image)
        result_saving(image_name, saving_recovery, '_recovered.png', output)
        result_saving(image_name, saving_restoration, '_restored.png', result)

    return None
      
def main(enhancement_image, reference_image, mask_image):
    #main
    #read input images with opencv
    enhancement = cv2.imread(enhancement_image, cv2.IMREAD_COLOR)
    reference = cv2.imread(reference_image, cv2.IMREAD_COLOR)
    mask = cv2.imread(mask_image, cv2.IMREAD_GRAYSCALE)
    
    #the restoration
    out = color_restoration.restoration(enhancement, reference)   
    result = output_convert.conversion(out)  
    
    #shearing
    output = color_restoration.FOV_recovery(result, mask)
    
    #getting images' name
    core_name = os.path.split(enhancement_image)[1]
    name = os.path.splitext(core_name)[0]
    image_name = name.split('_ace')[0]
        
    return (image_name, result, output)

#the entrance
if __name__ == '__main__':
    files_iteration()
    print('Congratulations! All have done!')