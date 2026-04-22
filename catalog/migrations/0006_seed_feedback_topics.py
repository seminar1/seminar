"""Наполняет справочник тем обращений обратной связи.

Темы охватывают наиболее частые поводы написать в научный центр
(вопросы по мероприятиям, регистрация, сотрудничество, технические
проблемы и т.д.) и выводятся в выпадающем списке формы обратной
связи (см. ``FeedbackView`` и шаблон ``catalog/feedback.html``).
"""
from django.db import migrations
from django.utils.text import slugify


TOPICS = [
    {
        'title': 'Вопрос по мероприятию',
        'icon': 'bi-calendar2-event',
        'description': (
            'Уточнить программу, место, время проведения или условия '
            'участия в конкретной конференции, семинаре или лекции.'
        ),
        'order': 10,
    },
    {
        'title': 'Регистрация и личный кабинет',
        'icon': 'bi-person-badge',
        'description': (
            'Не удаётся зарегистрироваться, подтвердить email, '
            'восстановить пароль или подать заявку на участие.'
        ),
        'order': 20,
    },
    {
        'title': 'Предложить своё мероприятие',
        'icon': 'bi-lightbulb',
        'description': (
            'Вы хотите провести научное мероприятие и разместить его '
            'в электронном каталоге университета.'
        ),
        'order': 30,
    },
    {
        'title': 'Сотрудничество и партнёрство',
        'icon': 'bi-people',
        'description': (
            'Предложения о совместных проектах, академическом '
            'партнёрстве или информационной поддержке.'
        ),
        'order': 40,
    },
    {
        'title': 'Работа со СМИ и информационный запрос',
        'icon': 'bi-megaphone',
        'description': (
            'Аккредитация журналистов, комментарии экспертов, '
            'пресс-релизы и публикации о мероприятиях центра.'
        ),
        'order': 50,
    },
    {
        'title': 'Техническая проблема на сайте',
        'icon': 'bi-bug',
        'description': (
            'Сайт медленно работает, страница не открывается, '
            'кнопка не реагирует или отображается ошибка.'
        ),
        'order': 60,
    },
    {
        'title': 'Предложение по улучшению сервиса',
        'icon': 'bi-stars',
        'description': (
            'Идеи, как сделать электронный каталог удобнее, '
            'и пожелания к новым функциям.'
        ),
        'order': 70,
    },
    {
        'title': 'Отзыв о мероприятии',
        'icon': 'bi-chat-heart',
        'description': (
            'Поделиться впечатлениями о посещённом мероприятии — '
            'положительными и теми, что стоит улучшить.'
        ),
        'order': 80,
    },
    {
        'title': 'Жалоба или претензия',
        'icon': 'bi-exclamation-octagon',
        'description': (
            'Сообщить о нарушении, некорректном контенте или '
            'иных серьёзных проблемах, требующих разбирательства.'
        ),
        'order': 90,
    },
    {
        'title': 'Другой вопрос',
        'icon': 'bi-chat-dots',
        'description': (
            'Тема не подходит ни под одну из категорий выше — '
            'просто опишите ваш вопрос в сообщении.'
        ),
        'order': 999,
    },
]


def seed(apps, schema_editor):
    """Создаёт темы обращений, если они ещё не существуют."""
    FeedbackTopic = apps.get_model('catalog', 'FeedbackTopic')

    for item in TOPICS:
        FeedbackTopic.objects.update_or_create(
            title=item['title'],
            defaults={
                'slug': slugify(item['title'], allow_unicode=True),
                'icon': item['icon'],
                'description': item['description'],
                'order': item['order'],
                'is_active': True,
            },
        )


def unseed(apps, schema_editor):
    """Удаляет созданные темы при откате миграции."""
    FeedbackTopic = apps.get_model('catalog', 'FeedbackTopic')
    FeedbackTopic.objects.filter(
        title__in=[t['title'] for t in TOPICS]
    ).delete()


class Migration(migrations.Migration):
    """Data-миграция с начальным наполнением справочника тем обращений."""

    dependencies = [
        ('catalog', '0005_feedbacktopic_eventreview_feedbackmessage'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
