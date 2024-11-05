#!/bin/bash

#Data preparation prior to Free-/Fast, LGI and LST

version=2.2.0

# Set directories
TEMP_DIR=$C_HOME/Data/TEMP_DIR
BIDS_dir="$C_HOME/Data/BIDS" # Source directory
destination_dir="$TEMP_DIR/Surf" # Destination directory

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
source $C_HOME/bin/max_jobs.sh
source $C_HOME/bin/gpu_mode.sh

# Define a function to run FastSurfer Docker container
run_fastsurfer() {
    subject_file="$1"
    # Extract subject information from file names
    subject=$(basename "$subject_file")
    subject_no_suffix="${subject%%_T1w-*}"

    # Set this variable to "true" or "false" based on whether you want to use GPU or not
    USE_GPU=$GPU  # Change to false to disable GPU

    # Construct the command with or without the GPU flag
    if [ "$USE_GPU" = TRUE ]; then
        GPU_FLAG="--gpus all"
    else
        GPU_FLAG=""
    fi

    # Run the docker command
    docker run $GPU_FLAG -v "$destination_dir/$study":/data \
        -v "$C_HOME/OUTPUT/FastSurfer:/output" \
        -v "$freesurfer_path:/freesurfer" \
        --rm --user $(id -u):$(id -g) deepmi/fastsurfer:latest \
        --fs_license /freesurfer/license.txt \
        --t1 "/data/$subject" \
        --sid "$subject_no_suffix" --sd "/output/$study" \
        --parallel --3T
}

for subject_folder in "$destination_dir"/*; do
    study=$(basename "$subject_folder")
    
    if [ "$study" = "Docker_img" ]; then
        continue
    fi

    # Iterate through subject files and run FastSurfer Docker containers in groups (optionally)
    for subject_file in "$subject_folder"/*T1w*nii.gz; do
        echo $subject_file

        # NB! If fastsurfer fails at asegdkt during startup, this is most likely due to RAM-issues (RAM or VRAM, depending on CPU/GPU-usage)
        # MRIs with high spatial resolution demand a very high amount of RAM/VRAM

        # Modify the integer to the left of "==" to define batch size
        run_fastsurfer "$subject_file" &
        ((++count % $MAX_JOBS == 0)) && wait
    done
done

# Wait for all background jobs to finish
wait

echo -e "\n[INFO] FastSurfer [v$version]: Processing completed for all subjects""!""\n\n****************************************************************************************************\n"
