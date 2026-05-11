(function () {
  'use strict';

  const TAB_ORDER = ['home', 'about', 'timeline', 'projects', 'contact'];

  const nav = document.getElementById('mainNav');
  const navToggle = document.getElementById('navToggle');
  const tabLinks = document.querySelectorAll('[data-tab]');
  const panels = document.querySelectorAll('.panel');
  const curtain = document.getElementById('curtain');

  let isTransitioning = false;

  function swap(id) {
    panels.forEach((p) => p.classList.toggle('is-active', p.id === id));
    document.querySelectorAll('.nav__link[data-tab]').forEach((a) => {
      a.classList.toggle('is-active', a.dataset.tab === id);
    });
    if (nav && nav.classList.contains('is-open')) {
      nav.classList.remove('is-open');
      document.body.style.overflow = '';
    }
    window.scrollTo(0, 0);
  }

  function activate(id, opts) {
    opts = opts || {};
    const target = document.getElementById(id);
    if (!target) return false;

    if (opts.silent || !curtain) {
      swap(id);
      if (!opts.silent) history.replaceState(null, '', '#' + id);
      return true;
    }

    if (isTransitioning) return false;
    const currentActive = document.querySelector('.panel.is-active');
    if (currentActive && currentActive.id === id) return false;

    isTransitioning = true;

    // Xác định hướng (tới vs lui) theo thứ tự tab
    const currentIdx = currentActive ? TAB_ORDER.indexOf(currentActive.id) : 0;
    const targetIdx = TAB_ORDER.indexOf(id);
    const isBack = targetIdx < currentIdx;

    // Đặt vị trí khởi đầu của màn (ngoài bên phải hoặc bên trái) — không animate
    curtain.classList.toggle('dir-back', isBack);
    // Force reflow để transform khởi đầu được áp dụng trước khi animate
    void curtain.offsetWidth;

    // Phase 1: màn quét vào phủ kín
    curtain.classList.add('is-anim', 'is-covering');

    const onCovered = () => {
      curtain.removeEventListener('transitionend', onCovered);
      // Swap panel sau màn cam
      swap(id);
      history.replaceState(null, '', '#' + id);

      // Phase 2: màn tiếp tục quét sang phía đối diện, lộ tab mới
      curtain.classList.remove('is-covering');
      curtain.classList.add('is-leaving');

      const onLeft = () => {
        curtain.removeEventListener('transitionend', onLeft);
        // Reset về trạng thái ban đầu, không animate
        curtain.classList.remove('is-anim', 'is-leaving', 'dir-back');
        void curtain.offsetWidth;
        isTransitioning = false;
      };
      curtain.addEventListener('transitionend', onLeft);
    };
    curtain.addEventListener('transitionend', onCovered);

    return true;
  }

  tabLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      const id = link.dataset.tab;
      if (id) { e.preventDefault(); activate(id); }
    });
  });

  const initial = location.hash ? location.hash.slice(1) : 'home';
  if (!activate(initial, { silent: true })) activate('home', { silent: true });

  window.addEventListener('hashchange', () => {
    activate(location.hash.slice(1) || 'home', { silent: true });
  });

  if (nav && navToggle) {
    navToggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }

  // Slide transition giữa các trang project detail
  const detail = document.querySelector('.proj-detail');
  if (detail) {
    document.addEventListener('click', (e) => {
      const a = e.target.closest('.proj-detail a');
      if (!a) return;
      const href = a.getAttribute('href');
      if (!href || /^(https?:|mailto:|tel:|#)/.test(href)) return;
      if (a.target === '_blank') return;
      e.preventDefault();
      detail.classList.add('is-leaving');
      setTimeout(() => { location.href = href; }, 260);
    });
  }

  // Keyboard navigation: ← → chuyển tab (chỉ trên SPA index)
  if (panels.length > 0) {
    document.addEventListener('keydown', (e) => {
      if (document.querySelector('.lightbox.is-open')) return;
      if (nav && nav.classList.contains('is-open')) return;
      if (e.target.matches && e.target.matches('input, textarea, select')) return;
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      const cur = document.querySelector('.panel.is-active');
      if (!cur) return;
      const idx = TAB_ORDER.indexOf(cur.id);
      const next = e.key === 'ArrowRight' ? idx + 1 : idx - 1;
      if (next < 0 || next >= TAB_ORDER.length) return;
      e.preventDefault();
      activate(TAB_ORDER[next]);
    });
  }

  // Lightbox cho gallery ảnh trong project detail
  const galleryImgs = document.querySelectorAll('.gallery img');
  if (galleryImgs.length > 0) {
    const items = Array.from(galleryImgs).map((img) => ({
      src: img.getAttribute('src'),
      alt: img.getAttribute('alt') || ''
    }));

    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.setAttribute('aria-hidden', 'true');
    lb.innerHTML = `
      <button class="lightbox__btn lightbox__close" aria-label="Đóng">
        <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square">
          <line x1="8" y1="8" x2="24" y2="24"/><line x1="24" y1="8" x2="8" y2="24"/>
        </svg>
      </button>
      <button class="lightbox__btn lightbox__nav lightbox__prev" aria-label="Ảnh trước">
        <svg viewBox="0 0 32 32" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter">
          <polyline points="20,8 12,16 20,24"/>
        </svg>
      </button>
      <button class="lightbox__btn lightbox__nav lightbox__next" aria-label="Ảnh sau">
        <svg viewBox="0 0 32 32" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter">
          <polyline points="12,8 20,16 12,24"/>
        </svg>
      </button>
      <img class="lightbox__img" src="" alt="">
      <p class="lightbox__counter"></p>
    `;
    document.body.appendChild(lb);

    const lbImg = lb.querySelector('.lightbox__img');
    const lbCounter = lb.querySelector('.lightbox__counter');
    let cur = 0;

    function show(i) {
      cur = (i + items.length) % items.length;
      lbImg.style.opacity = '0';
      const tmp = new Image();
      tmp.onload = () => {
        lbImg.src = items[cur].src;
        lbImg.alt = items[cur].alt;
        lbImg.style.opacity = '1';
      };
      tmp.src = items[cur].src;
      lbCounter.textContent = String(cur + 1).padStart(2, '0') + ' / ' + String(items.length).padStart(2, '0');
    }

    function open(i) {
      show(i);
      lb.classList.add('is-open');
      lb.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }

    function close() {
      lb.classList.remove('is-open');
      lb.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }

    galleryImgs.forEach((img, i) => {
      img.addEventListener('click', () => open(i));
    });

    lb.querySelector('.lightbox__close').addEventListener('click', close);
    lb.querySelector('.lightbox__prev').addEventListener('click', (e) => { e.stopPropagation(); show(cur - 1); });
    lb.querySelector('.lightbox__next').addEventListener('click', (e) => { e.stopPropagation(); show(cur + 1); });
    lb.addEventListener('click', (e) => {
      if (e.target === lb || e.target === lbImg) close();
    });

    document.addEventListener('keydown', (e) => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(cur - 1);
      else if (e.key === 'ArrowRight') show(cur + 1);
    });
  }
})();
