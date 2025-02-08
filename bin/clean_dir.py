import os

def remove_empty_dirs(path):
    # Recursively remove empty directories
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            # Check if the directory is empty or only contains .DS_Store files
            contents = os.listdir(dir_path)
            if '.DS_Store' in contents:
                try:
                    os.remove(os.path.join(dir_path, '.DS_Store'))
                    contents.remove('.DS_Store')  # Remove .DS_Store from the list of contents
                    print(f"Removed .DS_Store from {dir_path}")
                except FileNotFoundError:
                    print(f".DS_Store not found in {dir_path} (it might have been deleted or moved).")
            
            if not contents:  # If the directory is empty after removing .DS_Store
                try:
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                except OSError:
                    pass  # If the directory isn't empty (for other reasons), we skip it

if __name__ == "__main__":
    current_path = os.getcwd()
    remove_empty_dirs(current_path)
