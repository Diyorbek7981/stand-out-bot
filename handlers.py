from aiogram import F, Router
from aiogram.types import Message
from aiogram.types import CallbackQuery
from buttons.inline import language_button, subscribe_keyboard, certificate_button
from buttons.reply import get_menu, get_phone, check
import requests
from config import API, CHANNEL
from aiogram.fsm.context import FSMContext
from states import SignupStates
from aiogram.types import ReplyKeyboardRemove

router = Router()


@router.message(F.text == '/start')
async def start(message: Message):
    text = "Tilni tanlang 🇺🇿| Choose your language 🇬🇧| Выберите язык 🇷🇺"
    await message.answer(text, reply_markup=language_button)


@router.callback_query(lambda c: c.data.startswith("stlang_"))
async def process_language(callback: CallbackQuery):
    await callback.message.delete()
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    response = requests.get(f"{API}/users/{user_id}")

    messages = {
        "uz": "✅ Siz O‘zbek tilini tanladingiz 🇺🇿\n\n❗ Botdan foydalanish uchun avval kanalga a’zo bo‘ling.",
        "en": "✅ You selected English 🇬🇧\n\n❗ Please join our channel first to use the bot.",
        "ru": "✅ Вы выбрали Русский 🇷🇺\n\n❗ Пожалуйста, сначала подпишитесь на наш канал, чтобы использовать бота."
    }

    if response.status_code != 200:
        payload = {
            "telegram_id": user_id,
            "user_name": callback.from_user.username,
            "language": lang_code,
        }
        try:
            response = requests.post(url=f"{API}/create_user/", data=payload)
            if response.status_code in [200, 201]:
                text = messages.get(lang_code, "Unknown language ❌")

                await callback.message.answer(text, reply_markup=subscribe_keyboard())
            else:
                return f"⚠️Error in the request: {response.status_code} | {response.text}"
        except Exception as e:
            return f"[❌] Error in the request: {e}"
    else:
        payload = {
            "language": lang_code,
        }
        try:
            response = requests.patch(url=f"{API}/user_update/{user_id}/", json=payload)
            if response.status_code in [200, 201]:
                text = messages.get(lang_code, "Unknown language ❌")

                await callback.message.answer(text, reply_markup=subscribe_keyboard())
            else:
                return f"⚠️Error in the request: {response.status_code} | {response.text}"
        except Exception as e:
            return f"[❌] Error in the request: {e}"

    await callback.answer()


@router.callback_query(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: CallbackQuery):
    await callback_query.message.delete()
    user_id = callback_query.from_user.id
    bot = callback_query.bot

    try:
        response = requests.get(f"{API}/users/{user_id}")
        if response.status_code != 200:
            await callback_query.answer("⚠️ Xatolik: foydalanuvchi topilmadi!", show_alert=True)
            return
        req = response.json()
        language = req.get("language", "uz")
    except Exception as e:
        await callback_query.answer(f"⚠️ So‘rovda xatolik: {e}", show_alert=True)
        return

    messages = {
        "uz": "✅ Rahmat! Siz kanalga a’zo bo‘ldingiz.\n\n📝 Tanlovda qatnashish uchun ro‘yxatdan o‘ting.",
        "en": "✅ Thank you! You have joined the channel.\n\n📝 Please register to participate in the contest.",
        "ru": "✅ Спасибо! Вы подписались на канал.\n\n📝 Пожалуйста, зарегистрируйтесь, чтобы участвовать в конкурсе."
    }

    unsub_message = {
        "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
        "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
        "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
    }

    member = await bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=user_id)
    txt = messages.get(language, "Unknown language ❌")
    if member.status in ["member", "administrator", "creator"]:
        try:
            data = {"is_channel_member": True}
            response = requests.patch(url=f"{API}/user_update/{user_id}/", json=data)
            if response.status_code in [200, 204]:
                await callback_query.message.answer(text=txt, reply_markup=get_menu(language))
            else:
                await callback_query.answer(f"⚠️ Error in the request: {response.status_code} - {response.text}")
        except Exception as backend_err:
            return f"❌ Backend Error: {backend_err}"

    else:
        txt = unsub_message.get(language, "Unknown language ❌")
        await callback_query.message.answer(text=txt, reply_markup=subscribe_keyboard())


@router.message(lambda msg: msg.text in ["📝 Ro'yhatdan o'tish", "📝 Register", "📝 Регистрация"])
async def register_button_handler(message: Message, state: FSMContext):
    res = requests.get(f"{API}/users/{message.from_user.id}").json()
    language = res["language"]

    if res["is_channel_member"] == False:
        unsub_message = {
            "uz": "❌ Hali kanalga a’zo bo‘lmadingiz!\n\n📢 Kanalga a’zo bo‘ling va qayta tekshirish tugmasini bosing:",
            "en": "❌ You are not subscribed to the channel!\n\n📢 Please subscribe to the channel and click the check button again:",
            "ru": "❌ Вы не подписаны на канал!\n\n📢 Подпишитесь на канал и нажмите кнопку проверки снова:"
        }
        txt = unsub_message.get(language, "Unknown language ❌")
        await message.answer(text=txt, reply_markup=subscribe_keyboard())
        return

    if res["is_registered"] == False:
        full_name_prompt = {
            "uz": "👤 To‘liq ismingizni kiriting (F.I.Sh):",
            "en": "👤 Enter your full name (First, Last, and Surname):",
            "ru": "👤 Введите ваше полное имя (Ф.И.О):"
        }
        txt = full_name_prompt.get(language, "Unknown language ❌")
        await message.answer(text=txt)
        await state.set_state(SignupStates.name)
    else:
        await message.answer("✅ Siz ro‘yxatdan o‘tgansiz")


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
        certificate_prompt = {
            "uz": "🎓 Sertifikat yoki IELTS darajangizni kiriting",
            "en": "🎓 Enter your Certificate or IELTS level",
            "ru": "🎓 Введите уровень вашего сертификата или IELTS"
        }
        txt_acc = accepted_message.get(language, "Unknown language ❌")
        txt_cer = certificate_prompt.get(language, "Unknown language ❌")
        await message.answer(f"{txt_acc}\n\n📞 {message.contact.phone_number}")
        await message.answer(txt_cer, reply_markup=certificate_button)
        await state.set_state(SignupStates.certificate)

    else:
        await message.answer("❌ Send your contact information")


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
        templates = {
            "uz": (
                f"Ariza Beruvchi: {data.get('name')}\n"
                f"Yoshingiz: {data.get('age')}\n"
                f"User name: @{callback.from_user.username}\n"
                f"Telefon raqamingiz: {data.get('phone')}\n"
                f"Darajangiz: {data.get('certificate')}\n"
            ),
            "en": (
                f"Applicant: {data.get('name')}\n"
                f"Age: {data.get('age')}\n"
                f"Username: @{callback.from_user.username}\n"
                f"Phone number: {data.get('phone')}\n"
                f"Certificate Level: {data.get('certificate')}\n"
            ),
            "ru": (
                f"Заявитель: {data.get('name')}\n"
                f"Возраст: {data.get('age')}\n"
                f"Имя пользователя: @{callback.from_user.username}\n"
                f"Телефон: {data.get('phone')}\n"
                f"Уровень сертификата: {data.get('certificate')}\n"
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

    else:
        await callback.message.answer("❌ Please send the correct level", reply_markup=certificate_button)
