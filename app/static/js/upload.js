document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.querySelector('.drop-section');
    const listSection = document.querySelector('.list-section');
    const listContainer = document.querySelector('.list');
    const fileSelector = document.querySelector('.file-selector');
    const fileSelectorInput = document.querySelector('.file-selector-input');
    const message = document.querySelector('.validation-message');
    const uploadButton = document.querySelector('#upload');

    fileSelector.onclick = () => fileSelectorInput.click();
    fileSelectorInput.onchange = () => handleFiles(fileSelectorInput.files);

    // Drag-and-drop events
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.classList.add('drag-over-effect');
    });
    
    dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag-over-effect'));
    
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.classList.remove('drag-over-effect');
        
        // Only take the first file if multiple files are dropped
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileSelectorInput.files = new DataTransfer().files;
            handleFiles([files[0]]);
        }
    });

    function handleFiles(files) {
        // Clear existing files
        listContainer.innerHTML = '';
        uploadButton.disabled = true;
        
        // Only process the first file
        if (files.length > 0) {
            const file = files[0];
            if (typeValidation(file.type)) {
                uploadFile(file);
                uploadButton.disabled = false;
            } else {
                showMessage("Invalid file type. Please upload a PDF file.");
            }
        }
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

    function uploadFile(file) {
        listSection.style.display = 'block';
    
        // Create list item for displaying the file
        let li = document.createElement('li');
        li.classList.add('file-item');
        li.innerHTML = `
            <div class="col">
                <div class="file-name">
                    <span class="name">${file.name}</span>
                    <button type="button" class="delete-btn">
                        <span class="material-symbols-outlined">delete</span>
                    </button>
                </div>
            </div>
        `;

        // Add delete functionality
        const deleteBtn = li.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', () => {
            li.remove();
            fileSelectorInput.value = ''; // Clear the file input
            listSection.style.display = 'none';
            uploadButton.disabled = true;
            showMessage("File removed");
        });

        listContainer.innerHTML = ''; // Clear any existing files
        listContainer.appendChild(li);
        uploadButton.innerText = "Submit";
    }
});