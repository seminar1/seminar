"""Представления приложения catalog."""
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Max, ProtectedError, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import urlencode
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    View,
)

from catalog import reports as report_builders

from catalog.forms import (
    AdminFeedbackMessageStatusForm,
    CuratorRegistrationStatusForm,
    DirectionForm,
    EventForm,
    EventRegistrationForm,
    EventTypeForm,
    FeedbackMessageForm,
    FeedbackTopicForm,
)
from catalog.models import (
    Direction,
    Event,
    EventRegistration,
    EventType,
    FeedbackMessage,
    FeedbackTopic,
)
from users.mixins import AdminRequiredMixin, CuratorRequiredMixin


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


class EventDetailView(DetailView):
    """Детальная страница научного мероприятия.

    Черновики и отменённые события скрыты от обычных пользователей;
    их могут открывать только кураторы и администраторы (например,
    чтобы проверить карточку перед публикацией).
    """

    model = Event
    template_name = 'catalog/event_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Возвращает выборку, учитывающую права текущего пользователя."""
        queryset = (
            Event.objects
            .select_related('direction', 'event_type', 'organizer')
        )
        user = self.request.user
        if user.is_authenticated and (
            getattr(user, 'is_curator', False)
            or getattr(user, 'is_administrator', False)
        ):
            return queryset
        return queryset.filter(
            status__in=[
                Event.Status.PUBLISHED,
                Event.Status.COMPLETED,
            ]
        )

    def get_context_data(self, **kwargs):
        """Добавляет похожие мероприятия и заявку пользователя."""
        context = super().get_context_data(**kwargs)
        event = self.object
        context['related_events'] = (
            Event.objects
            .filter(
                Q(direction=event.direction) | Q(event_type=event.event_type)
            )
            .filter(status=Event.Status.PUBLISHED)
            .exclude(pk=event.pk)
            .select_related('direction', 'event_type')
            .order_by('starts_at')[:3]
        )

        user = self.request.user
        user_registration = event.get_user_registration(user)
        context['user_registration'] = user_registration
        context['has_active_registration'] = bool(
            user_registration and user_registration.is_active
        )
        context['can_register'] = event.can_user_register(user)
        return context


class EventRegisterView(LoginRequiredMixin, View):
    """Страница подачи заявки на участие в мероприятии.

    На GET-запросе показывает форму контактных данных, предзаполненную
    из профиля пользователя. На POST — создаёт запись ``EventRegistration``
    с учётом правил события: окно приёма заявок, требование подтверждения
    куратором, лист ожидания при отсутствии мест.
    """

    template_name = 'catalog/event_register.html'

    def get_event(self):
        """Возвращает опубликованное мероприятие по slug из URL."""
        return get_object_or_404(
            Event.objects.select_related('direction', 'event_type'),
            slug=self.kwargs['slug'],
            status=Event.Status.PUBLISHED,
        )

    def get_existing_registration(self, event, user):
        """Возвращает активную заявку пользователя, если она есть."""
        return (
            event.registrations
            .filter(user=user, status__in=EventRegistration.ACTIVE_STATUSES)
            .first()
        )

    def render(self, request, event, form):
        """Рендерит шаблон со стандартным набором контекста."""
        return render(
            request,
            self.template_name,
            {
                'event': event,
                'form': form,
            },
        )

    def get(self, request, *args, **kwargs):
        """Показывает форму регистрации (или редиректит при невозможности)."""
        event = self.get_event()
        existing = self.get_existing_registration(event, request.user)
        if existing is not None:
            messages.info(
                request,
                'Вы уже подали заявку на это мероприятие. '
                'Текущий статус: {status}.'.format(
                    status=existing.get_status_display().lower()
                ),
            )
            return redirect('catalog:event_detail', slug=event.slug)

        if not event.is_registration_open:
            messages.error(
                request,
                'Приём заявок на это мероприятие сейчас закрыт.',
            )
            return redirect('catalog:event_detail', slug=event.slug)

        form = EventRegistrationForm(user=request.user)
        return self.render(request, event, form)

    def post(self, request, *args, **kwargs):
        """Обрабатывает подачу заявки с учётом всех бизнес-правил."""
        event = self.get_event()
        existing = self.get_existing_registration(event, request.user)
        if existing is not None:
            messages.info(
                request,
                'Вы уже подали заявку на это мероприятие.',
            )
            return redirect('catalog:event_detail', slug=event.slug)

        if not event.is_registration_open:
            messages.error(
                request,
                'Приём заявок на это мероприятие сейчас закрыт.',
            )
            return redirect('catalog:event_detail', slug=event.slug)

        form = EventRegistrationForm(request.POST, user=request.user)
        if not form.is_valid():
            return self.render(request, event, form)

        with transaction.atomic():
            event_locked = (
                Event.objects.select_for_update().get(pk=event.pk)
            )
            registration = form.save(commit=False)
            registration.event = event_locked
            registration.user = request.user
            registration.source = EventRegistration.Source.SELF

            is_full = (
                event_locked.seats_total > 0
                and event_locked.seats_taken >= event_locked.seats_total
            )

            if is_full and event_locked.allow_waitlist:
                registration.status = EventRegistration.Status.WAITLIST
                last_position = (
                    event_locked.registrations
                    .filter(status=EventRegistration.Status.WAITLIST)
                    .aggregate(last=Max('waitlist_position'))['last']
                )
                registration.waitlist_position = (last_position or 0) + 1
            elif event_locked.requires_approval:
                registration.status = EventRegistration.Status.PENDING
            else:
                registration.status = EventRegistration.Status.CONFIRMED
                registration.confirmed_at = timezone.now()

            registration.save()

        status = registration.status
        if status == EventRegistration.Status.CONFIRMED:
            messages.success(
                request,
                f'Вы зарегистрированы на «{event.title}». Ждём вас!',
            )
        elif status == EventRegistration.Status.PENDING:
            messages.success(
                request,
                'Заявка отправлена. Куратор свяжется с вами после '
                'её рассмотрения.',
            )
        elif status == EventRegistration.Status.WAITLIST:
            messages.info(
                request,
                'Мест нет, вы добавлены в лист ожидания под номером '
                f'{registration.waitlist_position}. Мы уведомим вас, '
                'как только место освободится.',
            )
        return redirect('catalog:event_detail', slug=event.slug)


class EventRegistrationCancelView(LoginRequiredMixin, View):
    """Отмена заявки участником мероприятия.

    Работает только с POST-запросом. Участник может отменить лишь
    собственную активную заявку. При отмене подтверждённой заявки
    первая запись в листе ожидания автоматически переводится
    в статус «Подтверждена».
    """

    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        """Отменяет заявку и продвигает лист ожидания."""
        registration = get_object_or_404(
            EventRegistration.objects.select_related('event'),
            pk=pk,
            user=request.user,
        )

        if not registration.is_active:
            messages.info(
                request,
                'Эта заявка уже не активна.',
            )
            return redirect('catalog:my_registrations')

        event = registration.event
        was_confirmed = registration.status == EventRegistration.Status.CONFIRMED

        with transaction.atomic():
            registration.mark_cancelled(by=request.user)

            if was_confirmed and event.seats_total > 0:
                promoted = (
                    event.registrations
                    .filter(status=EventRegistration.Status.WAITLIST)
                    .order_by('waitlist_position', 'created_at')
                    .first()
                )
                if promoted is not None:
                    if event.requires_approval:
                        promoted.status = EventRegistration.Status.PENDING
                    else:
                        promoted.status = EventRegistration.Status.CONFIRMED
                        promoted.confirmed_at = timezone.now()
                    promoted.waitlist_position = None
                    promoted.save(update_fields=[
                        'status',
                        'confirmed_at',
                        'waitlist_position',
                        'updated_at',
                    ])

        messages.success(
            request,
            f'Заявка на «{event.title}» отменена.',
        )

        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('catalog:my_registrations')


class DashboardView(LoginRequiredMixin, TemplateView):
    """Главная страница личного кабинета («Обзор»).

    Сводный экран авторизованного пользователя: показывает ближайшее
    подтверждённое/ожидающее событие, счётчики заявок в разрезе
    статусов, последние поданные заявки и рекомендуемые мероприятия,
    на которые пользователь ещё не записан.
    """

    template_name = 'catalog/dashboard.html'

    def get_context_data(self, **kwargs):
        """Собирает сводку по заявкам и мероприятиям пользователя."""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()

        user_regs = EventRegistration.objects.filter(user=user)

        context['stats'] = {
            'total': user_regs.count(),
            'confirmed': user_regs.filter(
                status=EventRegistration.Status.CONFIRMED
            ).count(),
            'pending': user_regs.filter(
                status=EventRegistration.Status.PENDING
            ).count(),
            'waitlist': user_regs.filter(
                status=EventRegistration.Status.WAITLIST
            ).count(),
            'completed': user_regs.filter(
                event__status=Event.Status.COMPLETED,
                status=EventRegistration.Status.CONFIRMED,
            ).count(),
            'cancelled': user_regs.filter(
                status=EventRegistration.Status.CANCELLED
            ).count(),
        }

        upcoming_regs = (
            user_regs
            .filter(
                status__in=EventRegistration.ACTIVE_STATUSES,
                event__starts_at__gte=now,
            )
            .select_related('event', 'event__direction', 'event__event_type')
            .order_by('event__starts_at')
        )
        context['next_registration'] = upcoming_regs.first()
        context['upcoming_registrations'] = upcoming_regs[:5]

        context['recent_registrations'] = (
            user_regs
            .select_related('event', 'event__direction', 'event__event_type')
            .order_by('-created_at')[:5]
        )

        registered_event_ids = list(
            user_regs.values_list('event_id', flat=True)
        )
        context['recommended_events'] = (
            Event.objects
            .filter(
                status=Event.Status.PUBLISHED,
                starts_at__gte=now,
                is_featured=True,
            )
            .exclude(id__in=registered_event_ids)
            .select_related('direction', 'event_type')
            .order_by('starts_at')[:3]
        )

        return context


class MyRegistrationsView(LoginRequiredMixin, ListView):
    """Личный список заявок пользователя на научные мероприятия."""

    model = EventRegistration
    template_name = 'catalog/my_registrations.html'
    context_object_name = 'registrations'
    paginate_by = 15

    def get_queryset(self):
        """Возвращает заявки текущего пользователя, сгруппированные по дате."""
        return (
            EventRegistration.objects
            .filter(user=self.request.user)
            .select_related('event', 'event__direction', 'event__event_type')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        """Добавляет сводную статистику по заявкам пользователя."""
        context = super().get_context_data(**kwargs)
        user_regs = EventRegistration.objects.filter(user=self.request.user)
        context['stats'] = {
            'total': user_regs.count(),
            'confirmed': user_regs.filter(
                status=EventRegistration.Status.CONFIRMED
            ).count(),
            'pending': user_regs.filter(
                status=EventRegistration.Status.PENDING
            ).count(),
            'waitlist': user_regs.filter(
                status=EventRegistration.Status.WAITLIST
            ).count(),
        }
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


class FeedbackView(View):
    """Публичная страница формы обратной связи.

    Доступна всем пользователям без авторизации. При отправке
    формы создаётся запись ``FeedbackMessage`` со снимком контактных
    данных, выбранной темой обращения и технической метаинформацией
    (IP-адрес, User-Agent, реферер). Для авторизованных пользователей
    обращение связывается с их учётной записью.
    """

    template_name = 'catalog/feedback.html'

    def _get_client_ip(self, request):
        """Возвращает IP-адрес клиента с учётом прокси-заголовков."""
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR') or None

    def _build_context(self, request, form, preselected_topic=None):
        """Формирует общий контекст шаблона для GET и POST (с ошибками)."""
        highlights = [
            {
                'icon': 'bi-lightning-charge',
                'title': 'Ответ в течение 1–2 рабочих дней',
                'text': (
                    'Обращения обрабатываются в будние дни с 09:00 до 18:00. '
                    'Мы стараемся отвечать как можно быстрее.'
                ),
            },
            {
                'icon': 'bi-shield-check',
                'title': 'Конфиденциальность',
                'text': (
                    'Контактные данные используются исключительно для ответа '
                    'на ваше обращение и не передаются третьим лицам.'
                ),
            },
            {
                'icon': 'bi-chat-left-text',
                'title': 'Любой вопрос — без регистрации',
                'text': (
                    'Форма доступна всем: студентам, преподавателям, гостям '
                    'сайта. Авторизация не требуется.'
                ),
            },
        ]
        contact_shortcuts = [
            {
                'icon': 'bi-envelope-at',
                'label': 'Электронная почта',
                'value': 'science@muiv.ru',
                'href': 'mailto:science@muiv.ru',
            },
            {
                'icon': 'bi-telephone',
                'label': 'Телефон',
                'value': '+7 (495) 500-03-63',
                'href': 'tel:+74955000363',
            },
            {
                'icon': 'bi-geo-alt',
                'label': 'Адрес',
                'value': 'Москва, 2-й Кожуховский проезд, д. 12, стр. 1',
                'href': '{0}#map'.format(reverse('catalog:contacts')),
            },
        ]
        return {
            'form': form,
            'highlights': highlights,
            'contact_shortcuts': contact_shortcuts,
            'topics': FeedbackTopic.objects.filter(is_active=True),
            'preselected_topic': preselected_topic,
        }

    def get(self, request, *args, **kwargs):
        """Отображает пустую форму обратной связи.

        Если в адресе указан параметр ``?topic=<slug>``, соответствующая
        тема обращения заранее выбрана в выпадающем списке — удобно для
        перехода с других страниц сайта (например, «Для организаторов»).
        """
        user = request.user if request.user.is_authenticated else None
        initial = {}
        preselected_topic = None
        topic_slug = request.GET.get('topic')
        if topic_slug:
            preselected_topic = FeedbackTopic.objects.filter(
                slug=topic_slug, is_active=True,
            ).first()
            if preselected_topic is not None:
                initial['topic'] = preselected_topic.pk
        form = FeedbackMessageForm(user=user, initial=initial)
        return render(
            request,
            self.template_name,
            self._build_context(request, form, preselected_topic=preselected_topic),
        )

    def post(self, request, *args, **kwargs):
        """Валидирует форму, сохраняет обращение и перенаправляет пользователя."""
        user = request.user if request.user.is_authenticated else None
        form = FeedbackMessageForm(request.POST, user=user)

        if not form.is_valid():
            messages.error(
                request,
                'Не удалось отправить обращение: проверьте заполнение полей.',
            )
            return render(
                request,
                self.template_name,
                self._build_context(request, form),
            )

        feedback = form.save(commit=False)
        if user is not None:
            feedback.user = user
        feedback.ip_address = self._get_client_ip(request)
        feedback.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        feedback.referer = request.META.get('HTTP_REFERER', '')[:500]
        feedback.save()

        messages.success(
            request,
            'Спасибо! Ваше обращение отправлено — мы свяжемся с вами '
            'по указанному email в ближайшее время.',
        )
        return redirect('catalog:feedback')


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


class BenefitsView(TemplateView):
    """Публичная страница «Преимущества» платформы «Научный Центр».

    Страница доступна всем пользователям, включая неавторизованных,
    и описывает ключевые выгоды сервиса для участников, организаторов
    и администрации университета.
    """

    template_name = 'catalog/benefits.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон данные для секций страницы преимуществ."""
        context = super().get_context_data(**kwargs)
        context['hero_highlights'] = [
            {
                'icon': 'bi-lightning-charge',
                'title': 'Регистрация за 30 секунд',
                'text': 'Без бумажных заявлений и длинных очередей.',
            },
            {
                'icon': 'bi-shield-check',
                'title': 'Проверенные мероприятия',
                'text': 'Все события модерируются научным центром МУИВ.',
            },
            {
                'icon': 'bi-award',
                'title': 'Сертификаты онлайн',
                'text': 'Подтверждение участия всегда под рукой.',
            },
        ]
        context['key_benefits'] = [
            {
                'icon': 'bi-search',
                'title': 'Умный поиск и фильтры',
                'text': (
                    'Быстро находите конференции, семинары и круглые столы '
                    'по направлению, формату и дате проведения.'
                ),
            },
            {
                'icon': 'bi-calendar2-check',
                'title': 'Онлайн-регистрация',
                'text': (
                    'Подавайте заявку в несколько кликов и получайте '
                    'мгновенное подтверждение по электронной почте.'
                ),
            },
            {
                'icon': 'bi-person-badge',
                'title': 'Личный кабинет',
                'text': (
                    'Вся история заявок, статусы участия и полученные '
                    'сертификаты хранятся в одном месте.'
                ),
            },
            {
                'icon': 'bi-bell',
                'title': 'Уведомления о событиях',
                'text': (
                    'Получайте напоминания о предстоящих мероприятиях '
                    'и изменениях в расписании.'
                ),
            },
            {
                'icon': 'bi-geo-alt',
                'title': 'Любой формат участия',
                'text': (
                    'Очные, онлайн- и гибридные мероприятия — выбирайте '
                    'удобный способ участвовать в научной жизни.'
                ),
            },
            {
                'icon': 'bi-graph-up-arrow',
                'title': 'Прозрачная аналитика',
                'text': (
                    'Организаторы видят статистику регистраций и '
                    'посещаемости в реальном времени.'
                ),
            },
        ]
        context['comparison'] = {
            'before': {
                'title': 'Раньше',
                'icon': 'bi-emoji-frown',
                'items': [
                    'Бумажные заявки и очереди в деканате',
                    'Афиши мероприятий разбросаны по сайтам',
                    'Неудобный учёт участников в Excel',
                    'Потерянные сертификаты и документы',
                    'Нет единой статистики по событиям',
                ],
            },
            'after': {
                'title': 'С «Научным Центром»',
                'icon': 'bi-emoji-smile',
                'items': [
                    'Онлайн-регистрация за 30 секунд',
                    'Единый каталог всех научных событий',
                    'Автоматический учёт мест и заявок',
                    'Сертификаты и история в личном кабинете',
                    'Прозрачная аналитика и отчёты',
                ],
            },
        }
        context['metrics'] = [
            {'value': '30 сек', 'label': 'Среднее время регистрации'},
            {'value': '100%', 'label': 'Онлайн-обработка заявок'},
            {'value': '24/7', 'label': 'Доступ к каталогу мероприятий'},
            {'value': '0 ₽', 'label': 'Для студентов и сотрудников МУИВ'},
        ]
        context['faq'] = [
            {
                'question': 'Нужно ли быть студентом МУИВ, чтобы пользоваться сервисом?',
                'answer': (
                    'Нет. Платформа открыта для всех: студентов, сотрудников '
                    'университета и внешних участников. Каталог мероприятий '
                    'можно просматривать даже без регистрации.'
                ),
            },
            {
                'question': 'Сколько стоит участие в мероприятиях?',
                'answer': (
                    'Большинство событий для студентов и сотрудников МУИВ '
                    'бесплатны. Если у конкретного мероприятия есть '
                    'организационный взнос, это указывается в его описании.'
                ),
            },
            {
                'question': 'Как получить сертификат участника?',
                'answer': (
                    'После подтверждения участия куратором сертификат '
                    'автоматически появляется в личном кабинете в разделе '
                    '«Мои заявки». Его можно скачать в любое удобное время.'
                ),
            },
            {
                'question': 'Можно ли участвовать в мероприятиях онлайн?',
                'answer': (
                    'Да. На платформе публикуются очные, онлайн- и гибридные '
                    'события — выбирайте подходящий формат при регистрации.'
                ),
            },
        ]
        return context


class TermsOfServiceView(TemplateView):
    """Публичная страница «Пользовательское соглашение».

    Доступна всем пользователям без авторизации. Определяет правила
    использования электронного каталога научных мероприятий «Научный
    Центр», права и обязанности пользователей и администрации сервиса.
    """

    template_name = 'catalog/terms.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон секции документа и контактные данные."""
        context = super().get_context_data(**kwargs)
        context['effective_date'] = '23 апреля 2026 года'
        context['last_updated'] = '23 апреля 2026 года'
        context['operator'] = {
            'full_name': (
                'Частное образовательное учреждение высшего образования '
                '«Московский университет им. С.Ю. Витте»'
            ),
            'short_name': 'ЧОУВО «МУИВ им. С.Ю. Витте»',
            'address': (
                '115432, г. Москва, 2-й Кожуховский проезд, д. 12, стр. 1'
            ),
            'email': 'science@muiv.ru',
            'phone': '+7 (495) 500-03-63',
        }
        context['highlights'] = [
            {
                'icon': 'bi-journal-check',
                'title': 'Чёткие правила',
                'text': (
                    'Простой и понятный документ, который описывает '
                    'условия использования электронного каталога '
                    'научных мероприятий.'
                ),
            },
            {
                'icon': 'bi-shield-check',
                'title': 'Уважение к пользователю',
                'text': (
                    'Сервис ориентирован на добросовестное использование '
                    'и защищает интересы как участников, так и '
                    'организаторов мероприятий.'
                ),
            },
            {
                'icon': 'bi-arrow-repeat',
                'title': 'Актуальные редакции',
                'text': (
                    'Мы публикуем изменения заранее и храним историю '
                    'редакций, чтобы вы всегда могли ознакомиться с '
                    'актуальной версией соглашения.'
                ),
            },
        ]
        context['sections'] = [
            {
                'id': 'general',
                'title': '1. Общие положения',
                'paragraphs': [
                    (
                        'Настоящее Пользовательское соглашение (далее — '
                        '«Соглашение») регулирует отношения между '
                        'ЧОУВО «МУИВ им. С.Ю. Витте» (далее — '
                        '«Администрация») и физическим лицом (далее — '
                        '«Пользователь»), использующим электронный каталог '
                        'научных мероприятий «Научный Центр» (далее — '
                        '«Сервис»).'
                    ),
                    (
                        'Соглашение является публичной офертой в '
                        'соответствии со статьёй 437 Гражданского '
                        'кодекса Российской Федерации. Использование '
                        'Сервиса означает полное и безоговорочное '
                        'согласие Пользователя с условиями настоящего '
                        'Соглашения.'
                    ),
                    (
                        'Если Пользователь не согласен с условиями '
                        'Соглашения или отдельными его положениями, он '
                        'обязан прекратить использование Сервиса.'
                    ),
                ],
            },
            {
                'id': 'terms',
                'title': '2. Термины и определения',
                'list': [
                    {
                        'term': 'Сервис',
                        'definition': (
                            'электронный каталог научных мероприятий '
                            '«Научный Центр», доступный в сети Интернет, '
                            'включая все его страницы, разделы и '
                            'функциональные возможности.'
                        ),
                    },
                    {
                        'term': 'Пользователь',
                        'definition': (
                            'физическое лицо, использующее Сервис для '
                            'ознакомления с каталогом, регистрации на '
                            'мероприятия, отправки обращений и иных '
                            'целей, допустимых настоящим Соглашением.'
                        ),
                    },
                    {
                        'term': 'Учётная запись',
                        'definition': (
                            'совокупность сведений о Пользователе, '
                            'создаваемых при регистрации и обеспечивающих '
                            'доступ к личному кабинету и персональным '
                            'разделам Сервиса.'
                        ),
                    },
                    {
                        'term': 'Контент',
                        'definition': (
                            'любые материалы Сервиса: тексты, '
                            'изображения, логотипы, описания мероприятий, '
                            'программы, а также иные результаты '
                            'интеллектуальной деятельности.'
                        ),
                    },
                ],
            },
            {
                'id': 'account',
                'title': '3. Регистрация и учётная запись',
                'paragraphs': [
                    (
                        'Часть возможностей Сервиса доступна только '
                        'зарегистрированным Пользователям. Регистрация '
                        'является добровольной и бесплатной.'
                    ),
                    (
                        'При регистрации Пользователь обязуется:'
                    ),
                ],
                'list_items': [
                    (
                        'указывать достоверные, актуальные и полные '
                        'сведения о себе;'
                    ),
                    (
                        'своевременно обновлять регистрационные данные '
                        'в случае их изменения;'
                    ),
                    (
                        'не передавать логин и пароль третьим лицам и '
                        'обеспечивать их конфиденциальность;'
                    ),
                    (
                        'немедленно уведомить Администрацию о любом '
                        'несанкционированном доступе к учётной записи.'
                    ),
                ],
                'paragraphs_after': [
                    (
                        'Пользователь несёт полную ответственность за '
                        'все действия, совершённые с использованием его '
                        'учётной записи.'
                    ),
                    (
                        'Администрация вправе отказать в регистрации '
                        'или приостановить действие учётной записи при '
                        'нарушении Пользователем условий настоящего '
                        'Соглашения.'
                    ),
                ],
            },
            {
                'id': 'user-rights',
                'title': '4. Права и обязанности Пользователя',
                'paragraphs': [
                    'Пользователь имеет право:',
                ],
                'list_items': [
                    (
                        'бесплатно использовать функциональные возможности '
                        'Сервиса в объёме, предусмотренном настоящим '
                        'Соглашением;'
                    ),
                    (
                        'просматривать каталог мероприятий, подавать '
                        'заявки на участие и отменять их в установленном '
                        'порядке;'
                    ),
                    (
                        'получать электронные сертификаты по итогам '
                        'участия в мероприятиях;'
                    ),
                    (
                        'обращаться в Администрацию через форму обратной '
                        'связи по любым вопросам, связанным с работой '
                        'Сервиса;'
                    ),
                    (
                        'в любое время удалить свою учётную запись и '
                        'отозвать согласие на обработку персональных '
                        'данных.'
                    ),
                ],
                'paragraphs_after': [
                    'Пользователь обязуется:',
                ],
                'list_items_after': [
                    (
                        'соблюдать условия настоящего Соглашения и '
                        'требования законодательства Российской Федерации;'
                    ),
                    (
                        'не совершать действий, направленных на '
                        'нарушение работы Сервиса, обход систем защиты '
                        'и получение несанкционированного доступа к '
                        'данным других пользователей;'
                    ),
                    (
                        'не использовать Сервис для распространения '
                        'информации, запрещённой законодательством '
                        'Российской Федерации;'
                    ),
                    (
                        'не размещать от имени Администрации '
                        'недостоверные или вводящие в заблуждение '
                        'сведения;'
                    ),
                    (
                        'уважать права и законные интересы других '
                        'пользователей Сервиса.'
                    ),
                ],
            },
            {
                'id': 'admin-rights',
                'title': '5. Права и обязанности Администрации',
                'paragraphs': [
                    'Администрация Сервиса имеет право:',
                ],
                'list_items': [
                    (
                        'изменять структуру, дизайн и функциональные '
                        'возможности Сервиса без предварительного '
                        'уведомления Пользователей;'
                    ),
                    (
                        'проводить технические работы, сопровождающиеся '
                        'временной недоступностью Сервиса или отдельных '
                        'его функций;'
                    ),
                    (
                        'модерировать контент, размещаемый в рамках '
                        'Сервиса, и отказывать в публикации материалов, '
                        'противоречащих Соглашению или '
                        'законодательству РФ;'
                    ),
                    (
                        'ограничивать или прекращать доступ к Сервису '
                        'при нарушении Пользователем условий '
                        'настоящего Соглашения.'
                    ),
                ],
                'paragraphs_after': [
                    'Администрация обязуется:',
                ],
                'list_items_after': [
                    (
                        'обеспечивать работоспособность Сервиса в '
                        'соответствии с техническими возможностями;'
                    ),
                    (
                        'соблюдать конфиденциальность персональных '
                        'данных Пользователей в порядке, установленном '
                        'Политикой конфиденциальности;'
                    ),
                    (
                        'рассматривать обращения Пользователей в '
                        'разумные сроки и отвечать на них по существу.'
                    ),
                ],
            },
            {
                'id': 'usage',
                'title': '6. Правила использования Сервиса',
                'paragraphs': [
                    'При использовании Сервиса запрещается:',
                ],
                'list_items': [
                    (
                        'размещать материалы, содержащие элементы '
                        'насилия, экстремизма, дискриминации или '
                        'оскорбления чести и достоинства других лиц;'
                    ),
                    (
                        'использовать Сервис для рассылки рекламы, спама '
                        'и иных сообщений коммерческого характера;'
                    ),
                    (
                        'нарушать авторские и иные исключительные права '
                        'третьих лиц;'
                    ),
                    (
                        'совершать действия, направленные на '
                        'дестабилизацию работы Сервиса: DDoS-атаки, '
                        'автоматизированный сбор данных, внедрение '
                        'вредоносного кода;'
                    ),
                    (
                        'выдавать себя за другого пользователя, '
                        'представителя Администрации или организатора '
                        'мероприятия.'
                    ),
                ],
            },
            {
                'id': 'intellectual-property',
                'title': '7. Интеллектуальная собственность',
                'paragraphs': [
                    (
                        'Все права на Сервис и размещённый в нём контент, '
                        'включая, но не ограничиваясь: программный код, '
                        'дизайн, тексты, графические элементы, логотипы '
                        'и товарные знаки, — принадлежат Администрации '
                        'или используются на законных основаниях.'
                    ),
                    (
                        'Пользователь не вправе копировать, '
                        'воспроизводить, распространять или иным '
                        'образом использовать контент Сервиса без '
                        'предварительного письменного согласия '
                        'Администрации, за исключением случаев, '
                        'прямо предусмотренных законодательством '
                        'Российской Федерации.'
                    ),
                    (
                        'Размещая любой контент в рамках Сервиса, '
                        'Пользователь гарантирует, что обладает всеми '
                        'необходимыми правами для такого размещения и '
                        'предоставляет Администрации право использовать '
                        'этот контент в целях функционирования Сервиса.'
                    ),
                ],
            },
            {
                'id': 'liability',
                'title': '8. Ответственность сторон',
                'paragraphs': [
                    (
                        'Пользователь самостоятельно несёт '
                        'ответственность за достоверность указанных '
                        'при регистрации сведений и содержание '
                        'отправляемых обращений.'
                    ),
                    (
                        'Администрация не несёт ответственности за '
                        'содержание мероприятий, проводимых '
                        'организаторами, а также за возможные разногласия '
                        'между Пользователями и организаторами событий.'
                    ),
                    (
                        'Нарушение условий настоящего Соглашения может '
                        'повлечь блокировку учётной записи и иные '
                        'меры, предусмотренные законодательством '
                        'Российской Федерации.'
                    ),
                ],
            },
            {
                'id': 'limitation',
                'title': '9. Ограничение ответственности',
                'paragraphs': [
                    (
                        'Сервис предоставляется на условиях «как есть» '
                        '(as is). Администрация не гарантирует '
                        'бесперебойную и безошибочную работу Сервиса '
                        'и не несёт ответственности за прямые или '
                        'косвенные убытки, возникшие в связи с его '
                        'использованием.'
                    ),
                    (
                        'Администрация не несёт ответственности за '
                        'технические сбои, действия третьих лиц, '
                        'перебои в работе сети Интернет, хостинг-'
                        'провайдеров и иных инфраструктурных сервисов, '
                        'за исключением случаев, прямо предусмотренных '
                        'законодательством Российской Федерации.'
                    ),
                ],
            },
            {
                'id': 'disputes',
                'title': '10. Порядок разрешения споров',
                'paragraphs': [
                    (
                        'Все споры и разногласия, возникающие в связи '
                        'с исполнением настоящего Соглашения, стороны '
                        'стремятся разрешить путём переговоров.'
                    ),
                    (
                        'Обязательным условием разрешения спора является '
                        'направление письменной претензии другой стороне. '
                        'Срок рассмотрения претензии — 30 (тридцать) '
                        'календарных дней с даты её получения.'
                    ),
                    (
                        'При недостижении соглашения спор подлежит '
                        'рассмотрению в суде по месту нахождения '
                        'Администрации в соответствии с '
                        'законодательством Российской Федерации.'
                    ),
                ],
            },
            {
                'id': 'changes',
                'title': '11. Изменения соглашения',
                'paragraphs': [
                    (
                        'Администрация вправе в одностороннем порядке '
                        'вносить изменения в настоящее Соглашение. '
                        'Актуальная редакция всегда доступна на '
                        'странице Сервиса по адресу публикации.'
                    ),
                    (
                        'Существенные изменения вступают в силу с '
                        'момента публикации новой редакции. Продолжение '
                        'использования Сервиса после публикации новой '
                        'редакции означает согласие Пользователя с '
                        'внесёнными изменениями.'
                    ),
                    (
                        'Рекомендуем периодически проверять содержание '
                        'Соглашения, чтобы быть в курсе изменений.'
                    ),
                ],
            },
            {
                'id': 'contacts',
                'title': '12. Контактные данные',
                'paragraphs': [
                    (
                        'По всем вопросам, связанным с исполнением '
                        'настоящего Соглашения, Пользователь может '
                        'обратиться к Администрации:'
                    ),
                ],
                'contacts': True,
            },
        ]
        return context


class PrivacyPolicyView(TemplateView):
    """Публичная страница «Политика конфиденциальности».

    Доступна всем пользователям без авторизации. Описывает перечень
    обрабатываемых персональных данных, цели обработки, правовые
    основания, сроки хранения, меры защиты и права пользователей
    электронного каталога научных мероприятий МУИВ.
    """

    template_name = 'catalog/privacy.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон секции документа и вспомогательные блоки."""
        context = super().get_context_data(**kwargs)
        context['effective_date'] = '23 апреля 2026 года'
        context['last_updated'] = '23 апреля 2026 года'
        context['operator'] = {
            'full_name': (
                'Частное образовательное учреждение высшего образования '
                '«Московский университет им. С.Ю. Витте»'
            ),
            'short_name': 'ЧОУВО «МУИВ им. С.Ю. Витте»',
            'address': (
                '115432, г. Москва, 2-й Кожуховский проезд, д. 12, стр. 1'
            ),
            'email': 'science@muiv.ru',
            'phone': '+7 (495) 500-03-63',
        }
        context['highlights'] = [
            {
                'icon': 'bi-shield-check',
                'title': 'Минимум данных',
                'text': (
                    'Собираем только те сведения, которые необходимы для '
                    'работы электронного каталога и регистрации на '
                    'мероприятия.'
                ),
            },
            {
                'icon': 'bi-lock',
                'title': 'Надёжная защита',
                'text': (
                    'Используем организационные и технические меры защиты '
                    'персональных данных в соответствии с требованиями '
                    'законодательства РФ.'
                ),
            },
            {
                'icon': 'bi-x-octagon',
                'title': 'Без передачи третьим лицам',
                'text': (
                    'Не передаём ваши персональные данные в рекламных или '
                    'коммерческих целях — только в случаях, прямо '
                    'предусмотренных законом.'
                ),
            },
        ]
        context['sections'] = [
            {
                'id': 'general',
                'title': '1. Общие положения',
                'paragraphs': [
                    (
                        'Настоящая Политика конфиденциальности (далее — '
                        '«Политика») определяет порядок обработки и защиты '
                        'персональных данных пользователей электронного '
                        'каталога научных мероприятий «Научный Центр» '
                        '(далее — «Сервис»), размещённого в сети Интернет '
                        'и принадлежащего ЧОУВО «МУИВ им. С.Ю. Витте» '
                        '(далее — «Оператор»).'
                    ),
                    (
                        'Политика разработана в соответствии с '
                        'Федеральным законом от 27.07.2006 № 152-ФЗ '
                        '«О персональных данных» и иными нормативными '
                        'правовыми актами Российской Федерации в области '
                        'защиты персональных данных.'
                    ),
                    (
                        'Использование Сервиса означает безоговорочное '
                        'согласие пользователя с настоящей Политикой и '
                        'условиями обработки его персональных данных. '
                        'В случае несогласия пользователь должен '
                        'воздержаться от использования Сервиса.'
                    ),
                ],
            },
            {
                'id': 'terms',
                'title': '2. Термины и определения',
                'list': [
                    {
                        'term': 'Персональные данные',
                        'definition': (
                            'любая информация, относящаяся прямо или '
                            'косвенно к определённому или определяемому '
                            'физическому лицу (субъекту персональных '
                            'данных).'
                        ),
                    },
                    {
                        'term': 'Обработка персональных данных',
                        'definition': (
                            'любое действие с персональными данными: '
                            'сбор, запись, систематизация, хранение, '
                            'уточнение, использование, передача, '
                            'обезличивание, блокирование, удаление и '
                            'уничтожение.'
                        ),
                    },
                    {
                        'term': 'Пользователь',
                        'definition': (
                            'физическое лицо, использующее Сервис для '
                            'просмотра каталога мероприятий, регистрации '
                            'на события, отправки обращений или иных '
                            'целей, предусмотренных Сервисом.'
                        ),
                    },
                    {
                        'term': 'Cookies',
                        'definition': (
                            'небольшие фрагменты данных, сохраняемые '
                            'браузером пользователя и используемые '
                            'Сервисом для идентификации сессии и '
                            'настройки работы интерфейса.'
                        ),
                    },
                ],
            },
            {
                'id': 'data',
                'title': '3. Какие персональные данные мы обрабатываем',
                'paragraphs': [
                    (
                        'В процессе использования Сервиса Оператор '
                        'обрабатывает следующие категории персональных '
                        'данных:'
                    ),
                ],
                'list_items': [
                    'фамилия, имя, отчество;',
                    'адрес электронной почты;',
                    'контактный телефон (при добровольном указании);',
                    (
                        'наименование организации / учебного заведения '
                        '(при добровольном указании);'
                    ),
                    (
                        'логин и пароль для входа в личный кабинет '
                        '(пароль хранится в зашифрованном виде);'
                    ),
                    (
                        'сведения об участии в мероприятиях: даты подачи '
                        'заявок, статусы регистраций, история участия;'
                    ),
                    (
                        'технические данные: IP-адрес, сведения о браузере '
                        'и устройстве, данные cookie, дата и время '
                        'посещений.'
                    ),
                ],
                'paragraphs_after': [
                    (
                        'Сервис не собирает специальные категории '
                        'персональных данных (о расовой и национальной '
                        'принадлежности, политических взглядах, состоянии '
                        'здоровья и т. п.), а также биометрические '
                        'персональные данные.'
                    ),
                ],
            },
            {
                'id': 'purposes',
                'title': '4. Цели обработки персональных данных',
                'paragraphs': [
                    (
                        'Оператор обрабатывает персональные данные '
                        'пользователей исключительно в следующих целях:'
                    ),
                ],
                'list_items': [
                    (
                        'регистрация пользователя и предоставление '
                        'доступа к личному кабинету;'
                    ),
                    (
                        'регистрация участников на научные мероприятия '
                        'и формирование списков участников;'
                    ),
                    'выдача электронных сертификатов участников;',
                    (
                        'информирование пользователей о мероприятиях, '
                        'изменениях в расписании и статусе заявок;'
                    ),
                    (
                        'обработка обращений, полученных через форму '
                        'обратной связи;'
                    ),
                    (
                        'обеспечение стабильной работы Сервиса, анализ '
                        'посещаемости и устранение технических ошибок;'
                    ),
                    (
                        'исполнение требований законодательства '
                        'Российской Федерации.'
                    ),
                ],
            },
            {
                'id': 'legal-basis',
                'title': '5. Правовые основания обработки',
                'paragraphs': [
                    (
                        'Обработка персональных данных осуществляется '
                        'Оператором на следующих правовых основаниях:'
                    ),
                ],
                'list_items': [
                    (
                        'согласие субъекта персональных данных на '
                        'обработку его персональных данных;'
                    ),
                    (
                        'исполнение договора, стороной которого является '
                        'субъект персональных данных (в том числе '
                        'договора об участии в мероприятии);'
                    ),
                    (
                        'осуществление прав и законных интересов '
                        'Оператора или третьих лиц;'
                    ),
                    (
                        'выполнение возложенных на Оператора '
                        'законодательством Российской Федерации функций '
                        'и обязанностей.'
                    ),
                ],
            },
            {
                'id': 'sharing',
                'title': '6. Передача персональных данных третьим лицам',
                'paragraphs': [
                    (
                        'Оператор не продаёт, не передаёт и не '
                        'раскрывает персональные данные третьим лицам '
                        'в рекламных или коммерческих целях.'
                    ),
                    (
                        'Передача персональных данных возможна только '
                        'в следующих случаях:'
                    ),
                ],
                'list_items': [
                    (
                        'с письменного согласия пользователя, выраженного '
                        'в явной форме;'
                    ),
                    (
                        'по требованию уполномоченных государственных '
                        'органов в порядке и на основаниях, '
                        'установленных законодательством РФ;'
                    ),
                    (
                        'организаторам мероприятий — в объёме, '
                        'необходимом для проведения события и '
                        'идентификации участника;'
                    ),
                    (
                        'подрядчикам Оператора (хостинг, почтовые '
                        'сервисы) на условиях конфиденциальности и в '
                        'объёме, необходимом для оказания услуг.'
                    ),
                ],
            },
            {
                'id': 'storage',
                'title': '7. Сроки обработки и хранения',
                'paragraphs': [
                    (
                        'Оператор обрабатывает персональные данные '
                        'пользователя в течение всего срока использования '
                        'Сервиса и до момента удаления учётной записи '
                        'пользователем или Оператором.'
                    ),
                    (
                        'Отдельные категории данных могут храниться в '
                        'течение более длительного срока, если это '
                        'необходимо для исполнения требований '
                        'законодательства РФ (например, для бухгалтерской '
                        'и налоговой отчётности — не менее 5 лет).'
                    ),
                    (
                        'По истечении сроков хранения персональные '
                        'данные уничтожаются или обезличиваются.'
                    ),
                ],
            },
            {
                'id': 'rights',
                'title': '8. Права субъекта персональных данных',
                'paragraphs': [
                    'Пользователь имеет право:',
                ],
                'list_items': [
                    (
                        'получать сведения об обработке своих '
                        'персональных данных;'
                    ),
                    (
                        'требовать уточнения, блокирования или '
                        'уничтожения персональных данных, если они '
                        'являются неполными, устаревшими или '
                        'неточными;'
                    ),
                    (
                        'отозвать согласие на обработку персональных '
                        'данных в любой момент;'
                    ),
                    'удалить свою учётную запись в Сервисе;',
                    (
                        'обжаловать действия или бездействие Оператора в '
                        'уполномоченный орган по защите прав субъектов '
                        'персональных данных или в судебном порядке.'
                    ),
                ],
                'paragraphs_after': [
                    (
                        'Для реализации указанных прав пользователь '
                        'может направить обращение по контактным данным, '
                        'указанным в разделе 12 настоящей Политики.'
                    ),
                ],
            },
            {
                'id': 'cookies',
                'title': '9. Использование файлов cookie',
                'paragraphs': [
                    (
                        'Сервис использует файлы cookie для корректной '
                        'работы интерфейса, сохранения настроек '
                        'пользователя и анонимного анализа статистики '
                        'посещений.'
                    ),
                    (
                        'Пользователь может самостоятельно отключить '
                        'приём файлов cookie в настройках своего '
                        'браузера. При этом отдельные функции Сервиса '
                        'могут работать некорректно.'
                    ),
                ],
            },
            {
                'id': 'security',
                'title': '10. Меры защиты персональных данных',
                'paragraphs': [
                    (
                        'Оператор принимает необходимые правовые, '
                        'организационные и технические меры для защиты '
                        'персональных данных от неправомерного или '
                        'случайного доступа, уничтожения, изменения, '
                        'блокирования, копирования, распространения и '
                        'иных неправомерных действий.'
                    ),
                ],
                'list_items': [
                    'шифрование данных при передаче (протокол HTTPS);',
                    (
                        'разграничение прав доступа к информационной '
                        'системе;'
                    ),
                    (
                        'регулярное резервное копирование и мониторинг '
                        'целостности данных;'
                    ),
                    (
                        'обучение сотрудников Оператора правилам '
                        'обращения с персональными данными.'
                    ),
                ],
            },
            {
                'id': 'changes',
                'title': '11. Изменения в политике конфиденциальности',
                'paragraphs': [
                    (
                        'Оператор оставляет за собой право вносить '
                        'изменения в настоящую Политику. Актуальная '
                        'редакция всегда доступна на странице Сервиса '
                        'по адресу публикации.'
                    ),
                    (
                        'Существенные изменения вступают в силу с '
                        'момента публикации новой редакции. '
                        'Рекомендуем периодически проверять содержание '
                        'Политики, чтобы быть в курсе изменений.'
                    ),
                ],
            },
            {
                'id': 'contacts',
                'title': '12. Контактная информация',
                'paragraphs': [
                    (
                        'По всем вопросам, связанным с обработкой '
                        'персональных данных, пользователь может '
                        'обратиться к Оператору:'
                    ),
                ],
                'contacts': True,
            },
        ]
        return context


class OrganizersView(TemplateView):
    """Публичная страница «Для организаторов».

    Страница предназначена для внешних организаторов — преподавателей
    других учебных заведений, научных институтов, компаний и экспертов,
    которые хотят предложить собственное мероприятие или обсудить
    сотрудничество с научным центром МУИВ. Доступна всем пользователям
    без авторизации.
    """

    template_name = 'catalog/organizers.html'

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон данные для секций страницы «Для организаторов»."""
        context = super().get_context_data(**kwargs)
        context['hero_facts'] = [
            {
                'icon': 'bi-globe2',
                'value': 'Открыто',
                'label': 'Для внешних партнёров и организаций',
            },
            {
                'icon': 'bi-calendar2-check',
                'value': '150+',
                'label': 'Мероприятий в каталоге ежегодно',
            },
            {
                'icon': 'bi-megaphone',
                'value': 'Информ-\u200bподдержка',
                'label': 'Анонсы в каталоге и рассылках',
            },
        ]
        context['opportunities'] = [
            {
                'icon': 'bi-people',
                'title': 'Совместные мероприятия',
                'text': (
                    'Проведите конференцию, семинар или круглый стол '
                    'вместе с научным центром МУИВ и получите доступ '
                    'к аудитории университета.'
                ),
            },
            {
                'icon': 'bi-calendar-plus',
                'title': 'Собственное событие в каталоге',
                'text': (
                    'Разместите своё научное мероприятие в электронном '
                    'каталоге и принимайте заявки участников онлайн.'
                ),
            },
            {
                'icon': 'bi-mic',
                'title': 'Участие в качестве спикера',
                'text': (
                    'Предложите доклад или мастер-класс в рамках '
                    'уже запланированных событий научного центра.'
                ),
            },
            {
                'icon': 'bi-bookmark-star',
                'title': 'Информационное партнёрство',
                'text': (
                    'Получите информационную поддержку ваших научных '
                    'инициатив: анонсы, публикации и рассылки.'
                ),
            },
            {
                'icon': 'bi-journal-text',
                'title': 'Публикации по итогам',
                'text': (
                    'Совместная подготовка сборников материалов и '
                    'публикаций по результатам проведённых мероприятий.'
                ),
            },
            {
                'icon': 'bi-award',
                'title': 'Сертификация участников',
                'text': (
                    'Электронные сертификаты для участников вашего '
                    'мероприятия — автоматически в их личных кабинетах.'
                ),
            },
        ]
        context['partners'] = [
            {
                'icon': 'bi-building',
                'title': 'Университеты и академические институты',
                'text': (
                    'Приглашаем коллег из других университетов к '
                    'совместным научным проектам и обмену опытом.'
                ),
            },
            {
                'icon': 'bi-briefcase',
                'title': 'Компании и индустриальные партнёры',
                'text': (
                    'Проводите отраслевые конференции, хакатоны '
                    'и практико-ориентированные семинары со студентами.'
                ),
            },
            {
                'icon': 'bi-easel',
                'title': 'Независимые эксперты и исследователи',
                'text': (
                    'Поделитесь своим опытом через лекции, мастер-классы '
                    'и авторские научные встречи.'
                ),
            },
            {
                'icon': 'bi-patch-check',
                'title': 'Профессиональные сообщества и НКО',
                'text': (
                    'Организуйте тематические круглые столы и встречи '
                    'с участием аудитории научного центра МУИВ.'
                ),
            },
        ]
        context['process_steps'] = [
            {
                'number': '01',
                'title': 'Отправьте заявку',
                'text': (
                    'Заполните форму обратной связи с коротким описанием '
                    'мероприятия или идеи сотрудничества.'
                ),
            },
            {
                'number': '02',
                'title': 'Обсудим детали',
                'text': (
                    'Свяжемся с вами в течение 1–2 рабочих дней, уточним '
                    'формат, аудиторию и организационные вопросы.'
                ),
            },
            {
                'number': '03',
                'title': 'Подготовим событие',
                'text': (
                    'Поможем оформить страницу мероприятия в каталоге, '
                    'настроим регистрацию и информационную поддержку.'
                ),
            },
            {
                'number': '04',
                'title': 'Проведём вместе',
                'text': (
                    'Соберём участников, обеспечим площадку или онлайн-'
                    'трансляцию и выдадим сертификаты по итогам.'
                ),
            },
        ]
        context['formats'] = [
            {'icon': 'bi-easel2', 'title': 'Конференции'},
            {'icon': 'bi-chat-square-text', 'title': 'Круглые столы'},
            {'icon': 'bi-mortarboard', 'title': 'Научные семинары'},
            {'icon': 'bi-lightbulb', 'title': 'Мастер-классы'},
            {'icon': 'bi-camera-video', 'title': 'Онлайн-вебинары'},
            {'icon': 'bi-journals', 'title': 'Научные чтения'},
        ]
        context['benefits_points'] = [
            'Доступ к заинтересованной аудитории исследователей и студентов',
            'Продвижение мероприятия в каталоге и на главной странице',
            'Удобная онлайн-регистрация и учёт участников',
            'Автоматические электронные сертификаты',
            'Поддержка на всех этапах — от анонса до публикации итогов',
            'Прозрачная статистика регистраций и посещаемости',
        ]
        context['faq'] = [
            {
                'question': 'Я не работаю в МУИВ. Могу ли я предложить своё мероприятие?',
                'answer': (
                    'Да. Мы открыты к сотрудничеству с внешними '
                    'организаторами — преподавателями других вузов, '
                    'научных институтов, компаний и независимыми '
                    'экспертами. Для начала заполните форму обратной '
                    'связи, выбрав тему «Предложить своё мероприятие».'
                ),
            },
            {
                'question': 'Какие мероприятия вы готовы разместить в каталоге?',
                'answer': (
                    'В первую очередь — научные и научно-образовательные: '
                    'конференции, семинары, круглые столы, мастер-классы, '
                    'лекции и вебинары. Тематика должна быть связана с '
                    'исследованиями, образованием или профессиональным '
                    'развитием.'
                ),
            },
            {
                'question': 'Требуется ли оплата за размещение мероприятия?',
                'answer': (
                    'Размещение научных и образовательных мероприятий '
                    'в каталоге бесплатно. Условия коммерческих событий '
                    'обсуждаются индивидуально.'
                ),
            },
            {
                'question': 'Сколько времени занимает подготовка анонса?',
                'answer': (
                    'Обычно от 3 до 7 рабочих дней — в зависимости от '
                    'полноты предоставленных материалов и формата '
                    'сотрудничества. Мы стараемся публиковать анонсы '
                    'заблаговременно, чтобы обеспечить максимальный охват.'
                ),
            },
        ]
        context['feedback_topic_partnership'] = (
            'сотрудничество-и-партнёрство'
        )
        context['feedback_topic_propose'] = (
            'предложить-своё-мероприятие'
        )
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
        context['active_tab'] = 'events'
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

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон активную вкладку панели куратора."""
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'events'
        return context


class CuratorRegistrationsView(CuratorRequiredMixin, ListView):
    """Кураторская страница со списком всех регистраций.

    Выводит таблицу заявок со всех мероприятий, поддерживает поиск
    по участнику (ФИО / email / username), фильтр по статусу и по
    конкретному мероприятию. В сайдбаре — быстрые агрегаты
    (ожидают подтверждения, подтверждены, в листе ожидания).
    """

    model = EventRegistration
    template_name = 'catalog/curator/registrations.html'
    context_object_name = 'registrations'
    paginate_by = 25

    def _apply_non_status_filters(self, queryset):
        """Применяет поиск и фильтр по мероприятию, но не по статусу."""
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(full_name__icontains=query)
                | Q(email__icontains=query)
                | Q(user__username__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(event__title__icontains=query)
            )
        event_id = self.request.GET.get('event', '').strip()
        if event_id.isdigit():
            queryset = queryset.filter(event_id=int(event_id))
        return queryset

    def get_queryset(self):
        """Возвращает регистрации с применёнными фильтрами."""
        queryset = (
            EventRegistration.objects
            .select_related('event', 'user')
            .order_by('-created_at')
        )
        queryset = self._apply_non_status_filters(queryset)

        status = self.request.GET.get('status', '').strip()
        if status in dict(EventRegistration.Status.choices):
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        """Добавляет справочники фильтров и агрегированные счётчики."""
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'registrations'
        context['status_choices'] = EventRegistration.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        context['current_event'] = self.request.GET.get('event', '')
        context['search_query'] = self.request.GET.get('q', '')

        # Счётчики пересчитываются с учётом поиска и фильтра по
        # мероприятию, но без ограничения по статусу — чтобы кнопки-
        # карточки показывали, сколько заявок каждого статуса попадает
        # в текущую выборку.
        base_qs = self._apply_non_status_filters(
            EventRegistration.objects.all()
        )
        context['total_count'] = base_qs.count()
        context['pending_count'] = base_qs.filter(
            status=EventRegistration.Status.PENDING
        ).count()
        context['confirmed_count'] = base_qs.filter(
            status=EventRegistration.Status.CONFIRMED
        ).count()
        context['waitlist_count'] = base_qs.filter(
            status=EventRegistration.Status.WAITLIST
        ).count()

        preserved = {}
        if context['search_query']:
            preserved['q'] = context['search_query']
        if context['current_event']:
            preserved['event'] = context['current_event']
        context['preserved_query_string'] = urlencode(preserved)

        context['events_for_filter'] = (
            Event.objects.order_by('-starts_at')
            .only('id', 'title', 'starts_at')[:200]
        )

        selected_event_id = self.request.GET.get('event', '').strip()
        context['selected_event_obj'] = None
        if selected_event_id.isdigit():
            context['selected_event_obj'] = (
                Event.objects.filter(pk=int(selected_event_id))
                .only('id', 'title', 'starts_at')
                .first()
            )
        return context


class CuratorRegistrationDetailView(CuratorRequiredMixin, View):
    """Кураторская карточка отдельной регистрации.

    Показывает всю информацию по заявке: снимок контактных данных
    участника, связанное мероприятие, историю жизненного цикла
    (создано / подтверждено / отменено) и комментарий участника.
    Из управляющих действий доступно изменение статуса — в том
    числе подтверждение ожидающих заявок и отмена с указанием
    причины.
    """

    http_method_names = ['get', 'post']
    template_name = 'catalog/curator/registration_detail.html'

    def _get_registration(self, pk):
        """Загружает регистрацию с предвыбранными связями."""
        return get_object_or_404(
            EventRegistration.objects.select_related(
                'event', 'event__direction', 'event__event_type',
                'user', 'cancelled_by',
            ),
            pk=pk,
        )

    def _build_context(self, registration, status_form):
        """Формирует общий контекст шаблона для GET и POST."""
        return {
            'registration': registration,
            'status_form': status_form,
            'active_tab': 'registrations',
        }

    def get(self, request, pk, *args, **kwargs):
        """Отображает карточку регистрации с формой смены статуса."""
        registration = self._get_registration(pk)
        status_form = CuratorRegistrationStatusForm(instance=registration)
        return render(
            request,
            self.template_name,
            self._build_context(registration, status_form),
        )

    def post(self, request, pk, *args, **kwargs):
        """Сохраняет новый статус регистрации и служебные поля."""
        registration = self._get_registration(pk)
        previous_status = registration.status

        status_form = CuratorRegistrationStatusForm(
            request.POST, instance=registration
        )

        if status_form.is_valid():
            updated = status_form.save(commit=False)
            new_status = updated.status
            now = timezone.now()

            if (
                new_status == EventRegistration.Status.CONFIRMED
                and previous_status != EventRegistration.Status.CONFIRMED
            ):
                updated.confirmed_at = now
                updated.cancelled_at = None
                updated.cancelled_by = None
                updated.cancellation_reason = ''
                if previous_status == EventRegistration.Status.WAITLIST:
                    updated.waitlist_position = None

            elif (
                new_status == EventRegistration.Status.CANCELLED
                and previous_status != EventRegistration.Status.CANCELLED
            ):
                updated.cancelled_at = now
                updated.cancelled_by = request.user

            elif new_status == EventRegistration.Status.WAITLIST and (
                updated.waitlist_position in (None, 0)
            ):
                last_position = (
                    EventRegistration.objects
                    .filter(event=updated.event)
                    .exclude(pk=updated.pk)
                    .aggregate(Max('waitlist_position'))
                    .get('waitlist_position__max')
                )
                updated.waitlist_position = (last_position or 0) + 1

            updated.save()

            messages.success(
                request,
                f'Статус заявки #{registration.pk} обновлён: '
                f'«{registration.get_status_display()}».',
            )
            return redirect(
                'catalog:curator_registration_detail', pk=registration.pk
            )

        messages.error(
            request,
            'Не удалось обновить статус: проверьте корректность данных.',
        )
        return render(
            request,
            self.template_name,
            self._build_context(registration, status_form),
        )


class CuratorDirectionsView(CuratorRequiredMixin, ListView):
    """Кураторская страница управления научными направлениями."""

    model = Direction
    template_name = 'catalog/curator/directions.html'
    context_object_name = 'directions'
    paginate_by = 50

    def get_queryset(self):
        """Возвращает направления с подсчётом связанных мероприятий."""
        return (
            Direction.objects
            .annotate(events_count=Count('events'))
            .order_by('title')
        )

    def get_context_data(self, **kwargs):
        """Добавляет форму создания нового направления."""
        context = super().get_context_data(**kwargs)
        context['form'] = kwargs.get('form') or DirectionForm()
        context['edit_form'] = kwargs.get('edit_form')
        context['editing_id'] = kwargs.get('editing_id')
        context['active_tab'] = 'directions'
        return context

    def post(self, request, *args, **kwargs):
        """Создаёт новое направление или возвращает форму с ошибками."""
        form = DirectionForm(request.POST)
        if form.is_valid():
            direction = form.save()
            messages.success(
                request,
                f'Направление «{direction.title}» добавлено.',
            )
            return HttpResponseRedirect(
                reverse('catalog:curator_directions')
            )
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class CuratorDirectionUpdateView(CuratorRequiredMixin, View):
    """Обработка редактирования направления через inline-форму."""

    http_method_names = ['get', 'post']

    def get(self, request, pk, *args, **kwargs):
        """Показывает список направлений с открытой формой редактирования."""
        direction = get_object_or_404(Direction, pk=pk)
        view = CuratorDirectionsView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data(
            edit_form=DirectionForm(instance=direction),
            editing_id=direction.pk,
        )
        return view.render_to_response(context)

    def post(self, request, pk, *args, **kwargs):
        """Сохраняет изменения направления."""
        direction = get_object_or_404(Direction, pk=pk)
        form = DirectionForm(request.POST, instance=direction)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Направление «{direction.title}» обновлено.',
            )
            return HttpResponseRedirect(
                reverse('catalog:curator_directions')
            )
        view = CuratorDirectionsView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data(
            edit_form=form,
            editing_id=direction.pk,
        )
        return view.render_to_response(context)


class CuratorDirectionDeleteView(CuratorRequiredMixin, View):
    """Удаление направления (если не используется в мероприятиях)."""

    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        """Удаляет направление или показывает сообщение о блокировке."""
        direction = get_object_or_404(Direction, pk=pk)
        title = direction.title
        try:
            direction.delete()
            messages.success(
                request,
                f'Направление «{title}» удалено.',
            )
        except ProtectedError:
            messages.error(
                request,
                f'Нельзя удалить направление «{title}»: к нему привязаны '
                f'мероприятия. Сначала смените направление у этих событий.',
            )
        return redirect('catalog:curator_directions')


class CuratorEventTypesView(CuratorRequiredMixin, ListView):
    """Кураторская страница управления типами мероприятий."""

    model = EventType
    template_name = 'catalog/curator/event_types.html'
    context_object_name = 'event_types'
    paginate_by = 50

    def get_queryset(self):
        """Возвращает типы мероприятий с подсчётом связанных событий."""
        return (
            EventType.objects
            .annotate(events_count=Count('events'))
            .order_by('title')
        )

    def get_context_data(self, **kwargs):
        """Добавляет форму создания нового типа мероприятия."""
        context = super().get_context_data(**kwargs)
        context['form'] = kwargs.get('form') or EventTypeForm()
        context['edit_form'] = kwargs.get('edit_form')
        context['editing_id'] = kwargs.get('editing_id')
        context['active_tab'] = 'event_types'
        return context

    def post(self, request, *args, **kwargs):
        """Создаёт новый тип мероприятия или возвращает форму с ошибками."""
        form = EventTypeForm(request.POST)
        if form.is_valid():
            event_type = form.save()
            messages.success(
                request,
                f'Тип мероприятия «{event_type.title}» добавлен.',
            )
            return HttpResponseRedirect(
                reverse('catalog:curator_event_types')
            )
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class CuratorEventTypeUpdateView(CuratorRequiredMixin, View):
    """Обработка редактирования типа мероприятия через inline-форму."""

    http_method_names = ['get', 'post']

    def get(self, request, pk, *args, **kwargs):
        """Показывает список типов с открытой формой редактирования."""
        event_type = get_object_or_404(EventType, pk=pk)
        view = CuratorEventTypesView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data(
            edit_form=EventTypeForm(instance=event_type),
            editing_id=event_type.pk,
        )
        return view.render_to_response(context)

    def post(self, request, pk, *args, **kwargs):
        """Сохраняет изменения типа мероприятия."""
        event_type = get_object_or_404(EventType, pk=pk)
        form = EventTypeForm(request.POST, instance=event_type)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Тип мероприятия «{event_type.title}» обновлён.',
            )
            return HttpResponseRedirect(
                reverse('catalog:curator_event_types')
            )
        view = CuratorEventTypesView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data(
            edit_form=form,
            editing_id=event_type.pk,
        )
        return view.render_to_response(context)


class CuratorEventTypeDeleteView(CuratorRequiredMixin, View):
    """Удаление типа мероприятия (если не используется)."""

    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        """Удаляет тип или показывает сообщение о блокировке."""
        event_type = get_object_or_404(EventType, pk=pk)
        title = event_type.title
        try:
            event_type.delete()
            messages.success(
                request,
                f'Тип мероприятия «{title}» удалён.',
            )
        except ProtectedError:
            messages.error(
                request,
                f'Нельзя удалить тип «{title}»: к нему привязаны мероприятия. '
                f'Сначала смените тип у этих событий.',
            )
        return redirect('catalog:curator_event_types')


class AdminFeedbackTopicsView(AdminRequiredMixin, ListView):
    """Админ-страница управления темами обращений (CRUD).

    Отображает список тем с количеством связанных обращений, форму
    добавления новой темы и (при редактировании) inline-форму
    редактирования — в том же стиле, что и справочники направлений
    и типов мероприятий.
    """

    model = FeedbackTopic
    template_name = 'catalog/admin/feedback_topics.html'
    context_object_name = 'topics'
    paginate_by = 50

    def get_queryset(self):
        """Возвращает темы обращений с подсчётом связанных сообщений."""
        return (
            FeedbackTopic.objects
            .annotate(messages_count=Count('messages'))
            .order_by('order', 'title')
        )

    def get_context_data(self, **kwargs):
        """Добавляет форму создания и (опционально) редактирования темы."""
        context = super().get_context_data(**kwargs)
        context['form'] = kwargs.get('form') or FeedbackTopicForm()
        context['edit_form'] = kwargs.get('edit_form')
        context['editing_id'] = kwargs.get('editing_id')
        return context

    def post(self, request, *args, **kwargs):
        """Создаёт новую тему обращения или возвращает форму с ошибками."""
        form = FeedbackTopicForm(request.POST)
        if form.is_valid():
            topic = form.save()
            messages.success(
                request,
                f'Тема обращения «{topic.title}» добавлена.',
            )
            return HttpResponseRedirect(reverse('users:admin_feedback_topics'))
        self.object_list = self.get_queryset()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AdminFeedbackTopicUpdateView(AdminRequiredMixin, View):
    """Обработка редактирования темы обращения через inline-форму."""

    http_method_names = ['get', 'post']

    def get(self, request, pk, *args, **kwargs):
        """Показывает список тем с открытой формой редактирования."""
        topic = get_object_or_404(FeedbackTopic, pk=pk)
        view = AdminFeedbackTopicsView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data(
            edit_form=FeedbackTopicForm(instance=topic),
            editing_id=topic.pk,
        )
        return view.render_to_response(context)

    def post(self, request, pk, *args, **kwargs):
        """Сохраняет изменения темы обращения."""
        topic = get_object_or_404(FeedbackTopic, pk=pk)
        form = FeedbackTopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Тема обращения «{topic.title}» обновлена.',
            )
            return HttpResponseRedirect(reverse('users:admin_feedback_topics'))
        view = AdminFeedbackTopicsView()
        view.setup(request)
        view.object_list = view.get_queryset()
        context = view.get_context_data(
            edit_form=form,
            editing_id=topic.pk,
        )
        return view.render_to_response(context)


class AdminFeedbackTopicDeleteView(AdminRequiredMixin, View):
    """Удаление темы обращения из справочника."""

    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        """Удаляет тему; связанные обращения остаются (topic становится NULL)."""
        topic = get_object_or_404(FeedbackTopic, pk=pk)
        title = topic.title
        topic.delete()
        messages.success(
            request,
            f'Тема обращения «{title}» удалена. Связанные обращения сохранены '
            f'без темы.',
        )
        return redirect('users:admin_feedback_topics')


class AdminFeedbackMessagesView(AdminRequiredMixin, ListView):
    """Админ-страница списка обращений обратной связи.

    Поддерживает фильтрацию по статусу и теме, поиск по ФИО, email
    и тексту сообщения, а также отображает сводную статистику
    (всего, новые, в работе, отвеченные).
    """

    template_name = 'catalog/admin/feedback_messages.html'
    context_object_name = 'messages_list'
    paginate_by = 25

    def get_queryset(self):
        """Возвращает отфильтрованный и отсортированный список обращений."""
        queryset = (
            FeedbackMessage.objects
            .select_related('topic', 'user', 'assigned_to', 'related_event')
            .order_by('-created_at')
        )

        status = self.request.GET.get('status', '').strip()
        if status and status in dict(FeedbackMessage.Status.choices):
            queryset = queryset.filter(status=status)

        topic_id = self.request.GET.get('topic', '').strip()
        if topic_id.isdigit():
            queryset = queryset.filter(topic_id=int(topic_id))

        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(subject__icontains=search_query)
                | Q(message__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон фильтры, статистику и справочники."""
        context = super().get_context_data(**kwargs)
        base_queryset = FeedbackMessage.objects.all()
        context['total_count'] = base_queryset.count()
        context['new_count'] = base_queryset.filter(
            status=FeedbackMessage.Status.NEW
        ).count()
        context['in_progress_count'] = base_queryset.filter(
            status=FeedbackMessage.Status.IN_PROGRESS
        ).count()
        context['answered_count'] = base_queryset.filter(
            status=FeedbackMessage.Status.ANSWERED
        ).count()

        context['status_choices'] = FeedbackMessage.Status.choices
        context['topics'] = (
            FeedbackTopic.objects
            .order_by('order', 'title')
        )
        context['current_status'] = self.request.GET.get('status', '').strip()
        context['current_topic'] = self.request.GET.get('topic', '').strip()
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context


class AdminFeedbackMessageDetailView(AdminRequiredMixin, View):
    """Страница просмотра отдельного обращения обратной связи.

    Показывает все данные обращения — контакты автора, текст
    сообщения, связанное мероприятие и техническую мета-информацию.
    Из управляющих действий доступно только изменение статуса
    обработки (новое → в работе → отвечено → закрыто и т.п.).
    """

    http_method_names = ['get', 'post']
    template_name = 'catalog/admin/feedback_message_detail.html'

    def _get_feedback(self, pk):
        """Загружает обращение с предвыбранными связями."""
        return get_object_or_404(
            FeedbackMessage.objects.select_related(
                'topic', 'user', 'related_event'
            ),
            pk=pk,
        )

    def _build_context(self, feedback, status_form):
        """Формирует общий контекст шаблона для GET и POST."""
        return {
            'feedback': feedback,
            'status_form': status_form,
        }

    def get(self, request, pk, *args, **kwargs):
        """Отображает карточку обращения с компактным переключателем статуса."""
        feedback = self._get_feedback(pk)
        status_form = AdminFeedbackMessageStatusForm(instance=feedback)
        return render(
            request,
            self.template_name,
            self._build_context(feedback, status_form),
        )

    def post(self, request, pk, *args, **kwargs):
        """Сохраняет новый статус обращения."""
        feedback = self._get_feedback(pk)
        status_form = AdminFeedbackMessageStatusForm(
            request.POST, instance=feedback
        )
        if status_form.is_valid():
            status_form.save()
            messages.success(
                request,
                f'Статус обращения #{feedback.pk} обновлён: '
                f'«{feedback.get_status_display()}».',
            )
            return redirect(
                'users:admin_feedback_message_detail', pk=feedback.pk
            )

        return render(
            request,
            self.template_name,
            self._build_context(feedback, status_form),
        )


class AdminReportsView(AdminRequiredMixin, TemplateView):
    """Страница админ-панели со ссылками на выгрузку отчётов в Excel.

    Выводит сводные цифры по системе (мероприятия / регистрации /
    участники) и три кнопки для скачивания XLSX-отчётов:
    по мероприятиям, по регистрациям и «всё в одном».
    """

    template_name = 'catalog/admin/reports.html'

    def get_context_data(self, **kwargs):
        """Добавляет агрегированные показатели для превью на странице."""
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'reports'

        context['events_total'] = Event.objects.count()
        context['events_published'] = Event.objects.filter(
            status=Event.Status.PUBLISHED
        ).count()
        context['events_completed'] = Event.objects.filter(
            status=Event.Status.COMPLETED
        ).count()

        context['registrations_total'] = EventRegistration.objects.count()
        context['registrations_confirmed'] = EventRegistration.objects.filter(
            status=EventRegistration.Status.CONFIRMED
        ).count()
        context['registrations_pending'] = EventRegistration.objects.filter(
            status=EventRegistration.Status.PENDING
        ).count()
        context['registrations_waitlist'] = EventRegistration.objects.filter(
            status=EventRegistration.Status.WAITLIST
        ).count()

        context['participants_unique'] = (
            EventRegistration.objects.values('user_id').distinct().count()
        )
        context['directions_total'] = Direction.objects.count()
        context['event_types_total'] = EventType.objects.count()

        return context


XLSX_CONTENT_TYPE = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)


def _workbook_response(workbook, filename: str) -> HttpResponse:
    """Сериализует ``openpyxl.Workbook`` в HTTP-ответ с XLSX-вложением."""
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type=XLSX_CONTENT_TYPE)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


class AdminEventsReportExcelView(AdminRequiredMixin, View):
    """Выгружает XLSX-отчёт по мероприятиям (с показателями по регистрациям)."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        """Возвращает сгенерированный Excel-файл как attachment."""
        workbook = report_builders.build_events_report()
        filename = report_builders.build_filename('events_report')
        return _workbook_response(workbook, filename)


class AdminRegistrationsReportExcelView(AdminRequiredMixin, View):
    """Выгружает XLSX-отчёт со всеми регистрациями пользователей."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        """Возвращает сгенерированный Excel-файл как attachment."""
        workbook = report_builders.build_registrations_report()
        filename = report_builders.build_filename('registrations_report')
        return _workbook_response(workbook, filename)


class AdminSummaryReportExcelView(AdminRequiredMixin, View):
    """Выгружает сводный XLSX-отчёт с несколькими листами."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        """Возвращает сгенерированный Excel-файл как attachment."""
        workbook = report_builders.build_summary_report()
        filename = report_builders.build_filename('summary_report')
        return _workbook_response(workbook, filename)
