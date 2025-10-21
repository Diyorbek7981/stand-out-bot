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


def subscribe_keyboard():  # ///////////////////////////  Resume
    markup = InlineKeyboardBuilder()
    markup.button(text="📢 Kanalga a’zo bo‘lish", url=f"https://t.me/{CHANNEL}")
    markup.button(text="✅ Tekshirish", callback_data="check_sub")
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