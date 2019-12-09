# Non-Mydriatic Fundus Images Enhancement

## Overview
Our enhancement pipeline is a static and hands-off algorithm tree. It is used to enhance both mydriatic and non-mydriatic fundus images. Besides, our enhancement method can also remove overexposure and underexposure in the image like the Dodging and Burning technique. More important, you only need to keyboard several simple command-lines to test our pipeline.
  
## More Details
Our pipeline is a hybrid language toolbox for enhancing and reconstructing fundus images. This pipeline is made up of a set of fundus image processing methods to cope with a series of tasks, such as dehazing, denoising, region extension, unbalanced illuminance removal, texture enhancement. There are four important stages in its workflow as shown below.<br>
  
  ![Pipeline](https://github.com/dustcraft/Non-Mydriatic_Fundus_Images_Enhancement/raw/master/Figure3(2).png)
  
  
  This hybrid language toolbox provides the following methods:<br>
  1. Mask generation: generating the mask of an input fundus image, implemented by Python<br>
  2. Region extension: extending the FOV region of the fundus image from ellipse to rectangle, implemented by Python<br>
  3. Image enhancement: providing dehazing, denoising and texture enhancing operations, implemented by both Python and C<br>
  4. Color restoration: restoring the color of the enhanced image, implemented by Python<br>

## Dependencies
This repository is the integration of our pipeline algorithms, and it also contains some standalone third-party software which we have used. However, these codes rely on some extra libraries.

A. Python part<br>
The Python codes use several python modules, but some of them are not the default packages (or the standard libraries) of Python. So, please install the following required python modules:<br>

 Package      | Tested version    
 ---------- | :-----------:  
 [Python](https://www.python.org/)     | 3.6.4     
 [OpenCV](https://opencv.org/)     | 3.3.1
 [SciPy](https://www.scipy.org/)     | 1.0.0
 [PIL](http://www.pythonware.com/products/pil/)     | 5.0.0
 [NumPy](https://numpy.org/)     | 1.14.2
 [Skimage](https://github.com/scikit-image/scikit-image)     | 0.13.1
 
 Tips: To install [OpenCV](https://opencv.org/) in your own directory, please carefully select the correct version from [here](https://opencv.org/releases/).
 
 Example:<br>
Through the source code:
```bash
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
```
(Please download the corresponding release version)

```bash
[sudo] python3 setup.py install
```
Or directly through pip3 to install it:<br>

```bash
[sudo] pip3 install opencv-python==3.3.1
[sudo] pip3 install opencv-contrib-python==3.3.1
```
**Note**:
We need an extra OpenCV module -- [*ximgproc*](https://github.com/opencv/opencv_contrib) -- to perform our algorithms, but it does not belong to the official OpenCV distribution. So, you should install this extra module -- *Opencv-contrib*.

Besides, to make the OpenCV can work with Python IDE, like Anaconda3, you may need to follow the guide of [Install OpenCV for Anaconda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#) to setup OpenCV. If you use the Anaconda3 IDE, the extra release -- *Opencv-contrib* -- will be installed with the official OpenCV distribution by default.

Because most of the other modules are heavily dependent on *NumPy* modules, we recommend you to use the Python IDE, such as Anaconda3. If not, please install appropriate packages for your development environment (Python versions, 32-bit or 64-bit)

B. Other part (C part)<br>
The modified ACE algorithm, which has been developed by **Pascal Getreuer**, is a part of our enhancement method. You can find the details from [here](http://www.ipol.im/pub/art/2012/g-ace/article_lr.pdf). And its zip file is available [here](http://www.ipol.im/pub/art/2012/g-ace/).

## How to Use
You can test the whole pipeline with several simple Python command-lines. And these commands will start processing the test images in this directory then generate their enhanced images in the corresponding folders.

**1. Generating border-adding-images, first-filtered, recorrected-image, recovering-mask, and usm**<br>
```bash
[sudo] python ./synthesize.py # Only python3 is in your computer
```
Or<br>
```bash
[sudo] python3 ./synthesize.py # When both python2 and python3 are in your environment
```

Their results are in the corresponding folders: *border_adding_image*, *first_filtered*, *recorrected_image*, *recovering_mask*, *usm*.

**Note**: We only generate the masks after ellipse-fitting (***the recovering masks***) by default. And the former demonstration data will be replaced when you run this command-line. The default format of output images is **PNG**.

If you want to generate the original masks (just be polished by some morphological operations), you could run:<br>
```bash
[sudo] python ./direct_mask_generation.py
```
Or<br>
```bash
[sudo] python3 ./direct_mask_generation.py
```
You will find the results in the folder: *direct_mask*.

**2. Masks evaluations**
```bash
[sudo] python ./mask_similarity_coefficient.py
```
Or<br>
```bash
[sudo] python3 ./mask_similarity_coefficient.py
```
The output file is *fitted_mask_evaluation.txt*. However, we also presented its Excel version (***fitted_mask_evaluation.xlsx***) in this repository.

**Note**: The benchmark masks come from the **DRIVE** dataset. You can access them from [here](https://drive.grand-challenge.org/). And our evaluation demo just shows the results between the benchmark masks and the ellipse-fitted masks (the results in the *recovering_mask* folder). However, the results between the benchmark masks and the direct generation masks are listed in the file -- *direct_mask_evaluation.xlsx*. Actually, you can get this file (but the format is ***txt***) by changing several command-lines:

## Related
