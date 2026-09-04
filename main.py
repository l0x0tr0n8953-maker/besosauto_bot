import logging

import os

from aiogram import Bot, Dispatcher, types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID","0"))

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot)

# КНОПКА ДЛЯ НОМЕРА

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True)

phone_kb.add(KeyboardButton("📱 Отправить номер", request_contact=True))

# ХРАНИМ ДАННЫЕ

users_data = {}

# СТАРТ

@dp.message_handler(commands=['start'])

async def start(message: types.Message):

    users_data[message.from_user.id] = {}

    await message.answer("🚗 Какая марка авто интересует?")

# ШАГ 1 — МАРКА

@dp.message_handler(lambda message: message.from_user.id in users_data and "brand" not in users_data[message.from_user.id])

async def get_brand(message: types.Message):

    users_data[message.from_user.id]["brand"] = message.text

    await message.answer("Модель?")

# ШАГ 2 — МОДЕЛЬ

@dp.message_handler(lambda message: "model" not in users_data.get(message.from_user.id, {}))

async def get_model(message: types.Message):

    users_data[message.from_user.id]["model"] = message.text

    await message.answer("Бюджет?")

# ШАГ 3 — БЮДЖЕТ

@dp.message_handler(lambda message: "budget" not in users_data.get(message.from_user.id, {}))

async def get_budget(message: types.Message):

    users_data[message.from_user.id]["budget"] = message.text

    await message.answer("Отправьте номер телефона 📱", reply_markup=phone_kb)

# ШАГ 4 — ТЕЛЕФОН

@dp.message_handler(content_types=['contact'])

async def get_phone(message: types.Message):

    user = message.from_user

    data = users_data.get(user.id, {})

    phone = message.contact.phone_number

    text = f"""

🚗 Новая заявка!

👤 @{user.username}

🆔 {user.id}

Марка: {data.get("brand")}

Модель: {data.get("model")}

Бюджет: {data.get("budget")}

Телефон: {phone}

"""

    await bot.send_message(ADMIN_ID, text)

    await message.answer("✅ Заявка отправлена!", reply_markup=types.ReplyKeyboardRemove())

    users_data.pop(user.id, None)

if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)
