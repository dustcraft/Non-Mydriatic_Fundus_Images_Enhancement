function [ ] = platform_bliinds_II( )
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

%% saving part
saving_folder = 'nr_results';
savepath = fullfile(father_folder{1,:}, saving_folder);

prefix = 'bliinds_II_matlab_result';

XlsxFilename = strcat(prefix,'.xlsx');
XlsxFile = fullfile(savepath,XlsxFilename);

%will delete the existed file
if (exist(XlsxFile,'file') == 2) 
    delete(XlsxFile);
end

%% main 
ConvertFrameNum = numel(N); %get the number of files

M=[];
M_Y=[];
M_mean=[];
image_name = {};

for k = 1 : ConvertFrameNum
    %get files one by one
    recovery = fullfile(path,N{k});
    name = strsplit(N{k}, '_recovered');
    
    %reading all images
    %recovery
    recovery = double(imread(recovery));
   
    %single channel for R, G or B
    %discomposing all channels
    %recovery
    R_recovery = recovery(:,:,1);
    G_recovery = recovery(:,:,2);
    B_recovery = recovery(:,:,3);
    
    %converting RGB to YCrCb
    YCrCb_recovery = rgb2ycbcr(recovery);
    
    Y_recovery = YCrCb_recovery(:,:,1);
    
    %direct RGB
    direct_features = bliinds2_feature_extraction(recovery);
    
    temp = direct_features;
    row_features = temp(:)';
    direct_postprocessed_bliinds_II = bliinds_prediction(row_features);
    
    %mean RGB
    R_features = bliinds2_feature_extraction(R_recovery);
    temp = R_features;
    row_features = temp(:)';
    R_postprocessed_bliinds_II = bliinds_prediction(row_features);
    
    G_features = bliinds2_feature_extraction(G_recovery);
    temp = G_features;
    row_features = temp(:)';
    G_postprocessed_bliinds_II = bliinds_prediction(row_features);
    
    B_features = bliinds2_feature_extraction(B_recovery);
    temp = B_features;
    row_features = temp(:)';
    B_postprocessed_bliinds_II = bliinds_prediction(row_features);
    
    mean_rgb_postprocessed_bliinds_II = (R_postprocessed_bliinds_II + G_postprocessed_bliinds_II + B_postprocessed_bliinds_II) / 3.0;
         
    %Y channel
    Y_features = bliinds2_feature_extraction(Y_recovery);
    temp = Y_features;
    row_features = temp(:)';
    Y_postprocessed_bliinds_II = bliinds_prediction(row_features);
    
    M(k,1) = direct_postprocessed_bliinds_II;
    M_Y(k,1) = Y_postprocessed_bliinds_II;
    M_mean(k,1) = mean_rgb_postprocessed_bliinds_II;
    image_name{k, 1} = name{1};

end

title = {'name', 'Y_channel', 'RGB_mean_value', 'direct_postprocessed'};
temp = [image_name, num2cell(M_Y), num2cell(M_mean), num2cell(M)];

result = [title; temp];

xlswrite(XlsxFile, result);

end

