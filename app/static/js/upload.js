document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.querySelector('.drop-section');
    const listSection = document.querySelector('.list-section');
    const listContainer = document.querySelector('.list');
    const fileSelector = document.querySelector('.file-selector');
    const fileSelectorInput = document.querySelector('.file-selector-input');
    const message = document.querySelector('.validation-message');
    const Upload = document.querySelector('#upload');

    fileSelector.onclick = () => fileSelectorInput.click();
    fileSelectorInput.onchange = () => handleFiles(fileSelectorInput.files);
    //Upload.onclick = () => submitFile();

    // Drag-and-drop events
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('drag-over-effect');
    });
    dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag-over-effect'));
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('drag-over-effect');
        fileSelectorInput.files = e.dataTransfer.files;
        handleFiles(fileSelectorInput.files);
    });

    function handleFiles(files) {
        [...files].forEach((file) => {
            if (typeValidation(file.type)) {
                console.log("file:", file);
                uploadFile(file);
            } else {
                showMessage("Invalid file type.");
            }
        });
    }

    function typeValidation(type) {
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];
        return allowedTypes.includes(type);
    }

    function showMessage(text) {
        message.innerText = text;
        setTimeout(() => {
            message.innerText = "";
        }, 3000);
    }


    let totalFiles = 0;
    let completedFiles = 0;

    function uploadFile(file) {
        listSection.style.display = 'block';
        totalFiles += 1;
    
        // Create list item for displaying the file
        let li = document.createElement('li');
        li.classList.add('file-item');
        li.innerHTML = `
            <div class="col">
                <div class="file-name">
                    <span class="name">${file.name}</span>
                </div>
                <div class="file-progress">
                    <span></span>
                </div>
            </div>
        `;
        listContainer.prepend(li);
        Upload.innerText = "Submit";
    }
    
});