// Bulk Study Resources Upload JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Excel Upload Functionality
    const excelUploadArea = document.getElementById('excel-upload-area');
    const excelInput = document.getElementById('excel-input');
    const filePreview = document.getElementById('file-preview');
    const previewInfo = document.getElementById('preview-info');
    const previewTbody = document.getElementById('preview-tbody');
    const confirmUploadBtn = document.getElementById('confirm-upload-btn');
    const cancelUploadBtn = document.getElementById('cancel-upload-btn');
    const downloadTemplateBtn = document.getElementById('download-template-btn');
    
    let excelFilePath = null;
    let previewData = [];

    // Drag and drop functionality for Excel file
    excelUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        excelUploadArea.classList.add('dragover');
    });

    excelUploadArea.addEventListener('dragleave', () => {
        excelUploadArea.classList.remove('dragover');
    });

    excelUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        excelUploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        const excelFile = files.find(file => 
            file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
            file.type === 'application/vnd.ms-excel'
        );
        if (excelFile) {
            handleExcelFile(excelFile);
        } else {
            showError('Please upload an Excel file (.xlsx or .xls)');
        }
    });

    excelUploadArea.addEventListener('click', () => {
        excelInput.click();
    });

    excelInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleExcelFile(file);
        }
    });

    function handleExcelFile(file) {
        const formData = new FormData();
        formData.append('excel_file', file);

        // Show loading state
        showProgress('Validating Excel file...', 2000);

        fetch('/bulk-upload/upload-excel', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideProgress();
            
            if (data.success) {
                excelFilePath = data.excel_path;
                previewData = data.preview_data;
                displayFilePreview(data);
                showSuccess(data.message);
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            hideProgress();
            showError('Error uploading file: ' + error.message);
        });
    }

    function displayFilePreview(data) {
        if (data.preview_data && data.preview_data.length > 0) {
            filePreview.style.display = 'block';
            
            // Display preview info
            previewInfo.innerHTML = `
                <div class="preview-summary">
                    <p><strong>Total files to upload:</strong> ${data.total_files}</p>
                    <p><strong>Preview showing:</strong> First ${data.preview_data.length} files</p>
                    <p><strong>Columns found:</strong> ${data.columns.join(', ')}</p>
                </div>
            `;
            
            // Display preview table
            previewTbody.innerHTML = '';
            
            data.preview_data.forEach((file, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${file['File Name'] || '-'}</td>
                    <td>${file['Title'] || '-'}</td>
                    <td>${file['Class'] || '-'}</td>
                    <td>${file['Category'] || '-'}</td>
                    <td>${file['Description'] || '-'}</td>
                    <td><span class="status-pending">Pending</span></td>
                `;
                previewTbody.appendChild(row);
            });
        }
    }

    // Download template functionality
    downloadTemplateBtn.addEventListener('click', () => {
        downloadTemplateBtn.disabled = true;
        downloadTemplateBtn.textContent = 'Downloading...';
        
        fetch('/bulk-upload/download-template')
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Download failed');
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'study_resources_template.xlsx';
            a.click();
            window.URL.revokeObjectURL(url);
            showSuccess('Template downloaded successfully!');
        })
        .catch(error => {
            showError('Download failed: ' + error.message);
        })
        .finally(() => {
            downloadTemplateBtn.disabled = false;
            downloadTemplateBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7,10 12,15 17,10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download Study Resources Template
            `;
        });
    });

    // Confirm upload functionality
    confirmUploadBtn.addEventListener('click', () => {
        if (!excelFilePath) {
            showError('No Excel file to process');
            return;
        }

        // Show confirmation dialog
        if (!confirm(`Are you sure you want to upload ${previewData.length} study resources? This action cannot be undone.`)) {
            return;
        }

        confirmUploadBtn.disabled = true;
        confirmUploadBtn.textContent = 'Processing...';

        // Send confirmation request
        fetch('/bulk-upload/confirm-upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                excel_path: excelFilePath,
                uploaded_by: 'admin'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showProgress('Uploading study resources...', 3000);
                
                // Simulate progress updates
                let progress = 0;
                const interval = setInterval(() => {
                    progress += 10;
                    updateProgress(progress, `Uploading... ${progress}%`);
                    
                    if (progress >= 100) {
                        clearInterval(interval);
                        hideProgress();
                        showUploadResults(data.results);
                    }
                }, 300);
                
            } else {
                showError(data.error);
            }
        })
        .catch(error => {
            showError('Upload failed: ' + error.message);
        })
        .finally(() => {
            confirmUploadBtn.disabled = false;
            confirmUploadBtn.textContent = '✅ Confirm & Upload';
        });
    });

    // Cancel upload functionality
    cancelUploadBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to cancel? All uploaded data will be lost.')) {
            filePreview.style.display = 'none';
            excelInput.value = '';
            excelFilePath = null;
            previewData = [];
            hideProgress();
            hideResults();
        }
    });

    function showUploadResults(results) {
        uploadResults.style.display = 'block';
        
        let resultsHTML = `
            <div class="results-summary">
                <h5>Upload Summary</h5>
                <p><strong>Total files processed:</strong> ${results.total_files}</p>
                <p><strong>Successfully uploaded:</strong> ${results.successful_uploads}</p>
                <p><strong>Failed uploads:</strong> ${results.failed_uploads}</p>
            </div>
        `;
        
        // Show successful uploads
        if (results.success && results.success.length > 0) {
            resultsHTML += '<h6>✅ Successful Uploads:</h6>';
            results.success.forEach(success => {
                resultsHTML += `<div class="success-item">${success}</div>`;
            });
        }
        
        // Show errors
        if (results.errors && results.errors.length > 0) {
            resultsHTML += '<h6>❌ Errors:</h6>';
            results.errors.forEach(error => {
                resultsHTML += `<div class="error-item">${error}</div>`;
            });
        }
        
        resultsContent.innerHTML = resultsHTML;
    }

    // Progress and Results Functions
    const uploadProgress = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const progressDetails = document.getElementById('progress-details');
    const uploadResults = document.getElementById('upload-results');
    const resultsContent = document.getElementById('results-content');
    const closeResultsBtn = document.getElementById('close-results-btn');

    function showProgress(message, duration = 3000) {
        uploadProgress.style.display = 'block';
        progressDetails.textContent = message;
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += 2;
            progressFill.style.width = progress + '%';
            progressText.textContent = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    hideProgress();
                }, 500);
            }
        }, duration / 50);
    }

    function updateProgress(progress, message) {
        progressFill.style.width = progress + '%';
        progressText.textContent = Math.round(progress) + '%';
        progressDetails.textContent = message;
    }

    function hideProgress() {
        uploadProgress.style.display = 'none';
        progressFill.style.width = '0%';
        progressText.textContent = '0%';
    }

    function showResults(message, type = 'success') {
        uploadResults.style.display = 'block';
        
        const icon = type === 'success' ? '✅' : '❌';
        const className = type === 'success' ? 'success-item' : 'error-item';
        
        resultsContent.innerHTML = `
            <div class="${className}">
                <span>${icon}</span>
                <span>${message}</span>
            </div>
        `;
    }

    function hideResults() {
        uploadResults.style.display = 'none';
    }

    function showError(message) {
        showResults(message, 'error');
    }

    function showSuccess(message) {
        showResults(message, 'success');
    }

    closeResultsBtn.addEventListener('click', () => {
        uploadResults.style.display = 'none';
    });

    // Add fade-in animation to elements
    function addFadeInAnimation(element) {
        element.classList.add('fade-in');
    }

    // Initialize animations
    document.addEventListener('DOMContentLoaded', () => {
        const elements = document.querySelectorAll('.bulk-upload-container > *');
        elements.forEach((element, index) => {
            setTimeout(() => {
                addFadeInAnimation(element);
            }, index * 100);
        });
    });
}); 