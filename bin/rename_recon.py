import os
import shutil

# Define paths to the raw and recon directories
raw_dir = 'raw'
recon_dir = 'recon'

# Get a list of all files in the raw directory
raw_files = os.listdir(raw_dir)

# Create a dictionary to map sub-ses identifiers to full filenames in raw directory
raw_mapping = {}

for file in raw_files:
    if file.endswith('.nii.gz'):
        # Extract the sub and ses information
        sub_ses = '_'.join(file.split('_')[:2])
        # Store the name before the .nii.gz extension
        raw_mapping[sub_ses] = file.rsplit('.nii.gz', 1)[0]

# Get a list of all directories in the recon directory
recon_dirs = os.listdir(recon_dir)

for recon in recon_dirs:
    recon_path = os.path.join(recon_dir, recon)
    if os.path.isdir(recon_path):
        if recon in raw_mapping:
            new_name = raw_mapping[recon]
            new_path = os.path.join(recon_dir, new_name)
            # Rename the recon directory to match the raw filename without the extension
            shutil.move(recon_path, new_path)
            print(f'Renamed {recon_path} to {new_path}')
        else:
            print(f'No matching raw file for {recon}')
