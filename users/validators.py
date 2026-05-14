from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordCharacterClassValidator:
    """Requires passwords to contain several character classes."""

    def validate(self, password, user=None):
        checks = (
            (
                any(char.islower() for char in password or ''),
                _('Пароль должен содержать хотя бы одну строчную букву.'),
            ),
            (
                any(char.isupper() for char in password or ''),
                _('Пароль должен содержать хотя бы одну заглавную букву.'),
            ),
            (
                any(char.isdigit() for char in password or ''),
                _('Пароль должен содержать хотя бы одну цифру.'),
            ),
            (
                any(not char.isalnum() for char in password or ''),
                _('Пароль должен содержать хотя бы один специальный символ.'),
            ),
        )
        errors = [message for passed, message in checks if not passed]
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            'Пароль должен содержать строчные и заглавные буквы, цифры '
            'и специальные символы.'
        )
