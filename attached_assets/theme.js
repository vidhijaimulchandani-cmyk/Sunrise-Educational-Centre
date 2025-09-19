// Simple dark mode manager with localStorage persistence (no auto-injection)
(function () {
  var STORAGE_KEY = 'preferredTheme';
  var CLASS_DARK = 'dark-mode';

  function applyTheme(theme) {
    var isDark = theme === 'dark';
    if (isDark) {
      if (!document.body.classList.contains(CLASS_DARK)) {
        document.body.classList.add(CLASS_DARK);
      }
    } else {
      document.body.classList.remove(CLASS_DARK);
    }
    try { localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light'); } catch (e) {}
    updateToggleLabel();
    updateFooterToggleLabel();
  }

  function detectInitialTheme() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved === 'dark' || saved === 'light') return saved;
    } catch (e) {}
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  function bindToggleIfPresent() {
    var toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;
    toggle.addEventListener('click', function () {
      var isDark = document.body.classList.toggle(CLASS_DARK);
      try { localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light'); } catch (e) {}
      updateToggleLabel();
    });
    updateToggleLabel();
  }

  function bindFooterToggleIfPresent() {
    var footerToggle = document.getElementById('footerThemeToggle');
    if (!footerToggle) return;
    footerToggle.addEventListener('click', function () {
      var isDark = document.body.classList.toggle(CLASS_DARK);
      try { localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light'); } catch (e) {}
      updateFooterToggleLabel();
    });
    updateFooterToggleLabel();
  }

  function updateToggleLabel() {
    var toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;
    var isDark = document.body.classList.contains(CLASS_DARK);
    toggle.setAttribute('aria-pressed', String(isDark));

    // Prefer explicit data attribute to decide label style
    var wantsTextLabel = toggle.getAttribute('data-label') === 'text' || toggle.classList.contains('btn');
    if (wantsTextLabel) {
      toggle.textContent = isDark ? 'Light Mode' : 'Dark Mode';
    } else {
      toggle.textContent = isDark ? '☀️' : '🌙';
    }
    toggle.title = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  }

  function updateFooterToggleLabel() {
    var footerToggle = document.getElementById('footerThemeToggle');
    if (!footerToggle) return;
    var isDark = document.body.classList.contains(CLASS_DARK);
    footerToggle.setAttribute('aria-pressed', String(isDark));
    
    // Footer toggle always shows text labels
    footerToggle.innerHTML = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
    footerToggle.title = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  }

  // Initialize ASAP after DOM is ready
  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else { fn(); }
  }

  ready(function () {
    applyTheme(detectInitialTheme());
    bindToggleIfPresent();
    bindFooterToggleIfPresent();
  });
})();

