
// Authentication functionality

function showForm(formType) {
  // Hide all forms
  document.querySelectorAll('.auth-form').forEach(form => {
    form.classList.remove('active');
  });
  
  // Remove active class from all tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Show selected form
  document.getElementById(formType + '-form').classList.add('active');
  
  // Add active class to selected tab
  event.target.classList.add('active');
}

function handleLogin(event) {
  event.preventDefault();
  
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const remember = document.getElementById('remember').checked;
  
  // Simple validation
  if (!email || !password) {
    showMessage('Please fill in all fields', 'error');
    return;
  }
  
  // Store user data in localStorage (for demo purposes)
  const userData = {
    email: email,
    loginTime: new Date().toISOString(),
    remember: remember
  };
  
  localStorage.setItem('currentUser', JSON.stringify(userData));
  
  showMessage('Login successful! Redirecting...', 'success');
  
  // Redirect to main page after 2 seconds
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 2000);
}

function handleSignup(event) {
  event.preventDefault();
  
  const name = document.getElementById('signup-name').value;
  const email = document.getElementById('signup-email').value;
  const phone = document.getElementById('signup-phone').value;
  const className = document.getElementById('signup-class').value;
  const password = document.getElementById('signup-password').value;
  const confirmPassword = document.getElementById('signup-confirm').value;
  const termsAccepted = document.getElementById('terms').checked;
  
  // Validation
  if (!name || !email || !phone || !className || !password || !confirmPassword) {
    showMessage('Please fill in all fields', 'error');
    return;
  }
  
  if (password !== confirmPassword) {
    showMessage('Passwords do not match', 'error');
    return;
  }
  
  if (password.length < 6) {
    showMessage('Password must be at least 6 characters long', 'error');
    return;
  }
  
  if (!termsAccepted) {
    showMessage('Please accept the terms and conditions', 'error');
    return;
  }
  
  // Store user data
  const userData = {
    name: name,
    email: email,
    phone: phone,
    class: className,
    registrationDate: new Date().toISOString()
  };
  
  // Store in localStorage (for demo purposes)
  localStorage.setItem('registeredUser', JSON.stringify(userData));
  localStorage.setItem('currentUser', JSON.stringify(userData));
  
  showMessage('Account created successfully! Welcome to Sunrise Education Centre!', 'success');
  
  // Redirect to main page after 3 seconds
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 3000);
}

function showForgotPassword() {
  const email = prompt('Please enter your email address:');
  if (email) {
    showMessage('Password reset link has been sent to your email', 'success');
  }
}

function showMessage(message, type) {
  // Remove existing messages
  const existingMessage = document.querySelector('.message');
  if (existingMessage) {
    existingMessage.remove();
  }
  
  // Create new message
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  messageDiv.textContent = message;
  
  // Insert at the top of the active form
  const activeForm = document.querySelector('.auth-form.active');
  const article = activeForm.querySelector('article');
  article.insertBefore(messageDiv, article.firstChild);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (messageDiv.parentNode) {
      messageDiv.remove();
    }
  }, 5000);
}

// Check if user is already logged in
document.addEventListener('DOMContentLoaded', function() {
  const currentUser = localStorage.getItem('currentUser');
  if (currentUser) {
    const userData = JSON.parse(currentUser);
    showMessage(`Welcome back, ${userData.name || userData.email}!`, 'success');
  }
});
