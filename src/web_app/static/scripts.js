const uploadContainer = document.getElementById('upload-container');
const fileInput = document.getElementById('file');
const uploadForm = document.getElementById('upload-form');
const messageDiv = document.getElementById('message');
const imagePreviewContainer = document.querySelector('.image-preview-container');
const imagePreview = document.getElementById('image-preview');
const cropButton = document.getElementById('crop-button');
const FinishCropButton = document.getElementById('finish-crop-button');
const processButton = document.getElementById('process-button');
const clearButton = document.getElementById('clear-button');
const resultInput = document.getElementById('result-input');
let uploadedFileName = '';
let cropper;

uploadContainer.addEventListener('click', () => fileInput.click());

uploadContainer.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadContainer.classList.add('dragover');
});

uploadContainer.addEventListener('dragleave', () => {
    uploadContainer.classList.remove('dragover');
});

uploadContainer.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadContainer.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        handleFileUpload(fileInput.files[0]);
    }
});

function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageDiv.textContent = data.message;
            imagePreview.src = data.file_url + '?t=' + new Date().getTime();;
            imagePreview.style.display = 'block';
            cropButton.style.display = 'inline-block';
            processButton.style.display = 'inline-block';
            clearButton.style.display = 'inline-block';
            uploadedFileName = data.filename;
        } else {
            messageDiv.textContent = data.message;
        }
    })
    .catch(error => {
        messageDiv.style.color = 'red';
        messageDiv.textContent = 'An error occurred while uploading the file.';
        console.error('Error:', error);
    });
}

function initializeCropper() {
    if (cropper) {
        cropper.destroy();
    }
    cropper = new Cropper(imagePreview, {
        dragMode: 'move',
        autoCropArea: 0.65,
        restore: false,
        guides: true,
        center: false,
        highlight: false,
        cropBoxMovable: true,
        cropBoxResizable: true,
        toggleDragModeOnDblclick: false,
    });
}

cropButton.addEventListener('click', () => {
    initializeCropper();
    cropButton.style.display = 'none';
    FinishCropButton.style.display = 'inline-block';
});

FinishCropButton.addEventListener('click', () => {
    const canvas = cropper.getCroppedCanvas();
    canvas.toBlob((blob) => {
        const formData = new FormData();
        formData.append('croppedImage', blob, uploadedFileName);

        fetch(`/upload_cropped/${uploadedFileName}`, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageDiv.textContent = data.message;
                imagePreview.src = data.file_url + '?t=' + new Date().getTime();
                imagePreview.style.display = 'block';
                FinishCropButton.style.display = 'none';
                cropButton.style.display = 'inline-block';
                processButton.style.display = 'inline-block';
                cropper.destroy();
            } else {
                messageDiv.style.color = 'red';
                messageDiv.textContent = data.message;
            }
        })
        .catch(error => {
            messageDiv.style.color = 'red';
            messageDiv.textContent = 'An error occurred while uploading the cropped image.';
            console.error('Error:', error);
        });
    });
});

processButton.addEventListener('click', () => {
    fetch(`/process/${uploadedFileName}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageDiv.textContent = data.message;
            resultInput.value = data.result;
            resultInput.style.display = 'block';
        } else {
            messageDiv.style.color = 'red';
            messageDiv.textContent = data.message;
        }
    })
    .catch(error => {
        messageDiv.textContent = 'An error occurred while processing the file.';
        console.error('Error:', error);
    });
});

clearButton.addEventListener('click', () => {
    location.reload();
});