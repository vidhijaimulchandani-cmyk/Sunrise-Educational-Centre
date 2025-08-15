// Study Resources Page JavaScript - Apple Style

// Category switching functionality
function showCategory(event, categoryId) {
    // Hide all category content
    document.querySelectorAll('.category-content').forEach(content => {
        content.classList.remove('active');
    });

    // Deactivate all category tab buttons
    document.querySelectorAll('.category-tab').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected category content and activate its tab
    const activeCategoryContent = document.getElementById(categoryId);
    if (activeCategoryContent) {
        activeCategoryContent.classList.add('active');
        
        // Add smooth scroll to the category content
        activeCategoryContent.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Add click effect
    event.target.style.transform = 'scale(0.95)';
    setTimeout(() => {
        event.target.style.transform = '';
    }, 150);
}

// Resource opening functionality
function openResource(resourceName) {
    // This would typically open a PDF or document
    // For now, we'll show an alert with the resource name
    alert(`Opening: ${resourceName}\n\nThis would typically open the PDF/document in a new tab or download it.`);
    
    // In a real implementation, you might do something like:
    // window.open(`resources/${resourceName.replace(/\s+/g, '_')}.pdf`, '_blank');
}

// Enhanced resource card interactions
function enhanceResourceCards() {
    const resourceCards = document.querySelectorAll('.resource-card');
    
    resourceCards.forEach(card => {
        // Add click effect
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on the preview button
            if (e.target.classList.contains('btn-preview')) {
                return;
            }
            
            // Add click effect
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
        
        // Add hover sound effect (optional)
        card.addEventListener('mouseenter', function() {
            // You could add a subtle sound effect here
            this.style.cursor = 'pointer';
        });
    });
}

// Quick access functions
function downloadApp() {
    alert('Mobile app download would start here.\n\nRedirecting to app store...');
    // In real implementation:
    // window.open('https://play.google.com/store/apps/your-app', '_blank');
}

function openVideoLibrary() {
    alert('Opening video library...\n\nThis would redirect to the video lectures section.');
    // In real implementation:
    // window.location.href = 'video-library.html';
}

function submitDoubt() {
    const doubt = prompt('Please enter your doubt or question:');
    if (doubt && doubt.trim()) {
        alert(`Your doubt has been submitted successfully!\n\nDoubt: "${doubt}"\n\nSunrise Education Centre will respond within 24 hours.`);
        
        // In real implementation, you would send this to a server:
        // submitDoubtToServer(doubt);
    }
}

// Search functionality (bonus feature)
function searchResources() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const resourceCards = document.querySelectorAll('.resource-card');
    
    resourceCards.forEach(card => {
        const cardText = card.textContent.toLowerCase();
        if (cardText.includes(searchTerm)) {
            card.style.display = 'block';
            card.style.opacity = '1';
        } else {
            card.style.display = 'none';
            card.style.opacity = '0.5';
        }
    });
}

// Smooth animations for category tabs
function animateCategoryTabs() {
    const categoryTabs = document.querySelectorAll('.category-tab');
    
    categoryTabs.forEach((tab, index) => {
        // Add staggered animation
        tab.style.opacity = '0';
        tab.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            tab.style.transition = 'all 0.5s ease';
            tab.style.opacity = '1';
            tab.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Resource usage tracking
function trackResourceUsage(resourceName) {
    let usage = JSON.parse(localStorage.getItem('resourceUsage') || '{}');
    usage[resourceName] = (usage[resourceName] || 0) + 1;
    localStorage.setItem('resourceUsage', JSON.stringify(usage));
    
    // You could send this data to your analytics server
    console.log(`Resource accessed: ${resourceName}`);
}

// Initialize page with Apple-style enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Add search functionality if search input exists
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', searchResources);
    }
    
    // Enhance resource cards with interactions
    enhanceResourceCards();
    
    // Animate category tabs
    animateCategoryTabs();
    
    // Add click tracking for analytics
    const resourceLinks = document.querySelectorAll('.resource-card .btn-preview');
    resourceLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const resourceName = this.closest('.resource-card').querySelector('h3').textContent;
            trackResourceUsage(resourceName);
        });
    });
    
    // Show the first category tab by default
    const firstCategoryTab = document.querySelector('.category-tab');
    if (firstCategoryTab) {
        firstCategoryTab.click();
    }
    
    // Add smooth scrolling for better UX
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Utility function to format resource names for file paths
function formatResourceName(name) {
    return name.toLowerCase()
               .replace(/\s+/g, '_')
               .replace(/[^a-z0-9_]/g, '');
}

// Function to get most popular resources
function getPopularResources() {
    const usage = JSON.parse(localStorage.getItem('resourceUsage') || '{}');
    return Object.entries(usage)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([name]) => name);
}

// Function to show resource statistics (optional feature)
function showResourceStats() {
    const popularResources = getPopularResources();
    if (popularResources.length > 0) {
        console.log('Most popular resources:', popularResources);
        // You could display this in a nice modal or sidebar
    }
}

// Export functions for potential use in other scripts
window.StudyResources = {
    showCategory,
    openResource,
    trackResourceUsage,
    getPopularResources,
    showResourceStats
};
