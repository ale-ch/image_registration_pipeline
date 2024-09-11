import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to trigger the process
def run_process():
    main_dir = main_dir_entry.get()
    export_path = export_path_entry.get()
    make_dirs = make_dirs_var.get()
    input_dir_conv = input_dir_conv_entry.get()
    output_dir_conv = output_dir_conv_entry.get()
    output_dir_reg = output_dir_reg_entry.get()
    
    # Check if main_dir is provided
    if not main_dir:
        messagebox.showerror("Error", "--main-dir is required")
        return
    
    # Check if main_dir exists
    if not os.path.isdir(main_dir):
        messagebox.showerror("Error", f"main_dir does not exist: {main_dir}")
        return

    # Set default paths if not provided
    if not export_path:
        export_path = f"{main_dir}/logs/io/sample_sheet_current.csv"
    if not input_dir_conv:
        input_dir_conv = f"{main_dir}/data/input/image_conversion"
    if not output_dir_conv:
        output_dir_conv = f"{main_dir}/data/output/image_conversion"
    if not output_dir_reg:
        output_dir_reg = f"{main_dir}/data/output/image_registration"
    
    # Run the Python scripts as per the bash script
    os.system(f'python bin/utils/generate_sample_sheet/update_io.py --input-dir "{input_dir_conv}" --output-dir "{output_dir_conv}" --input-ext ".nd2" --output-ext ".ome.tiff" --logs-dir "{main_dir}/logs" --backup-dir "{main_dir}/logs/io/backups" --colnames patient_id input_path_conv output_path_conv converted filename --export-path "{main_dir}/logs/io/conv_sample_sheet.csv" --make-dirs')
    os.system(f'python bin/utils/generate_sample_sheet/assign_fixed_image.py --samp-sheet-path "{main_dir}/logs/io/conv_sample_sheet.csv" --export-path "{main_dir}/logs/io/conv_sample_sheet.csv"')
    os.system(f'python bin/utils/generate_sample_sheet/update_io.py --input-dir "{input_dir_conv}" --output-dir "{output_dir_reg}" --input-ext ".nd2" --output-ext ".ome.tiff" --logs-dir "{main_dir}/logs" --backup-dir "{main_dir}/logs/io/backups" --colnames patient_id input_path_reg output_path_reg registered filename --export-path "{main_dir}/logs/io/reg_sample_sheet.csv" --make-dirs')
    os.system(f'python bin/utils/generate_sample_sheet/remove_columns.py --csv-file-path "{main_dir}/logs/io/reg_sample_sheet.csv" --column input_path_reg patient_id --export-path "{main_dir}/logs/io/reg_sample_sheet.csv"')
    os.system(f'python bin/utils/generate_sample_sheet/join_samp_sheets.py --samp-sheets-paths "{main_dir}/logs/io/conv_sample_sheet.csv" "{main_dir}/logs/io/reg_sample_sheet.csv" --key-col-name "patient_id" --filter-pending --export-path "{export_path}" --export-path-filtered "{export_path}" --backup-dir "{main_dir}/logs/io/backups"')
    
    messagebox.showinfo("Success", "Process completed successfully!")

# Function to select main directory
def select_main_dir():
    dir_path = filedialog.askdirectory()
    if dir_path:
        main_dir_entry.delete(0, tk.END)
        main_dir_entry.insert(0, dir_path)

# Function to select export path
def select_export_path():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        export_path_entry.delete(0, tk.END)
        export_path_entry.insert(0, file_path)

# Function to select input directory for conversion
def select_input_dir_conv():
    dir_path = filedialog.askdirectory()
    if dir_path:
        input_dir_conv_entry.delete(0, tk.END)
        input_dir_conv_entry.insert(0, dir_path)

# Function to select output directory for conversion
def select_output_dir_conv():
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_dir_conv_entry.delete(0, tk.END)
        output_dir_conv_entry.insert(0, dir_path)

# Function to select output directory for registration
def select_output_dir_reg():
    dir_path = filedialog.askdirectory()
    if dir_path:
        output_dir_reg_entry.delete(0, tk.END)
        output_dir_reg_entry.insert(0, dir_path)

# Create the main window
root = tk.Tk()
root.title("Sample Sheet Generator")

# Labels and input fields
tk.Label(root, text="Main Directory").grid(row=0, column=0, sticky="e")
main_dir_entry = tk.Entry(root, width=50)
main_dir_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_main_dir).grid(row=0, column=2)

tk.Label(root, text="Export Path [/path/to/file.csv] (Optional)").grid(row=1, column=0, sticky="e")
export_path_entry = tk.Entry(root, width=50)
export_path_entry.grid(row=1, column=1, padx=10, pady=5)

make_dirs_var = tk.StringVar(value="true")
tk.Label(root, text="Make Dirs").grid(row=2, column=0, sticky="e")
tk.OptionMenu(root, make_dirs_var, "true", "false").grid(row=2, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Input Dir Conv (Optional)").grid(row=3, column=0, sticky="e")
input_dir_conv_entry = tk.Entry(root, width=50)
input_dir_conv_entry.grid(row=3, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_input_dir_conv).grid(row=3, column=2)

tk.Label(root, text="Output Dir Conv (Optional)").grid(row=4, column=0, sticky="e")
output_dir_conv_entry = tk.Entry(root, width=50)
output_dir_conv_entry.grid(row=4, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_output_dir_conv).grid(row=4, column=2)

tk.Label(root, text="Output Dir Reg (Optional)").grid(row=5, column=0, sticky="e")
output_dir_reg_entry = tk.Entry(root, width=50)
output_dir_reg_entry.grid(row=5, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=select_output_dir_reg).grid(row=5, column=2)

# Run button
tk.Button(root, text="Run", command=run_process, bg="green", fg="black").grid(row=6, column=0, columnspan=3, pady=20)

# Start the main loop
root.mainloop()
