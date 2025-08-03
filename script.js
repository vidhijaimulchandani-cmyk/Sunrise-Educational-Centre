function joinLiveClass() {
  // Navigate to the dedicated online class page
  window.location.href = 'online-class.html';
}

// Typing animation for the main heading
document.addEventListener('DOMContentLoaded', function() {
  const headingElement = document.getElementById('typing-hero');
  
  // Only run typing animation if the element exists
  if (headingElement) {
    const text = "Expert Coaching for Class 9 to 12";
    let index = 0;
    
    headingElement.classList.add('typing-active');
    
    function typeText() {
      if (index < text.length) {
        headingElement.textContent += text.charAt(index);
        index++;
        setTimeout(typeText, 100); // Adjust speed here (100ms per character)
      } else {
        // Remove typing cursor after completion
        setTimeout(() => {
          headingElement.style.borderRight = 'none';
          setTimeout(() => {
            headingElement.textContent = '';
            headingElement.style.borderRight = '';
            index = 0;
            setTimeout(typeText, 500); // Pause before restarting
          }, 1500); // Pause after finishing
        }, 1000);
      }
    }
    
    // Start typing after a small delay
    setTimeout(typeText, 500);
  }
});

// Section reveal on scroll
const revealElements = document.querySelectorAll('.animated-card');
const revealOnScroll = () => {
  const triggerBottom = window.innerHeight * 0.9;
  revealElements.forEach(el => {
    const boxTop = el.getBoundingClientRect().top;
    if (boxTop < triggerBottom) {
      el.style.animationPlayState = 'running';
    }
  });
};
window.addEventListener('scroll', revealOnScroll);
window.addEventListener('DOMContentLoaded', revealOnScroll);

// Button ripple effect
const buttons = document.querySelectorAll('.btn');
buttons.forEach(btn => {
  btn.addEventListener('click', function(e) {
    const circle = document.createElement('span');
    circle.classList.add('ripple');
    const rect = btn.getBoundingClientRect();
    circle.style.left = `${e.clientX - rect.left}px`;
    circle.style.top = `${e.clientY - rect.top}px`;
    btn.appendChild(circle);
    setTimeout(() => circle.remove(), 600);
  });
});

// Ripple CSS (inject if not present)
if (!document.getElementById('ripple-style')) {
  const style = document.createElement('style');
  style.id = 'ripple-style';
  style.textContent = `.ripple { position: absolute; border-radius: 50%; transform: scale(0); animation: ripple 0.6s linear; background: rgba(255,255,255,0.5); pointer-events: none; width: 100px; height: 100px; left: 0; top: 0; z-index: 10; } @keyframes ripple { to { transform: scale(2.5); opacity: 0; } } .btn { position: relative; overflow: hidden; }`;
  document.head.appendChild(style);
}

document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.querySelector(".hamburger");
    const navLinks = document.querySelector(".nav-links");

    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("active");
            navLinks.classList.toggle("active");
        });
    }
});

// Unified Dark Mode Implementation
function setupDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

// Initialize dark mode on page load
document.addEventListener('DOMContentLoaded', function() {
    setupDarkMode();
    
    // Setup dark mode toggle button if it exists
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
});