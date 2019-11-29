#!/bin/bash

#getting current folder
CURRENT=$(pwd)

#the executable variable of ACE
ACE=$1/ace

DATA=$CURRENT/usm
SAVE=$CURRENT/ace

echo "processing..."
rm -rf $SAVE
mkdir $SAVE

file=${DATA}"/*"

for images in $file;
do
  temp=${images##*/};
  image_name=${temp%.*};
  suffix=${images##*.};
  clip=${image_name%_*};
  full_name=${clip}"_ace."${suffix};
  save=${SAVE}"/"${full_name};
  echo $save;
  ($ACE -a 8 -w G:15 -m poly:7 -q 100 $images $save);
done;

echo "done."
