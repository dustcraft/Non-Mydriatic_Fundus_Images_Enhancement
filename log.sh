#!/bin/bash

while getopts ":p" OPTION ; do
        case $OPTION in
                p) para="${para} argument $1 = $2;";;
                *) echo "unknown parameter $1." ; exit 1 ; break;;
        esac
done

if [ -n "$1" ]
then
	echo "Note the parameter!"
else
	echo "Please enter a parameter (ACE executable path)!"; exit -1;
fi

if [ -n "$2" ]
then
	echo "OK!"
else
	echo "Please enter a ACE executable path!"; exit -1;
fi

echo $para
PARA=$2

t=$(date +%Y-%m-%d_%H:%M:%S)

FILENAME=ACE_procedure #change to your log file name

DIRECTION=$(pwd)

LOG=$DIRECTION/$FILENAME.log   #log file direction and prefix

SCRIPT=$DIRECTION/ace.sh

#create new log file
if [ ! -f "$LOG" ]; then  
    echo $LOG "is created"
    touch "$LOG"
    echo "**********" > $LOG
    echo "$t" >> $LOG
    echo "**********" >> $LOG
    var=`bash $SCRIPT $PARA`
    GLOG_logtostderr=1 echo "$var" 2>&1 | tee -a $LOG
else
    echo $LOG "has existed! It will be deleted first and then be created!"
    rm -rf $LOG
    touch "$LOG"
    echo "**********" >> $LOG
    echo "$t" >> $LOG
    echo "**********" >> $LOG
    var=`bash $SCRIPT $PARA`
    GLOG_logtostderr=1 echo "$var" 2>&1 | tee -a $LOG
fi
