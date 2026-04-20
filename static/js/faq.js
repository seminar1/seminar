(function () {
    'use strict';

    const searchInput = document.getElementById('faqSearch');
    const searchClear = document.getElementById('faqSearchClear');
    const groups = document.querySelectorAll('.faq-group');
    const items = document.querySelectorAll('.faq-item');
    const filters = document.querySelectorAll('.faq-filter');
    const emptyState = document.getElementById('faqEmpty');
    const emptyReset = document.getElementById('faqEmptyReset');
    const totalCount = document.querySelector('[data-total]');

    if (!groups.length) return;

    let activeFilter = 'all';

    function setTotal() {
        if (totalCount) totalCount.textContent = String(items.length);
    }

    function normalize(text) {
        return (text || '').toLowerCase().trim();
    }

    function apply() {
        const query = normalize(searchInput ? searchInput.value : '');
        let visibleItems = 0;
        const visibleGroupSlugs = new Set();

        items.forEach((item) => {
            const group = item.closest('.faq-group');
            const slug = group ? group.dataset.category : '';
            const haystack = item.dataset.question || '';

            const matchesFilter = activeFilter === 'all' || activeFilter === slug;
            const matchesQuery = !query || haystack.indexOf(query) !== -1;
            const isVisible = matchesFilter && matchesQuery;

            item.classList.toggle('is-hidden', !isVisible);
            if (isVisible) {
                visibleItems += 1;
                visibleGroupSlugs.add(slug);
            } else if (item.open) {
                item.open = false;
            }
        });

        groups.forEach((group) => {
            const slug = group.dataset.category;
            group.classList.toggle('is-hidden', !visibleGroupSlugs.has(slug));
        });

        if (emptyState) {
            emptyState.classList.toggle('is-visible', visibleItems === 0);
            emptyState.hidden = visibleItems !== 0;
        }

        if (searchClear) {
            searchClear.hidden = !query;
        }
    }

    filters.forEach((button) => {
        button.addEventListener('click', () => {
            filters.forEach((b) => b.classList.remove('is-active'));
            button.classList.add('is-active');
            activeFilter = button.dataset.filter || 'all';
            apply();
            const content = document.querySelector('.faq-content');
            if (content && window.innerWidth <= 1100) {
                const offset = 90;
                const top = content.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({ top, behavior: 'smooth' });
            }
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', apply);
    }

    if (searchClear) {
        searchClear.addEventListener('click', () => {
            if (searchInput) {
                searchInput.value = '';
                searchInput.focus();
            }
            apply();
        });
    }

    if (emptyReset) {
        emptyReset.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            filters.forEach((b) => b.classList.remove('is-active'));
            const allBtn = document.querySelector('.faq-filter[data-filter="all"]');
            if (allBtn) allBtn.classList.add('is-active');
            activeFilter = 'all';
            apply();
        });
    }

    setTotal();
    apply();
})();
