#!/bin/bash

cross_sectional_folder="$output/cross_sectional_data"
longitudinal_folder="$output/longitudinal_data"

mkdir -p "$cross_sectional_folder"
mkdir -p "$longitudinal_folder"

for study_folder in "$output"/*; do
    # Extract subject information from folder name
    study=$(basename "$study_folder")

    for subject_folder in "$study_folder"/*; do
        echo Found: "$subject_folder"

        if [ -d "$subject_folder" ]; then
            # Get the number of ses-* subfolders
            ses_folders=("$subject_folder"/ses-*)
            num_ses_folders=${#ses_folders[@]}

            # Check if it's longitudinal based on the number of ses-* subfolders
            if [ "$num_ses_folders" -ge 2 ]; then
                echo "Copying to longitudinal folder: $subject_folder"
                # Append the parent folder name to the study ID
                parent_folder=$(basename "$(dirname "$subject_folder")")
                if [ "$parent_folder" != "$study" ]; then
                    mkdir -p "$longitudinal_folder/${study}_${parent_folder}"
                    cp -rf "$subject_folder" "$longitudinal_folder/${study}_${parent_folder}/"
                else
                    if [ "$parent_folder" != "longitudinal_data" ]; then
                        mkdir -p "$longitudinal_folder/$study"
                        cp -rf "$subject_folder" "$longitudinal_folder/$study/"
                    fi
                fi
            else
                echo "Copying to cross-sectional folder: $subject_folder"
                # Append the parent folder name to the study ID only if it's different
                parent_folder=$(basename "$(dirname "$subject_folder")")
                if [ "$parent_folder" != "$study" ]; then
                    mkdir -p "$cross_sectional_folder/${study}_${parent_folder}"
                    cp -rf "$subject_folder" "$cross_sectional_folder/${study}_${parent_folder}/"
                else
                    if [ "$parent_folder" != "cross_sectional_data" ] && [ "$parent_folder" != "longitudinal_data" ]; then
                        mkdir -p "$cross_sectional_folder/$study"
                        cp -rf "$subject_folder" "$cross_sectional_folder/$study/"
                    fi
                fi
            fi
        fi
    done
done
