/* Universität Nordlicht – Demo-Interaktionen (kein Framework, keine Abhängigkeiten) */
(() => {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

  /* ---------- Header: Schatten beim Scrollen ---------- */
  const header = $('.site-header');
  const onScroll = () => header.classList.toggle('is-scrolled', window.scrollY > 8);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Mobile Navigation ---------- */
  const nav = $('#main-nav');
  const navToggle = $('.nav-toggle');
  const setNav = open => {
    nav.classList.toggle('is-open', open);
    navToggle.setAttribute('aria-expanded', String(open));
  };
  navToggle.addEventListener('click', () => {
    const open = navToggle.getAttribute('aria-expanded') !== 'true';
    setNav(open);
    if (open) $('a', nav).focus(); // Fokusreihenfolge: Menü steht im DOM vor dem Toggle
  });
  nav.addEventListener('click', e => { if (e.target.closest('a')) setNav(false); });
  // Menü schließen, wenn der Fokus es verlässt (Tab aus dem letzten Link) oder wenn die Desktop-Navigation greift
  document.addEventListener('focusin', e => {
    if (navToggle.getAttribute('aria-expanded') === 'true' && !nav.contains(e.target) && e.target !== navToggle) setNav(false);
  });
  window.matchMedia('(min-width: 1171px)').addEventListener('change', e => { if (e.matches) setNav(false); });

  /* ---------- Suche ---------- */
  const searchToggle = $('#search-toggle');
  const searchForm = $('#site-search');
  const searchInput = $('#q');
  const searchStatus = $('.site-search__status');
  const setSearch = open => {
    searchForm.hidden = !open;
    searchToggle.setAttribute('aria-expanded', String(open));
    if (open) searchInput.focus();
  };
  searchToggle.addEventListener('click', () => setSearch(searchForm.hidden));
  searchForm.addEventListener('submit', e => {
    e.preventDefault();
    const q = searchInput.value.trim();
    searchStatus.textContent = q
      ? `Demo: Die Suche nach „${q}“ ist in dieser Vorschau nicht angebunden.`
      : 'Bitte einen Suchbegriff eingeben.';
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (!searchForm.hidden) { setSearch(false); searchToggle.focus(); }
    if (navToggle.getAttribute('aria-expanded') === 'true') { setNav(false); navToggle.focus(); }
  });

  /* ---------- Aktive Navigation ---------- */
  const navLinks = $$('.main-nav__list a[href^="#"]:not(.btn)');
  const sections = navLinks.map(a => $(a.getAttribute('href'))).filter(Boolean);
  if ('IntersectionObserver' in window) {
    const spy = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        navLinks.forEach(a => {
          const on = a.getAttribute('href') === '#' + en.target.id;
          a.classList.toggle('is-active', on);
          if (on) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(s => spy.observe(s));
  }

  /* ---------- Scroll-Reveal ---------- */
  const revealEls = $$('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion.matches) {
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-visible');
        obs.unobserve(en.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    // Geschwister gestaffelt einblenden
    $$('ul, .campus-grid, .stats__grid').forEach(list => {
      $$(':scope > [data-reveal]', list).forEach((el, i) => el.style.setProperty('--d', `${i * 90}ms`));
    });
    revealEls.forEach(el => io.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('is-visible'));
  }

  /* ---------- Zähler ---------- */
  const counters = $$('[data-count]');
  const fmt = el => new Intl.NumberFormat(el.dataset.locale || 'de-DE');
  const render = (el, value) => { el.textContent = fmt(el).format(Math.round(value)) + (el.dataset.suffix || ''); };
  const countUp = el => {
    const target = Number(el.dataset.count);
    if (reduceMotion.matches) return render(el, target);
    const start = performance.now(), dur = 1600;
    const tick = now => {
      const t = Math.min(1, (now - start) / dur);
      render(el, target * (1 - Math.pow(1 - t, 4)));
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  if ('IntersectionObserver' in window && !reduceMotion.matches) {
    const cio = new IntersectionObserver((entries, obs) => {
      entries.forEach(en => { if (en.isIntersecting) { countUp(en.target); obs.unobserve(en.target); } });
    }, { threshold: 0.6 });
    counters.forEach(el => { render(el, 0); cio.observe(el); });
  }

  /* ---------- 3D-Tilt der Karten ---------- */
  if (finePointer.matches && !reduceMotion.matches) {
    $$('.tilt').forEach(card => {
      const max = card.matches('.quick__card, .campus-tile--big') ? 7 : 10;
      card.addEventListener('pointermove', e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        card.classList.add('is-tilting');
        card.style.setProperty('--rx', `${(x * max * 2).toFixed(2)}deg`);
        card.style.setProperty('--ry', `${(-y * max * 2).toFixed(2)}deg`);
      });
      card.addEventListener('pointerleave', () => {
        card.classList.remove('is-tilting');
        card.style.setProperty('--rx', '0deg');
        card.style.setProperty('--ry', '0deg');
      });
    });
  }

  /* ---------- Hero: Parallax für den Würfel ---------- */
  const hero = $('.hero');
  const scene = $('.hero__scene');
  const parallax = !reduceMotion.matches;

  /* ---------- Hero-Canvas: 3D-Partikelnetz ---------- */
  const canvas = $('#hero-canvas');
  const ctx = canvas.getContext('2d');
  const MAX_PTS = 130;
  const pts = Array.from({ length: MAX_PTS }, () => ({
    x: (Math.random() - 0.5) * 2, y: (Math.random() - 0.5) * 2, z: (Math.random() - 0.5) * 2,
    hue: Math.random() < 0.6 ? 172 : 250 // Teal oder Indigo
  }));
  const LINK = 150, BUCKETS = 6;
  let W = 0, H = 0, dpr = 1, n = MAX_PTS, rotY = 0, rotX = 0.25, tY = 0, tX = 0;
  let rafId = 0, visible = true, resizeTimer = 0;

  const resize = () => {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.clientWidth; H = canvas.clientHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    n = W < 700 ? 70 : MAX_PTS;
  };

  const project = p => {
    const cy = Math.cos(rotY), sy = Math.sin(rotY), cx = Math.cos(rotX), sx = Math.sin(rotX);
    const x = p.x * cy + p.z * sy;
    let z = -p.x * sy + p.z * cy;
    const y = p.y * cx - z * sx; z = p.y * sx + z * cx;
    const f = 1 / (1.9 - z * 0.55);
    const scale = Math.min(W, H * 1.4) * 0.62;
    return { sx: W * 0.62 + x * scale * f, sy: H * 0.5 + y * scale * f * 0.9, f, hue: p.hue };
  };

  const frame = () => {
    ctx.clearRect(0, 0, W, H);
    const P = new Array(n);
    for (let i = 0; i < n; i++) P[i] = project(pts[i]);
    // Linien nach Deckkraft in Eimer sortieren: ein Pfad pro Eimer statt ein Pfad pro Linie
    const paths = Array.from({ length: BUCKETS }, () => new Path2D());
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const dx = P[i].sx - P[j].sx, dy = P[i].sy - P[j].sy, d2 = dx * dx + dy * dy;
        if (d2 < LINK * LINK) {
          const q = (1 - Math.sqrt(d2) / LINK) * Math.min(P[i].f, P[j].f) * 1.4;
          const b = Math.min(BUCKETS - 1, Math.floor(q * BUCKETS * 0.9));
          paths[b].moveTo(P[i].sx, P[i].sy); paths[b].lineTo(P[j].sx, P[j].sy);
        }
      }
    }
    ctx.lineWidth = 1;
    paths.forEach((path, b) => {
      ctx.strokeStyle = `hsla(205, 85%, 72%, ${(0.06 + (b / BUCKETS) * 0.34).toFixed(3)})`;
      ctx.stroke(path);
    });
    P.forEach(p => {
      ctx.fillStyle = `hsla(${p.hue}, 90%, 78%, ${Math.min(1, 0.35 + p.f * 0.6).toFixed(2)})`;
      ctx.beginPath(); ctx.arc(p.sx, p.sy, 1 + p.f * 2.2, 0, Math.PI * 2); ctx.fill();
    });
  };

  const loop = () => {
    rotY += 0.0026 + tY * 0.0018; // Grundrotation + Maus
    rotX += (0.25 + tX - rotX) * 0.04;
    frame();
    rafId = requestAnimationFrame(loop);
  };
  const start = () => { if (rafId || reduceMotion.matches || !visible || document.hidden) return; rafId = requestAnimationFrame(loop); };
  const stop = () => { cancelAnimationFrame(rafId); rafId = 0; };

  resize();
  frame(); // Standbild (auch bei reduzierter Bewegung)
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { resize(); frame(); }, 120);
  });
  if (finePointer.matches) {
    hero.addEventListener('pointermove', e => {
      const r = hero.getBoundingClientRect();
      const nx = (e.clientX - r.left) / r.width - 0.5, ny = (e.clientY - r.top) / r.height - 0.5;
      tY = nx * 2; tX = ny * 0.5;
      if (parallax) {
        scene.style.setProperty('--px', `${(-nx * 36).toFixed(1)}px`);
        scene.style.setProperty('--py', `${(-ny * 26).toFixed(1)}px`);
      }
    });
    hero.addEventListener('pointerleave', () => {
      tX = 0; tY = 0;
      scene.style.setProperty('--px', '0px');
      scene.style.setProperty('--py', '0px');
    });
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([en]) => { visible = en.isIntersecting; visible ? start() : stop(); }, { threshold: 0 }).observe(hero);
  }
  document.addEventListener('visibilitychange', () => (document.hidden ? stop() : start()));
  reduceMotion.addEventListener('change', () => (reduceMotion.matches ? stop() : start()));
  start();

  /* ---------- Newsletter (Attrappe) ---------- */
  const nl = $('.newsletter');
  const nlStatus = $('.newsletter__status', nl);
  nl.noValidate = true; // eigene, zugängliche Fehlermeldung statt Browser-Tooltip
  nl.addEventListener('submit', e => {
    e.preventDefault();
    const input = $('input[type="email"]', nl);
    if (!input.checkValidity()) {
      nlStatus.classList.add('is-error');
      nlStatus.textContent = 'Bitte eine gültige E-Mail-Adresse eingeben.';
      input.focus();
      return;
    }
    nlStatus.classList.remove('is-error');
    nlStatus.textContent = 'Danke! (Demo: Es wurde nichts gesendet oder gespeichert.)';
    nl.reset();
  });
})();
