import os
import json
import time
from pathlib import Path

def folder_structure_to_json(folder_path, output_file = Path('data') / 'folder_structure.json'):
    """Creates or appends data to a JSON file in the specified format."""
    output_file_path = Path('data') / 'folder_structure.json'

    if output_file_path.exists():
        with output_file_path.open('r') as json_file:
            data = json.load(json_file)
    else:
        data = {"folders": []}

    folder_structure = {}
    current_time = int(time.time())

    for root, dirs, files in os.walk(folder_path):
        current_folder = folder_structure
        for dir_name in root[len(folder_path):].split(os.path.sep):
            if dir_name:
                current_folder = current_folder.setdefault(dir_name, {})

        for file_name in files:
            file_path = os.path.join(root, file_name)
            last_modification_time = os.path.getmtime(file_path)
            current_folder[file_name] = int(last_modification_time)

    folder_entry = {
        "name": folder_path,
        "data": [{"time": current_time, "structure": folder_structure}]
    }

    for folder in data["folders"]:
        if folder["name"] == folder_path:
            folder["data"].append({"time": current_time, "structure": folder_structure})
            break
    else:
        data["folders"].append(folder_entry)

    with output_file_path.open('w') as json_file:
        json.dump(data, json_file, indent=4)

# def difference_between_last_and_new(folder_path, output_file = Path('data') / 'folder_structure.json'):


# folder_structure_to_json(folder_path)