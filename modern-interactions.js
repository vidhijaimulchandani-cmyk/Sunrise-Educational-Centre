// ===== MODERN INTERACTIONS & ANIMATIONS =====

// Scroll Reveal Animation
class ScrollReveal {
    constructor() {
        this.elements = document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right');
        this.init();
    }

    init() {
        this.createObserver();
        this.observeElements();
    }

    createObserver() {
        const options = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    this.observer.unobserve(entry.target);
                }
            });
        }, options);
    }

    observeElements() {
        this.elements.forEach(element => {
            this.observer.observe(element);
        });
    }
}

// Smooth Scrolling for Anchor Links
class SmoothScroll {
    constructor() {
        this.init();
    }

    init() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Enhanced Typing Animation
class TypingAnimation {
    constructor(element, texts, options = {}) {
        this.element = element;
        this.texts = texts;
        this.options = {
            typeSpeed: 100,
            deleteSpeed: 50,
            pauseTime: 2000,
            loop: true,
            ...options
        };
        this.textIndex = 0;
        this.charIndex = 0;
        this.isDeleting = false;
        this.init();
    }

    init() {
        this.type();
    }

    type() {
        const currentText = this.texts[this.textIndex];
        
        if (this.isDeleting) {
            this.element.textContent = currentText.substring(0, this.charIndex - 1);
            this.charIndex--;
        } else {
            this.element.textContent = currentText.substring(0, this.charIndex + 1);
            this.charIndex++;
        }

        let typeSpeed = this.isDeleting ? this.options.deleteSpeed : this.options.typeSpeed;

        if (!this.isDeleting && this.charIndex === currentText.length) {
            typeSpeed = this.options.pauseTime;
            this.isDeleting = true;
        } else if (this.isDeleting && this.charIndex === 0) {
            this.isDeleting = false;
            this.textIndex = (this.textIndex + 1) % this.texts.length;
            typeSpeed = 500;
        }

        setTimeout(() => this.type(), typeSpeed);
    }
}

// Notification System
class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        this.notifications = [];
    }

    createContainer() {
        const container = document.createElement('div');
        container.className = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 2rem;
            right: 2rem;
            z-index: 1100;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            pointer-events: none;
        `;
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification-modern notification-${type}`;
        notification.style.pointerEvents = 'auto';
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.2rem;">${icons[type] || icons.info}</span>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; margin-left: auto;">×</button>
            </div>
        `;

        this.container.appendChild(notification);
        
        // Trigger show animation
        setTimeout(() => notification.classList.add('show'), 10);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }

        return notification;
    }
}

// Parallax Effect
class ParallaxEffect {
    constructor() {
        this.elements = document.querySelectorAll('[data-parallax]');
        this.init();
    }

    init() {
        if (this.elements.length === 0) return;
        
        window.addEventListener('scroll', () => this.updateParallax());
        this.updateParallax();
    }

    updateParallax() {
        const scrolled = window.pageYOffset;
        
        this.elements.forEach(element => {
            const rate = scrolled * (element.dataset.parallax || 0.5);
            element.style.transform = `translateY(${rate}px)`;
        });
    }
}

// Enhanced Button Interactions
class ButtonEnhancements {
    constructor() {
        this.init();
    }

    init() {
        // Add ripple effect to buttons
        document.querySelectorAll('.btn-modern, .btn-primary-modern, .btn-secondary-modern, .btn-glass').forEach(button => {
            button.addEventListener('click', this.createRipple);
        });

        // Add loading state functionality
        document.querySelectorAll('[data-loading]').forEach(button => {
            button.addEventListener('click', (e) => this.handleLoadingState(e.target));
        });
    }

    createRipple(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;

        // Add ripple animation keyframes if not exists
        if (!document.querySelector('#ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'ripple-styles';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    handleLoadingState(button) {
        const originalText = button.textContent;
        const loadingText = button.dataset.loading || 'Loading...';
        
        button.disabled = true;
        button.textContent = loadingText;
        button.classList.add('loading');

        // Simulate loading (remove this in real implementation)
        setTimeout(() => {
            button.disabled = false;
            button.textContent = originalText;
            button.classList.remove('loading');
        }, 2000);
    }
}

// Form Enhancements
class FormEnhancements {
    constructor() {
        this.init();
    }

    init() {
        // Add floating labels (but skip auth forms to avoid conflicts)
        document.querySelectorAll('.input-modern').forEach(input => {
            // Skip inputs in auth forms
            const form = input.closest('form');
            if (form && (form.id === 'loginForm' || form.id === 'signupForm')) {
                return;
            }
            this.addFloatingLabel(input);
        });

        // Add form validation (but skip auth forms)
        document.querySelectorAll('.form-modern').forEach(form => {
            this.addFormValidation(form);
        });
    }

    addFloatingLabel(input) {
        const wrapper = document.createElement('div');
        wrapper.className = 'input-wrapper';
        wrapper.style.position = 'relative';
        
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const label = document.createElement('label');
        label.textContent = input.placeholder;
        label.className = 'floating-label';
        label.style.cssText = `
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.6);
            transition: all 0.3s ease;
            pointer-events: none;
            background: transparent;
            padding: 0 0.25rem;
        `;

        wrapper.appendChild(label);

        const updateLabel = () => {
            if (input.value || input === document.activeElement) {
                label.style.top = '0';
                label.style.fontSize = '0.8rem';
                label.style.color = '#6a82fb';
                label.style.background = 'var(--glass-bg)';
            } else {
                label.style.top = '50%';
                label.style.fontSize = '1rem';
                label.style.color = 'rgba(255, 255, 255, 0.6)';
                label.style.background = 'transparent';
            }
        };

        input.addEventListener('focus', updateLabel);
        input.addEventListener('blur', updateLabel);
        input.addEventListener('input', updateLabel);
        
        updateLabel();
    }

    addFormValidation(form) {
        // Skip validation for auth forms to avoid conflicts
        if (form.id === 'loginForm' || form.id === 'signupForm') {
            return;
        }
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const inputs = form.querySelectorAll('.input-modern[required]');
            let isValid = true;

            inputs.forEach(input => {
                const errorElement = input.parentNode.querySelector('.form-error-modern');
                
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#ff6b6b';
                    
                    if (!errorElement) {
                        const error = document.createElement('div');
                        error.className = 'form-error-modern';
                        error.textContent = `${input.placeholder} is required`;
                        input.parentNode.appendChild(error);
                    }
                } else {
                    input.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                    if (errorElement) {
                        errorElement.remove();
                    }
                }
            });

            if (isValid) {
                // Form is valid, proceed with submission
                console.log('Form is valid, submitting...');
                // Allow the form to submit naturally
                form.submit();
            }
        });
    }
}

// Theme Switcher Enhancement
class ThemeSwitcher {
    constructor() {
        this.init();
    }

    init() {
        const toggles = document.querySelectorAll('#darkModeToggle, #footerThemeToggle');

        toggles.forEach(toggle => {
            if (!toggle.dataset.boundTheme) {
                toggle.addEventListener('click', () => this.toggleTheme());
                toggle.dataset.boundTheme = 'true';
            }
        });

        // Set initial theme: prefer saved 'preferredTheme'/'theme', else system preference
        let savedTheme = null;
        try {
            savedTheme = localStorage.getItem('preferredTheme') || localStorage.getItem('theme');
        } catch (e) {}

        if (savedTheme === 'dark' || savedTheme === 'light') {
            document.body.classList.toggle('dark-mode', savedTheme === 'dark');
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        }
        this.updateToggleText();
    }

    toggleTheme() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');

        try {
            localStorage.setItem('preferredTheme', isDark ? 'dark' : 'light');
            // keep legacy key in sync
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        } catch (e) {}

        this.updateToggleText();

        // Add smooth transition
        document.body.style.transition = 'all 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    updateToggleText() {
        const toggles = document.querySelectorAll('#darkModeToggle, #footerThemeToggle');
        const isDark = document.body.classList.contains('dark-mode');
        
        toggles.forEach(toggle => {
            toggle.textContent = isDark ? '☀️' : '🌙';
            toggle.title = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
        });
    }
}

// Initialize all enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize scroll reveal
    new ScrollReveal();
    
    // Initialize smooth scrolling
    new SmoothScroll();
    
    // Initialize typing animation for hero
    const heroElement = document.getElementById('typing-hero');
    if (heroElement) {
        new TypingAnimation(heroElement, [
            'Welcome to Sunrise Educational Centre',
            'Excellence in Mathematics Education',
            'Your Success is Our Mission',
            'Join the Future Leaders'
        ]);
    }
    
    // Initialize notification system
    window.notifications = new NotificationSystem();
    
    // Initialize parallax effect
    new ParallaxEffect();
    
    // Initialize button enhancements
    new ButtonEnhancements();
    
    // Initialize form enhancements
    new FormEnhancements();
    
    // Initialize theme switcher
    new ThemeSwitcher();
    
    // Show welcome notification after page load
    setTimeout(() => {
        if (window.notifications) {
            window.notifications.show('Welcome to Sunrise Educational Centre! 🌟', 'success', 4000);
        }
    }, 1000);
});

// Utility Functions
const utils = {
    // Debounce function for performance optimization
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function for scroll events
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Format numbers with animation
    animateNumber(element, start, end, duration = 2000) {
        const startTime = performance.now();
        const difference = end - start;

        const step = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(start + (difference * easeOutQuart));
            
            element.textContent = current.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };
        
        requestAnimationFrame(step);
    }
};

// Export for use in other scripts
window.ModernInteractions = {
    ScrollReveal,
    SmoothScroll,
    TypingAnimation,
    NotificationSystem,
    ParallaxEffect,
    ButtonEnhancements,
    FormEnhancements,
    ThemeSwitcher,
    utils
};