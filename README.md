# BrainSurf Lab (BSL) - An Automated MRI Processing Pipeline and Dataset Generator

![Screenshot from 2024-11-14 16-46-58](https://github.com/user-attachments/assets/f366e0ec-35f2-44bf-a42a-651992c0188a)

## Introduction
BSL is an attempt to alleviate the traditionally time-consuming and complex process of manually scripting, organizing, and harmonizing MRI data prior to statistical analyses. Typically, researchers spend significant time and effort preparing MRI data—writing custom scripts for each processing step, ensuring data consistency, and integrating various datasets into a unified format. This manual approach often introduces inefficiencies and the risk of errors, especially when managing large, multi-subject studies.

By automating these processes, we aim to reduce the overall manual workload. In BSL, you can also select and execute specific MRI processing scripts, ranging from data preprocessing and lesion segmentation to advanced tasks like Gyrification Index calculation and brain age estimation. Additionally, the "Full Pipeline" option offers complete streamlining by automating the sequential execution of all scripts for multiple subjects, and studies, ensuring that the entire workflow is cohesive and consistent.

BSL also has an integrated 3D plot feature for visualizing system resource usage in real-time. This visualization allows researchers to monitor and optimize CPU, RAM, and storage usage, ensuring that the system operates efficiently and stabile throughout the data processing stages.

In essence, BSL pushes to accelerate data preparation and dataset harmonization across subjects, transforming what would typically be a labor-intensive and error-prone task into a streamlined efficient workflow, allowing researchers to focus more on analysis and interpretation rather than data preparation.

## Setup and Requirements
Firstly, ensure that you have Python installed on your system. For consistency and stable resource monitoring, a custom virtual environment created with 'python -m venv' is preferred for the GUI.

At least 16 GB of RAM or VRAM (for GPU mode) is recommended and 40 GB free space, depending on batch size. The software has been tested on Linux 20/22/24.04, with dual Intel Xeon (Single AMD Radeon pro 5100, GPU mode not supported), Intel Core i7 (Single Nvidia GTX 1080, GPU mode enabled), and AMD Ryzen Threadripper (Dual Nvidia RTX4090 SLI, GPU mode enabled) using python 3.8/3.9, the latter version being a prerequesite for quality control. 

For MacOS, VMware Fusion w/ Linux Ubuntu 22.04/24.04 or Mint 22 is recommended! MacOS without virtualization is currently not supported. 

Other third-party softwares prerequesites not integrated in this install are: Matlab and FSL (see part 2c, bottom line).

The following command updates your system’s package lists and installs several tools: git for version control, wget for downloading files, unzip for extracting ZIP archives, python3 for the Python interpreter, and python3-pip for managing Python packages. The -y flag ensures that the installation proceeds without prompting for confirmation.

```
sudo apt-get update && sudo apt-get install -y git wget curl tcsh unzip python3 python3-pip gcc && \
sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt-get update && \

sudo apt-get install -y python3.9 python3.9-venv python3.8 python3.8-venv && \
sudo apt-get install -y python3.9-tk python3.8-tk && sudo apt-get update
```

### 1.) Clone to desired install path
```
git clone https://github.com/Laroz220/BSL.git && cd BSL
```
### 2.) Install and configure

#### a.) Create environment
Create a custom virtual environment using python -m venv by executing the following command:
```
mkdir -p sys/env && pushd sys/env && env_dir=$(pwd) && \

python3.8 -m venv brainsurf && \
python3.8 -m venv brain_age && \
python3.8 -m venv lst_ai && \
python3.9 -m venv qc_control && \
popd && \

export C_HOME=$(pwd)
```

#### b.) Install GUI- , environmental and pipeline dependencies
```
. "$env_dir/brainsurf/bin/activate" && \
sudo apt-get install \
libgirepository1.0-dev \
libcairo2-dev \
libgirepository1.0-dev \
python3.8-dev \
libgtk-3-dev && \

pip install wheel && pip install -r requirements_brainsurf.txt && pip check && \
. $env_dir/brain_age/bin/activate && pip install -r requirements_brain_age.txt && pip check && \
. $env_dir/lst_ai/bin/activate && pip install -r requirements_lst_ai.txt && pip check && \
. $env_dir/qc_control/bin/activate && pip install fsqc beautifulsoup4 && pip check && \

deactivate
```

#### c.) Download and configure third party software
This script installs BrainSurf Lab (BSL) v1.0, sets up necessary directories, and fetches third-party dependencies.

Setup: Initializes the home directory and creates required folders for data, outputs, and temporary files.

Dependencies:
Downloads and unzips the Lesions Segmentation Toolbox (LST) v3.0.0.
Clones the SPM12 and LST-AI repositories, and installs them with pip.
Clones and installs the HD-BET repository.
Downloads the Spinal Cord Toolbox (SCT) installer.

Final Steps: Updates the system PATH, checks installed Python packages, and concludes the setup.

```
. setup.sh
```

FSL is needed for brain age estimation; https://fsl.fmrib.ox.ac.uk/fsl/docs/#/install/index (NB! Install at default location). In addition, a full MATLAB installation is required because mris_compute_lgi does not support the MATLAB Compiler Runtime (MCR).

AFTER installation, please modify the "paths.txt" file in the /bin folder. I have entered my personal MATLAB- and Freesurfer paths for illustration purposes only.

## Usage

This repository uses a specific folder naming convention to organize and manage study data efficiently. The folder names should follow this format:

'StudyName_ParticipantNumber_SessionNumber', e.g. MS_0235_01

This would indicate:

- StudyName: MS (Multiple Sclerosis study),
- ParticipantNumber: 0235 (participant ID 235),
- SessionNumber: 01 (session 1).

** All subject folders must be placed in the "INPUT" ** 

Guidelines:

Always ensure the StudyName is a short, descriptive abbreviation (e.g., MS, AD or STROKE etc.), but is not limited in length as long as it is a singular string. 
The ParticipantNumber must be a 4-digit integer. If the participant number is less than 4 digits, pad it with leading zeros (e.g., 0023, 0567).
The SessionNumber must be a 2-digit integer. If the session number is less than 2 digits, pad it with a leading zero (e.g., 01, 02, 10).

Flexibility Across Multiple Studies

One of the key features of this system is its flexibility in handling data from multiple studies within the same processing batch. You can safely mix data from different studies (e.g., MS, AD, PD for Alzheimer's Disease, Parkinson's Disease, etc.) in the same dataset or processing pipeline. BSL is designed to automatically filter, sort, and organize the data based on the study identifier embedded in each folder name. It uses the StudyName prefix (like MS, AD, etc.) to categorize and label each participant's data correctly within the dataset.

This folder naming convention is critical for maintaining consistency and for automating processes such as data processing, organization, and analysis.

**

I hope you find this GUI both helpful and time-saving in your work. May it streamline your processes, enhance your efficiency, and allow you to focus on the more critical aspects of your tasks. Enjoy exploring its features, and feel free to reach out if there are additional functionalities that could further optimize your workflow!
