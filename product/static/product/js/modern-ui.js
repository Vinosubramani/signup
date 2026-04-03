// Sweet Dreams Bakery - Modern UI JavaScript Utilities

class SweetDreamsUI {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupToastNotifications();
        this.setupImageLazyLoading();
        this.setupSmoothScrolling();
    }

    // Get CSRF token for Django
    getCookie(name) {
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

    // Toast Notifications
    showToast(message, type = 'success', duration = 3000) {
        // Remove existing toast
        const existingToast = document.querySelector('.toast-modern');
        if (existingToast) {
            existingToast.remove();
        }

        // Create new toast
        const toast = document.createElement('div');
        toast.className = `toast-modern ${type === 'error' ? 'toast-error' : 'toast-success'}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span>${type === 'success' ? '✅' : '❌'}</span>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Hide toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // Wishlist functionality
    async toggleWishlist(productId, button) {
        const originalContent = button.innerHTML;
        button.innerHTML = '<div class="loading-spinner"></div>';
        button.disabled = true;

        try {
            const response = await fetch(`/wishlist/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();
            
            if (response.ok) {
                button.innerHTML = data.is_wishlisted ? '♥' : '♡';
                button.style.color = data.is_wishlisted ? 'var(--soft-coral)' : '';
                
                // Update wishlist count if element exists
                const wishlistCount = document.getElementById('wishlist-count');
                if (wishlistCount) {
                    wishlistCount.textContent = data.wishlist_count || 0;
                }
                
                // Success animation
                button.style.transform = 'scale(1.3)';
                setTimeout(() => {
                    button.style.transform = 'scale(1)';
                }, 200);
                
                // Show toast
                const message = data.is_wishlisted ? 'Added to wishlist! ❤️' : 'Removed from wishlist';
                this.showToast(message);
            } else {
                throw new Error('Failed to update wishlist');
            }
        } catch (error) {
            button.innerHTML = originalContent;
            this.showToast('Something went wrong!', 'error');
            console.error('Wishlist error:', error);
        } finally {
            button.disabled = false;
        }
    }

    // Share functionality
    shareProduct(productName, productUrl) {
        if (navigator.share) {
            navigator.share({
                title: productName,
                text: `Check out this delicious ${productName} from Sweet Dreams Bakery!`,
                url: productUrl
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(productUrl).then(() => {
                this.showToast('Product link copied to clipboard! 📋');
            }).catch(() => {
                this.showToast('Unable to copy link', 'error');
            });
        }
    }

    // Scroll animations
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        // Observe elements with animation classes
        document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right').forEach(el => {
            observer.observe(el);
        });
    }

    // Toast notification system
    setupToastNotifications() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
    }

    // Lazy loading for images
    setupImageLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // Smooth scrolling
    setupSmoothScrolling() {
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
    }

    // Product filtering
    filterProducts(type) {
        const grid = document.querySelector('#product-grid, .row');
        if (!grid) return;

        const products = Array.from(grid.children);
        
        // Sort products based on filter type
        switch(type) {
            case 'low-price':
                products.sort((a, b) => parseFloat(a.dataset.price) - parseFloat(b.dataset.price));
                break;
            case 'high-price':
                products.sort((a, b) => parseFloat(b.dataset.price) - parseFloat(a.dataset.price));
                break;
            case 'popular':
                // Sort by product name containing popular keywords
                products.sort((a, b) => {
                    const aName = a.querySelector('.card-title, h5, h6')?.textContent.toLowerCase() || '';
                    const bName = b.querySelector('.card-title, h5, h6')?.textContent.toLowerCase() || '';
                    const popularKeywords = ['chocolate', 'red velvet', 'vanilla', 'strawberry'];
                    
                    const aScore = popularKeywords.reduce((score, keyword) => 
                        aName.includes(keyword) ? score + 1 : score, 0);
                    const bScore = popularKeywords.reduce((score, keyword) => 
                        bName.includes(keyword) ? score + 1 : score, 0);
                    
                    return bScore - aScore;
                });
                break;
            default:
                // Keep original order
                break;
        }
        
        // Re-append sorted products with animation
        products.forEach((product, index) => {
            product.style.opacity = '0';
            product.style.transform = 'translateY(20px)';
            grid.appendChild(product);
            
            setTimeout(() => {
                product.style.transition = 'all 0.3s ease';
                product.style.opacity = '1';
                product.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    // Search functionality with debouncing
    setupSearch(inputSelector, resultsSelector, searchUrl) {
        const searchInput = document.querySelector(inputSelector);
        const resultsContainer = document.querySelector(resultsSelector);
        
        if (!searchInput || !resultsContainer) return;

        let debounceTimer;
        
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                resultsContainer.innerHTML = '';
                return;
            }
            
            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(`${searchUrl}?search=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    this.displaySearchResults(data, resultsContainer);
                } catch (error) {
                    console.error('Search error:', error);
                }
            }, 300);
        });
    }

    // Display search results
    displaySearchResults(results, container) {
        if (!results || results.length === 0) {
            container.innerHTML = '<p class="text-center text-muted">No results found</p>';
            return;
        }

        const html = results.map(product => `
            <div class="search-result-item" onclick="window.location.href='/product/${product.id}/'">
                <img src="${product.image || '/static/placeholder.jpg'}" alt="${product.name}" class="search-result-image">
                <div class="search-result-info">
                    <h6>${product.name}</h6>
                    <p class="text-muted">₹${product.price}</p>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Form validation
    validateForm(formSelector, rules) {
        const form = document.querySelector(formSelector);
        if (!form) return false;

        let isValid = true;
        const errors = {};

        Object.keys(rules).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            const rule = rules[fieldName];
            
            if (!field) return;

            // Clear previous errors
            field.classList.remove('is-invalid');
            const errorElement = field.parentNode.querySelector('.invalid-feedback');
            if (errorElement) errorElement.remove();

            // Validate field
            if (rule.required && !field.value.trim()) {
                errors[fieldName] = rule.required;
                isValid = false;
            } else if (rule.pattern && !rule.pattern.test(field.value)) {
                errors[fieldName] = rule.patternMessage || 'Invalid format';
                isValid = false;
            } else if (rule.minLength && field.value.length < rule.minLength) {
                errors[fieldName] = `Minimum ${rule.minLength} characters required`;
                isValid = false;
            }

            // Display error
            if (errors[fieldName]) {
                field.classList.add('is-invalid');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = errors[fieldName];
                field.parentNode.appendChild(errorDiv);
            }
        });

        return isValid;
    }

    // Loading states
    showLoading(element, text = 'Loading...') {
        const originalContent = element.innerHTML;
        element.dataset.originalContent = originalContent;
        element.innerHTML = `
            <div class="loading-spinner"></div>
            <span style="margin-left: 10px;">${text}</span>
        `;
        element.disabled = true;
    }

    hideLoading(element) {
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
        element.disabled = false;
    }
}

// Initialize the UI system
const sweetDreamsUI = new SweetDreamsUI();

// Global functions for backward compatibility
window.toggleWishlist = (productId, button) => sweetDreamsUI.toggleWishlist(productId, button);
window.shareProduct = (name, url) => sweetDreamsUI.shareProduct(name, url);
window.showToast = (message, type) => sweetDreamsUI.showToast(message, type);
window.filterProducts = (type) => sweetDreamsUI.filterProducts(type);

// Smooth scroll function
window.scrollToProducts = () => {
    const element = document.getElementById('products');
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SweetDreamsUI;
}