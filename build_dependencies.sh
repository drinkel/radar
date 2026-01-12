#!/bin/bash

# DRY_RUN=true                                           # comment out or set to false to disable dry run
SCRIPT_PATH=$(cd `dirname ${BASH_SOURCE[0]}`; pwd)
TMP_DIR=/tmp/

# if building on node, we will use ramdisk as a temporary dir
if [[ -d /ramdisk/$PBS_JOBID ]]; then
    TMP_DIR=/ramdisk/$PBS_JOBID
fi

# Karolina specific
if [[ $(uname -a) == *"karolina"* ]]; then
    echo "Building karolina specific modules"
    EB_PREFIX_PATH=${SCRIPT_PATH}/.easybuild_karolina
    PACKAGES=""

# Barbora specific
elif [[ $(uname -a) == *"barbora"* ]]; then
    echo "Building barbora specific modules"
    EB_PREFIX_PATH=${SCRIPT_PATH}/.easybuild_barbora
    # PACKAGES="
    # Qt5-5.15.2-GCCcore-10.2.0
    # Tkinter-3.8.6-GCCcore-10.2.0.eb
    # Graphviz-2.47.0-GCCcore-10.2.0-Java-11.eb
    # "
    # PACKAGES="
    # Graphviz-2.50.0-GCCcore-11.2.0.eb
    # PyQt5-5.15.4-GCCcore-11.2.0.eb
    # "
     PACKAGES=""

else
    echo "Unknown cluster or local environment, exiting!"
    exit 1
fi

echo "
DRY_RUN         = $DRY_RUN
EB_PREFIX_PATH  = $EB_PREFIX_PATH
PACKAGES        = $PACKAGES
"

module load EasyBuild
module use  $EB_PREFIX_PATH

if [[ $PACKAGES == "" ]]
then
    echo "Empty packages"
    exit 1
fi

if [[ $DRY_RUN == true ]]; then
    eb -D --tmpdir=${TMP_DIR} --buildpath=${TMP_DIR} --prefix=$EB_PREFIX_PATH  $PACKAGES
else
    eb --robot --tmpdir=${TMP_DIR} --buildpath=${TMP_DIR} --prefix=$EB_PREFIX_PATH  $PACKAGES
fi