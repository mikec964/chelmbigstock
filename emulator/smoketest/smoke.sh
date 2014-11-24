#!/usr/bin/env bash

# smoke test for Hadoop Streaming emulator for Python
# Initial: Nov 23, 2014
# Author: Hideki Ikeda

INPUT='input'
OUTPUT='output'

function test_simple {
	local CMD="$1 ../hdemu.py -input $INPUT -output $OUTPUT -mapper wc_mapper.py -reducer wc_reducer.py"
	echo $CMD
	eval $CMD

	# evaluate the test result
	if [ ! -e $OUTPUT ] ; then
		test_result=2
	else
		diff -q 'output/part-00000' 'expected/part-00000'
		test_result=$?
	fi

	# clean up
	if [ -e $OUTPUT ] ; then
		echo 'Cleaning up...'
		rm -rf $OUTPUT
	fi
}

function test_file {
	local CMD="$1 ../hdemu.py -input $INPUT -output $OUTPUT -mapper f_mapper.py -reducer f_reducer.py -files f_file.txt"
	echo $CMD
	eval $CMD

	# evaluate the test result
	if [ ! -e $OUTPUT ] ; then
		test_result=2
	else
		diff -q 'output/part-00000' 'expected/f-00000'
		test_result=$?
	fi

	# clean up
	if [ -e $OUTPUT ] ; then
		echo 'Cleaning up...'
		rm -rf $OUTPUT
	fi
}

function show_result {
	case $2 in
		0)
			echo $1 Succeeded
			;;
		1)
			echo $1 DIFFERENT from expected
			;;
		2)
			echo $1 NO RESULT
			;;
		*)
			echo $1 Unknown error code
	esac
}

# delete the result of the emulator, if any
if [ -e $OUTPUT ] ; then
	echo 'Deleting the previous result...'
	rm -rf $OUTPUT
fi

# test on both python 2.7 and python 3.x
test_simple 'python'
simple27=$test_result
test_simple 'python3'
simple3=$test_result

test_file 'python'
file27=$test_result
test_file 'python3'
file3=$test_result

echo
echo '**********************'
echo '**** Test Summary ****'
echo '**********************'
show_result 'Simple on python2.7' $simple27
show_result 'Simple on python3' $simple3
show_result 'File on python2.7' $file27
show_result 'File on python3' $file3

echo 'Done.'
