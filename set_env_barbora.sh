#!/bin/bash

if [[ $- != *i* ]]
then
	echo "ERROR: this script must be sourced."
	echo
	exit 1
fi

if [[ -d .easybuild_barbora/modules/all ]]
then
	module use  .easybuild_barbora/modules/all
fi

ml Graphviz/2.50.0-GCCcore-11.2.0

source environment/bin/activate

PYTHON39="$(pwd)/environment/lib/python3.9"



pip install PyQt6
export PYTHONPYCACHEPREFIX=/dev/null ### stops saving __pycache__



# Use this when using pip PyQt6 package from install script. 
# If you use PyQt6 module, this should be already taken care of.
if [ -d "$PYTHON39" ]; then
    export LD_LIBRARY_PATH=$(cd environment/lib/python3.9/site-packages/PyQt6/Qt6/lib/; pwd):${LD_LIBRARY_PATH}
fi
export PYTHONPATH=$(pwd)/src:$PYTHONPATH





#PYTHON36="$(pwd)/environment/lib/python3.6"
#PYTHON39="$(pwd)/environment/lib/python3.9"

#if [ -d "$PYTHON36" ]; then
#    export LD_LIBRARY_PATH=$(cd environment/lib/python3.6/site-packages/PyQt5/Qt5/lib/; pwd):${LD_LIBRARY_PATH}
#else
#    export LD_LIBRARY_PATH=$(cd environment/lib/python3.9/site-packages/PyQt5/Qt5/lib/; pwd):${LD_LIBRARY_PATH}
#fi





#export PYTHONPATH=$(pwd)/src:$PYTHONPATH

