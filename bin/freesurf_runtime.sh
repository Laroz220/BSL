#!/bin/bash

TEMP_DIR=$C_HOME/Data/TEMP_DIR

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
export SUBJECTS_DIR="$C_HOME/OUTPUT/FreeSurfer"; version=7.4.1

mkdir -p $SUBJECTS_DIR

source $FREESURFER_HOME/SetUpFreeSurfer.sh
source $C_HOME/bin/max_jobs.sh

BIDS_dir="$C_HOME/Data/BIDS" # Source directory
destination_dir="$TEMP_DIR/Surf" # Destination directory

# Check if the directory exists
if [ ! -d "$destination_dir" ]; then
    echo "Error: Destination directory '$destination_dir' not found."
    exit 1
fi

# Counter variable to track the number of processed subjects
subject_count=0

for subject_folder in "$destination_dir"/*; do
    study=$(basename "$subject_folder")
    
    if [ "$study" = "Docker_img" ]; then
        continue
    fi

    mkdir -p $SUBJECTS_DIR/$study

    for subject_file in "$subject_folder"/*T1w*nii.gz; do
        echo "$subject_file"
        if [ -e "$subject_file" ]; then
            ((subject_count++))
            subject=$(basename "$subject_file")
            subject_no_suffix="${subject%%_T1w-*}"

            cores_per_subject=2
            current_study="$SUBJECTS_DIR/$study"
            
            recon-all -all -i "$subject_file" -sd "$current_study" -s "$subject_no_suffix" -parallel -openmp "$cores_per_subject" &

            if grep -q "ERROR: You are trying to re-run an existing subject" recon-all.log > /dev/null 2>&1; then
                continue
            fi
            
            # Modify the integer to the left of "==" to define batch size
            if ((subject_count % $MAX_JOBS == 0)); then
                wait
            fi
        else
            echo "Error: No files found matching the pattern '$subject_folder/*T1w*nii.gz'."
        fi
    done
done

# Wait for all background processes to finish
wait

echo -e "\n[INFO] FreeSurfer [v$version]: Processing completed for all subjects""!""\n\n****************************************************************************************************\n"
