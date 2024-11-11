import os
import subprocess
import tkinter as tk
import psutil
import GPUtil
import matplotlib.pyplot as plt
import threading
import signal
import time
import glob
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from tkinter import ttk, messagebox, Scrollbar, font

# Map script names to display names
script_display_names = {
    "data_preprocessing.sh": "BIDS",
    "fastsurf_runtime.sh": "FastSurfer -All",
    "freesurf_runtime.sh": "FreeSurfer -All",
    "GI_index.sh": "GI-Index  ",
    "lst_ai.sh": "LST-AI",
    "lst.sh": "LST-traditional",
    "sct.sh": "Spinal Cord Toolbox",
    "brain_age_pyment.sh": "Brain Age",
    "qc_stats.sh": "Quality control & Dataset",
}

# Use display names in the GUI
scripts = list(script_display_names.values())

# Assume C_HOME is already set as an environment variable
c_home = os.environ.get('C_HOME')

# Build paths relative to C_HOME
preprocessing_script = os.path.join(c_home, "sys", "pipeline_run.sh")
script_folder = os.path.join(c_home, "bin")
base_folder = os.path.join(c_home, "OUTPUT")
GUI_SCRIPT_PATH = os.path.join(c_home, "sys", "pipeline_gui.py")

# Variable to store the start time
start_time = None

def start_timer():
    global start_time
    start_time = time.time()

# Function to stop the timer
def stop_timer():
    global start_time
    start_time = None

# Function to update the elapsed time label
def update_elapsed_time():
    global start_time, current_process

    if start_time:
        elapsed_time = time.time() - start_time
        elapsed_hours = int(elapsed_time // 3600)  # Calculate elapsed hours
        elapsed_minutes = int((elapsed_time % 3600) // 60)  # Calculate elapsed minutes
        elapsed_seconds = int(elapsed_time % 60)  # Calculate elapsed seconds

        elapsed_time_label.config(text=f"Elapsed Time: {elapsed_hours:03d}:{elapsed_minutes:02d}:{elapsed_seconds:02d}")

        if current_process and current_process.poll() is not None:
            start_time = None

    root.after(1000, update_elapsed_time)

def update_folder_count():
    relative_path = "Data/BIDS"
    directory_path = os.path.join(c_home, relative_path)

    # Use glob to find all folders that match the wildcard pattern
    wildcard_folders = glob.glob(os.path.join(directory_path, '*/'))

    # Initialize folder count
    folder_count = 0

    # Iterate through each wildcard folder and count subfolders starting with "sub"
    for wildcard_folder in wildcard_folders:
        sub_folders = [folder for folder in os.listdir(wildcard_folder) if folder.startswith("sub")]
        folder_count += len(sub_folders)

    # Update the counter label text
    folder_count_label.config(text=f"BIDS Created: {folder_count}")

    # Schedule the function to run again after a delay (e.g., every 1000 milliseconds)
    root.after(1000, update_folder_count)

def run_scripts():
    global current_process, is_paused, start_time, script_folder
    is_paused = False  # Reset the pause flag when starting a new script run
    start_timer()  # Start the timer when the scripts start running
    selected_scripts = [script for script, var in zip(script_display_names.keys(), checkboxes) if var.get()]

    if not selected_scripts and not preprocessing_var.get():
        messagebox.showinfo("No Scripts Selected", "Please select at least one script to run.")
        return

    # Clear existing output
    terminal_output.delete(1.0, tk.END)

    # Start a thread to run scripts
    threading.Thread(target=execute_scripts, args=(selected_scripts,), daemon=True).start()

def execute_scripts(selected_scripts):
    try:
        if preprocessing_var.get():
            run_command(preprocessing_script)
        
        # Ensure the order of execution for GI_index.sh and qc_stats.sh
        prioritized_scripts = []
        
        # First, ensure freeSurf_runtime.sh and fastSurf_runtime.sh are executed first if selected
        if 'freeSurf_runtime.sh' in selected_scripts:
            prioritized_scripts.append('freeSurf_runtime.sh')
            selected_scripts.remove('freeSurf_runtime.sh')
        
        if 'fastSurf_runtime.sh' in selected_scripts:
            prioritized_scripts.append('fastSurf_runtime.sh')
            selected_scripts.remove('fastSurf_runtime.sh')
        
        # Then ensure GI_index.sh is executed after freeSurf_runtime.sh and fastSurf_runtime.sh
        if 'GI_index.sh' in selected_scripts:
            prioritized_scripts.append('GI_index.sh')
            selected_scripts.remove('GI_index.sh')
        
        # Add any remaining scripts (in the selected order)
        prioritized_scripts.extend(selected_scripts)
        
        # Ensure qc_stats.sh is always executed last
        if 'qc_stats.sh' in prioritized_scripts:
            prioritized_scripts.remove('qc_stats.sh')
            prioritized_scripts.append('qc_stats.sh')
        elif 'qc_stats.sh' in selected_scripts:
            prioritized_scripts.append('qc_stats.sh')

        # Execute the scripts in the defined order
        for script in prioritized_scripts:
            script_path = os.path.join(script_folder, script)
            run_command(f"/bin/bash {script_path}")
    finally:
        stop_timer()  # Ensure the timer stops regardless of success or failure

# Function to execute the update script
def update_software():
    global current_process, script_folder
    update_script = "update.sh"  # Replace with the actual update script name

    # Clear existing output
    terminal_output.delete("1.0", tk.END)

    # Make sure 'script_folder' is properly initialized
    if script_folder:
        # Construct full path to the update script
        script_path = os.path.join(script_folder, update_script)

        # Check if the script exists before running it
        if os.path.exists(script_path):
            # Run the update script and display real-time output
            current_process = subprocess.Popen(f"/bin/bash {script_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            # Use a thread to update the terminal output in real-time
            update_output_in_thread(current_process)
        else:
            terminal_output.insert(tk.END, f"Script not found: {script_path}\n")
    else:
        terminal_output.insert(tk.END, "Error: 'script_folder' is not defined.\n")

def longitudinal_mode():
    global current_process, start_time, script_folder

    longitudinal = "longitudinal_mode.sh"  # Replace with the actual update script name

    # Clear existing output
    terminal_output.delete("1.0", tk.END)

    # Make sure 'script_folder' is properly initialized
    if script_folder:
        # Construct full path to the update script
        script_path = os.path.join(script_folder, longitudinal)

        # Check if the script exists before running it
        if os.path.exists(script_path):
            # Start the timer
            start_timer()

            # Run the update script and display real-time output
            current_process = subprocess.Popen(
                f"/bin/bash {script_path}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Use a thread to update the terminal output in real-time
            update_output_in_thread(current_process)

            # Ensure the timer stops when the script completes
            def check_process():
                if current_process.poll() is not None:  # Check if the process has finished
                    stop_timer()  # Stop the timer
                else:
                    root.after(1000, check_process)  # Check again after 1 second

            check_process()  # Start checking the process status
        else:
            terminal_output.insert(tk.END, f"Script not found: {script_path}\n")
    else:
        terminal_output.insert(tk.END, "Error: 'script_folder' is not defined.\n")

def stop_rsync():
    try:
        subprocess.run(["killall", "rsync"], check=True)
        print("rsync process terminated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping rsync: {e}")
        
def show_message(title, message, message_type="info"):
    if message_type == "info":
        messagebox.showinfo(title, message)
    elif message_type == "error":
        messagebox.showerror(title, message)
    elif message_type == "warning":
        messagebox.showwarning(title, message)

def stop_script():
    global current_process, root

    def stop_process(process_name):
        try:
            # Check if the process is running
            result = subprocess.run(["pgrep", "-f", process_name], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(["kill", pid], check=True)
                        print(f"Stopped process with PID {pid} (name: {process_name})")
                    except subprocess.CalledProcessError as e:
                        print(f"Error stopping process with PID {pid}: {e}")
                        #show_message("Error", f"An error occurred while stopping process with PID {pid}.", "error")
                
                # Force stop if necessary
                subprocess.run(["pkill", "-9", "-f", process_name], check=True)
                print(f"Force stopped {process_name}")
            else:
                # Process not found
                print(f"{process_name} not running")
                #show_message("Info", f"{process_name} process not found or could not be stopped.", "info")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping {process_name}: {e}")
            #show_message("Error", f"An error occurred while stopping {process_name}.", "error")

    def stop_all_containers():
        # Loop until all Docker containers are stopped
        while os.popen("docker ps -q").read().strip():
            os.system("docker stop $(docker ps -q)")
            print("Stopped a Docker container.")

    if current_process:
        show_message("Terminate", "Shutting down! This may take a few monents, please wait.. Click OK to proceed")

        stop_process("heudiconv")
        stop_process("data_preprocessing.sh")
        stop_process("MATLAB")
        stop_process("AntsN4BiasFieldCorrectionFs")
        stop_all_containers()
        stop_process("pipeline_gui.py")

    else:
        show_message("No Running Script", "There is no script currently running.", "info")
    
    # Close the GUI after stopping the script
    root.destroy()

# Systems info must be modified to include OSX-tempt for MacOS Host (Linux VM)
def get_system_info():
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    storage_percent = psutil.disk_usage('/').percent

    # Get CPU temperature
    temperatures = psutil.sensors_temperatures()
    cpu_temp = None
    if 'coretemp' in temperatures:
        if temperatures['coretemp']:
            cpu_temp = temperatures['coretemp'][0].current

    # Get GPU temperature
    gpus = GPUtil.getGPUs()
    gpu_temp = gpus[0].temperature if gpus else None

    return cpu_percent, ram_percent, storage_percent, cpu_temp, gpu_temp

cpu_data = []
ram_data = []
storage_data = []

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def update_plot(frame):
    cpu, ram, storage, cpu_temp, gpu_temp = get_system_info()
    cpu_data.append(cpu)
    ram_data.append(ram)
    storage_data.append(storage)

    ax.clear()
    ax.set_xlabel('CPU Usage (%)')
    ax.set_ylabel('RAM Usage (%)')
    ax.set_zlabel('Storage Usage (%)')
    ax.set_title('System Resource Usage Dynamics')

    ax.plot([cpu, cpu], [0, 0], [0, 100], color='blue', linestyle='solid', linewidth=2, alpha=0.8, label='CPU')
    ax.plot([0, 100], [ram, ram], [0, 0], color='green', linestyle='solid', linewidth=2, alpha=0.8, label='RAM')
    ax.plot([0, 0], [0, 100], [storage, storage], color='orange', linestyle='solid', linewidth=2, alpha=0.8, label='Storage')

    ax.plot([cpu, cpu], [ram, ram], [0, 100], color='grey', linestyle='dashed', linewidth=1, alpha=0.6)
    ax.plot([cpu, 100], [ram, ram], [storage, storage], color='grey', linestyle='dashed', linewidth=1, alpha=0.6)

    mean_cpu = sum(cpu_data) / len(cpu_data) if cpu_data else 0
    ax.scatter(mean_cpu, ram, zs=storage, c='r', marker='o', s=100, alpha=1.0, label='Mean CPU')

    text_offset = 8
    ax.text(mean_cpu, ram + text_offset, storage, f'{mean_cpu:.2f}%', color='black', fontsize=10, ha='center', va='bottom')

    # CPU Temperature Display
    if cpu_temp is not None:
        temp_color = 'green' if cpu_temp < 50 else 'orange' if cpu_temp < 80 else 'red'
        ax.text(-50, 0, 120, f'CPU Temp: {cpu_temp}°C', color=temp_color, fontsize=10, ha='left', va='bottom')
    else:
        ax.text(-50, 0, 120, 'CPU Temp: N/A', color='grey', fontsize=10, ha='left', va='bottom')

    # GPU Temperature Display
    if gpu_temp is not None:
        gpu_temp_color = 'green' if gpu_temp < 60 else 'orange' if gpu_temp < 85 else 'red'
        ax.text(-50, 0, 105, f'GPU Temp: {gpu_temp}°C', color=gpu_temp_color, fontsize=10, ha='left', va='bottom')
    else:
        ax.text(-50, 0, 105, 'GPU Temp: N/A', color='grey', fontsize=10, ha='left', va='bottom')

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_zlim(0, 100)

    ax.legend()

def run_command(command):
    global current_process
    current_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    update_output_in_thread(current_process)
    current_process.wait()  # Wait for the process to complete

def update_output_in_thread(process):
    threading.Thread(target=update_output, args=(process,), daemon=True).start()

def update_output(process):
    for line in iter(process.stdout.readline, ''):
        if line:
            # Thread-safe GUI update
            root.after(0, update_terminal_output, line)
    root.after(0, update_terminal_output, "Command completed.\n")

def update_terminal_output(line):
    if "Command completed." in line:
        terminal_output.insert(tk.END, line, "intense_green_large")
    elif "Error" in line:
        terminal_output.insert(tk.END, line, "red")
    else:
        terminal_output.insert(tk.END, line, "intense_green_large")
    terminal_output.see(tk.END)
    terminal_output.update()

def open_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            subprocess.run(['xdg-open', folder_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error opening folder: {e}")
    else:
        print(f"Folder does not exist: {folder_path}")

# Function to create the folder dropdown menu

def create_folder_dropdown(root, base_folder):
    folders = [folder for folder in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, folder))]

    selected_folder_var = tk.StringVar(root)
    default_text = "Show output folder"
    selected_folder_var.set(default_text)

    menu = None  # Initialize the menu variable

    def open_folder(path):
        """Open the specified folder in the file explorer."""
        if os.name == 'nt':  # For Windows
            subprocess.run(['explorer', path], check=True)
        elif os.name == 'posix':  # For macOS/Linux
            if subprocess.call(['which', 'open']) == 0:  # macOS
                subprocess.run(['open', path], check=True)
            elif subprocess.call(['which', 'xdg-open']) == 0:  # Linux
                subprocess.run(['xdg-open', path], check=True)
            else:
                print("Unsupported or unknown environment")
        else:
            print(f"Unsupported OS: {os.name}")

    def on_folder_selected(folder_name):
        if folder_name != default_text:
            selected_folder_path = os.path.join(base_folder, folder_name)
            open_folder(selected_folder_path)
            selected_folder_var.set(default_text)  # Reset to default after selection
            close_menu()  # Close the menu after selection

    def show_menu(event):
        global menu
        menu = tk.Menu(root, tearoff=0)
        for folder in folders:
            menu.add_command(label=folder, command=lambda f=folder: on_folder_selected(f))
        menu.post(event.x_root, event.y_root)
        root.bind("<Button-1>", close_menu)  # Bind to close menu when clicking elsewhere

    def close_menu(event=None):
        """Close the dropdown menu."""
        global menu
        if menu is not None:
            menu.unpost()
            menu = None  # Reset the menu variable
        root.unbind("<Button-1>")  # Unbind the click event when menu is closed

    folder_label = tk.Label(root, textvariable=selected_folder_var, relief="raised", padx=10, pady=5,
                             bg="white", fg="black")
    folder_label.grid(row=12, column=5, padx=1, pady=1)
    folder_label.bind("<Button-1>", show_menu)  # Show the menu on click

def scale_window(root, scale_factor):
    """Scale the window size by a scale factor."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    new_width = int(screen_width * scale_factor)
    new_height = int(screen_height * scale_factor)
    root.geometry(f"1355x485")

# Create the main window
root = tk.Tk()
root.title("MRI Processing Pipeline - BrainSurf Lab v1.0 - Multiple Sclerosis Research Group Oslo")

# Set initial size based on screen resolution
scale_factor = 0.8  # Adjust this scale factor to your needs (e.g., 0.8 for 80% of screen size)
scale_window(root, scale_factor)
root.configure(bg='#FFFFFF')

num_columns = 3  # Number of columns you want
checkboxes = [tk.BooleanVar(value=False) for _ in script_display_names]


# Create checkbuttons
for i, (script, var) in enumerate(zip(script_display_names.values(), checkboxes)):
    row_num = i // num_columns  # Determine the row number
    col_num = i % num_columns   # Determine the column number
    tk.Checkbutton(
        root,
        text=script,
        variable=var,
        fg='#000000',
        bg='#FFFFFF',
        padx=5,
        pady=5,
        relief='flat',
        highlightthickness=0,
        bd=0
    ).grid(row=row_num, column=col_num, sticky="W", padx=5, pady=5)

# Configure rows and columns to expand evenly
total_rows = (len(script_display_names) + num_columns - 1) // num_columns

# Ensure all rows and columns expand evenly
for i in range(total_rows):
    root.grid_rowconfigure(i, weight=1)  # Allow rows to expand equally

for i in range(num_columns):
    root.grid_columnconfigure(i, weight=1)  # Allow columns to expand equally

# Optionally set the minimum size of columns (if needed)
for i in range(num_columns):
    root.grid_columnconfigure(i, minsize=100)  # Set a minimum size for columns

# Optionally set the minimum size of rows (if needed)
for i in range(total_rows):
    root.grid_rowconfigure(i, minsize=30)  # Set a minimum size for rows

separator0 = tk.Canvas(root, height=1, width=10, bg='blue')
separator0.grid(row=len(scripts)+0, column=0, columnspan=4, sticky="ew", pady=5)

separator1 = tk.Canvas(root, height=1, width=10, bg='blue')
separator1.grid(row=len(scripts)+1, column=0, columnspan=2, sticky="ew", pady=5)

separator2 = tk.Canvas(root, height=1, width=10, bg='blue')
separator2.grid(row=len(scripts)+3, column=0, columnspan=6, sticky="ew", pady=5)

# BIDS COUNT LABEL
folder_count_label = tk.Label(root, text="Sub Folders: 0", fg='#000000', bg='#FFFFFF', font=('Helvetica', 14))
folder_count_label.grid(row=12, column=4, pady=10)

# TIMER LABEL
elapsed_time_label = tk.Label(root, text="Elapsed Time: 000:00:00 ", fg='#000000', bg='#FFFFFF', font=('Helvetica', 14))
elapsed_time_label.grid(row=12, column=1, columnspan=2, pady=10)

style = ttk.Style()
style.configure("TButton", foreground='#000000', background='#FFFFFF', padding=(5, 1))

# COMMAND BUTTONS
tk.Button(root, text="Initialize", command=run_scripts, fg='#000000', bg='#FFFFFF', padx=1, pady=5).grid(row=len(scripts)+1, sticky="W", columnspan=1, column=2, padx=1, pady=5)
tk.Button(root, text="Terminate Process", command=stop_script, fg='#000000', bg='#FFFFFF', padx=1, pady=5).grid(row=len(scripts)+1, sticky="W", columnspan=1, column=4, padx=1, pady=5)
tk.Button(root, text="Update", command=update_software, fg='#000000', bg='#FFFFFF', padx=1, pady=5).grid(row=len(scripts)+1, sticky="E", columnspan=1, column=4, padx=1, pady=5)

### LONGITUDINAL ANALYSIS
# This button is for longitudinal analysis
tk.Button(root, text="Initiate Longitudinal Pipeline", command=longitudinal_mode, fg='#000000', bg='#FFFFFF', padx=3, pady=5).grid(row=len(scripts)+0, sticky="E", columnspan=1, column=4, padx=1, pady=1)

###

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

#######

#GPU MODE
#tk.Button(root, text="GPU MODE", command=longitudinal_mode, fg='#000000', bg='#FFFFFF', padx=3, pady=5).grid(row=len(scripts)+3, sticky="E", columnspan=1, column=5, padx=130, pady=1)

def gpu_mode():

    file_path = os.path.join(script_folder, "gpu_mode.txt")

    if toggle_var.get():
        # Code to enable GPU mode
        button.config(bg='#00FF00', text="GPU MODE: ON")  # Change button text and color
        
        with open(file_path, "w") as f:
            f.write("TRUE")  # Write TRUE when GPU mode is ON
        
    else:
        # Code to disable GPU mode
        button.config(bg='#FF0000', text="GPU MODE: OFF")  # Change button text and color
        
        with open(file_path, "w") as f:
            f.write("FALSE")  # Write FALSE when GPU mode is OFF

# Variable to keep track of the toggle state
toggle_var = tk.BooleanVar(value=False)

# Create the toggle button
button = tk.Button(root, text="GPU MODE: OFF", command=lambda: [toggle_var.set(not toggle_var.get()), gpu_mode()], 
                   fg='#000000', bg='#FF0000', padx=3, pady=5)

button.grid(row=len(scripts)+3, sticky="E", columnspan=1, column=5, padx=117, pady=1)


######

# Global variable for MAX_JOBS
MAX_JOBS = None

def update_max_jobs():
    global MAX_JOBS
    try:
        # Get the value from the entry box and convert it to an integer
        MAX_JOBS = int(max_jobs_entry.get())
        print(f"MAX_JOBS updated to: {MAX_JOBS}")  # For debugging purposes

         # Define the path for the max_jobs.txt file
        file_path = os.path.join(script_folder, "max_jobs.txt")

        # Write the MAX_JOBS value to the specified file
        with open(file_path, "w") as f:
            f.write(str(MAX_JOBS))
        
        # Show confirmation message
        messagebox.showinfo("Confirmation", f"MAX_JOBS has been set to: {MAX_JOBS}")
    except ValueError:
        mess

# Define a custom font with a larger size
custom_font = font.Font(size=14)  # Change size to your desired value

max_jobs_entry = tk.Entry(root, width=3, font=custom_font)  # Set custom font
max_jobs_entry.grid(row=len(scripts)+3, column=5, padx=145, pady=1, sticky="W")  # Align to West
max_jobs_entry.insert(0, "1")  # Set default value to 1


# Create a button to update MAX_JOBS
update_button = tk.Button(root, text="Set (Batch size) --> ", command=update_max_jobs, fg='#000000', bg='#FFFFFF', padx=5, pady=5)
update_button.grid(row=len(scripts)+3, column=5, padx=1, pady=1, sticky="W")  # Align to East

# Set initial value if needed (optional)
# max_jobs_entry.insert(0, str(MAX_JOBS))  # 
#########

def edit_heuristic_file():
    file_path = os.path.expandvars('$C_HOME/bin/code/heuristic.py')
    subprocess.run(['xdg-open', file_path])  # Opens file in the default editor

# Example button for editing heuristic
edit_button = tk.Button(root, text="Edit heuristic", command=edit_heuristic_file, fg='#000000', bg='#FFFFFF', padx=5, pady=5)
edit_button.grid(row=len(scripts)+3, column=5, padx=1, pady=1, sticky="E")  # Same row, adjust column as needed

# RUN FULL PIPELINE BUTTON / TEXT SIZE (potential spot for other monitoring)
preprocessing_var = tk.BooleanVar(value=False)
font_size = 10
font_style = ('Helvetica', font_size)

# INITIALIZE MAIN-FULL
tk.Checkbutton(root, text=" Run Full Pipeline ", variable=preprocessing_var, fg='#000000', bg='#FFFFFF', padx=5, pady=5, font=font_style, borderwidth=1, relief="groove", highlightthickness=1, highlightbackground='#FFFFFF', activebackground='#FFFFFF', selectcolor='#FFFFFF').grid(row=len(scripts)+1, column=0, columnspan=2, sticky="W")
###

# INTEGRATED TERMINAL SETTINGS
terminal_output = tk.Text(root, height=28, width=10, wrap=tk.WORD, fg='#00FF00', bg='#000000', font=('Helvetica', 9))
terminal_output.grid(row=len(scripts)+2, column=0, columnspan=5, padx=10, pady=5, sticky="nsew")
##

# Ensure the row and columns are properly configured to expand
root.grid_rowconfigure(len(scripts)+2, weight=1)
root.grid_columnconfigure(0, weight=1)  # Adjust column weight to allow expansion
root.grid_columnconfigure(1, weight=0)  # Adjust weight if needed
root.grid_columnconfigure(2, weight=0)  # Column for scrollbar

# Function to save the terminal output to a file
def save_output():
    output = terminal_output.get("1.0", tk.END)  # Get all text from the terminal output
    if output.strip():  # Check if there is any output to save
        save_path = os.path.join(c_home, "OUTPUT", "terminal_output.txt")  # Define the save path
        with open(save_path, 'w') as file:  # Open the file in write mode
            file.write(output)  # Write the output to the file
        show_message("Output Saved", f"Terminal output saved to {save_path}", "info")  # Show success message
    else:
        show_message("No Output", "There is no output to save.", "info")  # Show message if no output

# Add a button to save terminal output
save_button = tk.Button(root, text="Save Terminal Output", command=save_output, fg='#000000', bg='#FFFFFF', padx=5, pady=5)
save_button.grid(row=len(scripts)+3, column=0, padx=1, pady=1, sticky="NE")  # Add button to the grid layout

# FIGURE PLOT
fig = plt.Figure()
ax = fig.add_subplot(111, projection='3d')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=5, rowspan=len(scripts)+3, padx=1)

ani = FuncAnimation(fig, update_plot, blit=False, cache_frame_data=False)

###

create_folder_dropdown(root, base_folder)
update_elapsed_time()
update_folder_count()

welcome_message = """
Welcome to Brain Surf Lab (BSL) v1.0, by Lars Skattebøl - An MRI processing tool

BSL is designed to select and execute specific MRI processing scripts from a list, covering tasks like data preprocessing, pipeline runtimes, Gyrification Index calculation, lesion segmentation, spinal cord analysis, brain age estimation, quality control and dataset generation.

A 3D plot dynamically visualizes system resource usage, including CPU, RAM, and storage, providing insights into the performance of the processing tasks.

The "Run Full Pipeline" option automates the sequential execution of all scripts for multiple subjects. This streamlines the processing workflow for comprehensive data analysis.

Enjoy!
"""

terminal_output.insert(tk.END, welcome_message, ("intense_green_large", "large_font"))
terminal_output.see(tk.END)
terminal_output.update()

terminal_output.tag_configure("intense_green_large", foreground="#00FF00")
terminal_output.tag_configure("large_font", font=('Helvetica', 11))

root.mainloop()
