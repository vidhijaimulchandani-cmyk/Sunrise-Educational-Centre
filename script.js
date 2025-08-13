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
    
    // Setup profile dropdown
    setupProfileDropdown();
    
    // Setup notification dropdown
    setupNotificationDropdown();
});

// Profile Dropdown Functionality
function setupProfileDropdown() {
    const profileDropdown = document.getElementById('profileDropdown');
    const profileLink = document.getElementById('profileLink');
    
    if (profileDropdown && profileLink) {
        // Show dropdown on click for mobile
        profileLink.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                profileDropdown.style.display = profileDropdown.style.display === 'block' ? 'none' : 'block';
            }
        });
        
        // Hide dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!profileLink.contains(e.target) && !profileDropdown.contains(e.target)) {
                profileDropdown.style.display = 'none';
            }
        });
        
        // Hide dropdown on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                profileDropdown.style.display = 'none';
            }
        });
    }
}

// Notification Dropdown Functionality
function setupNotificationDropdown() {
    const notificationItems = document.querySelectorAll('.notification-item');
    
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            const notificationType = this.getAttribute('data-type');
            const notificationId = this.getAttribute('data-notification-id');
            
            if (notificationType === 'personal_chat') {
                // For personal chat messages, mark as read and redirect to personal chat page
                markNotificationAsSeen(notificationId, 'personal_chat');
                window.location.href = '/personal-chat';
            } else {
                // For regular notifications, mark as seen
                markNotificationAsSeen(notificationId, 'notification');
            }
        });
    });
    
    // Start real-time notification updates
    startNotificationUpdates();
}

// Real-time notification updates
function startNotificationUpdates() {
    // Update notifications every 30 seconds
    setInterval(refreshNotifications, 30000);
    
    // Also refresh when the notification bell is clicked
    const bell = document.getElementById('notifBell');
    if (bell) {
        bell.addEventListener('click', refreshNotifications);
    }
}

// Refresh notifications from the server
function refreshNotifications() {
    fetch('/api/notifications')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateNotificationDropdown(data.notifications);
                updateNotificationCount(data.count);
            }
        })
        .catch(error => {
            console.error('Error refreshing notifications:', error);
        });
}

// Update the notification dropdown with new data
function updateNotificationDropdown(notifications) {
    const dropdown = document.getElementById('notifDropdown');
    if (!dropdown) return;
    
    const ul = dropdown.querySelector('ul');
    if (!ul) return;
    
    // Clear existing notifications
    ul.innerHTML = '';
    
    if (notifications && notifications.length > 0) {
        notifications.forEach(notification => {
            const li = createNotificationElement(notification);
            ul.appendChild(li);
        });
        
        // Re-setup click handlers for new notification items
        setupNotificationItemHandlers();
    } else {
        ul.innerHTML = '<li style="padding:0.7rem 0; color:#888; text-align:center;">No new notifications.</li>';
    }
}

// Create a notification element
function createNotificationElement(notification) {
    const li = document.createElement('li');
    
    if (notification.length >= 7) {
        const [id, message, created_at, status, notification_type, scheduled_time, item_type, sender_name] = notification;
        
        if (item_type === 'personal_chat') {
            li.className = 'notification-item personal-chat-item';
            li.setAttribute('data-notification-id', id);
            li.setAttribute('data-type', 'personal_chat');
            li.style.cssText = 'padding:0.5rem 0; border-bottom:1px solid #eee; font-size:0.98rem; color:#232946; cursor:pointer; transition:all 0.2s ease; border-left:3px solid #fc5c7d; padding-left:0.5rem;';
            li.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.3rem; margin-bottom:0.2rem;">
                    <span style="background:#fc5c7d; color:white; padding:0.1rem 0.4rem; border-radius:8px; font-size:0.7rem; font-weight:600;">💬</span>
                    <span style="color:#fc5c7d; font-size:0.8rem; font-weight:600;">@${sender_name || 'User'}</span>
                </div>
                ${message}<br><span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
            `;
        } else if (notification_type === 'forum_mention') {
            li.className = 'notification-item';
            li.setAttribute('data-notification-id', id);
            li.setAttribute('data-type', 'notification');
            li.style.cssText = 'padding:0.5rem 0; border-bottom:1px solid #eee; font-size:0.98rem; color:#232946; cursor:pointer; transition:all 0.2s ease; border-left:3px solid #ff6b6b; padding-left:0.5rem;';
            li.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.3rem; margin-bottom:0.2rem;">
                    <span style="background:#ff6b6b; color:white; padding:0.1rem 0.4rem; border-radius:8px; font-size:0.7rem; font-weight:600;">@</span>
                </div>
                ${message}<br><span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
            `;
        } else {
            li.className = 'notification-item';
            li.setAttribute('data-notification-id', id);
            li.setAttribute('data-type', 'notification');
            li.style.cssText = 'padding:0.5rem 0; border-bottom:1px solid #eee; font-size:0.98rem; color:#232946; cursor:pointer; transition:all 0.2s ease;';
            li.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.3rem; margin-bottom:0.2rem;">
                    <span style="background:#6a82fb; color:white; padding:0.1rem 0.4rem; border-radius:8px; font-size:0.7rem; font-weight:600;">📢</span>
                </div>
                ${message}<br><span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
            `;
        }
    } else {
        // Fallback for old notification format
        const [id, message, created_at, status, notification_type, scheduled_time] = notification;
        li.className = 'notification-item';
        li.setAttribute('data-notification-id', id);
        li.setAttribute('data-type', 'notification');
        li.style.cssText = 'padding:0.5rem 0; border-bottom:1px solid #eee; font-size:0.98rem; color:#232946; cursor:pointer; transition:all 0.2s ease;';
        li.innerHTML = `
            <div style="display:flex; align-items:center; gap:0.3rem; margin-bottom:0.2rem;">
                <span style="background:#6a82fb; color:white; padding:0.1rem 0.4rem; border-radius:8px; font-size:0.7rem; font-weight:600;">📢</span>
            </div>
            ${message}<br><span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
        `;
    }
    
    // Add hover effects
    li.addEventListener('mouseover', function() {
        if (li.classList.contains('personal-chat-item')) {
            this.style.background = '#ffe6cc';
        } else {
            this.style.background = '#f0f4ff';
        }
    });
    
    li.addEventListener('mouseout', function() {
        this.style.background = 'transparent';
    });
    
    return li;
}

// Setup click handlers for notification items
function setupNotificationItemHandlers() {
    const notificationItems = document.querySelectorAll('.notification-item');
    
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            const notificationType = this.getAttribute('data-type');
            const notificationId = this.getAttribute('data-notification-id');
            
            if (notificationType === 'personal_chat') {
                markNotificationAsSeen(notificationId, 'personal_chat');
                window.location.href = '/personal-chat';
            } else {
                markNotificationAsSeen(notificationId, 'notification');
            }
        });
    });
}

// Format datetime for display
function formatDateTime(dateString) {
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    } catch (e) {
        return dateString;
    }
}

// Mark notification as seen
function markNotificationAsSeen(notificationId, notificationType = 'notification') {
    fetch(`/api/mark-notification-seen/${notificationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: notificationType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the notification item from the dropdown
            const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationItem) {
                notificationItem.remove();
                
                // Update notification count
                updateNotificationCount();
                
                // Check if no more notifications
                const remainingNotifications = document.querySelectorAll('.notification-item');
                if (remainingNotifications.length === 0) {
                    const dropdown = document.getElementById('notifDropdown');
                    const ul = dropdown.querySelector('ul');
                    ul.innerHTML = '<li style="padding:1.1rem 1.2rem; color:#888; text-align:center; background:#f8fafc; border-radius:10px;">No new notifications or messages.</li>';
                    
                    // Hide notification count badge
                    const notificationCount = document.getElementById('notificationCount');
                    if (notificationCount) {
                        notificationCount.style.display = 'none';
                    }
                }
            }
        }
    })
    .catch(error => {
        console.error('Error marking notification as seen:', error);
    });
}

// Update notification count
function updateNotificationCount(count) {
    const notificationCount = document.getElementById('notificationCount');
    
    if (notificationCount) {
        if (count > 0) {
            notificationCount.textContent = count;
            notificationCount.style.display = 'flex';
        } else {
            notificationCount.style.display = 'none';
        }
    }
}

// Unified Dark Mode Implementation
function setupDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        updateToggleButton();
    }
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
    updateToggleButton();
}

function updateToggleButton() {
    const button = document.getElementById('darkModeToggle');
    if (button) {
        const isDark = document.body.classList.contains('dark-mode');
        button.innerHTML = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
        button.style.background = isDark ? 'rgba(255,255,255,0.1)' : 'transparent';
        button.style.color = isDark ? '#fff' : '#6a82fb';
        button.style.borderColor = isDark ? '#fff' : '#6a82fb';
    }
}

// Initialize dark mode on page load
document.addEventListener('DOMContentLoaded', function() {
    setupDarkMode();

    // Global notification dropdown behavior
    const bell = document.getElementById('notifBell');
    const dropdown = document.getElementById('notifDropdown');
    if (bell && dropdown) {
        // Toggle on bell click
        bell.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = dropdown.style.display === 'block';
            dropdown.style.display = isOpen ? 'none' : 'block';

            // Ensure dropdown stays within viewport on small screens
            if (!isOpen) {
                const rect = dropdown.getBoundingClientRect();
                if (rect.right > window.innerWidth) {
                    dropdown.style.left = `${Math.max(0, window.innerWidth - rect.width - 12)}px`;
                    dropdown.style.right = 'auto';
                }
            }
        });

        // Close when clicking outside
        document.addEventListener('click', function() {
            dropdown.style.display = 'none';
        });

        // Prevent closing when interacting inside
        dropdown.addEventListener('click', function(e) {
            e.stopPropagation();
        });

        // Close on ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') dropdown.style.display = 'none';
        });

        // Adjust on resize/orientation change
        window.addEventListener('resize', () => dropdown.style.display = 'none');
        window.addEventListener('orientationchange', () => dropdown.style.display = 'none');
    }
    
    // Setup dark mode toggle button if it exists
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
});