(function () {
  'use strict';

  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');
  const header = document.getElementById('header');
  const contactForm = document.getElementById('contact-form');
  const formFeedback = document.getElementById('form-feedback');
  const submitBtn = document.getElementById('submit-btn');

  // Mobile nav toggle
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navToggle.classList.toggle('active');
      navMenu.classList.toggle('open');
    });
  }

  // Close mobile nav on link click
  navLinks.forEach((link) => {
    link.addEventListener('click', () => {
      navToggle?.classList.remove('active');
      navMenu?.classList.remove('open');
    });
  });

  // Active nav link on scroll
  const sections = document.querySelectorAll('section[id]');

  function updateActiveNav() {
    const scrollY = window.scrollY + 100;

    sections.forEach((section) => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');

      if (scrollY >= top && scrollY < top + height) {
        navLinks.forEach((link) => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }

  window.addEventListener('scroll', updateActiveNav);
  updateActiveNav();

  // Header shadow on scroll
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      header?.style.boxShadow = '0 2px 20px rgba(10, 79, 85, 0.08)';
    } else {
      header.style.boxShadow = 'none';
    }
  });

  // Fade-in animation on scroll
  const fadeElements = document.querySelectorAll(
    '.section-title, .about-grid, .skills-grid, .timeline-item, .project-card, .edu-block, .contact-grid'
  );

  fadeElements.forEach((el) => el.classList.add('fade-in'));

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
  );

  fadeElements.forEach((el) => observer.observe(el));

  // Contact form submission
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const message = document.getElementById('message').value.trim();

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';
      formFeedback.hidden = true;

      try {
        const response = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, message }),
        });

        const data = await response.json();

        formFeedback.hidden = false;
        formFeedback.className = 'form-feedback ' + (data.success ? 'success' : 'error');
        formFeedback.textContent = data.message || data.error || 'Something went wrong.';

        if (data.success) {
          contactForm.reset();
        }
      } catch {
        formFeedback.hidden = false;
        formFeedback.className = 'form-feedback error';
        formFeedback.textContent = 'Network error. Please try again later.';
      }

      submitBtn.disabled = false;
      submitBtn.textContent = 'Send Message';
    });
  }

})();
