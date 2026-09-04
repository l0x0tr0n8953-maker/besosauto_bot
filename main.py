import logging

import asyncio

import os

from aiogram import Bot, Dispatcher, types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.utils import executor

API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 413820160

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

dp = Dispatcher(bot)

users_data = {}

# 📱 Кнопка отправки номера

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)

phone_kb.add(KeyboardButton("📱 Отправить номер", request_contact=True))

# 🚀 СТАРТ (с поддержкой кнопки из канала)

@dp.message_handler(commands=['start'])

async def start(message: types.Message):

    user_id = message.from_user.id

    args = message.get_args()  # ← ВАЖНО

    users_data[user_id] = {"step": "brand"}

    # 🔥 если пришел с кнопки

    if args:

        users_data[user_id]["car"] = args

        await message.answer(

            "👋 Вы заинтересовались данным авто.\n"

            "Давайте подберем лучший вариант 🚗\n\n"

            "🚗 Какая марка авто интересует?"

        )

    else:

        await message.answer("🚗 Какая марка авто интересует?")

    # ⏰ напоминания

    asyncio.create_task(follow_up(user_id, 600))

    asyncio.create_task(follow_up(user_id, 3600))

# 💬 ОБРАБОТКА ШАГОВ

@dp.message_handler()

async def process(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    step = users_data[user_id].get("step")

    if step == "brand":

        users_data[user_id]["brand"] = message.text

        users_data[user_id]["step"] = "model"

        await message.answer("🚘 Какая модель?")

    elif step == "model":

        users_data[user_id]["model"] = message.text

        users_data[user_id]["step"] = "budget"

        kb = ReplyKeyboardMarkup(resize_keyboard=True)

        kb.add("💰 до 2 млн", "💰 2–3 млн")

        kb.add("💰 3+ млн")

        await message.answer("💰 Выберите бюджет:", reply_markup=kb)

    elif step == "budget":

        users_data[user_id]["budget"] = message.text

        users_data[user_id]["step"] = "phone"

        await message.answer("📱 Отправьте номер телефона", reply_markup=phone_kb)

# 📞 ПОЛУЧЕНИЕ НОМЕРА (кнопка)

@dp.message_handler(content_types=['contact'])

async def get_phone(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    phone = message.contact.phone_number

    users_data[user_id]["phone"] = phone

    data = users_data[user_id]

    text = (

        f"🚗 Новая заявка!\n\n"

        f"👤 @{message.from_user.username}\n"

        f"🆔 {user_id}\n\n"

        f"🚘 Марка: {data.get('brand')}\n"

        f"🚘 Модель: {data.get('model')}\n"

        f"💰 Бюджет: {data.get('budget')}\n"

        f"📱 Телефон: {phone}\n"

        f"🔗 Источник: {data.get('car', 'не указан')}"

    )

    await bot.send_message(ADMIN_ID, text)

    await message.answer("✅ Заявка отправлена! Мы скоро свяжемся с вами.")

    users_data.pop(user_id, None)

# 📞 ЕСЛИ ВВЕЛИ НОМЕР ВРУЧНУЮ

@dp.message_handler(lambda message: message.text and message.text.startswith("+"))

async def manual_phone(message: types.Message):

    user_id = message.from_user.id

    if user_id not in users_data:

        return

    users_data[user_id]["phone"] = message.text

    data = users_data[user_id]

    text = (

        f"🚗 Новая заявка!\n\n"

        f"👤 @{message.from_user.username}\n"

        f"🆔 {user_id}\n\n"

        f"🚘 Марка: {data.get('brand')}\n"

        f"🚘 Модель: {data.get('model')}\n"

        f"💰 Бюджет: {data.get('budget')}\n"

        f"📱 Телефон: {message.text}\n"

        f"🔗 Источник: {data.get('car', 'не указан')}"

    )

    await bot.send_message(ADMIN_ID, text)

    await message.answer("✅ Заявка отправлена!")

    users_data.pop(user_id, None)

# ⏰ НАПОМИНАНИЯ

async def follow_up(user_id, delay):

    await asyncio.sleep(delay)

    if user_id in users_data and "phone" not in users_data[user_id]:

        try:

            await bot.send_message(

                user_id,

                "👋 Вы не оставили номер.\nМогу подобрать авто под ваш бюджет 🚗"

            )

        except:

            pass

# ▶️ ЗАПУСК

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
