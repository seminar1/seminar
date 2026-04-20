(function () {
    'use strict';

    const header = document.getElementById('siteHeader');
    const burger = document.getElementById('burgerBtn');
    const nav = document.getElementById('siteNav');

    function handleScroll() {
        if (!header) return;
        if (window.scrollY > 8) {
            header.classList.add('is-scrolled');
        } else {
            header.classList.remove('is-scrolled');
        }
    }

    function toggleNav() {
        if (!nav || !burger) return;
        const isOpen = nav.classList.toggle('is-open');
        burger.classList.toggle('is-open', isOpen);
        burger.setAttribute('aria-expanded', String(isOpen));
        document.body.style.overflow = isOpen ? 'hidden' : '';
    }

    function closeNavOnLink(event) {
        if (!nav || !burger) return;
        if (event.target.matches('.site-nav__link') && nav.classList.contains('is-open')) {
            nav.classList.remove('is-open');
            burger.classList.remove('is-open');
            burger.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }
    }

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
            anchor.addEventListener('click', (event) => {
                const targetId = anchor.getAttribute('href');
                if (!targetId || targetId === '#') return;
                const target = document.querySelector(targetId);
                if (target) {
                    event.preventDefault();
                    const offset = (header ? header.offsetHeight : 0) + 8;
                    const top = target.getBoundingClientRect().top + window.scrollY - offset;
                    window.scrollTo({ top, behavior: 'smooth' });
                }
            });
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        handleScroll();
        initSmoothScroll();
        if (burger) {
            burger.addEventListener('click', toggleNav);
        }
        if (nav) {
            nav.addEventListener('click', closeNavOnLink);
        }
    });

    window.addEventListener('scroll', handleScroll, { passive: true });
})();
