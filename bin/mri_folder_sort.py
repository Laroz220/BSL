import os
import shutil
import time

def move_file(source, destination):
    """
    Move a file from source to destination without printing the filename. If the destination file already exists,
    add a numerical suffix to the filename to avoid overwriting.
    """
    base_name, extension = os.path.splitext(os.path.basename(source))
    destination_path = os.path.join(destination, os.path.basename(source))
    
    # Handle duplicates by adding a numerical suffix
    counter = 1
    while os.path.exists(destination_path):
        destination_path = os.path.join(destination, f"{base_name}_{counter}{extension}")
        counter += 1
    
    try:
        shutil.move(source, destination_path)
    except Exception as e:
        print(f"Failed to move {os.path.basename(source)} to {destination_path}: {e}")

def extract_files_to_parent(subdir, parent_dir):
    """
    Move all files from subdirectories (including deeper ones) to the immediate parent directory.
    If files already exist, add a numerical suffix to avoid overwriting.
    """
    for root, dirs, files in os.walk(subdir, topdown=False):
        for file_name in files:
            if file_name != '.DS_Store':  # Skip .DS_Store files (macOS)
                file_path = os.path.join(root, file_name)
                if os.path.isfile(file_path) and root != parent_dir:
                    # Move each file to the parent directory
                    move_file(file_path, parent_dir)

        # Remove empty directories after files have been moved
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if os.path.isdir(dir_path):
                remove_directory_with_retry(dir_path)

def remove_directory_with_retry(dir_path, retries=3, delay=2):
    """
    Attempt to remove a directory, retrying if the directory is not empty.
    """
    for _ in range(retries):
        try:
            # Remove directory only if it's empty
            if not os.listdir(dir_path):  # Check if directory is empty
                os.rmdir(dir_path)
                print(f"Successfully removed empty directory: {dir_path}")
                break
            else:
                print(f"Directory {dir_path} is not empty, skipping removal.")
                break
        except OSError as e:
            if e.errno == 66:  # Directory not empty
                print(f"Failed to remove {dir_path}: {e}. Retrying...")
                time.sleep(delay)
            else:
                print(f"Failed to remove {dir_path}: {e}")
                break

def process_folders(folder_path):
    """
    Process each subfolder to extract files to the parent folder.
    """
    parent_folders_to_check = []
    for study_folder in os.listdir(folder_path):
        study_folder_path = os.path.join(folder_path, study_folder)
        if os.path.isdir(study_folder_path):
            parent_folders_to_check.append(study_folder_path)
            for session_folder in os.listdir(study_folder_path):
                session_folder_path = os.path.join(study_folder_path, session_folder)
                if os.path.isdir(session_folder_path):
                    extract_files_to_parent(session_folder_path, study_folder_path)

def main():
    folder_path = os.getcwd()  # Use the current working directory
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return

    process_folders(folder_path)

if __name__ == "__main__":
    main()
