/**
 * Shopping Cart and Checkout Logic
 */

async function updateItemQuantity(productId, newQty) {
  try {
    const res = await fetch('/api/cart/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, quantity: newQty })
    });
    const data = await res.json();
    if (data.success) {
      window.location.reload();
    }
  } catch (err) {
    showToast('Failed to update quantity', 'error');
  }
}

async function removeItemFromCart(productId) {
  if (!confirm('Are you sure you want to remove this item from your cart?')) return;

  try {
    const res = await fetch('/api/cart/remove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId })
    });
    const data = await res.json();
    if (data.success) {
      showToast('Item removed from cart', 'info');
      setTimeout(() => window.location.reload(), 300);
    }
  } catch (err) {
    showToast('Failed to remove item', 'error');
  }
}

async function applyCouponCode(code = null) {
  const input = document.getElementById('coupon-input');
  const couponCode = code || (input ? input.value.trim() : '');

  if (!couponCode) {
    showToast('Please enter a coupon code', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/coupons/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: couponCode })
    });
    const data = await res.json();

    if (data.success) {
      showToast(data.message, 'success');
      // Reload with coupon param
      const url = new URL(window.location.href);
      url.searchParams.set('coupon', couponCode);
      window.location.href = url.toString();
    } else {
      showToast(data.message, 'error');
    }
  } catch (err) {
    showToast('Failed to apply coupon', 'error');
  }
}

function removeCouponCode() {
  const url = new URL(window.location.href);
  url.searchParams.delete('coupon');
  window.location.href = url.toString();
}

// Simulated Order Placement
async function handlePlaceOrder(event) {
  event.preventDefault();
  const form = document.getElementById('checkout-form');
  const submitBtn = document.getElementById('place-order-btn');

  // Verify address selection
  const selectedAddress = form.querySelector('input[name="address_id"]:checked');
  if (!selectedAddress && !document.getElementById('new-address-form-wrapper')) {
    showToast('Please select or add a delivery address', 'warning');
    return;
  }

  const paymentMethod = form.querySelector('input[name="payment_method"]:checked')?.value || 'UPI';
  const deliverySlot = form.querySelector('input[name="delivery_slot"]:checked')?.value || 'Standard Delivery (24-48 Hours)';
  const couponCode = new URLSearchParams(window.location.search).get('coupon') || null;

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing Secure Payment...';

  const payload = {
    payment_method: paymentMethod,
    delivery_slot: deliverySlot,
    coupon_code: couponCode,
    address_id: selectedAddress ? selectedAddress.value : null
  };

  // If new address form filled
  const newAddrName = document.getElementById('addr-name');
  if (newAddrName && newAddrName.value.trim()) {
    payload.address_data = {
      full_name: document.getElementById('addr-name').value.trim(),
      phone: document.getElementById('addr-phone').value.trim(),
      pincode: document.getElementById('addr-pincode').value.trim(),
      address_line1: document.getElementById('addr-line1').value.trim(),
      address_line2: document.getElementById('addr-line2')?.value.trim() || '',
      city: document.getElementById('addr-city').value.trim(),
      state: document.getElementById('addr-state').value.trim(),
      address_type: document.getElementById('addr-type')?.value || 'Home',
      is_default: true
    };
  }

  try {
    const res = await fetch('/api/orders/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.success) {
      showToast('Order placed successfully! Redirecting...', 'success');
      setTimeout(() => {
        window.location.href = `/order/${data.order_number}`;
      }, 1000);
    } else {
      showToast(data.message || 'Order failed', 'error');
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Place Order & Pay';
    }
  } catch (err) {
    showToast('An error occurred during payment processing', 'error');
    submitBtn.disabled = false;
    submitBtn.innerHTML = 'Place Order & Pay';
  }
}

