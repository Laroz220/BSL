import os

def remove_empty_dirs(path):
    # Recursively remove empty directories
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            # Check if the directory is empty or only contains .DS_Store files
            contents = os.listdir(dir_path)
            if all(item == '.DS_Store' for item in contents):
                os.remove(os.path.join(dir_path, '.DS_Store'))
                contents.remove('.DS_Store')
            if not contents:
                try:
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                except OSError:
                    pass

if __name__ == "__main__":
    current_path = os.getcwd()
    remove_empty_dirs(current_path)
