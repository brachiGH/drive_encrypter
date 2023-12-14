const {
    ipcRenderer
} = require('electron');
const print = console.log;
const ChangeIcon = new CustomEvent('ChangeIcon');
var folder_list = []
var uploading_files_list = []
var type_of_item_being_donwloaded = "file"

window.addEventListener('DOMContentLoaded', () => {
    fetch_data("List_Of_Uploaded_Folders")
})




function fetch_data(url) {
    fetch('http://127.0.0.1:4269/' + url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            Uploaded_Folders_maker(JSON.parse(data))
        })
        .catch(error => {
            console.error('Error:', error);
        });

}

function Uploaded_Folders_maker(jsonData) {
    const LOUF = document.getElementById("LOUF")
    LOUF.innerHTML = ""

    jsonData.forEach(item => {
        add_folder_or_file(item)
    });

    folder_list.push(jsonData[0]["parents"][0])
    }

function add_folder_or_file(item, insert_on_top=false) {
    const LOUF = document.getElementById("LOUF")
    const listItem = document.createElement('li');
    const icon = Get_Icon(item.mimeType);
    const trashIcon = item.trashed ? '🗑️' : '';
    listItem.innerHTML = `
            <div class="icon">${icon}</div>
            <div style="flex: 1;">${item.name}</div>
            <div class="trash-icon">${trashIcon}</div>
        `;
    listItem.setAttribute('data-id', item.id);
    listItem.setAttribute('parents-id', item.parents[0]);
    listItem.setAttribute('type', item.mimeType.includes('folder') ? 'folder' : 'file');
    listItem.setAttribute('name', item.name);

    listItem.addEventListener('click', function () {
        const itemId = this.getAttribute('data-id');
        const parents_id = this.getAttribute('parents-id');
        // const type = this.getAttribute('type');
        console.log('Clicked item ID:', itemId, '\nparents-id:', parents_id);

        if (item.mimeType.includes('folder')) {
            if (itemId != "None" ) {
                fetch_data("folder-id/" + parents_id + "/" + itemId)
            } else if (folder_list.length > 1) {
                folder_list.pop() // remove the id of the current folder
                fetch_data("folder-id/" + folder_list.pop()) // get last folder id
            } else {
                print('pass')
            }
        }
    });

    listItem.addEventListener('ChangeIcon', function (event) {
        this.querySelector('.icon').innerText = Get_Icon(this.getAttribute('type'))
    });

    // Show context menu on right-click
    listItem.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showContextMenu(e.clientX, e.clientY);

        elem = get_parent_elem(e.target)
        const itemId = elem.getAttribute('data-id');
        const parents_id = elem.getAttribute('parents-id');
        const type = elem.getAttribute('type');
        const name = elem.getAttribute('name');
        ipcRenderer.send('Item-selected-context-menu', {
            'itemId': itemId,
            'parents_id': parents_id,
            'type': type,
            'name': name
        });
    });

    if(insert_on_top) {
        LOUF.insertBefore(listItem, LOUF.firstChild);
        uploading_files_list.push(listItem)
    }else {
    LOUF.appendChild(listItem);}
}

function Get_Icon(mimeType) {
    switch (true) {
        case mimeType.includes('folder'):
            return '📁';
        case mimeType.includes('uploading'):
            return '🔼';
        case mimeType.includes('downloading'):
            return '🔽';
        case mimeType.includes('refreashing'):
            return '🔄';
        default:
            return '📄';
    }
}


function get_parent_elem(target) {
    if (target.hasAttribute('parents-id')) {
        return target
    } else {
        return get_parent_elem(target.parentElement)
    }
}


ipcRenderer.on('download-Handler', (event, data) => {
    elem = document.querySelector(`[data-id="${data['itemId']}"]`)
    type_of_item_being_donwloaded = elem.getAttribute('type')
    elem.setAttribute('type', 'downloading')
    elem.dispatchEvent(ChangeIcon);
})


ipcRenderer.on('download-done-Handler', (event, id) => {
    print(id)
    elem = document.querySelector(`[data-id="${id}"]`)
    elem.setAttribute('type', type_of_item_being_donwloaded)
    elem.dispatchEvent(ChangeIcon);
})


ipcRenderer.on('send_files-Handler-uploading', (event, data) => {
    add_folder_or_file(data['item'], true)
})

ipcRenderer.on('send_files-Handler-done-uploading', (event, data) => {
    elem = uploading_files_list.shift()
    elem.querySelector('[style="flex: 1;"]').innerText = data['name']
    elem.setAttribute('type', data['type'])
    elem.setAttribute('data-id', data['id'])
    elem.setAttribute('parents-id', data['parent-id'])
    elem.querySelector('.icon').innerText = Get_Icon(data['type'])
})

ipcRenderer.on('done-deleting', (event, id) => {
    print(id)
    elem = document.querySelector(`[data-id="${id}"]`)
    elem.innerHTML += '<div class="trash-icon">🗑️</div>'
})