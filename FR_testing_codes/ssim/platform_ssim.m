function [ ] = platform_ssim( )
%% It is the platform of some IQA algorithms
% Author: YSL; E-mail: ysl1abx@gmail.com
clc;

%% getting file part
%batch processing
%getting the image files
temp = pwd;  
fracture = strsplit(temp, '\');
father_folder = fracture(1, 1:end-2);
image_folder = 'recovery';
path = fullfile(father_folder{1,:}, image_folder);

if isequal(path,0)
   disp('User selected Cancel');
   errordlg('not a path selected, the program will exit','Error! Please select a file path');
   error('Program exception');
else
   disp(['User selected ; ', path]);
end

A = dir(fullfile(path,'*.png'));% change to your image format, the default of this program is png.

if isequal(isempty(A),1)
   disp('Not contains any files');
   errordlg('not a correct selection, the program will exit','Error! Please select the right postfix');
   error('Program exception');
else
   disp('processing... ');
end

N = natsortfiles({A.name}); % sorting file names into the alphabetical order

%% border adding images
reference_folder1 = 'boder_adding_image';
path1 = fullfile(father_folder{1,:}, reference_folder1);

if isequal(path1,0)
   disp('User selected Cancel');
   errordlg('not a path selected, the program will exit','Error! Please select a file path');
   error('Program exception');
else
   disp(['User selected ; ', path1]);
end

%% recorrected images
reference_folder2 = 'recorrected_image';
path2 = fullfile(father_folder{1,:}, reference_folder2);

if isequal(path2,0)
   disp('User selected Cancel');
   errordlg('not a path selected, the program will exit','Error! Please select a file path');
   error('Program exception');
else
   disp(['User selected ; ', path2]);
end

%% saving part
saving_folder = 'fr_results';
savepath = fullfile(father_folder{1,:}, saving_folder);

prefix = 'ssim_matlab_result';

XlsxFilename = strcat(prefix,'.xlsx');
XlsxFile = fullfile(savepath,XlsxFilename);

%will delete the existed file
if (exist(XlsxFile,'file') == 2) 
    delete(XlsxFile);
end

%% main 
ConvertFrameNum = numel(N); %get the number of files

M=[];
M1=[];
M_Y=[];
M_Y1=[];
M_mean=[];
M_mean1=[];
image_name = {};

for k = 1 : ConvertFrameNum
    %get files one by one
    recovery = fullfile(path,N{k});
    
    %border_adding image
    name = strsplit(N{k}, '_recovered');
    border_name = strcat(name{1}, '_border_adding_image', '.png');
    border_adding_image = fullfile(path1, border_name);
    
    %recorrected image
    recorrected_name = strcat(name{1}, '_recorrected_image', '.png');
    recorrected_image = fullfile(path2, recorrected_name);
    
    %reading all images
    %recovery
    recovery = double(imread(recovery));
    %border_adding
    border_adding_image = double(imread(border_adding_image));
    %recorrected
    recorrected_image = double(imread(recorrected_image));
   
    %single channel for R, G or B
    %discomposing all channels
    %recovery
    R_recovery = recovery(:,:,1);
    G_recovery = recovery(:,:,2);
    B_recovery = recovery(:,:,3);
    
    %border adding
    R_border = border_adding_image(:,:,1);
    G_border = border_adding_image(:,:,2);
    B_border = border_adding_image(:,:,3);
    
    %recorrected image
    R_recorrected = recorrected_image(:,:,1);
    G_recorrected = recorrected_image(:,:,2);
    B_recorrected = recorrected_image(:,:,3);
    
    %converting RGB to YCrCb
    YCrCb_recovery = rgb2ycbcr(recovery);
    YCrCB_border = rgb2ycbcr(border_adding_image);
    YCrCB_recorrected = rgb2ycbcr(recorrected_image);
    
    Y_recovery = YCrCb_recovery(:,:,1);
    Y_border = YCrCB_border(:,:,1);
    Y_recorrected = YCrCB_recorrected(:,:,1);
    
    %direct RGB
    [direct_postprocessed_vs_origin_ssim, ~] = ssim(recovery, border_adding_image);
    [direct_postprocessed_vs_masked_ssim,~] = ssim(recovery, recorrected_image);
    
    %mean RGB
    [R_postprocessed_vs_origin_ssim, ~] = ssim(R_recovery, R_border);
    [G_postprocessed_vs_origin_ssim, ~] = ssim(G_recovery, G_border);
    [B_postprocessed_vs_origin_ssim, ~] = ssim(B_recovery, B_border);
    
    mean_rgb_postprocessed_vs_origin_ssim = (R_postprocessed_vs_origin_ssim + G_postprocessed_vs_origin_ssim + B_postprocessed_vs_origin_ssim) / 3.0;
    
    [R_postprocessed_vs_masked_ssim, ~] = ssim(R_recovery, R_recorrected);
    [G_postprocessed_vs_masked_ssim, ~] = ssim(G_recovery, G_recorrected);
    [B_postprocessed_vs_masked_ssim, ~] = ssim(B_recovery, B_recorrected);
    
    mean_rgb_postprocessed_vs_masked_ssim = (R_postprocessed_vs_masked_ssim + G_postprocessed_vs_masked_ssim + B_postprocessed_vs_masked_ssim) / 3.0;
        
    %Y channel
    [Y_postprocessed_vs_origin_ssim, ~] = ssim(Y_recovery, Y_border);
    [Y_postprocessed_vs_masked_ssim,~] = ssim(Y_recovery, Y_recorrected);
    
    M(k,1) = direct_postprocessed_vs_origin_ssim;
    M1(k,1) = direct_postprocessed_vs_masked_ssim;
    M_Y(k,1) = Y_postprocessed_vs_origin_ssim;
    M_Y1(k,1) = Y_postprocessed_vs_masked_ssim;
    M_mean(k,1) = mean_rgb_postprocessed_vs_origin_ssim;
    M_mean1(k,1) = mean_rgb_postprocessed_vs_masked_ssim;
    image_name{k, 1} = name{1};

end

title = {'name', 'Y_channel:postprocessed_vs_origin', 'Y_channel:postprocessed_vs_masked', 'RGB_mean_value:postprocessed_vs_origin', 'RGB_mean_value:postprocessed_vs_masked', 'direct_postprocessed_vs_origin_ssim','direct_postprocessed_vs_masked_ssim'};
temp = [image_name, num2cell(M_Y), num2cell(M_Y1), num2cell(M_mean), num2cell(M_mean1) , num2cell(M), num2cell(M1)];

result = [title; temp];

xlswrite(XlsxFile, result);

end

