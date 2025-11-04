from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.types import CallbackQuery
from buttons.inline import language_button, subscribe_keyboard, certificate_button, role_keyboard
from buttons.reply import get_menu, get_phone, check, menu
import requests
from config import API, CHANNEL, ADMIN
from aiogram.fsm.context import FSMContext
from states import SignupStates
from aiogram.types import ReplyKeyboardRemove
import json
import qrcode
import os
from aiogram.types import FSInputFile
from aiogram.filters import Command, CommandStart

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    bot = message.bot
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=message.from_user.id)
    try:
        await state.clear()
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return
        req = response.json()
        language = req.get("language", "en")

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }
            txt = unsub_message.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=subscribe_keyboard(language))
            return

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "en": "👤 Enter your full name (First, Last, and Surname):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        services_text = {
            "uz": "Bizning xizmatlar bilan tanishib chiqing",
            "en": "Explore our services",
            "ru": "Ознакомьтесь с нашими услугами"
        }
        txt = services_text.get(language, services_text["en"])
        await message.answer(f"🌟 {message.from_user.full_name}  {txt}", reply_markup=menu(language))
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.message(Command("help"))
async def state_name(message: Message, state: FSMContext):
    try:
        await state.clear()
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "en")

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "en": "👤 Enter your full name (First, Last, and Surname):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        res = requests.get(f"{API}/users/{ADMIN}").json()

        help_text = {
            "uz": "👨🏻‍💻 Yordam uchun Adminga murojaat qiling",
            "en": "👨🏻‍💻Please contact the Admin for assistance",
            "ru": "👨🏻‍💻 Для помощи обратитесь к Администратору"
        }
        txt = help_text.get(language, "Unknown language ❌")
        await message.answer(
            f"{txt}\n\nhttps://t.me/{res['user_name']}", reply_markup=menu(language))
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("stlang_"))
async def process_language(callback: CallbackQuery):
    await callback.message.delete()
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    bot = callback.bot
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=user_id)
    try:
        response = requests.get(f"{API}/users/{user_id}")
        if response.status_code != 200:
            payload = {
                "telegram_id": user_id,
                "user_name": callback.from_user.username,
                "language": lang_code,
            }
            try:
                response = requests.post(url=f"{API}/create_user/", data=payload)
                if response.status_code in [200, 201]:
                    messages = {
                        "uz": "✅ Siz O‘zbek tilini tanladingiz 🇺🇿\n\n❗ Botdan foydalanish uchun avval kanalga a’zo bo‘ling.",
                        "en": "✅ You selected English 🇬🇧\n\n❗ Please join our channel first to use the bot.",
                        "ru": "✅ Вы выбрали Русский 🇷🇺\n\n❗ Пожалуйста, сначала подпишитесь на наш канал, чтобы использовать бота."
                    }

                    text = messages.get(lang_code, "Unknown language ❌")
                    await callback.message.answer(text, reply_markup=subscribe_keyboard(lang_code))
                    return
                else:
                    return f"⚠️Error in the request: {response.status_code} | {response.text}"
            except Exception as e:
                return f"[❌] Error in the request: {e}"

        req = response.json()
        language = req.get("language", "en")

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }
            txt = unsub_message.get(language, "Unknown language ❌")
            await callback.message.answer(text=txt, reply_markup=subscribe_keyboard(language))
            return

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "en": "👤 Enter your full name (First, Last, and Surname):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await callback.message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await callback.state.set_state(SignupStates.name)
            return

        payload = {
            "language": lang_code,
        }
        try:
            response = requests.patch(url=f"{API}/user_update/{user_id}/", json=payload)
            if response.status_code in [200, 201]:
                messages = {
                    "uz": "✅ Siz O‘zbek tilini tanladingiz 🇺🇿",
                    "en": "✅ You selected English 🇬🇧",
                    "ru": "✅ Вы выбрали Русский 🇷🇺"
                }
                text = messages.get(lang_code, "Unknown language ❌")
                await callback.message.answer(text, reply_markup=menu(lang_code))
            else:
                return f"⚠️Error in the request: {response.status_code} | {response.text}"
        except Exception as e:
            return f"[❌] Error in the request: {e}"

        await callback.answer()
    except Exception as e:
        await callback.message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    await callback.message.delete()
    user_id = callback.from_user.id
    bot = callback.bot

    try:
        response = requests.get(f"{API}/users/{user_id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await callback.message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "en")
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=user_id)

        if req["is_registered"] == False:
            messages = {
                "uz": "✅ Rahmat! Siz kanalga a’zo bo‘ldingiz.\n\n📝 Tanlovda qatnashish uchun ro‘yxatdan o‘ting.",
                "en": "✅ Thank you! You have joined the channel.\n\n📝 Please register to participate in the contest.",
                "ru": "✅ Спасибо! Вы подписались на канал.\n\n📝 Пожалуйста, зарегистрируйтесь, чтобы участвовать в конкурсе."
            }

            if member.status in ["member", "administrator", "creator"]:
                txtunre = messages.get(language, "Unknown language ❌")
                await callback.message.answer(text=txtunre, reply_markup=get_menu(language))
                return
            else:
                unsub_message = {
                    "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                    "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                    "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
                }

                txt = unsub_message.get(language, "Unknown language ❌")
                await callback.message.answer(text=txt, reply_markup=subscribe_keyboard(language))
                return

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }

            txt = unsub_message.get(language, "Unknown language ❌")
            await callback.message.answer(text=txt, reply_markup=subscribe_keyboard(language))
        else:
            messages = {
                "uz": "✅ Rahmat! Siz kanalga a’zo bo‘ldingiz.",
                "en": "✅ Thank you! You have joined the channel.",
                "ru": "✅ Спасибо! Вы подписались на канал."
            }
            txtunre = messages.get(language, "Unknown language ❌")
            await callback.message.answer(text=txtunre, reply_markup=menu(language))

    except Exception as e:
        await callback.message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)


@router.message(lambda msg: msg.text in ["📝 Ro'yhatdan o'tish", "📝 Register", "📝 Регистрация"])
async def register_button_handler(message: Message, state: FSMContext):
    bot = message.bot
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=message.from_user.id)
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return
        req = response.json()
        language = req.get("language", "en")

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }
            txt = unsub_message.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=subscribe_keyboard(language))
            return

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "en": "👤 Enter your full name (First, Last, and Surname):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        services_text = {
            "uz": "Bizning xizmatlar bilan tanishib chiqing",
            "en": "Explore our services",
            "ru": "Ознакомьтесь с нашими услугами"
        }
        txt = services_text.get(language, services_text["en"])
        await message.answer(f"🌟 {message.from_user.full_name}  {txt}", reply_markup=menu(language))

    except Exception as e:
        await message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


@router.message(Command("stop"))
async def state_name(message: Message, state: FSMContext):
    bot = message.bot
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=message.from_user.id)
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return
        req = response.json()
        language = req.get("language", "en")

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }
            txt = unsub_message.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=subscribe_keyboard(language))
            return

        curent = await state.get_state()
        if curent == None:
            no_data_text = {
                "uz": "🔍 To'xtatish uchun ma'lumot mavjud emas",
                "en": "🔍 No data available to stop",
                "ru": "🔍 Нет данных для остановки"
            }
            txt = no_data_text.get(language, "Unknown language ❌")
            await message.answer(txt)
        else:
            cancelled_text = {
                "uz": "❌ Jarayon bekor qilindi",
                "en": "❌ Process has been cancelled",
                "ru": "❌ Процесс был отменён"
            }
            txt = cancelled_text.get(language, "Unknown language ❌")
            await message.answer(txt)
            await state.clear()
    except Exception as e:
        await message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


@router.message(Command("new"))
async def state_name(message: Message, state: FSMContext):
    bot = message.bot
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=message.from_user.id)
    curent = await state.get_state()
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return
        req = response.json()
        language = req.get("language", "en")

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }
            txt = unsub_message.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=subscribe_keyboard(language))
            return

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "en": "👤 Enter your full name (First, Last, and Surname):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")

            if curent == None:
                await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
                await state.set_state(SignupStates.name)
                return
            else:
                await state.clear()
                await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
                await state.set_state(SignupStates.name)
                return
        else:
            already_registered_text = {
                "uz": "✅ Siz ro‘yxatdan o‘tgansiz",
                "en": "✅ You are already registered",
                "ru": "✅ Вы уже зарегистрированы"
            }

            txt = already_registered_text.get(language, already_registered_text["en"])
            await message.answer(f"{message.from_user.full_name}  {txt}", reply_markup=menu(language))
    except Exception as e:
        await message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@router.message(SignupStates.name)
async def state_name(message: Message, state: FSMContext):
    res = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = res["language"]
    if 4 <= len(message.text) <= 100:
        if not any(digit in message.text for digit in '0123456789'):
            await state.update_data(name=message.text)
            accepted_message = {
                "uz": "✅ Qabul qilindi",
                "en": "✅ Accepted",
                "ru": "✅ Принято"
            }
            age_prompt = {
                "uz": "📅 Yoshingizni kiriting",
                "en": "📅 Enter your age",
                "ru": "📅 Введите ваш возраст"
            }
            txt_acc = accepted_message.get(language, "Unknown language ❌")
            txt_age = age_prompt.get(language, "Unknown language ❌")
            await message.answer(f"{txt_acc}\n\n👤 {message.text}")
            await message.answer(txt_age)
            await state.set_state(SignupStates.age)
        else:
            await message.answer("❌ The name cannot contain numbers!")
    else:
        await message.answer("❌ The length of the information you entered is invalid!")


@router.message(SignupStates.age)
async def state_age(message: Message, state: FSMContext):
    res = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = res["language"]
    if message.text.isdigit() and 4 < int(message.text) < 50:
        await state.update_data(age=message.text)
        accepted_message = {
            "uz": "✅ Qabul qilindi",
            "en": "✅ Accepted",
            "ru": "✅ Принято"
        }
        phone_prompt = {
            "uz": "📞 Telefon raqamingizni jo‘nating",
            "en": "📞 Send your phone number",
            "ru": "📞 Отправьте свой номер телефона"
        }
        txt_acc = accepted_message.get(language, "Unknown language ❌")
        txt_phone = phone_prompt.get(language, "Unknown language ❌")
        await message.answer(f"{txt_acc}\n\n📅 {message.text}")
        await message.answer(txt_phone,
                             reply_markup=get_phone(language))
        await state.set_state(SignupStates.phone)
    else:
        await message.answer("❌ Enter a valid age (between 4 and 50)")


@router.message(SignupStates.phone)
async def state_phone(message: Message, state: FSMContext):
    res = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = res["language"]
    if message.contact:
        await state.update_data(phone=message.contact.phone_number)
        accepted_message = {
            "uz": "✅ Qabul qilindi",
            "en": "✅ Accepted",
            "ru": "✅ Принято"
        }
        choose_role_text = {
            "uz": "📋 Siz kim bo‘lib ishtirok etmoqchisiz?",
            "en": "📋 In which position do you want to be?",
            "ru": "📋 В какой роли вы хотите участвовать?"
        }
        txt_acc = accepted_message.get(language, "Unknown language ❌")
        txt_cer = choose_role_text.get(language, "Unknown language ❌")
        await message.answer(f"{txt_acc}\n\n📞 {message.contact.phone_number}")
        await message.answer(txt_cer, reply_markup=role_keyboard(language))
        await state.set_state(SignupStates.role)

    else:
        await message.answer("❌ Send your contact information")


@router.callback_query(SignupStates.role, F.data.startswith("role_"))
async def save_user_role(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    role = callback.data.split("_")[1]
    res = requests.get(f"{API}/users/{callback.from_user.id}").json()
    language = res["language"]
    if role in ["presenter", "debater", "observer"]:
        await state.update_data(role=role)

        text_map = {
            "uz": {
                "presenter": "🎤 Siz Taqdimotchi sifatida tanlandingiz!",
                "debater": "🗣️ Siz Munozarachi sifatida tanlandingiz!",
                "observer": "👀 Siz Kuzatuvchi sifatida tanlandingiz!",
            },
            "en": {
                "presenter": "🎤 You have chosen to be a Presenter!",
                "debater": "🗣️ You have chosen to be a Debater!",
                "observer": "👀 You have chosen to be an Observer!",
            },
            "ru": {
                "presenter": "🎤 Вы выбрали роль Презентатора!",
                "debater": "🗣️ Вы выбрали роль Дебатёра!",
                "observer": "👀 Вы выбрали роль Наблюдателя!",
            },
        }

        certificate_prompt = {
            "uz": "🎓 Sertifikat yoki IELTS darajangizni kiriting",
            "en": "🎓 Enter your Certificate or IELTS level",
            "ru": "🎓 Введите уровень вашего сертификата или IELTS"
        }

        msg = text_map.get(language, text_map["en"]).get(role, "✅ Rol tanlandi!")
        txt = certificate_prompt.get(language, 'Unknown language ❌')
        await callback.message.answer(msg)
        await callback.message.answer(txt, reply_markup=certificate_button)
        await callback.answer()
        await state.set_state(SignupStates.certificate)
    else:
        await callback.message.answer("❌ Please send the correct level")


@router.callback_query(SignupStates.certificate)
async def state_certificate(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    res = requests.get(f"{API}/users/{callback.from_user.id}").json()
    language = res["language"]
    cert_level = callback.data.split("_")[1]
    if cert_level in ["B1", "B2", "C1", "C2"]:
        await state.update_data(certificate=cert_level)
        accepted_message = {
            "uz": "✅ Qabul qilindi",
            "en": "✅ Accepted",
            "ru": "✅ Принято"
        }
        txt_acc = accepted_message.get(language, "Unknown language ❌")
        await callback.message.answer(f"{txt_acc}\n\n🎓 {cert_level}")

        data = await state.get_data()
        role_translation = {
            "uz": {
                "presenter": "Taqdimotchi",
                "debater": "Munozarachi",
                "observer": "Kuzatuvchi",
            },
            "en": {
                "presenter": "Presenter",
                "debater": "Debater",
                "observer": "Observer",
            },
            "ru": {
                "presenter": "Презентатор",
                "debater": "Дебатёр",
                "observer": "Наблюдатель",
            },
        }
        role_text = role_translation.get(language, role_translation["en"]).get(data.get("role"), data.get("role"))

        templates = {
            "uz": (
                f"Ariza Beruvchi: {data.get('name')}\n"
                f"Yoshingiz: {data.get('age')}\n"
                f"User name: @{callback.from_user.username}\n"
                f"Telefon raqamingiz: {data.get('phone')}\n"
                f"Darajangiz: {data.get('certificate')}\n"
                f"O'rin: {role_text}\n"
            ),
            "en": (
                f"Applicant: {data.get('name')}\n"
                f"Age: {data.get('age')}\n"
                f"Username: @{callback.from_user.username}\n"
                f"Phone number: {data.get('phone')}\n"
                f"Certificate Level: {data.get('certificate')}\n"
                f"Position: {role_text}\n"
            ),
            "ru": (
                f"Заявитель: {data.get('name')}\n"
                f"Возраст: {data.get('age')}\n"
                f"Имя пользователя: @{callback.from_user.username}\n"
                f"Телефон: {data.get('phone')}\n"
                f"Уровень сертификата: {data.get('certificate')}\n"
                f"Позиция: {role_text}\n"
            )
        }

        messages = {
            "uz": "📄 Arizani tasdiqlaysizmi?",
            "en": "📄 Do you confirm the application?",
            "ru": "📄 Вы подтверждаете заявку?"
        }

        conf_msg = {
            "uz": "❗ ✔️ yoki /new ni tanlang",
            "en": "❗ Select ✔️ or /new",
            "ru": "❗ Выберите ✔️ или /new"
        }

        txt = messages.get(language, "Unknown language ❌")
        txt_conf = conf_msg.get(language, "Unknown language ❌")
        txt_template = templates.get(language, "Unknown language ❌")
        await callback.message.answer(f"{txt}\n\n{txt_template}\n\n{txt_conf}", reply_markup=check)
        await state.set_state(SignupStates.check)
    else:
        await callback.message.answer("❌ Please send the correct level", reply_markup=certificate_button)


@router.message(SignupStates.check)
async def state_name(message: Message, state: FSMContext, bot: Bot):
    req = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = req["language"]
    if message.text == "✔️":
        data = await state.get_data()

        user = (
            f"{message.from_user.mention_html('👤📝 Ma`lumotlar / Информация:')}\n\n"
            f"📝 ID: {req.get('id')}\n"
            f"👤 Ariza Beruvchi: {data.get('name')}\n"
            f"📅 Yosh: {data.get('age')}\n"
            f"🌐 User name: @{message.from_user.username}\n"
            f"📱 Telefon raqam: {data.get('phone')}\n"
            f"👨🏽‍💻 O'rin: {data.get('role')}\n"
            f"🎓 Daraja: {data.get('certificate')}\n\n\n"
            f"<a href='{API}/admin'>🌐 Arizani sayt orqali tasdiqlash</a>"
        )

        api_data = {
            'first_name': data.get('name'),
            'age': data.get('age'),
            'phone_number': data.get('phone'),
            'certificate': data.get('certificate'),
            'role': data.get('role'),
            'is_registered': True
        }

        postResponse = requests.patch(url=f"{API}/user_update/{message.from_user.id}/", json=api_data)

        if postResponse.status_code in (200, 201):
            json.dumps(postResponse.json(), indent=4)
            await bot.send_message(ADMIN, f"🌟 Yangi ariza:\n\n{user}", parse_mode='HTML')
            messages = {
                "uz": "✅ Arizangiz qabul qilindi",
                "en": "✅ Your application has been accepted",
                "ru": "✅ Ваша заявка принята"
            }
            txt = messages.get(language, "Unknown language ❌")
            await message.answer(txt, reply_markup=menu(language))
            await state.clear()

        else:
            error_text = {
                "uz": (
                    "❌ Ma'lumotlaringiz saqlanmadi\n\n"
                    "🗑 Jarayonni bekor qilish: /stop\n"
                    "🔄 Jarayonni boshidan boshlash: /new"
                ),
                "en": (
                    "❌ Your data was not saved\n\n"
                    "🗑 Cancel the process: /stop\n"
                    "🔄 Restart the process: /new"
                ),
                "ru": (
                    "❌ Ваши данные не сохранены\n\n"
                    "🗑 Отменить процесс: /stop\n"
                    "🔄 Начать процесс заново: /new"
                )
            }
            text = error_text.get(language, error_text["en"])
            await message.answer(text, reply_markup=check)
    else:
        txt = {
            "uz": (
                "✔️ Ma'lumotlarni tasdiqlash: ✔️\n"
                "🗑 Jarayonni bekor qilish: /stop\n"
                "🔄 Jarayonni boshidan boshlash: /new"
            ),
            "en": (
                "✔️ Confirm the information: ✔️\n"
                "🗑 Cancel the process: /stop\n"
                "🔄 Restart the process: /new"
            ),
            "ru": (
                "✔️ Подтвердить информацию: ✔️\n"
                "🗑 Отменить процесс: /stop\n"
                "🔄 Начать процесс заново: /new"
            )
        }
        text = txt.get(language, txt["en"])
        await message.answer(text, reply_markup=check)


@router.message(lambda msg: msg.text in ["📝 Ruhsatnoma olish", "📝 Get a permit", "📝 Получить разрешение"])
async def register_button_handler(message: Message):
    bot = message.bot
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=message.from_user.id)
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        res = response.json()
        language = res.get("language", "en")

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }
            txt = unsub_message.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=subscribe_keyboard(language))
            return

        if res["is_confirmed"] == False:
            response_text = {
                "uz": "🕒 Arizangiz ko‘rib chiqilmoqda. Tez orada javob olasiz.",
                "en": "🕒 Your application is being reviewed. You will receive a response soon.",
                "ru": "🕒 Ваша заявка рассматривается. Скоро вы получите ответ."
            }

            txt = response_text.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=menu(language))
            return

        user_info = (
            f"Ism: {res.get('first_name')}\n"
            f"Yosh: {res.get('age')}\n"
            f"Username: @{message.from_user.username}\n"
            f"Telefon: {res.get('phone_number')}\n"
            f"Daraja: {res.get('certificate')}\n"
            f"O'rin: {res.get('role')}"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(user_info)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        file_path = f"qr_{message.from_user.id}.png"
        img.save(file_path)

        file = FSInputFile(file_path)

        qr_ready_text = {
            "uz": "✅ Sizning ma'lumotlaringiz QR-kod ko‘rinishda tayyorlandi",
            "en": "✅ Your information has been prepared as a QR code",
            "ru": "✅ Ваша информация подготовлена в виде QR-кода"
        }
        txt = qr_ready_text.get(language, "Unknown language ❌")
        await message.answer_photo(photo=file, caption=txt, reply_markup=menu(language))

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await message.answer(f"⚠️ Error in the request: {e}", show_alert=True)


@router.message(lambda msg: msg.text in ["🌐 Tilni o‘zgartirish", "🌐 Change language", "🌐 Изменить язык"])
async def register_button_handler(message: Message, state: FSMContext):
    bot = message.bot
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=message.from_user.id)
    try:
        response = requests.get(f"{API}/users/{message.from_user.id}")
        if response.status_code != 200:
            text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
            await message.answer(text, reply_markup=language_button)
            return

        req = response.json()
        language = req.get("language", "en")

        if member.status not in ["member", "administrator", "creator"]:
            unsub_message = {
                "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
                "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
                "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
            }
            txt = unsub_message.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=subscribe_keyboard(language))
            return

        if req["is_registered"] == False:
            full_name_prompt = {
                "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
                "en": "👤 Enter your full name (First, Last, and Surname):",
                "ru": "👤 Введите ваше полное имя (Ф.И.О):"
            }
            txt = full_name_prompt.get(language, "Unknown language ❌")
            await message.answer(text=txt, reply_markup=ReplyKeyboardRemove())
            await state.set_state(SignupStates.name)
            return

        text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
        await message.answer(text, reply_markup=language_button)
    except Exception as e:
        await message.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)
