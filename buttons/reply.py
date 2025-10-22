from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

translations = {
    "uz": "📝 Ro'yhatdan o'tish",
    "en": "📝 Register",
    "ru": "📝 Регистрация"
}


def get_menu(language: str):
    text = translations.get(language, translations["en"])

    register_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text)]
        ],
        resize_keyboard=True
    )
    return register_menu


share_contact_text = {
    "uz": "📲 Kontakt ulashish",
    "en": "📲 Share Contact",
    "ru": "📲 Поделиться контактом"
}


def get_phone(language: str):
    text = share_contact_text.get(language, translations["en"])

    phone = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text, request_contact=True)]
        ],
        resize_keyboard=True
    )
    return phone


check = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='✔️'),
        ],
        [
            KeyboardButton(text='/new'),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Select the required section'
)

messages = {
    "uz": "📝 Ruhsatnoma olish",
    "en": "📝 Get a permit",
    "ru": "📝 Получить разрешение"
}

change_language_text = {
    "uz": "🌐 Tilni o‘zgartirish",
    "en": "🌐 Change language",
    "ru": "🌐 Изменить язык"
}


def menu(language: str):
    text = messages.get(language, translations["en"])
    tet = change_language_text.get(language, change_language_text["en"])

    phone = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=text)
            ],
            [
                KeyboardButton(text=tet)
            ]
        ],
        resize_keyboard=True
    )
    return phone
