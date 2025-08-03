// Study Resources Page JavaScript

// Category switching functionality
function showCategory(event, categoryId) {
    // Hide all category content
    document.querySelectorAll('.category-content').forEach(content => {
        content.classList.remove('active');
    });

    // Deactivate all sub-tab buttons
    document.querySelectorAll('.sub-tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected category content and activate its sub-tab
    const activeCategoryContent = document.getElementById(categoryId);
    if (activeCategoryContent) {
        activeCategoryContent.classList.add('active');
    }
    event.target.classList.add('active');
}

// Resource opening functionality
function openResource(resourceName) {
  // This would typically open a PDF or document
  // For now, we'll show an alert with the resource name
  alert(`Opening: ${resourceName}\n\nThis would typically open the PDF/document in a new tab or download it.`);
  
  // In a real implementation, you might do something like:
  // window.open(`resources/${resourceName.replace(/\s+/g, '_')}.pdf`, '_blank');
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

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
  // Add search functionality if search input exists
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', searchResources);
  }
  
  // Add click tracking for analytics (optional)
  const resourceLinks = document.querySelectorAll('.card a');
  resourceLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Track which resources are most accessed
      console.log(`Resource accessed: ${this.textContent}`);
    });
  });
  
  // Show the first category tab by default
  const firstCategoryTab = document.querySelector('.sub-tab-button');
  if (firstCategoryTab) {
    firstCategoryTab.click();
  }
});

// Utility function to format resource names for file paths
function formatResourceName(name) {
  return name.toLowerCase()
             .replace(/\s+/g, '_')
             .replace(/[^a-z0-9_]/g, '');
}

// Function to track most popular resources
function trackResourceUsage(resourceName) {
  let usage = JSON.parse(localStorage.getItem('resourceUsage') || '{}');
  usage[resourceName] = (usage[resourceName] || 0) + 1;
  localStorage.setItem('resourceUsage', JSON.stringify(usage));
}
