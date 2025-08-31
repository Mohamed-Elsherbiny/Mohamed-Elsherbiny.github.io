// Enhanced JS: nav toggle, smooth scroll, reveal on scroll, nav shrink on scroll, iframe load
document.addEventListener('DOMContentLoaded', function() {
  var toggle = document.getElementById('nav-toggle');
  var links = document.getElementById('nav-links');
  var topnav = document.querySelector('.topnav');

  if (toggle) {
    toggle.addEventListener('click', function() {
      links.classList.toggle('show');
    });
  }

  // Smooth scrolling for internal links
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        links.classList.remove('show');
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Nav shrink / scrolled class
  function onScroll() {
    if (window.scrollY > 24) topnav.classList.add('scrolled'); else topnav.classList.remove('scrolled');
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Reveal elements on scroll (cards, profile)
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.card, .profile-card, .hero, .embed-frame').forEach(function(el) {
    el.classList.add('reveal');
    observer.observe(el);
  });

  // Fade in iframe in blog page (if present)
  document.querySelectorAll('iframe').forEach(function(iframe) {
    iframe.addEventListener('load', function() { iframe.classList.add('loaded'); });
  });

});
