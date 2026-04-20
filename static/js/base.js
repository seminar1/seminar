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

    function initReveal() {
        const selector = [
            '.feature-card',
            '.direction-card',
            '.process-step',
            '.event-card',
            '.hero__stat',
            '.hero-card',
            '.value-card',
            '.team-card',
            '.timeline__item',
            '.about-stats__item',
            '.about-mission__card',
            '.contact-card',
            '.map-info-card',
            '.faq-group',
            '.event-item',
        ].join(', ');

        const targets = document.querySelectorAll(selector);
        if (!targets.length) return;

        targets.forEach((el) => el.classList.add('reveal'));

        if (!('IntersectionObserver' in window)) {
            targets.forEach((el) => el.classList.add('is-visible'));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        targets.forEach((el) => observer.observe(el));
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
        initReveal();
        if (burger) {
            burger.addEventListener('click', toggleNav);
        }
        if (nav) {
            nav.addEventListener('click', closeNavOnLink);
        }
    });

    window.addEventListener('scroll', handleScroll, { passive: true });
})();
