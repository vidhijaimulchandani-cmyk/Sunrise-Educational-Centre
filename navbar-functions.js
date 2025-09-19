// Navbar Functions - Standardized for all pages

// Hamburger menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function() {
            this.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });

    // Profile dropdown functionality
    const profileLink = document.getElementById('profileLink');
    const profileDropdown = document.getElementById('profileDropdown');
    
    if (profileLink && profileDropdown) {
        profileLink.addEventListener('click', function(e) {
            e.preventDefault();
            profileDropdown.style.display = profileDropdown.style.display === 'block' ? 'none' : 'block';
        });
    }

    // Admin dropdown functionality
    const adminLink = document.getElementById('adminLink');
    const adminDropdown = document.getElementById('adminDropdown');
    
    if (adminLink && adminDropdown) {
        adminLink.addEventListener('click', function(e) {
            e.preventDefault();
            adminDropdown.style.display = adminDropdown.style.display === 'block' ? 'none' : 'block';
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (profileDropdown && !profileLink.contains(event.target) && !profileDropdown.contains(event.target)) {
            profileDropdown.style.display = 'none';
        }
        if (adminDropdown && !adminLink.contains(event.target) && !adminDropdown.contains(event.target)) {
            adminDropdown.style.display = 'none';
        }
    });

    // Initialize notification functionality
    initializeNotifications();
    
    // Initialize theme toggle
    initializeThemeToggle();
    
    // Initialize search functionality
    initializeSearch();
});

// Notification Functions
function initializeNotifications() {
    const notifBell = document.getElementById('notifBell');
    const notificationPanel = document.getElementById('notification-panel');
    
    if (notifBell && notificationPanel) {
        notifBell.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleNotifications();
        });
    }
    
    // Load notifications count
    loadNotificationCount();
}

function toggleNotifications() {
    const panel = document.getElementById('notification-panel');
    if (panel) {
        if (panel.style.display === 'none' || panel.style.display === '') {
            panel.style.display = 'block';
            panel.style.animation = 'slideIn 0.3s ease-out';
            loadNotifications();
        } else {
            panel.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => {
                panel.style.display = 'none';
            }, 300);
        }
    }
}

function loadNotificationCount() {
    // Simulate loading notification count
    const badge = document.getElementById('notificationCount');
    if (badge) {
        // You can replace this with actual API call
        const count = 3; // Example count
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'flex';
        }
    }
}

function loadNotifications() {
    // This function can be extended to load real notifications from your backend
    console.log('Loading notifications...');
}

// Theme Toggle Functions
function initializeThemeToggle() {
    const themeToggle = document.getElementById('darkModeToggle');
    
    if (themeToggle) {
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggle.textContent = '☀️';
        }
        
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            
            // Update button icon
            this.textContent = isDark ? '☀️' : '🌙';
            
            // Save theme preference
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }
}

// Search Functions
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            performSearch(this.value);
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch(this.value);
            }
        });
    }
}

function openSearch() {
    const modal = document.getElementById('searchModal');
    if (modal) {
        modal.style.display = 'block';
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }
}

function closeSearch() {
    const modal = document.getElementById('searchModal');
    if (modal) {
        modal.style.display = 'none';
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        const results = document.getElementById('searchResults');
        if (results) {
            results.innerHTML = '';
        }
    }
}

function performSearch(query) {
    const resultsContainer = document.getElementById('searchResults');
    if (!resultsContainer || !query.trim()) {
        if (resultsContainer) resultsContainer.innerHTML = '';
        return;
    }
    
    // Simulate search results - replace with actual search API
    const mockResults = [
        { title: 'Mathematics Class 10', type: 'Course', url: '/study-resources?class=10&subject=math' },
        { title: 'JEE Preparation', type: 'Course', url: '/study-resources?category=jee' },
        { title: 'Live Classes', type: 'Feature', url: '/online-class' },
        { title: 'Admission Process', type: 'Info', url: '/admission' },
        { title: 'Student Forum', type: 'Community', url: '/forum' }
    ];
    
    const filteredResults = mockResults.filter(result => 
        result.title.toLowerCase().includes(query.toLowerCase())
    );
    
    if (filteredResults.length === 0) {
        resultsContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: rgba(255,255,255,0.7);">No results found</div>';
        return;
    }
    
    resultsContainer.innerHTML = filteredResults.map(result => `
        <div class="search-result-item" style="padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); cursor: pointer; transition: background 0.3s ease;" onclick="window.location.href='${result.url}'">
            <div style="color: white; font-weight: 600; margin-bottom: 5px;">${result.title}</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">${result.type}</div>
        </div>
    `).join('');
    
    // Add hover effects
    document.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(255,255,255,0.1)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.background = 'transparent';
        });
    });
}

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    const searchModal = document.getElementById('searchModal');
    const notificationPanel = document.getElementById('notification-panel');
    
    if (searchModal && event.target === searchModal) {
        closeSearch();
    }
    
    if (notificationPanel && !notificationPanel.contains(event.target) && !document.getElementById('notifBell').contains(event.target)) {
        notificationPanel.style.display = 'none';
    }
});

// Add CSS animations
const navbarStyles = document.createElement('style');
navbarStyles.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    .search-result-item:hover {
        background: rgba(255,255,255,0.1) !important;
    }
    
    .notification-item:hover {
        background: rgba(255,255,255,0.05);
        transform: translateX(5px);
    }
`;
document.head.appendChild(navbarStyles);