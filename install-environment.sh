#!/bin/bash

HLINE='--------------------------------------------------------------'

run_command()
{
	local COMMAND=$1
	echo "Running command: ${COMMAND}..."
	$COMMAND > /dev/null
	local RETURN_CODE=$?
	if [ $RETURN_CODE -gt 0 ]; then exit $RETURN_CODE; fi
}

if [ -z $RADAR_VENV_DIR ]
then
	RADAR_VENV_DIR='environment'
fi
echo "INFO: RADAR_VENV_DIR variable is set to: $RADAR_VENV_DIR"

echo $HLINE
echo 'Preparing virtual environment:'
run_command "python3 -m venv --clear $RADAR_VENV_DIR"
run_command "source ${RADAR_VENV_DIR}/bin/activate"
run_command 'python3 -m pip install --upgrade --no-color pip setuptools'
echo 'Done'

echo $HLINE
echo 'Installing dependencies into the prepared virtual environment:'
PYTHON_PACKAGES='scikit-learn matplotlib packaging seaborn PyQt6 pydot pyyed'
run_command "python3 -m pip install --no-color $PYTHON_PACKAGES"
echo 'Done'

deactivate
