-- phpMyAdmin SQL Dump
-- version 5.1.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Apr 23, 2026 at 03:04 PM
-- Server version: 8.0.42
-- PHP Version: 8.0.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `seminar`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int NOT NULL,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 3, 'add_permission'),
(6, 'Can change permission', 3, 'change_permission'),
(7, 'Can delete permission', 3, 'delete_permission'),
(8, 'Can view permission', 3, 'view_permission'),
(9, 'Can add group', 2, 'add_group'),
(10, 'Can change group', 2, 'change_group'),
(11, 'Can delete group', 2, 'delete_group'),
(12, 'Can view group', 2, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add Пользователь', 6, 'add_user'),
(22, 'Can change Пользователь', 6, 'change_user'),
(23, 'Can delete Пользователь', 6, 'delete_user'),
(24, 'Can view Пользователь', 6, 'view_user'),
(25, 'Can add Научное направление', 7, 'add_direction'),
(26, 'Can change Научное направление', 7, 'change_direction'),
(27, 'Can delete Научное направление', 7, 'delete_direction'),
(28, 'Can view Научное направление', 7, 'view_direction'),
(29, 'Can add Тип мероприятия', 10, 'add_eventtype'),
(30, 'Can change Тип мероприятия', 10, 'change_eventtype'),
(31, 'Can delete Тип мероприятия', 10, 'delete_eventtype'),
(32, 'Can view Тип мероприятия', 10, 'view_eventtype'),
(33, 'Can add Мероприятие', 8, 'add_event'),
(34, 'Can change Мероприятие', 8, 'change_event'),
(35, 'Can delete Мероприятие', 8, 'delete_event'),
(36, 'Can view Мероприятие', 8, 'view_event'),
(37, 'Can add Регистрация на мероприятие', 9, 'add_eventregistration'),
(38, 'Can change Регистрация на мероприятие', 9, 'change_eventregistration'),
(39, 'Can delete Регистрация на мероприятие', 9, 'delete_eventregistration'),
(40, 'Can view Регистрация на мероприятие', 9, 'view_eventregistration'),
(41, 'Can add Обращение обратной связи', 12, 'add_feedbackmessage'),
(42, 'Can change Обращение обратной связи', 12, 'change_feedbackmessage'),
(43, 'Can delete Обращение обратной связи', 12, 'delete_feedbackmessage'),
(44, 'Can view Обращение обратной связи', 12, 'view_feedbackmessage'),
(45, 'Can add Отзыв о мероприятии', 11, 'add_eventreview'),
(46, 'Can change Отзыв о мероприятии', 11, 'change_eventreview'),
(47, 'Can delete Отзыв о мероприятии', 11, 'delete_eventreview'),
(48, 'Can view Отзыв о мероприятии', 11, 'view_eventreview'),
(49, 'Can add Тема обращения', 13, 'add_feedbacktopic'),
(50, 'Can change Тема обращения', 13, 'change_feedbacktopic'),
(51, 'Can delete Тема обращения', 13, 'delete_feedbacktopic'),
(52, 'Can view Тема обращения', 13, 'view_feedbacktopic'),
(53, 'Can add Закладка (избранное)', 14, 'add_eventbookmark'),
(54, 'Can change Закладка (избранное)', 14, 'change_eventbookmark'),
(55, 'Can delete Закладка (избранное)', 14, 'delete_eventbookmark'),
(56, 'Can view Закладка (избранное)', 14, 'view_eventbookmark');

-- --------------------------------------------------------

--
-- Table structure for table `catalog_direction`
--

CREATE TABLE `catalog_direction` (
  `id` bigint NOT NULL,
  `title` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `catalog_direction`
--

INSERT INTO `catalog_direction` (`id`, `title`, `slug`, `icon`, `description`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'Экономика и финансы', 'экономика-и-финансы', 'bi-bank', 'Макроэкономика, корпоративные финансы, цифровая экономика и рынки капитала.', 1, '2026-04-21 11:57:36.439966', '2026-04-21 11:57:36.439966'),
(2, 'Менеджмент', 'менеджмент', 'bi-briefcase', 'Стратегический и проектный менеджмент, HR, предпринимательство и управление инновациями.', 1, '2026-04-21 11:57:36.456210', '2026-04-21 11:57:36.456210'),
(3, 'Юриспруденция', 'юриспруденция', 'bi-shield-check', 'Гражданское, предпринимательское и цифровое право, правовое регулирование новых технологий.', 1, '2026-04-21 11:57:36.460179', '2026-04-21 11:57:36.460179'),
(4, 'Информационные технологии', 'информационные-технологии', 'bi-cpu', 'Искусственный интеллект, анализ данных, информационная безопасность и разработка ПО.', 1, '2026-04-21 11:57:36.462686', '2026-04-21 11:57:36.462686'),
(5, 'Педагогика и психология', 'педагогика-и-психология', 'bi-mortarboard', 'Образовательные технологии, психология развития, дистанционное обучение и воспитание.', 1, '2026-04-21 11:57:36.465704', '2026-04-21 11:57:36.465704'),
(6, 'Гуманитарные науки', 'гуманитарные-науки', 'bi-globe', 'Социология, история, лингвистика и межкультурные коммуникации в современном обществе.', 1, '2026-04-21 11:57:36.468753', '2026-04-21 11:57:36.468753');

-- --------------------------------------------------------

--
-- Table structure for table `catalog_event`
--

CREATE TABLE `catalog_event` (
  `id` bigint NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `short_description` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_format` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `starts_at` datetime(6) NOT NULL,
  `ends_at` datetime(6) DEFAULT NULL,
  `location` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `online_url` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `seats_total` int UNSIGNED NOT NULL,
  `cover` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_featured` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `direction_id` bigint NOT NULL,
  `organizer_id` bigint DEFAULT NULL,
  `event_type_id` bigint NOT NULL,
  `allow_waitlist` tinyint(1) NOT NULL,
  `registration_closes_at` datetime(6) DEFAULT NULL,
  `registration_opens_at` datetime(6) DEFAULT NULL,
  `requires_approval` tinyint(1) NOT NULL
) ;

--
-- Dumping data for table `catalog_event`
--

INSERT INTO `catalog_event` (`id`, `title`, `slug`, `short_description`, `description`, `event_format`, `starts_at`, `ends_at`, `location`, `online_url`, `seats_total`, `cover`, `status`, `is_featured`, `created_at`, `updated_at`, `direction_id`, `organizer_id`, `event_type_id`, `allow_waitlist`, `registration_closes_at`, `registration_opens_at`, `requires_approval`) VALUES
(1, 'Международная конференция «Искусственный интеллект — 2026»', 'международная-конференция-искусственный-интеллект-2026', 'Три дня докладов, воркшопов и панельных дискуссий ведущих специалистов в области искусственного интеллекта и анализа данных.', 'Международная научно-практическая конференция объединяет исследователей, преподавателей и представителей индустрии. В программе — пленарные доклады, секционные заседания по машинному обучению, компьютерному зрению и этике ИИ, а также мастер-классы и нетворкинг.', 'offline', '2026-06-15 07:00:00.000000', '2026-06-17 15:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, Актовый зал', '', 250, '', 'published', 1, '2026-04-21 12:02:05.247261', '2026-04-21 12:02:05.247261', 4, NULL, 1, 1, NULL, NULL, 0),
(2, 'Цифровая экономика: вызовы и возможности 2026', 'цифровая-экономика-вызовы-и-возможности-2026', 'Онлайн-семинар о трансформации экономических моделей в эпоху цифровых платформ и блокчейн-технологий.', 'Ведущие экономисты университета и приглашённые эксперты обсудят влияние цифровизации на финансовые рынки, налогообложение и корпоративное управление.', 'online', '2026-05-12 11:00:00.000000', '2026-05-12 14:30:00.000000', '', 'https://meet.muiv.ru/digital-economy-2026', 500, '', 'published', 0, '2026-04-21 12:02:05.255791', '2026-04-21 12:02:05.255791', 1, NULL, 2, 1, NULL, NULL, 0),
(3, 'Круглый стол «Право и технологии: регулирование ИИ»', 'круглый-стол-право-и-технологии-регулирование-ии', 'Дискуссия о правовом регулировании искусственного интеллекта, защите данных и ответственности разработчиков.', 'Юристы, представители бизнеса и IT-специалисты обсудят актуальные законодательные инициативы, практику применения норм о персональных данных и границы ответственности за решения, принятые алгоритмами.', 'hybrid', '2026-07-08 08:00:00.000000', '2026-07-08 12:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, ауд. 305', 'https://meet.muiv.ru/law-ai-2026', 80, '', 'published', 1, '2026-04-21 12:02:05.261793', '2026-04-21 12:02:05.261793', 3, NULL, 3, 1, NULL, NULL, 0),
(4, 'Педагогика цифрового поколения', 'педагогика-цифрового-поколения', 'Открытая онлайн-лекция о методиках обучения школьников и студентов в условиях цифровой среды.', 'Лектор рассмотрит практические подходы к геймификации, микрообучению и формированию цифровых компетенций у обучающихся разных возрастных групп.', 'online', '2026-05-20 15:00:00.000000', '2026-05-20 17:00:00.000000', '', 'https://meet.muiv.ru/edu-lecture-2026', 0, '', 'published', 0, '2026-04-21 12:02:05.267729', '2026-04-21 12:02:05.267729', 5, NULL, 5, 1, NULL, NULL, 0),
(5, 'Научные чтения памяти С.Ю. Витте', 'научные-чтения-памяти-сю-витте', 'Ежегодные чтения, посвящённые наследию выдающегося государственного деятеля и реформатора.', 'Историки, экономисты и политологи представят доклады об экономических реформах конца XIX — начала XX века и их актуальности для современной России.', 'offline', '2026-10-03 07:00:00.000000', '2026-10-03 14:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, Большой зал', '', 180, '', 'published', 1, '2026-04-21 12:02:05.272194', '2026-04-21 12:02:05.272194', 6, NULL, 4, 1, NULL, NULL, 0),
(6, 'Воркшоп «Data Science для начинающих исследователей»', 'воркшоп-data-science-для-начинающих-исследователей', 'Практический воркшоп по работе с данными на Python: pandas, визуализация и первые ML-модели.', 'Участники на практике пройдут полный цикл исследования: от загрузки датасета и очистки данных до построения простой модели регрессии и интерпретации результатов.', 'hybrid', '2026-09-18 10:00:00.000000', '2026-09-18 15:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, Компьютерный класс 214', 'https://meet.muiv.ru/ds-workshop-2026', 40, '', 'published', 0, '2026-04-21 12:02:05.276255', '2026-04-21 12:02:05.276255', 4, NULL, 6, 1, NULL, NULL, 0),
(7, 'HR-менеджмент в эпоху искусственного интеллекта', 'hr-менеджмент-в-эпоху-искусственного-интеллекта', 'Двухдневная конференция о цифровой трансформации управления персоналом: подбор, обучение, аналитика.', 'HR-директора крупных компаний и исследователи обсудят внедрение AI-инструментов в рекрутинг, системы оценки эффективности, программы корпоративного обучения и управление вовлечённостью сотрудников.', 'hybrid', '2026-11-05 07:00:00.000000', '2026-11-06 14:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, Конференц-зал', 'https://meet.muiv.ru/hr-ai-2026', 150, '', 'published', 0, '2026-04-21 12:02:05.280195', '2026-04-21 12:02:05.280195', 2, NULL, 1, 1, NULL, NULL, 0),
(8, 'Финансовые рынки: прогноз на 2027 год', 'финансовые-рынки-прогноз-на-2027-год', 'Аналитический семинар о динамике рынков капитала, денежно-кредитной политике и инвестиционных стратегиях.', 'Эксперты представят макроэкономические прогнозы, сценарии развития фондового и валютного рынков, а также рекомендации по управлению портфелем в условиях глобальной неопределённости.', 'offline', '2027-01-22 12:00:00.000000', '2027-01-22 15:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, ауд. 401', '', 100, '', 'published', 0, '2026-04-21 12:02:05.285761', '2026-04-21 12:02:05.285761', 1, NULL, 2, 1, NULL, NULL, 0),
(9, 'История российской философии XIX века', 'история-российской-философии-xix-века', 'Чтения, посвящённые ключевым фигурам русской философской мысли: Соловьёв, Бердяев, Флоренский.', 'Философы и историки университета представили доклады о влиянии русской религиозной философии на европейскую интеллектуальную традицию и её актуальности сегодня.', 'offline', '2026-03-25 11:00:00.000000', '2026-03-25 15:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, Библиотека', '', 60, '', 'completed', 0, '2026-04-21 12:02:05.289805', '2026-04-21 12:02:05.289805', 6, NULL, 4, 1, NULL, NULL, 0),
(10, 'Стратегии корпоративного развития и устойчивый рост', 'стратегии-корпоративного-развития-и-устойчивый-рост', 'Круглый стол для топ-менеджеров о построении долгосрочных стратегий в условиях нестабильности рынков.', 'Участники обсудят модели устойчивого развития, ESG-стратегии, цифровую трансформацию и подходы к управлению рисками на горизонте 5–10 лет.', 'offline', '2026-12-14 08:00:00.000000', '2026-12-14 13:00:00.000000', 'г. Москва, 2-й Кожуховский пр-д, 12, ауд. 501', '', 70, '', 'draft', 0, '2026-04-21 12:02:05.294338', '2026-04-21 12:02:05.294338', 2, NULL, 3, 1, NULL, NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `catalog_eventbookmark`
--

CREATE TABLE `catalog_eventbookmark` (
  `id` bigint NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `event_id` bigint NOT NULL,
  `user_id` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `catalog_eventregistration`
--

CREATE TABLE `catalog_eventregistration` (
  `id` bigint NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `note` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `event_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `cancellation_reason` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `cancelled_at` datetime(6) DEFAULT NULL,
  `cancelled_by_id` bigint DEFAULT NULL,
  `confirmed_at` datetime(6) DEFAULT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `organization` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `position` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `waitlist_position` int UNSIGNED DEFAULT NULL
) ;

--
-- Dumping data for table `catalog_eventregistration`
--

INSERT INTO `catalog_eventregistration` (`id`, `status`, `note`, `created_at`, `updated_at`, `event_id`, `user_id`, `cancellation_reason`, `cancelled_at`, `cancelled_by_id`, `confirmed_at`, `email`, `full_name`, `organization`, `phone`, `position`, `source`, `waitlist_position`) VALUES
(1, 'confirmed', '', '2026-04-22 11:59:43.649481', '2026-04-22 11:59:43.649481', 2, 4, '', NULL, NULL, '2026-04-22 11:59:43.648474', 'viktor@gmail.com', 'Федоров Виктор', 'Управление Бизнесом', '324234', 'Студент', 'self', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `catalog_eventreview`
--

CREATE TABLE `catalog_eventreview` (
  `id` bigint NOT NULL,
  `author_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `author_email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rating` smallint UNSIGNED NOT NULL,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `text` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `pros` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `cons` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `moderation_note` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `moderated_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `event_id` bigint NOT NULL,
  `moderated_by_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL
) ;

-- --------------------------------------------------------

--
-- Table structure for table `catalog_eventtype`
--

CREATE TABLE `catalog_eventtype` (
  `id` bigint NOT NULL,
  `title` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `catalog_eventtype`
--

INSERT INTO `catalog_eventtype` (`id`, `title`, `slug`, `icon`, `is_active`) VALUES
(1, 'Конференция', 'конференция', 'bi-people', 1),
(2, 'Семинар', 'семинар', 'bi-chat-square-text', 1),
(3, 'Круглый стол', 'круглый-стол', 'bi-diagram-3', 1),
(4, 'Научные чтения', 'научные-чтения', 'bi-book', 1),
(5, 'Лекция', 'лекция', 'bi-mic', 1),
(6, 'Воркшоп', 'воркшоп', 'bi-tools', 1);

-- --------------------------------------------------------

--
-- Table structure for table `catalog_feedbackmessage`
--

CREATE TABLE `catalog_feedbackmessage` (
  `id` bigint NOT NULL,
  `full_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `organization` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `consent_to_processing` tinyint(1) NOT NULL,
  `subscribe_to_news` tinyint(1) NOT NULL,
  `ip_address` char(39) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `referer` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `admin_note` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `answered_at` datetime(6) DEFAULT NULL,
  `answer_text` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `answered_by_id` bigint DEFAULT NULL,
  `assigned_to_id` bigint DEFAULT NULL,
  `related_event_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `topic_id` bigint DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `catalog_feedbackmessage`
--

INSERT INTO `catalog_feedbackmessage` (`id`, `full_name`, `email`, `phone`, `organization`, `subject`, `message`, `consent_to_processing`, `subscribe_to_news`, `ip_address`, `user_agent`, `referer`, `source`, `status`, `admin_note`, `answered_at`, `answer_text`, `created_at`, `updated_at`, `answered_by_id`, `assigned_to_id`, `related_event_id`, `user_id`, `topic_id`) VALUES
(1, 'Федоров Виктор', 'viktor@gmail.com', '349857', 'Тестовая', 'Тестовое', 'Тестовое Тестовое Тестовое Тестовое', 1, 1, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36', 'http://127.0.0.1:8000/feedback/', 'contact_form', 'answered', '', NULL, '', '2026-04-22 11:37:00.901725', '2026-04-22 11:48:07.843313', NULL, NULL, NULL, 4, 5);

-- --------------------------------------------------------

--
-- Table structure for table `catalog_feedbacktopic`
--

CREATE TABLE `catalog_feedbacktopic` (
  `id` bigint NOT NULL,
  `title` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `order` int UNSIGNED NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ;

--
-- Dumping data for table `catalog_feedbacktopic`
--

INSERT INTO `catalog_feedbacktopic` (`id`, `title`, `slug`, `description`, `icon`, `order`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'Вопрос по мероприятию', 'вопрос-по-мероприятию', 'Уточнить программу, место, время проведения или условия участия в конкретной конференции, семинаре или лекции.', 'bi-calendar2-event', 10, 1, '2026-04-22 11:16:10.885218', '2026-04-22 11:16:10.885218'),
(2, 'Регистрация и личный кабинет', 'регистрация-и-личный-кабинет', 'Не удаётся зарегистрироваться, подтвердить email, восстановить пароль или подать заявку на участие.', 'bi-person-badge', 20, 1, '2026-04-22 11:16:10.893223', '2026-04-22 11:16:10.893223'),
(3, 'Предложить своё мероприятие', 'предложить-своё-мероприятие', 'Вы хотите провести научное мероприятие и разместить его в электронном каталоге университета.', 'bi-lightbulb', 30, 1, '2026-04-22 11:16:10.907219', '2026-04-22 11:16:10.907219'),
(4, 'Сотрудничество и партнёрство', 'сотрудничество-и-партнёрство', 'Предложения о совместных проектах, академическом партнёрстве или информационной поддержке.', 'bi-people', 40, 1, '2026-04-22 11:16:10.910218', '2026-04-22 11:16:10.910218'),
(5, 'Работа со СМИ и информационный запрос', 'работа-со-сми-и-информационный-запрос', 'Аккредитация журналистов, комментарии экспертов, пресс-релизы и публикации о мероприятиях центра.', 'bi-megaphone', 50, 1, '2026-04-22 11:16:10.912218', '2026-04-22 11:16:10.912218'),
(6, 'Техническая проблема на сайте', 'техническая-проблема-на-сайте', 'Сайт медленно работает, страница не открывается, кнопка не реагирует или отображается ошибка.', 'bi-bug', 60, 1, '2026-04-22 11:16:10.915217', '2026-04-22 11:16:10.915217'),
(7, 'Предложение по улучшению сервиса', 'предложение-по-улучшению-сервиса', 'Идеи, как сделать электронный каталог удобнее, и пожелания к новым функциям.', 'bi-stars', 70, 1, '2026-04-22 11:16:10.918218', '2026-04-22 11:16:10.918218'),
(8, 'Отзыв о мероприятии', 'отзыв-о-мероприятии', 'Поделиться впечатлениями о посещённом мероприятии — положительными и теми, что стоит улучшить.', 'bi-chat-heart', 80, 1, '2026-04-22 11:16:10.920219', '2026-04-22 11:16:10.920219'),
(9, 'Жалоба или претензия', 'жалоба-или-претензия', 'Сообщить о нарушении, некорректном контенте или иных серьёзных проблемах, требующих разбирательства.', 'bi-exclamation-octagon', 90, 1, '2026-04-22 11:16:10.923278', '2026-04-22 11:16:10.923278'),
(10, 'Другой вопрос', 'другой-вопрос', 'Тема не подходит ни под одну из категорий выше — просто опишите ваш вопрос в сообщении.', 'bi-chat-dots', 999, 1, '2026-04-22 11:16:10.926217', '2026-04-22 11:16:10.926217');

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL
) ;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int NOT NULL,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(2, 'auth', 'group'),
(3, 'auth', 'permission'),
(7, 'catalog', 'direction'),
(8, 'catalog', 'event'),
(14, 'catalog', 'eventbookmark'),
(9, 'catalog', 'eventregistration'),
(11, 'catalog', 'eventreview'),
(10, 'catalog', 'eventtype'),
(12, 'catalog', 'feedbackmessage'),
(13, 'catalog', 'feedbacktopic'),
(4, 'contenttypes', 'contenttype'),
(5, 'sessions', 'session'),
(6, 'users', 'user');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-04-20 12:56:55.630486'),
(2, 'contenttypes', '0002_remove_content_type_name', '2026-04-20 12:56:56.901563'),
(3, 'auth', '0001_initial', '2026-04-20 12:56:59.678250'),
(4, 'auth', '0002_alter_permission_name_max_length', '2026-04-20 12:57:00.224013'),
(5, 'auth', '0003_alter_user_email_max_length', '2026-04-20 12:57:00.285345'),
(6, 'auth', '0004_alter_user_username_opts', '2026-04-20 12:57:00.326190'),
(7, 'auth', '0005_alter_user_last_login_null', '2026-04-20 12:57:00.385196'),
(8, 'auth', '0006_require_contenttypes_0002', '2026-04-20 12:57:00.417602'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2026-04-20 12:57:00.488748'),
(10, 'auth', '0008_alter_user_username_max_length', '2026-04-20 12:57:00.543840'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2026-04-20 12:57:00.569995'),
(12, 'auth', '0010_alter_group_name_max_length', '2026-04-20 12:57:00.671001'),
(13, 'auth', '0011_update_proxy_permissions', '2026-04-20 12:57:00.714307'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2026-04-20 12:57:00.755318'),
(15, 'users', '0001_initial', '2026-04-20 12:57:04.404170'),
(16, 'admin', '0001_initial', '2026-04-20 12:57:05.841541'),
(17, 'admin', '0002_logentry_remove_auto_add', '2026-04-20 12:57:05.877242'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2026-04-20 12:57:05.930422'),
(19, 'catalog', '0001_initial', '2026-04-20 12:57:11.861168'),
(20, 'sessions', '0001_initial', '2026-04-20 12:57:12.283111'),
(21, 'catalog', '0002_seed_directions_and_event_types', '2026-04-21 11:57:36.527988'),
(22, 'catalog', '0003_seed_sample_events', '2026-04-21 12:02:05.337447'),
(23, 'catalog', '0004_remove_eventregistration_unique_event_user_registration_and_more', '2026-04-21 12:23:45.929182'),
(24, 'catalog', '0005_feedbacktopic_eventreview_feedbackmessage', '2026-04-22 11:09:55.888914'),
(25, 'catalog', '0006_seed_feedback_topics', '2026-04-22 11:16:10.960839'),
(26, 'catalog', '0007_eventbookmark', '2026-04-23 13:59:52.534247');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('v1rtsd0cw81ovhvzu4iiw3mzmpcn2e14', '.eJxVjM0OwiAQhN-FsyHyU7Z49O4zkGUXpGogKe3J-O62SQ96nPm-mbcIuC4lrD3NYWJxEVacfruI9Ex1B_zAem-SWl3mKcpdkQft8tY4va6H-3dQsJdtDTA6rxWf0aOCiBBBs7OUKEcyftiic8DJAFnWI2eyRvOgs1LJqwji8wXmwDgQ:1wFtfO:zcR5bPgEB-krOPDXChf9WgIwucLc1qmnlt7KGL_gFHw', '2026-05-07 13:00:26.469272');

-- --------------------------------------------------------

--
-- Table structure for table `users_user`
--

CREATE TABLE `users_user` (
  `id` bigint NOT NULL,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `patronymic` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `organization` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `position` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users_user`
--

INSERT INTO `users_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`, `patronymic`, `phone`, `organization`, `position`, `created_at`, `updated_at`) VALUES
(1, 'pbkdf2_sha256$1200000$QrDK0Gb2txI5vK1rGp63ta$71yHE7m2yQQco0+/GSqOmj7DG5N5XRgHaNeGQtppmxQ=', '2026-04-23 10:47:47.095887', 1, 'admin', '', '', 'admin@gmail.com', 1, 1, '2026-04-21 10:32:22.113559', 'admin', '', '', '', '', '2026-04-21 10:32:23.167604', '2026-04-21 10:32:23.167604'),
(3, 'pbkdf2_sha256$1200000$mFhnadfUOv56KqIWweMYfn$TgpeuspUxxD7NjNRlsAAqCIffLMqJ1g0YLHYluC3el4=', '2026-04-23 10:47:18.216008', 0, 'aleks', 'Александр', 'Васильевич', 'aleksandr@gmail.com', 0, 1, '2026-04-21 10:41:43.007817', 'curator', '', '', '', '', '2026-04-21 10:41:43.918388', '2026-04-21 10:43:39.314375'),
(4, 'pbkdf2_sha256$1200000$HoGTd7imvhLzSgoby9iTaZ$vRr8btc65hS1X/SYqQn05m7/U9I67xpxxxgYME4sQHE=', '2026-04-23 13:00:26.425987', 0, 'viktoor', 'Виктор', 'Федоров', 'viktor@gmail.com', 0, 1, '2026-04-21 12:20:57.981484', 'user', '', '', '', '', '2026-04-21 12:20:59.437708', '2026-04-21 12:20:59.437708');

-- --------------------------------------------------------

--
-- Table structure for table `users_user_groups`
--

CREATE TABLE `users_user_groups` (
  `id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users_user_user_permissions`
--

CREATE TABLE `users_user_user_permissions` (
  `id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `catalog_direction`
--
ALTER TABLE `catalog_direction`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `title` (`title`),
  ADD UNIQUE KEY `slug` (`slug`);

--
-- Indexes for table `catalog_event`
--
ALTER TABLE `catalog_event`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `slug` (`slug`),
  ADD KEY `catalog_eve_starts__4e9af6_idx` (`starts_at` DESC),
  ADD KEY `catalog_eve_status_0caf37_idx` (`status`,`starts_at` DESC),
  ADD KEY `catalog_eve_event_f_364985_idx` (`event_format`),
  ADD KEY `catalog_event_direction_id_919678ef_fk_catalog_direction_id` (`direction_id`),
  ADD KEY `catalog_event_organizer_id_c22c634f_fk_users_user_id` (`organizer_id`),
  ADD KEY `catalog_event_event_type_id_e594b96e_fk_catalog_eventtype_id` (`event_type_id`);

--
-- Indexes for table `catalog_eventbookmark`
--
ALTER TABLE `catalog_eventbookmark`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `catalog_eventbookmark_user_id_event_id_e4bb5b39_uniq` (`user_id`,`event_id`),
  ADD KEY `catalog_eventbookmark_event_id_e2059656_fk_catalog_event_id` (`event_id`),
  ADD KEY `catalog_eve_user_id_9742db_idx` (`user_id`,`created_at` DESC);

--
-- Indexes for table `catalog_eventregistration`
--
ALTER TABLE `catalog_eventregistration`
  ADD PRIMARY KEY (`id`),
  ADD KEY `catalog_eve_event_i_6123f7_idx` (`event_id`,`status`),
  ADD KEY `catalog_eventregistr_cancelled_by_id_d28bc251_fk_users_use` (`cancelled_by_id`),
  ADD KEY `catalog_eve_user_id_4cffe7_idx` (`user_id`,`status`),
  ADD KEY `catalog_eve_event_i_5aee9b_idx` (`event_id`,`waitlist_position`);

--
-- Indexes for table `catalog_eventreview`
--
ALTER TABLE `catalog_eventreview`
  ADD PRIMARY KEY (`id`),
  ADD KEY `catalog_eventreview_moderated_by_id_0376506f_fk_users_user_id` (`moderated_by_id`),
  ADD KEY `catalog_eve_event_i_d08b1d_idx` (`event_id`,`status`,`created_at` DESC),
  ADD KEY `catalog_eve_status_c61edf_idx` (`status`,`created_at` DESC),
  ADD KEY `catalog_eve_user_id_89b089_idx` (`user_id`,`created_at` DESC);

--
-- Indexes for table `catalog_eventtype`
--
ALTER TABLE `catalog_eventtype`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `title` (`title`),
  ADD UNIQUE KEY `slug` (`slug`);

--
-- Indexes for table `catalog_feedbackmessage`
--
ALTER TABLE `catalog_feedbackmessage`
  ADD PRIMARY KEY (`id`),
  ADD KEY `catalog_feedbackmessage_answered_by_id_d99a53c5_fk_users_user_id` (`answered_by_id`),
  ADD KEY `catalog_feedbackmessage_assigned_to_id_b9f69302_fk_users_user_id` (`assigned_to_id`),
  ADD KEY `catalog_feedbackmess_related_event_id_1b91e9d1_fk_catalog_e` (`related_event_id`),
  ADD KEY `catalog_feedbackmess_topic_id_4e7243fe_fk_catalog_f` (`topic_id`),
  ADD KEY `catalog_fee_created_06c3a0_idx` (`created_at` DESC),
  ADD KEY `catalog_fee_status_a686a0_idx` (`status`,`created_at` DESC),
  ADD KEY `catalog_fee_email_00a90d_idx` (`email`),
  ADD KEY `catalog_fee_user_id_b129ba_idx` (`user_id`,`created_at` DESC);

--
-- Indexes for table `catalog_feedbacktopic`
--
ALTER TABLE `catalog_feedbacktopic`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `title` (`title`),
  ADD UNIQUE KEY `slug` (`slug`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_users_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `users_user`
--
ALTER TABLE `users_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `users_user_role_36d76d_idx` (`role`);

--
-- Indexes for table `users_user_groups`
--
ALTER TABLE `users_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_user_groups_user_id_group_id_b88eab82_uniq` (`user_id`,`group_id`),
  ADD KEY `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `users_user_user_permissions`
--
ALTER TABLE `users_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_user_user_permissions_user_id_permission_id_43338c45_uniq` (`user_id`,`permission_id`),
  ADD KEY `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` (`permission_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=57;

--
-- AUTO_INCREMENT for table `catalog_direction`
--
ALTER TABLE `catalog_direction`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `catalog_event`
--
ALTER TABLE `catalog_event`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `catalog_eventbookmark`
--
ALTER TABLE `catalog_eventbookmark`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `catalog_eventregistration`
--
ALTER TABLE `catalog_eventregistration`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `catalog_eventreview`
--
ALTER TABLE `catalog_eventreview`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `catalog_eventtype`
--
ALTER TABLE `catalog_eventtype`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `catalog_feedbackmessage`
--
ALTER TABLE `catalog_feedbackmessage`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `catalog_feedbacktopic`
--
ALTER TABLE `catalog_feedbacktopic`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `users_user`
--
ALTER TABLE `users_user`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users_user_groups`
--
ALTER TABLE `users_user_groups`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users_user_user_permissions`
--
ALTER TABLE `users_user_user_permissions`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `catalog_event`
--
ALTER TABLE `catalog_event`
  ADD CONSTRAINT `catalog_event_direction_id_919678ef_fk_catalog_direction_id` FOREIGN KEY (`direction_id`) REFERENCES `catalog_direction` (`id`),
  ADD CONSTRAINT `catalog_event_event_type_id_e594b96e_fk_catalog_eventtype_id` FOREIGN KEY (`event_type_id`) REFERENCES `catalog_eventtype` (`id`),
  ADD CONSTRAINT `catalog_event_organizer_id_c22c634f_fk_users_user_id` FOREIGN KEY (`organizer_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `catalog_eventbookmark`
--
ALTER TABLE `catalog_eventbookmark`
  ADD CONSTRAINT `catalog_eventbookmark_event_id_e2059656_fk_catalog_event_id` FOREIGN KEY (`event_id`) REFERENCES `catalog_event` (`id`),
  ADD CONSTRAINT `catalog_eventbookmark_user_id_5132dc78_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `catalog_eventregistration`
--
ALTER TABLE `catalog_eventregistration`
  ADD CONSTRAINT `catalog_eventregistr_cancelled_by_id_d28bc251_fk_users_use` FOREIGN KEY (`cancelled_by_id`) REFERENCES `users_user` (`id`),
  ADD CONSTRAINT `catalog_eventregistration_event_id_802a2967_fk_catalog_event_id` FOREIGN KEY (`event_id`) REFERENCES `catalog_event` (`id`),
  ADD CONSTRAINT `catalog_eventregistration_user_id_a76a5d0c_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `catalog_eventreview`
--
ALTER TABLE `catalog_eventreview`
  ADD CONSTRAINT `catalog_eventreview_event_id_e49262f5_fk_catalog_event_id` FOREIGN KEY (`event_id`) REFERENCES `catalog_event` (`id`),
  ADD CONSTRAINT `catalog_eventreview_moderated_by_id_0376506f_fk_users_user_id` FOREIGN KEY (`moderated_by_id`) REFERENCES `users_user` (`id`),
  ADD CONSTRAINT `catalog_eventreview_user_id_207ef5ce_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `catalog_feedbackmessage`
--
ALTER TABLE `catalog_feedbackmessage`
  ADD CONSTRAINT `catalog_feedbackmess_related_event_id_1b91e9d1_fk_catalog_e` FOREIGN KEY (`related_event_id`) REFERENCES `catalog_event` (`id`),
  ADD CONSTRAINT `catalog_feedbackmess_topic_id_4e7243fe_fk_catalog_f` FOREIGN KEY (`topic_id`) REFERENCES `catalog_feedbacktopic` (`id`),
  ADD CONSTRAINT `catalog_feedbackmessage_answered_by_id_d99a53c5_fk_users_user_id` FOREIGN KEY (`answered_by_id`) REFERENCES `users_user` (`id`),
  ADD CONSTRAINT `catalog_feedbackmessage_assigned_to_id_b9f69302_fk_users_user_id` FOREIGN KEY (`assigned_to_id`) REFERENCES `users_user` (`id`),
  ADD CONSTRAINT `catalog_feedbackmessage_user_id_121bdd5d_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `users_user_groups`
--
ALTER TABLE `users_user_groups`
  ADD CONSTRAINT `users_user_groups_group_id_9afc8d0e_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `users_user_groups_user_id_5f6f5a90_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);

--
-- Constraints for table `users_user_user_permissions`
--
ALTER TABLE `users_user_user_permissions`
  ADD CONSTRAINT `users_user_user_perm_permission_id_0b93982e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `users_user_user_permissions_user_id_20aca447_fk_users_user_id` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
