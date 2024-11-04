import os
import shutil
import sys

# Function to rename and move all files for a given folder
def process_folder(folder_path):
    existing_files = set(os.listdir(folder_path))  # Existing files in the base folder

    # List subdirectories and process each
    for sub_dir in os.listdir(folder_path):
        sub_dir_path = os.path.join(folder_path, sub_dir)

        # Ensure it's a subdirectory
        if not os.path.isdir(sub_dir_path):
            continue

        for file_name in os.listdir(sub_dir_path):
            new_file_name = file_name
            file_path = os.path.join(sub_dir_path, file_name)
            target_path = os.path.join(folder_path, new_file_name)

            # If the file already exists, append the subdirectory to its name
            if new_file_name in existing_files:
                file_base, file_extension = os.path.splitext(file_name)
                file_extension = file_extension or '.dcm'  # Assume .dcm if no extension
                new_file_name = f"{file_base}_{sub_dir}{file_extension}"
                target_path = os.path.join(folder_path, new_file_name)

            # Move and rename the file
            shutil.move(file_path, target_path)
            existing_files.add(new_file_name)  # Update the set of existing files

        # Remove the subdirectory if it's empty
        if not os.listdir(sub_dir_path):
            os.rmdir(sub_dir_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py base_path")
        sys.exit(1)
        
    base_path = sys.argv[1]

    # Separate pipelines for different input
    for base_folder_name in os.listdir(base_path):
        base_folder_path = os.path.join(base_path, base_folder_name)
        
        # Skip if it's not a directory
        if not os.path.isdir(base_folder_path):
            continue

        # Process folders
        process_folder(base_folder_path)
