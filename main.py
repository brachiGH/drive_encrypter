import os
import json
import threading
import pickle
import google.auth
import google.auth.transport.requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
import mimetypes
import time
from urllib.parse import unquote
from tkinter import messagebox
from pathlib import Path
import datetime


def get_mime_type(file_path):
    """Gets the MIME type of a file."""
    return mimetypes.guess_type(file_path)[0]


BASE_DIR = Path(__file__).resolve().parent


# Define the path to the credentials JSON file
credentials_path = 'privite/client_secret_9058769209.apps.googleusercontent.com.json'

# Define the path to the token pickle file
token_path = 'privite/token.pickle'

# Define the MIME type of the file
# mime_type = 'application/octet-stream'  # Modify based on the file type

# List_Of_Uploaded_Folders       
backuper_folder_id = '1EQNnxIuPWaxh9e9T_hpHDW5BeHouClkc' #backuper

Master_password = *******************************




#######################################
##  encrypter  ##
#######################################
from cryptography.fernet import Fernet
from io import BytesIO
import base64

# Generate a random 32-byte key
# ur = os.urandom(32)
# encryption_key = base64.urlsafe_b64encode(ur)
# print(ur,encryption_key)

def encrypt_file(input_path, password):
    encryption_key = password.encode('utf-8')
    with open(input_path, 'rb') as file:
        data = file.read()

    fernet = Fernet(encryption_key)
    encrypted_data = fernet.encrypt(data)
    return encrypted_data

def decrypt_data(encrypted_data, password):
    encryption_key = password.encode('utf-8')
    fernet = Fernet(encryption_key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data


def calculate_encrypted_size(original_size):
    block_size = 16  # AES block size in bytes
    padding = 15  # PKCS#7 padding
    overhead = 16 + 16 + 47  # IV size + timestamp size + metadata size

    encrypted_size = (original_size // block_size + 1) * (block_size + padding) + overhead
    return encrypted_size
########################################




#################################
##  Google modified upload  ##
#################################
from googleapiclient import _helpers as util
DEFAULT_CHUNK_SIZE = 100 * 1024 * 1024

class MediaFileUpload_modified(MediaIoBaseUpload):
    """A MediaUpload for a file.

    Construct a MediaFileUpload and pass as the media_body parameter of the
    method. For example, if we had a service that allowed uploading images:

      media = MediaFileUpload('cow.png', mimetype='image/png',
        chunksize=1024*1024, resumable=True)
      farm.animals().insert(
          id='cow',
          name='cow.png',
          media_body=media).execute()

    Depending on the platform you are working on, you may pass -1 as the
    chunksize, which indicates that the entire file should be uploaded in a single
    request. If the underlying platform supports streams, such as Python 2.6 or
    later, then this can be very efficient as it avoids multiple connections, and
    also avoids loading the entire file into memory before sending it. Note that
    Google App Engine has a 5MB limit on request size, so you should never set
    your chunksize larger than 5MB, or to -1.
    """

    @util.positional(2)
    def __init__(self, filename, mimetype=None, chunksize=DEFAULT_CHUNK_SIZE, resumable=False, encrypt=True):
        """Constructor.

        Args:
          filename: string, Name of the file.
          mimetype: string, Mime-type of the file. If None then a mime-type will be
            guessed from the file extension.
          chunksize: int, File will be uploaded in chunks of this many bytes. Only
            used if resumable=True. Pass in a value of -1 if the file is to be
            uploaded in a single chunk. Note that Google App Engine has a 5MB limit
            on request size, so you should never set your chunksize larger than 5MB,
            or to -1.
          resumable: bool, True if this is a resumable upload. False means upload
            in a single request.
        """
        

        def return_encrypted_file_as_open_in_mode_rb(input_file_path):
            # input_file_path = 'path_to_your_input_file'
            encrypted_data = encrypt_file(input_file_path, Master_password)
            print(f"The file size after encryption: {(len(encrypted_data)/(1024*1024)):.2f} MB")
            # print(decrypt_data(encrypted_data))

            # Use BytesIO to open decrypted data as if it were a file in 'rb' mode
            decrypted_file_object = BytesIO(encrypted_data)
            
            # Now you can use 'decrypted_file_object' as if it's a file opened in 'rb' mode
            # For example:
            # decrypted_file_content = decrypted_file_object.read()
            return decrypted_file_object
    
        self._fd = None
        self._filename = filename
        print(self._filename)
        print(f"The file size before encryption: {(os.path.getsize(self._filename)/(1024*1024)):.2f} MB")

        if encrypt:
            self._fd = return_encrypted_file_as_open_in_mode_rb(self._filename)
        else:
            self._fd = open(self._filename, "rb")

        if mimetype is None:
            # No mimetype provided, make a guess.
            mimetype, _ = mimetypes.guess_type(filename)
            if mimetype is None:
                # Guess failed, use octet-stream.
                mimetype = "application/octet-stream"
        super(MediaFileUpload_modified, self).__init__(
            self._fd, mimetype, chunksize=chunksize, resumable=resumable
        )

    def __del__(self):
        if self._fd:
            self._fd.close()

    def to_json(self):
        """Creating a JSON representation of an instance of MediaFileUpload.

        Returns:
           string, a JSON representation of this instance, suitable to pass to
           from_json().
        """
        return self._to_json(strip=["_fd"])

    @staticmethod
    def from_json(s):
        d = json.loads(s)
        return MediaFileUpload_modified(
            d["_filename"],
            mimetype=d["_mimetype"],
            chunksize=d["_chunksize"],
            resumable=d["_resumable"],
        )



##########################################
##########################################







##########################################
##  comparer  ##
##########################################

def generate_folder_tree(__path, save=False):
    data = {
        'name': os.path.basename(__path),
        'type': 'folder',
        'id': None,
        'created_time': int(Path(__path).stat().st_mtime),  # Adding the creation time in epoch format
        'path': os.path.dirname(__path),
        'children': []
    }
    
    for item in os.listdir(__path):
        item_path = os.path.join(__path, item)
        if os.path.isdir(item_path):
            data['children'].append(generate_folder_tree(item_path))
        else:
            data['children'].append({
                'name': item,
                'type': 'file',
                'id': None,
                'created_time': int(Path(item_path).stat().st_mtime),  # Adding the creation time in epoch format
                'path':__path
            })
    
    if save:
        with open('data\\'+os.path.basename(__path)+'.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return data
    else:
        return data


def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def save_json_file(__path, data):
    with open('data\\'+os.path.basename(__path)+'.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)


# folder_path = 'backupervenv\Include'
# output_json_path = 'folder_tree.json'
# old_folder_tree = load_json_file(output_json_path)
# new_folder_tree = generate_folder_tree(folder_path)

# with open(output_json_path, 'w') as json_file:
#     json.dump(new_folder_tree, json_file, indent=4)



##############################################
##############################################







###################################################
####   popout    ####
###################################################
import tkinter as tk
from tkinter import ttk


class popout():
    def __init__(self, title="Progress Bar", text="Downloading"):
        self.root = tk.Tk()
        self.root.title(title)

        self.label = tk.Label(self.root, text=text, font=("Helvetica", 14))
        self.label.pack(pady=10)

        self.size_label = tk.Label(self.root, text="../.. MB", font=("Helvetica", 14))
        self.size_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.root, mode='determinate', length=300)
        self.progress_bar.pack(pady=10)

        self.update_label = tk.Label(self.root, text="Progress: 0%")
        self.update_label.pack(pady=5)

        self.current_progress = 0
        self.start_time = None
        self.timer_on_off = True

        

    def run_a_function(self, function=None, *args):
        if self.start_time is None:
            self.start_time = time.time()

        return function(*args, callback=self)
        self.timer_on_off = True

    def update_progress_timer(self):
        self.elapsed_time = time.time() - self.start_time
        self.update_label.config(text=f"Progress: {format_float(self.current_progress)}% Elapsed Time: {format_seconds(self.elapsed_time)}")
        if self.timer_on_off:
            self.root.after(50, self.update_progress_timer)

    def update_progress(self, current_progress, size):
        self.current_progress = current_progress*100
        self.progress_bar['value'] = self.current_progress
        self.size_label.config(text=f"{format_float(size*(self.current_progress/100))} MB/{format_float(size)} MB")

    def stop_progress_time(self):
        self.timer_on_off = False
        self.root.after(1500, self.root.destroy)
        return f"Elapsed Time: {format_seconds(self.elapsed_time)}"

    
    def update_name(self, text):
        self.label.config(text=text)

    def run(self):
        self.root.mainloop()



class download_popout:
    def __init__(self, title="Progress Bar", text="Downloading"):
        root = tk.Tk()
        root.title("download")
        root.geometry("470x180")

        popup_enabled = tk.BooleanVar(value=True)
        toggle_button = tk.Checkbutton(root, text="Are the files encrypted", variable=popup_enabled)
        toggle_button.pack(padx=20, pady=10)

        # Create a label for the password input
        password_label = tk.Label(root, text="Enter Password:")
        password_label.pack(padx=20, pady=5)

        # Create an entry widget for user input
        popup_message = tk.StringVar()
        message_entry = tk.Entry(root, textvariable=popup_message, show="*")
        message_entry.pack(padx=20, pady=5)

        def open_popup():
            self.is_encryption = popup_enabled.get()
            self.password = popup_message.get()
            root.after(500, root.destroy)

        popup_button = tk.Button(root, text="download", command=open_popup)
        popup_button.pack(padx=20, pady=20)

        # Start the main event loop
        root.mainloop()



###################################################
###################################################




def authenticate():
    """Authenticates and returns the Google Drive API service."""
    credentials = None

    # Load or create credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, ['https://www.googleapis.com/auth/drive'])
            credentials = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)

    # Build and return the Google Drive API service
    return build('drive', 'v3', credentials=credentials)




def upload_file_and_return_id(service, file_path, mime_type, _id, encrypt=True, return_=True, json_data_folder= None, json_file_path=None, __file_path_to_change=None):
    """Uploads a file to Google Drive in the specified folder and returns the file ID."""
    folder_id = _id
    print('----------------> parent-id:',folder_id)
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    # # Create a thread object for the function
    # thread = threading.Thread(target=my_function)

    # # Start the thread
    # thread.start()
    chunksize = 1024 * 1024 # 1mb
    media = MediaFileUpload_modified(file_path, mimetype=mime_type, chunksize=chunksize, resumable=True, encrypt=encrypt)

    # Create a progress indicator callback
    def progress_callback(progress):
        print(f'Upload progress: {round(progress * 100)}%')

    request = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    )

    print(f'Upload progress: 0%')
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress_callback(progress=status.progress())


    print(f'Upload progress: 100%\nFile uploaded successfully!')
    if return_:
        return response['id']
    else:
        print('-------> saving:',file_path, response['id'])
        run_a_function_that_needs_id_or_change_id_or_get_parent_id_using_path(___file_path=__file_path_to_change, json_data=json_data_folder, change_id = response['id'])

# def create_folder(service, folder_name, folder_id):
#     """Creates a new folder in Google Drive."""
#     file_metadata = {
#         'name': folder_name,
#         'mimeType': 'application/vnd.google-apps.folder',
#         'parents': [folder_id]
#     }
#     folder = service.files().create(body=file_metadata, fields='id').execute()
#     return folder

def delete_item(service, item_id):
    """Deletes a folder or file from Google Drive."""
    try:
        service.files().delete(fileId=item_id).execute()
        print('Item deleted successfully!')
    except Exception as e:
        print('An error occurred:', str(e))

def move_item_to_trash(service, item_id):
    """Moves a folder or file to the trash in Google Drive."""
    try:
        service.files().update(fileId=item_id, body={'trashed': True}).execute()
        print('Item moved to trash successfully!')
    except Exception as e:
        print('An error occurred:', str(e))

def list_files_in_directory(service, directory_id):
    """Lists all non-trashed files in the specified directory in Google Drive."""
    try:
        results = service.files().list(q=f"'{directory_id}' in parents", fields="files(id, parents, name, size, modifiedTime, trashed, mimeType)").execute()
        files = results.get('files', [])
        return files
    except Exception as e:
        print('An error occurred:', str(e))
        return []


def download_file(service, file_id, download_directory, callback=None):
    """Downloads a file from Google Drive and saves it locally."""
    try:
        request = service.files().get_media(fileId=file_id)
        file_name = service.files().get(fileId=file_id).execute()['name']
        if callback is not None:
            callback.update_name(file_name)
        
        def _run(callback):
            status_old = None
            with open(os.path.join(download_directory, file_name), 'wb') as file:
                chunksize = 1024 * 1024 #1MB
                downloader = MediaIoBaseDownload(file, request, chunksize=chunksize)

                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    status_ = status.progress()
                    if callback is not None:
                        callback.update_progress(status_, bytes_to_megabytes(downloader._total_size))

                    status_INT = int(status_ * 100)
                    if status_INT != status_old:
                        print(f'Download progress: {status_INT}%')
                        status_old = status_INT
                    
                if (status_INT == 100 ) and (callback is not None):
                    total_time_epl = callback.stop_progress_time()
                    print(total_time_epl)

        if callback is not None:
            _thread = threading.Thread(target=_run, args=(callback,))
            _thread.start()
            callback.update_progress_timer()
            callback.run()
        else:
            _run(None)

        print(f'File downloaded successfully to {download_directory}\\{file_name}')
    except Exception as e:
        print('An error occurred:', str(e))


def create_folder(service, folder_name, parent_folder_id=None):
    """Creates a folder in Google Drive and returns the folder ID."""
    try:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            folder_metadata['parents'] = [parent_folder_id]

        folder = service.files().create(body=folder_metadata, fields='id').execute()
        print('Folder created successfully! Folder ID:', folder['id'])
        return folder['id']
    except Exception as e:
        print('An error occurred:', str(e))
        return None





def get_file_size(file_path):
    """Gets the size of a file in megabytes (MB)."""
    if os.path.isfile(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    else:
        raise FileNotFoundError("File not found.")

def format_seconds(seconds):
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
def bytes_to_megabytes(bytes_value):
    megabytes = bytes_value / (1024 * 1024)
    return megabytes

def kbytes_to_megabytes(bytes_value):
    megabytes = bytes_value / (1024)
    return megabytes

def format_float(number):
    formatted_number = "{:.2f}".format(number)
    return formatted_number

def find_common_substring(strings):
    if not strings:
        return ""

    shortest_string = min(strings, key=len)
    common_substring = ""

    for i, char in enumerate(shortest_string):
        for other_string in strings:
            if other_string[i] != char:
                return common_substring
        common_substring += char

    return common_substring

def get_folder_size(folder_path):
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)

    return total_size

def remove_backslash_at_start(input_string):
    if input_string.startswith('\\'):
        return input_string[1:]  # Return the string without the first character
    else:
        return input_string  # Return the original string

def list_files_and_subdirectories(directory):
    l = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            l.append(os.path.join(root, file))

    return l




####################################################
####################################################
####################################################


try:
    # Authenticate and get the Google Drive API service
    drive_service = authenticate()
except google.auth.exceptions.RefreshError:
    print("Token has expired. Refreshing token...")

    # Load credentials and refresh the token
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, ['https://www.googleapis.com/auth/drive'])
    credentials = flow.run_local_server(port=0)
    
    # Save the refreshed credentials
    with open(token_path, 'wb') as token:
        pickle.dump(credentials, token)
    
    print("Token refreshed. Please run the script again.")
except Exception as e:
    print('An error occurred:', str(e))

####################################################
####################################################
####################################################




def upload_manger(files, encrypt=True):
    total_size = 0
    if len(files) == 1:
        directory_path = files[0]
        if not os.path.isdir(directory_path):
            # directory_path = os.path.dirname(directory_path)
            directory_path = ""
            total_size += os.path.getsize(files[0])
        else:
            total_size += get_folder_size(directory_path)
            files = list_files_and_subdirectories(directory_path)
    else:
        directory_path = sorted(files, key=lambda x: len(x.split('\\')))
        directory_path = os.path.dirname(directory_path[0])
        total_size += sum(os.path.getsize(file_) for file_ in files)


    _total_size = f'{bytes_to_megabytes(total_size):.2f}'
    print(f'total size: {_total_size} MB || Approximated size after encryption: {bytes_to_megabytes(calculate_encrypted_size(total_size)):.2f} MB')
    if directory_path == "":
        mime_type = get_mime_type(files[0])
        __id = upload_file_and_return_id(drive_service, files[0], mime_type, backuper_folder_id, encrypt)

        with open(f'data\\{os.path.basename(files[0])}.json', 'w') as json_file:
            data__ = {"name": os.path.basename(files[0]), "type":"file", "id": __id, "created_time": int(Path(files[0]).stat().st_mtime),'path':files[0].replace('\\'+os.path.basename(files[0]), '')}
            json.dump(data__, json_file, indent=4)

        return {"name": os.path.basename(files[0]), "type":"file", "id": __id, "parent-id":backuper_folder_id}
    else:
        new_folder_tree = generate_folder_tree(directory_path)
        ___parent_name = os.path.basename(os.path.normpath(directory_path))
        json_file_path = f'data\\{___parent_name}.json'

        path_manger_creates_folders(new_folder_tree)
        with open(json_file_path, 'w') as json_file:
            json.dump(new_folder_tree, json_file, indent=4)

        for __file in files:
            mime_type = get_mime_type(__file)
            _file_path = ___parent_name+'\\'+__file.replace(directory_path, '')
            print('-------------------------------------------------------------------------------------------------------------')
            try:
                run_a_function_that_needs_id_or_change_id_or_get_parent_id_using_path(___file_path=_file_path, json_data=new_folder_tree, ___id=None, change_id = False, function=upload_file_and_return_id, get_parent_id=True, service=drive_service, file_path=__file, mime_type=mime_type, encrypt=encrypt, return_=False, json_data_folder=new_folder_tree, json_file_path=str(json_file_path), __file_path_to_change=_file_path)
            except Exception as e:
                print(e)

        with open(json_file_path, 'w') as json_file:
            json.dump(new_folder_tree, json_file, indent=4)

        return {"name": new_folder_tree['name'], "type":new_folder_tree['type'], "id": new_folder_tree['id'], "parent-id":backuper_folder_id}



def path_manger_creates_folders(folder_tree, parent_folder_id=backuper_folder_id):
    if folder_tree['type'] == 'folder':
        __id = create_folder(drive_service, folder_tree['name'], parent_folder_id=parent_folder_id)
        folder_tree['id'] = __id

    for child in folder_tree['children']:
        if child['type'] == 'folder':
            path_manger_creates_folders(child, __id)

def run_a_function_that_needs_id_or_change_id_or_get_parent_id_using_path(___file_path, json_data, ___id=None, change_id = False, function=None, get_parent_id=False, **kwargs):
    # ___file_path is the file path without the base path(or the parent path) (example: c:\user\pc\FolderToUpload\test.txt --> ___file_path is FolderToUpload\test.txt)
    ___file_path = remove_backslash_at_start(___file_path)
    __path = ___file_path.split('\\')
    __name = __path.pop(0)
    if json_data['name'] == __name:
        if json_data['type'] == "folder":
            for file__data in json_data['children']:
                __id = json_data['id']
                run_a_function_that_needs_id_or_change_id_or_get_parent_id_using_path(___file_path='\\'.join(__path), json_data=file__data, ___id=__id, change_id = change_id, function=function, get_parent_id=get_parent_id, **kwargs)
        
        if len(__path) == 0:
            if not get_parent_id:
                ___id = json_data['id']
                json_data['id'] = change_id

            if change_id:
                json_data['id'] = change_id

            if function != None:
                function(_id=___id, **kwargs)


class search_by_id:
    def __init__(self, _id_):
        self.id= _id_
        self.directory_path = 'data'
        self.d = {'file_name':None,'data':None}
        file_list = []
        
        # Iterate through all files and directories in the specified directory
        for filename in os.listdir(self.directory_path):
            file_path = os.path.join(self.directory_path, filename)
            if os.path.isfile(file_path):
                file_list.append(filename)

        self.file_list = file_list

        self.s()

        return self.d
    
    
    def s(self):
        for _file in  self.file_list:
            r = load_json_file(self.directory_path+'/'+_file)
            children = r['children'].copy()
            __break = False
            if r['id'] == self.id:
                self.d['file_name'] = _file
                self.d['data'] = x
            else:
                for x in children:
                    if x['id'] == self.id:
                        self.d['file_name'] = _file
                        self.d['data'] = x
                        __break = True
                    if x['type'] == "folder":
                        children += x['children']
                if __break:
                    break

    def resulat(self):
        print(self.d)
# _data_ = search_by_id(self.id)

            


class Download_manger:
    def __init__(self, service, _id_, _parent_id_, _type_, _name_, _path_):
        self.id = _id_
        self.parent_id = _parent_id_
        self.type = _type_
        self.service = service
        self.name = _name_
        self.path = _path_
        dp = download_popout()
        self.encryption = dp.is_encryption
        self.password = dp.password
        self.lists_files = []


    def start(self):
        self.path___ = self.path+'\\'+self.name
        if 'file' in self.type:
            popout_ = popout('Downloading', "...")
            popout_.run_a_function(download_file, self.service, self.id, self.path)

            with open(f'data\\{self.name}.json', 'w') as json_file:
                data__ = {"name": self.name, "type":"file", "id": self.id, "created_time": int(time.time() * 1000),'path':self.path}
                json.dump(data__, json_file, indent=4)
            
            self.decrypt_file(self.path___)

        elif 'folder' in self.type:
            self.list_files_and_folders(self.service, self.id, self.path___, indent="")
            self.create_folders()
            self.download_files()
            file_tree = generate_folder_tree(self.path___, save=True)
            self.set_files_ids(file_tree)
            save_json_file(self.path___, self.set_files_ids(file_tree))

        else:
            print(self.type,'doesn\'t exist')

    def decrypt_file(self, path___):
        if self.encryption:
            try:
                f = open(path___, 'br')
                br = f.read()
                f.close()
                data_conten = decrypt_data(br, self.password)
                os.remove(path___)
                f = open(path___, 'bw')
                f.write(data_conten)
                f.close()
            except:
                print('=======>  WRONG PASSWORD!  <=======\n####################################################\n####################################################')
                messagebox.showwarning("Warning", "WRONG PASSWORD!")

    def download_files(self):
        for _file in self.lists_files:
            if _file['type'] == "file":
                __path_ = _file['path']+'\\'+_file['name']
                print('=====>', __path_)
                if Path(__path_).exists():
                    Path(__path_).unlink()
                download_file(self.service, _file['id'], _file['path'])
                self.decrypt_file(__path_)

    def list_files_and_folders(self, service, directory_id, path, indent=""):
        """Recursively lists all files and folders in the specified directory."""
        try:
            query = f"'{directory_id}' in parents"
            results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
            items = results.get('files', [])
            
            for item in items:
                item_name = item['name']
                item_id = item['id']
                item_mimeType = item['mimeType']
                
                if item_mimeType == 'application/vnd.google-apps.folder':
                    print(f"{indent}Folder: {item_name} (ID: {item_id})")
                    path_ = path+'\\'+item_name
                    self.lists_files.append({'name': item_name,'type': "folder", 'id':item_id, 'path':path_})
                    self.list_files_and_folders(service, item_id, path_, indent + "  ")
                else:
                    print(f"{indent}File: {item_name} (ID: {item_id})")
                    self.lists_files.append({'name': item_name,'type': "file", 'id':item_id, 'path':path})
                    
        except Exception as e:
            print('An error occurred:', str(e))

    def create_folders(self):
        for _file in self.lists_files:
            if _file['type'] == "folder" and not Path(_file['path']).exists():
                os.makedirs(_file['path'])

    def set_files_ids(self, tree):
        for _file in self.lists_files:
            if _file['type'] == 'folder':
                _file_path = _file['path'].replace(self.path,'')
            else:
                _file_path = _file['path'].replace(self.path,'')+"\\"+_file['name']
            _file_path = _file_path.split('\\')

            file_tree_ = tree
            while True:
                if len(_file_path) > 0:
                    item = _file_path.pop(0)
                    for child in file_tree_['children']:
                        if item == child['name']:
                            file_tree_ = child
                elif len(_file_path) == 0:
                    file_tree_['id'] = _file['id']
                    print('setting id:', _file['id'], _file['path']+'\\'+_file['name'])
                    break
        
        tree['id'] = self.id
        return tree


class delete_manger:
    def __init__(self, service, _id, _name):
        self.id = _id
        self.name = _name
        self.service = service
        move_item_to_trash(self.service, self.id)
        os.remove("data\\"+self.name+".json")

class refresh:
    def __init__(self):
        self.files = []
        self.data = {'files':[]}
        self.new_items = []
        self.deleted_items = []
        self.directory_path = BASE_DIR / 'data'

    def get_the_json_files(self):
        self.json_files = [BASE_DIR / 'data' / f.name for f in self.directory_path.iterdir() if f.is_file()]

    def compare(self):
        self.get_the_json_files()
        self.data = {'files':[]}
        d = {}

        for file_ in self.json_files:
            self.new_items = []
            self.modified_items = []
            self.deleted_items = []
            old_folder_tree = load_json_file(file_)
            path_of_the_uploaded_item = Path(old_folder_tree["path"]) / old_folder_tree["name"]
            d = {'file_path':str(path_of_the_uploaded_item),'type': old_folder_tree['type'],'new_items':[],'deleted_items':[],'modified_items':[]}
            if path_of_the_uploaded_item.exists():
                if old_folder_tree['type'] == 'folder':
                    new_folder_tree = generate_folder_tree(str(path_of_the_uploaded_item), False) 
                    self.compare_function(old_folder_tree, new_folder_tree)
                    d['new_items'] = self.new_items
                    d['deleted_items'] = self.deleted_items
                    d['modified_items'] = self.modified_items
                elif old_folder_tree['created_time'] != int(path_of_the_uploaded_item.stat().st_mtime):
                    d['modified_items'].append({'path':str(path_of_the_uploaded_item),'id':old_folder_tree['id']})
            else:
                d['deleted_items'].append({'path':str(path_of_the_uploaded_item),'id':old_folder_tree['id']})
                
            if d['new_items'] != [] or d['deleted_items'] != []:
                self.data['files'].append(d)


    def compare_function(self, old_tree, new_tree):
        if new_tree['name'] == old_tree['name']:
            new_items, removed_items, unchanged_old_tree, unchanged_new_tree = self.compare_children(old_tree['children'], new_tree['children'])

            for item in new_items:
                self.new_items.append({'path':str(Path(item["path"]) / item["name"]),'id':None})

            for item in removed_items:
                self.deleted_items.append({'path':str(Path(item["path"]) / item["name"]),'id':item['id']})

            for item1, item2 in zip(unchanged_old_tree, unchanged_new_tree):
                if item1['type'] == 'folder':
                    self.compare_function(item1, item2)
                elif item1['type'] == 'file' and item1['created_time'] != item2['created_time']:
                    self.modified_items.append({'path':str(Path(item1["path"]) / item1["name"]),'id':item1['id']})

        else:
            self.new_items.append({'path':str(Path(new_folder_tree["path"]) / new_folder_tree["name"]),'id':new_folder_tree['id']})
            self.deleted_items.append({'path':str(Path(old_folder_tree["path"]) / old_folder_tree["name"]),'id':new_folder_tree['id']})
        # new_items, deleted_items = compare_folder_trees(old_folder_tree, new_folder_tree)
        # print(new_items, deleted_items)
    
    def compare_children(self, old_tree, new_tree):
        dict1 = {item["name"]: item for item in old_tree}
        dict2 = {item["name"]: item for item in new_tree}

        new_items = [dict2[id_] for id_ in dict2 if id_ not in dict1]
        removed_items = [dict1[id_] for id_ in dict1 if id_ not in dict2]
        unchanged_items_old_tree = [dict1[id_] for id_ in dict1 if id_ in dict2]
        unchanged_items_new_tree = [dict2[id_] for id_ in dict2 if id_ in dict1]

        return new_items, removed_items, unchanged_items_old_tree, unchanged_items_new_tree

    def upload(self):
        for json_file in self.data['files']:
            for file_ in json_file['new_items']:
                print(file_)

    def delete(self):
        pass


refresh_manger = refresh()
            





###########################################################
######  localhost  #######
###########################################################
import http.server
import socketserver

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        if self.path == '/List_Of_Uploaded_Folders':
            # List all files in the specified directory
            files_in_directory = list_files_in_directory(drive_service, backuper_folder_id)

            self.wfile.write(json.dumps(files_in_directory, indent=2).encode('utf-8'))
        elif self.path.find('folder-id') != -1:
            _id = self.path.split('/')[-1]
            files_in_directory = list_files_in_directory(drive_service, _id)

            _return_folder = []
            if _id != backuper_folder_id:
                _return_folder = [{"mimeType": "folder","size": None,"id": "None","parents": [_id],"name": "/..","trashed": False,"modifiedTime": ""}]
            self.wfile.write(json.dumps(_return_folder+files_in_directory, indent=2).encode('utf-8'))
        elif 'refresh_upload' in self.path:
            refresh_manger.upload()
        elif 'refresh' in self.path:
            refresh_manger.compare()
            self.wfile.write(json.dumps(refresh_manger.data, indent=2).encode('utf-8'))
        elif 'delete' in self.path:
            _id_ = self.path.split('/')[-1]
            _name_ = unquote(self.path.split('/')[-2])
            print(self.path, _name_)
            delete_manger(drive_service, _id_, _name_)
            self.wfile.write(b"done")

        elif 'refresh_folder' in self.path:
            
            self.wfile.write(b"done")

        elif self.path == '/close':
            self.wfile.write(b"done")
            exit()

    def do_POST(self):
        print('======================================================================================================================\n----------------------------------------------------------------------------------------------------------------------\n======================================================================================================================')

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself
        self.send_response(200)

        if 'download' in self.path:
            _id_ = self.path.split('/')[-2]
            _parent_id_ = self.path.split('/')[-1]
            _type_ = self.path.split('/')[-3]
            _name_ = unquote(self.path.split('/')[-4])
            _path_ = post_data
            
            dm = Download_manger(drive_service, _id_, _parent_id_, _type_, _name_, _path_)
            dm.start()
        else:
            # filename = self.headers['filename']
            data = upload_manger(json.loads(post_data), 'encrypt' in self.path)
            self.send_header("name", data['name'])
            self.send_header("type", data['type'])
            self.send_header("id", data['id'])
            self.send_header("parent-id", data['parent-id'])

        self.send_header("Content-type", "text/plain")
        self.end_headers()
        print('======================================================================================================================\n----------------------------------------------------------------------------------------------------------------------\n======================================================================================================================')



def run_server():
    PORT = 4269  # You can change this port to any available port you prefer

    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Server is running on http://127.0.0.1:{PORT}")
        httpd.serve_forever()


##########################################################
##########################################################



if __name__ == "__main__":
    run_server()