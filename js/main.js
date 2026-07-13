/**
 * GARASTOR — main.js
 * Hamburger menu, mobile menu, header scroll, form validation
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── HAMBURGER MENU ──
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', function () {
      hamburger.classList.toggle('active');
      mobileMenu.classList.toggle('active');
      document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    });

    // Close menu when clicking a link
    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
      });
    });

    // Close menu on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  // ── HEADER SCROLL ──
  const header = document.querySelector('.site-header');
  if (header) {
    let lastScroll = 0;
    window.addEventListener('scroll', function () {
      const now = window.pageYOffset;
      if (now > 80 && now > lastScroll) {
        header.style.transform = 'translateY(-100%)';
      } else {
        header.style.transform = 'translateY(0)';
      }
      lastScroll = now;
    });
  }

  // ── SMOOTH SCROLL FOR ANCHOR LINKS ──
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var id = this.getAttribute('href');
      if (id === '#') return;
      var target = document.querySelector(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── CONTACT FORM ──
  var contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = (document.getElementById('name') || {}).value || '';
      var email = (document.getElementById('email') || {}).value || '';
      if (!name || !email) {
        alert('Please fill in your name and email.');
        return;
      }
      // Simple email validation
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        alert('Please enter a valid email address.');
        return;
      }
      alert('Thank you, ' + name + '. Your message has been received. We will contact you shortly.');
      contactForm.reset();
    });
  }

  // ── PRODUCT GALLERY (for products.html — simplified fallback) ──
  var productImages = document.querySelectorAll('.prod-thumb-img');
  if (productImages.length > 0) {
    // The inline script in products.html handles the main gallery logic;
    // this is a minimal enhancement
    productImages.forEach(function (container) {
      var img = container.querySelector('img');
      if (!img) return;
      container.style.cursor = 'pointer';
    });
  }

});