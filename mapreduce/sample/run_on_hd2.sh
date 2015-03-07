#!/usr/bin/env bash

# Sample script to run the stock MapReduce on Hadoop 2.x
# Author: Hideki Ikeda
# Mar 7, 2015

echo '************************************'
echo 'Stock anlyze MapReduce on Hadoop 2.x'
echo '************************************'

# Hadoop root directory
HD_ROOT=/usr/local/hadoop-2.6.0

# directories on HDFS
HD_INPUT=input
HD_OUTPUT=output

# Local directory of the mapper / reducer
LOCAL_MR_PATH=~/git/chelmbigstock/mapreduce

# Local data directories
LOCAL_INPUT_DIR=${LOCAL_MR_PATH}/input
LOCAL_OUTPUT_DIR=${LOCAL_MR_PATH}/output

# File name of stock data
FN_STOCK=stock.csv

echo - checking the input directory on HDFS
${HD_ROOT}/bin/hdfs dfs -ls $HD_INPUT > /dev/null
if [ $? -eq 0 ]
then
	echo OK
else
	echo - making the input dir on HDFS
	${HD_ROOT}/bin/hdfs dfs -mkdir $HD_INPUT
fi

echo - checking the data on HDFS
${HD_ROOT}/bin/hdfs dfs -ls ${HD_INPUT}/${FN_STOCK} > /dev/null
if [ $? -eq 0 ]
then
	echo OK
else
	echo - copying the input data to HDFS
	${HD_ROOT}/bin/hdfs dfs -copyFromLocal ${LOCAL_INPUT_DIR}/${FN_STOCK} $HD_INPUT
fi

echo - running MapReduce on Hadoop
HDCMD="${HD_ROOT}/bin/hadoop jar ${HD_ROOT}/share/hadoop/tools/lib/hadoop-streaming*.jar -files ${LOCAL_MR_PATH}/mapper.py,${LOCAL_MR_PATH}/reducer.py,${LOCAL_INPUT_DIR}/options.csv -input $HD_INPUT -output $HD_OUTPUT -mapper mapper.py -reducer reducer.py"
#echo $HDCMD
eval $HDCMD
if [ $? -ne 0 ]
then
	exit
fi

echo - getting data from HDFS
${HD_ROOT}/bin/hdfs dfs -copyToLocal ${HD_OUTPUT}/* ${LOCAL_OUTPUT_DIR}
if [ $? -ne 0 ]
then
	echo Failed to copy output files to local. Copy them manually.
	exit
fi
ls -l ${LOCAL_OUTPUT_DIR}

echo - removing the output directory on HDFS
${HD_ROOT}/bin/hdfs dfs -rm -R $HD_OUTPUT
