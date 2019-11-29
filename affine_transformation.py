# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Created on Fri Sep 20 09:24:57 2019

@author: yansl
"""

import os
import cv2

def files_iteration():
    image_path = 'F:/temp/samples/image_evaluation/image_all'
    for images in os.listdir(image_path):
        full_path = os.path.join(image_path, images)
        file = os.path.normcase(full_path)
        main(file)
    return None
      
def main(file):
    #main
    #read input images with opencv
    image = cv2.imread(file, cv2.IMREAD_COLOR)
    """
    resize the image
    """    
    resized_image = cv2.resize(image, (512, 512), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
    
        
    core_name = os.path.split(file)[1]
    name2 = os.path.splitext(core_name)[0]
    image_name2 = name2.split('_image')
    
    
    output = resized_image
    cv2.imwrite('F:/temp/data/renew/affine/' + image_name2[0] + '_affined.png', output)

    return None

#entrance
if __name__ == '__main__':
    files_iteration()