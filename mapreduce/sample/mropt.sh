#!
# This is a sample use of mkmropt.py
# Input:
#       input/mkmropt.ini
# Output:
#       input/result.csv

# For details about mkmropt.py, run mkmropt.py -h

CHELM_DIR=~/git/chelmbigstock
MAPRED_DIR=${CHELM_DIR}/mapreduce
SAMPLE_DIR=${MAPRED_DIR}/sample

python ${MAPRED_DIR}/mkmropt.py ${SAMPLE_DIR}/mkmropt.ini
