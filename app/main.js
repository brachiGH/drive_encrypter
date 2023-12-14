const {
    app,
    BrowserWindow,
    ipcMain,
    dialog
} = require('electron');
const path = require('path');
const fs = require('fs');
const print = console.log;
let Item_selected_context_menu = {
    'itemId': null,
    'parents_id': null,
    'type': null
}

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true, // Enable Node.js integration
            contextIsolation: false,
        }
    })

    win.loadFile('index.html')
}

app.whenReady().then(() => {
    createWindow()

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow()
        }
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
        fetch('http://127.0.0.1:4269/close')
    }
})


var encryption_status = true
// Handle the encryption
ipcMain.on('encryption-status', (event, status) => {
    console.log('encryption status:', status);
    encryption_status = status
});

// Handle the selected FOLDER
ipcMain.on('selected-items', (event, sentData) => {
    print('Selected Items:', sentData);

    if (sentData['selectedItems'].length != 0) {
        send_files(sentData['selectedItems'], sentData['path'])
    }
});

// Handle the selected Item
ipcMain.on('Item-selected-context-menu', (event, selectedItems) => {
    print('Selected Items:', selectedItems);

    Item_selected_context_menu = selectedItems
});

// Handle the selected Item
ipcMain.on('context-menu-download', (event, selectedItems) => {
    o = createFolder()

    const Item = { ...Item_selected_context_menu };

    const mainWindow = BrowserWindow.getAllWindows()[0];
    mainWindow.webContents.send('download-Handler', {
        'itemId': Item['itemId']
    });

    

    if (o != false) {
        fetch('http://127.0.0.1:4269/download/' + Item['name'] + '/' + Item['type'] + '/' + Item['itemId'] + '/' + Item['parents_id'], {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/html'
                },
                body: o
            }).then(() => {
                print(Item['itemId'])
                mainWindow.webContents.send('download-done-Handler', Item['itemId']);
            })
            .catch(error => {
                console.error('Error posting data:', error);
            });
    }
});

// Handle the selected Item
ipcMain.on('context-menu-delete', (event, selectedItems) => {
    const Item = { ...Item_selected_context_menu };

    fetch('http://127.0.0.1:4269/delete/' + Item['name'] + '/' + Item['itemId'])
    .then(() => {
        const mainWindow = BrowserWindow.getAllWindows()[0];
        mainWindow.webContents.send('done-deleting', Item['itemId']);
    })
});

async function send_files(files_data, path_) {
    const item = {
        "mimeType": "uploading",
        "size": 0,
        "id": "None",
        "parents": "None",
        "name": path_,
        "trashed": false,
        "modifiedTime": ""
    }

    const mainWindow = BrowserWindow.getAllWindows()[0];
    mainWindow.webContents.send('send_files-Handler-uploading', {
        'item': item
    });


    fetch(`http://127.0.0.1:4269/${encryption_status? 'encrypt' : 'pass'}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(files_data)
        }).then((response) => {
            id = response.headers.get('id')
            if (id != null || id != "None") {
                _name = response.headers.get('name')
                type = response.headers.get('type')
                parent_id = response.headers.get('parent-id')
                data = {'name': _name, 'type': type, 'id': id, 'parent-id': parent_id}
                mainWindow.webContents.send('send_files-Handler-done-uploading', data);
            }
        })
        .catch(error => {
            console.error('Error posting data:', error);
        });
}


// Example function to create a folder
function createFolder() {
    // Show a dialog to select the parent directory for the new folder
    const parentDir = dialog.showOpenDialogSync({
        title: 'Select Parent Directory',
        properties: ['openDirectory']
    });

    if (parentDir && parentDir.length > 0) {
        // const newFolderPath = path.join(parentDir[0], Default_folder_name);
        // return newFolderPath

        return parentDir[0]
    } else {
        return false
    }
}