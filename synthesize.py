# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Tue Oct 16 14:53:15 2018

@author: yansl

Note:
    synthesize the whole procedure
"""

import os
import shutil
import gc
import cv2
import time

import mask_maker
import image_fill
import discreteness_boundary_repair
import filter_enhancement

#%%
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

#%%
def files_iteration():
    start_time = time.time()
    #creating some saving folders
    saving_mask = file_operation('recovering_mask')
    saving_first = file_operation('first_filtered')
    saving_usm = file_operation('usm')
    saving_border = file_operation('boder_adding_image')
    saving_recorrected = file_operation('recorrected_image')
    #getting the original data folder
    current_path = os.getcwd()
    image_path = current_path.replace('\\', '/') + '/' + 'original_images'
    for images in os.listdir(image_path):
        full_path = os.path.join(image_path, images)
        if os.path.isdir(full_path):
            continue
        file = os.path.normcase(full_path)
        (recovering_mask, output, original_appearance_masking, usm_image, recorrected_image, image_name) = main(file)
        result_saving(image_name, saving_mask, '_recovering_mask.png', recovering_mask)
        result_saving(image_name, saving_first, '_first_filter_image.png', output)
        result_saving(image_name, saving_usm, '_usm.png', usm_image)
        result_saving(image_name, saving_border, '_border_adding_image.png', original_appearance_masking)
        result_saving(image_name, saving_recorrected, '_recorrected_image.png', recorrected_image)
    end_time = time.time()
    lapse = end_time - start_time
    print('time cost', lapse, 's')
    return None
      
def main(file):
    #main
    #reading input images with opencv
    image = cv2.imread(file, cv2.IMREAD_COLOR)
    #making mask
    (resized_image, mask_out, direct_out) = mask_maker.mask(image)
    #cropping mask & image
    (cropped_mask, cropped_image, cropped_direct_mask, original_appearance) = mask_maker.border_cropping(resized_image, mask_out, direct_out)    
    #releasing memory
    del image, mask_out, resized_image, direct_out
    gc.collect()
    #adding border
    #border default length is 20
    (mask_adding, image_adding, original_appearance_adding, coordinate) = mask_maker.border_adding(cropped_mask, cropped_image, original_appearance, border_length=20)
    #Reclaiming the original size masks & the masked images
    (direct_mask_adding, original_appearance_masking) = mask_maker.border_corresponding(cropped_mask, cropped_direct_mask, original_appearance_adding, border_length=20)
       
    #FOV extraction
    (ellipse_mask, ellipse) = mask_maker.FOV_adjustment(mask_adding)
    
    #Recovering masks & images for post-processing & testing
    (recovering_mask, recorrected_image) = mask_maker.recovering(mask_adding, ellipse_mask, original_appearance_masking, direct_mask_adding)
        
    #reflection symmetry
    (reflected_mask, reflected_image) = image_fill.reflection_symmetry(mask_adding, image_adding, coordinate, border_length=20)    
    #ROI cutting
    (cut_mask, cut_image) = image_fill.circle_cutting(ellipse_mask, reflected_mask, reflected_image)
    #circle filling
    filled_image = image_fill.circle_fill(cut_mask, cut_image, ellipse)
    #boundary repairing
    repaired_image = discreteness_boundary_repair.border_repair(cut_mask, filled_image, ellipse, 7)
        
    #filtering filled image
    (filtered_image, output) = filter_enhancement.filter_enhancement(repaired_image)    
    #unsharp mask enhancement
    usm_image = filter_enhancement.usm_enhancement(filtered_image)
        
    core_name = os.path.split(file)[1]
    image_name = os.path.splitext(core_name)[0]
    
    return (recovering_mask, output, original_appearance_masking, usm_image, recorrected_image, image_name)

#entrance
if __name__ == '__main__':
    files_iteration()