const {
    ipcRenderer
} = require('electron');
const print = console.log

const selectedItemsDiv = document.getElementById('selectedItems');
const folderInput = document.getElementById('folderInput');
const fileInput = document.getElementById('fileInput');
const dropArea = document.getElementById('dropArea');

folderInput.addEventListener('change', (event) => {
    const selectedItems = Array.from(event.target.files).map(item => item.path);

    draw_file_names(selectedItems)
    ipcRenderer.send('selected-items', {'selectedItems':selectedItems, 'path':removeLastPartAfterBackslash(selectedItems[0])});
});

fileInput.addEventListener('change', (event) => {
    const selectedFiles = Array.from(event.target.files).map(item => item.path);

    draw_file_names(selectedFiles)
    ipcRenderer.send('selected-items', {'selectedItems':selectedFiles, 'path':removeLastPartAfterBackslash(selectedFiles[0])});
});

dropArea.addEventListener('dragover', (event) => {
    event.preventDefault();
    dropArea.style.border = '2px dashed #aaa';
});

dropArea.addEventListener('dragleave', () => {
    dropArea.style.border = '2px dashed #ccc';
});

dropArea.addEventListener('drop', (event) => {
    event.preventDefault();
    dropArea.style.border = '2px dashed #ccc';

    const selectedItems = Array.from(event.dataTransfer.files).map(item => item.path);

    draw_file_names(selectedItems)
    ipcRenderer.send('selected-items', {'selectedItems':selectedItems, 'path':removeLastPartAfterBackslash(selectedItems[0])});
});


function draw_file_names(selectedItems) {
    selectedItemsDiv.innerHTML = '';
    selectedItems.forEach((item) => {
        selectedItemsDiv.innerHTML += `<p>${item}</p>`;
    });
}


const toggle = document.getElementById("encryptionToggle");
const statusText = document.getElementById("toggleLabel");
toggle.addEventListener("change", function() {
  if (toggle.checked) {
    statusText.innerText = "Files encrypted";
    ipcRenderer.send('encryption-status', true);
  } else {
    statusText.innerText = "Not encrypted";
    ipcRenderer.send('encryption-status', false);
  }
});


const downloadButton = document.getElementById('download-button');
const deleteButton = document.getElementById('delete-button');
let contextMenuVisible = false; // Track whether the context menu is visible

// Button actions
downloadButton.addEventListener('click', (e) => {
    // Add your download logic here
    hideContextMenu();

    ipcRenderer.send('context-menu-download', null);
    ipcRenderer.send('Item-selected-context-menu', {'itemId':null,'parents_id':null,'type':null,'name':null});
});

deleteButton.addEventListener('click', (e) => {
    // Add your delete logic here
    hideContextMenu();

    ipcRenderer.send('context-menu-delete', null);
    ipcRenderer.send('Item-selected-context-menu', {'itemId':null,'parents_id':null,'type':null,'name':null});
});



// Function to show context menu at a specific position
function showContextMenu(x, y) {
    const contextMenu = document.getElementById('context-menu');

    contextMenu.style.left = x + 'px';
    contextMenu.style.top = y + 'px';
    contextMenu.classList.remove('hidden');
    contextMenuVisible = true;
}

// Function to hide context menu
function hideContextMenu() {
const contextMenu = document.getElementById('context-menu');
    contextMenu.classList.add('hidden');
    contextMenuVisible = false;
}


// Hide context menu on click anywhere
document.addEventListener('click', (e) => {
    if (contextMenuVisible) {
        hideContextMenu();
    }
});

function removeLastPartAfterBackslash(inputString) {
    const lastBackslashIndex = inputString.lastIndexOf('\\');
    
    if (lastBackslashIndex !== -1) {
        const result = inputString.substring(0, lastBackslashIndex);
        return result;
    } else {
        return inputString;
    }
}


///////////////////////////////////////////////////////////////////////////
//  auto-sync
///////////////////////////////////////////////////////////////////////////

// Get references to the button and status elements
const toggleButton = document.getElementById('toggleButton');
const statusElement = document.getElementById('status');

let isToggled = false;

// Add a click event listener to the button
toggleButton.addEventListener('click', () => {
    // Toggle the state
    isToggled = !isToggled;

    // Update the status text and button appearance
    if (isToggled) {
        statusElement.textContent = 'Status: On';
        toggleButton.classList.add('active');
    } else {
        statusElement.textContent = 'Status: Off';
        toggleButton.classList.remove('active');
    }
});

function refresh(isToggled_ = false) {
    fetch('http://127.0.0.1:4269/refresh')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        print(JSON.parse(data))
        document.querySelector('#refresh-data').innerText = data
        if (isToggled || isToggled_) {
            upload_the_refreshed_data()
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function upload_the_refreshed_data() {
    fetch('http://127.0.0.1:4269/refresh_upload')
    .then(data => {
        print(JSON.parse(data))
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// refresh();

// // Set up the interval to call the function every 5 minutes
// const interval = setInterval(refresh, 300000);

document.querySelector('#refreshButton').addEventListener('click', ()=> {
    refresh(true)
})