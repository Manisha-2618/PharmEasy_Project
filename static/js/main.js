/**
 * PharmEasy Main Frontend JavaScript
 * Handles search suggestions, pincode modal, toast notifications, and global UI.
 */

// Global Toast Notification Helper
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'fa-check-circle';
  if (type === 'error') icon = 'fa-exclamation-circle';
  if (type === 'warning') icon = 'fa-exclamation-triangle';

  toast.innerHTML = `
    <i class="fas ${icon}" style="color: ${type === 'success' ? '#10847e' : (type === 'error' ? '#ef4444' : '#f59e0b')}; font-size: 18px;"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Global Add to Cart Handler
async function handleAddToCart(productId, quantity = 1, buttonElement = null) {
  if (buttonElement) {
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
  }

  try {
    const res = await fetch('/api/cart/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, quantity: quantity })
    });
    const data = await res.json();

    if (data.success) {
      showToast('Item added to your cart!', 'success');
      // Update header badge
      const cartBadges = document.querySelectorAll('.cart-badge');
      cartBadges.forEach(b => {
        b.textContent = data.cart_count;
        b.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
      });

      if (buttonElement) {
        buttonElement.innerHTML = '<i class="fas fa-check"></i> Added';
        buttonElement.style.background = '#10847e';
        buttonElement.style.color = '#ffffff';
        setTimeout(() => {
          buttonElement.disabled = false;
          buttonElement.innerHTML = '<i class="fas fa-shopping-basket"></i> Add to Cart';
          buttonElement.style.background = '#ffffff';
          buttonElement.style.color = '#10847e';
        }, 1500);
      }
    } else {
      showToast(data.message || 'Could not add item', 'error');
      if (buttonElement) {
        buttonElement.disabled = false;
        buttonElement.innerHTML = '<i class="fas fa-shopping-basket"></i> Add to Cart';
      }
    }
  } catch (err) {
    showToast('Failed to update cart. Please try again.', 'error');
    if (buttonElement) {
      buttonElement.disabled = false;
      buttonElement.innerHTML = '<i class="fas fa-shopping-basket"></i> Add to Cart';
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // 1. Search Auto-complete
  const searchInput = document.getElementById('header-search-input');
  const suggestionsBox = document.getElementById('search-suggestions');

  if (searchInput && suggestionsBox) {
    let debounceTimer;

    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();

      if (query.length < 2) {
        suggestionsBox.style.display = 'none';
        suggestionsBox.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
          const items = await res.json();

          if (items.length > 0) {
            suggestionsBox.innerHTML = items.map(item => `
              <div class="search-suggestion-item" onclick="window.location.href='/product/${item.slug}'">
                <img src="${item.image_url || '/static/images/pharmeasy-placeholder.png'}" alt="${item.name}" class="search-suggestion-thumb" />
                <div class="search-suggestion-info">
                  <div class="search-suggestion-name">${item.name}</div>
                  <div class="search-suggestion-price">₹${item.price.toFixed(2)} <span style="text-decoration: line-through; color: #8897a2; font-size: 11px;">₹${item.mrp.toFixed(2)}</span></div>
                </div>
                <i class="fas fa-chevron-right" style="color: #cbd5e1; font-size: 11px;"></i>
              </div>
            `).join('') + `
              <div class="search-suggestion-item" style="background: #f8fafc; justify-content: center; font-weight: 700; color: #10847e;" onclick="document.getElementById('header-search-form').submit()">
                See all results for "${query}" <i class="fas fa-arrow-right" style="margin-left: 6px;"></i>
              </div>
            `;
            suggestionsBox.style.display = 'block';
          } else {
            suggestionsBox.style.display = 'none';
          }
        } catch (err) {
          suggestionsBox.style.display = 'none';
        }
      }, 250);
    });

    // Close suggestions on outside click
    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        suggestionsBox.style.display = 'none';
      }
    });
  }

  // 2. Pincode Modal Handling
  const pincodePicker = document.getElementById('pincode-picker-btn');
  const pincodeModal = document.getElementById('pincode-modal');
  const pincodeClose = document.getElementById('pincode-modal-close');
  const pincodeForm = document.getElementById('pincode-form');

  if (pincodePicker && pincodeModal) {
    pincodePicker.addEventListener('click', () => {
      pincodeModal.classList.add('active');
    });

    if (pincodeClose) {
      pincodeClose.addEventListener('click', () => {
        pincodeModal.classList.remove('active');
      });
    }

    pincodeModal.addEventListener('click', (e) => {
      if (e.target === pincodeModal) {
        pincodeModal.classList.remove('active');
      }
    });

    if (pincodeForm) {
      pincodeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('modal-pincode-input');
        const pin = input.value.trim();

        if (pin.length !== 6 || isNaN(pin)) {
          showToast('Please enter a valid 6-digit Indian PIN code.', 'warning');
          return;
        }

        // Quick city lookup demo
        let city = 'New Delhi';
        if (pin.startsWith('400')) city = 'Mumbai';
        else if (pin.startsWith('560')) city = 'Bengaluru';
        else if (pin.startsWith('700')) city = 'Kolkata';
        else if (pin.startsWith('600')) city = 'Chennai';
        else if (pin.startsWith('500')) city = 'Hyderabad';
        else if (pin.startsWith('380')) city = 'Ahmedabad';
        else if (pin.startsWith('411')) city = 'Pune';

        try {
          const res = await fetch('/api/pincode/set', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pincode: pin, city: city })
          });
          const data = await res.json();
          if (data.success) {
            document.querySelectorAll('.pincode-value').forEach(el => el.textContent = `${pin} ${city}`);
            pincodeModal.classList.remove('active');
            showToast(`Delivery location set to ${city} (${pin})`, 'success');
          } else {
            showToast(data.message, 'error');
          }
        } catch (err) {
          showToast('Failed to update pincode', 'error');
        }
      });
    }
  }

  // Quick select pincodes in modal
  document.querySelectorAll('.quick-pincode-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const pin = chip.getAttribute('data-pin');
      const city = chip.getAttribute('data-city');
      const input = document.getElementById('modal-pincode-input');
      if (input) {
        input.value = pin;
        if (pincodeForm) pincodeForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  // Deals of the day countdown timer
  const timerElement = document.getElementById('deals-countdown');
  if (timerElement) {
    let hours = 5, minutes = 42, seconds = 19;
    setInterval(() => {
      if (seconds > 0) {
        seconds--;
      } else {
        seconds = 59;
        if (minutes > 0) {
          minutes--;
        } else {
          minutes = 59;
          if (hours > 0) hours--;
        }
      }
      const pad = (n) => n.toString().padStart(2, '0');
      timerElement.textContent = `Ends in ${pad(hours)}h : ${pad(minutes)}m : ${pad(seconds)}s`;
    }, 1000);
  }
});

