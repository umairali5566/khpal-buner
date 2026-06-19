// Main JavaScript for Khpal Buner

// Initialize favorites from localStorage
function getFavorites() {
    return JSON.parse(localStorage.getItem('favorites') || '[]');
}

function saveFavorites(favorites) {
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

// Compare functionality
function getCompareList() {
    return JSON.parse(localStorage.getItem('compare') || '[]');
}

function saveCompareList(list) {
    localStorage.setItem('compare', JSON.stringify(list));
}

// Format price with commas
function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function trackAnalyticsClick(trigger) {
    const url = trigger.dataset.analyticsUrl;
    const clickType = trigger.dataset.analyticsClick;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    if (!url || !clickType || !csrfToken) {
        return;
    }

    const data = new FormData();
    data.append('click_type', clickType);
    data.append('csrfmiddlewaretoken', csrfToken);

    if (navigator.sendBeacon && navigator.sendBeacon(url, data)) {
        return;
    }

    fetch(url, {
        method: 'POST',
        body: data,
        credentials: 'same-origin',
        keepalive: true,
    }).catch(() => {});
}

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.body.classList.toggle('navbar-open');
        });
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add custom validation if needed
        });
    });

    // Alert auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });

    // Responsive table handling
    const tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(table => {
        if (table.offsetWidth > window.innerWidth) {
            table.parentElement.classList.add('table-responsive');
        }
    });

    document.querySelectorAll('[data-analytics-click]').forEach(trigger => {
        trigger.addEventListener('click', function() {
            trackAnalyticsClick(this);
        });
    });

    document.querySelectorAll('.car-card[data-car-url]').forEach(card => {
        card.addEventListener('click', function(event) {
            if (event.target.closest('a, button')) {
                return;
            }
            window.location.href = this.dataset.carUrl;
        });
    });
});

// Add smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
