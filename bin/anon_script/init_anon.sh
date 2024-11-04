#!/bin/bash

echo Initializing: Anynomizing input data..

#Batch folder
target_folder=$C_HOME/INPUT

output_folder=$C_HOME/Data/DICOM

mkdir -p $output_folder

for subject in "$target_folder"/*; do
    subject_name=$(basename "$subject")
    output_name=$(basename "$output_folder")

    echo -e "\nAnonymizing $subject_name .. Please wait"

    python3  $C_HOME/bin/anon_script/anonymize.py $subject $output_folder/$subject_name

done
