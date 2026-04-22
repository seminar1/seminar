/**
 * Переключатели видимости полей ввода пароля на страницах auth.
 *
 * Ищет все обёртки [data-password-field] и навешивает обработчик на
 * вложенную кнопку [data-password-toggle] — она меняет type связанного
 * input-а между "password" и "text", обновляет иконку (bi-eye /
 * bi-eye-slash), aria-атрибуты и title.
 */
(function () {
    'use strict';

    const SHOW_LABEL = 'Показать пароль';
    const HIDE_LABEL = 'Скрыть пароль';

    function setupPasswordToggle(wrapper) {
        const input = wrapper.querySelector('input[type="password"], input[type="text"]');
        const button = wrapper.querySelector('[data-password-toggle]');
        const icon = wrapper.querySelector('[data-password-icon]');

        if (!input || !button) {
            return;
        }

        button.addEventListener('click', function () {
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            button.setAttribute('aria-pressed', isHidden ? 'true' : 'false');
            button.setAttribute(
                'aria-label',
                isHidden ? HIDE_LABEL : SHOW_LABEL
            );
            button.setAttribute('title', isHidden ? HIDE_LABEL : SHOW_LABEL);
            if (icon) {
                icon.classList.toggle('bi-eye', !isHidden);
                icon.classList.toggle('bi-eye-slash', isHidden);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const wrappers = document.querySelectorAll('[data-password-field]');
        wrappers.forEach(setupPasswordToggle);
    });
})();
