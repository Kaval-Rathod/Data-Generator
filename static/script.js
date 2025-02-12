document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const files = document.getElementById('files').files;
    const format = document.getElementById('format').value;
    
    if (files.length === 0) {
        alert('Please select files to process');
        return;
    }
    
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
        
    } catch (error) {
        logMessage(`Error: ${error.message}`, 'error');
    }
});

function logMessage(message, type = 'info') {
    const log = document.getElementById('processLog');
    const timestamp = new Date().toLocaleTimeString();
    const msgElement = document.createElement('div');
    msgElement.className = type === 'error' ? 'text-danger' : 'text-dark';
    msgElement.textContent = `${timestamp} - ${message}`;
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
                <a href="/download/${result.converted}" class="btn btn-sm btn-primary btn-download">Download</a>
            `;
        } else {
            item.innerHTML = `
                <div>
                    <strong>${result.original}</strong>
                    <small class="text-danger d-block">Error: ${result.error}</small>
                </div>
            `;
        }
        
        container.appendChild(item);
    });
} 