(function () {
    'use strict';

    function normalize(value) {
        return (value || '').toString().trim().toLowerCase();
    }

    function initPicker(picker) {
        var trigger = picker.querySelector('[data-event-picker-trigger]');
        var panel = picker.querySelector('[data-event-picker-panel]');
        var searchInput = picker.querySelector('[data-event-picker-search]');
        var list = picker.querySelector('[data-event-picker-list]');
        var emptyMsg = picker.querySelector('[data-event-picker-empty]');
        var hiddenInput = picker.querySelector('[data-event-picker-input]');
        var labelEl = picker.querySelector('[data-event-picker-label]');
        var sublabelEl = picker.querySelector('[data-event-picker-sublabel]');
        var clearBtn = picker.querySelector('[data-event-picker-clear]');
        var options = Array.prototype.slice.call(
            picker.querySelectorAll('[data-event-picker-option]')
        );

        if (!trigger || !panel || !hiddenInput || !options.length) {
            return;
        }

        function isOpen() {
            return !panel.hasAttribute('hidden');
        }

        function open() {
            panel.removeAttribute('hidden');
            picker.classList.add('is-open');
            trigger.setAttribute('aria-expanded', 'true');
            window.setTimeout(function () {
                if (searchInput) {
                    searchInput.focus();
                }
            }, 10);
        }

        function close() {
            panel.setAttribute('hidden', '');
            picker.classList.remove('is-open');
            trigger.setAttribute('aria-expanded', 'false');
            if (searchInput) {
                searchInput.value = '';
            }
            applyFilter('');
        }

        function toggle() {
            if (isOpen()) {
                close();
            } else {
                open();
            }
        }

        function applyFilter(query) {
            var q = normalize(query);
            var visibleCount = 0;

            options.forEach(function (option) {
                var li = option.parentElement;
                if (!li) return;

                var isAll = option.classList.contains('event-picker__option--all');
                if (isAll) {
                    li.style.display = '';
                    return;
                }

                var haystack = normalize(option.getAttribute('data-search'));
                var matches = !q || haystack.indexOf(q) !== -1;
                li.style.display = matches ? '' : 'none';
                if (matches) visibleCount += 1;
            });

            if (emptyMsg) {
                if (visibleCount === 0 && q.length) {
                    emptyMsg.removeAttribute('hidden');
                } else {
                    emptyMsg.setAttribute('hidden', '');
                }
            }
        }

        function selectOption(option) {
            var value = option.getAttribute('data-value') || '';
            var label = option.getAttribute('data-label') || '';
            var sublabel = option.getAttribute('data-sublabel') || '';

            hiddenInput.value = value;
            if (labelEl) labelEl.textContent = label;
            if (sublabelEl) sublabelEl.textContent = sublabel;

            options.forEach(function (opt) {
                opt.classList.toggle('is-selected', opt === option);
            });

            var form = picker.closest('form');
            if (form) {
                form.submit();
            } else {
                close();
            }
        }

        trigger.addEventListener('click', function (event) {
            event.preventDefault();
            toggle();
        });

        if (clearBtn) {
            clearBtn.addEventListener('click', function (event) {
                event.preventDefault();
                event.stopPropagation();
                var allOption = picker.querySelector('.event-picker__option--all');
                if (allOption) {
                    selectOption(allOption);
                }
            });
        }

        options.forEach(function (option) {
            option.addEventListener('click', function (event) {
                event.preventDefault();
                selectOption(option);
            });
        });

        if (searchInput) {
            searchInput.addEventListener('input', function () {
                applyFilter(searchInput.value);
            });
            searchInput.addEventListener('keydown', function (event) {
                if (event.key === 'Escape') {
                    close();
                    trigger.focus();
                } else if (event.key === 'Enter') {
                    event.preventDefault();
                    var firstVisible = options.find(function (opt) {
                        var li = opt.parentElement;
                        return li && li.style.display !== 'none'
                            && !opt.classList.contains('event-picker__option--all');
                    });
                    if (firstVisible) {
                        selectOption(firstVisible);
                    }
                }
            });
        }

        document.addEventListener('click', function (event) {
            if (!isOpen()) return;
            if (!picker.contains(event.target)) {
                close();
            }
        });

        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && isOpen()) {
                close();
                trigger.focus();
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var pickers = document.querySelectorAll('[data-event-picker]');
        pickers.forEach(initPicker);
    });
})();
