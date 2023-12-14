from pathlib import Path
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = Path('')
DESKTOP_PATH = Path.home() / 'Desktop'

from data.encrypt_files_packge import *



def showfolders():
    print('choice date:\n')
    for x in range(len(files)):
        print('  [{}] {}: {}'.format(x + 1, files[x]['date'], files[x]['files']))
    chosendate = files[inputgetint('\nenter date number: ', range(1, len(files) + 1)) - 1]
    return chosendate

def showfiles():
    print('choice files:\n')
    files = chosendate['files']
    for x in range(len(files)):
        print('  [{}]: {}'.format(x + 1, files[x]))
    xs = inputgetmultipleint('\nenter files numbers (enter \'-1\' to select all // exp: 1 6 3): ', range(-1, len(files) + 1))
    chosenfiles = []
    if xs[0] == -1:
        chosenfiles = files
    else:
        for x in xs:
            chosenfiles.append(files[x - 1])

    return chosenfiles

if __name__ == "__main__":
    main_dirs = [DESKTOP_PATH / 'files to encrypt', BASE_DIR / 'encrypted files', DESKTOP_PATH / 'decrypted files', BASE_DIR / 'data']

    for DIR in main_dirs:
        if not DIR.is_dir():
            DIR.mkdir(mode=511, parents=False, exist_ok=False)

    password = input('enter password: ')
    cipher = cipher(password)

    print('encrypt or decrypt')
    command = input('enter command: ')
    if command == 'encrypt':
        cipher.encrypt()
    elif command == 'decrypt':
        files = cipher.get_files()
        if len(files) != 0:
            chosendate = showfolders()

            chosenfiles = showfiles()
            cipher.decrypt(chosenfiles, chosendate['date'])
        else:
            print('No files are encrypted with that password!')
    else:
        print('\n  "{}" is an invalide command!'.format(command))

    input('\npress enter to exit')
