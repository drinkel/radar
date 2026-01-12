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
echo 'Activating prepared virtual environment:'
run_command "source ${RADAR_VENV_DIR}/bin/activate"
echo 'Done'

echo $HLINE
echo 'Installing PyInstaller into the prepared virtual environment:'
run_command 'python3 -m pip install --no-color pyinstaller'
echo 'Done'

echo $HLINE
echo 'Compiling RADAR visualizer into binary:'
RADAR_SCRIPT=runRadarGUI_analyze.py
run_command "pyinstaller -y --log-level WARN --onefile --paths src $RADAR_SCRIPT --name RADARvisualizer --distpath bin"
echo 'Done'

deactivate
