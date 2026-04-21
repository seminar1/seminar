"""Создаёт набор демонстрационных научных мероприятий каталога.

Заполняет таблицу ``Event`` разнообразными записями для проверки
каталога, фильтров и карточек лендинга: разные направления, типы,
форматы, статусы и даты.
"""
from datetime import datetime, timedelta

from django.db import migrations
from django.utils import timezone
from django.utils.text import slugify


SAMPLE_EVENTS = [
    {
        'title': 'Международная конференция «Искусственный интеллект — 2026»',
        'direction': 'Информационные технологии',
        'event_type': 'Конференция',
        'event_format': 'offline',
        'starts_at': (2026, 6, 15, 10, 0),
        'ends_at': (2026, 6, 17, 18, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, Актовый зал',
        'online_url': '',
        'seats_total': 250,
        'status': 'published',
        'is_featured': True,
        'short_description': (
            'Три дня докладов, воркшопов и панельных дискуссий ведущих '
            'специалистов в области искусственного интеллекта и анализа данных.'
        ),
        'description': (
            'Международная научно-практическая конференция объединяет '
            'исследователей, преподавателей и представителей индустрии. '
            'В программе — пленарные доклады, секционные заседания по '
            'машинному обучению, компьютерному зрению и этике ИИ, а также '
            'мастер-классы и нетворкинг.'
        ),
    },
    {
        'title': 'Цифровая экономика: вызовы и возможности 2026',
        'direction': 'Экономика и финансы',
        'event_type': 'Семинар',
        'event_format': 'online',
        'starts_at': (2026, 5, 12, 14, 0),
        'ends_at': (2026, 5, 12, 17, 30),
        'location': '',
        'online_url': 'https://meet.muiv.ru/digital-economy-2026',
        'seats_total': 500,
        'status': 'published',
        'is_featured': False,
        'short_description': (
            'Онлайн-семинар о трансформации экономических моделей '
            'в эпоху цифровых платформ и блокчейн-технологий.'
        ),
        'description': (
            'Ведущие экономисты университета и приглашённые эксперты '
            'обсудят влияние цифровизации на финансовые рынки, '
            'налогообложение и корпоративное управление.'
        ),
    },
    {
        'title': 'Круглый стол «Право и технологии: регулирование ИИ»',
        'direction': 'Юриспруденция',
        'event_type': 'Круглый стол',
        'event_format': 'hybrid',
        'starts_at': (2026, 7, 8, 11, 0),
        'ends_at': (2026, 7, 8, 15, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, ауд. 305',
        'online_url': 'https://meet.muiv.ru/law-ai-2026',
        'seats_total': 80,
        'status': 'published',
        'is_featured': True,
        'short_description': (
            'Дискуссия о правовом регулировании искусственного интеллекта, '
            'защите данных и ответственности разработчиков.'
        ),
        'description': (
            'Юристы, представители бизнеса и IT-специалисты обсудят '
            'актуальные законодательные инициативы, практику применения '
            'норм о персональных данных и границы ответственности '
            'за решения, принятые алгоритмами.'
        ),
    },
    {
        'title': 'Педагогика цифрового поколения',
        'direction': 'Педагогика и психология',
        'event_type': 'Лекция',
        'event_format': 'online',
        'starts_at': (2026, 5, 20, 18, 0),
        'ends_at': (2026, 5, 20, 20, 0),
        'location': '',
        'online_url': 'https://meet.muiv.ru/edu-lecture-2026',
        'seats_total': 0,
        'status': 'published',
        'is_featured': False,
        'short_description': (
            'Открытая онлайн-лекция о методиках обучения школьников '
            'и студентов в условиях цифровой среды.'
        ),
        'description': (
            'Лектор рассмотрит практические подходы к геймификации, '
            'микрообучению и формированию цифровых компетенций '
            'у обучающихся разных возрастных групп.'
        ),
    },
    {
        'title': 'Научные чтения памяти С.Ю. Витте',
        'direction': 'Гуманитарные науки',
        'event_type': 'Научные чтения',
        'event_format': 'offline',
        'starts_at': (2026, 10, 3, 10, 0),
        'ends_at': (2026, 10, 3, 17, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, Большой зал',
        'online_url': '',
        'seats_total': 180,
        'status': 'published',
        'is_featured': True,
        'short_description': (
            'Ежегодные чтения, посвящённые наследию выдающегося '
            'государственного деятеля и реформатора.'
        ),
        'description': (
            'Историки, экономисты и политологи представят доклады '
            'об экономических реформах конца XIX — начала XX века '
            'и их актуальности для современной России.'
        ),
    },
    {
        'title': 'Воркшоп «Data Science для начинающих исследователей»',
        'direction': 'Информационные технологии',
        'event_type': 'Воркшоп',
        'event_format': 'hybrid',
        'starts_at': (2026, 9, 18, 13, 0),
        'ends_at': (2026, 9, 18, 18, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, Компьютерный класс 214',
        'online_url': 'https://meet.muiv.ru/ds-workshop-2026',
        'seats_total': 40,
        'status': 'published',
        'is_featured': False,
        'short_description': (
            'Практический воркшоп по работе с данными на Python: '
            'pandas, визуализация и первые ML-модели.'
        ),
        'description': (
            'Участники на практике пройдут полный цикл исследования: '
            'от загрузки датасета и очистки данных до построения '
            'простой модели регрессии и интерпретации результатов.'
        ),
    },
    {
        'title': 'HR-менеджмент в эпоху искусственного интеллекта',
        'direction': 'Менеджмент',
        'event_type': 'Конференция',
        'event_format': 'hybrid',
        'starts_at': (2026, 11, 5, 10, 0),
        'ends_at': (2026, 11, 6, 17, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, Конференц-зал',
        'online_url': 'https://meet.muiv.ru/hr-ai-2026',
        'seats_total': 150,
        'status': 'published',
        'is_featured': False,
        'short_description': (
            'Двухдневная конференция о цифровой трансформации '
            'управления персоналом: подбор, обучение, аналитика.'
        ),
        'description': (
            'HR-директора крупных компаний и исследователи обсудят '
            'внедрение AI-инструментов в рекрутинг, системы оценки '
            'эффективности, программы корпоративного обучения '
            'и управление вовлечённостью сотрудников.'
        ),
    },
    {
        'title': 'Финансовые рынки: прогноз на 2027 год',
        'direction': 'Экономика и финансы',
        'event_type': 'Семинар',
        'event_format': 'offline',
        'starts_at': (2027, 1, 22, 15, 0),
        'ends_at': (2027, 1, 22, 18, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, ауд. 401',
        'online_url': '',
        'seats_total': 100,
        'status': 'published',
        'is_featured': False,
        'short_description': (
            'Аналитический семинар о динамике рынков капитала, '
            'денежно-кредитной политике и инвестиционных стратегиях.'
        ),
        'description': (
            'Эксперты представят макроэкономические прогнозы, '
            'сценарии развития фондового и валютного рынков, '
            'а также рекомендации по управлению портфелем '
            'в условиях глобальной неопределённости.'
        ),
    },
    {
        'title': 'История российской философии XIX века',
        'direction': 'Гуманитарные науки',
        'event_type': 'Научные чтения',
        'event_format': 'offline',
        'starts_at': (2026, 3, 25, 14, 0),
        'ends_at': (2026, 3, 25, 18, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, Библиотека',
        'online_url': '',
        'seats_total': 60,
        'status': 'completed',
        'is_featured': False,
        'short_description': (
            'Чтения, посвящённые ключевым фигурам русской '
            'философской мысли: Соловьёв, Бердяев, Флоренский.'
        ),
        'description': (
            'Философы и историки университета представили доклады '
            'о влиянии русской религиозной философии на европейскую '
            'интеллектуальную традицию и её актуальности сегодня.'
        ),
    },
    {
        'title': 'Стратегии корпоративного развития и устойчивый рост',
        'direction': 'Менеджмент',
        'event_type': 'Круглый стол',
        'event_format': 'offline',
        'starts_at': (2026, 12, 14, 11, 0),
        'ends_at': (2026, 12, 14, 16, 0),
        'location': 'г. Москва, 2-й Кожуховский пр-д, 12, ауд. 501',
        'online_url': '',
        'seats_total': 70,
        'status': 'draft',
        'is_featured': False,
        'short_description': (
            'Круглый стол для топ-менеджеров о построении долгосрочных '
            'стратегий в условиях нестабильности рынков.'
        ),
        'description': (
            'Участники обсудят модели устойчивого развития, '
            'ESG-стратегии, цифровую трансформацию и подходы '
            'к управлению рисками на горизонте 5–10 лет.'
        ),
    },
]


def seed_events(apps, schema_editor):
    """Создаёт демонстрационные мероприятия, если их ещё нет."""
    Event = apps.get_model('catalog', 'Event')
    Direction = apps.get_model('catalog', 'Direction')
    EventType = apps.get_model('catalog', 'EventType')

    tz = timezone.get_current_timezone()

    for item in SAMPLE_EVENTS:
        direction = Direction.objects.filter(title=item['direction']).first()
        event_type = EventType.objects.filter(title=item['event_type']).first()
        if not direction or not event_type:
            continue

        starts_at = timezone.make_aware(datetime(*item['starts_at']), tz)
        ends_at = None
        if item.get('ends_at'):
            ends_at = timezone.make_aware(datetime(*item['ends_at']), tz)

        slug = slugify(item['title'], allow_unicode=True)[:255]

        Event.objects.update_or_create(
            slug=slug,
            defaults={
                'title': item['title'],
                'short_description': item['short_description'],
                'description': item['description'],
                'direction': direction,
                'event_type': event_type,
                'event_format': item['event_format'],
                'starts_at': starts_at,
                'ends_at': ends_at,
                'location': item['location'],
                'online_url': item['online_url'],
                'seats_total': item['seats_total'],
                'status': item['status'],
                'is_featured': item['is_featured'],
            },
        )


def unseed_events(apps, schema_editor):
    """Удаляет демонстрационные мероприятия при откате миграции."""
    Event = apps.get_model('catalog', 'Event')
    slugs = [
        slugify(item['title'], allow_unicode=True)[:255]
        for item in SAMPLE_EVENTS
    ]
    Event.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    """Data-миграция с демонстрационными мероприятиями."""

    dependencies = [
        ('catalog', '0002_seed_directions_and_event_types'),
    ]

    operations = [
        migrations.RunPython(seed_events, unseed_events),
    ]
