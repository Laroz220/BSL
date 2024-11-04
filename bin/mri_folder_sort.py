import os
import shutil
import time

def move_file(source, destination):
    """
    Move a file from source to destination without printing the filename.
    """
    try:
        shutil.move(source, destination)
    except Exception as e:
        print(f"Failed to move {os.path.basename(source)} to {destination}: {e}")

def extract_files_to_subfolder(subdir):
    """
    Move all files from sub-subdirectories to the immediate subfolder.
    """
    if all(os.path.isfile(os.path.join(subdir, item)) for item in os.listdir(subdir)):
        return

    for root, dirs, files in os.walk(subdir, topdown=False):
        for file_name in files:
            if file_name != '.DS_Store':
                file_path = os.path.join(root, file_name)
                if os.path.isfile(file_path) and root != subdir:
                    move_file(file_path, os.path.join(subdir, file_name))

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
            os.rmdir(dir_path)
            print(f"Successfully removed {dir_path}")
            break
        except OSError as e:
            if e.errno == 66:  # Directory not empty
                print(f"Failed to remove {dir_path}: {e}. Retrying...")
                time.sleep(delay)
            else:
                print(f"Failed to remove {dir_path}: {e}")
                break

def remove_empty_directory_with_files(dir_path, retries=3, delay=2):
    """
    Attempt to remove a directory, including any files it contains.
    """
    for _ in range(retries):
        try:
            # Remove all contents
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    remove_empty_directory_with_files(item_path)
                else:
                    os.remove(item_path)
            
            # Remove the directory itself
            os.rmdir(dir_path)
            print(f"Successfully removed {dir_path}")
            break
        except Exception as e:
            print(f"Failed to remove {dir_path}: {e}. Retrying...")
            time.sleep(delay)

def rename_files_in_subfolder(subdir, prefix):
    """
    Rename files in the subfolder to include the prefix (parent_folder_subfolder_name)
    only if the subfolder name is a number.
    """
    if not subdir.split(os.sep)[-1].isdigit():
        return

    for file_name in os.listdir(subdir):
        if file_name != '.DS_Store':
            file_path = os.path.join(subdir, file_name)
            if os.path.isfile(file_path):
                new_file_name = f"{prefix}_{file_name}"
                new_file_path = os.path.join(subdir, new_file_name)
                os.rename(file_path, new_file_path)

def process_folders(folder_path):
    """
    Process each subfolder to extract files to the subfolder and then rename them
    if the subfolder name is a number.
    """
    parent_folders_to_check = []
    for study_folder in os.listdir(folder_path):
        study_folder_path = os.path.join(folder_path, study_folder)
        if os.path.isdir(study_folder_path):
            parent_folders_to_check.append(study_folder_path)
            for session_folder in os.listdir(study_folder_path):
                session_folder_path = os.path.join(study_folder_path, session_folder)
                if os.path.isdir(session_folder_path):
                    extract_files_to_subfolder(session_folder_path)
                    if session_folder.isdigit():
                        rename_files_in_subfolder(session_folder_path, f"{study_folder}_{session_folder}")
                        new_session_folder_name = f"{study_folder}_{session_folder}"
                        new_session_folder_path = os.path.join(folder_path, new_session_folder_name)
                        os.rename(session_folder_path, new_session_folder_path)
                    else:
                        # If the session folder name is not a number, move files up one level without renaming
                        for item in os.listdir(session_folder_path):
                            item_path = os.path.join(session_folder_path, item)
                            if os.path.isfile(item_path):
                                shutil.move(item_path, os.path.join(study_folder_path, item))
                        remove_empty_directory_with_files(session_folder_path)

def remove_empty_parent_folders(parent_folders):
    """
    Remove parent folders if they are empty.
    """
    for folder in parent_folders:
        try:
            os.rmdir(folder)
            print(f"Successfully removed empty parent folder: {folder}")
        except OSError as e:
            if e.errno == 39:  # Directory not empty
                print(f"Parent folder not empty, skipping removal: {folder}")
            else:
                print(f"Failed to remove {folder}: {e}")

def main():
    folder_path = os.getcwd()  # Use the current working directory
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return

    process_folders(folder_path)

if __name__ == "__main__":
    main()
