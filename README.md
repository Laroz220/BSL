# BrainSurf Lab (BSL) - An automated MRI Processing Pipeline and dataset generator

![Screenshot 2024-11-04 at 22 04 36](https://github.com/user-attachments/assets/a6eecf91-2dbc-43ba-86a5-bc6d67d5bf8c)

## Introduction
BSL is an attempt to alleviate the traditionally time-consuming and complex process of manually scripting, organizing, and harmonizing MRI data prior to statistical analyses. Typically, researchers spend significant time and effort preparing MRI data—writing custom scripts for each processing step, ensuring data consistency, and integrating various datasets into a unified format. This manual approach often introduces inefficiencies and the risk of errors, especially when managing large, multi-subject studies.

By automating these processes, we aim to reduce the overall manual workload. In BSL, you can also select and execute specific MRI processing scripts, ranging from data preprocessing and lesion segmentation to advanced tasks like Gyrification Index calculation and brain age estimation. Additionally, the "Full Pipeline" option offers complete streamlining by automating the sequential execution of all scripts for multiple subjects, and studies, ensuring that the entire workflow is cohesive and consistent.

BSL also has an integrated 3D plot feature for visualizing system resource usage in real-time. This visualization allows researchers to monitor and optimize CPU, RAM, and storage usage, ensuring that the system operates efficiently and stabile throughout the data processing stages.

In essence, BSL pushes to accelerate data preparation and dataset harmonization across subjects, transforming what would typically be a labor-intensive and error-prone task into a streamlined efficient workflow, allowing researchers to focus more on analysis and interpretation rather than data preparation.

## Setup and Requirements
Firstly, ensure that you have Python installed on your system. For consistency and stable resource monitoring, a custom virtual environment created with 'python -m venv' is preferred for the GUI.

At least 16 GB of RAM or VRAM (for GPU mode) is recommended and 14 GB free space. The software has been tested on Linux 20.04 and 22.04, with dual Intel Xeon (Single AMD Radeon pro 5100, GPU mode not supported), Intel Core i7 (Single Nvidia GTX 1080, GPU mode enabled), and AMD Ryzen Threadripper (Dual Nvidia RTX4090 SLI) using python 3.8/3.9, the latter version being a prerequesite from quality control. For MacOS, VirtualBox w/ Linux 20.04 is recommended. 

Other third-party softwares prerequesites not integrated in this install are: Matlab, FSL and Docker (see part 2c, bottom line).

The following command updates your system’s package lists and installs several tools: git for version control, wget for downloading files, unzip for extracting ZIP archives, python3 for the Python interpreter, and python3-pip for managing Python packages. The -y flag ensures that the installation proceeds without prompting for confirmation.

```
sudo apt-get update && sudo apt-get install -y git wget curl tcsh unzip python3 python3-pip gcc && \
sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt-get update && \

sudo apt-get install -y python3.9 python3.9-venv python3.8 python3.8-venv && \
sudo apt-get install -y python3.9-tk python3.8-tk && sudo apt-get update
```

### 1.) Clone to desired install path
```
git clone git@github.com:Laroz220/BrainSurf.git && cd BSL
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

pip install -r requirements_brainsurf.txt && pip check && \
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

Docker is needed for fastsurfer. For installation (if not installed already), please follow these instructions: 'https://docs.docker.com/engine/install/'. FSL is needed for brain age estimation; https://fsl.fmrib.ox.ac.uk/fsl/docs/#/install/index (NB! Install at default location).

AFTER installation, please modify the "paths.txt" file in the /bin folder. I have entered my personal MATLAB- and Freesurfer paths for illustration purposes only.
