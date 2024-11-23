#!/bin/bash

echo -e "\nInstalling BrainSurf Lab (BSL) v1.0 by Lars Skattebøl"
echo -e "Department of Neurology, Oslo University Hostpital & Institute of Clinical Medicine, University of Oslo\n"

echo -e "\n----------------------------------------------------------------------------------------------------"

echo -e A special thanks to:

echo -e "\nLST-AI: A deep learning ensemble for accurate MS lesion segmentation. Wiltgen, Tun and McGinnis, Julian and Schlaeger, Sarah and Kofler, Florian and Voon, CuiCi and Berthele, Achim and Bischl, Daria and Grundl, Lioba and Will, Nikolaus and Metz, Marie and others. NeuroImage: Clinical, 2024"; sleep 1
echo -e "\nGreedy: Fast Automatic Segmentation of Hippocampal Subfields and Medial Temporal Lobe Subregions In 3 Tesla and 7 Tesla T2-Weighted MRI. Yushkevich, Paul A and Pluta, John and Wang, Hongzhi and Wisse, Laura EM and Das, Sandhitsu and Wolk, David. Alzheimer's & Dementia, 2016 "; sleep 1
echo -e "\nHD-BET: Automated brain extraction of multisequence MRI using artificial neural networks. Isensee, Fabian and Schell, Marianne and Pflueger, Irada and Brugnara, Gianluca and Bonekamp, David and Neuberger, Ulf and Wick, Antje and Schlemmer, Heinz-Peter and Heiland, Sabine and Wick, Wolfgang and others. Human brain mapping, 2019"; sleep 1
echo -e "\nBrain age: Deep neural networks learn general and clinically relevant representations of the ageing brain. Esten H. Leonardsen and Han Peng and Tobias Kaufmann and Ingrid Agartz and Ole A. Andreassen and Elisabeth Gulowsen Celius and Thomas Espeseth and Hanne F. Harbo and Einar A. Høgestøl and Ann-Marie de Lange and Andre F. Marquand and Didac Vidal-Piñeiro and James M. Roe and Geir Selbæk and Øystein Sørensen and Stephen M. Smith and Lars T. Westlye and Thomas Wolfers and Yunpeng Wang. NeuroImage, 2022"; sleep 1
echo -e "\nSCT: Spinal Cord Toolbox, an open-source software for processing spinal cord MRI data. Benjamin De Leener and Simon Lévy and Sara M. Dupont and Vladimir S. Fonov and Nikola Stikov and D. Louis Collins and Virginie Callot and Julien Cohen-Adad. NeuroImage, 2017"; sleep 1
echo -e "\nFastSurfer: A fast and accurate deep learning based neuroimaging pipeline. Henschel L, Conjeti S, Estrada S, Diers K, Fischl B, Reuter M .NeuroImage, 2020"; sleep 1
echo -e "\nFreeSurfer: Please refer to https://surfer.nmr.mgh.harvard.edu/fswiki/FreeSurferMethodsCitation."; sleep 1 

echo -e "----------------------------------------------------------------------------------------------------\n"

echo -e "Lesions are segmented by the lesion growth algorithm (Schmidt et al., 2012) as implemented in the LST toolbox version 3.0.0 (www.statisticalmodelling.de/lst.html) for SPM."; sleep 1

export C_HOME="$(cd "$(dirname "$BASH_SOURCE")" && pwd -P)"
echo Home is: $C_HOME

#Set up folder structure

mkdir Data Data_vault OUTPUT QC_images INPUT
cd Data

mkdir -p BIDS TEMP_DIR/Stats TEMP_DIR/Surf
cd ..; cd OUTPUT

mkdir BrainAge_Pyment FastSurfer FreeSurfer LST LST_AI QC Results SCT Statistics
cd ..

echo -e "\n----------------------------------------------------------------------------------------------------"
echo -e "----------------------------------------------------------------------------------------------------\n"

#Fetching third-party dependencies

echo -e "Downloading libraries and third-party components..\n"

#fsqc_dir=$C_HOME/sys/libraries/fsqc
#mkdir -p $fsqc_dir
#git clone https://github.com/Deep-MI/fsqc.git $fsqc_dir

src_temp=$C_HOME/sys/software/temp_dir
mkdir -p $src_temp
cd $src_temp

# Lesions segmentation toolbox v3.0.0
curl -L -o $src_temp/LST_3.0.0.zip https://www.applied-statistics.de/LST_3.0.0.zip
unzip LST_3.0.0.zip > /dev/null 2>&1

# SPM12
cd $C_HOME/bin
git clone https://github.com/spm/spm12.git
mv $src_temp/LST $C_HOME/bin/spm12/toolbox

# Spinal cord toolbox
curl -L -o "$src_temp/install_sct-6.4_linux.sh" https://github.com/spinalcordtoolbox/spinalcordtoolbox/releases/download/6.4/install_sct-6.4_linux.sh
chmod +x "$src_temp/install_sct-6.4_linux.sh"
bash "$src_temp/install_sct-6.4_linux.sh" -y

#mv $HOME/sct_6.4 $C_HOME/sys/libraries 

# LST_AI
mkdir -p $C_HOME/bin/sbin/lst_directory
cd $C_HOME/bin/sbin/lst_directory

source $C_HOME/sys/env/lst_ai/bin/activate

git clone https://github.com/CompImg/LST-AI/
cd LST-AI
pip install -e .
cd ..

git clone https://github.com/MIC-DKFZ/HD-BET
cd HD-BET
#pip install -e .
pip install .

cd ..

curl -L -o "$src_temp/greedy" https://github.com/CompImg/LST-AI/releases/download/v1.0.0/greedy

chmod +x "$src_temp/greedy"
mkdir -p $C_HOME/sys/libraries/bin
mv $src_temp/greedy $C_HOME/sys/libraries/bin

# This is also automatically exported in LST_AI bin_script
export PATH="$C_HOME/sys/libraries/bin:$PATH"
deactivate

# Brain age

cd $C_HOME/bin
tar -xf Pyment.tar.xz; rm -rf Pyment.tar.xz

# FastSurfer Native
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh

cd $C_HOME/sys/libraries
git clone --branch stable https://github.com/Deep-MI/FastSurfer.git

cd FastSurfer
source env create -f ./env/fastsurfer.yml 

source ~/miniconda3/bin/activate

echo -e "\n----------------------------------------------------------------------------------------------------"
pip check
echo -e "----------------------------------------------------------------------------------------------------\n"

# Cleanup
cd $C_HOME
rm -f requirements_brain_age.txt requirements_brainsurf.txt requirements_lst_ai.txt setup.sh
rm -rf $C_HOME/sys/software/temp_dir/*
rm -rf $C_HOME/update

source $C_HOME/sys/env/brainsurf/bin/activate

echo -e "Creating desktop icon\n"

echo -e "[Desktop Entry]\nType=Application\nName=BrainSurf-main v1.0\nExec=/bin/bash $C_HOME/bin/gui_init.sh\nIcon=$C_HOME/bin/brainsurficon.jpeg\nTerminal=false\nCategories=Utility;" > $HOME/Desktop/brainsurf.desktop
gio set $HOME/Desktop/brainsurf.desktop metadata::trusted true && chmod +x $HOME/Desktop/brainsurf.desktop

chmod -R +x $C_HOME

echo -e "DONE\n"; sleep 3
echo Starting GUI..; python $C_HOME/sys/pipeline_gui.py
