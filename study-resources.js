// Study Resources Page JavaScript

// Tab switching functionality
function showClass(event, classId) {
    // Hide all main class content
    document.querySelectorAll('.class-content').forEach(content => {
    content.classList.remove('active');
  });
  
    // Deactivate all main tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
    button.classList.remove('active');
  });
  
    // Show the selected class content and activate its tab
    const activeClassContent = document.getElementById(classId);
    if (activeClassContent) {
        activeClassContent.classList.add('active');
    }
    event.target.classList.add('active');
  
    // Automatically click the first sub-tab within the newly active class
    const firstSubTab = activeClassContent ? activeClassContent.querySelector('.sub-tab-button') : null;
    if (firstSubTab) {
        firstSubTab.click();
    }
}

function showCategory(event, categoryId) {
    const target = event.target;
    // The parent container of the sub-tabs for the current class
    const parentContainer = target.closest('.class-content');

    // Hide all category content within this class
    parentContainer.querySelectorAll('.category-content').forEach(content => {
        content.classList.remove('active');
    });

    // Deactivate all sub-tab buttons within this class
    parentContainer.querySelectorAll('.sub-tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected category content and activate its sub-tab
    const activeCategoryContent = document.getElementById(categoryId);
    if (activeCategoryContent) {
        activeCategoryContent.classList.add('active');
    }
    target.classList.add('active');
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
  const resourceLinks = document.querySelectorAll('.resource-card a');
  resourceLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Track which resources are most accessed
      console.log(`Resource accessed: ${this.textContent}`);
    });
  });
  
  // Click the first main class tab by default
  const firstClassTab = document.querySelector('.tab-button');
  if (firstClassTab) {
    firstClassTab.click();
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
