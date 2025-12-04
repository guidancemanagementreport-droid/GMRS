// Mobile menu toggle with overlay
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;
    
    // Create mobile overlay if it doesn't exist
    let overlay = document.querySelector('.mobile-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'mobile-overlay';
        document.body.appendChild(overlay);
    }
    
    function openMenu() {
        hamburger.classList.add('active');
        navMenu.classList.add('active');
        overlay.classList.add('active');
        body.style.overflow = 'hidden'; // Prevent background scrolling
    }
    
    function closeMenu() {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        overlay.classList.remove('active');
        body.style.overflow = ''; // Restore scrolling
    }
    
    if (hamburger && navMenu) {
        // Toggle menu on hamburger click
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            if (navMenu.classList.contains('active')) {
                closeMenu();
            } else {
                openMenu();
            }
        });
        
        // Close menu when clicking overlay
        overlay.addEventListener('click', function() {
            closeMenu();
        });
        
        // Close menu when clicking a nav link (mobile)
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    closeMenu();
                }
            });
        });
        
        // Close menu on window resize if it becomes desktop view
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                closeMenu();
            }
        });
        
        // Close menu with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navMenu.classList.contains('active')) {
                closeMenu();
            }
        });
    }
    
    // Active tab management - Enhanced
    function setActiveTab() {
        const navLinks = document.querySelectorAll('.nav-menu a');
        const currentPath = window.location.pathname;
        const currentPathLower = currentPath.toLowerCase();
        
        // Remove active class from all links
        navLinks.forEach(link => {
            link.classList.remove('active');
        });
        
        // Find and set active link based on current URL
        navLinks.forEach(link => {
            const linkHref = link.getAttribute('href');
            if (!linkHref) return;
            
            try {
                // Handle absolute URLs
                const linkUrl = new URL(linkHref, window.location.origin);
                const linkPath = linkUrl.pathname.toLowerCase();
                
                // Exact match
                if (currentPathLower === linkPath) {
                    link.classList.add('active');
                    return;
                }
                
                // Check if current path starts with link path (for nested routes)
                if (linkPath !== '/' && currentPathLower.startsWith(linkPath)) {
                    link.classList.add('active');
                    return;
                }
            } catch (e) {
                // Handle relative URLs
                const normalizedHref = linkHref.toLowerCase();
                const normalizedPath = currentPathLower;
                
                // Match route patterns
                if (normalizedHref === normalizedPath) {
                    link.classList.add('active');
                    return;
                }
                
                // Match by route name patterns
                const routePatterns = {
                    'home': ['/', '/home'],
                    'about': ['/about'],
                    'guidance': ['/guidance-services', '/guidance'],
                    'anonymous': ['/anonymous', '/anonymous/report'],
                    'resources': ['/resources'],
                    'contact': ['/contact', '/crisis'],
                    'tracker': ['/report-tracker', '/tracker', '/track']
                };
                
                Object.keys(routePatterns).forEach(key => {
                    if (normalizedHref.includes(key) && routePatterns[key].some(pattern => normalizedPath.includes(pattern))) {
                        link.classList.add('active');
                    }
                });
            }
        });
        
        // Special handling for home page
        if (currentPath === '/' || currentPath === '' || currentPathLower.includes('home')) {
            navLinks.forEach(link => {
                const href = link.getAttribute('href') || '';
                const text = link.textContent.toLowerCase().trim();
                if (text === 'home' || href.includes('home') || href === '/') {
                    link.classList.add('active');
                }
            });
        }
    }
    
    // Set active tab on page load
    setActiveTab();
    
    // Update active tab when URL changes (for SPA-like behavior)
    let lastPath = window.location.pathname;
    setInterval(function() {
        if (window.location.pathname !== lastPath) {
            lastPath = window.location.pathname;
            setActiveTab();
        }
    }, 100);
    
    // Set active tab when clicking nav links
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active from all
            navLinks.forEach(l => l.classList.remove('active'));
            // Add active to clicked
            this.classList.add('active');
            
            // Store in sessionStorage for persistence
            try {
                sessionStorage.setItem('activeNav', this.href);
                sessionStorage.setItem('activeNavText', this.textContent.trim());
            } catch (e) {
                // Handle storage errors silently
            }
        });
    });
    
    // Restore active state from sessionStorage on page load
    try {
        const activeNavText = sessionStorage.getItem('activeNavText');
        if (activeNavText) {
            navLinks.forEach(link => {
                if (link.textContent.trim() === activeNavText) {
                    link.classList.add('active');
                }
            });
        }
    } catch (e) {
        // Handle storage errors
    }
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.style.borderColor = '#F44336';
        } else {
            field.style.borderColor = '';
        }
    });
    
    return isValid;
}

// Notification helper
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Auto-hide alerts
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

