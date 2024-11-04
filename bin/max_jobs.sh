#!/bin/bash

SCRIPT_FOLDER="$C_HOME/bin"
FILE_PATH="$SCRIPT_FOLDER/max_jobs.txt"

# Check if the file exists
if [ -f "$FILE_PATH" ]; then
    # Read the MAX_JOBS value from the file
    MAX_JOBS=$(<"$FILE_PATH")

    # Export MAX_JOBS as an environment variable
    export MAX_JOBS

    # Print confirmation
    echo "MAX_JOBS has been set to: $MAX_JOBS"
else
    echo "[INFO]: $FILE_PATH does not exist. Using default at MAX_JOBS == 1"
    export MAX_JOBS="1"
fi
