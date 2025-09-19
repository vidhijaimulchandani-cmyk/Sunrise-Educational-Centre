#!/usr/bin/env python3
"""
Script to fix navbar across all HTML pages in the Sunrise Educational Centre website
"""

import os
import re
from pathlib import Path

# Standard navbar HTML
STANDARD_NAVBAR = '''    <!-- Floating Navbar -->
    <nav class="floating-navbar black-glass">
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
            <li><a href="/admission">Admission</a></li>
            
            {% if is_admin %}
            <li class="admin-dropdown">
                <a href="#" id="adminLink">Admin ▾</a>
                <div class="admin-dropdown-menu" id="adminDropdown">
                    <a href="/admin" class="dropdown-item">Dashboard</a>
                    <a href="/batch-management" class="dropdown-item">Batch Management</a>
                    <a href="/content-management" class="dropdown-item">Content Management</a>
                    <a href="/query-management" class="dropdown-item">Query Management</a>
                    <a href="/live-class-management" class="dropdown-item">Live Classes</a>
                </div>
            </li>
            {% endif %}
            
            {% if username %}
            <li class="profile-dropdown">
                <a href="#" id="profileLink">{{ username }} ▾</a>
                <div class="profile-dropdown-menu" id="profileDropdown">
                    <a href="/profile" class="dropdown-item">My Profile</a>
                    <a href="/notifications" class="dropdown-item">Notifications</a>
                    <a href="/logout" class="dropdown-item">Logout</a>
                </div>
            </li>
            {% else %}
            <li><a href="/auth" class="btn-primary">Login</a></li>
            {% endif %}
            
            <li><button class="search-btn" onclick="openSearch()">🔍</button></li>
            <li style="position:relative;">
                <button id="notifBell" class="notification-bell" title="Notifications">
                    🔔
                    <span class="notification-badge" id="notificationCount" style="display:none;">0</span>
                </button>
            </li>
            <li>
                <button id="darkModeToggle" class="theme-toggle-btn" title="Toggle Dark Mode">
                    🌙
                </button>
            </li>
        </ul>
    </nav>'''

# Standard modals and scripts
STANDARD_MODALS = '''
    <!-- Search Modal -->
    <div id="searchModal" class="modal" style="display: none; position: fixed; z-index: 10000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5);">
        <div class="modal-content black-glass" style="margin: 10% auto; padding: 2rem; border-radius: 20px; width: 90%; max-width: 600px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="color: white; margin: 0;">🔍 Search</h2>
                <button onclick="closeSearch()" style="background: none; border: none; color: #fff; font-size: 1.5rem; cursor: pointer;">✕</button>
            </div>
            <input type="text" id="searchInput" placeholder="Search courses, resources, or topics..." style="width: 100%; padding: 15px; border: none; border-radius: 10px; background: rgba(255,255,255,0.1); color: white; font-size: 1rem; margin-bottom: 1rem;">
            <div id="searchResults" style="max-height: 300px; overflow-y: auto;"></div>
        </div>
    </div>

    <!-- Notification Panel -->
    <div id="notification-panel" class="notification-panel black-glass" style="display: none; position: fixed; top: 100px; right: 20px; width: 350px; max-height: 500px; overflow-y: auto; z-index: 999; border-radius: 16px; padding: 1rem; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.2);">
            <h3 style="margin: 0; font-size: 1.2rem; color: white;">🔔 Notifications</h3>
            <button onclick="toggleNotifications()" style="background: none; border: none; color: #fff; font-size: 1.2rem; cursor: pointer; padding: 0.2rem;">✕</button>
        </div>
        <div class="notification-list">
            <div class="notification-item" style="padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 0.5rem;">
                <div style="font-weight: 600; margin-bottom: 0.3rem; color: white;">📚 Latest Updates</div>
                <div style="font-size: 0.9rem; opacity: 0.8; color: rgba(255,255,255,0.8);">Check out new features and content</div>
            </div>
        </div>
    </div>

    <script src="navbar-functions.js"></script>'''

def fix_html_file(filepath):
    """Fix a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add required CSS files if missing
        head_section = content[:content.find('</head>')]
        
        required_css = [
            'floating-navbar.css',
            'uiverse-components.css'
        ]
        
        for css_file in required_css:
            if css_file not in head_section:
                # Add before </head>
                content = content.replace('</head>', f'    <link rel="stylesheet" href="{css_file}">\n</head>')
        
        # Check if page already has floating-navbar
        if 'floating-navbar' not in content:
            # Find body tag and add navbar after it
            body_match = re.search(r'<body[^>]*>', content)
            if body_match:
                insert_pos = body_match.end()
                content = content[:insert_pos] + '\n' + STANDARD_NAVBAR + '\n' + content[insert_pos:]
        
        # Add modals and scripts before </body> if not present
        if 'navbar-functions.js' not in content:
            content = content.replace('</body>', STANDARD_MODALS + '\n</body>')
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        else:
            print(f"⏭️  Skipped: {filepath} (already has navbar)")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all HTML files"""
    
    # Files to skip (already fixed or special cases)
    skip_files = {
        'index.html',
        'auth.html', 
        'admission.html',
        'batch.html',
        'navbar-template.html',
        'uiverse-demo.html',
        'uiverse-showcase.html',
        'test_auth_simple.html',
        'test_form_submission.html',
        'test_forum_debug.html',
        'test_forum_slider.html',
        'test_modal.html',
        'test_modern_navbar.html',
        'test_study_resources_slider.html',
        'test_admission_status.html',
        'mobile_dropdown_test.html'
    }
    
    # Get all HTML files
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in skip_files]
    
    print(f"🚀 Starting navbar fixes for {len(html_files)} files...")
    print("=" * 50)
    
    fixed_count = 0
    for html_file in sorted(html_files):
        if fix_html_file(html_file):
            fixed_count += 1
    
    print("=" * 50)
    print(f"✨ Completed! Fixed {fixed_count} out of {len(html_files)} files.")
    print("\n🎯 All pages now have:")
    print("  • Standardized floating navbar")
    print("  • Uiverse components support")
    print("  • Search functionality")
    print("  • Notification system")
    print("  • Theme toggle")
    print("  • Mobile responsive design")

if __name__ == "__main__":
    main()