"""Представления приложения catalog."""
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from catalog.forms import EventForm
from catalog.models import Direction, Event, EventType
from users.mixins import CuratorRequiredMixin


class EventsView(TemplateView):
    """Страница каталога научных мероприятий.

    Все данные загружаются из MySQL: список событий, справочники
    направлений, типов и форматов. Отображаются только мероприятия
    со статусом «Опубликовано».
    """

    template_name = 'catalog/events.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон справочники фильтров и мероприятия из БД."""
        context = super().get_context_data(**kwargs)

        directions = [{'slug': 'all', 'label': 'Все направления'}]
        directions.extend(
            {'slug': d.slug, 'label': d.title}
            for d in Direction.objects.filter(is_active=True)
        )
        context['directions'] = directions

        types = [{'slug': 'all', 'label': 'Все типы'}]
        types.extend(
            {'slug': t.slug, 'label': t.title}
            for t in EventType.objects.filter(is_active=True)
        )
        context['types'] = types

        formats = [{'slug': 'all', 'label': 'Любой формат'}]
        formats.extend(
            {'slug': value, 'label': label}
            for value, label in Event.Format.choices
        )
        context['formats'] = formats

        context['sort_options'] = [
            {'value': 'date', 'label': 'По дате (сначала ближайшие)'},
            {'value': 'popularity', 'label': 'По популярности'},
            {'value': 'name', 'label': 'По названию (А–Я)'},
        ]

        context['events'] = (
            Event.objects
            .filter(status=Event.Status.PUBLISHED)
            .select_related('direction', 'event_type')
            .order_by('starts_at')
        )
        return context


class FaqView(TemplateView):
    """Страница «Часто задаваемые вопросы» с категориями и поиском."""

    template_name = 'catalog/faq.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон категории и вопросы."""
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {
                'slug': 'account',
                'icon': 'bi-person-badge',
                'title': 'Регистрация и аккаунт',
                'items': [
                    {
                        'question': 'Как создать аккаунт на платформе?',
                        'answer': (
                            'Нажмите кнопку «Регистрация» в правом верхнем '
                            'углу сайта, заполните форму и подтвердите '
                            'электронную почту. После этого вам будет '
                            'доступен личный кабинет.'
                        ),
                    },
                    {
                        'question': 'Обязательно ли быть студентом МУИВ?',
                        'answer': (
                            'Нет. Платформа открыта как для сотрудников и '
                            'студентов университета, так и для внешних '
                            'участников — достаточно указать актуальные '
                            'контактные данные при регистрации.'
                        ),
                    },
                    {
                        'question': 'Как восстановить пароль?',
                        'answer': (
                            'На странице входа выберите «Забыли пароль?», '
                            'введите e-mail, и мы отправим ссылку для '
                            'восстановления доступа.'
                        ),
                    },
                    {
                        'question': 'Можно ли удалить аккаунт?',
                        'answer': (
                            'Да, вы можете отправить заявку на удаление '
                            'аккаунта в разделе «Настройки» личного '
                            'кабинета. Данные будут удалены в течение '
                            '30 календарных дней.'
                        ),
                    },
                ],
            },
            {
                'slug': 'events',
                'icon': 'bi-calendar2-event',
                'title': 'Участие в мероприятиях',
                'items': [
                    {
                        'question': 'Как записаться на мероприятие?',
                        'answer': (
                            'Откройте карточку интересующего события и '
                            'нажмите «Подать заявку». Подтверждение придёт '
                            'в личный кабинет и на указанный e-mail.'
                        ),
                    },
                    {
                        'question': 'Можно ли отменить заявку?',
                        'answer': (
                            'Да, до даты проведения мероприятия заявку '
                            'можно отменить в разделе «Мои заявки» '
                            'личного кабинета.'
                        ),
                    },
                    {
                        'question': 'Доступны ли онлайн-форматы участия?',
                        'answer': (
                            'Формат указан в карточке каждого события: '
                            'очный, дистанционный или гибридный. При '
                            'дистанционном участии ссылка на трансляцию '
                            'приходит на e-mail за 1 час до начала.'
                        ),
                    },
                    {
                        'question': 'Что делать, если мест уже нет?',
                        'answer': (
                            'Вы можете записаться в лист ожидания. Если '
                            'освободится место, мы автоматически сообщим '
                            'вам об этом по e-mail.'
                        ),
                    },
                ],
            },
            {
                'slug': 'organizers',
                'icon': 'bi-briefcase',
                'title': 'Организаторам',
                'items': [
                    {
                        'question': 'Как предложить собственное мероприятие?',
                        'answer': (
                            'Напишите на events@muiv.ru с кратким описанием '
                            'формата, даты и целевой аудитории. Менеджер '
                            'научного центра свяжется с вами и поможет '
                            'оформить заявку.'
                        ),
                    },
                    {
                        'question': 'Кто модерирует мероприятия?',
                        'answer': (
                            'Все новые события проходят модерацию '
                            'сотрудниками научного центра — обычно в '
                            'течение 1–2 рабочих дней.'
                        ),
                    },
                    {
                        'question': 'Можно ли редактировать опубликованное событие?',
                        'answer': (
                            'Да, организаторы могут менять дату, место, '
                            'программу и количество мест до начала '
                            'мероприятия. Участникам автоматически '
                            'отправляются уведомления об изменениях.'
                        ),
                    },
                    {
                        'question': 'Есть ли аналитика по участникам?',
                        'answer': (
                            'В кабинете организатора доступны отчёты по '
                            'количеству заявок, подтверждений и посещаемости, '
                            'а также выгрузка списка участников в CSV/XLSX.'
                        ),
                    },
                ],
            },
            {
                'slug': 'certificates',
                'icon': 'bi-award',
                'title': 'Сертификаты и документы',
                'items': [
                    {
                        'question': 'Выдаётся ли сертификат участника?',
                        'answer': (
                            'Да, после подтверждения посещения электронный '
                            'сертификат становится доступен в личном '
                            'кабинете в течение 3 рабочих дней.'
                        ),
                    },
                    {
                        'question': 'В каком формате предоставляется сертификат?',
                        'answer': (
                            'Сертификат формируется в формате PDF с '
                            'уникальным идентификатором и QR-кодом для '
                            'проверки подлинности.'
                        ),
                    },
                    {
                        'question': 'Можно ли получить печатную версию?',
                        'answer': (
                            'Для отдельных мероприятий доступен выпуск '
                            'печатного сертификата по запросу — уточняйте '
                            'у организатора события.'
                        ),
                    },
                ],
            },
            {
                'slug': 'technical',
                'icon': 'bi-tools',
                'title': 'Техническая поддержка',
                'items': [
                    {
                        'question': 'Не приходит письмо с подтверждением',
                        'answer': (
                            'Проверьте папку «Спам». Если письма нет, '
                            'нажмите «Отправить повторно» на странице входа '
                            'или напишите в поддержку: support@muiv.ru.'
                        ),
                    },
                    {
                        'question': 'Сайт медленно работает или выдаёт ошибку',
                        'answer': (
                            'Очистите кеш браузера и попробуйте зайти '
                            'снова. Если ошибка повторяется, отправьте '
                            'скриншот на support@muiv.ru с описанием шагов.'
                        ),
                    },
                    {
                        'question': 'Какие браузеры поддерживаются?',
                        'answer': (
                            'Платформа корректно работает в актуальных '
                            'версиях Chrome, Firefox, Edge, Safari и '
                            '«Яндекс.Браузера».'
                        ),
                    },
                ],
            },
        ]
        return context


class ContactsView(TemplateView):
    """Статичная страница «Контакты» с формой и картой."""

    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон данные для контактных блоков."""
        context = super().get_context_data(**kwargs)
        context['contact_cards'] = [
            {
                'icon': 'bi-geo-alt',
                'title': 'Адрес',
                'lines': [
                    'г. Москва, 115432',
                    '2-й Кожуховский проезд, д. 12, стр. 1',
                ],
                'link_text': 'Посмотреть на карте',
                'link_href': '#map',
            },
            {
                'icon': 'bi-telephone',
                'title': 'Телефоны',
                'lines': [
                    '+7 (495) 500-03-63 — приёмная',
                    '+7 (495) 500-03-64 — научный центр',
                ],
                'link_text': 'Позвонить',
                'link_href': 'tel:+74955000363',
            },
            {
                'icon': 'bi-envelope',
                'title': 'Электронная почта',
                'lines': [
                    'science@muiv.ru — общие вопросы',
                    'events@muiv.ru — организаторам мероприятий',
                ],
                'link_text': 'Написать письмо',
                'link_href': 'mailto:science@muiv.ru',
            },
            {
                'icon': 'bi-clock',
                'title': 'Часы работы',
                'lines': [
                    'Пн–Пт: 09:00 — 18:00',
                    'Сб–Вс: выходные дни',
                ],
                'link_text': 'Написать в научный центр',
                'link_href': 'mailto:science@muiv.ru',
            },
        ]
        return context


class AboutView(TemplateView):
    """Статичная страница «О нас» с описанием сервиса и команды."""

    template_name = 'catalog/about.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон данные для секций страницы."""
        context = super().get_context_data(**kwargs)
        context['values'] = [
            {
                'icon': 'bi-lightbulb',
                'title': 'Открытость знаний',
                'text': (
                    'Научные мероприятия должны быть доступны каждому '
                    'исследователю, студенту и преподавателю университета.'
                ),
            },
            {
                'icon': 'bi-hand-thumbs-up',
                'title': 'Удобство и скорость',
                'text': (
                    'Простая регистрация, быстрый поиск и понятные личные '
                    'кабинеты — всё, чтобы сосредоточиться на науке.'
                ),
            },
            {
                'icon': 'bi-shield-check',
                'title': 'Доверие и качество',
                'text': (
                    'Модерация мероприятий и проверка организаторов '
                    'обеспечивают высокий уровень научного контента.'
                ),
            },
            {
                'icon': 'bi-people',
                'title': 'Сообщество',
                'text': (
                    'Мы объединяем учёных, студентов и партнёров в единую '
                    'цифровую среду научной жизни МУИВ.'
                ),
            },
        ]
        context['timeline'] = [
            {
                'year': '2023',
                'title': 'Идея проекта',
                'text': (
                    'Сформулирована потребность в единой цифровой площадке '
                    'для научных мероприятий университета.'
                ),
            },
            {
                'year': '2024',
                'title': 'Прототипирование',
                'text': (
                    'Спроектирована архитектура сервиса, определены '
                    'ключевые сценарии использования и структура каталога.'
                ),
            },
            {
                'year': '2025',
                'title': 'Разработка MVP',
                'text': (
                    'Реализованы каталог мероприятий, регистрация участников '
                    'и личные кабинеты на стеке Python / Django / MySQL.'
                ),
            },
            {
                'year': '2026',
                'title': 'Запуск и развитие',
                'text': (
                    'Публичный запуск сервиса для всех подразделений и '
                    'интеграция с внутренними системами МУИВ.'
                ),
            },
        ]
        context['team'] = [
            {
                'initials': 'АВ',
                'name': 'Анна Викторова',
                'role': 'Руководитель научного центра',
                'description': (
                    'Отвечает за научную политику, координацию мероприятий '
                    'и партнёрские программы.'
                ),
            },
            {
                'initials': 'ДК',
                'name': 'Дмитрий Комаров',
                'role': 'Ведущий разработчик',
                'description': (
                    'Проектирует архитектуру сервиса и развивает его '
                    'техническую платформу.'
                ),
            },
            {
                'initials': 'ЕС',
                'name': 'Екатерина Смирнова',
                'role': 'Менеджер мероприятий',
                'description': (
                    'Помогает организаторам запускать события и сопровождает '
                    'участников от регистрации до сертификата.'
                ),
            },
            {
                'initials': 'ИП',
                'name': 'Илья Петров',
                'role': 'UX/UI-дизайнер',
                'description': (
                    'Создаёт удобные и понятные интерфейсы для всех '
                    'пользователей платформы.'
                ),
            },
        ]
        context['stats'] = [
            {'value': '25+', 'label': 'Лет МУИВ им. С.Ю. Витте'},
            {'value': '30 000+', 'label': 'Выпускников университета'},
            {'value': '150+', 'label': 'Мероприятий ежегодно'},
            {'value': '12', 'label': 'Научных направлений'},
        ]
        return context


class LandingView(TemplateView):
    """Главная лендинг-страница электронного каталога научных мероприятий."""

    template_name = 'catalog/landing.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон данные для секций лендинга."""
        context = super().get_context_data(**kwargs)

        upcoming_events = list(
            Event.objects
            .filter(status=Event.Status.PUBLISHED)
            .select_related('direction', 'event_type')
            .order_by('starts_at')[:3]
        )
        context['upcoming_events'] = upcoming_events

        featured_event = next(
            (event for event in upcoming_events if event.is_featured),
            upcoming_events[0] if upcoming_events else None,
        )
        context['featured_event'] = featured_event
        context['features'] = [
            {
                'icon': 'bi-journal-bookmark',
                'title': 'Каталог мероприятий',
                'text': (
                    'Полный перечень конференций, семинаров, круглых столов '
                    'и научных чтений Московского университета им. С.Ю. Витте.'
                ),
            },
            {
                'icon': 'bi-person-check',
                'title': 'Онлайн-регистрация',
                'text': (
                    'Запись на участие в несколько кликов: подача заявки, '
                    'выбор формата участия и автоматическое подтверждение.'
                ),
            },
            {
                'icon': 'bi-pencil-square',
                'title': 'Управление событиями',
                'text': (
                    'Организаторы создают, редактируют и публикуют мероприятия, '
                    'отслеживают список зарегистрированных участников.'
                ),
            },
            {
                'icon': 'bi-search',
                'title': 'Удобный поиск и фильтры',
                'text': (
                    'Находите события по направлению, дате, формату участия и '
                    'уровню мероприятия за считанные секунды.'
                ),
            },
            {
                'icon': 'bi-bell',
                'title': 'Уведомления',
                'text': (
                    'Напоминания о предстоящих событиях и изменениях в '
                    'программе прямо в личном кабинете.'
                ),
            },
            {
                'icon': 'bi-graph-up',
                'title': 'Аналитика и отчёты',
                'text': (
                    'Администратор получает статистику посещаемости и '
                    'активности участников для поддержки решений.'
                ),
            },
        ]
        context['steps'] = [
            {
                'number': '01',
                'title': 'Регистрация',
                'text': 'Создайте аккаунт и заполните краткий профиль участника.',
            },
            {
                'number': '02',
                'title': 'Поиск мероприятия',
                'text': 'Отфильтруйте события по направлению, дате и формату.',
            },
            {
                'number': '03',
                'title': 'Подача заявки',
                'text': 'Заполните форму участия и получите подтверждение.',
            },
            {
                'number': '04',
                'title': 'Участие',
                'text': 'Посетите мероприятие и получите электронный сертификат.',
            },
        ]
        context['stats'] = [
            {'value': '150+', 'label': 'Мероприятий в год'},
            {'value': '12', 'label': 'Научных направлений'},
            {'value': '5 000+', 'label': 'Активных участников'},
            {'value': '98%', 'label': 'Положительных отзывов'},
        ]
        context['directions'] = [
            {
                'icon': 'bi-bank',
                'title': 'Экономика и финансы',
                'text': (
                    'Макроэкономика, корпоративные финансы, цифровая '
                    'экономика и рынки капитала.'
                ),
            },
            {
                'icon': 'bi-briefcase',
                'title': 'Менеджмент',
                'text': (
                    'Стратегический и проектный менеджмент, HR, '
                    'предпринимательство и управление инновациями.'
                ),
            },
            {
                'icon': 'bi-shield-check',
                'title': 'Юриспруденция',
                'text': (
                    'Гражданское, предпринимательское и цифровое право, '
                    'правовое регулирование новых технологий.'
                ),
            },
            {
                'icon': 'bi-cpu',
                'title': 'Информационные технологии',
                'text': (
                    'Искусственный интеллект, анализ данных, '
                    'информационная безопасность и разработка ПО.'
                ),
            },
            {
                'icon': 'bi-mortarboard',
                'title': 'Педагогика и психология',
                'text': (
                    'Образовательные технологии, психология развития, '
                    'дистанционное обучение и воспитание.'
                ),
            },
            {
                'icon': 'bi-globe',
                'title': 'Гуманитарные науки',
                'text': (
                    'Социология, история, лингвистика и межкультурные '
                    'коммуникации в современном обществе.'
                ),
            },
        ]
        return context


class CuratorEventsView(CuratorRequiredMixin, ListView):
    """Кураторская панель: список мероприятий с быстрыми действиями."""

    model = Event
    template_name = 'catalog/curator/events.html'
    context_object_name = 'events_list'
    paginate_by = 20

    def get_queryset(self):
        """Возвращает мероприятия с применёнными фильтрами и поиском."""
        queryset = (
            Event.objects
            .select_related('direction', 'event_type', 'organizer')
            .order_by('-starts_at')
        )
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(title__icontains=query)
        status = self.request.GET.get('status', '').strip()
        if status in dict(Event.Status.choices):
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        """Добавляет справочники и агрегаты для шапки дашборда."""
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Event.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        qs = Event.objects.all()
        context['total_count'] = qs.count()
        context['published_count'] = qs.filter(
            status=Event.Status.PUBLISHED
        ).count()
        context['draft_count'] = qs.filter(status=Event.Status.DRAFT).count()
        context['completed_count'] = qs.filter(
            status=Event.Status.COMPLETED
        ).count()
        return context


class CuratorEventCreateView(CuratorRequiredMixin, CreateView):
    """Создание нового научного мероприятия куратором."""

    model = Event
    form_class = EventForm
    template_name = 'catalog/curator/event_form.html'
    success_url = reverse_lazy('catalog:curator_events')

    def form_valid(self, form):
        """Сохраняет мероприятие и проставляет организатора."""
        event = form.save(commit=False)
        event.organizer = self.request.user
        event.save()
        self.object = event
        messages.success(
            self.request,
            f'Мероприятие «{event.title}» успешно создано.',
        )
        return super().form_valid(form)
