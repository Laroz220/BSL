#!/bin/bash

### QC-control

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
export SUBJECTS_DIR="$C_HOME/OUTPUT/FreeSurfer"

version=7.4.1

mkdir -p $SUBJECTS_DIR

source $FREESURFER_HOME/SetUpFreeSurfer.sh
source $C_HOME/sys/env/qc_control/bin/activate

### FreeSurfer QC and stats                        #8  Revised - OK!  

rm -rf $C_HOME/QC_images $C_HOME/OUTPUT/QC $TEMP_DIR/Stats
rm -rf $C_HOME/OUTPUT/Results/Data_Merged_ALL.csv

mkdir -p $C_HOME/OUTPUT/QC/FastSurfer $C_HOME/OUTPUT/QC/FreeSurfer
mkdir -p $C_HOME/QC_images/FastSurfer $C_HOME/QC_images/FreeSurfer 
mkdir -p $TEMP_DIR/Stats/temp_stats

# Define a singular serial loop for fast- and freesurfer
# Export stats files

# FreeSurfer QC and stats export

for qc in "$C_HOME/OUTPUT"; do
    Freesurfer=$qc/FreeSurfer
    Fastsurfer=$qc/FastSurfer

    for study_directories in "$Freesurfer"/*; do
        study=$(basename "$study_directories")

        run_fsqc --subjects_dir $C_HOME/OUTPUT/FreeSurfer/$study --output_dir $C_HOME/OUTPUT/QC/FreeSurfer/$study --screenshots --fornix --shape --outlier
        
        for subject_folder in $study_directories/*; do
            subject_name=$(basename "$subject_folder")
            mkdir -p $C_HOME/OUTPUT/QC/FreeSurfer/$study
            mkdir -p $TEMP_DIR/Stats/FreeSurfer/$study
            
            rsync -av --include='lh.aparc.DKTatlas.stats' --include='rh.aparc.DKTatlas.stats' --include='brainvol.stats' --include='wmparc.stats' --include='aseg.stats' --exclude='*' "$C_HOME"/OUTPUT/FreeSurfer/"$study"/"$subject_name"/stats/ "$TEMP_DIR"/Stats/FreeSurfer/"$study"/"$subject_name"
            rsync -av $C_HOME/OUTPUT/QC/FreeSurfer/$study/screenshots/"$subject_name"/* $C_HOME/QC_images/FreeSurfer/

        done
    done

# FastSurfer QC and stats export                         #9  Revised - OK!

    for study_directories in "$Fastsurfer"/*; do
        study=$(basename "$study_directories")
        
        run_fsqc --subjects_dir $C_HOME/OUTPUT/FastSurfer/$study --output_dir $C_HOME/OUTPUT/QC/FastSurfer/$study --fastsurfer --screenshots --fornix --shape --outlier

        for subject_folder in $study_directories/*; do
            subject_name=$(basename "$subject_folder")
            mkdir -p $C_HOME/OUTPUT/QC/FastSurfer/$study
            mkdir -p $TEMP_DIR/Stats/FastSurfer/$study
            
            rsync -av --include='aseg+DKT.stats' --include='brainvol.stats' --include='cerebellum.CerebNet.stats' --include='wmparc.DKTatlas.mapped.stats' --exclude='*' "$C_HOME"/OUTPUT/FastSurfer/"$study"/"$subject_name"/stats/ "$TEMP_DIR"/Stats/FastSurfer/"$study"/"$subject_name"
            rsync -av $C_HOME/OUTPUT/QC/FastSurfer/$study/screenshots/"$subject_name"/* $C_HOME/QC_images/FastSurfer/

        done
    done
done

location_fsaverage="$TEMP_DIR/Stats/FreeSurfer"
find "$location_fsaverage" -type d -name "fsaverage" -exec rm -rf {} +

### Output generator                              #10 

#FastSurfer datagen

# Create an individual .csv for each .stat prior to fusion

for stat_run in "$TEMP_DIR/Stats"; do
    Freesurfer="$stat_run/FreeSurfer"
    Fastsurfer="$stat_run/FastSurfer"

    echo -e "\nWriting statistics...\n"

    for study_directories in "$Fastsurfer"/*; do
        study=$(basename "$study_directories")
        echo $study
            
        for subject_folder in "$study_directories"/*; do
            subject_name=$(basename "$subject_folder")

            echo -e "\nProcessing $subject_name\n"

            for stat_files in "$subject_folder"/*; do

                if [ "$stat_files" == "$subject_folder/aseg+DKT.stats" ]; then
                    echo "Found aseg+DKT.stats file: $stat_files"
                    output_file="$subject_folder/aseg+DKT_output.csv"
                    python3 "$C_HOME/bin/fast_stat/datagen_aseg_DKT.py" "$stat_files" "$output_file"

                elif [ "$stat_files" == "$subject_folder/brainvol.stats" ]; then
                    echo "Found brainvol.stats file: $stat_files"
                    output_file="$subject_folder/brainvol_output.csv"
                    python3 "$C_HOME/bin/fast_stat/datagen_brainvol.py" "$stat_files" "$output_file"

                elif [ "$stat_files" == "$subject_folder/cerebellum.CerebNet.stats" ]; then
                    echo "Found cerebellum.CerebNet.stats file: $stat_files"
                    output_file="$subject_folder/cerebellum.CerebNet_output.csv"
                    python3 "$C_HOME/bin/fast_stat/datagen_cerebnet.py" "$stat_files" "$output_file"

                elif [ "$stat_files" == "$subject_folder/wmparc.DKTatlas.mapped.stats" ]; then
                    echo "Found wmparc.DKTatlas.mapped.stats file: $stat_files"
                    output_file="$subject_folder/wmparc.DKTatlas_output.csv"
                    python3 "$C_HOME/bin/fast_stat/datagen_wmparc_DKTatlas.py" "$stat_files" "$output_file"

                fi

            done

            # Fusion point 1
            python3 "$C_HOME/bin/fast_stat/datagen_combine_local.py" "$subject_folder" "$study_directories" "$subject_name.csv" 

        done

        # Fusion point 2
        python3 "$C_HOME/bin/datagen_combine_regional.py" "$study_directories" "$study_directories" "$study.csv" 

        for csv_files in "$study_directories"/$study.csv; do
            mv "$csv_files" "$TEMP_DIR/Stats/temp_stats"

        done
    done

    # Fusion point 3
    python3 $C_HOME/bin/datagen_combine_global.py $C_HOME/Data/TEMP_DIR/Stats/temp_stats $TEMP_DIR/Stats/temp_stats/Fastsurfer_data.csv

    cd $TEMP_DIR/Stats/temp_stats

    # Cleanup prior to file transfer
    rm -rf ALS.csv HSCT.csv MS.csv
    mv Fastsurfer_data.csv $TEMP_DIR/Stats

#FreeSurfer datagen

    for study_directories in "$Freesurfer"/*; do
        study=$(basename "$study_directories")
    
        for subject_folder in "$study_directories"/*; do
            # Skip processing if the folder name is "fsaverage"
            if [ "$(basename "$subject_folder")" == "fsaverage" ]; then
                echo "Skipping fsaverage folder: $subject_folder"
                continue
            fi
            
            subject_name=$(basename "$subject_folder")
            echo -e "\nProcessing $subject_name\n"

            for stat_files in "$subject_folder"/*; do

                if [ "$stat_files" == "$subject_folder/lh.aparc.DKTatlas.stats" ]; then
                    echo "Found lh.aparc.DKTatlas.stats file: $stat_files"
                    output_file="$subject_folder/lh_aparc_DKT_output.csv"
                    python3 "$C_HOME/bin/free_stat/datagen_aparc_DKT.py" "$stat_files" "$output_file"

                elif [ "$stat_files" == "$subject_folder/rh.aparc.DKTatlas.stats" ]; then
                    echo "Found rh.aparc.DKTatlas.stats file: $stat_files"
                    output_file="$subject_folder/rh_aparc_DKT_output.csv"
                    python3 "$C_HOME/bin/free_stat/datagen_aparc_DKT.py" "$stat_files" "$output_file"

                elif [ "$stat_files" == "$subject_folder/brainvol.stats" ]; then
                    echo "Found brainvol.stats file: $stat_files"
                    output_file="$subject_folder/brainvol_output.csv"
                    python3 "$C_HOME/bin/free_stat/datagen_brainvol.py" "$stat_files" "$output_file"

                elif [ "$stat_files" == "$subject_folder/wmparc.stats" ]; then
                    echo "Found wmparc.stats file: $stat_files"
                    output_file="$subject_folder/wmparc_output.csv"
                    python3 "$C_HOME/bin/free_stat/datagen_wmparc.py" "$stat_files" "$output_file"

                elif [ "$stat_files" == "$subject_folder/aseg.stats" ]; then
                    echo "Found aseg.stats file: $stat_files"
                    output_file="$subject_folder/aseg_output.csv"
                    python3 "$C_HOME/bin//free_stat/datagen_aseg.py" "$stat_files" "$output_file"
                fi
            done

            # Fusion point 1
            python3 "$C_HOME/bin/free_stat/datagen_combine_local.py" "$subject_folder" "$study_directories" "$subject_name.csv" 

        done

        # Fusion point 2
        python3 "$C_HOME/bin/datagen_combine_regional.py" "$study_directories" "$study_directories" "$study.csv" 

        for csv_files in "$study_directories"/$study.csv; do
            mv "$csv_files" "$TEMP_DIR/Stats/temp_stats"

        done
    done
done

# Fusion point 3
python3 $C_HOME/bin/datagen_combine_global.py $C_HOME/Data/TEMP_DIR/Stats/temp_stats $TEMP_DIR/Stats/temp_stats/Freesurfer_data.csv

cd $TEMP_DIR/Stats/temp_stats

# Cleanup prior to file transfer
mv Freesurfer_data.csv $TEMP_DIR/Stats
rm -rf *

# Terminal fusion point 3-3 Free-Fast / Data.csv
cd $TEMP_DIR/Stats; python3 $C_HOME/bin/datagen_combine_universal.py $C_HOME/Data/TEMP_DIR/Stats $C_HOME/OUTPUT/Statistics/Data.csv

#mv Data.csv $C_HOME/OUTPUT/Statistics

### LST

echo -e "\nCreating LST statistics...\n"

mkdir -p $C_HOME/OUTPUT/Statistics/LST
cd $C_HOME/OUTPUT/Statistics/LST

target_LST="$C_HOME/OUTPUT/LST"

for study_directories in "$target_LST"/*; do

    for subject_folder in "$study_directories"/*; do
        subject_name=$(basename "$subject_folder")

        echo -e "\nProcessing subject: $subject_name:"

        for html_file in "$subject_folder"/t1w/*_rm"$subject_name"_T2w-flair.html; do
            echo -e "\nInput: $html_file"

            python3 $C_HOME/bin/LST_stat/LST_to_csv.py $html_file

            output="$subject_folder/t1w/*.csv"
            echo Output file: $output

            mv $output "$subject_name"_LST.csv

        done
    done
done

python3 $C_HOME/bin/LST_stat/Merge_LST.py

directory=$C_HOME/OUTPUT/Statistics/LST
cd "$directory"; mv Merged_Data.csv $C_HOME/OUTPUT/Statistics

# Add script for fusing with data.csv
python3 $C_HOME/bin/LST_stat/datagen_fuse_all_LST.py $C_HOME/OUTPUT/Statistics/Merged_Data.csv $C_HOME/OUTPUT/Statistics/Data.csv $C_HOME/OUTPUT/Statistics/Data_Merged_LST.csv

rm $C_HOME/OUTPUT/Statistics/Merged_Data.csv

#/usr/bin/bash $C_HOME/bin/LST_stat/cleanup_LST.sh

# LST-AI

echo -e "\nCreating LST-AI statistics...\n"

# Ensure correct directory
mkdir -p "$C_HOME/OUTPUT/Statistics/LST_AI"
cd "$C_HOME/OUTPUT/Statistics/LST_AI" || exit

target_LST_AI="$C_HOME/OUTPUT/LST_AI"

for study_directories in "$target_LST_AI"/*; do
    for subject_folder in "$study_directories"/*; do
        if [ -d "$subject_folder" ]; then
            subject_name=$(basename "$subject_folder")
            echo -e "\nProcessing subject: $subject_name:\n"
            echo "$subject_folder"

            input_1="$subject_folder"/annotated_lesion_stats.csv
            input_2="$subject_folder"/lesion_stats.csv

            echo "Input 1: $input_1"
            echo "Input 2: $input_2"

            # Check if input files exist
            if [ -f "$input_1" ] && [ -f "$input_2" ]; then
                # Execute Python script
                python3 "$C_HOME/bin/LST_stat/LST_AI_to_csv.py" "$input_1" "$input_2"

                # Check if combined CSV file exists
                if [ -f combined.csv ]; then
                    # Rename the combined CSV file to match the subject directory
                    mv -f combined.csv "${subject_name}_LST.csv" 2>/dev/null

                    # Move the renamed CSV file to the output directory
                    mv -f "${subject_name}_LST.csv" "$C_HOME/OUTPUT/Statistics/LST_AI" 2>/dev/null
                    echo "CSV file moved successfully."
                else
                    echo "Error: Combined CSV file not found for subject $subject_name."
                fi
            else
                echo "Error: Required input files not found for subject $subject_name."
            fi
        fi
    done
done

cd $C_HOME/OUTPUT/Statistics/LST_AI; python3 $C_HOME/bin/LST_stat/Merge_LST.py

directory=$C_HOME/OUTPUT/Statistics/LST_AI
cd "$directory"; mv Merged_Data.csv $C_HOME/OUTPUT/Statistics

# Add script for fusing with data.csv
python3 $C_HOME/bin/LST_stat/datagen_fuse_all_LST_AI.py $C_HOME/OUTPUT/Statistics/Merged_Data.csv $C_HOME/OUTPUT/Statistics/Data_Merged_LST.csv $C_HOME/OUTPUT/Statistics/Data_Merged_LST_AI.csv

rm $C_HOME/OUTPUT/Statistics/Merged_Data.csv

# Brain Age

target_file="$C_HOME/OUTPUT/BrainAge_Pyment/predictions.csv"

# Check if the target file exists
if [ -f "$target_file" ]; then
    # Use awk to process the file
    awk -F, 'BEGIN {OFS=","} 
    NR==1 { 
        for (i=1; i<=NF; i++) {
            if ($i == "id") $i = "Subject_ID";
        }
        print;
        next;
    }
    { print }' "$target_file" > temp.csv && mv temp.csv "$target_file"
    echo "Column 'id' renamed to 'Subject_ID' in $target_file"
else
    echo "Error: File $target_file not found."
fi

# Modify and combine the csv.
python3 $C_HOME/bin/pyment_stat/df_modify_var.py $C_HOME/OUTPUT/BrainAge_Pyment/predictions.csv $C_HOME/OUTPUT/BrainAge_Pyment/predictions_modified.csv

output=$C_HOME/OUTPUT/BrainAge_Pyment/predictions_modified.csv
cp -rf $output $C_HOME/OUTPUT/Statistics

python3 $C_HOME/bin/pyment_stat/datagen_fuse_all_pyment_all.py $C_HOME/OUTPUT/Statistics/predictions_modified.csv $C_HOME/OUTPUT/Statistics/Data_Merged_LST_AI.csv $C_HOME/OUTPUT/Statistics/Data_Merged_ALL.csv

# Preparing results; creating backup

cd $C_HOME/OUTPUT/Statistics; mkdir -p $C_HOME/OUTPUT/Results/Archive
mv Data_Merged_ALL.csv $C_HOME/OUTPUT/Results
cp -rf $C_HOME/OUTPUT/Results/Data_Merged_ALL.csv $C_HOME/OUTPUT/Results/Archive

cd $C_HOME/OUTPUT/Results/Archive; mv Data_Merged_ALL.csv Dataset_$(date +%Y-%m-%d_%H-%M)

rm -rf $C_HOME/OUTPUT/Statistics/* $C_HOME/Data/TEMP_DIR/Stats/*

### Merge QC-specific data


echo -e "\nQC Done""!"" Dataset located at $C_HOME//Results""\n\n****************************************************************************************************\n"
