#!/bin/bash

export BA_HOME=$C_HOME/OUTPUT/BrainAge_Pyment

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
export SUBJECTS_DIR="$C_HOME/OUTPUT/FreeSurfer"

version=7.4.1

mkdir -p $SUBJECTS_DIR

source $FREESURFER_HOME/SetUpFreeSurfer.sh

echo -e "Initializing Brain Age..\n"
echo Securing folder structure..

mkdir -p $BA_HOME/bin/raw $BA_HOME/bin/cropped/images
mkdir -p $BA_HOME/bin/recon

#If preexisting, clean folders
echo -e "\nCleaning $BA_HOME //recon..\n"
rm -rf $BA_HOME/bin/recon/*

TEMP_DIR=$C_HOME/Data/TEMP_DIR
cd $TEMP_DIR/Surf; echo -e "\nImporting data.. [importing T1s]"

# Find study ID
for t1w_folders in "$TEMP_DIR"/Surf/*; do
    study=$(basename "$t1w_folders")

    if [ "$study" = "Docker_img" ]; then
        continue
    fi

    for t1w_files in "$t1w_folders"/*T1*; do
        cp -rf $t1w_files $BA_HOME/bin/raw
    done
done

# Import preprocessed freesurfer-folders
for study_folder in "$C_HOME/OUTPUT/FreeSurfer/"*; do
    echo "Processing study folder: $study_folder"

    # Loop through each processed folder within the current study folder
    for processed_folder in "$study_folder/"*; do
        # Skip the fsaverage folder
        if [[ "$(basename "$processed_folder")" == "fsaverage" ]]; then
            echo "Skipping folder: $processed_folder"
            continue
        fi

        echo "Syncing processed folder: $processed_folder"
        
        # Use rsync to sync the folder, and wait for it to finish before moving to the next one
        rsync -av --quiet "$processed_folder" "$BA_HOME/bin/recon"
        
        # Check the exit status of rsync to ensure it completed successfully
        if [ $? -eq 0 ]; then
            echo "Sync completed successfully for: $processed_folder"
        else
            echo "Sync failed for: $processed_folder"
        fi
    done
done

# Rename preprocessed folders to their corresponding raw-names
cd $BA_HOME/bin; python3 $C_HOME/bin/rename_recon.py

#Automatically create .CSV-file
cd $C_HOME/bin
echo Creating label file..; python3 label_import.py $BA_HOME/bin $BA_HOME/bin/cropped/labels.csv

# Import environment; modify if needed:
source $C_HOME/sys/env/brain_age/bin/activate

cd Pyment; echo -e "\nPreprocessing $t1w_files: freesurfer autorecon1\n"; python3 Pyment_run.py 

echo -e "\n\nBrain age estimation completed""!""\n\n**************************************************\n"
