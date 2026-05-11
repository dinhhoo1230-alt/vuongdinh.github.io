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
})();
