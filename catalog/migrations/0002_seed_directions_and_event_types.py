"""Наполняет справочники научных направлений и типов мероприятий.

Данные совпадают со списком направлений, показываемых на лендинге
(см. ``LandingView.get_context_data``), и базовым набором типов,
упомянутых в шапке и секциях главной страницы.
"""
from django.db import migrations
from django.utils.text import slugify


DIRECTIONS = [
    {
        'title': 'Экономика и финансы',
        'icon': 'bi-bank',
        'description': (
            'Макроэкономика, корпоративные финансы, цифровая экономика '
            'и рынки капитала.'
        ),
    },
    {
        'title': 'Менеджмент',
        'icon': 'bi-briefcase',
        'description': (
            'Стратегический и проектный менеджмент, HR, '
            'предпринимательство и управление инновациями.'
        ),
    },
    {
        'title': 'Юриспруденция',
        'icon': 'bi-shield-check',
        'description': (
            'Гражданское, предпринимательское и цифровое право, '
            'правовое регулирование новых технологий.'
        ),
    },
    {
        'title': 'Информационные технологии',
        'icon': 'bi-cpu',
        'description': (
            'Искусственный интеллект, анализ данных, '
            'информационная безопасность и разработка ПО.'
        ),
    },
    {
        'title': 'Педагогика и психология',
        'icon': 'bi-mortarboard',
        'description': (
            'Образовательные технологии, психология развития, '
            'дистанционное обучение и воспитание.'
        ),
    },
    {
        'title': 'Гуманитарные науки',
        'icon': 'bi-globe',
        'description': (
            'Социология, история, лингвистика и межкультурные '
            'коммуникации в современном обществе.'
        ),
    },
]


EVENT_TYPES = [
    {'title': 'Конференция', 'icon': 'bi-people'},
    {'title': 'Семинар', 'icon': 'bi-chat-square-text'},
    {'title': 'Круглый стол', 'icon': 'bi-diagram-3'},
    {'title': 'Научные чтения', 'icon': 'bi-book'},
    {'title': 'Лекция', 'icon': 'bi-mic'},
    {'title': 'Воркшоп', 'icon': 'bi-tools'},
]


def seed(apps, schema_editor):
    """Создаёт направления и типы, если они ещё не существуют."""
    Direction = apps.get_model('catalog', 'Direction')
    EventType = apps.get_model('catalog', 'EventType')

    for item in DIRECTIONS:
        Direction.objects.update_or_create(
            title=item['title'],
            defaults={
                'slug': slugify(item['title'], allow_unicode=True),
                'icon': item['icon'],
                'description': item['description'],
                'is_active': True,
            },
        )

    for item in EVENT_TYPES:
        EventType.objects.update_or_create(
            title=item['title'],
            defaults={
                'slug': slugify(item['title'], allow_unicode=True),
                'icon': item['icon'],
                'is_active': True,
            },
        )


def unseed(apps, schema_editor):
    """Удаляет созданные справочные записи при откате миграции."""
    Direction = apps.get_model('catalog', 'Direction')
    EventType = apps.get_model('catalog', 'EventType')

    Direction.objects.filter(
        title__in=[d['title'] for d in DIRECTIONS]
    ).delete()
    EventType.objects.filter(
        title__in=[t['title'] for t in EVENT_TYPES]
    ).delete()


class Migration(migrations.Migration):
    """Data-миграция с начальным наполнением справочников каталога."""

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
