#!/bin/bash

# Override the conditional HOME variable, if applicable
# export C_HOME=path/to/directory 

### Data organization/preprocessing & BIDS
source $C_HOME/bin/data_preprocessing.sh            #   Revised - OK!!

### Script list run-through fast- & freesurfer
source $C_HOME/bin/fastsurf_runtime.sh              #1   Revised - OK!!
source $C_HOME/bin/freesurf_runtime.sh              #2   Revised - OK!
source $C_HOME/bin/GI_index.sh                      #3   OK! / Not revised.. Currently omitting. To time-consuming. Parallel not possible

### LST/SCT 
source $C_HOME/bin/lst_ai.sh                        #4   Revised - OK!
source $C_HOME/bin/lst.sh                           #5   Revised - OK!
source $C_HOME/bin/sct.sh                           #6   Revised - OK!

### Brain age after LST-processing**
source $C_HOME/bin/brain_age_pyment.sh              #7   Revised - OK!

### QC-control
source $C_HOME/bin/qc_stats.sh

### MOVE BIDS-folders to output (/Desktop/output)
#echo "Moving folders to output"
cd $C_HOME; mkdir Data_vault; cd Data_vault
mkdir BIDS Freesurfer Fastsurfer Brain_age LST LST_AI SCT 

input=$C_HOME/OUTPUT
output_dest=$C_HOME/Data_vault

#BIDS - cross-sectional / longitudinal data
echo Moving BIDS to vault.. at $C_HOME
rsync -av --quiet $C_HOME/Data/BIDS/cross_sectional_data/* $output_dest/BIDS/cross_sectional_data 2>/dev/null
rsync -av --quiet $C_HOME/Data/BIDS/longitudinal_data/* $output_dest/BIDS/longitudinal_data 2>/dev/null
echo -e "[Done]\n"

#Fastsurfer  
echo Moving FastSurfer to vault..
rsync -av --quiet $input/FastSurfer/* $output_dest/FastSurfer 2>/dev/null
echo -e "[Done]\n"

#Freesurfer
echo Moving FreeSurfer to vault..
rsync -av --quiet $input/FreeSurfer/* $output_dest/FreeSurfer 2>/dev/null
echo -e "[Done]\n"

#LST_AI
echo Moving LST AI to vault..
rsync -av --quiet $input/LST_AI/* $output_dest/LST_AI 2>/dev/null
echo -e "[Done]\n"

#LST
echo Moving LST to vault..
rsync -av --quiet $input/LST/* $output_dest/LST 2>/dev/null
echo -e "[Done]\n"

#SCT
echo Moving SCT to vault..
rsync -av --quiet $input/SCT/* $output_dest/SCT 2>/dev/null
echo -e "[Done]\n"

echo -e "\nData back-up completed""!""\n\n**************************************************\n"
echo -e "**************************************************\n"
echo -e "\nPipeline Completed\n\nTo continue, please restart GUI to ensure script stability"
echo -e "\n\n**************************************************\n"

#Create a list of overall processed subjects
#Processed subjects** -csv, co-register with MRI-dataset (main)

#mkdir -p $HOME/Desktop/Output/BIDS
#cd $C_HOME/Data/BIDS; find -type d -name 'sub*' -exec mv -t $HOME/Desktop/Output/BIDS {} + 2>/dev/null

#echo "Cleaning..."; cd $C_HOME/Data/BIDS
#rm -rf !(code|cross_sectional_data|longitudinal_data)
#find $C_HOME/Data/BIDS -mindepth 1 -maxdepth 1 -type d \( ! -name 'code' -a ! -name 'cross_sectional_data' -a ! -name 'longitudinal_data' \) -exec rm -rf {} +
#rm -rf .bidsignore
