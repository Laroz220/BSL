#!/bin/bash
#bash --version >4 not a requirement

# Target file
file="$C_HOME/bin/paths.txt"

# Initialize variables to hold the paths
matlab_path=""
freesurfer_path=""

# Check if the file exists and is a file
if [[ -f "$file" ]]; then
    while IFS= read -r line; do
        if [[ -z "$line" ]]; then
            echo "Warning: Empty line found."
            continue
        fi

        if [[ "$line" == MATLAB=* ]]; then
            matlab_path="${line#MATLAB=}"
            # Use eval to expand $HOME and any other variables
            eval matlab_path="$matlab_path"
            echo "Extracted and expanded MATLAB path: '$matlab_path'"

        elif [[ "$line" == FREESURFER=* ]]; then
            freesurfer_path="${line#FREESURFER=}"
            # Use eval to expand $HOME and any other variables
            eval freesurfer_path="$freesurfer_path"
            echo "Extracted and expanded FREESURFER path: '$freesurfer_path'"
        fi
    done < "$file"
else
    echo "File not found: $file"
fi

# Set the Matlab environment
export PATH=$PATH:$matlab_path
matlab -batch "addpath(genpath('$freesurfer_path')); savepath;"

# Set the FreeSurfer environment
export FREESURFER_HOME="$freesurfer_path"
export SUBJECTS_DIR=$C_HOME/OUTPUT/FreeSurfer

# Create the SUBJECTS_DIR directory if it doesn't exist
mkdir -p "$SUBJECTS_DIR"

# Source the FreeSurfer setup script
source "$FREESURFER_HOME/SetUpFreeSurfer.sh"

#Precautionary cleanup to avoid errors
directories=(
    "$C_HOME/OUTPUT/FreeSurfer"
    "$C_HOME/OUTPUT/FastSurfer"
)

# Iterate through the directories and search for the files
for dir in "${directories[@]}"; do
    echo "Searching in $dir"
    find "$dir" -type f -name "IsRunning.lh+rh" -exec rm -f {} \;
    echo "Deleted all 'IsRunning.lh+rh' files in $dir"
done

echo "File cleanup complete."

### FREESURFER

echo Loading LGI on FreeSurfer Data..
source $C_HOME/bin/max_jobs.sh

for study_folder in "$SUBJECTS_DIR"/*; do
    # Skip if not a directory
    if [[ ! -d "$study_folder" ]]; then
        continue
    fi

    # Loop through each subject folder
    for subject_folder in "$study_folder"/*; do
        if [[ ! -d "$subject_folder" ]]; then
            continue
        fi

        # Get the subject name from the folder path
        subject=$(basename "$subject_folder")

        if [[ "$subject" == "fsaverage" ]]; then
            echo "Skipping fsaverage folder..."
            continue  # Move to the next subject
        fi

        rm $subject/scripts/IsRunning.lh+rh;

        echo "Processing $subject_folder"; recon-all -s "$subject_folder" -localGI -sd "$study_folder" &

        # Limit the number of parallel jobs to avoid overloading the system
        if (( $(jobs | wc -l) >= $MAX_JOBS )); then  # Adjust the '4' to the number of jobs you want to run in parallel
            wait -n  # Wait for any job to finish before starting a new one
        fi
    done
done

# Wait for all background jobs to finish before exiting the script
wait

### FASTSURFER

echo Loading LGI on FastSurfer Data..

export SUBJECTS_DIR=$C_HOME/OUTPUT/FastSurfer      #Redefine directory_path
source $FREESURFER_HOME/SetUpFreeSurfer.sh

for study_folder in "$SUBJECTS_DIR"/*; do
    # Skip if not a directory
    if [[ ! -d "$study_folder" ]]; then
        continue
    fi

    # Loop through each subject folder
    for subject_folder in "$study_folder"/*; do
        if [[ ! -d "$subject_folder" ]]; then
            continue
        fi

        # Get the subject name from the folder path
        subject=$(basename "$subject_folder")

        if [[ "$subject" == "fsaverage" ]]; then
            echo "Skipping fsaverage folder..."
            continue  # Move to the next subject
        fi

        echo $subject_folder

        rm $subject/scripts/IsRunning.lh+rh;

        echo "Processing $subject_folder"; recon-all -s "$subject_folder" -localGI -sd "$study_folder" &

        # Limit the number of parallel jobs to avoid overloading the system
        if (( $(jobs | wc -l) >= 4 )); then  # Adjust the '4' to the number of jobs you want to run in parallel
            wait -n  # Wait for any job to finish before starting a new one
        fi
    done
done

# Wait for all background jobs to finish before exiting the script
wait

#Continue with Statistical mapping script... (currently being worked at)
