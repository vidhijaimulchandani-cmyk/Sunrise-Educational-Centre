// Admission Form JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('admissionForm');
    const steps = document.querySelectorAll('.form-step');
    const progressSteps = document.querySelectorAll('.progress-step');
    const nextBtn = document.getElementById('nextBtn');
    const prevBtn = document.getElementById('prevBtn');
    const submitBtn = document.getElementById('submitBtn');
    const successModal = document.getElementById('successModal');
    
    let currentStep = 1;
    const totalSteps = steps.length;
    
    // Initialize form
    initializeForm();
    
    function initializeForm() {
        // Set up event listeners
        nextBtn.addEventListener('click', nextStep);
        prevBtn.addEventListener('click', previousStep);
        form.addEventListener('submit', handleSubmit);
        
        // Program card selection
        const programCards = document.querySelectorAll('.program-card');
        programCards.forEach(card => {
            card.addEventListener('click', function() {
                const radio = this.querySelector('input[type="radio"]');
                radio.checked = true;
                updateProgramSelection();
            });
        });
        
        // Form validation on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearFieldError);
        });
        
        // URL parameter handling
        const urlParams = new URLSearchParams(window.location.search);
        const selectedClass = urlParams.get('class');
        if (selectedClass) {
            preSelectProgram(selectedClass);
        }
    }
    
    function nextStep() {
        if (validateCurrentStep()) {
            if (currentStep < totalSteps) {
                currentStep++;
                updateStepDisplay();
                updateProgressBar();
                updateNavigationButtons();
            }
        }
    }
    
    function previousStep() {
        if (currentStep > 1) {
            currentStep--;
            updateStepDisplay();
            updateProgressBar();
            updateNavigationButtons();
        }
    }
    
    function updateStepDisplay() {
        steps.forEach((step, index) => {
            if (index + 1 === currentStep) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }
    
    function updateProgressBar() {
        progressSteps.forEach((step, index) => {
            const stepNumber = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNumber === currentStep) {
                step.classList.add('active');
            } else if (stepNumber < currentStep) {
                step.classList.add('completed');
            }
        });
    }
    
    function updateNavigationButtons() {
        // Show/hide previous button
        if (currentStep === 1) {
            prevBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'inline-flex';
        }
        
        // Show/hide next and submit buttons
        if (currentStep === totalSteps) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-flex';
        } else {
            nextBtn.style.display = 'inline-flex';
            submitBtn.style.display = 'none';
        }
        
        // Update button text
        if (currentStep === totalSteps - 1) {
            nextBtn.textContent = 'Review & Submit';
        } else {
            nextBtn.textContent = 'Next';
        }
    }
    
    function validateCurrentStep() {
        const currentStepElement = document.querySelector(`[data-step="${currentStep}"]`);
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        // Special validation for step 3 (program selection)
        if (currentStep === 3) {
            const selectedProgram = form.querySelector('input[name="selectedProgram"]:checked');
            if (!selectedProgram) {
                showError('Please select a program to continue.');
                isValid = false;
            }
            
            const preferredSubjects = form.querySelectorAll('input[name="preferredSubjects"]:checked');
            if (preferredSubjects.length === 0) {
                showError('Please select at least one preferred subject.');
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name || field.id;
        
        // Clear previous error
        clearFieldError(field);
        
        // Required field validation
        if (field.hasAttribute('required') && !value) {
            showFieldError(field, `${getFieldLabel(field)} is required.`);
            return false;
        }
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showFieldError(field, 'Please enter a valid email address.');
                return false;
            }
        }
        
        // Phone validation
        if (field.type === 'tel' && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                showFieldError(field, 'Please enter a valid phone number.');
                return false;
            }
        }
        
        // Percentage validation
        if (field.name === 'previousPercentage' || field.name === 'targetPercentage') {
            if (value && (value < 0 || value > 100)) {
                showFieldError(field, 'Percentage must be between 0 and 100.');
                return false;
            }
        }
        
        return true;
    }
    
    function showFieldError(field, message) {
        field.style.borderColor = 'var(--error-color)';
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.color = 'var(--error-color)';
        errorDiv.style.fontSize = '12px';
        errorDiv.style.marginTop = '4px';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearFieldError(field) {
        field.style.borderColor = '';
        const errorDiv = field.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    function getFieldLabel(field) {
        const label = field.parentNode.querySelector('label');
        return label ? label.textContent.replace(' *', '') : field.name || field.id;
    }
    
    function showError(message) {
        // Create temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.style.background = 'var(--error-color)';
        errorDiv.style.color = 'white';
        errorDiv.style.padding = '12px 16px';
        errorDiv.style.borderRadius = '8px';
        errorDiv.style.marginBottom = '20px';
        errorDiv.style.textAlign = 'center';
        errorDiv.textContent = message;
        
        const currentStepElement = document.querySelector(`[data-step="${currentStep}"]`);
        const stepHeader = currentStepElement.querySelector('.step-header');
        stepHeader.parentNode.insertBefore(errorDiv, stepHeader.nextSibling);
        
        // Remove error after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    function updateProgramSelection() {
        const programCards = document.querySelectorAll('.program-card');
        programCards.forEach(card => {
            const radio = card.querySelector('input[type="radio"]');
            if (radio.checked) {
                card.style.borderColor = 'var(--primary-color)';
                card.style.transform = 'translateY(-4px)';
                card.style.boxShadow = 'var(--shadow-light)';
            } else {
                card.style.borderColor = '';
                card.style.transform = '';
                card.style.boxShadow = '';
            }
        });
    }
    
    function preSelectProgram(programType) {
        let programValue = '';
        switch (programType) {
            case '9-10':
                programValue = 'class9-10';
                break;
            case '11-12':
                programValue = 'class11-12';
                break;
            case 'crash':
                programValue = 'crash';
                break;
        }
        
        if (programValue) {
            const radio = document.querySelector(`input[value="${programValue}"]`);
            if (radio) {
                radio.checked = true;
                updateProgramSelection();
            }
        }
    }
    
    function handleSubmit(e) {
        e.preventDefault();
        
        if (!validateCurrentStep()) {
            return;
        }
        
        // Check terms acceptance
        const termsAccepted = document.getElementById('termsAccepted').checked;
        if (!termsAccepted) {
            showError('Please accept the Terms and Conditions to continue.');
            return;
        }
        
        // Prepare form data
        const formData = new FormData(form);
        const applicationData = {};
        
        for (let [key, value] of formData.entries()) {
            if (key === 'preferredSubjects') {
                if (!applicationData[key]) {
                    applicationData[key] = [];
                }
                applicationData[key].push(value);
            } else {
                applicationData[key] = value;
            }
        }
        
        // Show loading state
        submitBtn.textContent = 'Submitting...';
        submitBtn.disabled = true;
        
        // Simulate form submission (replace with actual API call)
        setTimeout(() => {
            showSuccessModal(applicationData);
            submitBtn.textContent = 'Submit Application';
            submitBtn.disabled = false;
        }, 2000);
    }
    
    function showSuccessModal(data) {
        // Populate application summary
        const summaryDiv = document.getElementById('applicationSummary');
        summaryDiv.innerHTML = `
            <div class="review-item">
                <span class="review-label">Name:</span>
                <span>${data.firstName} ${data.lastName}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Email:</span>
                <span>${data.email}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Phone:</span>
                <span>${data.phone}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Class:</span>
                <span>Class ${data.currentClass}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Program:</span>
                <span>${getProgramName(data.selectedProgram)}</span>
            </div>
        `;
        
        // Show modal
        successModal.classList.add('active');
        
        // Close modal on background click
        successModal.addEventListener('click', function(e) {
            if (e.target === successModal) {
                successModal.classList.remove('active');
            }
        });
    }
    
    function getProgramName(programValue) {
        const programs = {
            'class9-10': 'Class 9 & 10',
            'class11-12': 'Class 11 & 12',
            'crash': 'Crash Course'
        };
        return programs[programValue] || programValue;
    }
    
    // Update review section when reaching step 4
    function updateReviewSection() {
        if (currentStep === 4) {
            updatePersonalReview();
            updateAcademicReview();
            updateProgramReview();
        }
    }
    
    function updatePersonalReview() {
        const personalReview = document.getElementById('personalReview');
        const firstName = document.getElementById('firstName').value;
        const lastName = document.getElementById('lastName').value;
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;
        const dateOfBirth = document.getElementById('dateOfBirth').value;
        const gender = document.getElementById('gender').value;
        const address = document.getElementById('address').value;
        const city = document.getElementById('city').value;
        const state = document.getElementById('state').value;
        const pincode = document.getElementById('pincode').value;
        
        personalReview.innerHTML = `
            <div class="review-item">
                <span class="review-label">Name:</span>
                <span>${firstName} ${lastName}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Email:</span>
                <span>${email}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Phone:</span>
                <span>${phone}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Date of Birth:</span>
                <span>${dateOfBirth}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Gender:</span>
                <span>${gender}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Address:</span>
                <span>${address}, ${city}, ${state} - ${pincode}</span>
            </div>
        `;
    }
    
    function updateAcademicReview() {
        const academicReview = document.getElementById('academicReview');
        const currentClass = document.getElementById('currentClass').value;
        const board = document.getElementById('board').value;
        const schoolName = document.getElementById('schoolName').value;
        const previousPercentage = document.getElementById('previousPercentage').value;
        const targetPercentage = document.getElementById('targetPercentage').value;
        const weakSubjects = document.getElementById('weakSubjects').value;
        const academicGoals = document.getElementById('academicGoals').value;
        
        academicReview.innerHTML = `
            <div class="review-item">
                <span class="review-label">Current Class:</span>
                <span>Class ${currentClass}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Board:</span>
                <span>${board.toUpperCase()}</span>
            </div>
            <div class="review-item">
                <span class="review-label">School:</span>
                <span>${schoolName}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Previous Percentage:</span>
                <span>${previousPercentage || 'Not provided'}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Target Percentage:</span>
                <span>${targetPercentage}%</span>
            </div>
            <div class="review-item">
                <span class="review-label">Weak Subjects:</span>
                <span>${weakSubjects || 'Not specified'}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Academic Goals:</span>
                <span>${academicGoals || 'Not specified'}</span>
            </div>
        `;
    }
    
    function updateProgramReview() {
        const programReview = document.getElementById('programReview');
        const selectedProgram = document.querySelector('input[name="selectedProgram"]:checked');
        const preferredSubjects = document.querySelectorAll('input[name="preferredSubjects"]:checked');
        
        const programName = selectedProgram ? getProgramName(selectedProgram.value) : 'Not selected';
        const subjects = Array.from(preferredSubjects).map(subject => {
            const label = subject.parentNode.textContent.trim();
            return label;
        }).join(', ');
        
        programReview.innerHTML = `
            <div class="review-item">
                <span class="review-label">Selected Program:</span>
                <span>${programName}</span>
            </div>
            <div class="review-item">
                <span class="review-label">Preferred Subjects:</span>
                <span>${subjects || 'Not selected'}</span>
            </div>
        `;
    }
    
    // Enhanced step navigation with review updates
    const originalNextStep = nextStep;
    nextStep = function() {
        if (originalNextStep()) {
            updateReviewSection();
        }
    };
    
    // Add smooth scrolling to form sections
    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
    
    // Enhanced navigation with smooth scrolling
    const originalUpdateStepDisplay = updateStepDisplay;
    updateStepDisplay = function() {
        originalUpdateStepDisplay();
        scrollToTop();
    };
    
    // Add form auto-save functionality
    function autoSaveForm() {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        localStorage.setItem('admissionFormData', JSON.stringify(data));
    }
    
    function loadSavedForm() {
        const savedData = localStorage.getItem('admissionFormData');
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    if (field.type === 'checkbox' || field.type === 'radio') {
                        field.checked = data[key] === 'on' || data[key] === 'true';
                    } else {
                        field.value = data[key];
                    }
                }
            });
        }
    }
    
    // Auto-save on input change
    form.addEventListener('input', autoSaveForm);
    
    // Load saved data on page load
    loadSavedForm();
    
    // Clear saved data on successful submission
    const originalHandleSubmit = handleSubmit;
    handleSubmit = function(e) {
        originalHandleSubmit(e);
        localStorage.removeItem('admissionFormData');
    };
});