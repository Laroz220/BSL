#!/bin/bash

SCRIPT_FOLDER="$C_HOME/bin"
FILE_PATH="$SCRIPT_FOLDER/gpu_mode.txt"

# Check if the file exists
if [ -f "$FILE_PATH" ]; then

    GPU=$(<"$FILE_PATH")

    # Export MAX_JOBS as an environment variable
    export GPU

    # Print confirmation
    echo "[INFO]: GPU processing has been set to $GPU"

else
    echo "[INFO]: $FILE_PATH does not exist. Using default mode: CPU"
    export GPU=FALSE
fi
