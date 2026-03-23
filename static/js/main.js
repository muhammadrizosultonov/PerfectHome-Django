// ---- NAVBAR SCROLL ----
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 30);
});

// ---- MOBILE MENU ----
const menuBtn = document.getElementById('menu-btn');
const menuClose = document.getElementById('menu-close');
const mobileMenu = document.getElementById('mobile-menu');

if (menuBtn) menuBtn.addEventListener('click', () => mobileMenu.classList.add('open'));
if (menuClose) menuClose.addEventListener('click', () => mobileMenu.classList.remove('open'));

// ---- LANGUAGE SWITCHER ----
document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

// ---- ORDER MODAL ----
const orderModal = document.getElementById('order-modal');
const openModalBtns = document.querySelectorAll('[data-open-modal]');
const closeModalBtn = document.getElementById('close-modal');
const orderForm = document.getElementById('order-form');
const orderFormStatus = document.getElementById('order-form-status');

openModalBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const orderUrl = btn.getAttribute('data-order-url');
    if (orderForm && orderUrl) {
      orderForm.setAttribute('action', orderUrl);
    }
    if (orderFormStatus) orderFormStatus.textContent = '';
    orderModal?.classList.add('active');
  });
});
if (closeModalBtn) closeModalBtn.addEventListener('click', () => orderModal.classList.remove('active'));
if (orderModal) {
  orderModal.addEventListener('click', (e) => {
    if (e.target === orderModal) orderModal.classList.remove('active');
  });
}

// ---- ESC TO CLOSE MODAL ----
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') orderModal?.classList.remove('active');
});

// ---- PRODUCT GALLERY THUMBNAILS ----
const mainImg = document.getElementById('main-product-img');
const thumbs = document.querySelectorAll('.thumb-img');
thumbs.forEach(thumb => {
  thumb.addEventListener('click', () => {
    if (mainImg) mainImg.src = thumb.src;
    thumbs.forEach(t => t.classList.remove('active'));
    thumb.classList.add('active');
  });
});

// ---- BRAND SEARCH ----
const brandSearch = document.getElementById('brand-search');
const brandCards = document.querySelectorAll('.brand-item');
if (brandSearch) {
  brandSearch.addEventListener('input', () => {
    const q = brandSearch.value.toLowerCase();
    brandCards.forEach(card => {
      const name = card.getAttribute('data-name')?.toLowerCase() || '';
      card.style.display = name.includes(q) ? '' : 'none';
    });
  });
}

// ---- SCROLL REVEAL ----
const revealEls = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('fade-up');
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });
revealEls.forEach(el => observer.observe(el));

// ---- LOAD MORE ----
const loadMoreBtn = document.getElementById('load-more');
if (loadMoreBtn) {
  loadMoreBtn.addEventListener('click', () => {
    loadMoreBtn.textContent = 'Loading...';
    setTimeout(() => { loadMoreBtn.textContent = 'No more products'; loadMoreBtn.disabled = true; }, 1200);
  });
}

// ---- CONTACT FORM ----
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = contactForm.querySelector('button[type="submit"]');
    btn.textContent = 'Sent!';
    btn.disabled = true;
    setTimeout(() => { btn.textContent = 'Send Message'; btn.disabled = false; contactForm.reset(); }, 2500);
  });
}

// ---- ORDER FORM ----
if (orderForm) {
  orderForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const action = orderForm.getAttribute('action');
    if (!action) {
      if (orderFormStatus) orderFormStatus.textContent = 'Order URL is missing.';
      return;
    }

    const btn = orderForm.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Sending...';
    btn.disabled = true;

    try {
      const response = await fetch(action, {
        method: 'POST',
        body: new FormData(orderForm),
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      const data = await response.json().catch(() => ({}));

      if (response.ok && data.ok) {
        if (orderFormStatus) orderFormStatus.textContent = data.message || 'Request sent.';
        setTimeout(() => {
          orderModal?.classList.remove('active');
          orderForm.reset();
          if (orderFormStatus) orderFormStatus.textContent = '';
        }, 1400);
      } else {
        if (orderFormStatus) orderFormStatus.textContent = data.error || 'Invalid request.';
      }
    } catch (err) {
      if (orderFormStatus) orderFormStatus.textContent = 'Network error. Please try again.';
    } finally {
      btn.textContent = originalText;
      btn.disabled = false;
    }
  });
}
