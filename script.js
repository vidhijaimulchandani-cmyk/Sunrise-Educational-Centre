function joinLiveClass() {
  // Navigate to the dedicated online class page (server route)
  window.location.href = '/online-class';
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
    // Inject a universal navbar if missing
    try {
      if (!document.querySelector('.floating-navbar')) {
        const nav = document.createElement('nav');
        nav.className = 'floating-navbar black-glass';
        nav.innerHTML = `
          <button class="hamburger" aria-label="Menu" aria-expanded="false">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
          </button>
          <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/online-class">Live Classes</a></li>
            <li><a href="/batch">Batches</a></li>
            <li><a href="/study-resources">Study Resources</a></li>
            <li><a href="/forum">Forum</a></li>
            <li class="profile-dropdown">
              <a href="#" id="profileLink">Profile ▾</a>
              <div class="profile-dropdown-menu" id="profileDropdown">
                <a href="/profile" class="dropdown-item">My Profile</a>
                <a href="/notifications" class="dropdown-item">Notifications</a>
                <a href="/auth" class="dropdown-item" id="loginLink">Login</a>
                <a href="/logout" class="dropdown-item" id="logoutLink" style="display:none;">Logout</a>
              </div>
            </li>
            <li style="position:relative;">
              <button id="notifBell" class="notification-bell" title="Notifications">🔔
                <span id="notificationCount" class="notification-badge" style="display:none;"></span>
              </button>
              <div id="notifDropdown" style="display:none;"><strong style="color:#6a82fb;">Notifications</strong><ul style="list-style:none; padding:0; margin:0;"></ul></div>
            </li>
          </ul>`;
        document.body.insertBefore(nav, document.body.firstChild);
      }
    } catch (e) {}

    const hamburger = document.querySelector(".hamburger");
    const navLinks = document.querySelector(".nav-links");

    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("active");
            navLinks.classList.toggle("active");
        });
    }
    
    // Auto-enhance all floating navbars across pages
    try {
      const navbars = document.querySelectorAll('.floating-navbar');
      navbars.forEach(nav => {
        // Ensure black-glass styling for consistency
        if (!nav.classList.contains('black-glass')) {
          nav.classList.add('black-glass');
        }

        // Ensure a hamburger exists for mobile
        let burger = nav.querySelector('.hamburger');
        if (!burger) {
          burger = document.createElement('button');
          burger.className = 'hamburger';
          burger.setAttribute('aria-label', 'Menu');
          burger.setAttribute('aria-expanded', 'false');
          burger.innerHTML = '<span class="bar"></span><span class="bar"></span><span class="bar"></span>';
          // Prepend the hamburger before nav-links
          const links = nav.querySelector('.nav-links');
          if (links) {
            nav.insertBefore(burger, links);
          } else {
            nav.appendChild(burger);
          }
        }

        // Wire up hamburger toggle to corresponding nav-links within same nav
        const links = nav.querySelector('.nav-links');
        if (burger && links) {
          burger.addEventListener('click', () => {
            const isActive = links.classList.toggle('active');
            burger.classList.toggle('active', isActive);
            burger.setAttribute('aria-expanded', String(isActive));
          });
        }

        // Ensure Notification bell exists (and dropdown container)
        if (links && !document.getElementById('notifBell')) {
          const notifLi = document.createElement('li');
          notifLi.style.position = 'relative';
          notifLi.innerHTML = `
            <button id="notifBell" title="Notifications" style="background:none;border:none;cursor:pointer;position:relative;color:#fff;">
              🔔
              <span id="notificationCount" style="position:absolute;top:0;right:0;width:18px;height:18px;background:#fc5c7d;border-radius:50%;color:white;font-size:10px;font-weight:bold;display:none;align-items:center;justify-content:center;">0</span>
            </button>
            <div id="notifDropdown" style="display:none;">
              <strong style="color:#6a82fb;">Notifications</strong>
              <ul style="list-style:none; padding:0; margin:0;"></ul>
            </div>`;
          links.appendChild(notifLi);
        }

        // Ensure Profile dropdown exists
        if (links && !document.getElementById('profileLink')) {
          const profileLi = document.createElement('li');
          profileLi.className = 'profile-dropdown';
          profileLi.innerHTML = `
            <a href="#" id="profileLink">Profile ▾</a>
            <div class="profile-dropdown-menu" id="profileDropdown">
              <a href="/profile" class="dropdown-item">My Profile</a>
              <a href="/notifications" class="dropdown-item">Notifications</a>
              <a href="/auth" class="dropdown-item" id="loginLink">Login</a>
              <a href="/logout" class="dropdown-item" id="logoutLink" style="display:none;">Logout</a>
            </div>`;
          links.appendChild(profileLi);
        }

        // Ensure core links consistency (Home present)
        if (links && !links.querySelector('a[href="/"]')) {
          const li = document.createElement('li');
          const a = document.createElement('a');
          a.href = '/';
          a.textContent = 'Home';
          li.appendChild(a);
          links.insertBefore(li, links.firstChild);
        }

        // Ensure Scholars link exists
        if (links && !links.querySelector('a[href="/scholars"]')) {
          const li = document.createElement('li');
          const a = document.createElement('a');
          a.href = '/scholars';
          a.textContent = 'Scholars';
          li.appendChild(a);
          links.appendChild(li);
        }
      });
    } catch (e) {
      // no-op: defensive guard for pages without nav
    }
    
    // Setup profile dropdown
    setupProfileDropdown();
    
    // Setup notification dropdown
    setupNotificationDropdown();

    // Remove Admission and theme toggle from all navbars
    try {
      document.querySelectorAll('.floating-navbar .nav-links a[href="/admission"]').forEach(a => {
        const li = a.closest('li');
        if (li && li.parentElement) li.parentElement.removeChild(li);
        else a.remove();
      });
      const themeBtn = document.getElementById('darkModeToggle');
      if (themeBtn) {
        const li = themeBtn.closest('li');
        if (li && li.parentElement) li.parentElement.removeChild(li);
        else themeBtn.remove();
      }
    } catch (e) {}

    // Mark active link based on current path
    try {
      const currentPath = window.location.pathname;
      document.querySelectorAll('.floating-navbar .nav-links a').forEach(a => {
        const href = a.getAttribute('href');
        if (!href) return;
        if (href === '/' && currentPath === '/') {
          a.classList.add('active');
        } else if (href !== '/' && currentPath.startsWith(href)) {
          a.classList.add('active');
        } else {
          a.classList.remove('active');
        }
      });
    } catch (e) {}
});

// Profile Dropdown Functionality
function setupProfileDropdown() {
    const profileDropdown = document.getElementById('profileDropdown');
    const profileLink = document.getElementById('profileLink');
    
    if (profileDropdown && profileLink) {
        // Show dropdown on click for all devices (mobile-friendly)
        profileLink.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle dropdown visibility
            const isVisible = profileDropdown.classList.contains('active');
            
            // Close all other dropdowns first
            closeAllDropdowns();
            
            if (!isVisible) {
                profileDropdown.classList.add('active');
                
                // Position dropdown properly on mobile
                if (window.innerWidth <= 768) {
                    positionDropdownForMobile(profileDropdown);
                    // Prevent body scroll on mobile when dropdown is open
                    document.body.classList.add('dropdown-open');
                }
            } else {
                // Remove dropdown-open class when closing
                document.body.classList.remove('dropdown-open');
            }
        });
        
        // Hide dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!profileLink.contains(e.target) && !profileDropdown.contains(e.target)) {
                profileDropdown.classList.remove('active');
            }
        });
        
        // Hide dropdown on window resize
        window.addEventListener('resize', function() {
            profileDropdown.classList.remove('active');
        });
        
        // Hide dropdown on orientation change
        window.addEventListener('orientationchange', function() {
            setTimeout(() => {
                profileDropdown.classList.remove('active');
            }, 100);
        });
    }
}

// Function to position dropdown properly on mobile
function positionDropdownForMobile(dropdown) {
    if (!dropdown) return;
    
    // Get the profile link position
    const profileLink = document.getElementById('profileLink');
    if (!profileLink) return;
    
    const linkRect = profileLink.getBoundingClientRect();
    const dropdownRect = dropdown.getBoundingClientRect();
    
    // Calculate available space
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // Position dropdown below the profile link if there's space
    if (linkRect.bottom + dropdownRect.height <= viewportHeight) {
        dropdown.style.top = '100%';
        dropdown.style.bottom = 'auto';
    } else {
        // Position above if not enough space below
        dropdown.style.top = 'auto';
        dropdown.style.bottom = '100%';
    }
    
    // Ensure dropdown doesn't go off-screen horizontally
    if (linkRect.right + dropdownRect.width > viewportWidth) {
        dropdown.style.right = '0';
        dropdown.style.left = 'auto';
    } else {
        dropdown.style.left = '0';
        dropdown.style.right = 'auto';
    }
}

// Function to close all dropdowns
function closeAllDropdowns() {
    const profileDropdown = document.getElementById('profileDropdown');
    const notifDropdown = document.getElementById('notifDropdown');
    
    if (profileDropdown) profileDropdown.classList.remove('active');
    if (notifDropdown) notifDropdown.style.display = 'none';
    
    // Remove dropdown-open class to restore body scroll
    document.body.classList.remove('dropdown-open');
}

// Function to position notification dropdown properly on mobile
function positionNotificationDropdownForMobile(dropdown) {
    if (!dropdown) return;
    
    // Get the notification bell position
    const bell = document.getElementById('notifBell');
    if (!bell) return;
    
    const bellRect = bell.getBoundingClientRect();
    const dropdownRect = dropdown.getBoundingClientRect();
    
    // Calculate available space
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // Position dropdown below the bell if there's space
    if (bellRect.bottom + dropdownRect.height <= viewportHeight) {
        dropdown.style.top = '36px';
        dropdown.style.bottom = 'auto';
    } else {
        // Position above if not enough space below
        dropdown.style.top = 'auto';
        dropdown.style.bottom = '36px';
    }
    
    // Ensure dropdown doesn't go off-screen horizontally
    if (bellRect.right + dropdownRect.width > viewportWidth) {
        dropdown.style.right = '0';
        dropdown.style.left = 'auto';
    } else {
        dropdown.style.left = '0';
        dropdown.style.right = 'auto';
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
            console.log('Received notification data:', data);
            if (data.success) {
                // Log each notification for debugging
                if (data.notifications && data.notifications.length > 0) {
                    console.log('Processing notifications:');
                    data.notifications.forEach((notification, index) => {
                        console.log(`Notification ${index + 1}:`, {
                            id: notification[0],
                            message: notification[1],
                            messageLength: notification[1] ? notification[1].length : 0,
                            type: notification[4],
                            itemType: notification[6]
                        });
                    });
                }
                
                updateNotificationDropdown(data.notifications);
                updateNotificationCount(data.count);
            } else {
                console.error('Notification API returned error:', data.error);
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
        
        // Ensure message is properly displayed and not truncated
        const displayMessage = message || 'No message content';
        console.log('Creating notification element:', { id, message: displayMessage, type: notification_type, item_type });
        
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
                <div style="word-wrap: break-word; max-width: 100%;">${displayMessage}</div>
                <span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
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
                <div style="word-wrap: break-word; max-width: 100%;">${displayMessage}</div>
                <span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
            `;
        } else if (notification_type === 'block_warning' || notification_type === 'ban_warning') {
            // Special handling for block/ban notifications
            li.className = 'notification-item block-notification';
            li.setAttribute('data-notification-id', id);
            li.setAttribute('data-type', 'notification');
            li.style.cssText = 'padding:0.5rem 0; border-bottom:1px solid #eee; font-size:0.98rem; color:#dc3545; cursor:pointer; transition:all 0.2s ease; border-left:3px solid #dc3545; padding-left:0.5rem; background: #fff5f5;';
            li.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.3rem; margin-bottom:0.2rem;">
                    <span style="background:#dc3545; color:white; padding:0.1rem 0.4rem; border-radius:8px; font-size:0.7rem; font-weight:600;">🚫</span>
                    <span style="color:#dc3545; font-size:0.8rem; font-weight:600;">${notification_type === 'block_warning' ? 'Block Warning' : 'Ban Warning'}</span>
                </div>
                <div style="word-wrap: break-word; max-width: 100%; color: #721c24;">${displayMessage}</div>
                <span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
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
                <div style="word-wrap: break-word; max-width: 100%;">${displayMessage}</div>
                <span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
            `;
        }
    } else {
        // Fallback for old notification format
        const [id, message, created_at, status, notification_type, scheduled_time] = notification;
        const displayMessage = message || 'No message content';
        
        li.className = 'notification-item';
        li.setAttribute('data-notification-id', id);
        li.setAttribute('data-type', 'notification');
        li.style.cssText = 'padding:0.5rem 0; border-bottom:1px solid #eee; font-size:0.98rem; color:#232946; cursor:pointer; transition:all 0.2s ease;';
        li.innerHTML = `
            <div style="display:flex; align-items:center; gap:0.3rem; margin-bottom:0.2rem;">
                <span style="background:#6a82fb; color:white; padding:0.1rem 0.4rem; border-radius:8px; font-size:0.7rem; font-weight:600;">📢</span>
            </div>
            <div style="word-wrap: break-word; max-width: 100%;">${displayMessage}</div>
            <span style="font-size:0.85rem; color:#888;">${formatDateTime(created_at)}</span>
        `;
    }
    
    // Add hover effects
    li.addEventListener('mouseover', function() {
        if (li.classList.contains('personal-chat-item')) {
            this.style.background = '#ffe6cc';
        } else if (li.classList.contains('block-notification')) {
            this.style.background = '#ffe6e6';
        } else {
            this.style.background = '#f0f4ff';
        }
    });
    
    li.addEventListener('mouseout', function() {
        if (li.classList.contains('block-notification')) {
            this.style.background = '#fff5f5';
        } else {
            this.style.background = 'transparent';
        }
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
    
    // Setup mobile touch handling for dropdowns
    setupMobileTouchHandling();

    // Global notification dropdown behavior
    const bell = document.getElementById('notifBell');
    const dropdown = document.getElementById('notifDropdown');
    if (bell && dropdown) {
        // Toggle on bell click
        bell.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = dropdown.style.display === 'block';
            
            // Close all other dropdowns first
            closeAllDropdowns();
            
            if (!isOpen) {
                dropdown.style.display = 'block';
                
                // Position dropdown properly on mobile
                if (window.innerWidth <= 768) {
                    positionNotificationDropdownForMobile(dropdown);
                    // Prevent body scroll on mobile when dropdown is open
                    document.body.classList.add('dropdown-open');
                }
            } else {
                // Remove dropdown-open class when closing
                document.body.classList.remove('dropdown-open');
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
        window.addEventListener('resize', () => {
            dropdown.style.display = 'none';
        });
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                dropdown.style.display = 'none';
            }, 100);
        });
    }
    
    // Setup dark mode toggle button if it exists
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
});

// Inject "Last updated" time (IST) into footer across all pages
document.addEventListener('DOMContentLoaded', function() {
    try {
        initLastUpdatedFooter();
    } catch (e) {
        console.error('Error initializing last-updated footer:', e);
    }
});

function initLastUpdatedFooter() {
    // Ensure a footer exists; if not, create a minimal one
    let footer = document.querySelector('footer.footer');
    if (!footer) {
        footer = document.createElement('footer');
        footer.className = 'footer';
        const container = document.createElement('div');
        container.className = 'container footer-content';
        footer.appendChild(container);
        document.body.appendChild(footer);
    }

    const container = footer.querySelector('.footer-content') || footer;
    let updatedEl = footer.querySelector('#footerLastUpdated');
    if (!updatedEl) {
        updatedEl = document.createElement('div');
        updatedEl.id = 'footerLastUpdated';
        updatedEl.className = 'footer-updated';
        container.appendChild(updatedEl);
    }

    fetch('/api/site-last-updated')
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data && data.success && data.formatted) {
                updatedEl.textContent = 'Last updated: ' + data.formatted;
            } else {
                updatedEl.textContent = 'Last updated: ' + (new Date()).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST';
            }
        })
        .catch(function() {
            updatedEl.textContent = 'Last updated: ' + (new Date()).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' }) + ' IST';
        });
}

// Setup mobile touch handling for better dropdown experience
function setupMobileTouchHandling() {
    // Add touch event listeners for mobile devices
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        // Prevent double-tap zoom on dropdown items
        const dropdownItems = document.querySelectorAll('.dropdown-item, .notification-item');
        dropdownItems.forEach(item => {
            item.addEventListener('touchend', function(e) {
                // Small delay to prevent immediate closing
                setTimeout(() => {
                    // Handle the action (navigation, etc.)
                    if (this.href) {
                        window.location.href = this.href;
                    }
                }, 100);
            });
        });
        
        // Better touch handling for dropdown toggles
        const profileLink = document.getElementById('profileLink');
        const notifBell = document.getElementById('notifBell');
        
        if (profileLink) {
            profileLink.addEventListener('touchend', function(e) {
                e.preventDefault();
                // Small delay to ensure proper touch handling
                setTimeout(() => {
                    this.click();
                }, 50);
            });
        }
        
        if (notifBell) {
            notifBell.addEventListener('touchend', function(e) {
                e.preventDefault();
                // Small delay to ensure proper touch handling
                setTimeout(() => {
                    this.click();
                }, 50);
            });
        }
    }
}