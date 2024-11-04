#!/bin/bash

echo -e "\nStarting longitudinal pipeline - Analysing available data..\n\n****************************************************************************************************"
echo -e "****************************************************************************************************\n"; sleep 1
echo -e "Running FreeSurfer for unprocessed subjects..\n"; sleep 2

#Double check if freesurfer has been run for all subjects
source $C_HOME/bin/freesurf_runtime.sh

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
#export SUBJECTS_DIR="$C_HOME/OUTPUT/FreeSurfer/$study_name"

version=7.4.1

source $FREESURFER_HOME/SetUpFreeSurfer.sh

echo -e "All subjects have been processed.\n"; sleep 2

# Set your directories
BIDS_DIR="$C_HOME/Data/BIDS/longitudinal_data"
TEMP_DIR="$C_HOME/Data/TEMP_DIR/Surf/Docker_img"
DATA_DIR="$C_HOME/OUTPUT/FreeSurfer"

echo "BIDS Directory: $BIDS_DIR"
echo -e "TEMP Directory: $TEMP_DIR\n"

for study_dir in "$BIDS_DIR"/*; do
    if [ -d "$study_dir" ]; then
        study_name=$(basename "$study_dir")
        export SUBJECTS_DIR="$C_HOME/OUTPUT/FreeSurfer/$study_name"

        for file in "$study_dir"/*; do
            file_name=$(basename "$file")

            if ls "$TEMP_DIR"/*"$file_name"* > /dev/null 2>&1; then
                echo "Study: $study_name, Subject: $file_name; Found a match in longitudinal data"
                
                echo -e "\nPreparing longitudinal analysis.. Please wait\n\n****************************************************************************************************"
                echo -e "****************************************************************************************************\n"
                
                # Define your base file name
                file_name="$file_name"   #eg sub-0001

                # Define the number of sessions you want to process
                num_sessions=$(find "$file" -maxdepth 1 -type d -name "*ses-*" | wc -l)

                # Construct the recon-all command
                cmd="recon-all -base $file_name"

                # Loop to add the time points
                for ((i=1; i<=num_sessions; i++)); do
                    cmd+=" -tp \"${file_name}_ses-$(printf '%02d' $i)\""
                done

                # Add the final part of the command
                cmd+=" -all"

                # Echo the command for debugging
                echo "Running command: $cmd"

                # Execute the command
                eval $cmd

                echo -e "\nLongitudinal base processing completed\n\n****************************************************************************************************"

                for ((i=1; i<=num_sessions; i++)); do
                    session_file="${file_name}_ses-$(printf '%02d' $i)"
                    # Construct the recon-all command for longitudinal analysis
                    cmd_long="recon-all -long $session_file $file_name -all"

                    # Echo the command for debugging
                    echo "Running longitudinal command: $cmd_long"

                    # Execute the command in the background
                    eval $cmd_long &
                done

                # Wait for all background processes to finish
                wait
                
                echo -e "****************************************************************************************************"
                echo -e "\nLongitudinal pipeline completed! \n\n****************************************************************************************************"
                echo -e "****************************************************************************************************\n"

            else
                echo "Study: $study_name, Subject: $file_name; No matching file found in longitudinal data"

            fi
        done
    fi
done

# Create a separate longitudinal dataset on FS-output

#mkdir -p $C_HOME/OUTPUT/Statistics/Longitudinal

echo -e "\nCreating FreeSurfer-long dataset\n\n****************************************************************************************************"
echo -e "****************************************************************************************************\n"; sleep 1

Freesurfer="$C_HOME/OUTPUT/FreeSurfer"
TEMP_DIR="$C_HOME/Data/TEMP_DIR"

# FreeSurfer datagen
for study_directories in "$Freesurfer"/*; do
    study=$(basename "$study_directories")
    
    for subject_folder in "$study_directories"/*; do
        # Skip processing if the folder name is "fsaverage"
        if [ "$(basename "$subject_folder")" == "fsaverage" ]; then
            echo "Skipping fsaverage folder: $subject_folder"
            continue
        fi
        
        subject_name=$(basename "$subject_folder")
        
        # Check if the subject name contains "long"
        if [[ "$subject_name" == *long* ]]; then
            echo -e "\nProcessing $subject_name\n"
            
            mkdir -p "$TEMP_DIR/Stats/FreeSurfer/$study"
            rsync -av \
                --include='lh.aparc.DKTatlas.stats' \
                --include='rh.aparc.DKTatlas.stats' \
                --include='brainvol.stats' \
                --include='wmparc.stats' \
                --include='aseg.stats' \
                --exclude='*' \
                "$C_HOME/OUTPUT/FreeSurfer/$study/$subject_name/stats/" \
                "$TEMP_DIR/Stats/FreeSurfer/$study/$subject_name"
            
            stat_dir="$TEMP_DIR/Stats/FreeSurfer/$study/$subject_name"            

            # Check if the stats directory exists before proceeding
            if [ -d "$TEMP_DIR/Stats/FreeSurfer/$study/$subject_name" ]; then                
                for stat_files in "$TEMP_DIR/Stats/FreeSurfer/$study/$subject_name"/*; do
                    if [ "$stat_files" == "$stat_dir/lh.aparc.DKTatlas.stats" ]; then
                        echo "Found lh.aparc.DKTatlas.stats file: $stat_files"
                        output_file="$stat_dir/lh_aparc_DKT_output.csv"
                        python3 "$C_HOME/bin/free_stat/datagen_aparc_DKT.py" "$stat_files" "$output_file"

                    elif [ "$stat_files" == "$stat_dir/rh.aparc.DKTatlas.stats" ]; then
                        echo "Found rh.aparc.DKTatlas.stats file: $stat_files"
                        output_file="$stat_dir/rh_aparc_DKT_output.csv"
                        python3 "$C_HOME/bin/free_stat/datagen_aparc_DKT.py" "$stat_files" "$output_file"

                    elif [ "$stat_files" == "$stat_dir/brainvol.stats" ]; then
                        echo "Found brainvol.stats file: $stat_files"
                        output_file="$stat_dir/brainvol_output.csv"
                        python3 "$C_HOME/bin/free_stat/datagen_brainvol.py" "$stat_files" "$output_file"

                    elif [ "$stat_files" == "$stat_dir/wmparc.stats" ]; then
                        echo "Found wmparc.stats file: $stat_files"
                        output_file="$stat_dir/wmparc_output.csv"
                        python3 "$C_HOME/bin/free_stat/datagen_wmparc.py" "$stat_files" "$output_file"

                    elif [ "$stat_files" == "$stat_dir/aseg.stats" ]; then
                        echo "Found aseg.stats file: $stat_files"
                        output_file="$stat_dir/aseg_output.csv"
                        python3 "$C_HOME/bin/free_stat/datagen_aseg.py" "$stat_files" "$output_file"

                    else
                        echo "No stats directory found for $stat_files."
            
                    fi

                done   

                # Fusion point 1
                python3 "$C_HOME/bin/free_stat/datagen_combine_local.py" "$stat_dir" "$TEMP_DIR/Stats/FreeSurfer/$study" "$subject_name.csv" 

            fi
        
        fi

        # Fusion point 2
        python3 "$C_HOME/bin/datagen_combine_regional.py" "$TEMP_DIR/Stats/FreeSurfer/$study" "$TEMP_DIR/Stats/FreeSurfer/$study" "$study.csv" 

    done
done

# Fusion point 3
python3 $C_HOME/bin/datagen_combine_global.py $C_HOME/Data/TEMP_DIR/Stats/temp_stats $TEMP_DIR/Stats/temp_stats/Freesurfer_data.csv

cd $TEMP_DIR/Stats/temp_stats

# Cleanup prior to file transfer
mv Freesurfer_data.csv $TEMP_DIR/Stats

