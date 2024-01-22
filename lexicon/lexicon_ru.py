LEXICON_MENU_RU: dict[str, str] = {
    '/help': 'Справка по работе бота',
    '/home': '🏠В главное меню',
}

LEXICON_INLINE_MENU_RU: dict[str, str] = {
    'about': 'Обо мне',
    'view_practises': 'Смотреть практики',
    'user_message': 'Написать сообщение',
}

LEXICON_INLINE_ADMIN_MENU_RU: dict[str, str] = {
    'manage_practises': 'Управлять практиками',
    'manage_page:start': 'Редактировать начальный пост',
    'manage_page:about': 'Редактировать раздел "Обо мне"',
}

LEXICON_INLINE_ADMIN_PRACTISE_NAV_MENU: dict[str, str] = {
    'manage_practises': '📄 Назад с списку практик',
    'delete_practise': '✖ Удалить практику',
}

LEXICON_INLINE_ADMIN_POST_NAV_MENU: dict[str, str] = {
    'manage_page:': '📄 Назад с списку постов',
    'delete_post': '✖ Удалить пост',
}

LEXICON_INLINE_VIEW_PRACTISE_NAV_MENU: dict[str, str] = {
    'view_practises': '📄 Назад с списку практик',
}

LEXICON_INLINE_ADMIN_MEDIA_NAV_MENU: dict[str, str] = {
    'practise:': '📄 Назад к редактированию практики',
    'delete_media': '✖ Удалить урок',
}

LEXICON_INLINE_VIEW_MEDIA_NAV_MENU: dict[str, str] = {
    'view_practise:': '📄 Назад к практике',
}

LEXICON_INLINE_PRACTISE_MENU_RU: dict[str, str] = {
    'add_practise': 'Добавить новую практику',
}

LEXICON_INLINE_POST_MENU_RU: dict[str, str] = {
    'add_post': 'Добавить новый пост',
}

LEXICON_BTN_GROUP_LABELS_RU: dict[str, str] = {
    'start_menu': 'Чем я могу Вам помочь?',
    'practise_list': 'Выберите практику для редактирования/удаления',
    'practise_actions': 'Выберите желаемое действие',
    'post_actions': 'Выберите желаемое действие',
    'post_list': 'Выберите пост для редактирования/удаления',
}

LEXICON_CHAPTER_LABELS_RU: dict[str, str] = {
    'manage_practise': '👉 УПРАВЛЕНИЕ ПРАКТИКАМИ',
    'home': '👉 ГЛАВНОЕ МЕНЮ',
    'edit_practise': '👉 РЕДАКТИРОВАНИЕ ПРАКТИКИ',
    'edit_media': '👉 РЕДАКТИРОВАНИЕ УРОКА',
    'edit_post': '👉 РЕДАКТИРОВАНИЕ ПОСТА',
    'user_message': '👉 ОТПРАВКА СООБЩЕНИЙ (вы можете отправлять текст, фото и видео), я все обязательно прочитаю и напишу Вам ответ!',
    'view_practises': '👇 ДОСТУПНЫЕ ДЛЯ ПРОСМОТРА ПРАКТИКИ',
    'view_practise_selected': '🧘🧘🧘 ПРАКТИКА 🧘🧘🧘',
    'view_lesson_selected': '🧘 ЗАНЯТИЕ 🧘',
    'manage_page': 'УПРАВЛЯТЬ СТРАНИЦЕЙ',
}

LEXICON_CHAPTER_EXIT_RU: dict[str, str] = {
    'practise_exit': '🏠 Закончить и выйти в главное меню',
    'post_exit': '🏠 Закончить и выйти в главное меню',
    'about_exit': '🏠 Выйти в главное меню',
}

LEXICON_DEFAULT_NAMES_RU: dict[str, str] = {
    'practise_title': 'Новая практика...',
    'media_title': 'Новый урок...',
    'post_name': 'Новый пост...',
    'practise_description': 'Измените описание практики...',
    'media_description': 'Измените описание урока...',
    'title': 'Заголовок',
    'name': 'Имя',
    'change': 'Изменить',
    'description': 'Описание',
    'order': 'Порядок следования',
    'media_content': 'Медиа-контент',
    'media_content_empty': 'Сюда пока ничего не загружено',
    'post_change_name': 'Укажите новое имя поста 👇',
    'post_change_order': 'Укажите порядок поста 👇',
    'post_change_post': 'Напишите пост (или загрузите фото, видео, группу медиа-объектов) 👇',
    'practise_change_title': 'Укажите новый заголовок для практики 👇',
    'practise_change_description': 'Укажите новое описание для практики 👇',
    'practise_change_media': 'Загрузите медиа-контент (фото или видео-файл)',
    'media_change_title': 'Укажите новый заголовок для урока 👇',
    'media_change_category': 'Укажите категорию подготовки для ученика 👇',
    'media_change_description': 'Укажите новое описание для урока 👇',
    'media_change_media': 'Загрузите медиа-контент (фото или видео-файл)',
    'media_change_cost': 'Укажите стоимость урока (в рублях, без дробной части)',
    'practise_navigation_menu': '\n ☸☸☸ Навигационное меню ☸☸☸',
    'delete_success': 'Успешно удалено!',
    'practise_content_published': 'Практика опубликована!',
    'practise_content_not_published': 'Практика еще не опубликована',
    'media_content_free': 'Урок бесплатный',
    'media_content_not_free': 'Урок платный',
    'add_media': '✚ Добавить урок',
    'lessons': '\n   Доступные уроки\n',
    'media_cost': '$ Стоимость урока',
    'media_category': 'Категория ученика',
    'success_swap': 'Порядок успешно изменен!',
    'choose_practise': 'Выберите практику:',
    'invite_payment': '''\nКонтент данного урока платный.\nВы можете оплатить урок прямо в Telegram, это абсолютно безопасно.''',
    'payment_cost': 'Стоимость урока: ',
    'pay': 'Начать процесс оплаты',
    'payment_description': 'Оплата за получение услуги на сервисе @YogaMasterMindBot',
}

LEXICON_BTN_LABELS_RU: dict[str, str] = {
    'cancel_edit': '✖ Отменить редактирование',
}

LEXICON_MEDIA_CATEGORIES_RU: dict[str, str] = {
    'any': "Любой",
    'novice': "Новичек",
    'advanced': "Продвинутый",
}


LEXICON_BASIC_BTNS_RU: dict[str, str] = {
    'back': "◀️Назад",
}

LEXICON_DEFAULT_MESSGES_RU: dict[str, str] = {
    'message_sent': "✉ Сообщение успешно отправлено",
}
