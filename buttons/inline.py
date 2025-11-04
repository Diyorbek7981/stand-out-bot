from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CHANNEL

language_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O‘zbek tili", callback_data="stlang_uz"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="stlang_en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="stlang_ru"),
        ],
    ], resize_keyboard=True
)

channel_subscribe_text = {
    "uz": "📢 Kanalga a’zo bo‘lish",
    "en": "📢 Subscribe to the channel",
    "ru": "📢 Подписаться на канал"
}

check_text = {
    "uz": "✅ Tekshirish",
    "en": "✅ Check",
    "ru": "✅ Проверить"
}


def subscribe_keyboard(language: str):
    markup = InlineKeyboardBuilder()
    text = channel_subscribe_text.get(language, channel_subscribe_text["en"])
    txt = check_text.get(language, check_text["en"])
    markup.button(text=text, url=f"https://t.me/{CHANNEL}")
    markup.button(text=txt, callback_data="check_sub")
    markup.adjust(1)
    return markup.as_markup()


certificate_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🟢 B1", callback_data="cert_B1"),
            InlineKeyboardButton(text="🔵 B2", callback_data="cert_B2"),
        ],
        [
            InlineKeyboardButton(text="🟣 C1", callback_data="cert_C1"),
            InlineKeyboardButton(text="🟡 C2", callback_data="cert_C2"),
        ],
    ]
)

role_texts = {
    "uz": {
        "presenter": "🎤 Taqdimotchi",
        "debater": "🗣️ Munozarachi",
        "observer": "👀 Kuzatuvchi"
    },
    "en": {
        "presenter": "🎤 Presenter",
        "debater": "🗣️ Debater",
        "observer": "👀 Observer"
    },
    "ru": {
        "presenter": "🎤 Презентатор",
        "debater": "🗣️ Дебатёр",
        "observer": "👀 Наблюдатель"
    }
}


def role_keyboard(language: str):
    markup = InlineKeyboardBuilder()
    texts = role_texts.get(language, role_texts["en"])

    markup.button(text=texts["presenter"], callback_data="role_presenter")
    markup.button(text=texts["debater"], callback_data="role_debater")
    markup.button(text=texts["observer"], callback_data="role_observer")
    markup.adjust(1)
    return markup.as_markup()
