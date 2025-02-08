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

### DCM sanity check / Prestep conversion to uncompressed DICOMs
for input in "$C_HOME"/INPUT/*; do
    echo -e "[INFO]: Evaluating --> $input.."
    python $C_HOME/bin/dcm_decomp.py -i $input #> /dev/null 2>&1

done; echo [INFO]: Decompression completed!

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

mkdir -p $destination_dir/Docker_img $C_HOME/Data/BIDS/Series_description
sd_label_dir=$C_HOME/Data/BIDS/Series_description

### Transfer T1w- and T2w-files from BIDS-folders to $destination_dir at //Surf/$Study and //Surf/Docker_img
mkdir -p "$destination_dir/Docker_img" "$C_HOME/Data/BIDS/Series_description"
sd_label_dir="$C_HOME/Data/BIDS/Series_description"

# Loop through subjects
for subject_folder in "$output"/*; do
    study=$(basename "$subject_folder")
    mkdir -p "$destination_dir/$study"  # Ensure the directory exists

    # Check if .heudiconv exists before proceeding
    if [[ ! -d "$subject_folder/.heudiconv" ]]; then
        echo "Skipping $subject_folder (no .heudiconv directory found)"
        continue
    fi

    # Loop over .tsv files inside .heudiconv but exclude unwanted folders
    find "$subject_folder/.heudiconv" -type f -name "dicominfo_*.tsv" | while read -r file; do
        parent_folder=$(basename "$(dirname "$(dirname "$file")")")

        # Skip specific folders
        if [[ "$parent_folder" == "longitudinal_data" || "$parent_folder" == "cross_sectional_data" ]]; then
            continue
        fi

        filename=$(basename "$file")
        dest="$sd_label_dir/$filename"

        # Rename if file already exists
        if [[ -e "$dest" ]]; then
            timestamp=$(date +"%Y%m%d_%H%M%S")
            new_name="${filename%.tsv}_$timestamp.tsv"
            dest="$sd_label_dir/$new_name"
        fi

        rsync -av --quiet "$file" "$dest"
    done

    # Loop over subject directories
    for subject_dir in "$subject_folder"/sub-*/ses-*; do
        if [[ -d "$subject_dir/anat" ]]; then
            # Copy T1w files
            t1w_files=$(find "$subject_dir/anat" -type f -name "*T1*NC*.nii.gz" ! -name "*CE*" 2>/dev/null)
            for file in $t1w_files; do
                cp "$file" "$destination_dir/$study"
                cp "$file" "$destination_dir/Docker_img"
            done

            # Copy T2w files
            t2w_files=$(find "$subject_dir/anat" -type f -name "*T2w*flair*.nii.gz" 2>/dev/null)
            for file in $t2w_files; do
                cp "$file" "$destination_dir/$study"
            done

            echo "Copying $(basename "$file") to $destination_dir and Docker_img..."
        fi
    done
done

### Cleanup
rm -rf $destination_dir/longitudinal_data $destination_dir/cross_sectional_data
sleep 2; echo -e "\nTransfer completed!\n"

### Create a dicominfo_all.tsv
cd $sd_label_dir; python $C_HOME/bin/merge_tsv.py $C_HOME/Data/BIDS/tsv_all.tsv
echo INFO]: tsv_all.tsv located at $sd_label_dir

echo T1w- and T2w-files transferred from BIDS-folders to $destination_dir
echo -e "\nData preprocessing done""!""\n\n****************************************************************************************************\n"
