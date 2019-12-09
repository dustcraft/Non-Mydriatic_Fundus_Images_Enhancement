# Non-Mydriatic Fundus Images Enhancement
  Our enhancement pipeline is a static and hands-off algorithm tree. It is used to enhance both mydriatic and non-mydriatic fundus images. Besides, our enhancement method can also remove overexposure and underexposure in the image like the Dodging and Burning technique. More important, you only need to keyboard several simple command-lines to test our pipeline.

## Overview
  Our pipeline is a hybrid language toolbox for enhancing and reconstructing fundus images. This pipeline is made up of a set of fundus image processing methods to cope with a series of tasks, such as dehazing, denoising, region extension, unbalanced illuminance removal, texture enhancement. There are four important stages in its workflow as shown below.<br>
  
  ![Pipeline](https://github.com/dustcraft/Non-Mydriatic_Fundus_Images_Enhancement/raw/master/Figure3(2).png)
  
  
  This hybrid language toolbox provides the following methods:
  1. Mask generation: generating the mask of an input fundus image, implemented by Python<br>
  2. Region extension: extending the FOV region of the fundus image from ellipse to rectangle, implemented by Python<br>
  3. Image enhancement: providing dehazing, denoising and texture enhancing operations, implemented by both Python and C<br>
  4. Color restoration: restoring the color of the enhanced image, implemented by Python<br>

  

## More Details

## Dependencies

## How to Use

## Related
