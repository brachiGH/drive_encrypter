import subprocess
import platform


def is_windows():
    """Checks if the user is on a Windows operating system."""
    return platform.system().lower() == 'windows'


    

class compress:
    def __init__(self, folder_path=None, archive_path=None, password="none"):
        self.folder_path = folder_path
        self.archive_path = archive_path
        self.password = password


    def compress_and_encrypt_folder(self):
        """Compresses and encrypts a folder using 7za command-line tool with password and encrypted file names."""
        if is_windows():
            command = ['C:\\Program Files\\7-Zip\\7zG.exe', 'a', '-t7z', self.archive_path, self.folder_path, '-p{}'.format(self.password), '-mhe=on']
        else:
            command = ['7za', 'a', '-t7z', self.archive_path, self.folder_path, '-p{}'.format(self.password), '-mhe=on']
        
        subprocess.run(command)
        print("Folder compressed and encrypted successfully!")
    
# Example usage
folder_path = 'messenger-screenshots'      # Replace with the path to the folder you want to compress and encrypt
archive_path = 'archive.7z' # Replace with the desired path and filename for the compressed and encrypted archive
password = 'your-password'          # Replace with the desired password for encryption

# compress_and_encrypt_folder(folder_path, archive_path, password)
