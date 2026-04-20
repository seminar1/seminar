(function () {
    'use strict';

    const form = document.getElementById('eventsForm');
    if (!form) return;

    const searchInput = document.getElementById('eventsSearch');
    const sortSelect = document.getElementById('eventsSort');
    const resetBtn = document.getElementById('eventsReset');
    const emptyReset = document.getElementById('eventsEmptyReset');
    const grid = document.getElementById('eventsGrid');
    const emptyState = document.getElementById('eventsEmpty');
    const countEl = document.getElementById('eventsCount');
    const chipsEl = document.getElementById('eventsChips');
    const filterSelects = form.querySelectorAll('select[data-filter]');
    const items = Array.from(grid.querySelectorAll('.event-item'));

    const filterLabels = {};
    filterSelects.forEach((select) => {
        const key = select.dataset.filter;
        filterLabels[key] = {};
        Array.from(select.options).forEach((option) => {
            filterLabels[key][option.value] = option.textContent.trim();
        });
    });

    function initProgressBars() {
        grid.querySelectorAll('.event-item__progress-bar').forEach((bar) => {
            const value = parseInt(bar.dataset.value, 10) || 0;
            const total = parseInt(bar.dataset.total, 10) || 1;
            const percent = Math.min(Math.round((value / total) * 100), 100);
            bar.style.width = percent + '%';
        });
    }

    function normalize(text) {
        return (text || '').toLowerCase().trim();
    }

    function getFilters() {
        const values = {};
        filterSelects.forEach((select) => {
            values[select.dataset.filter] = select.value;
        });
        return values;
    }

    function renderChips() {
        if (!chipsEl) return;
        chipsEl.innerHTML = '';
        const filters = getFilters();
        Object.keys(filters).forEach((key) => {
            const value = filters[key];
            if (!value || value === 'all') return;
            const label = (filterLabels[key] && filterLabels[key][value]) || value;
            const chip = document.createElement('span');
            chip.className = 'events-chip';
            chip.innerHTML = `${label}<button type="button" aria-label="Убрать фильтр" data-remove="${key}"><i class="bi bi-x"></i></button>`;
            chipsEl.appendChild(chip);
        });

        chipsEl.querySelectorAll('button[data-remove]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const key = btn.dataset.remove;
                const select = form.querySelector(`select[data-filter="${key}"]`);
                if (select) {
                    select.value = 'all';
                    apply();
                }
            });
        });
    }

    function sortItems() {
        if (!sortSelect) return;
        const mode = sortSelect.value;
        const sorted = items.slice().sort((a, b) => {
            if (mode === 'name') {
                const titleA = normalize(a.querySelector('.event-item__title').textContent);
                const titleB = normalize(b.querySelector('.event-item__title').textContent);
                return titleA.localeCompare(titleB, 'ru');
            }
            if (mode === 'popularity') {
                const seatsA = Number(a.querySelector('.event-item__progress-bar').dataset.value);
                const seatsB = Number(b.querySelector('.event-item__progress-bar').dataset.value);
                return seatsB - seatsA;
            }
            return 0;
        });
        sorted.forEach((el) => grid.appendChild(el));
    }

    function apply() {
        const query = normalize(searchInput ? searchInput.value : '');
        const filters = getFilters();
        let visible = 0;

        items.forEach((item) => {
            const matchesDirection =
                !filters.direction || filters.direction === 'all' ||
                item.dataset.direction === filters.direction;
            const matchesType =
                !filters.type || filters.type === 'all' ||
                item.dataset.type === filters.type;
            const matchesFormat =
                !filters.format || filters.format === 'all' ||
                item.dataset.format === filters.format;
            const matchesQuery =
                !query || (item.dataset.haystack || '').indexOf(query) !== -1;

            const isVisible = matchesDirection && matchesType && matchesFormat && matchesQuery;
            item.classList.toggle('is-hidden', !isVisible);
            if (isVisible) visible += 1;
        });

        sortItems();
        if (countEl) countEl.textContent = String(visible);
        if (emptyState) {
            emptyState.classList.toggle('is-visible', visible === 0);
            emptyState.hidden = visible !== 0;
        }
        renderChips();
    }

    function resetAll() {
        if (searchInput) searchInput.value = '';
        filterSelects.forEach((select) => {
            select.value = 'all';
        });
        if (sortSelect) sortSelect.value = 'date';
        apply();
    }

    form.addEventListener('submit', (event) => event.preventDefault());
    filterSelects.forEach((select) => select.addEventListener('change', apply));
    if (sortSelect) sortSelect.addEventListener('change', apply);
    if (searchInput) searchInput.addEventListener('input', apply);
    if (resetBtn) resetBtn.addEventListener('click', resetAll);
    if (emptyReset) emptyReset.addEventListener('click', resetAll);

    initProgressBars();
    apply();
})();
