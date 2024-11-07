#!/bin/bash

SCT_HOME=$HOME/sct_6.4/bin
TEMP_DIR=$C_HOME/Data/TEMP_DIR

cd $SCT_HOME

input_dir="$TEMP_DIR/Surf" # Destination directory
output_dir="$C_HOME/OUTPUT/SCT"

source $C_HOME/bin/max_jobs.sh

for subject_folder in "$input_dir"/*; do
    study=$(basename "$subject_folder")
    
    if [ "$study" = "Docker_img" ]; then
        continue
    fi

    for subject_file in "$subject_folder"/*T1w*nii.gz; do
        echo Found: "$subject_file"

        subject=$(basename "$subject_file")
        echo Processing file: $subject

        subject_no_suffix="${subject%%_T1w-*}"

        # Start the job in the background
        ./sct_deepseg_sc -i "$subject_file" -c t1 -ofolder "$output_dir"/"$study" &
        ((++count % $MAX_JOBS == 0)) && wait

    done
done

# Wait for all background jobs to finish
wait
