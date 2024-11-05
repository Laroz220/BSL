#!/bin/bash

export C_HOME="$(cd "$(dirname "$BASH_SOURCE")" && cd .. && pwd -P)"

echo Home is: $C_HOME
source $C_HOME/sys/env/brainsurf/bin/activate

# Export software version for update
source $C_HOME/sys/version.sh

# Cleanup from install prior runs
rm -f $C_HOME/setup.sh /dev/null 2>&1
rm -f $C_HOME/bin/max_jobs.txt
rm -f $C_HOME/bin/gpu_mode.txt

# Create a new max_jobs.txt with the integer 1
echo 1 > $C_HOME/bin/max_jobs.txt
echo FALSE > $C_HOME/bin/gpu_mode.txt

# Run the Python script
python $C_HOME/sys/pipeline_gui.py
