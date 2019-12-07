# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Sat Jan  5 16:17:53 2019

@author: yansl
"""

import os
import numpy as np
import cv2
import gc

import scipy.spatial
from PIL import Image

def file_operation(file_name):
    #creating a folder to save the results
    pwd = os.getcwd()
    pwd = pwd.strip()
    path = pwd.rstrip('\\')
    file_path = path.replace('\\', '/') + '/' + file_name
    
    #make sure the save path is existed
    #note that the existed folder will be deleted
    if (os.path.exists(file_path)):
        os.remove(file_name)
    else:
        print('The results text do not exist!')
    return None

def result_saving(text_name, image_name, folder_name, results):
    """
    file processing part
    """
    #save estimation values
    file = open(folder_name + text_name, 'a')
    
    file.write('name' + '  ' + 'cos' + '  ' + 'dice' + '  '  + 'jaccard' + '  ' + 'pearson' + '  ' + 'tanimoto' + '\n')
    file.write(image_name + ':' + '  ')
    file.write(str(results[0]) + '  ')
    
    file.write(str(results[1]) + '  ')
    file.write(str(results[2]) + '  ')
    file.write(str(results[3]) + '  ')
    file.write(str(results[4]) + '\n')
    file.write('\n')
    file.close()
    return None

def files(folder_name, image_name, postfix_name):
    #creating a folder to save the results
    pwd = os.getcwd()
    pwd = pwd.strip()
    path = pwd.rstrip('\\')
    result = path.replace('\\', '/') + '/' + folder_name + '/' + image_name + postfix_name
    
    return result

def files_iteration():    
    #getting files
    current_path = os.getcwd()
    image_path = current_path.replace('\\', '/') + '/' + 'benchmark'
    
    #the folder of results
    saving_evaluation = current_path.replace('\\', '/') + '/'
    
    #creating the new text file
    #!Note: we will delete the existed results text file.
    file_operation('fitted_mask_evaluation.txt')
    
    for images in os.listdir(image_path):
        full_path = os.path.join(image_path, images)
        if os.path.isdir(full_path):
            continue
        file = os.path.normcase(full_path)
                
        temp = os.path.splitext(images)[0]
        image_name = temp.split('_mask')[0]
        target_image = files('recovering_mask', image_name, '_recovering_mask.png')
                
        (image_name, outputs) = main(file, target_image)
        result_saving('fitted_mask_evaluation.txt', image_name, saving_evaluation, outputs)
    return None

"""
secondary functions
"""
def cos_similarity(vector1, vector2):
    result_temp = 1 - scipy.spatial.distance.cosine(vector1, vector2)
    result_cos = round(np.float64(result_temp), 5)
    return result_cos

def dice_similarity(vector1, vector2):
    vector1[vector1 > 0] = 1
    vector1 = vector1.copy().astype(np.bool)
    vector2[vector2 > 0] = 1
    vector2 = vector2.copy().astype(np.bool)
    result_temp = 1 - scipy.spatial.distance.dice(vector1, vector2)
    result_dice = round(np.float64(result_temp), 5)
    return result_dice

def jaccard_similarity(vector1, vector2):
    result_temp = 1 - scipy.spatial.distance.jaccard(vector1, vector2)
    result_jaccard = round(np.float64(result_temp), 5)
    return result_jaccard

def pearson_similarity(vector1, vector2):
    result_temp = 1 - scipy.spatial.distance.correlation(vector1, vector2)
    result_pearson = round(np.float64(result_temp), 5)
    return result_pearson

def tanimoto_similarity(vector1, vector2):
    vector1[vector1 > 0] = 1
    vector1 = vector1.copy().astype(np.bool)
    vector2[vector2 > 0] = 1
    vector2 = vector2.copy().astype(np.bool)    
    result_temp = 1 - scipy.spatial.distance.rogerstanimoto(vector1, vector2)
    result_tanimoto = round(np.float64(result_temp), 5)
    return result_tanimoto

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

def border_addition(image, top, bottom, left, right, value):
    temp = image.copy()
    #adding border
    temp = cv2.copyMakeBorder(temp, top, bottom, left, right, cv2.BORDER_CONSTANT, value)
    return temp

def border_cropping(mask):
    """
    mask coordinate processing & processing part
    """
    #get bounding box
    (x, y, width, height) = boundingbox(mask)
    """
    mask & image cropping part
    """
    #image coordinate (y, x)
    #numpy array range: [a, b), note: include a, but not include b!
    #numpy array order: [row, column]    
    #cropping
    cropped_mask = mask[y : (y + height), x : (x + width)]

    return (cropped_mask, x, width, y, height)

def border_adding(mask, border_length=20):
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
    
    return (mask_adding, coordinate)

"""
main function
"""     
def main(official_mask_fullname, generated_mask_name):
    #main
    #read input images with PIL   
    official_temp = Image.open(official_mask_fullname).convert('L')
    generated_temp = Image.open(generated_mask_name).convert('L')
    
    #pixels comparison
    official_mask = np.array(official_temp)
    official_mask[official_mask > 0] = 255
    generated_mask = np.array(generated_temp)
    generated_mask[generated_mask > 0] = 255
    
    #scatch around for image's dimensions
    #note: shape[0] denotes row (y), shape[1] denotes column (x)
    official_size = official_mask.shape[0: 2]
    generated_size = generated_mask.shape[0: 2]
    
    if ((official_size[0] != generated_size[0]) or (official_size[1] != generated_size[1])):
        #get the core size of offcial mask
        (cropped_official, official_x, official_width, official_y, official_height) = border_cropping(official_mask)
        (cropped_generated, generated_x, generated_width, generated_y, generated_height) = border_cropping(generated_mask)
        #estimate the difference between the two core sizes
        cropped_official_size = cropped_official.shape[0: 2]
        cropped_generated_size = cropped_generated.shape[0: 2]
        
        diff_y = (cropped_official_size[0] - cropped_generated_size[0]) / 2
        diff_x = (cropped_official_size[1] - cropped_generated_size[1]) / 2
        
        if (diff_y < 0):
            constant_y = -1
        else:
            constant_y = 1
            
        if (diff_x < 0):
            constant_x = -1
        else:
            constant_x = 1
                
        #scan the size of cropped official mask
        start_x = official_x
        start_y = official_y
        end_x = start_x + official_width
        end_y = start_y + official_height
        
        if (np.fabs(diff_x) > int(np.fabs(diff_x))):
            left_x = start_x + int(diff_x)
            right_x = official_size[1] - end_x + int(diff_x) + constant_x
        else:
            left_x = start_x + int(diff_x)
            right_x = official_size[1] - end_x + int(diff_x)
        
        if (np.fabs(diff_y) > int(np.fabs(diff_y))):
            up_y = start_y + int(diff_y)
            down_y = official_size[0] - end_y + int(diff_y) + constant_y
        else:
            up_y = start_y + int(diff_y)
            down_y = official_size[0] - end_y + int(diff_y)
            
        resized_mask = border_addition(cropped_generated, up_y, down_y, left_x, right_x, 0)
    else:
        resized_mask = generated_mask
    
    #cosine similarity
    official_vector = official_mask.flatten().reshape(1, -1)
    resized_vector = resized_mask.flatten().reshape(1, -1)
    #release memory
    del generated_temp, official_temp, generated_mask, official_mask
    gc.collect()
    
    #scipy method
    result_cos = cos_similarity(official_vector, resized_vector)
    result_dice = dice_similarity(official_vector, resized_vector)
    result_jaccard = jaccard_similarity(official_vector, resized_vector)
    result_pearson = pearson_similarity(official_vector, resized_vector)
    result_tanimoto = tanimoto_similarity(official_vector, resized_vector)
    
    #save
    core_name = os.path.split(official_mask_fullname)[1]
    name = os.path.splitext(core_name)[0]
    image_name = name.split('_mask')[0]
    
    outputs = (result_cos, result_dice, result_jaccard, result_pearson, result_tanimoto)

    return (image_name, outputs)

#entrance
if __name__ == '__main__':
    files_iteration()
