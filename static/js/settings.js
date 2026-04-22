(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var navLinks = document.querySelectorAll('[data-section]');
        if (!navLinks.length) {
            return;
        }

        var sections = [];
        navLinks.forEach(function (link) {
            var id = link.getAttribute('data-section');
            var target = document.getElementById(id);
            if (target) {
                sections.push({ id: id, el: target, link: link });
            }
        });

        function activate(id) {
            navLinks.forEach(function (link) {
                var isActive = link.getAttribute('data-section') === id;
                link.classList.toggle('is-active', isActive);
            });
        }

        navLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                var id = link.getAttribute('data-section');
                activate(id);
            });
        });

        if ('IntersectionObserver' in window && sections.length) {
            var observer = new IntersectionObserver(function (entries) {
                var visible = entries
                    .filter(function (entry) { return entry.isIntersecting; })
                    .sort(function (a, b) {
                        return b.intersectionRatio - a.intersectionRatio;
                    });
                if (visible.length) {
                    activate(visible[0].target.id);
                }
            }, {
                rootMargin: '-40% 0px -50% 0px',
                threshold: [0, 0.25, 0.5, 0.75, 1],
            });

            sections.forEach(function (section) {
                observer.observe(section.el);
            });
        }
    });
})();
