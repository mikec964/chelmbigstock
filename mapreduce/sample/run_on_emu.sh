#!/usr/bin/env bash

# Sample script to run the stock MapReduce on the emulator
# Author: Hideki Ikeda
# Mar 6, 2015

# If you want to debug the mapreduce, uncomment the line right below
# DEBUG=1

# Directory of the mapper / reducer
MAPREDUCE_PATH=~/git/chelmbigstock/mapreduce

# Directory of input data for the mapper
MR_INPUT_DIR=~/git/chelmbigstock/mapreduce/input

# Directory of result from the reducer
MR_OUTPUT_DIR=~/git/chelmbigstock/mapreduce/output

# The emulator directory
EMULATOR_DIR=~/git/pyhdemu

if [ -e $MR_OUTPUT_DIR ] ; then
	rm -rf $MR_OUTPUT_DIR
fi

if [ $DEBUG -eq 1 ]; then
	echo Debug flag is on!
	MR_INTERIM_DIR=~/git/chelmbigstock/mapreduce/interim
	if [ -e $MR_INTERIM_DIR ] ; then
		rm -rf $MR_INTERIM_DIR
	fi
	OPT_INTERIM="-interim $MR_INTERIM_DIR"
fi

python ${EMULATOR_DIR}/hdemu.py -input ${MR_INPUT_DIR}/stock.csv -output $MR_OUTPUT_DIR -mapper ${MAPREDUCE_PATH}/mapper.py -reducer ${MAPREDUCE_PATH}/reducer.py -files ${MR_INPUT_DIR}/options.csv $OPT_INTERIM
