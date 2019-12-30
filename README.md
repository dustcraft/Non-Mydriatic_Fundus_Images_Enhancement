# Non-Mydriatic Fundus Images Enhancement

## Overview

![front](https://github.com/dustcraft/Non-Mydriatic_Fundus_Images_Enhancement/raw/master/video_start1(1).png)

&ensp;&ensp;Our enhancement pipeline is a static and hands-off algorithm tree. It is used to enhance both mydriatic and non-mydriatic fundus images. Besides, our enhancement method can also remove overexposure and underexposure in the image like the Dodging and Burning technique. More important, you only need to keyboard several simple command-lines to test our pipeline.
  
## More Details
&ensp;&ensp;Our pipeline is a hybrid language toolbox for enhancing and reconstructing fundus images. This pipeline is made up of a set of fundus image processing methods to cope with a series of tasks, such as dehazing, denoising, region extension, unbalanced illuminance removal, and texture enhancement. There are four important stages in this workflow as shown below.<br>
  
  ![Pipeline](https://github.com/dustcraft/Non-Mydriatic_Fundus_Images_Enhancement/raw/master/Figure3(2).png)
  
  
  This hybrid language toolbox provides the following methods:<br>
  1. Mask generation: generating the mask of an input fundus image, implemented by Python<br>
  2. Region extension: extending the FOV region of the fundus image from ellipse to rectangle, implemented by Python<br>
  3. Image enhancement: providing dehazing, denoising and texture enhancing operations, implemented by both Python and C<br>
  4. Color restoration: restoring the color of the enhanced image, implemented by Python<br>

## Dependencies
&ensp;&ensp;This repository is the integration of our pipeline algorithms, and it also contains some standalone third-party software which we have used. However, these codes rely on some extra libraries.

A. Python part<br>
&ensp;&ensp;The Python codes use several python modules, but some of them are not the default packages (or the standard libraries) of Python. So, please install the following required python modules:<br>

 Package      | Tested version    
 ---------- | :-----------:  
 [Python](https://www.python.org/)     | 3.6.4     
 [OpenCV](https://opencv.org/)     | 3.3.1
 [SciPy](https://www.scipy.org/)     | 1.0.0
 [PIL](http://www.pythonware.com/products/pil/)     | 5.0.0
 [NumPy](https://numpy.org/)     | 1.14.2
 [Skimage](https://github.com/scikit-image/scikit-image)     | 0.13.1
 
 Tips: To install [OpenCV](https://opencv.org/) in your own directory, please carefully select the version from [here](https://opencv.org/releases/).
 
 Example:<br>
&ensp;&ensp;Through the source code:
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
We need an extra OpenCV module -- [*ximgproc*](https://github.com/opencv/opencv_contrib) -- to perform our algorithms, but it does not belong to the official OpenCV distribution. So, you should install this extra package -- *Opencv-contrib*.

&ensp;&ensp;Besides, to make the OpenCV can work with Python IDE, like [Anaconda3](https://www.anaconda.com/), you may need to follow the guide of [Install OpenCV for Anaconda](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#) to setup OpenCV. If you use the Anaconda3 IDE, the extra release -- *Opencv-contrib* -- will be installed with the official OpenCV distribution by default.

&ensp;&ensp;Because most of the other modules are heavily dependent on *NumPy* module, we recommend you to use the Python IDE, such as Anaconda3. If not, please install appropriate packages for your development environment (Python versions, 32-bit or 64-bit)

B. Other part (C part)<br>
&ensp;&ensp;The modified ACE algorithm, which has been developed by **Pascal Getreuer**, is a part of our enhancement method. You can find the details from [here](http://www.ipol.im/pub/art/2012/g-ace/article_lr.pdf). And its zip file is available [here](http://www.ipol.im/pub/art/2012/g-ace/).

## How to Use
&ensp;&ensp;You can test the whole pipeline with several simple Python command-lines. And these commands will start processing the test images in this directory then generate their enhanced outputs in the corresponding folders.

**1. Generating border-adding-images, first-filtered, recorrected-image, recovering-mask, and usm**<br>
```bash
[sudo] python ./synthesize.py # Only python3 is in your computer
```
Or<br>
```bash
[sudo] python3 ./synthesize.py # When both python2 and python3 are in your environment
```

&ensp;&ensp;Their results are in the corresponding folders: *border_adding_image*, *first_filtered*, *recorrected_image*, *recovering_mask*, *usm*.

![affine](https://github.com/dustcraft/Non-Mydriatic_Fundus_Images_Enhancement/raw/master/affine_image1.png)<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;A sample of the extension result<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;This image is generated from ***10_left*** (which is from the Kaggle sample dataset) by affine transformation.

**Note**: We only generate the masks after ellipse-fitting (***the recovering masks***) by default. And the existed data will be replaced when you run this command-line. The default format of output images is **PNG**.

&ensp;&ensp;If you want to generate the original masks (just be polished by some morphological operations), you could run:<br>
```bash
[sudo] python ./direct_mask_generation.py
```
Or<br>
```bash
[sudo] python3 ./direct_mask_generation.py
```
&ensp;&ensp;You will find the results in the folder: *direct_mask*.

**2. Masks evaluations**
```bash
[sudo] python ./mask_similarity_coefficient.py
```
Or<br>
```bash
[sudo] python3 ./mask_similarity_coefficient.py
```
&ensp;&ensp;The output file is *fitted_mask_evaluation.txt*. However, we also presented its Excel version (***fitted_mask_evaluation.xlsx***) in this repository.

**Note**: The benchmark masks come from the **DRIVE** dataset. You can access them from [here](https://drive.grand-challenge.org/). And our evaluation demo just shows the results between the benchmark masks and the ellipse-fitted masks (the results in the *recovering_mask* folder). However, the results between the benchmark masks and the direct generation masks are listed in the file -- *direct_mask_evaluation.xlsx*. Actually, you can get this file (but the format is ***txt***) by changing several command-lines:

```python
    #creating the new text file
    #!Note: we will delete the existed results text file.
    #file_operation('fitted_mask_evaluation.txt') <-comment this line
    file_operation('direct_mask_evaluation.txt') # <-adding this line
    

    for images in os.listdir(image_path):
        full_path = os.path.join(image_path, images)
        if os.path.isdir(full_path):
            continue
        file = os.path.normcase(full_path)
                
        temp = os.path.splitext(images)[0]
        image_name = temp.split('_mask')[0]
        #target_image = files('recovering_mask', image_name, '_recovering_mask.png') <-comment this line
        target_image = files('direct_mask', image_name, '_auto_threshold.png') # <-adding this line
                
        (image_name, outputs) = main(file, target_image)
        #result_saving('fitted_mask_evaluation.txt', image_name, saving_evaluation, outputs) <-comment this line
        result_saving('direct_mask_evaluation.txt', image_name, saving_evaluation, outputs) # <-adding this line
```

**3. ACE processing**

```bash
[sudo] chmod 777 ace.sh log.sh
[sudo] bash ./log.sh -p /path/to/your/ace/installation/folder
```

For instance:<br>
```bash
[sudo] chmod 777 ./ace.sh ./log.sh
[sudo] bash ./log.sh -p /home/***/ace_20121029
```
&ensp;&ensp;The processing log file is *ACE_procedure.log*, and this file will be replaced when you run the command-lines above. So we still presented our log with the **pdf** format: *ACE_procedure.pdf*.

**4. Color restoration**
```bash
[sudo] python ./postprocessing.py
```
Or<br>
```bash
[sudo] python3 ./postprocessing.py
```

&ensp;&ensp;And the results are in the folders: *recovery and restoration*, respectively.

![enhancement](https://github.com/dustcraft/Non-Mydriatic_Fundus_Images_Enhancement/raw/master/enhanced_image(1).png)<br>
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;A sample of the color restred result

**5. Testing**

&ensp;&ensp;This directory has already included all of the FR (in the *FR_source_testing_codes*) and NR (in the *NR_source_testing_codes*) source codes. And we have provided their batch-running platforms in this directory. Nevertheless, you could use your own from [here](https://ece.uwaterloo.ca/~z70wang/research/iwssim/) and [here](http://live.ece.utexas.edu/research/Quality/index_algorithms.htm).

***Run***: &ensp;**platform_xxx.m** in each folder (*FR_testing_codes* and *NR_testing_codes*).<br>

&ensp;&ensp;Their results are saved in the *fr_results* and *nr_results*, respectively.

***Note***: Some algorithms need a few other third-party tools, but you can find them in the *tools*. The Python programs were tested on **Windows7**, **Windoes10**, and **Linux** (Ubuntu14.04) with Python3.6 or Anaconda3. The shell codes were only tested on **Linux** (Ubuntu14.04). The Matlab programs were tested on **Windows7**, **Windoes10** with Matlab 2013, Matlab 2016, and Matlab 2018. **Mac OS** are not officially supported.

![results](https://github.com/dustcraft/Non-Mydriatic_Fundus_Images_Enhancement/raw/master/nr_results_plot(1).jpg)

## Related
*Author*: Songlin Yan <ysl1abx@gmail.com> <br>
*URL*:

## References
1. P. Getreuer, “Automatic color enhancement (ace) and its fast implementation,” Image Processing On Line, vol. 2, pp. 266–277, 2012.
2. K. Ma, Q. Wu, Z. Wang, Z. Duanmu, H. Yong, H. Li, and L. Zhang, “Group mad competition-a new methodology to compare objective image quality models,” in Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, 2016, pp. 1664–1673.
