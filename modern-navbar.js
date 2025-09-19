// Modern Navbar JavaScript
function navigateTo(url) {
    // Add loading animation
    const button = event.target.closest('.button');
    if (button) {
        button.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            window.location.href = url;
        }, 150);
    }
}

function openSearch() {
    // Create search modal or use existing search functionality
    const searchTerm = prompt("🔍 Enter your search term:");
    if (searchTerm && searchTerm.trim()) {
        // You can customize this based on your search implementation
        // For now, we'll show an alert, but you can redirect to a search page
        alert(`Searching for: "${searchTerm}"\n\nThis would typically redirect to a search results page or filter current content.`);
        
        // Example: Redirect to search results
        // window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
        
        // Example: Filter current page content
        // filterPageContent(searchTerm);
    }
}

// Set active button based on current page
function setActiveNavButton() {
    const currentPath = window.location.pathname;
    const buttons = document.querySelectorAll('.modern-navbar .button');
    
    if (buttons.length === 0) return; // No navbar present
    
    // Remove active class from all buttons
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Add active class based on current page
    if (currentPath === '/' || currentPath === '/index' || currentPath === '/home') {
        buttons[0].classList.add('active'); // Home
    } else if (currentPath.includes('/profile') || currentPath.includes('/user')) {
        buttons[2].classList.add('active'); // Profile
    } else if (currentPath.includes('/study-resources') || currentPath.includes('/resources')) {
        buttons[3].classList.add('active'); // Resources
    } else if (currentPath.includes('/forum')) {
        buttons[4].classList.add('active'); // Forum
    } else if (currentPath.includes('/online-class') || currentPath.includes('/live-class')) {
        // Find the live classes button (might be at different index depending on page)
        const liveClassBtn = Array.from(buttons).find(btn => 
            btn.getAttribute('data-tooltip') === 'Live Classes'
        );
        if (liveClassBtn) {
            liveClassBtn.classList.add('active');
        }
    }
}

// Initialize navbar functionality
document.addEventListener('DOMContentLoaded', function() {
    setActiveNavButton();
    
    // Add smooth animations to buttons
    const buttons = document.querySelectorAll('.modern-navbar .button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Handle page visibility changes to update active states
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        setActiveNavButton();
    }
});

// Export functions for global use
window.navigateTo = navigateTo;
window.openSearch = openSearch;
window.setActiveNavButton = setActiveNavButton;