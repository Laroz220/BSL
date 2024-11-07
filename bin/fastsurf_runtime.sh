#!/bin/bash

#Data preparation prior to Free-/Fast, LGI and LST

version=2.3.2

# Set directories
TEMP_DIR=$C_HOME/Data/TEMP_DIR
BIDS_dir="$C_HOME/Data/BIDS" # Source directory
destination_dir="$TEMP_DIR/Surf" # Destination directory

# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

# Target file
file="$C_HOME/bin/paths.txt"

# Initialize variables to hold the paths
freesurfer_path=""

# Check if the file exists and is a file
if [[ -f "$file" ]]; then
    while IFS= read -r line; do
        if [[ -z "$line" ]]; then
            echo "Warning: Empty line found."
            continue
        fi

        if [[ "$line" == FREESURFER=* ]]; then
            freesurfer_path="${line#FREESURFER=}"
            # Use eval to expand $HOME and any other variables
            eval freesurfer_path="$freesurfer_path"
            echo "Extracted and expanded FREESURFER path: '$freesurfer_path'"
        fi
    done < "$file"
else
    echo "File not found: $file"
fi

export FREESURFER_HOME="$freesurfer_path"
export FASTSURFER_HOME="$C_HOME/sys/libraries/FastSurfer"

source $C_HOME/bin/max_jobs.sh
source $C_HOME/bin/gpu_mode.sh

export SUBJECTS_DIR="$C_HOME/OUTPUT/FastSurfer"
source $FREESURFER_HOME/SetUpFreeSurfer.sh

# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

USE_GPU=$GPU  # Change to false to disable GPU

if [ "$USE_GPU" = TRUE ]; then
    GPU_FLAG="cuda"
else
    GPU_FLAG="cpu"
fi

cd $FASTSURFER_HOME

source ~/miniconda3/bin/activate
source activate fastsurfer

# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

for subject_folder in "$destination_dir"/*; do
    study=$(basename "$subject_folder")
    
    if [ "$study" = "Docker_img" ]; then
        continue
    fi

    # Iterate through subject files and run FastSurfer Docker containers in groups (optionally)
    for subject_file in "$subject_folder"/*T1w*nii.gz; do
        echo $subject_file
        
        subject=$(basename "$subject_file")
        subject_no_suffix="${subject%%_T1w-*}"

        echo $subject_no_suffix

        # NB! If fastsurfer fails at asegdkt during startup, this is most likely due to RAM-issues (RAM or VRAM, depending on CPU/GPU-usage)
        # MRIs with high spatial resolution demand a very high amount of RAM/VRAM

        ./run_fastsurfer.sh --sid sub-0001 --sd $SUBJECTS_DIR/$study --t1 $subject_file --device $GPU_FLAG &
        ((++count % $MAX_JOBS == 0)) && wait
    done
done

# Wait for all background jobs to finish
wait

# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

echo -e "\n[INFO] FastSurfer [v$version]: Processing completed for all subjects""!""\n\n****************************************************************************************************\n"
