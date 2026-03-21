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

openModalBtns.forEach(btn => {
  btn.addEventListener('click', () => orderModal?.classList.add('active'));
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
const orderForm = document.getElementById('order-form');
if (orderForm) {
  orderForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const btn = orderForm.querySelector('button[type="submit"]');
    btn.textContent = 'Request Sent!';
    btn.disabled = true;
    setTimeout(() => { orderModal.classList.remove('active'); btn.textContent = 'Send Request'; btn.disabled = false; orderForm.reset(); }, 1800);
  });
}
