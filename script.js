function joinLiveClass() {
  // Navigate to the dedicated online class page
  window.location.href = 'online-class.html';
}

// Enhanced Typography Animation System
document.addEventListener('DOMContentLoaded', function() {
  // Enhanced typing animation for the main heading
  const headingElement = document.querySelector('.hero-content h1');
  
  // Only run typing animation if the element exists
  if (headingElement) {
    const text = "Expert Coaching for Class 9 to 12";
    let index = 0;
    
    function typeText() {
      if (index < text.length) {
        headingElement.textContent += text.charAt(index);
        index++;
        setTimeout(typeText, 100); // Adjust speed here (100ms per character)
      } else {
        // Add a subtle glow effect after typing completes
        setTimeout(() => {
          headingElement.classList.add('text-glow');
        }, 500);
      }
    }
    
    // Clear the heading and start typing
    headingElement.textContent = '';
    
    // Start typing after a brief delay
    setTimeout(typeText, 500); // Pause before restarting
  }
  
  // Enhanced scroll-triggered animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
        
        // Add staggered animations for child elements
        const animatedChildren = entry.target.querySelectorAll('.animated-text, .animate-stagger');
        animatedChildren.forEach((child, index) => {
          child.style.animationDelay = `${index * 0.1}s`;
          child.style.animationPlayState = 'running';
        });
      }
    });
  }, observerOptions);
  
  // Observe all animated cards and sections
  const revealElements = document.querySelectorAll('.animated-card, .section-header, .card-section');
  revealElements.forEach(el => {
    el.style.animationPlayState = 'paused';
    observer.observe(el);
  });
  
  // Enhanced text animation triggers
  function triggerTextAnimation(element, animationType) {
    element.style.animation = 'none';
    element.offsetHeight; // Trigger reflow
    element.classList.remove('text-reveal', 'text-slide-in', 'text-fade-in-up', 'text-scale-in', 'text-glow', 'text-bounce', 'text-shimmer', 'text-wave', 'text-pulse', 'text-rainbow', 'text-gradient');
    element.classList.add(animationType);
  }
  
  // Add click-to-animate functionality for demonstration
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('animation-trigger')) {
      const targetElement = document.querySelector(e.target.dataset.target);
      if (targetElement) {
        triggerTextAnimation(targetElement, e.target.dataset.animation);
      }
    }
  });
  
  // Enhanced hover effects for typography
  const typographyElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  typographyElements.forEach(element => {
    element.addEventListener('mouseenter', function() {
      if (!this.classList.contains('text-glow') && !this.classList.contains('text-shimmer')) {
        this.classList.add('text-hover-glow');
      }
    });
    
    element.addEventListener('mouseleave', function() {
      this.classList.remove('text-hover-glow');
    });
  });
  
  // Parallax effect for hero section text
  let ticking = false;
  function updateParallax() {
    const scrolled = window.pageYOffset;
    const heroText = document.querySelector('.hero-content h1');
    if (heroText) {
      const rate = scrolled * -0.5;
      heroText.style.transform = `translateY(${rate}px)`;
    }
    ticking = false;
  }
  
  function requestTick() {
    if (!ticking) {
      requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }
  
  window.addEventListener('scroll', requestTick);
  
  // Enhanced ripple effect for buttons
  function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    button.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }
  
  const buttons = document.querySelectorAll('.btn, .btn-cta, .subject-btn');
  buttons.forEach(button => {
    button.addEventListener('click', createRipple);
  });
  
  // Add ripple effect styles
  const style = document.createElement('style');
  style.textContent = `
    .ripple {
      position: absolute;
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s linear;
      background: rgba(255,255,255,0.5);
      pointer-events: none;
      width: 100px;
      height: 100px;
      left: 0;
      top: 0;
      z-index: 10;
    }
    @keyframes ripple {
      to {
        transform: scale(2.5);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
  
  // Enhanced text reveal on scroll
  const textObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const text = entry.target;
        const words = text.textContent.split(' ');
        text.innerHTML = '';
        
        words.forEach((word, index) => {
          const span = document.createElement('span');
          span.textContent = word + ' ';
          span.style.opacity = '0';
          span.style.transform = 'translateY(20px)';
          span.style.animation = `textFadeInUp 0.6s ease-out ${index * 0.1}s forwards`;
          text.appendChild(span);
        });
        
        textObserver.unobserve(text);
      }
    });
  }, { threshold: 0.5 });
  
  // Observe text elements for reveal animation
  const textElements = document.querySelectorAll('.text-reveal-on-scroll');
  textElements.forEach(el => textObserver.observe(el));
  
  // Enhanced loading animations
  function addLoadingAnimations() {
    const loadingElements = document.querySelectorAll('.loading-animate');
    loadingElements.forEach((element, index) => {
      element.style.animationDelay = `${index * 0.1}s`;
      element.classList.add('text-fade-in-up');
    });
  }
  
  // Call loading animations after page load
  window.addEventListener('load', addLoadingAnimations);
  
  // Enhanced performance monitoring for animations
  let animationFrameCount = 0;
  let lastTime = performance.now();
  
  function monitorAnimationPerformance(currentTime) {
    animationFrameCount++;
    
    if (currentTime - lastTime >= 1000) {
      const fps = Math.round((animationFrameCount * 1000) / (currentTime - lastTime));
      
      // Reduce animation complexity if FPS is low
      if (fps < 30) {
        document.body.classList.add('reduce-animations');
      } else {
        document.body.classList.remove('reduce-animations');
      }
      
      animationFrameCount = 0;
      lastTime = currentTime;
    }
    
    requestAnimationFrame(monitorAnimationPerformance);
  }
  
  requestAnimationFrame(monitorAnimationPerformance);
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