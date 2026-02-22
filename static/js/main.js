/**
 * Warm Hook Hugs — Main JavaScript
 * ==================================
 * Mobile menu, search, cookie consent, star rating, wishlist, autocomplete.
 */

document.addEventListener('DOMContentLoaded', () => {

    // ══════════════════════════════════════════
    // MOBILE MENU TOGGLE
    // ══════════════════════════════════════════
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // ══════════════════════════════════════════
    // SEARCH TOGGLE (Desktop)
    // ══════════════════════════════════════════
    const searchToggle = document.getElementById('search-toggle-btn');
    const searchDropdown = document.getElementById('search-dropdown');

    if (searchToggle && searchDropdown) {
        searchToggle.addEventListener('click', (e) => {
            e.preventDefault();
            searchDropdown.classList.toggle('open');
            if (searchDropdown.classList.contains('open')) {
                const input = searchDropdown.querySelector('input');
                if (input) input.focus();
            }
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!searchDropdown.contains(e.target) && !searchToggle.contains(e.target)) {
                searchDropdown.classList.remove('open');
            }
        });
    }

    // ══════════════════════════════════════════
    // SEARCH AUTOCOMPLETE
    // ══════════════════════════════════════════
    const searchInput = document.getElementById('search-input');
    const autocompleteContainer = document.getElementById('autocomplete-results');

    if (searchInput && autocompleteContainer) {
        let debounceTimer;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();

            if (query.length < 2) {
                autocompleteContainer.innerHTML = '';
                autocompleteContainer.classList.add('hidden');
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/search/autocomplete/?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            autocompleteContainer.innerHTML = data.results.map(item =>
                                `<a href="${item.url}">${item.name} <span class="text-stone-400 text-xs">in ${item.category}</span></a>`
                            ).join('');
                            autocompleteContainer.classList.remove('hidden');
                        } else {
                            autocompleteContainer.innerHTML = '<p class="px-4 py-3 text-sm text-stone-400">No results found</p>';
                            autocompleteContainer.classList.remove('hidden');
                        }
                    })
                    .catch(() => {
                        autocompleteContainer.classList.add('hidden');
                    });
            }, 300);
        });

        // Close autocomplete on blur (with delay for click registration)
        searchInput.addEventListener('blur', () => {
            setTimeout(() => { autocompleteContainer.classList.add('hidden'); }, 200);
        });
    }

    // ══════════════════════════════════════════
    // FADE-IN ON SCROLL
    // ══════════════════════════════════════════
    const fadeElements = document.querySelectorAll('.fade-in');
    if (fadeElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });

        fadeElements.forEach(el => observer.observe(el));
    }

    // ══════════════════════════════════════════
    // AUTO-DISMISS ALERT MESSAGES
    // ══════════════════════════════════════════
    const alerts = document.querySelectorAll('[role="alert"]');
    alerts.forEach(alert => {
        // Add enter animation
        alert.classList.add('toast-enter');

        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);

        // Dismiss on click of close button
        const closeBtn = alert.querySelector('[data-dismiss]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            });
        }
    });

    // ══════════════════════════════════════════
    // COOKIE CONSENT
    // ══════════════════════════════════════════
    const cookieBanner = document.getElementById('cookie-consent');

    if (cookieBanner && !localStorage.getItem('cookie_consent')) {
        setTimeout(() => { cookieBanner.classList.add('visible'); }, 1500);
    }

    window.acceptCookies = function () {
        localStorage.setItem('cookie_consent', 'accepted');
        if (cookieBanner) cookieBanner.classList.remove('visible');
    };

    window.declineCookies = function () {
        localStorage.setItem('cookie_consent', 'declined');
        if (cookieBanner) cookieBanner.classList.remove('visible');
        // Disable analytics cookies
        window['ga-disable-GA_MEASUREMENT_ID'] = true;
    };

    // ══════════════════════════════════════════
    // INTERACTIVE STAR RATING (Review Form)
    // ══════════════════════════════════════════
    const starContainer = document.getElementById('star-rating');
    const ratingInput = document.getElementById('rating-input');

    if (starContainer && ratingInput) {
        const stars = starContainer.querySelectorAll('.star-btn');

        stars.forEach(star => {
            star.addEventListener('click', (e) => {
                e.preventDefault();
                const value = star.dataset.value;
                ratingInput.value = value;

                // Update visual state
                stars.forEach(s => {
                    s.classList.toggle('active', parseInt(s.dataset.value) <= parseInt(value));
                });
            });

            star.addEventListener('mouseenter', () => {
                const value = star.dataset.value;
                stars.forEach(s => {
                    s.classList.toggle('active', parseInt(s.dataset.value) <= parseInt(value));
                });
            });
        });

        starContainer.addEventListener('mouseleave', () => {
            const currentVal = parseInt(ratingInput.value) || 0;
            stars.forEach(s => {
                s.classList.toggle('active', parseInt(s.dataset.value) <= currentVal);
            });
        });
    }

    // ══════════════════════════════════════════
    // WISHLIST TOGGLE (AJAX)
    // ══════════════════════════════════════════
    document.querySelectorAll('.wishlist-toggle-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const productId = btn.dataset.productId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                              getCookie('csrftoken');

            fetch(`/wishlist/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(res => res.json())
            .then(data => {
                if (data.added) {
                    btn.classList.add('text-red-500');
                    btn.classList.remove('text-stone-300');
                } else {
                    btn.classList.remove('text-red-500');
                    btn.classList.add('text-stone-300');
                }
                // Update wishlist count in nav
                const badge = document.getElementById('wishlist-count');
                if (badge && data.count !== undefined) {
                    badge.textContent = data.count;
                    badge.classList.toggle('hidden', data.count === 0);
                }
            })
            .catch(err => console.error('Wishlist toggle failed:', err));
        });
    });

    // ══════════════════════════════════════════
    // NEWSLETTER FORM (AJAX)
    // ══════════════════════════════════════════
    const nlForm = document.getElementById('newsletter-form');
    if (nlForm) {
        nlForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(nlForm);
            const csrfToken = formData.get('csrfmiddlewaretoken');

            fetch('/newsletter/subscribe/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData,
            })
            .then(res => {
                if (res.ok) {
                    nlForm.innerHTML = '<p class="text-sage font-medium">Thank you for subscribing! 💕</p>';
                }
            })
            .catch(() => {});
        });
    }

    // ══════════════════════════════════════════
    // IMAGE ZOOM (Product Detail)
    // ══════════════════════════════════════════
    const mainImage = document.getElementById('main-image');
    const imageContainer = document.getElementById('main-image-container');

    if (mainImage && imageContainer) {
        imageContainer.addEventListener('mousemove', (e) => {
            const rect = imageContainer.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            mainImage.style.transformOrigin = `${x}% ${y}%`;
            mainImage.style.transform = 'scale(1.5)';
        });

        imageContainer.addEventListener('mouseleave', () => {
            mainImage.style.transform = 'scale(1)';
        });
    }

    // ── Thumbnail gallery switch ──
    document.querySelectorAll('.thumb-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (mainImage) {
                mainImage.src = btn.dataset.src;
            }
        });
    });

});

// ══════════════════════════════════════════
// UTILITY: Get CSRF cookie
// ══════════════════════════════════════════
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
