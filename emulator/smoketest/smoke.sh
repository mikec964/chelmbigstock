#!/usr/bin/env bash

# smoke test for Hadoop Streaming emulator for Python
# Initial: Nov 23, 2014
# Author: Hideki Ikeda

INPUT='input'
OUTPUT='output'
MAPPER='wc_mapper.py'
REDUCER='wc_reducer.py'

function test_simple {
	local CMD="$1 ../hdemu.py -input $INPUT -output $OUTPUT -mapper $MAPPER -reducer $REDUCER"
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

echo
echo '**********************'
echo '**** Test Summary ****'
echo '**********************'
show_result 'python2.7' $simple27
show_result 'python3' $simple3

echo 'Done.'
