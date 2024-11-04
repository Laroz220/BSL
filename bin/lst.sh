#!/bin/bash

#MODIFY OPTIONAL (matlab runtime PATH)
# Set MATLAB path to refined $PATH at ~/.bashrc

# export matlab path if not already set
# export PATH=$PATH:$HOME/path/to/matlab_version/bin

file="$C_HOME/bin/paths.txt"

# Initialize variables to hold the paths
matlab_path=""

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
        fi

    done < "$file"
else
    echo "File not found: $file"
fi

# Set the Matlab environment
export PATH=$PATH:$matlab_path

echo -e "\n****************************************************************************************************\n"
echo -e "Initializing Lesions Segmentation Toolbox (LST) 3.0\n"
echo -e "****************************************************************************************************\n"

# KAPPA 0.3 - some subcortical lesions are missed in centrum semiovale
# Kappa 0.2 - Same as 0.3
# Kappa 0.1 - lesion volume detected* sucortical not included, but increased sensitivity for periventricular

LST_PATH="$C_HOME/bin/spm12/toolbox/LST"; SPM_PATH="$C_HOME/bin/spm12"; TEMP_DIR=$C_HOME/Data/TEMP_DIR; LST_DIR=$C_HOME/OUTPUT/LST; LST_DIR_TEMP="$LST_DIR/TEMP"
data_directory=$C_HOME/Data/BIDS

source $C_HOME/bin/max_jobs.sh
current_jobs=0

cd $C_HOME/OUTPUT/LST

for study_folder in "$data_directory"/*; do
    study=$(basename "$study_folder")
    
    if [ "$study" = "cross_sectional_data" ] || [ "$study" = "longitudinal_data" ]; then
        continue
    fi
    
    for subject_folder in "$study_folder"/sub-*/; do
        subject=$(basename "$subject_folder")

        for session_folder in "$subject_folder"/*/; do
            session=$(basename "$session_folder")

            echo "Processing Study: $study, Subject: $subject, Session: $session"

            # Find T1w and T2w files
            t1w_files=($(ls "$session_folder/anat"/*T1w* 2>/dev/null | grep -E 'space|cube|mprage|bravo' | grep -E -v 'CE' | grep '\.nii\.gz$'))
            t2w_files=($(ls "$session_folder/anat"/*T2w* 2>/dev/null | grep -E 'flair' | grep '\.nii\.gz$'))

            # Create directories if they don't exist
            mkdir -p "$LST_DIR"/"$study"/"$subject"_"$session"/t1w
            mkdir -p "$LST_DIR"/"$study"/"$subject"_"$session"/t2w

            # Copy and decompress T1w files
            for t1w_file in "${t1w_files[@]}"; do
                rsync -av --quiet "$t1w_file" "$LST_DIR"/"$study"/"$subject"_"$session"/t1w
                gunzip "$LST_DIR"/"$study"/"$subject"_"$session"/t1w/$(basename "$t1w_file")
            done

            # Copy and decompress T2w files
            for t2w_file in "${t2w_files[@]}"; do
                rsync -av --quiet "$t2w_file" "$LST_DIR"/"$study"/"$subject"_"$session"/t2w
                gunzip "$LST_DIR"/"$study"/"$subject"_"$session"/t2w/$(basename "$t2w_file")
            done

            T1W_input=$(find "$LST_DIR/$study" -type f -name "${subject}_${session}_T1w*.nii" -print -quit)
            T2W_input=$(find "$LST_DIR/$study" -type f -name "${subject}_${session}_T2w*.nii" -print -quit)

            # Define the MATLAB command with additional flags
            matlab_cmd="addpath('$LST_PATH'); addpath('$SPM_PATH'); set(0,'DefaultFigureVisible','off'); ps_LST_lga('$T1W_input', '$T2W_input', 0.3, 50, 1); exit;"

            # Run MATLAB in headless mode without GUI elements, suppressing all popups
            matlab -nodisplay -nosplash -nodesktop -batch "$matlab_cmd" &


            # Increment current job count
            ((current_jobs++))

            # Wait if max jobs are running
            if [ "$current_jobs" -ge "$MAX_JOBS" ]; then
                wait -n  # Wait for the first background job to finish
                ((current_jobs--))  # Decrement job count after one finishes
            fi
        
        done
    done
done

# Wait for all background jobs to finish
wait
