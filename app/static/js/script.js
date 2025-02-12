// Theme Switching
const themeToggle = document.getElementById('themeToggle');
const lightIcon = document.getElementById('lightIcon');
const darkIcon = document.getElementById('darkIcon');

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);
    
    if (theme === 'dark') {
        lightIcon.classList.add('d-none');
        darkIcon.classList.remove('d-none');
    } else {
        lightIcon.classList.remove('d-none');
        darkIcon.classList.add('d-none');
    }
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
setTheme(savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    setTheme(currentTheme === 'dark' ? 'light' : 'dark');
});

// File input handling with improved UX
const uploadArea = document.querySelector('.upload-area');
const fileInput = document.getElementById('files');
const fileList = document.getElementById('fileList');

uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('border-primary');
});
uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('border-primary');
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('border-primary');
    fileInput.files = e.dataTransfer.files;
    updateFileList(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => updateFileList(e.target.files));

function updateFileList(files) {
    if (files.length > 0) {
        fileList.innerHTML = Array.from(files)
            .map(file => `
                <div class="text-primary">
                    <i class="bi bi-file-earmark-text me-2"></i>${file.name}
                </div>
            `).join('');
    } else {
        fileList.innerHTML = '<i class="bi bi-info-circle me-1"></i>No files selected';
    }
}

// Form submission
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const files = document.getElementById('files').files;
    const format = document.getElementById('format').value;
    
    if (files.length === 0) {
        showToast('Please select files to process', 'warning');
        return;
    }
    
    showLoading(true);
    
    // Upload files
    const formData = new FormData();
    for (let file of files) {
        formData.append('file', file);
    }
    
    try {
        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const uploadResult = await uploadResponse.json();
        
        if (uploadResult.error) {
            throw new Error(uploadResult.error);
        }
        
        logMessage('Files uploaded successfully. Starting processing...');
        
        // Process files
        const processResponse = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                files: uploadResult.files,
                format: format
            })
        });
        
        const processResult = await processResponse.json();
        
        if (processResult.error) {
            throw new Error(processResult.error);
        }
        
        logMessage('Processing complete!');
        updateConvertedFiles(processResult.results);
        showToast('Files processed successfully!', 'success');
        
    } catch (error) {
        logMessage(`Error: ${error.message}`, 'error');
        showToast(error.message, 'error');
    } finally {
        showLoading(false);
    }
});

function logMessage(message, type = 'info') {
    const log = document.getElementById('processLog');
    const timestamp = new Date().toLocaleTimeString();
    const msgElement = document.createElement('div');
    msgElement.className = type === 'error' ? 'text-danger' : 'text-dark';
    msgElement.innerHTML = `
        <span class="text-muted">${timestamp}</span> - 
        <span class="${type === 'error' ? 'text-danger' : ''}">${message}</span>
    `;
    log.appendChild(msgElement);
    log.scrollTop = log.scrollHeight;
}

function updateConvertedFiles(results) {
    const container = document.getElementById('convertedFiles');
    
    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'list-group-item';
        
        if (result.status === 'success') {
            item.innerHTML = `
                <div>
                    <strong>${result.converted}</strong>
                    <small class="text-muted d-block">From: ${result.original}</small>
                </div>
                <a href="/download/${result.converted}" 
                   class="btn btn-sm btn-primary btn-download">
                    <i class="bi bi-download"></i> Download
                </a>
            `;
        } else {
            item.innerHTML = `
                <div>
                    <strong>${result.original}</strong>
                    <small class="text-danger d-block">
                        <i class="bi bi-exclamation-triangle"></i> Error: ${result.error}
                    </small>
                </div>
            `;
        }
        
        container.appendChild(item);
    });
}

function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
    }
}

function clearLog() {
    const log = document.getElementById('processLog');
    log.innerHTML = '';
}

function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast show`;
    toast.innerHTML = `
        <div class="toast-header">
            <i class="bi bi-${type === 'error' ? 'exclamation-circle text-danger' : 
                           type === 'warning' ? 'exclamation-triangle text-warning' : 
                           'check-circle text-success'} me-2"></i>
            <strong class="me-auto">Notification</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
} 