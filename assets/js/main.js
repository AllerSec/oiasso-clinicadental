/* ============================================================
   Clínica Dental Oiasso — main.js
   Vanilla + GSAP (loaded via CDN before this file).
   ============================================================ */
(function () {
  'use strict';

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hasGSAP = typeof window.gsap !== 'undefined';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ----------------------------------------------------------
     0. Footer year
  ---------------------------------------------------------- */
  $$('[data-year]').forEach((el) => (el.textContent = new Date().getFullYear()));

  /* ----------------------------------------------------------
     1. Page loader — only the first visit per session
  ---------------------------------------------------------- */
  const loader = $('#loader');
  function dismissLoader() {
    if (!loader) return;
    loader.classList.add('is-leaving');
    setTimeout(() => { loader.hidden = true; }, 750);
  }
  if (loader) {
    const seen = sessionStorage.getItem('oiasso_seen') || /[?&]_test\b/.test(location.search);
    if (seen || prefersReduced) {
      loader.hidden = true;
    } else {
      sessionStorage.setItem('oiasso_seen', '1');
      document.documentElement.style.overflow = 'hidden';
      const finish = () => {
        document.documentElement.style.overflow = '';
        dismissLoader();
      };
      if (hasGSAP) {
        const path = $('.loader__draw', loader);
        const tl = gsap.timeline({ onComplete: finish });
        if (path) {
          const len = path.getTotalLength();
          gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
          tl.to(path, { strokeDashoffset: 0, duration: 1.1, ease: 'power2.inOut' });
        }
        tl.to({}, { duration: 0.25 });
      } else {
        setTimeout(finish, 1100);
      }
    }
  }

  /* ----------------------------------------------------------
     2. Header scrolled state
  ---------------------------------------------------------- */
  const header = $('.site-header');
  if (header) {
    const onScroll = () => header.setAttribute('data-scrolled', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ----------------------------------------------------------
     3. Mobile menu
  ---------------------------------------------------------- */
  const burger = $('.nav__burger');
  const mobileNav = $('.mobile-nav');
  function setMenu(open) {
    document.body.setAttribute('data-menu-open', open);
    if (burger) burger.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  }
  if (burger) {
    burger.addEventListener('click', () =>
      setMenu(document.body.getAttribute('data-menu-open') !== 'true')
    );
    $$('.mobile-nav__link, .mobile-nav__group a, .mobile-nav .btn').forEach((a) =>
      a.addEventListener('click', () => setMenu(false))
    );
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.body.getAttribute('data-menu-open') === 'true') setMenu(false);
    });
  }

  /* ----------------------------------------------------------
     4. Language switcher dropdown
  ---------------------------------------------------------- */
  const lang = $('.lang-switch');
  if (lang) {
    const btn = $('.lang-switch__btn', lang);
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = lang.getAttribute('data-open') === 'true';
      lang.setAttribute('data-open', !open);
      btn.setAttribute('aria-expanded', !open);
    });
    document.addEventListener('click', () => {
      lang.setAttribute('data-open', 'false');
      btn.setAttribute('aria-expanded', 'false');
    });
  }

  /* ----------------------------------------------------------
     4b. Nav dropdowns (hover via CSS; click/keyboard for touch & a11y)
  ---------------------------------------------------------- */
  const dropBtns = $$('.nav__drop-btn');
  dropBtns.forEach((b) => {
    const item = b.closest('.nav__has-drop');
    b.addEventListener('click', (e) => {
      e.preventDefault(); e.stopPropagation();
      const open = item.getAttribute('data-open') === 'true';
      // cerrar el resto
      $$('.nav__has-drop').forEach((i) => { i.setAttribute('data-open', 'false'); const bb = $('.nav__drop-btn', i); if (bb) bb.setAttribute('aria-expanded', 'false'); });
      item.setAttribute('data-open', String(!open));
      b.setAttribute('aria-expanded', String(!open));
    });
  });
  if (dropBtns.length) {
    document.addEventListener('click', () => {
      $$('.nav__has-drop').forEach((i) => { i.setAttribute('data-open', 'false'); const bb = $('.nav__drop-btn', i); if (bb) bb.setAttribute('aria-expanded', 'false'); });
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') $$('.nav__has-drop').forEach((i) => { i.setAttribute('data-open', 'false'); const bb = $('.nav__drop-btn', i); if (bb) bb.setAttribute('aria-expanded', 'false'); });
    });
  }

  /* ----------------------------------------------------------
     5. Before / After sliders
  ---------------------------------------------------------- */
  $$('.ba').forEach((ba) => {
    const after = $('.ba__after', ba);
    const handle = $('.ba__handle', ba);
    if (!after || !handle) return;
    let dragging = false;
    const setPos = (clientX) => {
      const r = ba.getBoundingClientRect();
      let pct = ((clientX - r.left) / r.width) * 100;
      pct = Math.max(2, Math.min(98, pct));
      after.style.clipPath = `inset(0 0 0 ${pct}%)`;
      handle.style.left = pct + '%';
    };
    const start = () => (dragging = true);
    const stop = () => (dragging = false);
    const move = (e) => {
      if (!dragging) return;
      setPos(e.touches ? e.touches[0].clientX : e.clientX);
    };
    ba.addEventListener('mousedown', (e) => { start(); setPos(e.clientX); });
    ba.addEventListener('touchstart', (e) => { start(); setPos(e.touches[0].clientX); }, { passive: true });
    window.addEventListener('mousemove', move);
    window.addEventListener('touchmove', move, { passive: true });
    window.addEventListener('mouseup', stop);
    window.addEventListener('touchend', stop);
    // keyboard
    ba.setAttribute('tabindex', '0');
    ba.setAttribute('role', 'slider');
    ba.setAttribute('aria-label', 'Comparador antes y después');
    ba.addEventListener('keydown', (e) => {
      const cur = parseFloat(handle.style.left) || 50;
      if (e.key === 'ArrowLeft') { const v = Math.max(2, cur - 4); after.style.clipPath = `inset(0 0 0 ${v}%)`; handle.style.left = v + '%'; }
      if (e.key === 'ArrowRight') { const v = Math.min(98, cur + 4); after.style.clipPath = `inset(0 0 0 ${v}%)`; handle.style.left = v + '%'; }
    });
  });

  /* ----------------------------------------------------------
     6. GSAP animations (skipped entirely under reduced motion)
  ---------------------------------------------------------- */
  if (hasGSAP && !prefersReduced) {
    gsap.registerPlugin(ScrollTrigger);
    document.documentElement.classList.add('js-anim');

    const mm = gsap.matchMedia();

    // Reveal on scroll — batched. Content is only pre-hidden when .js-anim is set,
    // so no-JS users always see it. A fallback guarantees nothing stays hidden.
    const revealItems = $$('[data-reveal]');
    const showReveal = (els) =>
      gsap.to(els, { opacity: 1, x: 0, y: 0, scale: 1, duration: 0.8, ease: 'power3.out', stagger: 0.08, overwrite: true });
    ScrollTrigger.batch('[data-reveal]', { start: 'top 90%', onEnter: (batch) => showReveal(batch) });
    // Immediately reveal anything already within/above the viewport on load.
    requestAnimationFrame(() => {
      const vh = window.innerHeight;
      revealItems.forEach((el) => { if (el.getBoundingClientRect().top < vh * 0.92) gsap.set(el, { opacity: 1, x: 0, y: 0, scale: 1 }); });
    });
    // Hard safety net: if a reveal never fires (e.g. tab hidden, ScrollTrigger error),
    // make sure content is visible after a few seconds.
    setTimeout(() => revealItems.forEach((el) => { if (parseFloat(getComputedStyle(el).opacity) < 0.1) gsap.set(el, { opacity: 1, x: 0, y: 0, scale: 1 }); }), 4000);

    // Hero choreography — uses gsap.from() so content stays visible if interrupted,
    // plus a hard fallback that clears any leftover inline styles.
    const heroTitle = $('.hero__title');
    if (heroTitle) {
      const words = $$('.hero__title .word, .hero__title .accent');
      const heroBits = $$('.hero__lead, .hero__cta, .hero__trust, .hero .pill, .hero__visual, .hero__badge');
      const tl = gsap.timeline({ delay: 0.15 });
      if (words.length) {
        tl.from(words, { yPercent: 115, opacity: 0, duration: 0.9, ease: 'power4.out', stagger: 0.08, clearProps: 'all' });
      }
      const underline = $('.hero__title .accent svg path');
      if (underline) {
        const len = underline.getTotalLength();
        gsap.set(underline, { strokeDasharray: len, strokeDashoffset: len });
        tl.to(underline, { strokeDashoffset: 0, duration: 0.7, ease: 'power2.out' }, '-=0.3');
      }
      tl.from('.hero .pill', { y: 16, opacity: 0, duration: 0.6, ease: 'power3.out', clearProps: 'all' }, 0);
      tl.from('.hero__lead, .hero__cta, .hero__trust', { y: 20, opacity: 0, duration: 0.7, ease: 'power3.out', stagger: 0.12, clearProps: 'all' }, '-=0.5');
      tl.from('.hero__visual', { scale: 0.92, opacity: 0, duration: 1, ease: 'power3.out', clearProps: 'all' }, '-=0.9');
      tl.from('.hero__badge', { y: 16, opacity: 0, scale: 0.9, duration: 0.6, ease: 'back.out(1.6)', stagger: 0.15, clearProps: 'all' }, '-=0.4');
      // safety net: never leave hero content hidden
      setTimeout(() => { heroBits.forEach((el) => { el.style.opacity = ''; el.style.transform = ''; }); gsap.set(words, { clearProps: 'all' }); }, 1600);
    }

    // Hero floating decorations parallax (desktop only)
    mm.add('(min-width: 880px)', () => {
      $$('.hero__deco svg').forEach((el, i) => {
        gsap.to(el, {
          y: (i % 2 ? 40 : -40), rotation: (i % 2 ? 12 : -12),
          ease: 'none',
          scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 },
        });
      });
      // hero photo subtle parallax
      gsap.to('.hero__photo img', {
        yPercent: 8, ease: 'none',
        scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 },
      });
    });

    // Animated counters
    $$('[data-count]').forEach((el) => {
      const target = parseFloat(el.getAttribute('data-count'));
      const obj = { v: 0 };
      ScrollTrigger.create({
        trigger: el, start: 'top 90%', once: true,
        onEnter: () =>
          gsap.to(obj, {
            v: target, duration: 1.6, ease: 'power2.out',
            onUpdate: () => {
              el.textContent = (el.getAttribute('data-suffix') === '%')
                ? Math.round(obj.v) + '%'
                : Math.round(obj.v) + (el.getAttribute('data-suffix') || '');
            },
          }),
      });
    });

    // Draw-on-scroll SVG icons
    $$('.draw-path').forEach((p) => {
      const len = p.getTotalLength();
      gsap.set(p, { strokeDasharray: len, strokeDashoffset: len });
      ScrollTrigger.create({
        trigger: p, start: 'top 88%', once: true,
        onEnter: () => gsap.to(p, { strokeDashoffset: 0, duration: 1.2, ease: 'power2.out' }),
      });
    });

    // Magnetic buttons (pointer, fine only)
    mm.add('(hover: hover) and (pointer: fine)', () => {
      $$('.magnetic').forEach((el) => {
        const strength = 0.3;
        const onMove = (e) => {
          const r = el.getBoundingClientRect();
          const x = (e.clientX - (r.left + r.width / 2)) * strength;
          const y = (e.clientY - (r.top + r.height / 2)) * strength;
          gsap.to(el, { x, y, duration: 0.4, ease: 'power3.out' });
        };
        const onLeave = () => gsap.to(el, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.4)' });
        el.addEventListener('mousemove', onMove);
        el.addEventListener('mouseleave', onLeave);
      });
    });

    // refresh after fonts settle
    document.fonts && document.fonts.ready.then(() => ScrollTrigger.refresh());
  }
})();
