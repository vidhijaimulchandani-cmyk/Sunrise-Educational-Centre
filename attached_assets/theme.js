// Simple dark mode manager with localStorage persistence (no auto-injection)
(function () {
  var STORAGE_KEY = 'preferredTheme';
  var CLASS_DARK = 'dark-mode';
  // Expose a lightweight flag so other scripts can detect a dedicated theme manager
  try { window.__THEME_MANAGER_ACTIVE__ = true; } catch (e) {}

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
    updateFooterSliderUI();
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
      updateFooterSliderUI();
    });
    updateFooterToggleLabel();
  }

  // Footer slider (UIverse style) support
  function bindFooterSliderIfPresent() {
    var slider = document.getElementById('footerThemeSlider');
    if (!slider) return;

    // Initialize checked state from current theme
    slider.checked = document.body.classList.contains(CLASS_DARK);

    slider.addEventListener('change', function () {
      var wantDark = !!slider.checked;
      var isDark = document.body.classList.contains(CLASS_DARK);
      if (wantDark !== isDark) {
        document.body.classList.toggle(CLASS_DARK, wantDark);
        try { localStorage.setItem(STORAGE_KEY, wantDark ? 'dark' : 'light'); } catch (e) {}
      }
      updateToggleLabel();
      updateFooterToggleLabel();
      updateFooterSliderUI();
    });

    updateFooterSliderUI();
  }

  function updateFooterSliderUI() {
    var slider = document.getElementById('footerThemeSlider');
    if (!slider) return;
    var isDark = document.body.classList.contains(CLASS_DARK);
    if (slider.checked !== isDark) slider.checked = isDark;
    // Optional: update aria state for accessibility
    slider.setAttribute('aria-pressed', String(isDark));
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
    bindFooterSliderIfPresent();
  });
})();

