#!/bin/bash

# If newly created folders are locked: run "chmod -R 777 $C_HOME"

# Set directory for temporary output
TEMP_DIR=$C_HOME/Data/TEMP_DIR

echo -e "\nInitializing MRI Pipeline\n\n****************************************************************************************************"
echo -e "****************************************************************************************************\n"

### Temporary data
echo "Cleaning Temp directories..."

rm -rf $TEMP_DIR/BIDS_conversion_temp $TEMP_DIR/Surf/*
rm -rf $C_HOME/Data/DICOM

cd $C_HOME/OUTPUT/BrainAge_Pyment 2>/dev/null; rm -rf predictions_modified.csv predictions.csv 2>/dev/null
cd $C_HOME/OUTPUT/BrainAge_Pyment/bin 2>/dev/null

rm -rf predictions_modified.csv predictions.csv brainmasks cropped/labels.csv cropped/images/* mni152 nifti recon reoriented 2>/dev/null
sleep 5

find "$C_HOME/Data/BIDS" -mindepth 1 -maxdepth 1 ! -name "code" -exec rm -rf {} +

### Anonymization
source $C_HOME/bin/anon_script/init_anon.sh

### Rsync DICOM to TEMP_DIR

echo -e "\nIdentifying DICOM subfolders.."

#Pre-step; check folder structure prior to deconstruction of dcm´s

cd $C_HOME/Data/DICOM
python3 $C_HOME/bin/mri_folder_sort.py

#Parental clean-up
python3 $C_HOME/bin/clean_dir.py

echo "Done!"

echo -e "\nPlease wait""!"" Copy- and relocating..."

src_dir="$C_HOME/Data/DICOM"
dest_dir="$C_HOME/Data/TEMP_DIR/BIDS_conversion_temp"

### Append pids for rsync targeting
rsync_pids=()

### Annihilate rsync if GUI is terminated
terminate_script() {
    echo "Exiting script. Killing rsync processes..."
    for pid in "${rsync_pids[@]}"; do
        kill "$pid"
    done
    exit 1
}

trap 'terminate_script' SIGINT SIGTERM

for dir in "$src_dir"/*; do
    dir_name=$(basename "$dir")

    study_id=$(echo "$dir_name" | grep -oE '^[^_]+')
    subject_id=$(echo "$dir_name" | grep -oE '[0-9]+' | head -1)
    session=$(echo "$dir_name" | grep -oE '[0-9]+' | tail -1)

    export LABEL=$study_id
    mkdir -p "$dest_dir/$LABEL/$subject_id/$session"

    rsync -av --quiet "$dir/" "$dest_dir/$LABEL/$subject_id/$session" &
    rsync_pids+=($!)

done; wait

echo -e "\nTransfer completed""!""\n\n****************************************************************************************************\n"

echo -e "Restructuring DICOM into BIDS:\n"

### BIDS that shit

heuristic="$C_HOME/bin/code/heuristic.py"
output="$C_HOME/Data/BIDS"

for subject_folder in "$TEMP_DIR"/BIDS_conversion_temp/*; do
    # Extract subject information from folder name
    study=$(basename "$subject_folder")

    input="$TEMP_DIR/BIDS_conversion_temp/$study"

    # Iterate through sessions within the subject folder
    for session_folder in "$subject_folder"/*; do
        # Extract session information from session folder name
        subject=$(basename "$session_folder")

        # Iterate through sessions within the subject folder
        for subject_folder in "$session_folder"/*; do
            # Extract session information from session folder name
            session=$(basename "$subject_folder")

            echo Processing "Study: $study, subject: $subject, Session: $session"

            # Run heudiconv
            heudiconv \
                -d "$input"/{subject}/{session}/* \
                -s "$subject" \
                --ses "$session" \
                --grouping all \
                -f "$heuristic" \
                -c dcm2niix -b \
                -o "$output"/"$study"
        done
    done
done

echo -e "\nMRI folder structuring in BIDS completed\n\n****************************************************************************************************\n"

### Separate data into longitudinal and cross-sectional in //Data/BIDS
source $C_HOME/bin/data_filter.sh             #    Revised - OK!!

# Set directories
destination_dir="$TEMP_DIR/Surf" # Destination directory

mkdir -p $destination_dir/Docker_img

### Transfer T1w- and T2w-files from BIDS-folders to $destination_dir at //Surf/$Study and //Surf/Docker_img
for subject_folder in "$output"/*; do
    study=$(basename "$subject_folder")
    mkdir "$destination_dir/$study"

    #loop over subject_dir, transferring required files
    for subject_dir in "$subject_folder"/sub-*/ses-*; do
        # Check if the subject directory contains an 'anat' subdirectory
        if [ -d "$subject_dir/anat" ]; then
            # Get a list of T1w files matching the specified criteria
            t1w_files="$(ls "$subject_dir/anat"/*T1* 2>/dev/null | grep -E 'NC' | grep -E -v 'CE' | grep '\.nii\.gz$')"

            # Check if there are any T1w files before attempting to copy
            if [ -n "$t1w_files" ]; then
                cp -r $t1w_files "$destination_dir/$study"
                cp -r $t1w_files "$destination_dir/Docker_img"
            fi

            # Get a list of T2w files matching the specified criteria
            t2w_files="$(ls "$subject_dir/anat"/*T2w* 2>/dev/null | grep -E 'flair' | grep '\.nii\.gz$')"

            # Check if there are any T2w files before attempting to copy
            if [ -n "$t2w_files" ]; then
                cp -r $t2w_files "$destination_dir/$study"
            fi

            echo Copying "$(basename "$t1w_files")" and "$(basename "$t2w_files")" to "$destination_dir" and //Docker_img...

        fi
    done
done

### Cleanup
rm -rf $destination_dir/longitudinal_data $destination_dir/cross_sectional_data
sleep 2; echo Transfer completed

echo T1w- and T2w-files transferred from BIDS-folders to $destination_dir
echo -e "\nData preprocessing done""!""\n\n****************************************************************************************************\n"
