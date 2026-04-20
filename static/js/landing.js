(function () {
    'use strict';

    function initReveal() {
        const targets = document.querySelectorAll(
            '.feature-card, .direction-card, .process-step, .event-card, .hero__stat, .hero-card'
        );

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

    function initStatsCounter() {
        const values = document.querySelectorAll('.hero__stat-value');
        if (!values.length) return;

        values.forEach((node) => {
            const raw = node.textContent.trim();
            const match = raw.match(/(\d[\d\s]*)/);
            if (!match) return;

            const target = parseInt(match[1].replace(/\s/g, ''), 10);
            const suffix = raw.replace(match[1], '');
            if (Number.isNaN(target) || target === 0) return;

            let current = 0;
            const duration = 1200;
            const start = performance.now();

            function tick(now) {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                current = Math.round(target * eased);
                const formatted = current.toLocaleString('ru-RU');
                node.textContent = formatted + suffix;
                if (progress < 1) {
                    requestAnimationFrame(tick);
                }
            }

            const observer = new IntersectionObserver((entries, obs) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        requestAnimationFrame(tick);
                        obs.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(node);
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initReveal();
        initStatsCounter();
    });
})();
