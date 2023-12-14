import os
import pickle
import google.auth
import google.auth.transport.requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the path to the credentials JSON file
credentials_path = 'credentials.json'

# Define the path to the token pickle file
token_path = 'token.pickle'

# Define the path to the file you want to upload
file_path = 'file.txt'

# Define the MIME type of the file
import mimetypes

def get_mime_type(file_path):
    """Gets the MIME type of a file."""
    return mimetypes.guess_type(file_path)[0]

mime_type = get_mime_type(file_path)
print("MIME type:", mime_type)
mime_type = mime_type  # Modify based on the file type

# Define the ID of the folder you want to upload to
folder_id = '1Zy49FyeHMMF9IZFHIovO9rMl7sbDfkDE'

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

def upload_file(service, file_path, mime_type, folder_id):
    """Uploads a file to Google Drive in the specified folder."""

    try:
        file_size = get_file_size(file_path)
        print(f"uploading \"{file_path}\" size is: {file_size:.2f} MB")
    except FileNotFoundError as e:
        print(str(e))

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type)
    service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()


def get_file_size(file_path):
    """Gets the size of a file in megabytes (MB)."""
    if os.path.isfile(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    else:
        raise FileNotFoundError("File not found.")


try:
    # Authenticate and get the Google Drive API service
    drive_service = authenticate()

    # Upload the file to the specified folder
    upload_file(drive_service, file_path, mime_type, folder_id)

    print(f'"{file_path}" uploaded successfully!')
except Exception as e:
    print('An error occurred:', str(e))

