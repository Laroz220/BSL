#!/bin/bash

echo "This is LST-AI, an automatized lesion segmentation protocol for cross-sectional data; Initializing.."; sleep 2

#Activate the specific python environment required
source $C_HOME/sys/env/lst_ai/bin/activate

#Import 'greedy'
#export PATH="$HOME/bin:$PATH"
export PATH="$C_HOME/sys/libraries/bin:$PATH"

data_directory=$C_HOME/Data/BIDS
output=$C_HOME/OUTPUT/LST_AI

source $C_HOME/bin/max_jobs.sh
current_jobs=0

cd "$data_directory"

for study_folder in "$data_directory"/*; do
    study=$(basename "$study_folder")
    
    if [ "$study" = "cross_sectional_data" ] || [ "$study" = "longitudinal_data" ]; then
        continue
    fi
    
    for subject_folder in "$study_folder"/sub-*/; do
        # Extract subject information from folder name
        subject=$(basename "$subject_folder")

        # Iterate through sessions within the subject folder
        for session_folder in "$subject_folder"/*/; do
            # Extract session information from session folder name
            session=$(basename "$session_folder")

            echo "Processing Study: $study, Subject: $subject, Session: $session"

            t1w_files=($(ls "$session_folder/anat"/*T1w* 2>/dev/null | grep -E 'space|cube|mprage|bravo' | grep -E -v 'CE' | grep '\.nii\.gz$'))
            t2w_files=($(ls "$session_folder/anat"/*T2w* 2>/dev/null | grep -E 'flair' | grep '\.nii\.gz$'))

            for t1w_file in "${t1w_files[@]}"; do
                for t2w_file in "${t2w_files[@]}"; do
                    echo "T1w file: $t1w_file"
                    echo "T2w file: $t2w_file"

                    out_folder=$output/$study/"${subject}_${session}"

                    # Add "cpu" or "0" at the --device flag to change CPU/GPU-processing. 
                    lst --t1 $t1w_file --flair $t2w_file --output $out_folder --device cpu &

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
    done
done

# Wait for all background jobs to finish
wait

#Deactivate custom python environment when done
deactivate
