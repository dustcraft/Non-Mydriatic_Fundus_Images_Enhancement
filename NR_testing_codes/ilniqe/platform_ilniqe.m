function [ ] = platform_ilniqe( )
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

prefix = 'ILNIQE_matlab_result';

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
image_name = {};

%To assess the quality of a given image

templateModel = load('templatemodel.mat');
templateModel = templateModel.templateModel;
mu_prisparam = templateModel{1};
cov_prisparam = templateModel{2};
meanOfSampleData = templateModel{3};
principleVectors = templateModel{4};

for k = 1 : ConvertFrameNum
    %get files one by one
    recovery = fullfile(path,N{k});
    name = strsplit(N{k}, '_recovered');
    
    %reading all images
    %recovery
    recovery = double(imread(recovery));
    
    %converting RGB to YCrCb
    YCrCb_recovery = rgb2ycbcr(recovery);
    
    Y_recovery = YCrCb_recovery(:,:,1);
    
    %direct RGB 
    direct_postprocessed_ilniqe = real(computequality(recovery,mu_prisparam,cov_prisparam,principleVectors,meanOfSampleData));

    %Y channel
    %change to 3 channels
    multichannel = cat(3, Y_recovery, Y_recovery ,Y_recovery);
    Y_postprocessed_ilniqe = real(computequality(multichannel,mu_prisparam,cov_prisparam,principleVectors,meanOfSampleData));
    
    M(k,1) = direct_postprocessed_ilniqe;
    M_Y(k,1) = Y_postprocessed_ilniqe;
    image_name{k, 1} = name{1};

end

title = {'name', 'Y_channel', 'direct_postprocessed'};
temp = [image_name, num2cell(M_Y), num2cell(M)];

result = [title; temp];

xlswrite(XlsxFile, result);

end