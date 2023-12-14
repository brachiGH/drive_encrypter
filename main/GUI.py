import tkinter as tk
from tkinter import filedialog
import os
from pathlib import Path

import threading
import time

from libs.compress import *
from libs.foldersManger import *

compressedfolder = compress()





def print_encrypt_files():
    """Prints 'done' every second."""
    while True:
        folder_path = "C:\\Users\\pc\\Desktop\\files to encrypt"

        files_list.delete(0, tk.END)
        for root, dirs, files in os.walk(folder_path):
            level = root.replace(folder_path, '').count(os.sep)
            for file in files:
                file_path = os.path.join(root, file)
                files_list.insert(tk.END, file_path)

        time.sleep(3)


def display_file_structure():
    """Displays the file structure of the selected folder in a box."""
    folder_path = filedialog.askdirectory()
    compressedfolder.folder_path = folder_path
    folder_structure_to_json(folder_path)


    if folder_path:
        file_structure.delete('1.0', tk.END)

        for root, dirs, files in os.walk(folder_path):
            level = root.replace(folder_path, '').count(os.sep)
            indent = ' ' * 4 * level
            file_structure.insert(tk.END, f'{indent}[{os.path.basename(root)}]\n')
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                file_structure.insert(tk.END, f'{sub_indent}{file}\n')

def display_file_content(event):
    """Displays the content of the selected file."""
    selection = files_list.curselection()
    if selection:
        file_path = files_list.get(selection[0])
        with open(file_path, 'r') as file:
            content_text.delete('1.0', tk.END)
            content_text.insert(tk.END, file.read())

def display_file_save():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    compressedfolder.archive_path = file_path
    compressedfolder.compress_and_encrypt_folder()

# Create the GUI window
window = tk.Tk()

# Create the file structure box
file_structure = tk.Text(window, height=40, width=70)
file_structure.pack(side=tk.LEFT, padx=10, pady=10)

# Create the files list
files_list = tk.Listbox(window, height=40, width=60)
files_list.pack(side=tk.LEFT, padx=10, pady=10)
files_list.bind('<<ListboxSelect>>', display_file_content)

# Create the content box
content_text = tk.Text(window, height=40, width=60)
content_text.pack(side=tk.LEFT, padx=10, pady=10)

# Create the button
button = tk.Button(window, text='Select Folder to upload', command=display_file_structure)
button.pack(pady=10)
button = tk.Button(window, text='Select Folder to save', command=display_file_save)
button.pack(pady=10)

# Create and start the separate thread
thread = threading.Thread(target=print_encrypt_files)
thread.daemon = True
thread.start()

# Run the GUI event loop
window.mainloop()


